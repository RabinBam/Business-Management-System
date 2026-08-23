from datetime import UTC, date, datetime
from threading import RLock
from uuid import uuid4

from app.schemas.task import TaskRead
from app.schemas.workflow import (
    ExecutiveSummary,
    WorkflowCreate,
    WorkflowFailure,
    WorkflowRead,
    WorkflowStatus,
)

STAGE_NAMES: dict[WorkflowStatus, str] = {
    WorkflowStatus.CREATED: "created",
    WorkflowStatus.SEGMENTING: "objective_segmentation",
    WorkflowStatus.ASSIGNING: "management_refinement",
    WorkflowStatus.EXECUTING: "worker_execution",
    WorkflowStatus.REVIEWING: "management_review",
    WorkflowStatus.REPORTING: "report_generation",
    WorkflowStatus.MARKETING: "marketing_planning",
    WorkflowStatus.FINAL_REVIEW: "management_final_review",
    WorkflowStatus.COMPLETED: "completed",
    WorkflowStatus.FAILED: "failed",
}

ALLOWED_TRANSITIONS: dict[WorkflowStatus, set[WorkflowStatus]] = {
    WorkflowStatus.CREATED: {WorkflowStatus.SEGMENTING, WorkflowStatus.FAILED},
    WorkflowStatus.SEGMENTING: {WorkflowStatus.ASSIGNING, WorkflowStatus.FAILED},
    WorkflowStatus.ASSIGNING: {WorkflowStatus.EXECUTING, WorkflowStatus.FAILED},
    WorkflowStatus.EXECUTING: {WorkflowStatus.REVIEWING, WorkflowStatus.FAILED},
    WorkflowStatus.REVIEWING: {WorkflowStatus.REPORTING, WorkflowStatus.FAILED},
    WorkflowStatus.REPORTING: {WorkflowStatus.MARKETING, WorkflowStatus.FAILED},
    WorkflowStatus.MARKETING: {WorkflowStatus.FINAL_REVIEW, WorkflowStatus.FAILED},
    WorkflowStatus.FINAL_REVIEW: {WorkflowStatus.COMPLETED, WorkflowStatus.FAILED},
    WorkflowStatus.COMPLETED: set(),
    WorkflowStatus.FAILED: set(),
}


class WorkflowServiceError(RuntimeError):
    """Base exception for workflow application rules."""


class WorkflowNotFoundError(WorkflowServiceError):
    pass


class WorkflowConflictError(WorkflowServiceError):
    pass


class WorkflowValidationError(WorkflowServiceError):
    pass


class WorkflowService:
    """Thread-safe in-memory workflow repository and state transition owner."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowRead] = {}
        self._tasks: dict[str, list[TaskRead]] = {}
        self._lock = RLock()

    def create(self, payload: WorkflowCreate) -> WorkflowRead:
        if payload.deadline < date.today():
            raise WorkflowValidationError("Workflow deadline cannot be in the past")
        workflow_id = f"wf-{uuid4().hex[:8]}"
        workflow = WorkflowRead(id=workflow_id, **payload.model_dump())
        with self._lock:
            self._workflows[workflow_id] = workflow
            self._tasks[workflow_id] = []
        return workflow.model_copy(deep=True)

    def get(self, workflow_id: str) -> WorkflowRead | None:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            return workflow.model_copy(deep=True) if workflow is not None else None

    def require(self, workflow_id: str) -> WorkflowRead:
        workflow = self.get(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)
        return workflow

    def get_tasks(self, workflow_id: str) -> list[TaskRead] | None:
        with self._lock:
            tasks = self._tasks.get(workflow_id)
            return [task.model_copy(deep=True) for task in tasks] if tasks is not None else None

    def replace_tasks(self, workflow_id: str, tasks: list[TaskRead]) -> list[TaskRead]:
        with self._lock:
            self._require_stored(workflow_id)
            if any(task.workflow_id != workflow_id for task in tasks):
                raise WorkflowValidationError("Every task must belong to the workflow")
            ids = [task.id for task in tasks]
            if len(ids) != len(set(ids)):
                raise WorkflowValidationError("Task IDs must be unique within a workflow")
            self._tasks[workflow_id] = [task.model_copy(deep=True) for task in tasks]
            return [task.model_copy(deep=True) for task in tasks]

    def transition(self, workflow_id: str, target: WorkflowStatus) -> WorkflowRead:
        with self._lock:
            workflow = self._require_stored(workflow_id)
            if target not in ALLOWED_TRANSITIONS[workflow.status]:
                raise WorkflowConflictError(
                    f"Cannot transition workflow from {workflow.status} to {target}"
                )
            now = datetime.now(UTC)
            workflow.status = target
            workflow.current_stage = STAGE_NAMES[target]
            workflow.updated_at = now
            if target is WorkflowStatus.SEGMENTING and workflow.started_at is None:
                workflow.started_at = now
            if target is WorkflowStatus.COMPLETED:
                workflow.completed_at = now
            return workflow.model_copy(deep=True)

    def fail(
        self,
        workflow_id: str,
        *,
        code: str,
        message: str,
    ) -> WorkflowRead:
        with self._lock:
            workflow = self._require_stored(workflow_id)
            if workflow.status is WorkflowStatus.COMPLETED:
                raise WorkflowConflictError("A completed workflow cannot be failed")
            failed_stage = workflow.status
            now = datetime.now(UTC)
            workflow.status = WorkflowStatus.FAILED
            workflow.current_stage = STAGE_NAMES[WorkflowStatus.FAILED]
            workflow.updated_at = now
            workflow.completed_at = now
            workflow.failure = WorkflowFailure(
                code=code,
                message=message,
                failed_stage=failed_stage,
            )
            return workflow.model_copy(deep=True)

    def store_executive_summary(
        self,
        workflow_id: str,
        summary: ExecutiveSummary,
    ) -> WorkflowRead:
        with self._lock:
            workflow = self._require_stored(workflow_id)
            if workflow.status is not WorkflowStatus.FINAL_REVIEW:
                raise WorkflowConflictError(
                    "Executive summary can be stored only during final review"
                )
            workflow.executive_summary = summary.model_copy(deep=True)
            workflow.updated_at = datetime.now(UTC)
            return workflow.model_copy(deep=True)

    def run(self, workflow_id: str) -> WorkflowRead:
        """Compatibility transition used until the async pipeline is connected."""

        return self.transition(workflow_id, WorkflowStatus.SEGMENTING)

    def clear(self) -> None:
        """Clear volatile storage for isolated tests."""

        with self._lock:
            self._workflows.clear()
            self._tasks.clear()

    def _require_stored(self, workflow_id: str) -> WorkflowRead:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)
        return workflow


_workflow_service = WorkflowService()


def get_workflow_service() -> WorkflowService:
    return _workflow_service
