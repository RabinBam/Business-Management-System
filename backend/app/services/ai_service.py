import json
from collections import defaultdict, deque
from collections.abc import Mapping
from functools import lru_cache
from typing import Protocol, TypeVar, cast

from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from app.config import Settings, settings

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class AIServiceError(RuntimeError):
    """Base error raised by the provider-neutral AI boundary."""


class AIConfigurationError(AIServiceError):
    """Raised when a selected provider is missing required configuration."""


class AIResponseError(AIServiceError):
    """Raised when a provider does not return a usable structured response."""


class AIService(Protocol):
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SchemaT],
        model: str | None = None,
    ) -> SchemaT: ...


class OpenAIProvider:
    """OpenAI Responses API adapter using native Pydantic structured outputs."""

    def __init__(
        self,
        config: Settings,
        *,
        client: AsyncOpenAI | None = None,
    ) -> None:
        if not config.openai_api_key and client is None:
            raise AIConfigurationError("OPENAI_API_KEY is required for AI_PROVIDER=openai")
        if not config.ai_primary_model:
            raise AIConfigurationError("AI_PRIMARY_MODEL is required for AI_PROVIDER=openai")
        self._config = config
        self._client = client or AsyncOpenAI(
            api_key=config.openai_api_key,
            timeout=config.ai_timeout_seconds,
            max_retries=config.ai_max_retries,
        )

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SchemaT],
        model: str | None = None,
    ) -> SchemaT:
        selected_model = model or self._config.ai_primary_model
        try:
            response = await self._client.responses.parse(
                model=selected_model,
                instructions=system_prompt,
                input=user_prompt,
                text_format=schema,
                store=False,
                timeout=self._config.ai_timeout_seconds,
            )
        except ValidationError as exc:
            raise AIResponseError("OpenAI output failed Pydantic validation") from exc
        except OpenAIError as exc:
            raise AIServiceError(f"OpenAI request failed: {exc.__class__.__name__}") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise AIResponseError("OpenAI returned no parsed structured output")
        try:
            return schema.model_validate(parsed)
        except ValidationError as exc:
            raise AIResponseError("OpenAI output failed Pydantic validation") from exc


class OpenRouterProvider:
    """OpenRouter chat adapter with schema-constrained, locally validated output."""

    def __init__(self, config: Settings, *, client: AsyncOpenAI | None = None) -> None:
        if not config.openrouter_api_key and client is None:
            raise AIConfigurationError("OPENROUTER_API_KEY is required for AI_PROVIDER=openrouter")
        if not config.ai_primary_model:
            raise AIConfigurationError("AI_PRIMARY_MODEL is required for AI_PROVIDER=openrouter")
        self._config = config
        self._client = client or AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.openrouter_api_key,
            timeout=config.ai_timeout_seconds,
            max_retries=config.ai_max_retries,
        )

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SchemaT],
        model: str | None = None,
    ) -> SchemaT:
        try:
            response = await self._client.chat.completions.parse(
                model=model or self._config.ai_primary_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=schema,
                max_tokens=self._config.ai_max_output_tokens,
                extra_body={
                    "provider": {"require_parameters": True},
                    "reasoning": {"enabled": False},
                },
                timeout=self._config.ai_timeout_seconds,
            )
        except (TypeError, AttributeError) as exc:
            raise AIResponseError(
                "OpenRouter returned an incomplete response. "
                "The free provider may be unavailable; retry the workflow later."
            ) from exc
        except ValidationError as exc:
            raise AIResponseError("OpenRouter output failed Pydantic validation") from exc
        except OpenAIError as exc:
            # Provider error bodies may contain sensitive request data.
            status = getattr(exc, "status_code", None)
            guidance = {
                400: "The model rejected the request. Check model structured-output support.",
                401: "The API key is invalid or expired. Update OPENROUTER_API_KEY in .env.",
                402: (
                    "Insufficient OpenRouter credits or key spending allowance. "
                    "Check your balance at https://openrouter.ai/settings/credits "
                    "and the key's spending limit. An unlimited key limit does not add credits."
                ),
                403: "Access was denied. Check OpenRouter account and provider restrictions.",
                404: "No matching model endpoint was found. Check the model ID and routing.",
                429: "OpenRouter rate limit reached. Wait before retrying the workflow.",
            }.get(status, "Check OpenRouter availability, model support, and your connection.")
            status_label = f" (HTTP {status})" if isinstance(status, int) else ""
            raise AIServiceError(
                f"OpenRouter request failed: {exc.__class__.__name__}{status_label}. " + guidance
            ) from exc
        if not response.choices or response.choices[0].message.parsed is None:
            raise AIResponseError("OpenRouter returned no parsed structured output")
        try:
            return schema.model_validate(response.choices[0].message.parsed)
        except ValidationError as exc:
            raise AIResponseError("OpenRouter output failed Pydantic validation") from exc


