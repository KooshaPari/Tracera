"""Event schemas for TraceRTM."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Schema for creating an event."""

    event_type: str = Field(..., min_length=1, max_length=50)
    event_data: dict[str, Any]
    agent_id: str
    item_id: str | None = None


class EventResponse(BaseModel):
    """Schema for event response."""

    id: str
    project_id: str
    item_id: str | None
    event_type: str
    event_data: dict[str, Any]
    agent_id: str
    timestamp: datetime

    class Config:
        from_attributes = True
