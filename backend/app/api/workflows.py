from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.common import ApiResponse
from app.schemas.task import TaskRead
from app.schemas.workflow import WorkflowCreate, WorkflowRead
from app.services.workflow_service import WorkflowService, get_workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])
Service = Annotated[WorkflowService, Depends(get_workflow_service)]


def _not_found(workflow_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "WORKFLOW_NOT_FOUND",
            "message": f"Workflow '{workflow_id}' was not found.",
        },
    )


@router.post("", response_model=ApiResponse[WorkflowRead], status_code=201)
async def create_workflow(payload: WorkflowCreate, service: Service) -> ApiResponse[WorkflowRead]:
    workflow = service.create(payload)
    return ApiResponse(data=workflow, message="Workflow created")


@router.get("/{workflow_id}", response_model=ApiResponse[WorkflowRead])
async def get_workflow(workflow_id: str, service: Service) -> ApiResponse[WorkflowRead]:
    workflow = service.get(workflow_id)
    if workflow is None:
        raise _not_found(workflow_id)
    return ApiResponse(data=workflow, message="Workflow loaded")


@router.post("/{workflow_id}/run", response_model=ApiResponse[WorkflowRead])
async def run_workflow(workflow_id: str, service: Service) -> ApiResponse[WorkflowRead]:
    workflow = service.run(workflow_id)
    if workflow is None:
        raise _not_found(workflow_id)
    return ApiResponse(data=workflow, message="Workflow started")


@router.get("/{workflow_id}/tasks", response_model=ApiResponse[list[TaskRead]])
async def get_tasks(workflow_id: str, service: Service) -> ApiResponse[list[TaskRead]]:
    tasks = service.get_tasks(workflow_id)
    if tasks is None:
        raise _not_found(workflow_id)
    return ApiResponse(data=tasks, message="Tasks loaded")

