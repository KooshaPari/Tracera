"""Agent session model for per-session sandbox persistence (DB-backed store)."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin


def generate_agent_session_uuid() -> uuid.UUID:
    """Generate a UUID for agent session ID.

    Returns:
        New UUID for session.
    """
    return uuid.uuid4()


class AgentSession(Base, TimestampMixin):
    """Persisted agent session: session_id -> sandbox_root, optional project."""

    __tablename__ = "agent_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_agent_session_uuid)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    sandbox_root: Mapped[str] = mapped_column(String(1024), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index("ix_agent_sessions_session_id", "session_id", unique=True),
        Index("ix_agent_sessions_project_id", "project_id"),
    )
