from fastapi import APIRouter, HTTPException, status

from app.schemas.common import ApiResponse
from app.schemas.marketing import MarketingPlan
from app.services.marketing_service import marketing_service

router = APIRouter(prefix="/workflows", tags=["marketing"])

@router.get("/{workflow_id}/marketing", response_model=ApiResponse[MarketingPlan])
async def get_marketing_plan(workflow_id: str) -> ApiResponse[MarketingPlan]:
    # Hooked up to the service
    plan = marketing_service.get_plan(workflow_id)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "MARKETING_NOT_READY",
                "message": f"The marketing plan for workflow '{workflow_id}' is not ready.",
            },
        )
        
    return ApiResponse(data=plan, message="Marketing plan loaded")

@router.put("/{workflow_id}/marketing", response_model=ApiResponse[MarketingPlan])
async def update_marketing_plan(
    workflow_id: str, plan: MarketingPlan
) -> ApiResponse[MarketingPlan]:
    if getattr(plan, 'workflow_id', None) != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "WORKFLOW_ID_MISMATCH",
                "message": "Path and marketing-plan workflow IDs must match.",
            },
        )
    try:
        plan.validate_budget()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"code": "BUDGET_EXCEEDED", "message": str(exc)},
        ) from exc
        
    # Hooked up to save the valid plan in memory
    marketing_service.save_plan(plan)
    
    return ApiResponse(data=plan, message="Marketing plan validated and saved")