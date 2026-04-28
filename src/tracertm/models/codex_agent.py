"""Codex Agent Interaction model for QA Integration system.

Tracks AI agent tasks for code review, image/video analysis, and test generation.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base
from tracertm.models.types import JSONType


def generate_codex_uuid() -> str:
    """Generate a UUID string for codex interaction ID."""
    return str(uuid.uuid4())


class CodexAgentInteraction(Base):
    """Codex Agent Interaction model for tracking AI agent tasks.

    Logs interactions with Codex CLI for reviewing images, videos,
    code, and generating tests.
    """

    __tablename__ = "codex_agent_interactions"

    __table_args__ = (
        Index("idx_codex_interactions_project_id", "project_id"),
        Index("idx_codex_interactions_execution_id", "execution_id"),
        Index("idx_codex_interactions_status", "status"),
        Index("idx_codex_interactions_task_type", "task_type"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_codex_uuid)
    execution_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("executions.id", ondelete="SET NULL"),
        nullable=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    artifact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("execution_artifacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Task type: review_image, review_video, code_review, generate_test, analyze_logs
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Input/output data
    input_data: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)
    output_data: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Task prompt and response
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status: pending, running, completed, failed, cancelled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Usage tracking
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<CodexAgentInteraction(id={self.id!r}, task_type={self.task_type!r}, status={self.status!r})>"
