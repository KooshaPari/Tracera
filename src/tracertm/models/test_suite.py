"""Test Suite model for organizing test cases into hierarchical collections."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
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
    return str(uuid.uuid4())


class TestSuiteStatus(StrEnum):
    """Status of a test suite."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TestSuite(Base, TimestampMixin):
    """Organized collection of test cases.

    Supports hierarchical structure (parent/child suites).
    """

    __tablename__ = "test_suites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    suite_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[TestSuiteStatus] = mapped_column(
        SQLEnum(TestSuiteStatus),
        nullable=False,
        default=TestSuiteStatus.DRAFT,
    )

    # Hierarchy
    parent_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("test_suites.id", ondelete="SET NULL"),
        nullable=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Categorization
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[object] | None] = mapped_column(JSONType, nullable=True)

    # Execution settings
    is_parallel_execution: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Environment requirements
    required_environment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    environment_variables: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)
    setup_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    teardown_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ownership
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    responsible_team: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metrics
    total_test_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    automated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pass_rate: Mapped[float | None] = mapped_column(nullable=True)

    # Extensible metadata
    suite_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    parent = relationship("TestSuite", remote_side=[id], back_populates="children")
    children = relationship("TestSuite", back_populates="parent", cascade="all, delete-orphan")
    test_case_associations = relationship("TestSuiteTestCase", back_populates="suite", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_test_suites_project_id", "project_id"),
        Index("ix_test_suites_parent_id", "parent_id"),
        Index("ix_test_suites_status", "status"),
        Index("ix_test_suites_category", "category"),
        Index("ix_test_suites_owner", "owner"),
        Index("ix_test_suites_created_at", "created_at"),
    )


class TestSuiteTestCase(Base, TimestampMixin):
    """Association table linking test suites to test cases.

    Supports ordering and optional overrides.
    """

    __tablename__ = "test_suite_test_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    suite_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False)
    test_case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Ordering within suite
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Optional overrides for this suite context
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    skip_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_parameters: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Relationships
    suite = relationship("TestSuite", back_populates="test_case_associations")
    test_case = relationship("TestCase", back_populates="suite_associations")

    __table_args__ = (
        Index("ix_test_suite_test_cases_suite_id", "suite_id"),
        Index("ix_test_suite_test_cases_test_case_id", "test_case_id"),
        Index("ix_test_suite_test_cases_order", "suite_id", "order_index"),
    )


class TestSuiteActivity(Base):
    """Audit log for test suite changes."""

    __tablename__ = "test_suite_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    suite_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False)
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
        Index("ix_test_suite_activities_suite_id", "suite_id"),
        Index("ix_test_suite_activities_created_at", "created_at"),
        Index("ix_test_suite_activities_type", "activity_type"),
    )


# Auto-generate suite number
@event.listens_for(TestSuite, "before_insert")
def generate_suite_number(
    _mapper: Mapper[TestSuite],
    _connection: Connection,
    target: TestSuite,
) -> None:
    """Generate a sequential suite number before insert."""
    if not target.suite_number:
        short_id = str(uuid.uuid4())[:8].upper()
        target.suite_number = f"TS-{short_id}"
