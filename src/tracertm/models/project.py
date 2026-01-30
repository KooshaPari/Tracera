"""
Project model for TraceRTM.
"""

import uuid
from typing import Any

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_uuid() -> str:
    """Generate a UUID string for project ID."""
    return str(uuid.uuid4())


class Project(Base, TimestampMixin):
    """
    Project model representing a TraceRTM project.

    A project contains items, links, and configuration.
    """

    __tablename__ = "projects"
    __table_args__: dict[str, Any] = {"extend_existing": True}

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_uuid
    )
    account_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_metadata: Mapped[dict[str, object]] = mapped_column(
        JSONType, nullable=False, default=dict
    )

    # Relationships
    account: Mapped["Account"] = relationship(
        "Account", back_populates="projects"
    )

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
