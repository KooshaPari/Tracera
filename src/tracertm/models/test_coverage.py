"""Test Coverage model for tracking test-to-requirement traceability."""

import uuid as uuid_module
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid_module.uuid4())


class CoverageType(StrEnum):
    """Type of coverage relationship."""

    DIRECT = "direct"  # Test directly tests the requirement
    PARTIAL = "partial"  # Test partially covers the requirement
    INDIRECT = "indirect"  # Test indirectly verifies requirement
    REGRESSION = "regression"  # Test is for regression testing


class CoverageStatus(StrEnum):
    """Status of the coverage mapping."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    NEEDS_REVIEW = "needs_review"


class TestCoverage(Base, TimestampMixin):
    """Links test cases to requirements (items) for traceability.

    Enables coverage analysis and traceability matrices.
    """

    __tablename__ = "test_coverages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    # The test case providing coverage
    test_case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
    )

    # The requirement/item being covered
    requirement_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Coverage details
    coverage_type: Mapped[CoverageType] = mapped_column(
        SQLEnum(CoverageType),
        nullable=False,
        default=CoverageType.DIRECT,
    )
    status: Mapped[CoverageStatus] = mapped_column(
        SQLEnum(CoverageStatus),
        nullable=False,
        default=CoverageStatus.ACTIVE,
    )

    # Coverage percentage (0-100) for partial coverage
    coverage_percentage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Rationale for the coverage mapping
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Verification tracking
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_test_result: Mapped[str | None] = mapped_column(String(50), nullable=True)  # passed/failed/etc
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Personnel
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Extensible metadata
    coverage_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    test_case = relationship("TestCase")
    requirement = relationship("Item")

    __table_args__ = (
        Index("ix_test_coverages_project_id", "project_id"),
        Index("ix_test_coverages_test_case_id", "test_case_id"),
        Index("ix_test_coverages_requirement_id", "requirement_id"),
        Index("ix_test_coverages_coverage_type", "coverage_type"),
        Index("ix_test_coverages_status", "status"),
        # Unique constraint: one test case can only map to a requirement once
        Index("ix_test_coverages_unique", "test_case_id", "requirement_id", unique=True),
    )


class CoverageActivity(Base):
    """Audit log for coverage changes."""

    __tablename__ = "coverage_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    coverage_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_coverages.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    from_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activity_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        Index("ix_coverage_activities_coverage_id", "coverage_id"),
        Index("ix_coverage_activities_created_at", "created_at"),
        Index("ix_coverage_activities_type", "activity_type"),
    )
