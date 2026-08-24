"""Person 2 starting point: role-aware worker execution."""

from __future__ import annotations

from app.schemas.task import GeneratedTask, TaskRead, TaskStatus
from app.schemas.worker import WorkerProfile, WorkerResult
from app.services.worker_service import get_worker_service


class WorkerAgent:
    """Execute a task by matching it to the best available worker profile.

    The agent itself does not perform real work — it simulates deterministic
    execution based on the worker's profile and the task requirements.  When a
    real AI provider is wired up (Person 1), the ``execute`` method can
    delegate to the provider while keeping the matching logic deterministic.
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
        }

        evidence: list[str] = [
            f"Worker {worker.name} matched with role '{worker.role}'.",
            f"Experience: {worker.experience_years} years "
            f"(required: {task.minimum_experience_years}).",
            f"Skills overlap evaluated against: {', '.join(task.required_skills) or 'none specified'}.",
        ]

        return WorkerResult(
            task_id=task.id,
            worker_id=worker.id,
            summary=summary,
            output=output,
            evidence=evidence,
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
