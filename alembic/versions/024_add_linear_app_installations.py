"""Add linear_app_installations table for account-level Linear integrations.

Revision ID: 024_linear_app_installations
Revises: 023_github_projects
Create Date: 2026-01-28 13:30:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON

from alembic import context, op

# revision identifiers, used by Alembic.
revision = "024_linear_app_installations"
down_revision = "023_github_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Determine JSON type based on database
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind is not None else context.get_context().dialect.name
    json_type = JSON if dialect_name == "postgresql" else SQLITE_JSON

    # Create linear_app_installations table
    op.create_table(
        "linear_app_installations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("workspace_id", sa.String(255), nullable=False, unique=True),
        sa.Column("workspace_name", sa.String(255), nullable=False),
        sa.Column(
            "integration_credential_id",
            sa.String(36),
            sa.ForeignKey("integration_credentials.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("scopes", json_type, nullable=False, server_default="[]"),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspended_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_linear_app_installations_account", "linear_app_installations", ["account_id"])
    op.create_index("ix_linear_app_installations_workspace_id", "linear_app_installations", ["workspace_id"])

    # Add linear_app_installation_id to integration_credentials
    op.add_column("integration_credentials", sa.Column("linear_app_installation_id", sa.String(36), nullable=True))
    op.create_foreign_key(
        "fk_integration_credentials_linear_app_installation_id",
        "integration_credentials",
        "linear_app_installations",
        ["linear_app_installation_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_integration_credentials_linear_app_installation_id",
        "integration_credentials",
        ["linear_app_installation_id"],
    )


def downgrade() -> None:
    """Downgrade."""
    # Remove linear_app_installation_id from integration_credentials
    op.drop_index("ix_integration_credentials_linear_app_installation_id", table_name="integration_credentials")
    op.drop_constraint(
        "fk_integration_credentials_linear_app_installation_id",
        "integration_credentials",
        type_="foreignkey",
    )
    op.drop_column("integration_credentials", "linear_app_installation_id")

    # Drop linear_app_installations table
    op.drop_table("linear_app_installations")
