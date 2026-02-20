"""Allow global (user-level) integration credentials.

Revision ID: 016
Revises: 015
Create Date: 2026-01-28 00:00:00.000000
"""

from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Allow credentials without a project_id and add user index."""
    with op.batch_alter_table("integration_credentials") as batch:
        batch.alter_column("project_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
        batch.create_index(
            "ix_integration_credentials_created_by_user",
            ["created_by_user_id"],
            unique=False,
        )


def downgrade() -> None:
    """Revert to project-scoped credentials only."""
    with op.batch_alter_table("integration_credentials") as batch:
        batch.drop_index("ix_integration_credentials_created_by_user")
        batch.alter_column("project_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)
