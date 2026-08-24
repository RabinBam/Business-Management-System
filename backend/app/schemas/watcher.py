from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class WatcherState(StrEnum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"


class WatcherEvent(BaseModel):
    workflow_id: str | None = None
    component: str
    event_type: str
    message: str
    retry_count: int = Field(default=0, ge=0)
    resolved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WatcherStatus(BaseModel):
    state: WatcherState
    active_incidents: int
    events: list[WatcherEvent] = Field(default_factory=list)
