<<<<<<< HEAD
from datetime import UTC, date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class WorkflowStatus(StrEnum):
    CREATED = "CREATED"
    SEGMENTING = "SEGMENTING"
    ASSIGNING = "ASSIGNING"
    EXECUTING = "EXECUTING"
    REVIEWING = "REVIEWING"
    REPORTING = "REPORTING"
    MARKETING = "MARKETING"
    FINAL_REVIEW = "FINAL_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    objective: str = Field(min_length=10, max_length=2_000)
    budget: float = Field(ge=0)
    deadline: date


class WorkflowRead(WorkflowCreate):
    id: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_stage: str = "created"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
=======
from datetime import UTC, date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class WorkflowStatus(StrEnum):
    CREATED = "CREATED"
    SEGMENTING = "SEGMENTING"
    ASSIGNING = "ASSIGNING"
    EXECUTING = "EXECUTING"
    REVIEWING = "REVIEWING"
    REPORTING = "REPORTING"
    MARKETING = "MARKETING"
    FINAL_REVIEW = "FINAL_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=120)
    objective: str = Field(min_length=10, max_length=2_000)
    budget: float = Field(ge=0)
    deadline: date


class WorkflowFailure(BaseModel):
    code: str
    message: str
    failed_stage: WorkflowStatus


class ExecutiveSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    objective: str
    overview: str
    major_work_completed: list[str] = Field(default_factory=list)
    financial_summary: str
    sales_prediction: str
    marketing_strategy: str
    major_risks: list[str] = Field(default_factory=list)
    management_recommendation: str


class WorkflowRead(WorkflowCreate):
    id: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_stage: str = "created"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failure: WorkflowFailure | None = None
    executive_summary: ExecutiveSummary | None = None
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
