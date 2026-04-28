"""Add notifications table.

Revision ID: 027_add_notifications
Revises: 026_fix_rls_policies
Create Date: 2026-01-29 02:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "029_add_notifications"
down_revision = "028_add_item_specifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("type", sa.String(50), nullable=False, server_default="info"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_project_id", "notifications", ["project_id"])

    # RLS Policies for Notifications
    op.execute("ALTER TABLE notifications ENABLE ROW LEVEL SECURITY")

    # Select: Users can see their own notifications
    op.execute("""
        CREATE POLICY notifications_select_policy ON notifications FOR SELECT
        USING (user_id = current_setting('app.current_user_id', true))
    """)

    # Update: Users can mark their own notifications as read
    op.execute("""
        CREATE POLICY notifications_update_policy ON notifications FOR UPDATE
        USING (user_id = current_setting('app.current_user_id', true))
    """)

    # Delete: Users can delete their own notifications
    op.execute("""
        CREATE POLICY notifications_delete_policy ON notifications FOR DELETE
        USING (user_id = current_setting('app.current_user_id', true))
    """)

    # Insert: System can insert (bypass RLS usually), or users can trigger?
    # Usually notifications are system generated. We'll allow insert if user matches for now (e.g. testing)
    op.execute("""
        CREATE POLICY notifications_insert_policy ON notifications FOR INSERT
        WITH CHECK (user_id = current_setting('app.current_user_id', true))
    """)


def downgrade() -> None:
    """Downgrade."""
    op.drop_table("notifications")
