"""Add test coverage for traceability.

Revision ID: 010_add_test_coverage
Revises: 010_merge_heads
Create Date: 2024-01-27 00:00:00.000000

This migration must come after the merge_heads migration to ensure both
parallel 008 branches (graph views and test cases) have been applied.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010_add_test_coverage"
down_revision: str | None = "010_merge_heads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create test coverage tables."""
    # Test Coverages table - links test cases to requirements
    op.create_table(
        "test_coverages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("test_case_id", sa.String(36), sa.ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "requirement_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "coverage_type",
            sa.Enum("direct", "partial", "indirect", "regression", name="coveragetype"),
            nullable=False,
            server_default="direct",
        ),
        sa.Column(
            "status",
            sa.Enum("active", "deprecated", "needs_review", name="coveragestatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("coverage_percentage", sa.Integer(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by", sa.String(255), nullable=True),
        sa.Column("last_test_result", sa.String(50), nullable=True),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("coverage_metadata", sa.JSON(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Indexes for test_coverages
    op.create_index("ix_test_coverages_project_id", "test_coverages", ["project_id"])
    op.create_index("ix_test_coverages_test_case_id", "test_coverages", ["test_case_id"])
    op.create_index("ix_test_coverages_requirement_id", "test_coverages", ["requirement_id"])
    op.create_index("ix_test_coverages_coverage_type", "test_coverages", ["coverage_type"])
    op.create_index("ix_test_coverages_status", "test_coverages", ["status"])
    op.create_index("ix_test_coverages_unique", "test_coverages", ["test_case_id", "requirement_id"], unique=True)

    # Coverage Activities table - audit log
    op.create_table(
        "coverage_activities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("coverage_id", sa.String(36), sa.ForeignKey("test_coverages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_type", sa.String(100), nullable=False),
        sa.Column("from_value", sa.Text(), nullable=True),
        sa.Column("to_value", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.String(255), nullable=True),
        sa.Column("activity_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Indexes for coverage_activities
    op.create_index("ix_coverage_activities_coverage_id", "coverage_activities", ["coverage_id"])
    op.create_index("ix_coverage_activities_created_at", "coverage_activities", ["created_at"])
    op.create_index("ix_coverage_activities_type", "coverage_activities", ["activity_type"])


def downgrade() -> None:
    """Drop test coverage tables."""
    # Drop indexes
    op.drop_index("ix_coverage_activities_type", "coverage_activities")
    op.drop_index("ix_coverage_activities_created_at", "coverage_activities")
    op.drop_index("ix_coverage_activities_coverage_id", "coverage_activities")

    op.drop_index("ix_test_coverages_unique", "test_coverages")
    op.drop_index("ix_test_coverages_status", "test_coverages")
    op.drop_index("ix_test_coverages_coverage_type", "test_coverages")
    op.drop_index("ix_test_coverages_requirement_id", "test_coverages")
    op.drop_index("ix_test_coverages_test_case_id", "test_coverages")
    op.drop_index("ix_test_coverages_project_id", "test_coverages")

    # Drop tables
    op.drop_table("coverage_activities")
    op.drop_table("test_coverages")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS coveragestatus")
    op.execute("DROP TYPE IF EXISTS coveragetype")
