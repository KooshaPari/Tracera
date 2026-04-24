"""Project model for TraceRTM."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from tracertm.models.item import Item


def generate_uuid() -> uuid.UUID:
    """Generate a UUID for project ID."""
    return uuid.uuid4()


class Project(Base, TimestampMixin):
    """Project model representing a TraceRTM project.

    A project contains items, links, and configuration.
    """

    __tablename__ = "projects"
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    account_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSONType, nullable=False, default=dict)

    # Relationships
    items: Mapped[list[Item]] = relationship(
        "Item",
        foreign_keys="Item.project_id",
        lazy="select",
    )
    # account: Mapped["Account"] = relationship(
    #     "Account", back_populates="projects"

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "project_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "project_metadata"
        super().__setattr__(name, value)

    def __getitem__(self, key: str) -> object:
        """Get item."""
        return getattr(self, key)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Project(id={self.id!r}, name={self.name!r})>"
