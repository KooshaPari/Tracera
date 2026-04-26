"""CQRS Queries - read operations."""
from uuid import UUID
from pydantic import BaseModel, Field


class GetByIDQuery(BaseModel):
    """Query for getting an entity by ID."""

    id: UUID


class ListQuery(BaseModel):
    """Query for listing entities."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
