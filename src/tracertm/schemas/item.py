"""Item schemas for TraceRTM."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema for creating an item."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    view: str = Field(..., min_length=1, max_length=50)
    item_type: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="todo", max_length=50)
    parent_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: str | None = Field(None, max_length=50)
    parent_id: str | None = None
    metadata: dict[str, Any] | None = None


class ItemResponse(BaseModel):
    """Schema for item response."""

    id: str
    project_id: str
    title: str
    description: str | None
    view: str
    item_type: str
    status: str
    parent_id: str | None
    metadata: dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: str | None

    class Config:
        from_attributes = True
