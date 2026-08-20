from pydantic import BaseModel, Field


class FinancialSummary(BaseModel):
    total_budget: float = Field(ge=0)
    planned_spend: float = Field(ge=0)
    remaining_budget: float


class SalesPrediction(BaseModel):
    current_sales: float = Field(ge=0)
    predicted_sales: float = Field(ge=0)
    growth_percent: float
    method: str = "linear_regression"


class Report(BaseModel):
    workflow_id: str
    financial: FinancialSummary
    sales_prediction: SalesPrediction
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