class MockAIProvider:
    """Deterministic provider for local runs and isolated agent tests.

    Tests may enqueue exact Pydantic objects. When no fixture is queued, a
    small schema-aware response keeps Person 1's integration path usable
    without credentials; it does not perform work owned by other team members.
    """

    def __init__(
        self,
        responses: Mapping[type[BaseModel], list[BaseModel | Mapping[str, object]]] | None = None,
    ) -> None:
        self._responses: dict[type[BaseModel], deque[BaseModel | Mapping[str, object]]] = (
            defaultdict(deque)
        )
        for schema, values in (responses or {}).items():
            self._responses[schema].extend(values)

    def enqueue(
        self,
        schema: type[SchemaT],
        response: SchemaT | Mapping[str, object],
    ) -> None:
        self._responses[schema].append(response)

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SchemaT],
        model: str | None = None,
    ) -> SchemaT:
        del system_prompt, model
        queued = self._responses[schema]
        payload: BaseModel | Mapping[str, object]
        if queued:
            payload = queued.popleft()
        else:
            payload = self._default_payload(schema, user_prompt)
        try:
            return schema.model_validate(payload)
        except ValidationError as exc:
            raise AIResponseError(f"Mock response for {schema.__name__} is invalid") from exc

    @staticmethod
    def _default_payload(schema: type[SchemaT], user_prompt: str) -> Mapping[str, object]:
        if schema.__name__ == "GeneratedTaskList":
            return {
                "tasks": [
                    {
                        "title": "Define the operating plan",
                        "description": (
                            "Translate the objective into scope, milestones, and owners."
                        ),
                        "priority": "HIGH",
                        "difficulty": 3,
                        "required_role": "Business Analyst",
                        "minimum_experience_years": 2,
                        "required_skills": ["planning", "analysis"],
                        "dependency_task_ids": [],
                        "expected_output": "An approved operating plan",
                        "acceptance_criteria": ["Scope, milestones, and owners are documented"],
                    },
                    {
                        "title": "Prepare execution readiness",
                        "description": "Confirm resources, risks, and delivery controls.",
                        "priority": "HIGH",
                        "difficulty": 3,
                        "required_role": "Project Manager",
                        "minimum_experience_years": 3,
                        "required_skills": ["delivery", "risk management"],
                        "dependency_task_ids": ["task-001"],
                        "expected_output": "A delivery-ready execution checklist",
                        "acceptance_criteria": ["Resources, risks, and controls are confirmed"],
                    },
                ]
            }
        if schema.__name__ == "GeneratedTask":
            return cast(Mapping[str, object], _extract_json_payload(user_prompt, "TASK_JSON"))
        if schema.__name__ == "ManagementReview":
            result = _extract_json_payload(user_prompt, "RESULT_JSON")
            return {
                "task_id": str(result.get("task_id", "unknown-task")),
                "decision": "APPROVED",
                "feedback": "The submitted result satisfies the stated acceptance criteria.",
                "acceptance_criteria_met": ["Management review completed"],
                "revision_instructions": [],
            }
        if schema.__name__ == "ExecutiveSummary":
            return {
                "objective": "Executive objective completed",
                "overview": "The workflow completed its managed review cycle.",
                "major_work_completed": ["Planned work reviewed by management"],
                "financial_summary": "See the approved financial report.",
                "sales_prediction": "See the approved sales prediction.",
                "marketing_strategy": "See the human-reviewed marketing plan.",
                "major_risks": [],
                "management_recommendation": "Proceed with the approved plan and monitor delivery.",
            }
        if schema.__name__ == "MarketingPlan":
            context = _extract_json_payload(user_prompt, "MARKETING_CONTEXT")
            budget = max(0.0, float(context.get("approved_budget", 0.0)))
            return {
                "workflow_id": str(context.get("workflow_id", "unknown-workflow")),
                "approved_budget": budget,
                "objective": str(context.get("objective", "Approved marketing objective")),
                "target_audience": "Customers most aligned with the approved objective",
                "allocations": [
                    {
                        "channel": "Digital advertising",
                        "amount": round(budget * 0.4, 2),
                        "reason": "Reach qualified audiences with measurable campaigns.",
                    },
                    {
                        "channel": "Content and search",
                        "amount": round(budget * 0.3, 2),
                        "reason": "Capture existing demand and explain the offer.",
                    },
                    {
                        "channel": "Partnerships",
                        "amount": round(budget * 0.2, 2),
                        "reason": "Extend trusted distribution without exceeding budget.",
                    },
                ],
                "timeline": [
                    "Week 1: prepare assets and measurement",
                    "Week 2: launch controlled campaigns",
                    "Weeks 3-4: optimize and report outcomes",
                ],
                "expected_outcome": "Measurable progress toward the approved objective.",
            }
        raise AIResponseError(f"No mock response is registered for {schema.__name__}")


def _extract_json_payload(prompt: str, marker: str) -> dict[str, object]:
    prefix = f"{marker}:"
    marker_index = prompt.find(prefix)
    if marker_index < 0:
        raise AIResponseError(f"Mock prompt is missing {prefix}")
    raw = prompt[marker_index + len(prefix) :].strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AIResponseError(f"Mock prompt contains invalid {marker} data") from exc
    if not isinstance(payload, dict):
        raise AIResponseError(f"{marker} must contain a JSON object")
    return cast(dict[str, object], payload)


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    provider = settings.ai_provider.strip().lower()
    if provider == "mock":
        return MockAIProvider()
    if provider == "openai":
        return OpenAIProvider(settings)
    if provider == "openrouter":
        return OpenRouterProvider(settings)
    raise AIConfigurationError(f"Unsupported AI_PROVIDER: {settings.ai_provider}")
