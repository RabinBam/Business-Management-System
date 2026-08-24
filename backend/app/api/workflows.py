from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.integrations import delete_workflow_artifacts
from app.schemas.common import ApiResponse
from app.schemas.task import ManagementReview, TaskRead
from app.schemas.worker import WorkerResult
from app.schemas.workflow import WorkflowCreate, WorkflowRead, WorkflowStatusRead
from app.security import require_admin_key
from app.services.workflow_service import (
    WorkflowConflictError,
    WorkflowExecutionError,
    WorkflowNotFoundError,
    WorkflowService,
    WorkflowValidationError,
    get_workflow_service,
)

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


def _workflow_error(
    *,
    status_code: int,
    code: str,
    message: str,
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


@router.post("", response_model=ApiResponse[WorkflowRead], status_code=201)
async def create_workflow(payload: WorkflowCreate, service: Service) -> ApiResponse[WorkflowRead]:
    try:
        workflow = service.create(payload)
    except WorkflowValidationError as exc:
        raise _workflow_error(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="WORKFLOW_INVALID",
            message=str(exc),
        ) from exc
    return ApiResponse(data=workflow, message="Workflow created")


@router.get("", response_model=ApiResponse[list[WorkflowRead]])
async def list_workflows(service: Service) -> ApiResponse[list[WorkflowRead]]:
    return ApiResponse(data=service.list(), message="Workflows loaded")


@router.get("/{workflow_id}", response_model=ApiResponse[WorkflowRead])
async def get_workflow(workflow_id: str, service: Service) -> ApiResponse[WorkflowRead]:
    workflow = service.get(workflow_id)
    if workflow is None:
        raise _not_found(workflow_id)
    return ApiResponse(data=workflow, message="Workflow loaded")


@router.get("/{workflow_id}/status", response_model=ApiResponse[WorkflowStatusRead])
async def get_workflow_status(
    workflow_id: str, service: Service
) -> ApiResponse[WorkflowStatusRead]:
    workflow = service.get(workflow_id)
    if workflow is None:
        raise _not_found(workflow_id)
    return ApiResponse(
        data=WorkflowStatusRead.model_validate(workflow.model_dump()),
        message="Workflow status loaded",
    )


@router.post("/{workflow_id}/refine", response_model=ApiResponse[WorkflowRead])
async def refine_workflow(
    workflow_id: str, service: Service
) -> ApiResponse[WorkflowRead]:
    if service.get(workflow_id) is None:
        raise _not_found(workflow_id)
    try:
        workflow = await service.prepare_workflow(workflow_id)
    except WorkflowConflictError as exc:
        raise _workflow_error(
            status_code=status.HTTP_409_CONFLICT,
            code="WORKFLOW_CONFLICT",
            message=str(exc),
        ) from exc
    return ApiResponse(data=workflow, message="Workflow tasks refined")


@router.post("/{workflow_id}/retry", response_model=ApiResponse[WorkflowRead])
async def retry_workflow(
    workflow_id: str, service: Service
) -> ApiResponse[WorkflowRead]:
    if service.get(workflow_id) is None:
        raise _not_found(workflow_id)
    try:
        workflow = service.retry_failed(workflow_id)
    except WorkflowConflictError as exc:
        raise _workflow_error(
            status_code=status.HTTP_409_CONFLICT,
            code="WORKFLOW_CONFLICT",
            message=str(exc),
        ) from exc
    return ApiResponse(data=workflow, message="Workflow ready to retry")


@router.post("/{workflow_id}/cancel", response_model=ApiResponse[WorkflowRead])
async def cancel_workflow(
    workflow_id: str, service: Service
) -> ApiResponse[WorkflowRead]:
    if service.get(workflow_id) is None:
        raise _not_found(workflow_id)
    try:
        workflow = service.cancel(workflow_id)
    except WorkflowConflictError as exc:
        raise _workflow_error(
            status_code=status.HTTP_409_CONFLICT,
            code="WORKFLOW_CONFLICT",
            message=str(exc),
        ) from exc
    return ApiResponse(data=workflow, message="Workflow cancelled")


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_key)],
)
async def delete_workflow(workflow_id: str, service: Service) -> None:
    if service.get(workflow_id) is None:
        raise _not_found(workflow_id)
    service.delete(workflow_id)
    delete_workflow_artifacts(workflow_id)


@router.post("/{workflow_id}/run", response_model=ApiResponse[WorkflowRead])
async def run_workflow(workflow_id: str, service: Service) -> ApiResponse[WorkflowRead]:
    if service.get(workflow_id) is None:
        raise _not_found(workflow_id)
    try:
        workflow = await service.run_workflow(workflow_id)
    except WorkflowNotFoundError as exc:
        raise _not_found(workflow_id) from exc
    except WorkflowConflictError as exc:
        raise _workflow_error(
            status_code=status.HTTP_409_CONFLICT,
            code="WORKFLOW_CONFLICT",
            message=str(exc),
        ) from exc
    except WorkflowValidationError as exc:
        raise _workflow_error(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="WORKFLOW_INVALID",
            message=str(exc),
        ) from exc
    except WorkflowExecutionError as exc:
        raise _workflow_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="WORKFLOW_EXECUTION_FAILED",
            message=str(exc),
        ) from exc
    return ApiResponse(data=workflow, message="Workflow advanced")


@router.get("/{workflow_id}/tasks", response_model=ApiResponse[list[TaskRead]])
async def get_tasks(workflow_id: str, service: Service) -> ApiResponse[list[TaskRead]]:
    tasks = service.get_tasks(workflow_id)
    if tasks is None:
        raise _not_found(workflow_id)
    return ApiResponse(data=tasks, message="Tasks loaded")


@router.get("/{workflow_id}/results", response_model=ApiResponse[list[WorkerResult]])
async def get_results(
    workflow_id: str, service: Service
) -> ApiResponse[list[WorkerResult]]:
    results = service.get_worker_results(workflow_id)
    if results is None:
        raise _not_found(workflow_id)
    return ApiResponse(data=results, message="Worker results loaded")


@router.get("/{workflow_id}/reviews", response_model=ApiResponse[list[ManagementReview]])
async def get_reviews(
    workflow_id: str, service: Service
) -> ApiResponse[list[ManagementReview]]:
    reviews = service.get_reviews(workflow_id)
    if reviews is None:
        raise _not_found(workflow_id)
    return ApiResponse(data=reviews, message="Management reviews loaded")
