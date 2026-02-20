"""Add project_id to agent_locks when missing (legacy schema fix).

agent_locks may have been created without project_id. This revision adds the column
if missing, backfills from items, and creates the index.

Revision ID: 051_add_agent_locks_project_id
Revises: 050_add_processes_if_not_exists
Create Date: 2026-01-31

"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

revision: str = "051_add_agent_locks_project_id"
down_revision: str | None = "050_add_processes_if_not_exists"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    conn = op.get_bind()
    if conn.dialect.name != "postgresql":
        return

    # Check if agent_locks.project_id exists (any schema)
    r = conn.execute(
        text(
            """
            SELECT table_schema FROM information_schema.columns
            WHERE table_name = 'agent_locks' AND column_name = 'project_id'
            LIMIT 1
            """,
        ),
    ).fetchone()
    if r is not None:
        schema = r[0]
        qual = f'"{schema}".agent_locks' if schema != "public" else "agent_locks"
        op.execute(f"CREATE INDEX IF NOT EXISTS idx_locks_project_item ON {qual} (project_id, item_id)")
        return

    # Find schema of agent_locks
    r2 = conn.execute(
        text("SELECT table_schema FROM information_schema.tables WHERE table_name = 'agent_locks' LIMIT 1"),
    ).fetchone()
    if r2 is None:
        return
    schema = r2[0]
    qual = f'"{schema}".agent_locks' if schema != "public" else "agent_locks"
    proj_ref = f'"{schema}".projects(id)' if schema != "public" else "projects(id)"
    items_qual = f'"{schema}".items' if schema != "public" else "items"

    op.execute(f"ALTER TABLE {qual} ADD COLUMN IF NOT EXISTS project_id UUID REFERENCES {proj_ref} ON DELETE CASCADE")
    op.execute(
        f"UPDATE {qual} SET project_id = (SELECT project_id FROM {items_qual} WHERE id = {qual}.item_id::uuid) WHERE project_id IS NULL",
    )
    # Only set NOT NULL if no nulls remain (orphan locks may have no matching item)
    null_count = conn.execute(text(f"SELECT COUNT(*) FROM {qual} WHERE project_id IS NULL")).scalar()
    if null_count == 0:
        op.execute(f"ALTER TABLE {qual} ALTER COLUMN project_id SET NOT NULL")
    op.execute(f"CREATE INDEX IF NOT EXISTS idx_locks_project_item ON {qual} (project_id, item_id)")


def downgrade() -> None:
    """Downgrade."""
