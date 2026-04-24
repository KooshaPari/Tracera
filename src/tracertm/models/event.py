"""Event model for TraceRTM (event sourcing)."""

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


class Event(Base, TimestampMixin):
    """Event model for event sourcing.

    All state changes are recorded as events for history tracking.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    agent_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    data: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False)

    __table_args__ = (
        Index("idx_events_project_entity", "project_id", "entity_id"),
        Index("idx_events_project_type", "project_id", "event_type"),
        Index("idx_events_created_at", "created_at"),
        {"extend_existing": True},
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Event(id={self.id!r}, type={self.event_type!r}, entity={self.entity_id!r})>"
