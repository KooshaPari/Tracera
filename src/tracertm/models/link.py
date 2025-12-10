"""
Link model for TraceRTM.
"""

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_link_uuid() -> str:
    """Generate a UUID string for link ID."""
    return str(uuid.uuid4())


class Link(Base, TimestampMixin):
    """
    Link model representing relationships between items.

    Links are bidirectional and typed (implements, tests, depends_on, etc.).
    """

    __tablename__ = "links"
    __table_args__ = (
        Index("idx_links_source_target", "source_item_id", "target_item_id"),
        Index("idx_links_project_type", "project_id", "link_type"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_link_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_item_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_item_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    link_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    link_metadata: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    def __init__(self, **kwargs):
        if "type" in kwargs and "link_type" not in kwargs:
            kwargs["link_type"] = kwargs.pop("type")
        if "metadata" in kwargs and "link_metadata" not in kwargs:
            kwargs["link_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __getattribute__(self, name):
        if name == "type":
            return object.__getattribute__(self, "link_type")
        if name == "metadata":
            return object.__getattribute__(self, "link_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name == "type":
            name = "link_type"
        if name == "metadata":
            name = "link_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return f"<Link(id={self.id!r}, type={self.link_type!r})>"
