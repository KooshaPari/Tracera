"""Add github_projects table for linking TraceRTM projects to GitHub Projects v2.

Revision ID: 023_github_projects
Revises: 022_github_app_installations
Create Date: 2026-01-28 13:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON

from alembic import context, op

# revision identifiers, used by Alembic.
revision = "023_github_projects"
down_revision = "022_github_app_installations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Determine JSON type based on database
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind is not None else context.get_context().dialect.name
    json_type = JSON if dialect_name == "postgresql" else SQLITE_JSON

    # Create github_projects table
    op.create_table(
        "github_projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("github_repo_id", sa.Integer(), nullable=False),
        sa.Column("github_repo_owner", sa.String(255), nullable=False),
        sa.Column("github_repo_name", sa.String(255), nullable=False),
        sa.Column("github_project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_project_number", sa.Integer(), nullable=False),
        sa.Column("auto_sync", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sync_config", json_type, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_github_projects_project", "github_projects", ["project_id"])
    op.create_index("ix_github_projects_repo", "github_projects", ["github_repo_id"])
    op.create_index("ix_github_projects_github_project", "github_projects", ["github_project_id"])


def downgrade() -> None:
    """Downgrade."""
    op.drop_table("github_projects")
