"""
Project model for TraceRTM.
"""

import uuid
from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_uuid() -> uuid.UUID:
    """Generate a UUID for project ID."""
    return uuid.uuid4()


class Project(Base, TimestampMixin):
    """
    Project model representing a TraceRTM project.

    A project contains items, links, and configuration.
    """

    __tablename__ = "projects"
    __table_args__: dict[str, Any] = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    profile_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, index=True
    )
    account_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_metadata: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSONType, nullable=False, default=dict
    )

    # Relationships
    # account: Mapped["Account"] = relationship(
    #     "Account", back_populates="projects"
    # )

    def __getattribute__(self, name: str) -> object:
        if name == "metadata":
            return object.__getattribute__(self, "project_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "metadata":
            name = "project_metadata"
        super().__setattr__(name, value)

    def __getitem__(self, key: str) -> object:
        return getattr(self, key)

    def __repr__(self) -> str:
        return f"<Project(id={self.id!r}, name={self.name!r})>"
