"""Add notification expiration timestamp.

Revision ID: 060_add_notification_expiration
Revises: 311d43aa5450
Create Date: 2026-04-26
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "060_add_notification_expiration"
down_revision = "311d43aa5450"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the expiration timestamp used by the Go notification service."""
    op.execute("""
        ALTER TABLE notifications
        ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_notifications_expires_at
        ON notifications(expires_at)
    """)


def downgrade() -> None:
    """Remove the notification expiration timestamp."""
    op.execute("DROP INDEX IF EXISTS idx_notifications_expires_at")
    op.execute("ALTER TABLE notifications DROP COLUMN IF EXISTS expires_at")
