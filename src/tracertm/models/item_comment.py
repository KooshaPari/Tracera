"""ItemComment model — per-item discussion thread entry."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin, generate_uuid


class ItemComment(Base, TimestampMixin):
    """A single comment posted on a TraceRTM item."""

    __tablename__ = "item_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(generate_uuid()))
    item_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ItemComment(id={self.id!r}, item_id={self.item_id!r}, author={self.author_name!r})>"
