"""ADR (Architecture Decision Record) model."""

from datetime import date as date_type
from datetime import datetime

from sqlalchemy import JSON, Date, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class ADR(Base, TimestampMixin):
    """Architecture Decision Record (MADR 4.0 format)."""

    __tablename__ = "adrs"
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    adr_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # proposed, accepted, etc.

    # MADR Format
    context: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    consequences: Mapped[str] = mapped_column(Text, nullable=False)

    # Details
    decision_drivers: Mapped[list[str]] = mapped_column(JSON, default=list)
    considered_options: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)

    # Traceability
    related_requirements: Mapped[list[str]] = mapped_column(JSON, default=list)
    related_adrs: Mapped[list[str]] = mapped_column(JSON, default=list)
    supersedes: Mapped[str | None] = mapped_column(String(50), nullable=True)
    superseded_by: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Compliance
    compliance_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        String(50),
        nullable=True,  # Storing as ISO string for SQLite compatibility if needed, or actual DateTime
    )  # Correction: Using proper type below, Alembic usually handles DateTime fine

    # Metadata
    stakeholders: Mapped[list[str]] = mapped_column(JSON, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", backref="adrs")
