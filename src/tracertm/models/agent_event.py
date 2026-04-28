"""Agent Event model for TraceRTM - represents events from agents."""

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_event_uuid() -> uuid.UUID:
    """Generate a UUID for event ID."""
    return uuid.uuid4()


class AgentEvent(Base, TimestampMixin):
    """Represents an event from an agent.

    Events track:
    - Agent actions (create, update, delete)
    - Coordination messages
    - Conflict notifications
    - Status updates
    """

    __tablename__ = "agent_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_event_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)

    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # item_created, item_updated, conflict, etc.
    item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id"),
        nullable=True,
        index=True,
    )

    # Event data
    event_data: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    __table_args__ = (
        Index("idx_agent_events_project_agent", "project_id", "agent_id"),
        Index("idx_agent_events_project_type", "project_id", "event_type"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<AgentEvent(id={self.id!r}, type={self.event_type!r}, agent_id={self.agent_id!r})>"
