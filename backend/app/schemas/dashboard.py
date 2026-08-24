from pydantic import BaseModel, Field

from app.schemas.watcher import WatcherEvent
from app.schemas.workflow import WorkflowRead


class DashboardMetrics(BaseModel):
    workflow_count: int = Field(ge=0)
    active_workflows: int = Field(ge=0)
    completed_workflows: int = Field(ge=0)
    failed_workflows: int = Field(ge=0)
    total_budget: float = Field(ge=0)
    planned_spend: float = Field(ge=0)
    available_budget: float
    predicted_growth_percent: float


class DashboardRead(BaseModel):
    metrics: DashboardMetrics
    recent_workflows: list[WorkflowRead] = Field(default_factory=list)
    recent_events: list[WatcherEvent] = Field(default_factory=list)
