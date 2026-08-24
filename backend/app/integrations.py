from threading import RLock

from app.agents.watcher import execute_with_watch
from app.agents.worker import get_worker_agent
from app.config import settings
from app.schemas.marketing import MarketingPlan
from app.schemas.report import Report
from app.schemas.task import ManagementReview, TaskRead
from app.schemas.worker import WorkerResult
from app.schemas.workflow import WorkflowRead
from app.services.marketing_service import marketing_service
from app.services.report_service import get_report_service
from app.services.watcher_service import watcher_service
from app.services.workflow_service import (
    WorkflowCollaborators,
    WorkflowService,
    get_workflow_service,
)

_simulated_report_failures: set[str] = set()
_simulation_lock = RLock()


async def _execute_workers(tasks: list[TaskRead]) -> list[WorkerResult]:
    workflow_id = tasks[0].workflow_id if tasks else None
    return await execute_with_watch(
        "worker_agent",
        lambda: get_worker_agent().assign_and_execute_all(tasks),
        workflow_id=workflow_id,
        max_retries=1,
    )


async def _generate_report_adapter(
    workflow: WorkflowRead,
    _tasks: list[TaskRead],
    _results: list[WorkerResult],
    _reviews: list[ManagementReview],
) -> Report:
    return await generate_report_for_workflow(workflow)


async def generate_report_for_workflow(workflow: WorkflowRead) -> Report:
    """Run report generation through failure simulation and watcher recovery."""

    def operation() -> Report:
        if settings.simulate_report_failure:
            with _simulation_lock:
                if workflow.id not in _simulated_report_failures:
                    _simulated_report_failures.add(workflow.id)
                    raise RuntimeError("Simulated report generation failure")
        return get_report_service().generate_report(workflow)

    return await execute_with_watch(
        "report_agent",
        operation,
        workflow_id=workflow.id,
        max_retries=1,
    )


async def generate_marketing_for_workflow(
    workflow: WorkflowRead,
    report: Report,
) -> MarketingPlan:
    approved_budget = max(0.0, report.financial.remaining_budget)
    approved_context: dict[str, object] = {
        "sales_prediction": report.sales_prediction.model_dump(mode="json"),
        "risks": list(report.risks),
        "recommendations": list(report.recommendations),
    }
    return await execute_with_watch(
        "marketing_agent",
        lambda: marketing_service.generate_plan(
            workflow_id=workflow.id,
            product_brief=workflow.objective,
            max_budget=approved_budget,
            approved_context=approved_context,
        ),
        workflow_id=workflow.id,
        max_retries=1,
    )


def _record_workflow_event(
    workflow_id: str,
    component: str,
    event_type: str,
    message: str,
    retry_count: int,
) -> None:
    watcher_service.record_event(
        workflow_id=workflow_id,
        component=component,
        event_type=event_type,
        message=message,
        retry_count=retry_count,
        resolved=event_type == "STATUS_CHANGED",
    )


def configure_workflow_integrations(
    service: WorkflowService | None = None,
) -> WorkflowService:
    """Attach the existing team services to the Person 1 workflow spine."""

    workflow_service = service or get_workflow_service()
    workflow_service.configure_collaborators(
        WorkflowCollaborators(
            execute_workers=_execute_workers,
            generate_report=_generate_report_adapter,
            generate_marketing=generate_marketing_for_workflow,
            record_event=_record_workflow_event,
        )
    )
    return workflow_service
