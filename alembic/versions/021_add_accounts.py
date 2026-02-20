"""Add accounts and account_users tables.

Creates account model for workspace/organization support and account-user relationships.

Revision ID: 021_accounts
Revises: 020_specifications
Create Date: 2026-01-28 12:00:00.000000
"""

import logging

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON

from alembic import context, op

_log = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = "021_accounts"
down_revision = "020_specifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Determine JSON type based on database
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind is not None else context.get_context().dialect.name
    json_type = JSON if dialect_name == "postgresql" else SQLITE_JSON

    # Create accounts table
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("account_type", sa.String(50), nullable=False, server_default="personal"),
        sa.Column("metadata", json_type, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_accounts_name", "accounts", ["name"])
    op.create_index("ix_accounts_slug", "accounts", ["slug"])

    # Create account_users table
    op.create_table(
        "account_users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("account_id", "user_id", name="uc_account_user"),
    )
    op.create_index("ix_account_users_user_id", "account_users", ["user_id"])

    # Add account_id to projects table
    op.add_column("projects", sa.Column("account_id", sa.String(36), nullable=True))
    op.create_foreign_key("fk_projects_account_id", "projects", "accounts", ["account_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_projects_account_id", "projects", ["account_id"])

    # Remove unique constraint on projects.name since accounts can have projects with same name
    # First check if constraint exists
    conn = op.get_bind()
    if conn is None or context.is_offline_mode():
        for constraint_name in ("projects_name_key", "uq_projects_name"):
            try:
                op.drop_constraint(constraint_name, "projects", type_="unique")
            except Exception as e:
                _log.debug("drop_constraint %s: %s", constraint_name, e)
    else:
        inspector = sa.inspect(conn)
        unique_constraints = [c["name"] for c in inspector.get_unique_constraints("projects")]
        if "projects_name_key" in unique_constraints or any("name" in str(c) for c in unique_constraints):
            # Try to drop the constraint - exact name may vary
            try:
                op.drop_constraint("projects_name_key", "projects", type_="unique")
            except Exception as e:
                _log.debug("drop_constraint projects_name_key: %s", e)
                try:
                    op.drop_constraint("uq_projects_name", "projects", type_="unique")
                except Exception as e2:
                    _log.debug("drop_constraint uq_projects_name: %s", e2)


def downgrade() -> None:
    """Downgrade."""
    # Remove account_id from projects
    op.drop_index("ix_projects_account_id", table_name="projects")
    op.drop_constraint("fk_projects_account_id", "projects", type_="foreignkey")
    op.drop_column("projects", "account_id")

    # Restore unique constraint on projects.name
    op.create_unique_constraint("projects_name_key", "projects", ["name"])

    # Drop account_users table
    op.drop_table("account_users")

    # Drop accounts table
    op.drop_table("accounts")
