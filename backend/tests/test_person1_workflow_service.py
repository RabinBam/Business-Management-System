import asyncio
from datetime import date, timedelta

import pytest

from app.schemas.marketing import BudgetAllocation, MarketingPlan
from app.schemas.report import FinancialSummary, Report, SalesPrediction
from app.schemas.task import ManagementReview, TaskRead, TaskStatus
from app.schemas.worker import WorkerResult
from app.schemas.workflow import WorkflowCreate, WorkflowRead, WorkflowStatus
from app.services.ai_service import MockAIProvider
from app.services.workflow_service import (
    WorkflowCollaborators,
    WorkflowConflictError,
    WorkflowExecutionError,
    WorkflowService,
    WorkflowValidationError,
)


def _payload(**overrides: object) -> WorkflowCreate:
    values: dict[str, object] = {
        "title": "Regional launch",
        "objective": "Launch the service with measurable delivery controls.",
        "budget": 100_000,
        "deadline": date.today() + timedelta(days=30),
    }
    values.update(overrides)
    return WorkflowCreate.model_validate(values)


def _complete_collaborators() -> WorkflowCollaborators:
    def execute(tasks: list[TaskRead]) -> list[WorkerResult]:
        return [
            WorkerResult(
                task_id=task.id,
                worker_id=f"worker-{index:03d}",
                summary="Task completed with evidence.",
            )
            for index, task in enumerate(tasks, start=1)
        ]

    def report(
        workflow: WorkflowRead,
        _tasks: list[TaskRead],
        _results: list[WorkerResult],
        _reviews: list[ManagementReview],
    ) -> Report:
        return Report(
            workflow_id=workflow.id,
            financial=FinancialSummary(
                total_budget=100_000,
                planned_spend=75_000,
                remaining_budget=25_000,
            ),
            sales_prediction=SalesPrediction(
                current_sales=100,
                predicted_sales=115,
                growth_percent=15,
            ),
            risks=[],
            recommendations=["Proceed"],
        )

    def marketing(workflow: WorkflowRead, _report: Report) -> MarketingPlan:
        return MarketingPlan(
            workflow_id=workflow.id,
            approved_budget=25_000,
            objective="Reach qualified buyers",
            target_audience="Operations leaders",
            allocations=[
                BudgetAllocation(
                    channel="Search",
                    amount=10_000,
                    reason="High intent",
                )
            ],
            timeline=["Week 1: launch"],
        )

    return WorkflowCollaborators(
        execute_workers=execute,
        generate_report=report,
        generate_marketing=marketing,
    )


def test_workflow_pauses_at_unowned_worker_stage() -> None:
    service = WorkflowService(ai_service=MockAIProvider())
    workflow = service.create(_payload())

    result = asyncio.run(service.run_workflow(workflow.id))

    assert result.status is WorkflowStatus.EXECUTING
    tasks = service.get_tasks(workflow.id)
    assert tasks is not None
    assert len(tasks) == 2
    assert all(task.status is TaskStatus.PENDING for task in tasks)


def test_workflow_completes_through_injected_collaborators() -> None:
    service = WorkflowService(
        ai_service=MockAIProvider(),
        collaborators=_complete_collaborators(),
    )
    workflow = service.create(_payload())

    result = asyncio.run(service.run_workflow(workflow.id))

    assert result.status is WorkflowStatus.COMPLETED
    assert result.executive_summary is not None
    assert result.executive_summary.objective == workflow.objective
    tasks = service.get_tasks(workflow.id)
    assert tasks is not None
    assert all(task.status is TaskStatus.COMPLETED for task in tasks)


def test_workflow_resumes_after_collaborators_are_configured() -> None:
    service = WorkflowService(ai_service=MockAIProvider())
    workflow = service.create(_payload())
    paused = asyncio.run(service.run_workflow(workflow.id))
    assert paused.status is WorkflowStatus.EXECUTING

    service.configure_collaborators(_complete_collaborators())
    completed = asyncio.run(service.run_workflow(workflow.id))

    assert completed.status is WorkflowStatus.COMPLETED


def test_workflow_persists_failure_stage() -> None:
    def fail_workers(_tasks: list[TaskRead]) -> list[WorkerResult]:
        raise RuntimeError("worker gateway unavailable")

    service = WorkflowService(
        ai_service=MockAIProvider(),
        collaborators=WorkflowCollaborators(
            execute_workers=fail_workers,
        ),
    )
    workflow = service.create(_payload())

    with pytest.raises(WorkflowExecutionError):
        asyncio.run(service.run_workflow(workflow.id))

    failed = service.require(workflow.id)
    assert failed.status is WorkflowStatus.FAILED
    assert failed.failure is not None
    assert failed.failure.failed_stage is WorkflowStatus.EXECUTING
    assert "worker gateway unavailable" in failed.failure.message


def test_illegal_state_transition_is_rejected() -> None:
    service = WorkflowService(ai_service=MockAIProvider())
    workflow = service.create(_payload())

    with pytest.raises(WorkflowConflictError, match="Cannot transition"):
        service.transition(workflow.id, WorkflowStatus.REPORTING)


def test_past_deadline_is_rejected() -> None:
    service = WorkflowService(ai_service=MockAIProvider())

    with pytest.raises(WorkflowValidationError, match="past"):
        service.create(_payload(deadline=date.today() - timedelta(days=1)))


def test_concurrent_runs_are_serialized_and_idempotent() -> None:
    service = WorkflowService(
        ai_service=MockAIProvider(),
        collaborators=_complete_collaborators(),
    )
    workflow = service.create(_payload())

    async def run_twice() -> list[object]:
        return await asyncio.gather(
            service.run_workflow(workflow.id),
            service.run_workflow(workflow.id),
        )

    results = asyncio.run(run_twice())

    assert all(result.status is WorkflowStatus.COMPLETED for result in results)
    tasks = service.get_tasks(workflow.id)
    assert tasks is not None
    assert len(tasks) == 2


def test_workflow_emits_events_through_observer_port() -> None:
    events: list[tuple[str, str, str, str, int]] = []
    collaborators = _complete_collaborators()
    service = WorkflowService(
        ai_service=MockAIProvider(),
        collaborators=WorkflowCollaborators(
            execute_workers=collaborators.execute_workers,
            generate_report=collaborators.generate_report,
            generate_marketing=collaborators.generate_marketing,
            record_event=lambda *event: events.append(event),
        ),
    )
    workflow = service.create(_payload())

    result = asyncio.run(service.run_workflow(workflow.id))

    assert result.status is WorkflowStatus.COMPLETED
    assert any(event[2] == "STATUS_CHANGED" for event in events)
    assert events[-1][3] == "Workflow entered COMPLETED"
