from threading import RLock

from app.agents.marketing_agent import MarketingAgent
from app.config import settings
from app.database import SQLiteJsonStore, get_json_store
from app.schemas.marketing import MarketingPlan
from app.services.ai_service import get_ai_service


class MarketingService:
    """Generate, validate, and persist marketing plans in memory."""

    def __init__(
        self,
        agent: MarketingAgent | None = None,
        *,
        store: SQLiteJsonStore | None = None,
    ) -> None:
        self._plans: dict[str, MarketingPlan] = {}
        self._agent = agent
        self._lock = RLock()
        self._store = store
        if store is not None:
            self._plans = {
                workflow_id: MarketingPlan.model_validate(payload)
                for workflow_id, payload in store.list("marketing_plans")
            }

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
            if self._store is not None:
                self._store.put(
                    "marketing_plans",
                    plan.workflow_id,
                    stored.model_dump(mode="json"),
                )
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
            if self._store is not None:
                self._store.clear_namespace("marketing_plans")

    def delete_plan(self, workflow_id: str) -> None:
        with self._lock:
            self._plans.pop(workflow_id, None)
            if self._store is not None:
                self._store.delete("marketing_plans", workflow_id)

    def prune_orphans(self, valid_workflow_ids: set[str]) -> None:
        with self._lock:
            orphans = set(self._plans) - valid_workflow_ids
        for workflow_id in orphans:
            self.delete_plan(workflow_id)


marketing_service = MarketingService(store=get_json_store())


def get_marketing_service() -> MarketingService:
    return marketing_service
