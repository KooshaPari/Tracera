"""
BDD Scenario model.
"""

from typing import Any, ClassVar

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class Scenario(Base, TimestampMixin):
    """BDD Scenario."""

    __tablename__: ClassVar[str] = "scenarios"  # type: ignore[misc]
    __table_args__: ClassVar[dict[str, Any]] = {"extend_existing": True}  # type: ignore[misc]

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    feature_id: Mapped[str] = mapped_column(String(36), ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    scenario_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    gherkin_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Steps
    background: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    given_steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    when_steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    then_steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)

    # Outline
    is_outline: Mapped[bool] = mapped_column(Boolean, default=False)
    examples: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Metadata & Traceability
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    requirement_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    test_case_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0)

    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    feature = relationship(
        "tracertm.models.feature.Feature",
        backref="scenarios",
    )
