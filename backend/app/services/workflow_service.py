<<<<<<< HEAD
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

=======
import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from threading import RLock
from uuid import uuid4

from app.agents.manager import Manager
from app.agents.orchestrator import Orchestrator
from app.config import settings
from app.schemas.marketing import MarketingPlan
from app.schemas.report import Report
from app.schemas.task import ManagementDecision, ManagementReview, TaskRead, TaskStatus
from app.schemas.worker import WorkerResult
from app.schemas.workflow import (
    ExecutiveSummary,
    WorkflowCreate,
    WorkflowFailure,
    WorkflowRead,
    WorkflowStatus,
)
from app.services.ai_service import AIService, get_ai_service

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

WorkerExecutor = Callable[
    [list[TaskRead]], Awaitable[list[WorkerResult]] | list[WorkerResult]
]
ReportGenerator = Callable[
    [WorkflowRead, list[TaskRead], list[WorkerResult], list[ManagementReview]],
    Awaitable[Report] | Report,
]
MarketingGenerator = Callable[
    [WorkflowRead, Report], Awaitable[MarketingPlan] | MarketingPlan
]
EventRecorder = Callable[[str, str, str, str, int], None]


@dataclass(frozen=True)
class WorkflowCollaborators:
    """Ports implemented by Persons 2 and 3; Person 1 only coordinates them.

    ``record_event`` receives workflow ID, component, event type, message, and
    retry count. A Watcher adapter can consume these without coupling this
    service to Person 3's persistence implementation.
    """

    execute_workers: WorkerExecutor | None = None
    generate_report: ReportGenerator | None = None
    generate_marketing: MarketingGenerator | None = None
    record_event: EventRecorder | None = None


@dataclass
class WorkflowArtifacts:
    worker_results: list[WorkerResult] = field(default_factory=list)
    reviews: list[ManagementReview] = field(default_factory=list)
    report: Report | None = None
    marketing: MarketingPlan | None = None


class WorkflowServiceError(RuntimeError):
    """Base exception for workflow application rules."""


class WorkflowNotFoundError(WorkflowServiceError):
    pass


class WorkflowConflictError(WorkflowServiceError):
    pass


class WorkflowValidationError(WorkflowServiceError):
    pass


class WorkflowExecutionError(WorkflowServiceError):
    def __init__(self, workflow: WorkflowRead) -> None:
        super().__init__(workflow.failure.message if workflow.failure else "Workflow failed")
        self.workflow = workflow


