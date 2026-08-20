from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GeneratedTask(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: str
    difficulty: int = Field(ge=1, le=5)
    required_role: str
    minimum_experience_years: float = Field(ge=0)
    required_skills: list[str] = Field(default_factory=list)
    dependency_task_ids: list[str] = Field(default_factory=list)
    expected_output: str
    acceptance_criteria: list[str] = Field(default_factory=list)


class TaskRead(GeneratedTask):
    id: str
    workflow_id: str
    status: TaskStatus = TaskStatus.PENDING

