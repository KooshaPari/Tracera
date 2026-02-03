"""Workflow run tracking model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_workflow_run_uuid() -> str:
    return str(uuid.uuid4())


class WorkflowRun(Base, TimestampMixin):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_workflow_run_uuid)
    project_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    graph_id: Mapped[str | None] = mapped_column(
        String(255), ForeignKey("graphs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    workflow_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")

    external_run_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    payload: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    result: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_workflow_runs_project", "project_id", "created_at"),
        Index("ix_workflow_runs_status", "status"),
        Index("ix_workflow_runs_external", "external_run_id"),
    )
