from fastapi import APIRouter

from app.api import dashboard, employees, marketing, money, reports, watcher, workers, workflows

api_router = APIRouter()
api_router.include_router(workflows.router)
api_router.include_router(reports.router)
api_router.include_router(marketing.router)
api_router.include_router(watcher.router)
api_router.include_router(workers.router)
api_router.include_router(dashboard.router)
api_router.include_router(employees.router)
api_router.include_router(money.router)

