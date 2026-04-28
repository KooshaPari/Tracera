"""Add test suites and test runs for Phase 2 QE.

Revision ID: 009_add_test_suites_runs
Revises: 008_add_test_cases
Create Date: 2026-01-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009_add_test_suites_runs"
down_revision: str | None = "008_add_test_cases"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    # Create test_suites table
    op.create_table(
        "test_suites",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("suite_number", sa.String(50), nullable=False, unique=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Basic info
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("objective", sa.Text, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.Enum("draft", "active", "deprecated", "archived", name="test_suite_status"),
            nullable=False,
            default="draft",
        ),
        # Hierarchy
        sa.Column(
            "parent_id",
            sa.String(36),
            sa.ForeignKey("test_suites.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("order_index", sa.Integer, nullable=False, default=0),
        # Categorization
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        # Execution settings
        sa.Column("is_parallel_execution", sa.Boolean, nullable=False, default=False),
        sa.Column("estimated_duration_minutes", sa.Integer, nullable=True),
        # Environment requirements
        sa.Column("required_environment", sa.String(255), nullable=True),
        sa.Column("environment_variables", sa.JSON, nullable=True),
        sa.Column("setup_instructions", sa.Text, nullable=True),
        sa.Column("teardown_instructions", sa.Text, nullable=True),
        # Ownership
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("responsible_team", sa.String(255), nullable=True),
        # Metrics
        sa.Column("total_test_cases", sa.Integer, nullable=False, default=0),
        sa.Column("automated_count", sa.Integer, nullable=False, default=0),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_result", sa.String(50), nullable=True),
        sa.Column("pass_rate", sa.Float, nullable=True),
        # Metadata
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, default=1),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create test_suite_test_cases junction table
    op.create_table(
        "test_suite_test_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "suite_id",
            sa.String(36),
            sa.ForeignKey("test_suites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_case_id",
            sa.String(255),
            sa.ForeignKey("test_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("order_index", sa.Integer, nullable=False, default=0),
        sa.Column("is_mandatory", sa.Boolean, nullable=False, default=True),
        sa.Column("skip_reason", sa.Text, nullable=True),
        sa.Column("custom_parameters", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create test_suite_activities table
    op.create_table(
        "test_suite_activities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "suite_id",
            sa.String(36),
            sa.ForeignKey("test_suites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("activity_type", sa.String(100), nullable=False),
        sa.Column("from_value", sa.Text, nullable=True),
        sa.Column("to_value", sa.Text, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("performed_by", sa.String(255), nullable=True),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create test_runs table
    op.create_table(
        "test_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_number", sa.String(50), nullable=False, unique=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "suite_id",
            sa.String(36),
            sa.ForeignKey("test_suites.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Basic info
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Status & type
        sa.Column(
            "status",
            sa.Enum("pending", "running", "passed", "failed", "blocked", "cancelled", name="test_run_status"),
            nullable=False,
            default="pending",
        ),
        sa.Column(
            "run_type",
            sa.Enum("manual", "automated", "ci_cd", "scheduled", name="test_run_type"),
            nullable=False,
            default="manual",
        ),
        # Environment
        sa.Column("environment", sa.String(255), nullable=True),
        sa.Column("build_number", sa.String(255), nullable=True),
        sa.Column("build_url", sa.String(1000), nullable=True),
        sa.Column("branch", sa.String(255), nullable=True),
        sa.Column("commit_sha", sa.String(64), nullable=True),
        # Timing
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        # Personnel
        sa.Column("initiated_by", sa.String(255), nullable=True),
        sa.Column("executed_by", sa.String(255), nullable=True),
        # Metrics summary
        sa.Column("total_tests", sa.Integer, nullable=False, default=0),
        sa.Column("passed_count", sa.Integer, nullable=False, default=0),
        sa.Column("failed_count", sa.Integer, nullable=False, default=0),
        sa.Column("skipped_count", sa.Integer, nullable=False, default=0),
        sa.Column("blocked_count", sa.Integer, nullable=False, default=0),
        sa.Column("error_count", sa.Integer, nullable=False, default=0),
        sa.Column("pass_rate", sa.Float, nullable=True),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("failure_summary", sa.Text, nullable=True),
        # Categorization
        sa.Column("tags", sa.JSON, nullable=True),
        # CI/CD integration
        sa.Column("external_run_id", sa.String(255), nullable=True),
        sa.Column("webhook_id", sa.String(36), nullable=True),
        # Metadata
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, default=1),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create test_results table
    op.create_table(
        "test_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(36),
            sa.ForeignKey("test_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_case_id",
            sa.String(255),
            sa.ForeignKey("test_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Result
        sa.Column(
            "status",
            sa.Enum("passed", "failed", "skipped", "blocked", "error", name="test_result_status"),
            nullable=False,
        ),
        # Timing
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        # Personnel
        sa.Column("executed_by", sa.String(255), nullable=True),
        # Details
        sa.Column("actual_result", sa.Text, nullable=True),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("stack_trace", sa.Text, nullable=True),
        # Evidence
        sa.Column("screenshots", sa.JSON, nullable=True),
        sa.Column("logs_url", sa.String(1000), nullable=True),
        sa.Column("attachments", sa.JSON, nullable=True),
        # Step-level results
        sa.Column("step_results", sa.JSON, nullable=True),
        # Defect tracking
        sa.Column("linked_defect_ids", sa.JSON, nullable=True),
        sa.Column("created_defect_id", sa.String(36), nullable=True),
        # Retry information
        sa.Column("retry_count", sa.Integer, nullable=False, default=0),
        sa.Column("is_flaky", sa.Boolean, nullable=False, default=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Metadata
        sa.Column("metadata", sa.JSON, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create test_run_activities table
    op.create_table(
        "test_run_activities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(36),
            sa.ForeignKey("test_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("activity_type", sa.String(100), nullable=False),
        sa.Column("from_value", sa.Text, nullable=True),
        sa.Column("to_value", sa.Text, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("performed_by", sa.String(255), nullable=True),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create indexes for test_suites
    op.create_index("ix_test_suites_project_id", "test_suites", ["project_id"])
    op.create_index("ix_test_suites_parent_id", "test_suites", ["parent_id"])
    op.create_index("ix_test_suites_status", "test_suites", ["status"])
    op.create_index("ix_test_suites_category", "test_suites", ["category"])
    op.create_index("ix_test_suites_owner", "test_suites", ["owner"])
    op.create_index("ix_test_suites_created_at", "test_suites", ["created_at"])

    # Create indexes for test_suite_test_cases
    op.create_index("ix_test_suite_test_cases_suite_id", "test_suite_test_cases", ["suite_id"])
    op.create_index("ix_test_suite_test_cases_test_case_id", "test_suite_test_cases", ["test_case_id"])
    op.create_index("ix_test_suite_test_cases_order", "test_suite_test_cases", ["suite_id", "order_index"])

    # Create indexes for test_suite_activities
    op.create_index("ix_test_suite_activities_suite_id", "test_suite_activities", ["suite_id"])
    op.create_index("ix_test_suite_activities_created_at", "test_suite_activities", ["created_at"])
    op.create_index("ix_test_suite_activities_type", "test_suite_activities", ["activity_type"])

    # Create indexes for test_runs
    op.create_index("ix_test_runs_project_id", "test_runs", ["project_id"])
    op.create_index("ix_test_runs_suite_id", "test_runs", ["suite_id"])
    op.create_index("ix_test_runs_status", "test_runs", ["status"])
    op.create_index("ix_test_runs_run_type", "test_runs", ["run_type"])
    op.create_index("ix_test_runs_started_at", "test_runs", ["started_at"])
    op.create_index("ix_test_runs_completed_at", "test_runs", ["completed_at"])
    op.create_index("ix_test_runs_environment", "test_runs", ["environment"])
    op.create_index("ix_test_runs_initiated_by", "test_runs", ["initiated_by"])
    op.create_index("ix_test_runs_external_run_id", "test_runs", ["external_run_id"])

    # Create indexes for test_results
    op.create_index("ix_test_results_run_id", "test_results", ["run_id"])
    op.create_index("ix_test_results_test_case_id", "test_results", ["test_case_id"])
    op.create_index("ix_test_results_status", "test_results", ["status"])
    op.create_index("ix_test_results_started_at", "test_results", ["started_at"])
    op.create_index("ix_test_results_executed_by", "test_results", ["executed_by"])
    op.create_index("ix_test_results_is_flaky", "test_results", ["is_flaky"])

    # Create indexes for test_run_activities
    op.create_index("ix_test_run_activities_run_id", "test_run_activities", ["run_id"])
    op.create_index("ix_test_run_activities_created_at", "test_run_activities", ["created_at"])
    op.create_index("ix_test_run_activities_type", "test_run_activities", ["activity_type"])


def downgrade() -> None:
    """Downgrade."""
    # Drop indexes
    op.drop_index("ix_test_run_activities_type", table_name="test_run_activities")
    op.drop_index("ix_test_run_activities_created_at", table_name="test_run_activities")
    op.drop_index("ix_test_run_activities_run_id", table_name="test_run_activities")

    op.drop_index("ix_test_results_is_flaky", table_name="test_results")
    op.drop_index("ix_test_results_executed_by", table_name="test_results")
    op.drop_index("ix_test_results_started_at", table_name="test_results")
    op.drop_index("ix_test_results_status", table_name="test_results")
    op.drop_index("ix_test_results_test_case_id", table_name="test_results")
    op.drop_index("ix_test_results_run_id", table_name="test_results")

    op.drop_index("ix_test_runs_external_run_id", table_name="test_runs")
    op.drop_index("ix_test_runs_initiated_by", table_name="test_runs")
    op.drop_index("ix_test_runs_environment", table_name="test_runs")
    op.drop_index("ix_test_runs_completed_at", table_name="test_runs")
    op.drop_index("ix_test_runs_started_at", table_name="test_runs")
    op.drop_index("ix_test_runs_run_type", table_name="test_runs")
    op.drop_index("ix_test_runs_status", table_name="test_runs")
    op.drop_index("ix_test_runs_suite_id", table_name="test_runs")
    op.drop_index("ix_test_runs_project_id", table_name="test_runs")

    op.drop_index("ix_test_suite_activities_type", table_name="test_suite_activities")
    op.drop_index("ix_test_suite_activities_created_at", table_name="test_suite_activities")
    op.drop_index("ix_test_suite_activities_suite_id", table_name="test_suite_activities")

    op.drop_index("ix_test_suite_test_cases_order", table_name="test_suite_test_cases")
    op.drop_index("ix_test_suite_test_cases_test_case_id", table_name="test_suite_test_cases")
    op.drop_index("ix_test_suite_test_cases_suite_id", table_name="test_suite_test_cases")

    op.drop_index("ix_test_suites_created_at", table_name="test_suites")
    op.drop_index("ix_test_suites_owner", table_name="test_suites")
    op.drop_index("ix_test_suites_category", table_name="test_suites")
    op.drop_index("ix_test_suites_status", table_name="test_suites")
    op.drop_index("ix_test_suites_parent_id", table_name="test_suites")
    op.drop_index("ix_test_suites_project_id", table_name="test_suites")

    # Drop tables
    op.drop_table("test_run_activities")
    op.drop_table("test_results")
    op.drop_table("test_runs")
    op.drop_table("test_suite_activities")
    op.drop_table("test_suite_test_cases")
    op.drop_table("test_suites")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS test_result_status")
    op.execute("DROP TYPE IF EXISTS test_run_type")
    op.execute("DROP TYPE IF EXISTS test_run_status")
    op.execute("DROP TYPE IF EXISTS test_suite_status")
