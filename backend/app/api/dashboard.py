from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardRead
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=ApiResponse[DashboardRead])
async def get_dashboard() -> ApiResponse[DashboardRead]:
    return ApiResponse(data=dashboard_service.get(), message="Dashboard loaded")
