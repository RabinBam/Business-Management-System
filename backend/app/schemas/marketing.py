from pydantic import BaseModel, Field


class BudgetAllocation(BaseModel):
    channel: str
    amount: float = Field(ge=0)
    reason: str


class MarketingPlan(BaseModel):
    workflow_id: str
    approved_budget: float = Field(ge=0)
    objective: str
    target_audience: str
    allocations: list[BudgetAllocation] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    expected_outcome: str = ""

    def validate_budget(self) -> float:
        allocated = sum(item.amount for item in self.allocations)
        if allocated > self.approved_budget:
            raise ValueError("Marketing allocation exceeds the approved budget")
        return allocated

