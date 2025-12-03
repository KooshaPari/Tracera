"""Link schemas for TraceRTM."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LinkCreate(BaseModel):
    """Schema for creating a link."""

    source_item_id: str
    target_item_id: str
    link_type: str = Field(..., min_length=1, max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LinkResponse(BaseModel):
    """Schema for link response."""

    id: str
    project_id: str
    source_item_id: str
    target_item_id: str
    link_type: str
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
