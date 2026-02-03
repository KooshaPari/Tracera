"""
Link model for TraceRTM.
"""

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_link_uuid() -> uuid.UUID:
    """Generate a UUID for link ID."""
    return uuid.uuid4()


class Link(Base, TimestampMixin):
    """
    Link model representing relationships between items.

    Links are bidirectional and typed (implements, tests, depends_on, etc.).
    """

    __tablename__ = "links"
    __table_args__ = (
        Index("idx_links_source_target", "source_item_id", "target_item_id"),
        Index("idx_links_project_type", "project_id", "link_type"),
        Index("idx_links_project_graph", "project_id", "graph_id"),
        {"extend_existing": True},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_link_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    graph_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("graphs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    link_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    link_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    def __init__(self, **kwargs: object) -> None:
        if "type" in kwargs and "link_type" not in kwargs:
            kwargs["link_type"] = kwargs.pop("type")
        if "metadata" in kwargs and "link_metadata" not in kwargs:
            kwargs["link_metadata"] = kwargs.pop("metadata")
        if "source_id" in kwargs and "source_item_id" not in kwargs:
            kwargs["source_item_id"] = kwargs.pop("source_id")
        if "target_id" in kwargs and "target_item_id" not in kwargs:
            kwargs["target_item_id"] = kwargs.pop("target_id")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        if name == "type":
            return object.__getattribute__(self, "link_type")
        if name == "metadata":
            return object.__getattribute__(self, "link_metadata")
        if name == "source_id":
            return object.__getattribute__(self, "source_item_id")
        if name == "target_id":
            return object.__getattribute__(self, "target_item_id")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "type":
            name = "link_type"
        if name == "metadata":
            name = "link_metadata"
        if name == "source_id":
            name = "source_item_id"
        if name == "target_id":
            name = "target_item_id"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return f"<Link(id={self.id!r}, type={self.link_type!r})>"
