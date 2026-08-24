import asyncio
from datetime import date, timedelta

import pytest

from app.agents.orchestrator import OrchestrationError, Orchestrator
from app.schemas.task import GeneratedTaskList
from app.services.ai_service import MockAIProvider


def _task(title: str, dependencies: list[str] | None = None) -> dict[str, object]:
    return {
        "title": title,
        "description": f"Complete {title.lower()} with a documented result.",
        "priority": "HIGH",
        "difficulty": 3,
        "required_role": "Business Analyst",
        "minimum_experience_years": 2,
        "required_skills": ["analysis"],
        "dependency_task_ids": dependencies or [],
        "expected_output": f"{title} output",
        "acceptance_criteria": [f"{title} is reviewed"],
    }


def test_orchestrator_returns_validated_tasks() -> None:
    plan = {"tasks": [_task("Plan"), _task("Execute", ["task-001"])]}
    provider = MockAIProvider({GeneratedTaskList: [plan]})
    orchestrator = Orchestrator(provider, max_tasks=4)

    tasks = asyncio.run(
        orchestrator.segment(
            objective="Create a measurable launch plan.",
            budget=50_000,
            deadline=date.today() + timedelta(days=30),
        )
    )

    assert [task.title for task in tasks] == ["Plan", "Execute"]
    assert tasks[1].dependency_task_ids == ["task-001"]


def test_orchestrator_retries_one_invalid_business_plan() -> None:
    invalid = {"tasks": [_task("Plan", ["task-002"]), _task("Execute")]}
    valid = {"tasks": [_task("Plan"), _task("Execute", ["task-001"])]}
    provider = MockAIProvider({GeneratedTaskList: [invalid, valid]})
    failures: list[tuple[Exception, int]] = []
    orchestrator = Orchestrator(
        provider,
        max_tasks=4,
        on_validation_failure=lambda error, attempt: failures.append((error, attempt)),
    )

    tasks = asyncio.run(
        orchestrator.segment(
            objective="Create a measurable launch plan.",
            budget=50_000,
            deadline=date.today() + timedelta(days=30),
        )
    )

    assert len(tasks) == 2
    assert len(failures) == 1
    assert failures[0][1] == 0


def test_orchestrator_fails_after_retry_limit() -> None:
    plan = {"tasks": [_task("Plan"), _task("Execute")]}
    provider = MockAIProvider({GeneratedTaskList: [plan, plan]})
    orchestrator = Orchestrator(provider, max_tasks=1)

    with pytest.raises(OrchestrationError, match="valid task plan"):
        asyncio.run(
            orchestrator.segment(
                objective="Create a measurable launch plan.",
                budget=50_000,
                deadline=date.today() + timedelta(days=30),
            )
        )
