"""Workflow run tracking model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from datetime import datetime
else:
    datetime = __import__("datetime").datetime


def generate_workflow_run_uuid() -> str:
    """Generate a UUID string for workflow run ID.

    Returns:
        New UUID string for workflow run.
    """
    return str(uuid.uuid4())


class WorkflowRun(Base, TimestampMixin):
    """Workflow run tracking record."""

    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=generate_workflow_run_uuid,
    )
    workflow_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("workflows.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    output: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    __table_args__ = (Index("idx_workflow_runs_workflow_id", "workflow_id"),)
