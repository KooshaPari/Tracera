"""
BDD Feature model.
"""

from typing import Any, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class Feature(Base, TimestampMixin):
    """BDD Feature."""

    __tablename__ = "features"
    __table_args__: dict[str, Any] = {"extend_existing": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    feature_number: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # User Story Format
    as_a: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    i_want: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    so_that: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Traceability
    related_requirements: Mapped[List[str]] = mapped_column(JSON, default=list)
    related_adrs: Mapped[List[str]] = mapped_column(JSON, default=list)

    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", backref="features")
