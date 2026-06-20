"""ExternalLink model for TraceRTM."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_external_link_uuid() -> str:
    """Generate a UUID string for external link ID."""
    return str(uuid.uuid4())


class ExternalLink(Base, TimestampMixin):
    """External link attached to an item (Figma, repo, doc, etc.)."""

    __tablename__ = "external_links"
    __table_args__ = (
        Index("idx_external_links_item", "item_id"),
        Index("idx_external_links_project", "project_id"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_external_link_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    target: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    link_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ExternalLink(id={self.id!r}, provider={self.provider!r})>"
