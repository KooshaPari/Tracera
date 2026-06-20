"""BDD Scenario model."""

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class Scenario(Base, TimestampMixin):
    """BDD Scenario."""

    __tablename__ = "scenarios"
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    feature_id: Mapped[str] = mapped_column(String(36), ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    scenario_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    gherkin_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Steps
    background: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    given_steps: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    when_steps: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    then_steps: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)

    # Outline
    is_outline: Mapped[bool] = mapped_column(Boolean, default=False)
    examples: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    # Metadata & Traceability
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    requirement_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    test_case_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0)

    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    feature = relationship(
        "tracertm.models.feature.Feature",
        backref="scenarios",
    )
