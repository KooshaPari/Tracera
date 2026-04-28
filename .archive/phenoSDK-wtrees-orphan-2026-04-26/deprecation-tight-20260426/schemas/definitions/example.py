"""
Example Pydantic schema used to validate the schema tooling pipeline.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WorkspaceRecord(BaseModel):
    """
    Lightweight representation of a workspace row.
    """

    id: str = Field(..., description="Primary key for the workspace.")
    name: str = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    archived_at: datetime | None = Field(
        default=None,
        description="Soft-delete marker; null indicates active workspace.",
    )
