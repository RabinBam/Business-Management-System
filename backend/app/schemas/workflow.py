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
