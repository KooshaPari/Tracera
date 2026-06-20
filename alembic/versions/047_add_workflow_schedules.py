"""Add workflow schedules table for Temporal schedule tracking.

Revision ID: 047_add_workflow_schedules
Revises: 046_add_composite_performance_indexes
Create Date: 2026-01-31
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "047_add_workflow_schedules"
down_revision = "046_add_composite_performance_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    op.create_table(
        "workflow_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("workflow_name", sa.String(length=200), nullable=False),
        sa.Column("schedule_id", sa.String(length=255), nullable=False),
        sa.Column("schedule_type", sa.String(length=50), nullable=False, server_default="cron"),
        sa.Column(
            "schedule_spec",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("task_queue", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("created_by_user_id", sa.String(length=255), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workflow_schedules_project", "workflow_schedules", ["project_id", "created_at"], unique=False)
    op.create_index("ix_workflow_schedules_status", "workflow_schedules", ["status"], unique=False)
    op.create_index("ix_workflow_schedules_schedule_id", "workflow_schedules", ["schedule_id"], unique=True)


def downgrade() -> None:
    """Downgrade."""
    op.drop_index("ix_workflow_schedules_schedule_id", table_name="workflow_schedules")
    op.drop_index("ix_workflow_schedules_status", table_name="workflow_schedules")
    op.drop_index("ix_workflow_schedules_project", table_name="workflow_schedules")
    op.drop_table("workflow_schedules")
