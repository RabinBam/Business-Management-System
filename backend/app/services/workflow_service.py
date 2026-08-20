from uuid import uuid4

from app.schemas.task import TaskRead
from app.schemas.workflow import WorkflowCreate, WorkflowRead, WorkflowStatus


class WorkflowService:
    """Small in-memory adapter. Replace storage without changing the router contract."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowRead] = {}
        self._tasks: dict[str, list[TaskRead]] = {}

    def create(self, payload: WorkflowCreate) -> WorkflowRead:
        workflow_id = f"wf-{uuid4().hex[:8]}"
        workflow = WorkflowRead(id=workflow_id, **payload.model_dump())
        self._workflows[workflow_id] = workflow
        self._tasks[workflow_id] = []
        return workflow

    def get(self, workflow_id: str) -> WorkflowRead | None:
        return self._workflows.get(workflow_id)

    def run(self, workflow_id: str) -> WorkflowRead | None:
        workflow = self.get(workflow_id)
        if workflow is None:
            return None
        # Person 1: replace this transition with the orchestrated, watched pipeline.
        workflow.status = WorkflowStatus.SEGMENTING
        workflow.current_stage = "objective_segmentation"
        return workflow

    def get_tasks(self, workflow_id: str) -> list[TaskRead] | None:
        return self._tasks.get(workflow_id)


_workflow_service = WorkflowService()


def get_workflow_service() -> WorkflowService:
    return _workflow_service

