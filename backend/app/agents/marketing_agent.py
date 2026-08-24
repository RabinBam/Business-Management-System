from app.schemas.marketing import MarketingPlan
from app.agents.watcher import with_retry_and_watch

class MarketingAgent:
    def __init__(self, ai_provider):
        self.ai_provider = ai_provider

    @with_retry_and_watch(service_name="MarketingAgent")
    async def generate_plan(self, product_brief: str, max_budget: float, **kwargs) -> MarketingPlan:
        # 1. Construct the prompt for the AI
        prompt = (
            f"Create a marketing plan for the following product: {product_brief}. "
            f"The strict maximum budget is ${max_budget}. "
            f"Return the response as a JSON object matching this schema: "
            f"id (string), campaign_name (string), target_audience (list of strings), "
            f"estimated_budget (number), max_budget (number), and strategy (string)."
        )
        
        # 2. Call AI provider
        raw_response = await self.ai_provider.generate(prompt=prompt, **kwargs)
        
        # 3. Parse and validate using your Pydantic schema
        plan = MarketingPlan.model_validate_json(raw_response)
        
        return plan