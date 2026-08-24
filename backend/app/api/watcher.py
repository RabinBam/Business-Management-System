from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.watcher import WatcherEvent, WatcherStatus
from app.services.watcher_service import watcher_service

router = APIRouter(prefix="/watcher", tags=["watcher"])


@router.get("", response_model=ApiResponse[WatcherStatus])
async def get_watcher_status() -> ApiResponse[WatcherStatus]:
    return ApiResponse(data=watcher_service.status(), message="Watcher status loaded")


@router.get("/status", response_model=ApiResponse[WatcherStatus])
async def get_watcher_status_alias() -> ApiResponse[WatcherStatus]:
    return ApiResponse(data=watcher_service.status(), message="Watcher status loaded")


@router.get("/events", response_model=ApiResponse[list[WatcherEvent]])
async def get_watcher_events() -> ApiResponse[list[WatcherEvent]]:
    return ApiResponse(data=watcher_service.status().events, message="Watcher events loaded")
