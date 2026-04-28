"""Test Case model for TraceRTM Quality Engineering.

Represents individual test cases with steps, expected results, and automation status.
Supports lifecycle management from draft through approval to deprecation.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_test_case_uuid() -> str:
    """Generate a UUID string for test case ID."""
    return str(uuid.uuid4())


class TestCaseStatus(StrEnum):
    """Valid test case statuses following QA lifecycle."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TestCaseType(StrEnum):
    """Types of test cases."""

    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    UNIT = "unit"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    REGRESSION = "regression"
    SMOKE = "smoke"
    EXPLORATORY = "exploratory"


class TestCasePriority(StrEnum):
    """Priority levels for test case execution order."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AutomationStatus(StrEnum):
    """Automation implementation status."""

    NOT_AUTOMATED = "not_automated"
    IN_PROGRESS = "in_progress"
    AUTOMATED = "automated"
    CANNOT_AUTOMATE = "cannot_automate"


class TestCase(Base, TimestampMixin):
    """Test Case model representing an individual test specification.

    Test cases define what to test, how to test it, and expected results.
    They can be linked to requirements for traceability and grouped into
    test suites for organized execution.
    """

    __tablename__ = "test_cases"

    __table_args__ = (
        Index("idx_test_cases_project_status", "project_id", "status"),
        Index("idx_test_cases_project_type", "project_id", "test_type"),
        Index("idx_test_cases_project_priority", "project_id", "priority"),
        Index("idx_test_cases_automation_status", "automation_status"),
        Index("idx_test_cases_assigned_to", "assigned_to"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_test_case_uuid)
    test_case_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lifecycle Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=TestCaseStatus.DRAFT.value, index=True)

    # Classification
    test_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=TestCaseType.FUNCTIONAL.value,
        index=True,
    )
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default=TestCasePriority.MEDIUM.value, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Test Definition
    preconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_steps: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    expected_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    postconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_data: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Automation
    automation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=AutomationStatus.NOT_AUTOMATED.value,
        index=True,
    )
    automation_script_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    automation_framework: Mapped[str | None] = mapped_column(String(100), nullable=True)
    automation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Execution Estimates
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Assignment & Ownership
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Review & Approval Dates
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deprecated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deprecation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Execution History Summary
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_execution_result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_executions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pass_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Flexible metadata
    test_case_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships (lazy-loaded to avoid circular imports)
    suite_associations = relationship("TestSuiteTestCase", back_populates="test_case", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize TestCase instance.

        Handles metadata field aliasing for backward compatibility.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        # Map friendly aliases
        if "metadata" in kwargs and "test_case_metadata" not in kwargs:
            kwargs["test_case_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "test_case_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "test_case_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<TestCase(id={self.id!r}, number={self.test_case_number!r}, title={self.title!r})>"


class TestCaseActivity(Base, TimestampMixin):
    """Activity log for test case changes.

    Tracks all status transitions and significant updates for audit trail.
    """

    __tablename__ = "test_case_activities"

    __table_args__ = (
        Index("idx_test_case_activities_test_case_id", "test_case_id"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_test_case_uuid)
    test_case_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("test_cases.id", ondelete="CASCADE"),
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
        return f"<TestCaseActivity(id={self.id!r}, type={self.activity_type!r})>"
