"""Person 2 starting point: role-aware worker execution."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.config import settings
from app.schemas.task import TaskRead, TaskStatus
from app.schemas.worker import WorkerProfile, WorkerResult
from app.services.ai_service import AIService, MockAIProvider, get_ai_service
from app.services.worker_service import get_worker_service


class TaskDeliverable(BaseModel):
    summary: str = Field(min_length=1)
    deliverable: str = Field(min_length=1)
    evidence: list[str]
    limitations: list[str]


class WorkerAgent:
    """Execute a task by matching it to the best available worker profile.

    Mock mode simulates execution. Configured providers produce written
    deliverables while matching and estimated costs remain deterministic.
    """

    def __init__(self) -> None:
        self._service = get_worker_service()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assign_and_execute(self, task: TaskRead) -> WorkerResult:
        """Match *task* to the best worker and produce a deterministic result.

        Returns a ``WorkerResult`` that summarises the simulated execution.
        """
        worker, reason = self._service.match_worker(task)
        return self._simulate_execution(task, worker, reason)

    def assign_and_execute_all(
        self, tasks: list[TaskRead],
    ) -> list[WorkerResult]:
        """Execute every task in order and return the collected results."""
        return [self.assign_and_execute(t) for t in tasks]

    async def execute_all(
        self, tasks: list[TaskRead], *, ai_service: AIService | None = None,
    ) -> list[WorkerResult]:
        provider = ai_service or get_ai_service()
        if isinstance(provider, MockAIProvider):
            return self.assign_and_execute_all(tasks)
        results: list[WorkerResult] = []
        pending = list(tasks)
        completed_ids: set[str] = set()
        while pending:
            task = next((item for item in pending
                         if set(item.dependency_task_ids) <= completed_ids), None)
            if task is None:
                raise ValueError("Worker tasks contain missing or cyclic dependencies")
            pending.remove(task)
            worker, reason = self._service.match_worker(task)
            deliverable = await provider.generate_structured(
                system_prompt=(
                    "You are an Byapari business worker. Produce the actual written "
                    "deliverable requested by the task, satisfying its acceptance criteria "
                    "and revision instructions. Use earlier results where relevant. "
                    "You cannot perform external actions. Do not claim to have launched "
                    "campaigns, contacted people, or verified external facts. Clearly state "
                    "assumptions and limitations; evidence must refer to supplied inputs "
                    "or content in your deliverable."
                ),
                user_prompt=(
                    "TASK_JSON:\n" + task.model_dump_json()
                    + "\nWORKER_JSON:\n" + worker.model_dump_json()
                    + "\nEARLIER_RESULTS:\n"
                    + "\n".join(result.model_dump_json() for result in results)
                ),
                schema=TaskDeliverable,
                model=settings.ai_worker_model or None,
            )
            results.append(WorkerResult(
                task_id=task.id,
                worker_id=worker.id,
                summary=deliverable.summary,
                output={
                    "assigned_worker": worker.name,
                    "deliverable": deliverable.deliverable,
                    "limitations": deliverable.limitations,
                    "revision_count": task.revision_count,
                },
                evidence=deliverable.evidence,
                cost=task.estimated_cost,
                assignment_reason=reason,
            ))
            completed_ids.add(task.id)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _simulate_execution(
        task: TaskRead,
        worker: WorkerProfile,
        match_reason: str,
    ) -> WorkerResult:
        """Produce a deterministic ``WorkerResult`` for the given assignment.

        In the future this can delegate to the AI service for richer output.
        """
        summary = (
            f"Task '{task.title}' executed by {worker.name} ({worker.role}, "
            f"{worker.experience_years}y experience). {match_reason}"
        )

        output: dict[str, object] = {
            "task_id": task.id,
            "task_title": task.title,
            "assigned_worker": worker.name,
            "worker_role": worker.role,
            "match_reason": match_reason,
            "status": TaskStatus.COMPLETED,
            "revision_count": task.revision_count,
            "revision_instructions": list(task.revision_instructions),
            "estimated_cost": task.estimated_cost,
        }

        evidence: list[str] = [
            f"Worker {worker.name} matched with role '{worker.role}'.",
            f"Experience: {worker.experience_years} years "
            f"(required: {task.minimum_experience_years}).",
            "Skills overlap evaluated against: "
            f"{', '.join(task.required_skills) or 'none specified'}.",
        ]

        return WorkerResult(
            task_id=task.id,
            worker_id=worker.id,
            summary=summary,
            output=output,
            evidence=evidence,
            cost=task.estimated_cost,
            assignment_reason=match_reason,
        )


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_worker_agent: WorkerAgent | None = None


def get_worker_agent() -> WorkerAgent:
    global _worker_agent
    if _worker_agent is None:
        _worker_agent = WorkerAgent()
    return _worker_agent
