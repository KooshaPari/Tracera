"""Test Run model for tracking test execution instances."""

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
    event,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid_module.uuid4())


class TestRunStatus(StrEnum):
    """Status of a test run."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TestResultStatus(StrEnum):
    """Status of an individual test result."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    ERROR = "error"


class TestRunType(StrEnum):
    """Type of test run."""

    MANUAL = "manual"
    AUTOMATED = "automated"
    CI_CD = "ci_cd"
    SCHEDULED = "scheduled"


class TestRun(Base, TimestampMixin):
    """Execution instance of a test suite or ad-hoc tests."""

    __tablename__ = "test_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Source
    suite_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("test_suites.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status & type
    status: Mapped[TestRunStatus] = mapped_column(SQLEnum(TestRunStatus), nullable=False, default=TestRunStatus.PENDING)
    run_type: Mapped[TestRunType] = mapped_column(SQLEnum(TestRunType), nullable=False, default=TestRunType.MANUAL)

    # Environment
    environment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    build_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    build_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Timing
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Personnel
    initiated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    executed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metrics summary
    total_tests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blocked_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pass_rate: Mapped[float | None] = mapped_column(nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Categorization
    tags: Mapped[list[object] | None] = mapped_column(JSONType, nullable=True)

    # CI/CD integration
    external_run_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    webhook_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Extensible metadata
    run_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    suite = relationship("TestSuite")
    results = relationship("TestResult", back_populates="run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_test_runs_project_id", "project_id"),
        Index("ix_test_runs_suite_id", "suite_id"),
        Index("ix_test_runs_status", "status"),
        Index("ix_test_runs_run_type", "run_type"),
        Index("ix_test_runs_started_at", "started_at"),
        Index("ix_test_runs_completed_at", "completed_at"),
        Index("ix_test_runs_environment", "environment"),
        Index("ix_test_runs_initiated_by", "initiated_by"),
        Index("ix_test_runs_external_run_id", "external_run_id"),
    )


class TestResult(Base, TimestampMixin):
    """Individual test case result within a test run."""

    __tablename__ = "test_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    test_case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Result
    status: Mapped[TestResultStatus] = mapped_column(SQLEnum(TestResultStatus), nullable=False)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Personnel
    executed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Details
    actual_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Evidence
    screenshots: Mapped[list[object] | None] = mapped_column(JSONType, nullable=True)
    logs_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    attachments: Mapped[list[object] | None] = mapped_column(JSONType, nullable=True)

    # Step-level results
    step_results: Mapped[list[object] | None] = mapped_column(JSONType, nullable=True)

    # Defect tracking
    linked_defect_ids: Mapped[list[object] | None] = mapped_column(JSONType, nullable=True)
    created_defect_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Retry information
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_flaky: Mapped[bool] = mapped_column(default=False)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Extensible metadata
    run_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Relationships
    run = relationship("TestRun", back_populates="results")
    test_case = relationship("TestCase", back_populates="results")

    __table_args__ = (
        Index("ix_test_results_run_id", "run_id"),
        Index("ix_test_results_test_case_id", "test_case_id"),
        Index("ix_test_results_status", "status"),
        Index("ix_test_results_started_at", "started_at"),
        Index("ix_test_results_executed_by", "executed_by"),
        Index("ix_test_results_is_flaky", "is_flaky"),
    )


class TestRunActivity(Base):
    """Audit log for test run changes."""

    __tablename__ = "test_run_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    from_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    run_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        Index("ix_test_run_activities_run_id", "run_id"),
        Index("ix_test_run_activities_created_at", "created_at"),
        Index("ix_test_run_activities_type", "activity_type"),
    )


# Auto-generate run number
@event.listens_for(TestRun, "before_insert")
def generate_run_number(
    _mapper: Mapper["TestRun"],
    _connection: Connection,
    target: "TestRun",
) -> None:
    """Generate a sequential run number before insert."""
    if not target.run_number:
        short_id = str(uuid_module.uuid4())[:8].upper()
        target.run_number = f"TR-{short_id}"
