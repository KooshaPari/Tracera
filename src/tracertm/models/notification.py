"""Notification model for user alerts."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin, generate_uuid


class Notification(Base, TimestampMixin):
    """User notification model."""

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # Optional: Link to a specific project if relevant
    project_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    type: Mapped[str] = mapped_column(String(50), nullable=False, default="info")  # info, success, warning, error
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Notification(id={self.id!r}, user={self.user_id!r}, title={self.title!r})>"
