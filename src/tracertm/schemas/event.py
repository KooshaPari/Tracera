"""Event schemas for TraceRTM."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """Schema for creating an event."""

    event_type: str = Field(..., min_length=1, max_length=50)
    event_data: dict[str, object]
    agent_id: str
    item_id: str | None = None


class EventResponse(BaseModel):
    """Schema for event response."""

    id: str
    project_id: str
    item_id: str | None
    event_type: str
    event_data: dict[str, object]
    agent_id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
