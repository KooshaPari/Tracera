"""Add step_definitions table for BDD step implementation.

This migration adds the step_definitions table to support BDD test automation
and links Gherkin steps to their implementation code.

Revision ID: 027_add_step_definitions
Revises: 026_fix_rls_policies
Create Date: 2026-01-29 02:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.sqlite import JSON

from alembic import op

# revision identifiers, used by Alembic.
revision = "027_add_step_definitions"
down_revision = "026_fix_rls_policies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add step_definitions table with all required columns."""
    # Step Definitions table for BDD automation
    op.create_table(
        "step_definitions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_number", sa.String(50), nullable=False),
        sa.Column("step_type", sa.String(50), nullable=False),  # given, when, then, and
        sa.Column("pattern", sa.String(500), nullable=False),  # Regex pattern to match steps
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "implementation_language",
            sa.String(50),
            nullable=False,
            server_default="python",
        ),  # python, javascript, etc.
        sa.Column("implementation_code", sa.Text(), nullable=False),  # The actual step code
        sa.Column("file_path", sa.String(500), nullable=True),  # Path to implementation file
        sa.Column("line_number", sa.Integer(), nullable=True),  # Line where implementation starts
        sa.Column("parameters", JSON(), nullable=True),  # Expected parameters: [{name, type, required}]
        sa.Column("return_type", sa.String(100), nullable=True),  # Expected return type
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),  # active, deprecated, draft
        sa.Column("tags", JSON(), nullable=True),  # Tags for filtering/organization
        sa.Column("related_scenarios", JSON(), nullable=True),  # Scenario IDs using this step
        sa.Column("execution_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("success_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failure_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=True),  # Average execution time
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("metadata", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Indexes on foreign keys and frequently queried fields
    op.create_index("idx_step_definitions_project", "step_definitions", ["project_id"])
    op.create_index("idx_step_definitions_step_type", "step_definitions", ["step_type"])
    op.create_index("idx_step_definitions_status", "step_definitions", ["status"])
    op.create_index("idx_step_definitions_language", "step_definitions", ["implementation_language"])
    op.create_index("idx_step_definitions_project_status", "step_definitions", ["project_id", "status"])
    op.create_index("idx_step_definitions_pattern", "step_definitions", ["pattern"])


def downgrade() -> None:
    """Remove step_definitions table and indexes."""
    op.drop_index("idx_step_definitions_pattern", table_name="step_definitions")
    op.drop_index("idx_step_definitions_project_status", table_name="step_definitions")
    op.drop_index("idx_step_definitions_language", table_name="step_definitions")
    op.drop_index("idx_step_definitions_status", table_name="step_definitions")
    op.drop_index("idx_step_definitions_step_type", table_name="step_definitions")
    op.drop_index("idx_step_definitions_project", table_name="step_definitions")
    op.drop_table("step_definitions")
