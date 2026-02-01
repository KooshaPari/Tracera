"""
ADR (Architecture Decision Record) model.
"""

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from datetime import date as date_type
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class ADR(Base, TimestampMixin):
    """Architecture Decision Record (MADR 4.0 format)."""

    __tablename__ = "adrs"
    __table_args__: dict[str, Any] = {"extend_existing": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    adr_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # proposed, accepted, etc.

    # MADR Format
    context: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    consequences: Mapped[str] = mapped_column(Text, nullable=False)

    # Details
    decision_drivers: Mapped[List[str]] = mapped_column(JSON, default=list)
    considered_options: Mapped[List[dict]] = mapped_column(JSON, default=list)
    
    # Traceability
    related_requirements: Mapped[List[str]] = mapped_column(JSON, default=list)
    related_adrs: Mapped[List[str]] = mapped_column(JSON, default=list)
    supersedes: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    superseded_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Compliance
    compliance_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        String(50), nullable=True  # Storing as ISO string for SQLite compatibility if needed, or actual DateTime
    ) # Correction: Using proper type below, Alembic usually handles DateTime fine

    # Metadata
    stakeholders: Mapped[List[str]] = mapped_column(JSON, default=list)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", backref="adrs")
