"""ItemView model for TraceRTM."""

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin


class ItemView(Base, TimestampMixin):
    """Join table mapping items to views (many-to-many)."""

    __tablename__ = "item_views"
    __table_args__ = (
        Index("idx_item_views_item", "item_id"),
        Index("idx_item_views_view", "view_id"),
        Index("idx_item_views_project_view", "project_id", "view_id"),
        {"extend_existing": True},
    )

    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    view_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("views.id", ondelete="CASCADE"),
        primary_key=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ItemView(item_id={self.item_id!r}, view_id={self.view_id!r}, primary={self.is_primary})>"
