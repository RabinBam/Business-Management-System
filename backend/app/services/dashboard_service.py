from app.schemas.dashboard import DashboardMetrics, DashboardRead
from app.schemas.workflow import WorkflowStatus
from app.services.report_service import get_report_service
from app.services.watcher_service import watcher_service
from app.services.workflow_service import WorkflowService, get_workflow_service


class DashboardService:
    def __init__(self, workflow_service: WorkflowService | None = None) -> None:
        self._workflow_service = workflow_service or get_workflow_service()

    def get(self) -> DashboardRead:
        workflows = self._workflow_service.list()
        workflow_ids = {workflow.id for workflow in workflows}
        reports = [
            report
            for report in get_report_service().list_reports()
            if report.workflow_id in workflow_ids
        ]
        planned_spend = sum(report.financial.planned_spend for report in reports)
        predicted_growth = (
            sum(report.sales_prediction.growth_percent for report in reports)
            / len(reports)
            if reports
            else 0
        )
        total_budget = sum(workflow.budget for workflow in workflows)
        terminal = {
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        }
        return DashboardRead(
            metrics=DashboardMetrics(
                workflow_count=len(workflows),
                active_workflows=sum(workflow.status not in terminal for workflow in workflows),
                completed_workflows=sum(
                    workflow.status is WorkflowStatus.COMPLETED for workflow in workflows
                ),
                failed_workflows=sum(
                    workflow.status is WorkflowStatus.FAILED for workflow in workflows
                ),
                total_budget=total_budget,
                planned_spend=planned_spend,
                available_budget=total_budget - planned_spend,
                predicted_growth_percent=round(predicted_growth, 2),
            ),
            recent_workflows=workflows[:5],
            recent_events=[
                event
                for event in watcher_service.status().events
                if event.workflow_id is None or event.workflow_id in workflow_ids
            ][:8],
        )


dashboard_service = DashboardService()
