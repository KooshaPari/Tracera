"""Add problems, processes, problem_activities, and process_executions tables.

Revision ID: 007_add_problems_and_processes
Revises: 006_add_priority_owner
Create Date: 2026-01-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007_add_problems_and_processes"
down_revision: str | None = "006_add_priority_owner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    # Create problems table
    op.create_table(
        "problems",
        # Core Identification
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("problem_number", sa.String(50), unique=True, nullable=False),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Lifecycle Status
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("resolution_type", sa.String(50), nullable=True),
        # Classification
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("sub_category", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        # Impact Assessment
        sa.Column("impact_level", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("urgency", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("affected_systems", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("affected_users_estimated", sa.Integer, nullable=True),
        sa.Column("business_impact_description", sa.Text, nullable=True),
        # Root Cause Analysis
        sa.Column("rca_performed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("rca_method", sa.String(50), nullable=True),
        sa.Column("rca_notes", sa.Text, nullable=True),
        sa.Column("rca_data", postgresql.JSONB, nullable=True),
        sa.Column("root_cause_identified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("root_cause_description", sa.Text, nullable=True),
        sa.Column("root_cause_category", sa.String(50), nullable=True),
        sa.Column("root_cause_confidence", sa.String(20), nullable=True),
        sa.Column("rca_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rca_completed_by", sa.String(255), nullable=True),
        # Solutions & Workarounds
        sa.Column("workaround_available", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("workaround_description", sa.Text, nullable=True),
        sa.Column("workaround_effectiveness", sa.String(50), nullable=True),
        sa.Column("permanent_fix_available", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("permanent_fix_description", sa.Text, nullable=True),
        sa.Column("permanent_fix_implemented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("permanent_fix_change_id", sa.String(255), nullable=True),
        # Known Error Integration
        sa.Column("known_error_id", sa.String(255), nullable=True),
        sa.Column("knowledge_article_id", sa.String(255), nullable=True),
        # Assignment & Ownership
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("assigned_team", sa.String(255), nullable=True),
        sa.Column("owner", sa.String(255), nullable=True),
        # Closure
        sa.Column("closed_by", sa.String(255), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closure_notes", sa.Text, nullable=True),
        # Target dates
        sa.Column("target_resolution_date", sa.DateTime(timezone=True), nullable=True),
        # Metadata
        sa.Column("problem_metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        # Optimistic locking
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        # Soft delete
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Timestamps from mixin
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for problems
    op.create_index("idx_problems_problem_number", "problems", ["problem_number"])
    op.create_index("idx_problems_project_id", "problems", ["project_id"])
    op.create_index("idx_problems_status", "problems", ["status"])
    op.create_index("idx_problems_project_status", "problems", ["project_id", "status"])
    op.create_index("idx_problems_project_priority", "problems", ["project_id", "priority"])
    op.create_index("idx_problems_project_impact", "problems", ["project_id", "impact_level"])
    op.create_index("idx_problems_assigned_to", "problems", ["assigned_to"])
    op.create_index("idx_problems_category", "problems", ["category"])
    op.create_index("idx_problems_known_error_id", "problems", ["known_error_id"])
    op.create_index("idx_problems_deleted_at", "problems", ["deleted_at"])

    # Create problem_activities table
    op.create_table(
        "problem_activities",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("problem_id", sa.String(255), sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_type", sa.String(50), nullable=False),
        sa.Column("from_value", sa.String(255), nullable=True),
        sa.Column("to_value", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("performed_by", sa.String(255), nullable=True),
        sa.Column("activity_metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        # Timestamps from mixin
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for problem_activities
    op.create_index("idx_problem_activities_problem_id", "problem_activities", ["problem_id"])

    # Create processes table
    op.create_table(
        "processes",
        # Core Identification
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("process_number", sa.String(50), unique=True, nullable=False),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("purpose", sa.Text, nullable=True),
        # Lifecycle Status
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        # Classification
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        # Versioning
        sa.Column("version_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_active_version", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "parent_version_id",
            sa.String(255),
            sa.ForeignKey("processes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("version_notes", sa.Text, nullable=True),
        # Process Definition
        sa.Column("stages", postgresql.JSONB, nullable=True),
        sa.Column("swimlanes", postgresql.JSONB, nullable=True),
        # BPMN Support
        sa.Column("bpmn_xml", sa.Text, nullable=True),
        sa.Column("bpmn_diagram_url", sa.String(500), nullable=True),
        # Inputs/Outputs
        sa.Column("inputs", postgresql.JSONB, nullable=True),
        sa.Column("outputs", postgresql.JSONB, nullable=True),
        # Triggers and Conditions
        sa.Column("triggers", postgresql.JSONB, nullable=True),
        sa.Column("exit_criteria", postgresql.ARRAY(sa.String), nullable=True),
        # Ownership
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("responsible_team", sa.String(255), nullable=True),
        # Metrics
        sa.Column("expected_duration_hours", sa.Integer, nullable=True),
        sa.Column("sla_hours", sa.Integer, nullable=True),
        # Activation/Deactivation
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_by", sa.String(255), nullable=True),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deprecated_by", sa.String(255), nullable=True),
        sa.Column("deprecation_reason", sa.Text, nullable=True),
        # Related entities
        sa.Column("related_process_ids", postgresql.ARRAY(sa.String), nullable=True),
        # Metadata
        sa.Column("process_metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        # Optimistic locking
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        # Soft delete
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Timestamps from mixin
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for processes
    op.create_index("idx_processes_process_number", "processes", ["process_number"])
    op.create_index("idx_processes_project_id", "processes", ["project_id"])
    op.create_index("idx_processes_status", "processes", ["status"])
    op.create_index("idx_processes_project_status", "processes", ["project_id", "status"])
    op.create_index("idx_processes_project_category", "processes", ["project_id", "category"])
    op.create_index("idx_processes_is_active", "processes", ["is_active_version"])
    op.create_index("idx_processes_owner", "processes", ["owner"])
    op.create_index("idx_processes_category", "processes", ["category"])
    op.create_index("idx_processes_deleted_at", "processes", ["deleted_at"])

    # Create process_executions table
    op.create_table(
        "process_executions",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("process_id", sa.String(255), sa.ForeignKey("processes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("execution_number", sa.String(50), unique=True, nullable=False),
        # Status
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        # Progress
        sa.Column("current_stage_id", sa.String(255), nullable=True),
        sa.Column("completed_stages", postgresql.ARRAY(sa.String), nullable=True),
        # Timing
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        # Actors
        sa.Column("initiated_by", sa.String(255), nullable=True),
        sa.Column("completed_by", sa.String(255), nullable=True),
        # Context
        sa.Column("trigger_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("context_data", postgresql.JSONB, nullable=False, server_default="{}"),
        # Output
        sa.Column("result_summary", sa.Text, nullable=True),
        sa.Column("output_item_ids", postgresql.ARRAY(sa.String), nullable=True),
        # Timestamps from mixin
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for process_executions
    op.create_index("idx_process_executions_process_id", "process_executions", ["process_id"])
    op.create_index("idx_process_executions_status", "process_executions", ["status"])
    op.create_index("idx_process_executions_execution_number", "process_executions", ["execution_number"])


def downgrade() -> None:
    """Downgrade."""
    # Drop process_executions
    op.drop_index("idx_process_executions_execution_number", table_name="process_executions")
    op.drop_index("idx_process_executions_status", table_name="process_executions")
    op.drop_index("idx_process_executions_process_id", table_name="process_executions")
    op.drop_table("process_executions")

    # Drop processes
    op.drop_index("idx_processes_deleted_at", table_name="processes")
    op.drop_index("idx_processes_category", table_name="processes")
    op.drop_index("idx_processes_owner", table_name="processes")
    op.drop_index("idx_processes_is_active", table_name="processes")
    op.drop_index("idx_processes_project_category", table_name="processes")
    op.drop_index("idx_processes_project_status", table_name="processes")
    op.drop_index("idx_processes_status", table_name="processes")
    op.drop_index("idx_processes_project_id", table_name="processes")
    op.drop_index("idx_processes_process_number", table_name="processes")
    op.drop_table("processes")

    # Drop problem_activities
    op.drop_index("idx_problem_activities_problem_id", table_name="problem_activities")
    op.drop_table("problem_activities")

    # Drop problems
    op.drop_index("idx_problems_deleted_at", table_name="problems")
    op.drop_index("idx_problems_known_error_id", table_name="problems")
    op.drop_index("idx_problems_category", table_name="problems")
    op.drop_index("idx_problems_assigned_to", table_name="problems")
    op.drop_index("idx_problems_project_impact", table_name="problems")
    op.drop_index("idx_problems_project_priority", table_name="problems")
    op.drop_index("idx_problems_project_status", table_name="problems")
    op.drop_index("idx_problems_status", table_name="problems")
    op.drop_index("idx_problems_project_id", table_name="problems")
    op.drop_index("idx_problems_problem_number", table_name="problems")
    op.drop_table("problems")
