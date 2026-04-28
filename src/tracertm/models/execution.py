"""Execution model for QA Integration system.

Tracks test/recording execution runs with Docker containers.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_execution_uuid() -> str:
    """Generate a UUID string for execution ID."""
    return str(uuid.uuid4())


class Execution(Base, TimestampMixin):
    """Execution model representing a test/recording run.

    Tracks VHS recordings, Playwright tests, Codex agent interactions,
    and custom test executions in Docker containers.
    """

    __tablename__ = "executions"

    __table_args__ = (
        Index("idx_executions_project_id", "project_id"),
        Index("idx_executions_status", "status"),
        Index("idx_executions_execution_type", "execution_type"),
        Index("idx_executions_trigger_source", "trigger_source"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_execution_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_run_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("test_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    item_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Execution type: vhs, playwright, codex, custom
    execution_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Trigger source: github_pr, github_push, webhook, manual
    trigger_source: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status: pending, running, passed, failed, cancelled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Docker container tracking
    container_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    container_image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Configuration and environment
    config: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)
    environment: Mapped[str | None] = mapped_column(Text, nullable=True)  # Encrypted env vars

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Results
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    artifacts: Mapped[list["ExecutionArtifact"]] = relationship(
        "ExecutionArtifact",
        back_populates="execution",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Execution(id={self.id!r}, type={self.execution_type!r}, status={self.status!r})>"


class ExecutionArtifact(Base):
    """Execution artifact model for screenshots, videos, GIFs, logs, and traces.

    Links artifacts to executions and optionally to graph nodes (items).
    """

    __tablename__ = "execution_artifacts"

    __table_args__ = (
        Index("idx_execution_artifacts_execution_id", "execution_id"),
        Index("idx_execution_artifacts_item_id", "item_id"),
        Index("idx_execution_artifacts_artifact_type", "artifact_type"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_execution_uuid)
    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Artifact type: screenshot, video, gif, log, trace, tape
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # File paths (local filesystem)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # File metadata
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    artifact_metadata: Mapped[dict[str, object] | None] = mapped_column(
        JSONType,
        nullable=True,
    )  # dimensions, duration, etc.

    # Timestamps
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    execution: Mapped["Execution"] = relationship("Execution", back_populates="artifacts")

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "artifact_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "artifact_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ExecutionArtifact(id={self.id!r}, type={self.artifact_type!r})>"
