"""Workflow model for TraceRTM."""

from __future__ import annotations

import uuid

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import GUID, Base, TimestampMixin


def generate_workflow_uuid() -> uuid.UUID:
    """Generate a UUID for workflow ID."""
    return uuid.uuid4()


class Workflow(Base, TimestampMixin):
    """Workflow model representing an agent workflow."""

    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=generate_workflow_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    workflow_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Workflow(id={self.id!r}, name={self.name!r})>"
