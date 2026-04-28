"""Add API keys and usage tracking tables.

Revision ID: 058_add_api_keys
Revises: 054_add_spatial_gist_index
Create Date: 2026-02-01 18:30:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "058_add_api_keys"
down_revision = "054_add_spatial_gist_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Create API keys table
    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="read-only"),
        sa.Column("scopes", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("last_used_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "created_by_id",
            sa.String(36),
            sa.ForeignKey("accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("revoked_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "revoked_by_id",
            sa.String(36),
            sa.ForeignKey("accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("revoked_reason", sa.Text, nullable=True),
        sa.CheckConstraint("role IN ('read-only', 'read-write', 'admin')", name="api_keys_role_check"),
    )

    # Create indexes for API keys
    op.create_index("idx_api_keys_account_id", "api_keys", ["account_id"])
    op.create_index("idx_api_keys_project_id", "api_keys", ["project_id"])
    op.create_index("idx_api_keys_is_active", "api_keys", ["is_active"])
    op.create_index("idx_api_keys_expires_at", "api_keys", ["expires_at"])

    # Create API key usage tracking table
    op.create_table(
        "api_key_usage",
        sa.Column("api_key_id", UUID(as_uuid=True), sa.ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("request_count", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("error_count", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("bytes_transferred", sa.BigInteger, nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("api_key_id", "date", name="api_key_usage_pkey"),
    )

    # Create indexes for usage tracking
    op.create_index("idx_api_key_usage_date", "api_key_usage", ["date"])
    op.create_index("idx_api_key_usage_request_count", "api_key_usage", ["request_count"])

    # Add comments for documentation
    op.execute("""
        COMMENT ON TABLE api_keys IS 'API keys for programmatic access with RBAC';
        COMMENT ON COLUMN api_keys.key_hash IS 'Argon2id hash of the API key';
        COMMENT ON COLUMN api_keys.role IS 'Permission level: read-only, read-write, or admin';
        COMMENT ON COLUMN api_keys.scopes IS 'Array of scope strings for fine-grained permissions';
        COMMENT ON COLUMN api_keys.last_used_at IS 'Timestamp of last API key usage';
        COMMENT ON COLUMN api_keys.expires_at IS 'Optional expiration timestamp';
        COMMENT ON COLUMN api_keys.is_active IS 'Whether the key is currently active';
        COMMENT ON COLUMN api_keys.revoked_at IS 'Timestamp when key was revoked';
        COMMENT ON COLUMN api_keys.revoked_by_id IS 'Account ID of user who revoked the key';
        COMMENT ON COLUMN api_keys.revoked_reason IS 'Reason for key revocation';

        COMMENT ON TABLE api_key_usage IS 'Daily usage metrics for API keys';
        COMMENT ON COLUMN api_key_usage.request_count IS 'Total requests made with this key on this date';
        COMMENT ON COLUMN api_key_usage.error_count IS 'Number of failed requests on this date';
        COMMENT ON COLUMN api_key_usage.bytes_transferred IS 'Total bytes transferred on this date';
    """)


def downgrade() -> None:
    """Downgrade."""
    # Drop tables in reverse order
    op.drop_table("api_key_usage")
    op.drop_table("api_keys")
