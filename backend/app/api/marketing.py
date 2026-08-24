from fastapi import APIRouter, HTTPException, status

from app.integrations import generate_marketing_for_workflow
from app.schemas.common import ApiResponse
from app.schemas.marketing import MarketingPlan
from app.services.marketing_service import marketing_service
from app.services.report_service import get_report_service
from app.services.workflow_service import get_workflow_service

router = APIRouter(prefix="/workflows", tags=["marketing"])


@router.post("/{workflow_id}/marketing/generate", response_model=ApiResponse[MarketingPlan])
async def generate_marketing_plan(workflow_id: str) -> ApiResponse[MarketingPlan]:
    workflow = get_workflow_service().get(workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow '{workflow_id}' was not found.",
            },
        )
    report = get_report_service().get_report(workflow_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPORT_NOT_READY",
                "message": "Generate the workflow report before marketing.",
            },
        )
    plan = await generate_marketing_for_workflow(workflow, report)
    return ApiResponse(data=plan, message="Marketing plan generated")


@router.get("/{workflow_id}/marketing", response_model=ApiResponse[MarketingPlan])
async def get_marketing_plan(workflow_id: str) -> ApiResponse[MarketingPlan]:
    plan = marketing_service.get_plan(workflow_id)
    if plan is not None:
        return ApiResponse(data=plan, message="Marketing plan loaded")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "MARKETING_NOT_READY",
            "message": f"The marketing plan for workflow '{workflow_id}' is not ready.",
        },
    )


@router.put("/{workflow_id}/marketing", response_model=ApiResponse[MarketingPlan])
async def update_marketing_plan(
    workflow_id: str, plan: MarketingPlan
) -> ApiResponse[MarketingPlan]:
    if plan.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "WORKFLOW_ID_MISMATCH",
                "message": "Path and marketing-plan workflow IDs must match.",
            },
        )
    try:
        saved = marketing_service.save_plan(plan)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"code": "BUDGET_EXCEEDED", "message": str(exc)},
        ) from exc
    return ApiResponse(data=saved, message="Marketing plan saved")
