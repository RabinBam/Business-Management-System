import json
from collections.abc import Mapping

from app.schemas.marketing import MarketingPlan
from app.services.ai_service import AIService

MARKETING_SYSTEM_PROMPT = """You are Byapari's marketing planning agent.
Use only the supplied management-approved objective and report summary. Create
a practical plan with an audience, channel allocations, timeline, and expected
outcome. Never exceed the approved budget and do not invent access to private
financial details that are not in the supplied context."""


class MarketingAgent:
    """Generate schema-validated plans through the shared AI service boundary."""

    def __init__(self, ai_service: AIService, *, model: str | None = None) -> None:
        self._ai_service = ai_service
        self._model = model

    async def generate_plan(
        self,
        *,
        workflow_id: str,
        product_brief: str,
        max_budget: float,
        approved_context: Mapping[str, object] | None = None,
    ) -> MarketingPlan:
        context: dict[str, object] = {
            "workflow_id": workflow_id,
            "objective": product_brief,
            "approved_budget": max_budget,
            "approved_context": dict(approved_context or {}),
        }
        plan = await self._ai_service.generate_structured(
            system_prompt=MARKETING_SYSTEM_PROMPT,
            user_prompt="MARKETING_CONTEXT:\n" + json.dumps(context, ensure_ascii=False),
            schema=MarketingPlan,
            model=self._model,
        )
        authoritative = plan.model_copy(
            update={
                "workflow_id": workflow_id,
                "approved_budget": max_budget,
                "objective": product_brief,
            }
        )
        authoritative.validate_budget()
        return authoritative
