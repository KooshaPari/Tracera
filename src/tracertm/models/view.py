"""View model for TraceRTM."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_view_uuid() -> str:
    """Generate a UUID string for view ID."""
    return str(uuid.uuid4())


class View(Base, TimestampMixin):
    """View model representing a named perspective for items.

    Views group items into user-facing, functional, UI, data, etc.
    """

    __tablename__ = "views"
    __table_args__ = (
        Index("idx_views_project_name", "project_id", "name", unique=True),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_view_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    view_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<View(id={self.id!r}, name={self.name!r})>"
