"""Item model for TraceRTM."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from tracertm.models.link import Link


def generate_item_uuid() -> uuid.UUID:
    """Generate a UUID for item ID."""
    return uuid.uuid4()


class Item(Base, TimestampMixin):
    """Item model representing a traceable item in any view.

    Items can be features, code files, tests, APIs, etc.
    """

    __tablename__ = "items"

    # Ensure existing table options are preserved if re-defining
    __table_args__ = (
        Index("idx_items_project_status", "project_id", "status"),
        Index("idx_items_project_type", "project_id", "type"),
        {"extend_existing": True},  # Allow re-definition if table exists
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_item_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    view: Mapped[str] = mapped_column("type", String(50), nullable=False, index=True)
    item_type: Mapped[str] = synonym("view")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="todo", index=True)

    priority: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    item_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    source_links: Mapped[list[Link]] = relationship(
        "Link",
        foreign_keys="Link.source_item_id",
        back_populates="source_item",
        lazy="select",
    )
    target_links: Mapped[list[Link]] = relationship(
        "Link",
        foreign_keys="Link.target_item_id",
        back_populates="target_item",
        lazy="select",
    )
    parent: Mapped[Item | None] = relationship(
        "Item",
        remote_side="Item.id",
        back_populates="children",
        foreign_keys=[parent_id],
        lazy="select",
    )
    children: Mapped[list[Item]] = relationship(
        "Item",
        back_populates="parent",
        foreign_keys=[parent_id],
        lazy="select",
    )

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,  # Enable optimistic locking
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize Item instance.

        Handles field aliasing and schema compatibility.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        # Map test-friendly aliases to internal column names
        if "type" in kwargs and "item_type" not in kwargs:
            kwargs["item_type"] = kwargs.pop("type")
        if "metadata" in kwargs and "item_metadata" not in kwargs:
            kwargs["item_metadata"] = kwargs.pop("metadata")
        # Drop fields not present in the Go-backed schema
        kwargs.pop("owner", None)
        kwargs.pop("node_kind_id", None)
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "type":
            return object.__getattribute__(self, "view")
        if name == "metadata":
            return object.__getattribute__(self, "item_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "type":
            name = "item_type"
        if name == "metadata":
            name = "item_metadata"
        super().__setattr__(name, value)

    @property
    def node_kind_id(self) -> None:
        """Compatibility property for Go-backed schema.

        Returns:
            Always None (not used in current schema).
        """
        return None

    @property
    def owner(self) -> None:
        """Compatibility property for Go-backed schema.

        Returns:
            Always None (not used in current schema).
        """
        return None

    def __getitem__(self, key: str) -> object:
        """Allow dict-style access used by some tests."""
        return getattr(self, key)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Item(id={self.id!r}, title={self.title!r}, view={self.view!r})>"
