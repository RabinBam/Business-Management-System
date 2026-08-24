"""Person 2 starting point for deterministic worker matching and execution."""

from __future__ import annotations

import json
from pathlib import Path

from app.schemas.task import GeneratedTask
from app.schemas.worker import WorkerProfile

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class WorkerService:
    """Load worker profiles from disk and match them to tasks deterministically.

    Matching order: role → experience → skill-overlap → tie-break by
    experience then ID.  The list of profiles is never mutated after
    construction so matching results are stable across calls.
    """

    def __init__(self) -> None:
        self._profiles: list[WorkerProfile] = self._load_profiles()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_workers(self) -> list[WorkerProfile]:
        """Return all loaded worker profiles."""
        return list(self._profiles)

    def get_worker(self, worker_id: str) -> WorkerProfile | None:
        """Look up a single profile by ID, or ``None`` if not found."""
        for profile in self._profiles:
            if profile.id == worker_id:
                return profile
        return None

    def match_worker(self, task: GeneratedTask) -> tuple[WorkerProfile, str]:
        """Find the best worker for *task* using deterministic scoring.

        Returns ``(worker, reason)`` where *reason* is a human-readable
        explanation of the match.

        Raises
        ------
        ValueError
            If no worker profiles are available at all.
        """
        if not self._profiles:
            raise ValueError("No worker profiles available.")

        # Step 1 — filter by required_role (case-insensitive).
        role_matches = [
            p for p in self._profiles
            if p.role.lower() == task.required_role.lower()
        ]

        if not role_matches:
            candidates = list(self._profiles)
            reason_prefix = f"No worker with role '{task.required_role}' found. "
        else:
            candidates = role_matches
            reason_prefix = f"Matched role '{task.required_role}'. "

        # Step 2 — filter by minimum experience.
        exp_matches = [
            p for p in candidates
            if p.experience_years >= task.minimum_experience_years
        ]

        if not exp_matches:
            # Fallback: sort a *copy* so we never mutate the internal list.
            candidates = sorted(
                candidates, key=lambda w: w.experience_years, reverse=True,
            )
            reason_prefix += (
                f"No worker meets {task.minimum_experience_years} years "
                f"experience, using best available. "
            )
        else:
            candidates = exp_matches
            reason_prefix += (
                f"Meets experience requirement "
                f"(>= {task.minimum_experience_years} years). "
            )

        # Step 3 — score by skill overlap.
        task_skills = {s.lower() for s in task.required_skills}

        best_candidate: WorkerProfile | None = None
        best_score = -1

        for p in candidates:
            worker_skills = {s.lower() for s in p.skills}
            score = len(task_skills & worker_skills)

            # Deterministic tie-breaking: more experience wins, then lower ID.
            if score > best_score:
                best_score = score
                best_candidate = p
            elif score == best_score and best_candidate is not None:
                if p.experience_years > best_candidate.experience_years:
                    best_candidate = p
                elif (
                    p.experience_years == best_candidate.experience_years
                    and p.id < best_candidate.id
                ):
                    best_candidate = p

        if best_candidate is None:
            best_candidate = candidates[0]

        reason = reason_prefix + f"Matched {best_score} required skills."
        return best_candidate, reason

    def match_workers_for_tasks(
        self, tasks: list[GeneratedTask],
    ) -> list[tuple[GeneratedTask, WorkerProfile, str]]:
        """Match every task and return ``(task, worker, reason)`` tuples."""
        return [(t, *self.match_worker(t)) for t in tasks]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_profiles() -> list[WorkerProfile]:
        """Read ``worker_profiles.json`` from the data directory."""
        profiles_file = _DATA_DIR / "worker_profiles.json"
        if not profiles_file.exists():
            return []
        raw = json.loads(profiles_file.read_text(encoding="utf-8"))
        return [WorkerProfile.model_validate(p) for p in raw]


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_worker_service: WorkerService | None = None


def get_worker_service() -> WorkerService:
    global _worker_service
    if _worker_service is None:
        _worker_service = WorkerService()
    return _worker_service
