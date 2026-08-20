from fastapi import APIRouter

from app.api import marketing, reports, watcher, workflows

api_router = APIRouter()
api_router.include_router(workflows.router)
api_router.include_router(reports.router)
api_router.include_router(marketing.router)
api_router.include_router(watcher.router)

