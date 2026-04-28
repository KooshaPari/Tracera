"""Link schemas for TraceRTM."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LinkCreate(BaseModel):
    """Schema for creating a link."""

    source_item_id: str
    target_item_id: str
    link_type: str = Field(..., min_length=1, max_length=50)
    metadata: dict[str, object] = Field(default_factory=dict)


class LinkResponse(BaseModel):
    """Schema for link response."""

    id: str
    project_id: str
    source_item_id: str
    target_item_id: str
    link_type: str
    metadata: dict[str, object]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
