from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ApiResponse
from app.services.worker_service import get_worker_service
from app.services.workflow_service import (
    WorkflowConflictError,
    WorkflowNotFoundError,
    WorkflowValidationError,
    get_workflow_service,
)

router = APIRouter(prefix="/employees", tags=["employees"])


class Submission(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    deliverable: str = Field(min_length=10, max_length=20000)


@router.get("/{worker_id}/tasks")
async def employee_tasks(worker_id: str):
    if get_worker_service().get_worker(worker_id) is None:
        raise HTTPException(404, "Employee not found")
    service = get_workflow_service()
    items = []
    for workflow in service.list():
        results = {r.task_id: r for r in service.get_worker_results(workflow.id) or []}
        reviews = {r.task_id: r for r in service.get_reviews(workflow.id) or []}
        for task in service.get_tasks(workflow.id) or []:
            if task.assigned_worker_id == worker_id:
                items.append(
                    {
                        "workflow": workflow,
                        "task": task,
                        "result": results.get(task.id),
                        "review": reviews.get(task.id),
                        "ready": set(task.dependency_task_ids) <= set(results),
                    }
                )
    return ApiResponse(data=items)


@router.post("/{worker_id}/tasks/{workflow_id}/{task_id}/submit")
async def submit(worker_id: str, workflow_id: str, task_id: str, payload: Submission):
    try:
        result = await get_workflow_service().submit_employee_work(
            workflow_id,
            task_id,
            worker_id,
            payload.deliverable.strip(),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(404, "Workflow not found") from exc
    except (WorkflowConflictError, WorkflowValidationError) as exc:
        raise HTTPException(409, str(exc)) from exc
    return ApiResponse(data=result, message="Work submitted for review")
