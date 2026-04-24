"""Agent Lock model for TraceRTM - represents locks on items held by agents."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin


def generate_lock_uuid() -> str:
    """Generate a UUID string for lock ID."""
    return str(uuid.uuid4())


class AgentLock(Base, TimestampMixin):
    """Represents a lock on an item held by an agent.

    Locks are used to:
    - Prevent concurrent modifications
    - Coordinate agent work
    - Ensure data consistency
    """

    __tablename__ = "agent_locks"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_lock_uuid)
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(255), ForeignKey("agents.id"), nullable=False, index=True)

    # Lock details
    lock_type: Mapped[str] = mapped_column(String(50), default="exclusive")  # exclusive, shared
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_locks_item_agent", "item_id", "agent_id"),
        Index("idx_locks_project_item", "project_id", "item_id"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<AgentLock(id={self.id!r}, item_id={self.item_id!r}, agent_id={self.agent_id!r})>"

    def is_expired(self) -> bool:
        """Check if lock has expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at
