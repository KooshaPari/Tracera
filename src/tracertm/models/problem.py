"""Problem model for TraceRTM.

Represents high-level problems that need investigation, root cause analysis,
and resolution tracking. Follows ITIL problem management patterns.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_problem_uuid() -> str:
    """Generate a UUID string for problem ID."""
    return str(uuid.uuid4())


class ProblemStatus(StrEnum):
    """Valid problem statuses following ITIL lifecycle."""

    OPEN = "open"
    IN_INVESTIGATION = "in_investigation"
    PENDING_WORKAROUND = "pending_workaround"
    KNOWN_ERROR = "known_error"
    AWAITING_FIX = "awaiting_fix"
    CLOSED = "closed"


class ResolutionType(StrEnum):
    """How the problem was resolved."""

    PERMANENT_FIX = "permanent_fix"
    WORKAROUND_ONLY = "workaround_only"
    CANNOT_REPRODUCE = "cannot_reproduce"
    DEFERRED = "deferred"
    BY_DESIGN = "by_design"


class ImpactLevel(StrEnum):
    """Impact severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RCAMethod(StrEnum):
    """Root Cause Analysis methodologies."""

    FIVE_WHYS = "five_whys"
    FISHBONE = "fishbone"
    KEPNER_TREGOE = "kepner_tregoe"
    FMEA = "fmea"
    PARETO = "pareto"
    OTHER = "other"


class RootCauseCategory(StrEnum):
    """Categories of root causes."""

    SYSTEMATIC = "systematic"
    HUMAN = "human"
    ENVIRONMENTAL = "environmental"
    PROCESS = "process"
    TECHNOLOGY = "technology"


class Problem(Base, TimestampMixin):
    """Problem model representing a tracked problem requiring investigation.

    Problems have a complex lifecycle from Open through Investigation
    to Known Error and eventual resolution. They support:
    - Root Cause Analysis workflows
    - Known Error Database integration
    - Impact assessment
    - Workaround and permanent fix tracking
    """

    __tablename__ = "problems"

    __table_args__ = (
        Index("idx_problems_project_status", "project_id", "status"),
        Index("idx_problems_project_priority", "project_id", "priority"),
        Index("idx_problems_project_impact", "project_id", "impact_level"),
        Index("idx_problems_assigned_to", "assigned_to"),
        Index("idx_problems_category", "category"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_problem_uuid)
    problem_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lifecycle Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ProblemStatus.OPEN.value, index=True)
    resolution_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Classification
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    sub_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Impact Assessment
    impact_level: Mapped[str] = mapped_column(String(20), nullable=False, default=ImpactLevel.MEDIUM.value, index=True)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False, default=ImpactLevel.MEDIUM.value)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default=ImpactLevel.MEDIUM.value, index=True)
    affected_systems: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    affected_users_estimated: Mapped[int | None] = mapped_column(Integer, nullable=True)
    business_impact_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Root Cause Analysis
    rca_performed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rca_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rca_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rca_data: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    root_cause_identified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    root_cause_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    root_cause_confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rca_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rca_completed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Solutions & Workarounds
    workaround_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    workaround_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    workaround_effectiveness: Mapped[str | None] = mapped_column(String(50), nullable=True)

    permanent_fix_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    permanent_fix_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    permanent_fix_implemented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    permanent_fix_change_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Known Error Integration
    known_error_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    knowledge_article_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Assignment & Ownership
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    assigned_team: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Closure
    closed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closure_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Target dates
    target_resolution_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Flexible metadata
    problem_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize Problem instance.

        Handles metadata field aliasing for backward compatibility.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        # Map friendly aliases
        if "metadata" in kwargs and "problem_metadata" not in kwargs:
            kwargs["problem_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "problem_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "problem_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Problem(id={self.id!r}, number={self.problem_number!r}, title={self.title!r})>"


class ProblemActivity(Base, TimestampMixin):
    """Activity log for problem changes.

    Tracks all status transitions and significant updates for audit trail.
    """

    __tablename__ = "problem_activities"

    __table_args__ = (
        Index("idx_problem_activities_problem_id", "problem_id"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_problem_uuid)
    problem_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    to_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activity_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ProblemActivity(id={self.id!r}, type={self.activity_type!r})>"
