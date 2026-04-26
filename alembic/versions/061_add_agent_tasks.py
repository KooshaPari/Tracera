"""Add agent task persistence table.

Revision ID: 061_add_agent_tasks
Revises: 060_add_notification_expiration
Create Date: 2026-04-26
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "061_add_agent_tasks"
down_revision = "060_add_notification_expiration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the durable task queue table used by the Go agent runtime."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS agent_tasks (
            id VARCHAR(255) PRIMARY KEY,
            project_id VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            priority INTEGER NOT NULL DEFAULT 1,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_agent_tasks_project_id ON agent_tasks(project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_agent_tasks_priority ON agent_tasks(priority)")
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_tasks_project_status
        ON agent_tasks(project_id, status)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_tasks_project_priority
        ON agent_tasks(project_id, priority)
    """)


def downgrade() -> None:
    """Drop the durable task queue table."""
    op.execute("DROP TABLE IF EXISTS agent_tasks")
