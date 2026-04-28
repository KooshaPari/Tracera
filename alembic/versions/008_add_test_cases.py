"""Add test_cases and test_case_activities tables for Quality Engineering.

Revision ID: 008_add_test_cases
Revises: 007_add_problems_and_processes
Create Date: 2026-01-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008_add_test_cases"
down_revision: str | None = "007_add_problems_and_processes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    # Create test_cases table
    op.create_table(
        "test_cases",
        # Primary key
        sa.Column("id", sa.String(255), primary_key=True),
        # Unique identifier (human-readable)
        sa.Column("test_case_number", sa.String(50), unique=True, nullable=False),
        # Foreign key with cascade delete
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Basic information
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("objective", sa.Text, nullable=True),
        # Lifecycle status
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        # Classification
        sa.Column("test_type", sa.String(50), nullable=False, server_default="functional"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        # Test definition
        sa.Column("preconditions", sa.Text, nullable=True),
        sa.Column("test_steps", postgresql.JSONB, nullable=True),
        sa.Column("expected_result", sa.Text, nullable=True),
        sa.Column("postconditions", sa.Text, nullable=True),
        sa.Column("test_data", postgresql.JSONB, nullable=True),
        # Automation
        sa.Column("automation_status", sa.String(50), nullable=False, server_default="not_automated"),
        sa.Column("automation_script_path", sa.String(500), nullable=True),
        sa.Column("automation_framework", sa.String(100), nullable=True),
        sa.Column("automation_notes", sa.Text, nullable=True),
        # Estimates
        sa.Column("estimated_duration_minutes", sa.Integer, nullable=True),
        # Assignment & Ownership
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("approved_by", sa.String(255), nullable=True),
        # Review & Approval dates
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deprecation_reason", sa.Text, nullable=True),
        # Execution history summary
        sa.Column("last_executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_execution_result", sa.String(50), nullable=True),
        sa.Column("total_executions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("pass_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("fail_count", sa.Integer, nullable=False, server_default="0"),
        # Flexible metadata
        sa.Column("test_case_metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        # Optimistic locking
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        # Soft delete
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for test_cases
    op.create_index("idx_test_cases_test_case_number", "test_cases", ["test_case_number"])
    op.create_index("idx_test_cases_project_id", "test_cases", ["project_id"])
    op.create_index("idx_test_cases_status", "test_cases", ["status"])
    op.create_index("idx_test_cases_project_status", "test_cases", ["project_id", "status"])
    op.create_index("idx_test_cases_project_type", "test_cases", ["project_id", "test_type"])
    op.create_index("idx_test_cases_project_priority", "test_cases", ["project_id", "priority"])
    op.create_index("idx_test_cases_automation_status", "test_cases", ["automation_status"])
    op.create_index("idx_test_cases_assigned_to", "test_cases", ["assigned_to"])
    op.create_index("idx_test_cases_category", "test_cases", ["category"])
    op.create_index("idx_test_cases_deleted_at", "test_cases", ["deleted_at"])

    # Create test_case_activities table
    op.create_table(
        "test_case_activities",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("test_case_id", sa.String(255), sa.ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_type", sa.String(50), nullable=False),
        sa.Column("from_value", sa.String(255), nullable=True),
        sa.Column("to_value", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("performed_by", sa.String(255), nullable=True),
        sa.Column("activity_metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for test_case_activities
    op.create_index("idx_test_case_activities_test_case_id", "test_case_activities", ["test_case_id"])
    op.create_index("idx_test_case_activities_activity_type", "test_case_activities", ["activity_type"])
    op.create_index("idx_test_case_activities_created_at", "test_case_activities", ["created_at"])


def downgrade() -> None:
    """Downgrade."""
    # Drop test_case_activities indexes and table
    op.drop_index("idx_test_case_activities_created_at", table_name="test_case_activities")
    op.drop_index("idx_test_case_activities_activity_type", table_name="test_case_activities")
    op.drop_index("idx_test_case_activities_test_case_id", table_name="test_case_activities")
    op.drop_table("test_case_activities")

    # Drop test_cases indexes and table
    op.drop_index("idx_test_cases_deleted_at", table_name="test_cases")
    op.drop_index("idx_test_cases_category", table_name="test_cases")
    op.drop_index("idx_test_cases_assigned_to", table_name="test_cases")
    op.drop_index("idx_test_cases_automation_status", table_name="test_cases")
    op.drop_index("idx_test_cases_project_priority", table_name="test_cases")
    op.drop_index("idx_test_cases_project_type", table_name="test_cases")
    op.drop_index("idx_test_cases_project_status", table_name="test_cases")
    op.drop_index("idx_test_cases_status", table_name="test_cases")
    op.drop_index("idx_test_cases_project_id", table_name="test_cases")
    op.drop_index("idx_test_cases_test_case_number", table_name="test_cases")
    op.drop_table("test_cases")
