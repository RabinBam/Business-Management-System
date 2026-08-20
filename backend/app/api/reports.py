from fastapi import APIRouter, HTTPException, status

from app.schemas.common import ApiResponse
from app.schemas.report import Report

router = APIRouter(prefix="/workflows", tags=["reports"])


@router.get("/{workflow_id}/report", response_model=ApiResponse[Report])
async def get_report(workflow_id: str) -> ApiResponse[Report]:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "REPORT_NOT_READY",
            "message": f"The report for workflow '{workflow_id}' is not ready.",
        },
    )

