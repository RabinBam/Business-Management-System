from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ManagementDecision(StrEnum):
    APPROVED = "APPROVED"
    REVISION_REQUIRED = "REVISION_REQUIRED"


class GeneratedTask(BaseModel):
    """A provider-neutral task produced by the orchestrator.

    Dependency IDs use the task's one-based position in its containing plan:
    ``task-001``, ``task-002``, and so on. The workflow service preserves those
    IDs when it materializes :class:`TaskRead` records.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=2_000)
    priority: TaskPriority
    difficulty: int = Field(ge=1, le=5)
    required_role: str = Field(min_length=1, max_length=120)
    minimum_experience_years: float = Field(ge=0, le=60)
    required_skills: list[str] = Field(min_length=1, max_length=12)
    dependency_task_ids: list[str] = Field(default_factory=list, max_length=20)
    expected_output: str = Field(min_length=1, max_length=1_000)
    acceptance_criteria: list[str] = Field(min_length=1, max_length=12)
    employee_brief: str = Field(default="", max_length=2000)
    handoff_notes: str = Field(default="", max_length=1500)

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value

    @field_validator("required_skills", "acceptance_criteria")
    @classmethod
    def normalize_string_lists(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = value.strip()
            key = item.casefold()
            if item and key not in seen:
                normalized.append(item)
                seen.add(key)
        if not normalized:
            raise ValueError("at least one non-empty value is required")
        return normalized

    @field_validator("dependency_task_ids")
    @classmethod
    def normalize_dependencies(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value.strip().lower() for value in values if value.strip()))


class GeneratedTaskList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[GeneratedTask] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_plan(self) -> "GeneratedTaskList":
        valid_ids = {f"task-{index:03d}" for index in range(1, len(self.tasks) + 1)}
        graph: dict[str, list[str]] = {}
        titles: set[str] = set()

        for index, task in enumerate(self.tasks, start=1):
            task_id = f"task-{index:03d}"
            title_key = task.title.casefold()
            if title_key in titles:
                raise ValueError(f"duplicate task title: {task.title}")
            titles.add(title_key)

            if task_id in task.dependency_task_ids:
                raise ValueError(f"{task_id} cannot depend on itself")
            unknown = set(task.dependency_task_ids) - valid_ids
            if unknown:
                joined = ", ".join(sorted(unknown))
                raise ValueError(f"{task_id} has unknown dependencies: {joined}")
            graph[task_id] = task.dependency_task_ids

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise ValueError("task dependency graph contains a cycle")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in graph[task_id]:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id)
        return self


class TaskRead(GeneratedTask):
    id: str
    workflow_id: str
    status: TaskStatus = TaskStatus.PENDING
    estimated_cost: float = Field(default=0, ge=0)
    assigned_worker_id: str | None = None
    assigned_worker_name: str | None = None
    assignment_reason: str | None = None
    revision_count: int = Field(default=0, ge=0)
    revision_instructions: list[str] = Field(default_factory=list)


class ManagementReview(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    task_id: str
    decision: ManagementDecision
    feedback: str = Field(min_length=1, max_length=2_000)
    acceptance_criteria_met: list[str] = Field(default_factory=list)
    revision_instructions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_revision_instructions(self) -> "ManagementReview":
        if (
            self.decision is ManagementDecision.REVISION_REQUIRED
            and not self.revision_instructions
        ):
            raise ValueError("revision instructions are required for a revision decision")
        return self

