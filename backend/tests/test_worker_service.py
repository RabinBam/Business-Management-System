"""Tests for the worker service — profile loading, matching, and edge cases."""

from app.schemas.task import GeneratedTask
from app.schemas.worker import WorkerProfile
from app.services.worker_service import WorkerService


def _make_task(**overrides: object) -> GeneratedTask:
    defaults: dict[str, object] = {
        "title": "Test task",
        "description": "A task for testing",
        "priority": "high",
        "difficulty": 3,
        "required_role": "developer",
        "minimum_experience_years": 2.0,
        "required_skills": ["Python", "FastAPI"],
        "dependency_task_ids": [],
        "expected_output": "Working code",
        "acceptance_criteria": ["Code passes tests"],
    }
    defaults.update(overrides)
    return GeneratedTask(**defaults)  # type: ignore[arg-type]


class TestWorkerServiceLoading:
    """Ensure profiles are loaded from the JSON fixture."""

    def test_loads_profiles(self) -> None:
        service = WorkerService()
        workers = service.get_workers()
        assert len(workers) >= 1
        assert all(isinstance(w, WorkerProfile) for w in workers)

    def test_get_worker_by_id(self) -> None:
        service = WorkerService()
        worker = service.get_worker("w-001")
        assert worker is not None
        assert worker.id == "w-001"

    def test_get_worker_missing(self) -> None:
        service = WorkerService()
        assert service.get_worker("w-999") is None


class TestWorkerMatching:
    """Deterministic matching: role → experience → skill overlap."""

    def test_matches_by_role(self) -> None:
        service = WorkerService()
        task = _make_task(required_role="developer")
        worker, reason = service.match_worker(task)
        assert worker.role == "developer"
        assert "Matched role" in reason

    def test_respects_experience_requirement(self) -> None:
        service = WorkerService()
        task = _make_task(required_role="developer", minimum_experience_years=5.0)
        worker, reason = service.match_worker(task)
        assert worker.experience_years >= 5.0

    def test_fallback_when_no_role_match(self) -> None:
        service = WorkerService()
        task = _make_task(required_role="astronaut")
        worker, reason = service.match_worker(task)
        # Should still return a worker, just not with the exact role.
        assert worker is not None
        assert "No worker with role" in reason

    def test_match_workers_for_tasks_returns_all(self) -> None:
        service = WorkerService()
        tasks = [
            _make_task(required_role="analyst"),
            _make_task(required_role="marketer"),
        ]
        results = service.match_workers_for_tasks(tasks)
        assert len(results) == 2
        for task, worker, reason in results:
            assert isinstance(worker, WorkerProfile)
            assert isinstance(reason, str)
