"""Workflow schedule tracking model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from datetime import datetime
else:
    datetime = __import__("datetime").datetime


def generate_workflow_schedule_uuid() -> uuid.UUID:
    """Generate a UUID for workflow schedule ID.

    Returns:
        New UUID for workflow schedule.
    """
    return uuid.uuid4()


class WorkflowSchedule(Base, TimestampMixin):
    """Model for tracking workflow execution schedules."""

    __tablename__ = "workflow_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_workflow_schedule_uuid)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    workflow_name: Mapped[str] = mapped_column(String(200), nullable=False)
    schedule_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    schedule_type: Mapped[str] = mapped_column(String(50), nullable=False, default="cron")
    schedule_spec: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)
    task_queue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_by_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_workflow_schedules_project", "project_id", "created_at"),
        Index("ix_workflow_schedules_status", "status"),
    )
