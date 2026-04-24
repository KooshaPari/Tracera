"""Requirement Quality model for ISO 29148 analysis and derived metrics."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.types import JSONType

from .base import Base, TimestampMixin, generate_uuid


class RequirementQuality(Base, TimestampMixin):
    """ISO 29148 Requirement Quality Analysis with derived metrics.

    Tracks:
    - Quality dimensions (unambiguity, completeness, verifiability, etc.)
    - Impact propagation (CPI, upstream/downstream)
    - Volatility and change tracking
    - WSJF prioritization
    - Verification evidence
    """

    __tablename__ = "requirement_quality"

    __table_args__ = (
        Index("idx_rq_item_id", "item_id"),
        Index("idx_rq_project_id", "project_id"),
        Index("idx_rq_overall_score", "overall_quality_score"),
        Index("idx_rq_volatility", "volatility_index"),
        Index("idx_rq_cpi", "change_propagation_index"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # ISO 29148 Quality Dimensions (0-1 scale)
    quality_scores: Mapped[dict[str, float]] = mapped_column(JSONType, nullable=False, default=dict)
    overall_quality_score: Mapped[float] = mapped_column(Float, default=0.5)

    # Quality Issues from Analysis
    quality_issues: Mapped[list[dict[str, object]]] = mapped_column(JSONType, nullable=False, default=list)

    # Impact Analysis
    change_propagation_index: Mapped[float] = mapped_column(Float, default=0.0)
    downstream_impact_count: Mapped[int] = mapped_column(Integer, default=0)
    upstream_dependency_count: Mapped[int] = mapped_column(Integer, default=0)
    impact_assessment: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Volatility Tracking
    change_count: Mapped[int] = mapped_column(Integer, default=0)
    volatility_index: Mapped[float] = mapped_column(Float, default=0.0)
    change_history: Mapped[list[dict[str, object]]] = mapped_column(JSONType, nullable=False, default=list)
    last_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # WSJF Prioritization
    wsjf_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    wsjf_components: Mapped[dict[str, float]] = mapped_column(JSONType, nullable=False, default=dict)

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_evidence: Mapped[list[dict[str, object]]] = mapped_column(JSONType, nullable=False, default=list)

    # Analysis Metadata
    last_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    analysis_version: Mapped[int] = mapped_column(Integer, default=1)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    item = relationship("Item", backref="requirement_quality")
