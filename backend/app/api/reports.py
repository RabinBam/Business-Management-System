from fastapi import APIRouter, HTTPException, status

from app.schemas.common import ApiResponse
from app.schemas.report import Report
from app.services.report_service import get_report_service
from app.services.workflow_service import get_workflow_service

router = APIRouter(prefix="/workflows", tags=["reports"])


@router.get("/{workflow_id}/report", response_model=ApiResponse[Report])
async def get_report(workflow_id: str) -> ApiResponse[Report]:
    """Return the financial and prediction report for a workflow.

    If a report has already been generated it is returned from cache.
    Otherwise the service builds a fresh report from the workflow's
    budget and the current sales prediction data.
    """
    report_service = get_report_service()
    workflow_service = get_workflow_service()

    # Try the cache first.
    report = report_service.get_report(workflow_id)
    if report is not None:
        return ApiResponse(data=report, message="Report loaded")

    # No cached report — generate one if the workflow exists.
    workflow = workflow_service.get(workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow '{workflow_id}' was not found.",
            },
        )

    report = report_service.generate_report(workflow)
    return ApiResponse(data=report, message="Report generated")
