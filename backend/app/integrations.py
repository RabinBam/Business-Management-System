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
        lambda: get_worker_agent().execute_all(tasks),
        workflow_id=workflow_id,
        max_retries=1,
    )


async def _generate_report_adapter(
    workflow: WorkflowRead,
    _tasks: list[TaskRead],
    results: list[WorkerResult],
    _reviews: list[ManagementReview],
) -> Report:
    return await generate_report_for_workflow(
        workflow,
        task_spend=sum(result.cost for result in results),
    )


async def generate_report_for_workflow(
    workflow: WorkflowRead,
    *,
    task_spend: float = 0,
) -> Report:
    """Run report generation through failure simulation and watcher recovery."""

    def operation() -> Report:
        if settings.simulate_report_failure:
            with _simulation_lock:
                if workflow.id not in _simulated_report_failures:
                    _simulated_report_failures.add(workflow.id)
                    raise RuntimeError("Simulated report generation failure")
        return get_report_service().generate_report(workflow, task_spend=task_spend)

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
        "approved_team_work": [
            {
                "task_id": r.task_id,
                "deliverable": str(r.output.get("deliverable", r.summary))[:2500],
            }
            for r in get_workflow_service().get_worker_results(workflow.id) or []
        ],
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
    valid_workflow_ids = {workflow.id for workflow in workflow_service.list()}
    get_report_service().prune_orphans(valid_workflow_ids)
    marketing_service.prune_orphans(valid_workflow_ids)
    watcher_service.prune_orphans(valid_workflow_ids)
    workflow_service.configure_collaborators(
        WorkflowCollaborators(
            execute_workers=_execute_workers,
            generate_report=_generate_report_adapter,
            generate_marketing=generate_marketing_for_workflow,
            record_event=_record_workflow_event,
        )
    )
    return workflow_service


def delete_workflow_artifacts(workflow_id: str) -> None:
    """Remove cross-service records after the workflow aggregate is deleted."""

    get_report_service().delete_report(workflow_id)
    marketing_service.delete_plan(workflow_id)
    watcher_service.delete_workflow_events(workflow_id)
