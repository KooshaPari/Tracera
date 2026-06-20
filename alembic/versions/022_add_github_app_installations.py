"""Add GitHub App installations table.

Creates github_app_installations table and updates integration_credentials to support account-level and GitHub App installations.

Revision ID: 022_github_app_installations
Revises: 021_accounts
Create Date: 2026-01-28 12:30:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON

from alembic import context, op

# revision identifiers, used by Alembic.
revision = "022_github_app_installations"
down_revision = "021_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Determine JSON type based on database
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind is not None else context.get_context().dialect.name
    json_type = JSON if dialect_name == "postgresql" else SQLITE_JSON

    # Create github_app_installations table
    op.create_table(
        "github_app_installations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installation_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("account_login", sa.String(255), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("permissions", json_type, nullable=False, server_default="{}"),
        sa.Column("repository_selection", sa.String(50), nullable=False, server_default="all"),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspended_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_github_app_installations_account", "github_app_installations", ["account_id"])
    op.create_index("ix_github_app_installations_installation_id", "github_app_installations", ["installation_id"])

    # Add account_id and github_app_installation_id to integration_credentials
    op.add_column("integration_credentials", sa.Column("account_id", sa.String(36), nullable=True))
    op.add_column("integration_credentials", sa.Column("github_app_installation_id", sa.String(36), nullable=True))

    op.create_foreign_key(
        "fk_integration_credentials_account_id",
        "integration_credentials",
        "accounts",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_integration_credentials_github_app_installation_id",
        "integration_credentials",
        "github_app_installations",
        ["github_app_installation_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_integration_credentials_account_id", "integration_credentials", ["account_id"])
    op.create_index(
        "ix_integration_credentials_github_app_installation_id",
        "integration_credentials",
        ["github_app_installation_id"],
    )

    # Update index to include account_id
    import logging

    log = logging.getLogger(__name__)
    try:
        op.drop_index("ix_integration_credentials_project_provider", table_name="integration_credentials")
    except Exception as e:
        log.debug("drop_index ix_integration_credentials_project_provider: %s", e)
    op.create_index(
        "ix_integration_credentials_account_provider",
        "integration_credentials",
        ["account_id", "provider"],
    )


def downgrade() -> None:
    """Downgrade."""
    # Remove indexes and foreign keys
    op.drop_index("ix_integration_credentials_github_app_installation_id", table_name="integration_credentials")
    op.drop_index("ix_integration_credentials_account_id", table_name="integration_credentials")
    op.drop_constraint(
        "fk_integration_credentials_github_app_installation_id",
        "integration_credentials",
        type_="foreignkey",
    )
    op.drop_constraint("fk_integration_credentials_account_id", "integration_credentials", type_="foreignkey")

    # Remove columns
    op.drop_column("integration_credentials", "github_app_installation_id")
    op.drop_column("integration_credentials", "account_id")

    # Drop github_app_installations table
    op.drop_table("github_app_installations")
