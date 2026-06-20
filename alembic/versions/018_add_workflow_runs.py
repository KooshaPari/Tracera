"""Add workflow run tracking table.

Revision ID: 018
Revises: 017
Create Date: 2026-01-29 00:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("graph_id", sa.String(255), sa.ForeignKey("graphs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("workflow_name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="queued"),
        sa.Column("external_run_id", sa.String(255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("result", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_workflow_runs_project", "workflow_runs", ["project_id", "created_at"], unique=False)
    op.create_index("ix_workflow_runs_status", "workflow_runs", ["status"], unique=False)
    op.create_index("ix_workflow_runs_external", "workflow_runs", ["external_run_id"], unique=False)


def downgrade() -> None:
    """Downgrade."""
    op.drop_index("ix_workflow_runs_external", table_name="workflow_runs")
    op.drop_index("ix_workflow_runs_status", table_name="workflow_runs")
    op.drop_index("ix_workflow_runs_project", table_name="workflow_runs")
    op.drop_table("workflow_runs")