class WorkflowService:
    """Person 1 workflow repository, state machine, and integration coordinator."""

    def __init__(
        self,
        *,
        ai_service: AIService | None = None,
        collaborators: WorkflowCollaborators | None = None,
    ) -> None:
        self._workflows: dict[str, WorkflowRead] = {}
        self._tasks: dict[str, list[TaskRead]] = {}
        self._artifacts: dict[str, WorkflowArtifacts] = {}
        self._run_locks: dict[str, asyncio.Lock] = {}
        self._lock = RLock()
        self._ai_service = ai_service
        self._collaborators = collaborators or WorkflowCollaborators()
        self._manager: Manager | None = None

    def configure_collaborators(self, collaborators: WorkflowCollaborators) -> None:
        self._collaborators = collaborators

    def create(self, payload: WorkflowCreate) -> WorkflowRead:
        if payload.deadline < date.today():
            raise WorkflowValidationError("Workflow deadline cannot be in the past")
        workflow_id = f"wf-{uuid4().hex[:8]}"
        workflow = WorkflowRead(id=workflow_id, **payload.model_dump())
        with self._lock:
            self._workflows[workflow_id] = workflow
            self._tasks[workflow_id] = []
            self._artifacts[workflow_id] = WorkflowArtifacts()
            self._run_locks[workflow_id] = asyncio.Lock()
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
            updated = workflow.model_copy(deep=True)
        self._record_event(
            workflow_id,
            "workflow_service",
            "STATUS_CHANGED",
            f"Workflow entered {target}",
            0,
        )
        return updated

    async def run_workflow(self, workflow_id: str) -> WorkflowRead:
        run_lock = self._get_run_lock(workflow_id)
        async with run_lock:
            return await self._run_workflow_locked(workflow_id)

    async def _run_workflow_locked(self, workflow_id: str) -> WorkflowRead:
        workflow = self.require(workflow_id)
        if workflow.status is WorkflowStatus.COMPLETED:
            return workflow
        if workflow.status is WorkflowStatus.FAILED:
            raise WorkflowConflictError("A failed workflow cannot be resumed")
        if workflow.status in {WorkflowStatus.SEGMENTING, WorkflowStatus.ASSIGNING}:
            raise WorkflowConflictError(
                f"Workflow cannot resume from transient state {workflow.status}"
            )

        try:
            if workflow.status is WorkflowStatus.CREATED:
                workflow = await self._plan_and_refine(workflow)
            if workflow.status is WorkflowStatus.EXECUTING:
                workflow = await self._execute_workers(workflow)
            if workflow.status is WorkflowStatus.REVIEWING:
                workflow = await self._review_results(workflow)
            if workflow.status is WorkflowStatus.REPORTING:
                workflow = await self._generate_report(workflow)
            if workflow.status is WorkflowStatus.MARKETING:
                workflow = await self._generate_marketing(workflow)
            if workflow.status is WorkflowStatus.FINAL_REVIEW:
                workflow = await self._finalize(workflow)
            return workflow
        except (WorkflowNotFoundError, WorkflowConflictError, WorkflowValidationError):
            raise
        except Exception as exc:
            failed = self.fail(
                workflow_id,
                code="WORKFLOW_EXECUTION_FAILED",
                message=f"{exc.__class__.__name__}: {exc}",
            )
            raise WorkflowExecutionError(failed) from exc

    async def _plan_and_refine(self, workflow: WorkflowRead) -> WorkflowRead:
        self.transition(workflow.id, WorkflowStatus.SEGMENTING)
        orchestrator = self._build_orchestrator(workflow.id)
        manager = self._get_manager()
        generated = await orchestrator.segment(
            objective=workflow.objective,
            budget=workflow.budget,
            deadline=workflow.deadline,
        )

        self.transition(workflow.id, WorkflowStatus.ASSIGNING)
        tasks: list[TaskRead] = []
        for index, task in enumerate(generated, start=1):
            refined = await manager.refine_task(task)
            tasks.append(
                TaskRead(
                    id=f"task-{index:03d}",
                    workflow_id=workflow.id,
                    **refined.model_dump(),
                )
            )
        self.replace_tasks(workflow.id, tasks)
        return self.transition(workflow.id, WorkflowStatus.EXECUTING)

    async def _execute_workers(self, workflow: WorkflowRead) -> WorkflowRead:
        executor = self._collaborators.execute_workers
        if executor is None:
            return workflow
        tasks = self.get_tasks(workflow.id) or []
        self._set_all_task_statuses(workflow.id, TaskStatus.RUNNING)
        results = await _await_if_needed(executor(tasks))
        self._validate_worker_results(tasks, results)
        self._artifacts[workflow.id].worker_results = [
            result.model_copy(deep=True) for result in results
        ]
        self._set_all_task_statuses(workflow.id, TaskStatus.COMPLETED)
        return self.transition(workflow.id, WorkflowStatus.REVIEWING)

    async def _review_results(self, workflow: WorkflowRead) -> WorkflowRead:
        tasks = self.get_tasks(workflow.id) or []
        artifacts = self._artifacts[workflow.id]
        if not artifacts.worker_results:
            raise WorkflowConflictError("Worker results are unavailable for management review")
        manager = self._get_manager()
        reviews = await manager.review_results(
            tasks=tasks,
            results=artifacts.worker_results,
        )
        artifacts.reviews = [review.model_copy(deep=True) for review in reviews]
        if any(
            review.decision is ManagementDecision.REVISION_REQUIRED for review in reviews
        ):
            return workflow
        return self.transition(workflow.id, WorkflowStatus.REPORTING)

    async def _generate_report(self, workflow: WorkflowRead) -> WorkflowRead:
        generator = self._collaborators.generate_report
        if generator is None:
            return workflow
        tasks = self.get_tasks(workflow.id) or []
        artifacts = self._artifacts[workflow.id]
        report = await _await_if_needed(
            generator(workflow, tasks, artifacts.worker_results, artifacts.reviews)
        )
        if report.workflow_id != workflow.id:
            raise WorkflowValidationError("Report belongs to a different workflow")
        artifacts.report = report.model_copy(deep=True)
        return self.transition(workflow.id, WorkflowStatus.MARKETING)

    async def _generate_marketing(self, workflow: WorkflowRead) -> WorkflowRead:
        generator = self._collaborators.generate_marketing
        if generator is None:
            return workflow
        artifacts = self._artifacts[workflow.id]
        if artifacts.report is None:
            raise WorkflowConflictError("Report is unavailable for marketing generation")
        marketing = await _await_if_needed(generator(workflow, artifacts.report))
        if marketing.workflow_id != workflow.id:
            raise WorkflowValidationError("Marketing plan belongs to a different workflow")
        artifacts.marketing = marketing.model_copy(deep=True)
        return self.transition(workflow.id, WorkflowStatus.FINAL_REVIEW)

    async def _finalize(self, workflow: WorkflowRead) -> WorkflowRead:
        artifacts = self._artifacts[workflow.id]
        if artifacts.report is None or artifacts.marketing is None:
            raise WorkflowConflictError("Final review inputs are incomplete")
        manager = self._get_manager()
        summary = await manager.create_executive_summary(
            workflow=workflow,
            report=artifacts.report,
            marketing=artifacts.marketing,
            reviews=artifacts.reviews,
        )
        self.store_executive_summary(workflow.id, summary)
        return self.transition(workflow.id, WorkflowStatus.COMPLETED)

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
            failed = workflow.model_copy(deep=True)
        self._record_event(
            workflow_id,
            "workflow_service",
            "FAILED",
            message,
            0,
        )
        return failed

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

    def clear(self) -> None:
        """Clear volatile storage for isolated tests."""

        with self._lock:
            self._workflows.clear()
            self._tasks.clear()
            self._artifacts.clear()
            self._run_locks.clear()

    def _set_all_task_statuses(self, workflow_id: str, status: TaskStatus) -> None:
        tasks = self.get_tasks(workflow_id)
        if tasks is None:
            raise WorkflowNotFoundError(workflow_id)
        self.replace_tasks(
            workflow_id,
            [task.model_copy(update={"status": status}) for task in tasks],
        )

    @staticmethod
    def _validate_worker_results(
        tasks: list[TaskRead], results: list[WorkerResult]
    ) -> None:
        task_ids = {task.id for task in tasks}
        result_ids = [result.task_id for result in results]
        if len(result_ids) != len(set(result_ids)):
            raise WorkflowValidationError("Worker results contain duplicate task IDs")
        if set(result_ids) != task_ids:
            raise WorkflowValidationError("Worker results must cover every workflow task")

    def _build_orchestrator(self, workflow_id: str) -> Orchestrator:
        return Orchestrator(
            self._get_ai_service(),
            model=settings.ai_primary_model or None,
            max_tasks=settings.ai_max_tasks,
            validation_retries=1,
            on_validation_failure=lambda error, attempt: self._record_event(
                workflow_id,
                "orchestrator",
                "VALIDATION_FAILED",
                str(error),
                attempt,
            ),
        )

    def _get_manager(self) -> Manager:
        if self._manager is None:
            self._manager = Manager(
                self._get_ai_service(),
                model=settings.ai_primary_model or None,
            )
        return self._manager

    def _get_ai_service(self) -> AIService:
        if self._ai_service is None:
            self._ai_service = get_ai_service()
        return self._ai_service

    def _get_run_lock(self, workflow_id: str) -> asyncio.Lock:
        with self._lock:
            self._require_stored(workflow_id)
            return self._run_locks.setdefault(workflow_id, asyncio.Lock())

    def _record_event(
        self,
        workflow_id: str,
        component: str,
        event_type: str,
        message: str,
        retry_count: int,
    ) -> None:
        recorder = self._collaborators.record_event
        if recorder is None:
            return
        try:
            recorder(workflow_id, component, event_type, message, retry_count)
        except Exception:
            # Monitoring must never become a new workflow failure mode.
            return

    def _require_stored(self, workflow_id: str) -> WorkflowRead:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)
        return workflow


async def _await_if_needed[T](value: Awaitable[T] | T) -> T:
    if inspect.isawaitable(value):
        return await value
    return value


_workflow_service = WorkflowService()


def get_workflow_service() -> WorkflowService:
    return _workflow_service
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
