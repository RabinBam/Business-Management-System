import asyncio

from app.agents.worker import TaskDeliverable, WorkerAgent
from app.schemas.task import TaskRead


class RecordingProvider:
    def __init__(self):
        self.calls = []

    async def generate_structured(self, **kwargs):
        self.calls.append(kwargs)
        return TaskDeliverable(
            summary="Prepared a plan",
            deliverable="Milestone 1: validate demand.",
            evidence=["Includes a measurable milestone"],
            limitations=["Draft only"],
        )


def task(task_id, dependencies=None):
    return TaskRead(
        id=task_id,
        workflow_id="wf-test",
        title="Prepare a plan",
        description="Prepare an operating plan.",
        priority="HIGH",
        difficulty=2,
        required_role="Business Analyst",
        minimum_experience_years=2,
        required_skills=["analysis"],
        expected_output="Operating plan",
        acceptance_criteria=["Include milestones"],
        estimated_cost=250,
        dependency_task_ids=dependencies or [],
        revision_count=1,
        revision_instructions=["Add measurable milestones"],
    )


def test_ai_workers_preserve_authoritative_fields_and_pass_dependency_outputs():
    provider = RecordingProvider()
    results = asyncio.run(
        WorkerAgent().execute_all(
            [task("task-002", ["task-001"]), task("task-001")],
            ai_service=provider,
        )
    )
    assert [result.task_id for result in results] == ["task-001", "task-002"]
    assert all(result.cost == 250 and result.worker_id for result in results)
    assert all(result.output["assigned_worker"] for result in results)
    assert "Milestone 1" in results[0].output["deliverable"]
    assert "Add measurable milestones" in provider.calls[0]["user_prompt"]
    assert "Milestone 1" in provider.calls[1]["user_prompt"]
    assert provider.calls[0]["schema"] is TaskDeliverable


def test_worker_dependency_error_is_visible():
    import pytest

    with pytest.raises(ValueError, match="dependencies"):
        asyncio.run(
            WorkerAgent().execute_all(
                [task("task-001", ["missing"])],
                ai_service=RecordingProvider(),
            )
        )
