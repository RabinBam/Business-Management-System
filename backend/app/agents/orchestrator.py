import json
from collections.abc import Callable
from datetime import date

from app.schemas.task import GeneratedTask, GeneratedTaskList
from app.services.ai_service import AIResponseError, AIService, get_ai_service

SYSTEM_PROMPT = """You are the AegisFlow work decomposition agent.
Break one executive objective into a small set of concrete, verifiable tasks.
Plan the work; do not perform it.

For dependency_task_ids, task positions are canonical IDs: task-001, task-002,
and so on. A task may depend only on an earlier task. Every task must state a
role, minimum experience, required skills, expected output, and measurable
acceptance criteria. Return only data matching the supplied schema."""

ValidationFailureHandler = Callable[[Exception, int], None]


class OrchestrationError(RuntimeError):
    """Raised when a valid task plan cannot be produced."""


class OrchestrationValidationError(OrchestrationError):
    """Raised when structured output violates deterministic planning rules."""


class Orchestrator:
    def __init__(
        self,
        ai_service: AIService,
        *,
        model: str | None = None,
        max_tasks: int = 8,
        validation_retries: int = 1,
        on_validation_failure: ValidationFailureHandler | None = None,
    ) -> None:
        if max_tasks < 1:
            raise ValueError("max_tasks must be positive")
        if validation_retries < 0:
            raise ValueError("validation_retries cannot be negative")
        self._ai_service = ai_service
        self._model = model
        self._max_tasks = max_tasks
        self._validation_retries = validation_retries
        self._on_validation_failure = on_validation_failure

    async def segment(
        self,
        *,
        objective: str,
        budget: float,
        deadline: date,
    ) -> list[GeneratedTask]:
        prompt = self._build_prompt(objective=objective, budget=budget, deadline=deadline)
        last_error: Exception | None = None

        for attempt in range(self._validation_retries + 1):
            try:
                plan = await self._ai_service.generate_structured(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=prompt,
                    schema=GeneratedTaskList,
                    model=self._model,
                )
                self._validate_business_rules(plan)
                return plan.tasks
            except (AIResponseError, OrchestrationValidationError) as exc:
                last_error = exc
                if self._on_validation_failure is not None:
                    self._on_validation_failure(exc, attempt)
                if attempt == self._validation_retries:
                    break
                prompt = self._retry_prompt(prompt, exc)

        raise OrchestrationError("Unable to produce a valid task plan") from last_error

    def _validate_business_rules(self, plan: GeneratedTaskList) -> None:
        if len(plan.tasks) > self._max_tasks:
            raise OrchestrationValidationError(
                f"Plan contains {len(plan.tasks)} tasks; maximum is {self._max_tasks}"
            )

        for index, task in enumerate(plan.tasks, start=1):
            for dependency in task.dependency_task_ids:
                dependency_index = _dependency_index(dependency)
                if dependency_index >= index:
                    raise OrchestrationValidationError(
                        f"task-{index:03d} must depend only on earlier tasks"
                    )

    def _build_prompt(self, *, objective: str, budget: float, deadline: date) -> str:
        payload = {
            "objective": objective,
            "approved_budget": budget,
            "deadline": deadline.isoformat(),
            "maximum_tasks": self._max_tasks,
        }
        return "EXECUTIVE_OBJECTIVE:\n" + json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _retry_prompt(original_prompt: str, error: Exception) -> str:
        return (
            original_prompt
            + "\n\nThe previous plan failed deterministic validation. Regenerate the entire plan. "
            + f"Validation issue: {error}"
        )


def _dependency_index(task_id: str) -> int:
    try:
        prefix, number = task_id.split("-", maxsplit=1)
        if prefix != "task":
            raise ValueError
        return int(number)
    except ValueError as exc:
        raise OrchestrationValidationError(
            f"Invalid dependency ID '{task_id}'; expected task-NNN"
        ) from exc


async def segment_objective(
    *,
    objective: str,
    budget: float,
    deadline: date,
    ai_service: AIService | None = None,
    model: str | None = None,
    max_tasks: int = 8,
) -> list[GeneratedTask]:
    """Functional entry point used by the workflow service and isolated tests."""

    orchestrator = Orchestrator(
        ai_service or get_ai_service(),
        model=model,
        max_tasks=max_tasks,
    )
    return await orchestrator.segment(
        objective=objective,
        budget=budget,
        deadline=deadline,
    )
