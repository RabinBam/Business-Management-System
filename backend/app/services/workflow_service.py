from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import ROUND_DOWN, Decimal
from threading import RLock
from uuid import uuid4

from app.agents.manager import Manager
from app.agents.orchestrator import Orchestrator
from app.config import settings
from app.database import SQLiteJsonStore, get_json_store
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
from app.services.ai_service import AIService, MockAIProvider, get_ai_service
from app.services.worker_service import get_worker_service

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
    WorkflowStatus.CANCELLED: "cancelled",
}

ALLOWED_TRANSITIONS: dict[WorkflowStatus, set[WorkflowStatus]] = {
    WorkflowStatus.CREATED: {
        WorkflowStatus.SEGMENTING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.SEGMENTING: {
        WorkflowStatus.ASSIGNING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.ASSIGNING: {
        WorkflowStatus.EXECUTING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.EXECUTING: {
        WorkflowStatus.REVIEWING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.REVIEWING: {
        WorkflowStatus.EXECUTING,
        WorkflowStatus.REPORTING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.REPORTING: {
        WorkflowStatus.MARKETING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.MARKETING: {
        WorkflowStatus.FINAL_REVIEW,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.FINAL_REVIEW: {
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.COMPLETED: set(),
    WorkflowStatus.FAILED: set(),
    WorkflowStatus.CANCELLED: set(),
}

WorkerExecutor = Callable[[list[TaskRead]], Awaitable[list[WorkerResult]] | list[WorkerResult]]
ReportGenerator = Callable[
    [WorkflowRead, list[TaskRead], list[WorkerResult], list[ManagementReview]],
    Awaitable[Report] | Report,
]
MarketingGenerator = Callable[[WorkflowRead, Report], Awaitable[MarketingPlan] | MarketingPlan]
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
    revision_count: int = 0


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
        store: SQLiteJsonStore | None = None,
    ) -> None:
        self._workflows: dict[str, WorkflowRead] = {}
        self._tasks: dict[str, list[TaskRead]] = {}
        self._artifacts: dict[str, WorkflowArtifacts] = {}
        self._run_locks: dict[str, asyncio.Lock] = {}
        self._lock = RLock()
        self._ai_service = ai_service
        self._collaborators = collaborators or WorkflowCollaborators()
        self._manager: Manager | None = None
        self._store = store
        self._load_state()

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
            self._persist_workflow(workflow_id)
        return workflow.model_copy(deep=True)

    def list(self) -> list[WorkflowRead]:
        with self._lock:
            workflows = [workflow.model_copy(deep=True) for workflow in self._workflows.values()]
        return sorted(workflows, key=lambda item: item.created_at, reverse=True)

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

    def get_worker_results(self, workflow_id: str) -> list[WorkerResult] | None:
        with self._lock:
            artifacts = self._artifacts.get(workflow_id)
            if artifacts is None:
                return None
            return [result.model_copy(deep=True) for result in artifacts.worker_results]

    def get_reviews(self, workflow_id: str) -> list[ManagementReview] | None:
        with self._lock:
            artifacts = self._artifacts.get(workflow_id)
            if artifacts is None:
                return None
            return [review.model_copy(deep=True) for review in artifacts.reviews]

    def replace_tasks(self, workflow_id: str, tasks: list[TaskRead]) -> list[TaskRead]:
        with self._lock:
            self._require_stored(workflow_id)
            if any(task.workflow_id != workflow_id for task in tasks):
                raise WorkflowValidationError("Every task must belong to the workflow")
            ids = [task.id for task in tasks]
            if len(ids) != len(set(ids)):
                raise WorkflowValidationError("Task IDs must be unique within a workflow")
            self._tasks[workflow_id] = [task.model_copy(deep=True) for task in tasks]
            self._persist_workflow(workflow_id)
            return [task.model_copy(deep=True) for task in tasks]

    def delete(self, workflow_id: str) -> None:
        with self._lock:
            self._require_stored(workflow_id)
            self._workflows.pop(workflow_id, None)
            self._tasks.pop(workflow_id, None)
            self._artifacts.pop(workflow_id, None)
            self._run_locks.pop(workflow_id, None)
            if self._store is not None:
                for namespace in ("workflows", "workflow_tasks", "workflow_artifacts"):
                    self._store.delete(namespace, workflow_id)

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
            if target is WorkflowStatus.CANCELLED:
                workflow.completed_at = now
            self._persist_workflow(workflow_id)
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

    async def prepare_workflow(self, workflow_id: str) -> WorkflowRead:
        run_lock = self._get_run_lock(workflow_id)
        async with run_lock:
            workflow = self.require(workflow_id)
            if workflow.status is WorkflowStatus.CREATED:
                try:
                    return await self._plan_and_refine(workflow)
                except Exception as exc:
                    failed = self.fail(workflow_id, code="PLANNING_FAILED", message=str(exc))
                    raise WorkflowExecutionError(failed) from exc
            if workflow.status is WorkflowStatus.EXECUTING:
                return workflow
            raise WorkflowConflictError(f"Workflow cannot be refined from {workflow.status}")

    async def _run_workflow_locked(self, workflow_id: str) -> WorkflowRead:
        workflow = self.require(workflow_id)
        if workflow.status in {WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED}:
            return workflow
        if workflow.status is WorkflowStatus.FAILED:
            raise WorkflowConflictError("A failed workflow cannot be resumed")
        if workflow.status in {WorkflowStatus.SEGMENTING, WorkflowStatus.ASSIGNING}:
            workflow = self._recover_planning_stage(workflow)

        try:
            for _step in range(20):
                if workflow.status is WorkflowStatus.CREATED:
                    workflow = await self._plan_and_refine(workflow)
                elif workflow.status is WorkflowStatus.EXECUTING:
                    advanced = await self._execute_workers(workflow)
                    if advanced.status is workflow.status:
                        return advanced
                    workflow = advanced
                elif workflow.status is WorkflowStatus.REVIEWING:
                    workflow = await self._review_results(workflow)
                elif workflow.status is WorkflowStatus.REPORTING:
                    advanced = await self._generate_report(workflow)
                    if advanced.status is workflow.status:
                        return advanced
                    workflow = advanced
                elif workflow.status is WorkflowStatus.MARKETING:
                    advanced = await self._generate_marketing(workflow)
                    if advanced.status is workflow.status:
                        return advanced
                    workflow = advanced
                elif workflow.status is WorkflowStatus.FINAL_REVIEW:
                    workflow = await self._finalize(workflow)
                else:
                    return workflow
            raise RuntimeError("Workflow exceeded the maximum state-machine steps")
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
        refined_plan = (
            [await manager.refine_task(task) for task in generated]
            if isinstance(self._get_ai_service(), MockAIProvider)
            else await manager.refine_plan(generated)
        )
        total_weight = sum(max(task.difficulty, 1) for task in refined_plan)
        execution_cents = int(
            (Decimal(str(workflow.budget)) * 60).to_integral_value(rounding=ROUND_DOWN)
        )
        remaining_cents = execution_cents
        for index, refined in enumerate(refined_plan, start=1):
            worker, reason = get_worker_service().match_worker(refined)
            cents = (
                remaining_cents
                if index == len(refined_plan)
                else execution_cents * max(refined.difficulty, 1) // total_weight
            )
            remaining_cents -= cents
            estimated_cost = cents / 100
            tasks.append(
                TaskRead(
                    id=f"task-{index:03d}",
                    workflow_id=workflow.id,
                    estimated_cost=round(estimated_cost, 2),
                    assigned_worker_id=worker.id,
                    assigned_worker_name=worker.name,
                    assignment_reason=reason,
                    **refined.model_dump(),
                )
            )
        self.replace_tasks(workflow.id, tasks)
        return self.transition(workflow.id, WorkflowStatus.EXECUTING)

    async def _execute_workers(self, workflow: WorkflowRead) -> WorkflowRead:
        if workflow.execution_mode == "employee":
            tasks = self.get_tasks(workflow.id) or []
            results = self._artifacts[workflow.id].worker_results
            if not tasks or {t.id for t in tasks} != {r.task_id for r in results}:
                return workflow
            return self.transition(workflow.id, WorkflowStatus.REVIEWING)
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
        results_by_task = {result.task_id: result for result in results}
        completed_tasks: list[TaskRead] = []
        for task in tasks:
            result = results_by_task[task.id]
            assigned_name = result.output.get("assigned_worker")
            completed_tasks.append(
                task.model_copy(
                    update={
                        "status": TaskStatus.COMPLETED,
                        "assigned_worker_id": result.worker_id,
                        "assigned_worker_name": (
                            str(assigned_name) if assigned_name is not None else None
                        ),
                        "assignment_reason": result.assignment_reason,
                    }
                )
            )
        self.replace_tasks(workflow.id, completed_tasks)
        self._persist_workflow(workflow.id)
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
        revision_reviews = {
            review.task_id: review
            for review in reviews
            if review.decision is ManagementDecision.REVISION_REQUIRED
        }
        if revision_reviews:
            artifacts.revision_count += 1
            if artifacts.revision_count > settings.management_max_revisions:
                raise RuntimeError("Management revision limit exceeded")
            revised_tasks = [
                task.model_copy(
                    update={
                        "status": TaskStatus.PENDING,
                        "revision_count": task.revision_count + 1,
                        "revision_instructions": list(
                            revision_reviews[task.id].revision_instructions
                        ),
                    }
                )
                if task.id in revision_reviews
                else task.model_copy(update={"status": TaskStatus.PENDING})
                for task in tasks
            ]
            self.replace_tasks(workflow.id, revised_tasks)
            if workflow.execution_mode == "employee":
                artifacts.worker_results = [
                    r for r in artifacts.worker_results if r.task_id not in revision_reviews
                ]
                revised_tasks = [
                    t.model_copy(update={"status": TaskStatus.COMPLETED})
                    if t.id not in revision_reviews
                    else t
                    for t in revised_tasks
                ]
                self.replace_tasks(workflow.id, revised_tasks)
            else:
                artifacts.worker_results = []
            self._persist_workflow(workflow.id)
            self._record_event(
                workflow.id,
                "manager",
                "REVISION_REQUESTED",
                f"Management requested revision cycle {artifacts.revision_count}",
                artifacts.revision_count,
            )
            return self.transition(workflow.id, WorkflowStatus.EXECUTING)
        self._set_all_task_statuses(workflow.id, TaskStatus.COMPLETED)
        self._persist_workflow(workflow.id)
        return self.transition(workflow.id, WorkflowStatus.REPORTING)

    async def demo_complete_tasks(self, workflow_id: str) -> WorkflowRead:
        """Simulate task completion and approval for a local presentation."""
        async with self._get_run_lock(workflow_id):
            workflow = self._require_stored(workflow_id)
            if workflow.status != WorkflowStatus.EXECUTING:
                raise WorkflowConflictError(
                    "Prepare the task plan first; it must be awaiting work."
                )
            tasks = self.get_tasks(workflow_id) or []
            if not tasks:
                raise WorkflowConflictError("No prepared tasks to complete.")
            artifacts = self._artifacts[workflow_id]
            results = {r.task_id: r for r in artifacts.worker_results}
            for task in tasks:
                if task.id not in results:
                    results[task.id] = WorkerResult(
                        task_id=task.id,
                        worker_id=task.assigned_worker_id or "demo",
                        summary="DEMO ONLY: simulated completion; no real work performed.",
                        output={
                            "source": "demo",
                            "assigned_worker": task.assigned_worker_name,
                            "deliverable": "DEMO ONLY: simulated completion of " + task.title,
                        },
                        evidence=["Demo button; not verified evidence"],
                        cost=task.estimated_cost,
                        assignment_reason=task.assignment_reason or "Demo",
                    )
            artifacts.worker_results = list(results.values())
            artifacts.reviews = [
                ManagementReview(
                    task_id=t.id,
                    decision=ManagementDecision.APPROVED,
                    feedback="DEMO ONLY: review bypassed for presentation.",
                )
                for t in tasks
            ]
            self.replace_tasks(
                workflow_id, [t.model_copy(update={"status": TaskStatus.COMPLETED}) for t in tasks]
            )
            self.transition(workflow_id, WorkflowStatus.REVIEWING)
            self._persist_workflow(workflow_id)
            self._record_event(
                workflow_id,
                "demo",
                "DEMO_COMPLETED",
                "Task completion and review simulated for presentation.",
                0,
            )
            return self.transition(workflow_id, WorkflowStatus.REPORTING)

    async def submit_employee_work(
        self,
        workflow_id: str,
        task_id: str,
        worker_id: str,
        deliverable: str,
    ) -> WorkerResult:
        async with self._get_run_lock(workflow_id):
            workflow = self.require(workflow_id)
            if workflow.execution_mode != "employee" or workflow.status != WorkflowStatus.EXECUTING:
                raise WorkflowConflictError("This workflow is not accepting employee submissions.")
            tasks = self.get_tasks(workflow_id) or []
            task = next((t for t in tasks if t.id == task_id), None)
            if task is None or task.assigned_worker_id != worker_id:
                raise WorkflowValidationError("This task is not assigned to the selected employee.")
            results = self._artifacts[workflow_id].worker_results
            if task_id in {r.task_id for r in results}:
                raise WorkflowConflictError("Work is already submitted. Wait for review.")
            if not set(task.dependency_task_ids) <= {r.task_id for r in results}:
                raise WorkflowConflictError("Submit the prerequisite tasks first.")
            result = WorkerResult(
                task_id=task_id,
                worker_id=worker_id,
                summary="Employee submission: " + task.title,
                output={
                    "deliverable": deliverable,
                    "source": "employee",
                    "assigned_worker": task.assigned_worker_name,
                    "submitted_at": datetime.now(UTC).isoformat(),
                },
                evidence=["Submitted by the assigned employee for management review."],
                cost=task.estimated_cost,
                assignment_reason=task.assignment_reason or "",
            )
            results.append(result)
            self.replace_tasks(
                workflow_id,
                [
                    t.model_copy(update={"status": TaskStatus.SUBMITTED}) if t.id == task_id else t
                    for t in tasks
                ],
            )
            self._persist_workflow(workflow_id)
            self._record_event(
                workflow_id,
                "employee",
                "WORK_SUBMITTED",
                f"{task.assigned_worker_name} submitted {task.title} for review",
                0,
            )
            return result.model_copy(deep=True)

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
        self._persist_workflow(workflow.id)
        return self.transition(workflow.id, WorkflowStatus.MARKETING)

    async def _generate_marketing(self, workflow: WorkflowRead) -> WorkflowRead:
        generator = self._collaborators.generate_marketing
        if generator is None:
            return workflow
        artifacts = self._artifacts[workflow.id]
        if artifacts.marketing is not None:
            return workflow
        if artifacts.report is None:
            raise WorkflowConflictError("Report is unavailable for marketing generation")
        marketing = await _await_if_needed(generator(workflow, artifacts.report))
        if marketing.workflow_id != workflow.id:
            raise WorkflowValidationError("Marketing plan belongs to a different workflow")
        artifacts.marketing = marketing.model_copy(deep=True)
        self._persist_workflow(workflow.id)
        self._record_event(
            workflow.id,
            "marketing",
            "AWAITING_APPROVAL",
            "Marketing draft ready for edits and explicit team approval.",
            0,
        )
        return self.get(workflow.id)

    async def save_marketing_draft(
        self,
        workflow_id: str,
        plan: MarketingPlan,
        *,
        approve: bool = False,
    ) -> MarketingPlan:
        from app.services.marketing_service import marketing_service

        async with self._get_run_lock(workflow_id):
            workflow = self._require_stored(workflow_id)
            if workflow.status != WorkflowStatus.MARKETING:
                raise WorkflowConflictError(
                    "Marketing edits and approval require the marketing stage."
                )
            artifacts = self._artifacts[workflow_id]
            if artifacts.report is None or artifacts.marketing is None:
                raise WorkflowConflictError("Generate the marketing draft before approval.")
            if plan.workflow_id != workflow_id:
                raise WorkflowValidationError("Marketing plan belongs to another workflow")
            saved = plan.model_copy(
                update={
                    "approved_budget": max(0, artifacts.report.financial.remaining_budget),
                }
            )
            saved.validate_budget()
            marketing_service.save_plan(saved)
            artifacts.marketing = saved.model_copy(deep=True)
            self.invalidate_summary(workflow_id)
            self._persist_workflow(workflow_id)
            if approve:
                self._record_event(
                    workflow_id,
                    "marketing",
                    "MARKETING_APPROVED",
                    "Marketing team confirmed the edited plan for final review.",
                    0,
                )
                self.transition(workflow_id, WorkflowStatus.FINAL_REVIEW)
            return saved

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
            results=artifacts.worker_results,
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
            self._persist_workflow(workflow_id)
            failed = workflow.model_copy(deep=True)
        self._record_event(
            workflow_id,
            "workflow_service",
            "FAILED",
            message,
            0,
        )
        return failed

    def cancel(self, workflow_id: str) -> WorkflowRead:
        workflow = self.require(workflow_id)
        if workflow.status in {
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        }:
            raise WorkflowConflictError(f"Workflow cannot be cancelled from {workflow.status}")
        return self.transition(workflow_id, WorkflowStatus.CANCELLED)

    def retry_failed(self, workflow_id: str) -> WorkflowRead:
        with self._lock:
            workflow = self._require_stored(workflow_id)
            if workflow.status is not WorkflowStatus.FAILED or workflow.failure is None:
                raise WorkflowConflictError("Only a failed workflow can be retried")
            target = workflow.failure.failed_stage
            if target in {WorkflowStatus.SEGMENTING, WorkflowStatus.ASSIGNING}:
                target = WorkflowStatus.CREATED
                self._tasks[workflow_id] = []
                self._artifacts[workflow_id] = WorkflowArtifacts()
            workflow.status = target
            workflow.current_stage = STAGE_NAMES[target]
            workflow.failure = None
            workflow.completed_at = None
            workflow.updated_at = datetime.now(UTC)
            self._persist_workflow(workflow_id)
            retried = workflow.model_copy(deep=True)
        self._record_event(
            workflow_id,
            "workflow_service",
            "RETRY_REQUESTED",
            f"Workflow restored to {target}",
            0,
        )
        return retried

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
            self._persist_workflow(workflow_id)
            return workflow.model_copy(deep=True)

    def invalidate_summary(self, workflow_id: str) -> None:
        with self._lock:
            workflow = self._require_stored(workflow_id)
            workflow.executive_summary = None
            workflow.updated_at = datetime.now(UTC)
            self._persist_workflow(workflow_id)

    async def refresh_summary(
        self, workflow_id: str, report: Report, marketing: MarketingPlan
    ) -> WorkflowRead:
        async with self._get_run_lock(workflow_id):
            workflow = self.require(workflow_id)
            if workflow.status != WorkflowStatus.COMPLETED:
                raise WorkflowConflictError(
                    "Complete management review before generating the CEO summary."
                )
            artifacts = self._artifacts[workflow_id]
            summary = await self._get_manager().create_executive_summary(
                workflow=workflow,
                report=report,
                marketing=marketing,
                reviews=artifacts.reviews,
                results=artifacts.worker_results,
            )
            with self._lock:
                stored = self._require_stored(workflow_id)
                if stored.updated_at != workflow.updated_at:
                    raise WorkflowConflictError(
                        "The plan changed during summary generation. Try again."
                    )
                stored.executive_summary = summary
                stored.updated_at = datetime.now(UTC)
                artifacts.marketing = marketing
                self._persist_workflow(workflow_id)
            return self.require(workflow_id)

    def has_running_operations(self) -> bool:
        return any(lock.locked() for lock in self._run_locks.values())

    def clear(self) -> None:
        """Clear volatile storage for isolated tests."""

        with self._lock:
            self._workflows.clear()
            self._tasks.clear()
            self._artifacts.clear()
            self._run_locks.clear()
            if self._store is not None:
                for namespace in ("workflows", "workflow_tasks", "workflow_artifacts"):
                    self._store.clear_namespace(namespace)

    def _load_state(self) -> None:
        if self._store is None:
            return
        for workflow_id, payload in self._store.list("workflows"):
            workflow = WorkflowRead.model_validate(payload)
            tasks_payload = self._store.get("workflow_tasks", workflow_id) or {}
            artifact_payload = self._store.get("workflow_artifacts", workflow_id) or {}
            self._workflows[workflow_id] = workflow
            self._tasks[workflow_id] = [
                TaskRead.model_validate(task) for task in tasks_payload.get("items", [])
            ]
            self._artifacts[workflow_id] = WorkflowArtifacts(
                worker_results=[
                    WorkerResult.model_validate(result)
                    for result in artifact_payload.get("worker_results", [])
                ],
                reviews=[
                    ManagementReview.model_validate(review)
                    for review in artifact_payload.get("reviews", [])
                ],
                report=(
                    Report.model_validate(artifact_payload["report"])
                    if artifact_payload.get("report") is not None
                    else None
                ),
                marketing=(
                    MarketingPlan.model_validate(artifact_payload["marketing"])
                    if artifact_payload.get("marketing") is not None
                    else None
                ),
                revision_count=int(artifact_payload.get("revision_count", 0)),
            )
            self._run_locks[workflow_id] = asyncio.Lock()

    def _persist_workflow(self, workflow_id: str) -> None:
        if self._store is None:
            return
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return
        tasks = self._tasks.get(workflow_id, [])
        artifacts = self._artifacts.get(workflow_id, WorkflowArtifacts())
        self._store.put(
            "workflows",
            workflow_id,
            workflow.model_dump(mode="json"),
        )
        self._store.put(
            "workflow_tasks",
            workflow_id,
            {"items": [task.model_dump(mode="json") for task in tasks]},
        )
        self._store.put(
            "workflow_artifacts",
            workflow_id,
            {
                "worker_results": [
                    result.model_dump(mode="json") for result in artifacts.worker_results
                ],
                "reviews": [review.model_dump(mode="json") for review in artifacts.reviews],
                "report": (
                    artifacts.report.model_dump(mode="json")
                    if artifacts.report is not None
                    else None
                ),
                "marketing": (
                    artifacts.marketing.model_dump(mode="json")
                    if artifacts.marketing is not None
                    else None
                ),
                "revision_count": artifacts.revision_count,
            },
        )

    def _recover_planning_stage(self, workflow: WorkflowRead) -> WorkflowRead:
        with self._lock:
            stored = self._require_stored(workflow.id)
            stored.status = WorkflowStatus.CREATED
            stored.current_stage = STAGE_NAMES[WorkflowStatus.CREATED]
            stored.failure = None
            stored.updated_at = datetime.now(UTC)
            self._tasks[workflow.id] = []
            self._artifacts[workflow.id] = WorkflowArtifacts()
            self._persist_workflow(workflow.id)
            recovered = stored.model_copy(deep=True)
        self._record_event(
            workflow.id,
            "workflow_service",
            "RECOVERED",
            "Recovered interrupted planning stage",
            0,
        )
        return recovered

    def _set_all_task_statuses(self, workflow_id: str, status: TaskStatus) -> None:
        tasks = self.get_tasks(workflow_id)
        if tasks is None:
            raise WorkflowNotFoundError(workflow_id)
        self.replace_tasks(
            workflow_id,
            [task.model_copy(update={"status": status}) for task in tasks],
        )

    @staticmethod
    def _validate_worker_results(tasks: list[TaskRead], results: list[WorkerResult]) -> None:
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
            include_workforce=not isinstance(self._get_ai_service(), MockAIProvider),
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


_workflow_service = WorkflowService(store=get_json_store())


def get_workflow_service() -> WorkflowService:
    return _workflow_service
