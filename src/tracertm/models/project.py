"""
Project model for TraceRTM.
"""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

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
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_metadata: Mapped[dict] = mapped_column(
        JSONType, nullable=False, default=dict
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id!r}, name={self.name!r})>"
