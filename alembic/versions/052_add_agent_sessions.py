"""Add agent_sessions table for per-session sandbox persistence.

Revision ID: 052_add_agent_sessions
Revises: 051_add_agent_locks_project_id
Create Date: 2026-01-31

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "052_add_agent_sessions"
down_revision: str | None = "051_add_agent_locks_project_id"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    op.create_table(
        "agent_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", sa.String(255), nullable=False),
        sa.Column("sandbox_root", sa.String(1024), nullable=False),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_agent_sessions_session_id", "agent_sessions", ["session_id"], unique=True)
    op.create_index("ix_agent_sessions_project_id", "agent_sessions", ["project_id"], unique=False)


def downgrade() -> None:
    """Downgrade."""
    op.drop_index("ix_agent_sessions_project_id", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_session_id", table_name="agent_sessions")
    op.drop_table("agent_sessions")
