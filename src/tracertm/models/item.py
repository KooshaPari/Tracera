"""
Item model for TraceRTM.
"""

import uuid
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_item_uuid() -> str:
    """Generate a UUID string for item ID."""
    return str(uuid.uuid4())


class Item(Base, TimestampMixin):
    """
    Item model representing a traceable item in any view.

    Items can be features, code files, tests, APIs, etc.
    """

    __tablename__ = "items"

    # Ensure existing table options are preserved if re-defining
    __table_args__ = (
        Index("idx_items_project_view", "project_id", "view"),
        Index("idx_items_project_status", "project_id", "status"),
        Index("idx_items_project_type", "project_id", "item_type"),
        {"extend_existing": True},  # Allow re-definition if table exists
    )

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_item_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    view: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="todo", index=True
    )

    priority: Mapped[str] = mapped_column(
        String(50), nullable=False, default="medium", index=True
    )

    owner: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )

    parent_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    item_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    __mapper_args__: dict[str, Any] = {
        "version_id_col": version,  # Enable optimistic locking
    }

    def __init__(self, **kwargs: object) -> None:
        # Map test-friendly aliases to internal column names
        if "type" in kwargs and "item_type" not in kwargs:
            kwargs["item_type"] = kwargs.pop("type")
        if "metadata" in kwargs and "item_metadata" not in kwargs:
            kwargs["item_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        if name == "type":
            return object.__getattribute__(self, "item_type")
        if name == "metadata":
            return object.__getattribute__(self, "item_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "type":
            name = "item_type"
        if name == "metadata":
            name = "item_metadata"
        super().__setattr__(name, value)

    def __getitem__(self, key: str) -> object:
        """Allow dict-style access used by some tests."""
        return getattr(self, key)

    def __repr__(self) -> str:
        return f"<Item(id={self.id!r}, title={self.title!r}, view={self.view!r})>"
