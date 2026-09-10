from fastapi import APIRouter, HTTPException, status

from app.integrations import generate_marketing_for_workflow
from app.schemas.common import ApiResponse
from app.schemas.marketing import MarketingPlan
from app.services.ai_service import AIServiceError
from app.services.marketing_service import marketing_service
from app.services.report_service import get_report_service
from app.services.workflow_service import WorkflowConflictError, get_workflow_service

router = APIRouter(prefix="/workflows", tags=["marketing"])


@router.post("/{workflow_id}/marketing/generate", response_model=ApiResponse[MarketingPlan])
async def generate_marketing_plan(workflow_id: str) -> ApiResponse[MarketingPlan]:
    service = get_workflow_service()
    if service.get(workflow_id) is None:
        raise HTTPException(404, "Workflow not found")
    async with service._get_run_lock(workflow_id):
        return await _generate_marketing_locked(workflow_id)


async def _generate_marketing_locked(workflow_id: str) -> ApiResponse[MarketingPlan]:
    workflow = get_workflow_service().get(workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow '{workflow_id}' was not found.",
            },
        )
    if workflow.status in {"FINAL_REVIEW", "COMPLETED"}:
        raise HTTPException(409, "Marketing is already confirmed for final review.")
    report = get_report_service().get_report(workflow_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPORT_NOT_READY",
                "message": "Generate the workflow report before marketing.",
            },
        )
    try:
        plan = await generate_marketing_for_workflow(workflow, report)
    except AIServiceError as exc:
        raise HTTPException(502, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            422, "AI marketing allocations exceeded the budget. Retry generation."
        ) from exc
    get_workflow_service().invalidate_summary(workflow_id)
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
    return await _save_draft(workflow_id, plan, approve=False)


async def _save_draft(workflow_id: str, plan: MarketingPlan, *, approve: bool):
    if get_workflow_service().get(workflow_id) is None:
        raise HTTPException(404, "Workflow not found")
    try:
        saved = await get_workflow_service().save_marketing_draft(
            workflow_id,
            plan,
            approve=approve,
        )
    except WorkflowConflictError as exc:
        raise HTTPException(409, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return ApiResponse(
        data=saved,
        message=(
            "Marketing approved for final review"
            if approve
            else "Draft saved; awaiting marketing approval"
        ),
    )


@router.post("/{workflow_id}/marketing/approve", response_model=ApiResponse[MarketingPlan])
async def approve_marketing(workflow_id: str, plan: MarketingPlan):
    if plan.workflow_id != workflow_id:
        raise HTTPException(409, "Path and marketing-plan workflow IDs must match")
    return await _save_draft(workflow_id, plan, approve=True)


@router.post("/{workflow_id}/summary/refresh")
async def refresh_summary(workflow_id: str):
    if get_workflow_service().get(workflow_id) is None:
        raise HTTPException(404, "Workflow not found")
    plan = marketing_service.get_plan(workflow_id)
    report = get_report_service().get_report(workflow_id)
    if plan is None or report is None:
        raise HTTPException(409, "Complete reporting and marketing first")
    try:
        workflow = await get_workflow_service().refresh_summary(workflow_id, report, plan)
    except WorkflowConflictError as exc:
        raise HTTPException(409, str(exc)) from exc
    except AIServiceError as exc:
        raise HTTPException(502, str(exc)) from exc
    return ApiResponse(data=workflow, message="CEO summary updated")
