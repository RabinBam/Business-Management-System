from fastapi import APIRouter, HTTPException, status

from app.schemas.common import ApiResponse
from app.schemas.task import TaskRead
from app.schemas.worker import WorkerRead
from app.services.worker_service import get_worker_service
from app.services.workflow_service import get_workflow_service

router = APIRouter(prefix="/workers", tags=["workers"])


def _all_tasks() -> list[TaskRead]:
    workflow_service = get_workflow_service()
    return [
        task
        for workflow in workflow_service.list()
        for task in (workflow_service.get_tasks(workflow.id) or [])
    ]


@router.get("", response_model=ApiResponse[list[WorkerRead]])
async def list_workers() -> ApiResponse[list[WorkerRead]]:
    workers = get_worker_service().get_directory(_all_tasks())
    return ApiResponse(data=workers, message="Workers loaded")


@router.get("/{worker_id}", response_model=ApiResponse[WorkerRead])
async def get_worker(worker_id: str) -> ApiResponse[WorkerRead]:
    worker = next(
        (
            item
            for item in get_worker_service().get_directory(_all_tasks())
            if item.id == worker_id
        ),
        None,
    )
    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKER_NOT_FOUND",
                "message": f"Worker '{worker_id}' was not found.",
            },
        )
    return ApiResponse(data=worker, message="Worker loaded")
