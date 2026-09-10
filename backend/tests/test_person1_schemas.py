import pytest
from pydantic import ValidationError

from app.schemas.task import GeneratedTaskList, ManagementReview


def _task(title: str, dependencies: list[str] | None = None) -> dict[str, object]:
    return {
        "title": title,
        "description": "A concrete task description.",
        "priority": "high",
        "difficulty": 2,
        "required_role": "Analyst",
        "minimum_experience_years": 1,
        "required_skills": ["Analysis"],
        "dependency_task_ids": dependencies or [],
        "expected_output": "Reviewed output",
        "acceptance_criteria": ["Output is approved"],
    }


def test_task_plan_rejects_unknown_dependency() -> None:
    with pytest.raises(ValidationError, match="unknown dependencies"):
        GeneratedTaskList.model_validate({"tasks": [_task("Plan", ["task-999"])]})


def test_task_plan_rejects_cycles() -> None:
    with pytest.raises(ValidationError, match="cycle"):
        GeneratedTaskList.model_validate(
            {
                "tasks": [
                    _task("Plan", ["task-002"]),
                    _task("Execute", ["task-001"]),
                ]
            }
        )


def test_revision_review_requires_instructions() -> None:
    with pytest.raises(ValidationError, match="revision instructions"):
        ManagementReview(
            task_id="task-001",
            decision="REVISION_REQUIRED",
            feedback="More evidence is needed.",
        )
