"""Agent checkpoint model for conversation state snapshots."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin


def generate_checkpoint_uuid() -> uuid.UUID:
    """Generate a UUID for agent checkpoint ID.

    Returns:
        New UUID for checkpoint.
    """
    return uuid.uuid4()


class AgentCheckpoint(Base, TimestampMixin):
    """Checkpoint for agent session conversation state and sandbox snapshot.

    Stores conversation history, tool use state, and reference to MinIO sandbox snapshot.
    Used for session resumability after crashes or restarts.
    """

    __tablename__ = "agent_checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_checkpoint_uuid)

    # Reference to agent session
    session_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("agent_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Turn number in conversation (for ordering)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Conversation state snapshot (messages, tool use history, etc.)
    state_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)

    # Reference to sandbox snapshot in MinIO (S3)
    sandbox_snapshot_s3_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Checkpoint metadata
    # - model used, token counts, duration, etc.
    checkpoint_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)

    # Optional description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_agent_checkpoints_session_id", "session_id"),
        Index("ix_agent_checkpoints_turn_number", "turn_number"),
        Index(
            "ix_agent_checkpoints_session_turn",
            "session_id",
            "turn_number",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<AgentCheckpoint(id={self.id}, session_id={self.session_id}, "
            f"turn={self.turn_number}, has_snapshot={bool(self.sandbox_snapshot_s3_key)})>"
        )
