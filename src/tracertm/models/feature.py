"""BDD Feature model."""

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class Feature(Base, TimestampMixin):
    """BDD Feature."""

    __tablename__ = "features"
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_number: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # User Story Format
    as_a: Mapped[str | None] = mapped_column(String(255), nullable=True)
    i_want: Mapped[str | None] = mapped_column(String(255), nullable=True)
    so_that: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Traceability
    related_requirements: Mapped[list[str]] = mapped_column(JSON, default=list)
    related_adrs: Mapped[list[str]] = mapped_column(JSON, default=list)

    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", backref="features")
