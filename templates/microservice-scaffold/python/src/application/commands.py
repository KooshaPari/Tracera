"""CQRS Commands - write operations."""
from uuid import UUID
from pydantic import BaseModel, Field
from ..domain.errors import ValidationError


class CreateCommand(BaseModel):
    """Command for creating an entity."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class UpdateCommand(BaseModel):
    """Command for updating an entity."""

    id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class DeleteCommand(BaseModel):
    """Command for deleting an entity."""

    id: UUID
