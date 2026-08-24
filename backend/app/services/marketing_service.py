from threading import RLock

from app.agents.marketing_agent import MarketingAgent
from app.config import settings
from app.schemas.marketing import MarketingPlan
from app.services.ai_service import get_ai_service


class MarketingService:
    """Generate, validate, and persist marketing plans in memory."""

    def __init__(self, agent: MarketingAgent | None = None) -> None:
        self._plans: dict[str, MarketingPlan] = {}
        self._agent = agent
        self._lock = RLock()

    def set_agent(self, agent: MarketingAgent) -> None:
        self._agent = agent

    def get_plan(self, workflow_id: str) -> MarketingPlan | None:
        with self._lock:
            plan = self._plans.get(workflow_id)
            return plan.model_copy(deep=True) if plan is not None else None

    def save_plan(self, plan: MarketingPlan) -> MarketingPlan:
        plan.validate_budget()
        stored = plan.model_copy(deep=True)
        with self._lock:
            self._plans[plan.workflow_id] = stored
        return stored.model_copy(deep=True)

    async def generate_plan(
        self,
        *,
        workflow_id: str,
        product_brief: str,
        max_budget: float,
        approved_context: dict[str, object] | None = None,
    ) -> MarketingPlan:
        if self._agent is None:
            self._agent = MarketingAgent(
                get_ai_service(),
                model=settings.ai_primary_model or None,
            )
        plan = await self._agent.generate_plan(
            workflow_id=workflow_id,
            product_brief=product_brief,
            max_budget=max_budget,
            approved_context=approved_context,
        )
        return self.save_plan(plan)

    def clear(self) -> None:
        with self._lock:
            self._plans.clear()


marketing_service = MarketingService()


def get_marketing_service() -> MarketingService:
    return marketing_service
