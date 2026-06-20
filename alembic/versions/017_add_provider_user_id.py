"""Add provider_user_id to integration credentials.

Revision ID: 017
Revises: 016
Create Date: 2026-01-28 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add provider_user_id column."""
    with op.batch_alter_table("integration_credentials") as batch:
        batch.add_column(sa.Column("provider_user_id", sa.String(255), nullable=True))
        batch.create_index(
            "ix_integration_credentials_provider_user",
            ["provider_user_id"],
            unique=False,
        )


def downgrade() -> None:
    """Drop provider_user_id column."""
    with op.batch_alter_table("integration_credentials") as batch:
        batch.drop_index("ix_integration_credentials_provider_user")
        batch.drop_column("provider_user_id")
