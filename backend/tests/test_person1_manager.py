import asyncio
from datetime import date, timedelta

import pytest

from app.agents.manager import ManagementError, Manager
from app.schemas.marketing import BudgetAllocation, MarketingPlan
from app.schemas.report import FinancialSummary, Report, SalesPrediction
from app.schemas.task import GeneratedTask, ManagementReview, TaskRead
from app.schemas.worker import WorkerResult
from app.schemas.workflow import WorkflowCreate, WorkflowRead
from app.services.ai_service import MockAIProvider


def _task(**overrides: object) -> GeneratedTask:
    payload: dict[str, object] = {
        "title": "Analyze launch readiness",
        "description": "Assess delivery readiness and document gaps.",
        "priority": "HIGH",
        "difficulty": 3,
        "required_role": "Business Analyst",
        "minimum_experience_years": 2,
        "required_skills": ["analysis"],
        "dependency_task_ids": [],
        "expected_output": "Readiness assessment",
        "acceptance_criteria": ["Risks and mitigations are documented"],
    }
    payload.update(overrides)
    return GeneratedTask.model_validate(payload)


def _task_read() -> TaskRead:
    return TaskRead(
        id="task-001",
        workflow_id="wf-test",
        **_task().model_dump(),
    )


def _workflow() -> WorkflowRead:
    create = WorkflowCreate(
        title="Launch",
        objective="Launch the service with measurable controls.",
        budget=100_000,
        deadline=date.today() + timedelta(days=30),
    )
    return WorkflowRead(id="wf-test", **create.model_dump())


def _report() -> Report:
    return Report(
        workflow_id="wf-test",
        financial=FinancialSummary(
            total_budget=100_000,
            planned_spend=80_000,
            remaining_budget=20_000,
        ),
        sales_prediction=SalesPrediction(
            current_sales=100,
            predicted_sales=115,
            growth_percent=15,
        ),
        risks=["Delivery timing"],
        recommendations=["Monitor weekly"],
    )


def _marketing() -> MarketingPlan:
    return MarketingPlan(
        workflow_id="wf-test",
        approved_budget=20_000,
        objective="Reach qualified buyers",
        target_audience="Operations leaders",
        allocations=[
            BudgetAllocation(channel="Search", amount=10_000, reason="High intent")
        ],
        timeline=["Week 1: launch"],
    )


def test_manager_refines_without_changing_dependencies() -> None:
    original = _task()
    refined = _task(description="Assess delivery readiness with named evidence.")
    manager = Manager(MockAIProvider({GeneratedTask: [refined]}))

    result = asyncio.run(manager.refine_task(original))

    assert result.description == refined.description
    assert result.dependency_task_ids == original.dependency_task_ids


def test_manager_rejects_dependency_changes() -> None:
    original = _task()
    changed = _task(dependency_task_ids=["task-001"])
    manager = Manager(MockAIProvider({GeneratedTask: [changed]}))

    with pytest.raises(ManagementError, match="dependencies"):
        asyncio.run(manager.refine_task(original))


def test_manager_reviews_worker_result() -> None:
    task = _task_read()
    result = WorkerResult(
        task_id=task.id,
        worker_id="worker-001",
        summary="Readiness analyzed",
    )
    review = ManagementReview(
        task_id=task.id,
        decision="APPROVED",
        feedback="Evidence meets the criteria.",
        acceptance_criteria_met=task.acceptance_criteria,
    )
    manager = Manager(MockAIProvider({ManagementReview: [review]}))

    approved = asyncio.run(manager.review_worker_result(task=task, result=result))

    assert approved.decision == "APPROVED"


def test_manager_rejects_result_for_another_task() -> None:
    task = _task_read()
    result = WorkerResult(
        task_id="task-999",
        worker_id="worker-001",
        summary="Wrong result",
    )

    with pytest.raises(ManagementError, match="does not belong"):
        asyncio.run(Manager(MockAIProvider()).review_worker_result(task=task, result=result))


def test_manager_summary_preserves_authoritative_objective() -> None:
    manager = Manager(MockAIProvider())

    summary = asyncio.run(
        manager.create_executive_summary(
            workflow=_workflow(),
            report=_report(),
            marketing=_marketing(),
            reviews=[],
        )
    )

    assert summary.objective == _workflow().objective
    assert summary.management_recommendation

