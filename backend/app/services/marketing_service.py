from typing import Dict, Optional
from app.schemas.marketing import MarketingPlan
from app.agents.marketing_agent import MarketingAgent

class MarketingService:
    def __init__(self, agent: Optional[MarketingAgent] = None) -> None:
        # In-memory store mapping workflow_id to MarketingPlan
        self._plans: Dict[str, MarketingPlan] = {}
        self._agent = agent

    def set_agent(self, agent: MarketingAgent) -> None:
        """Inject the agent (useful for initialization when the AI provider is ready)."""
        self._agent = agent

    def get_plan(self, workflow_id: str) -> Optional[MarketingPlan]:
        """Retrieve a marketing plan by workflow ID."""
        return self._plans.get(workflow_id)

    def save_plan(self, plan: MarketingPlan) -> MarketingPlan:
        """Save or update a marketing plan."""
        # Note: The router already handles budget validation via Pydantic
        self._plans[plan.workflow_id] = plan
        return plan

    async def generate_plan(self, workflow_id: str, product_brief: str, max_budget: float, **kwargs) -> MarketingPlan:
        """Generate a new marketing plan using the AI agent."""
        if not self._agent:
            raise RuntimeError("MarketingAgent is not initialized. Cannot generate plan.")
            
        # Call the agent (which includes your with_retry_and_watch decorator)
        plan = await self._agent.generate_plan(
            product_brief=product_brief, 
            max_budget=max_budget,
            **kwargs
        )
        
        # Ensure the workflow_id is attached to the newly generated plan
        plan.workflow_id = workflow_id
        
        # Save to memory and return
        return self.save_plan(plan)

# Export a singleton instance so the router can import it directly
marketing_service = MarketingService()