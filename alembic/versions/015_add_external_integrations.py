"""Add external integrations tables.

Revision ID: 015
Revises: 014
Create Date: 2026-01-27 12:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "015"
down_revision = "014_add_webhooks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add external integrations tables."""
    # integration_credentials
    op.create_table(
        "integration_credentials",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("credential_type", sa.String(50), nullable=False),
        sa.Column("encrypted_token", sa.String(1024), nullable=False),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refresh_token", sa.String(512), nullable=True),
        sa.Column("scopes", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validation_error", sa.String(1000), nullable=True),
        sa.Column("provider_metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_by_user_id", sa.String(36), nullable=True),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rotation_required_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_integration_credentials_project_provider",
        "integration_credentials",
        ["project_id", "provider"],
    )
    op.create_index(
        "ix_integration_credentials_status",
        "integration_credentials",
        ["status"],
    )
    op.create_index(
        "ix_integration_credentials_expires",
        "integration_credentials",
        ["token_expires_at"],
    )

    # integration_mappings
    op.create_table(
        "integration_mappings",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("integration_credential_id", sa.String(36), nullable=False),
        sa.Column("tracertm_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracertm_item_type", sa.String(50), nullable=False),
        sa.Column("external_system", sa.String(100), nullable=False),
        sa.Column("external_id", sa.String(500), nullable=False),
        sa.Column("external_url", sa.String(2000), nullable=False),
        sa.Column("mapping_metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("direction", sa.String(50), nullable=False, server_default="bidirectional"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("auto_sync", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_direction", sa.String(50), nullable=True),
        sa.Column("sync_error_message", sa.String(1000), nullable=True),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_conflict_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "conflict_resolution_strategy",
            sa.String(50),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("field_resolution_rules", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["integration_credential_id"],
            ["integration_credentials.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["tracertm_item_id"], ["items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "uc_mapping_external",
        "integration_mappings",
        ["project_id", "external_id"],
    )
    op.create_index(
        "ix_integration_mappings_credential",
        "integration_mappings",
        ["integration_credential_id"],
    )
    op.create_index(
        "ix_integration_mappings_item",
        "integration_mappings",
        ["tracertm_item_id"],
    )
    op.create_index(
        "ix_integration_mappings_external_id",
        "integration_mappings",
        ["external_id"],
    )
    op.create_index(
        "ix_integration_mappings_status",
        "integration_mappings",
        ["status"],
    )
    op.create_index(
        "ix_integration_mappings_last_sync",
        "integration_mappings",
        ["last_sync_at"],
    )

    # integration_sync_queue
    op.create_table(
        "integration_sync_queue",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("integration_credential_id", sa.String(36), nullable=False),
        sa.Column("mapping_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("direction", sa.String(50), nullable=False),
        sa.Column("priority", sa.String(50), nullable=False, server_default="normal"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(2000), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.ForeignKeyConstraint(
            ["integration_credential_id"],
            ["integration_credentials.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["mapping_id"],
            ["integration_mappings.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "uc_idempotency",
        "integration_sync_queue",
        ["mapping_id", "idempotency_key"],
    )
    op.create_index(
        "ix_sync_queue_credential_status",
        "integration_sync_queue",
        ["integration_credential_id", "status"],
    )
    op.create_index(
        "ix_sync_queue_mapping",
        "integration_sync_queue",
        ["mapping_id"],
    )
    op.create_index(
        "ix_sync_queue_priority_status",
        "integration_sync_queue",
        ["priority", "status"],
    )
    op.create_index(
        "ix_sync_queue_retry",
        "integration_sync_queue",
        ["status", "next_retry_at"],
    )
    op.create_index(
        "ix_sync_queue_created",
        "integration_sync_queue",
        ["created_at"],
    )

    # integration_sync_logs
    op.create_table(
        "integration_sync_logs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("sync_queue_id", sa.String(36), nullable=True),
        sa.Column("mapping_id", sa.String(36), nullable=False),
        sa.Column("operation", sa.String(50), nullable=False),
        sa.Column("direction", sa.String(50), nullable=False),
        sa.Column("source_system", sa.String(100), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=False),
        sa.Column("target_system", sa.String(100), nullable=False),
        sa.Column("target_id", sa.String(255), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_message", sa.String(2000), nullable=True),
        sa.Column("sync_metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.ForeignKeyConstraint(
            ["sync_queue_id"],
            ["integration_sync_queue.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["mapping_id"],
            ["integration_mappings.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_sync_log_mapping",
        "integration_sync_logs",
        ["mapping_id"],
    )
    op.create_index(
        "ix_sync_log_queue",
        "integration_sync_logs",
        ["sync_queue_id"],
    )
    op.create_index(
        "ix_sync_log_success",
        "integration_sync_logs",
        ["success"],
    )
    op.create_index(
        "ix_sync_log_created",
        "integration_sync_logs",
        ["created_at"],
    )
    op.create_index(
        "ix_sync_log_operation",
        "integration_sync_logs",
        ["operation"],
    )

    # integration_conflicts
    op.create_table(
        "integration_conflicts",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("mapping_id", sa.String(36), nullable=False),
        sa.Column("field", sa.String(100), nullable=False),
        sa.Column("tracertm_value", sa.Text(), nullable=True),
        sa.Column("external_value", sa.Text(), nullable=True),
        sa.Column("resolution_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("resolved_value", sa.Text(), nullable=True),
        sa.Column("resolution_strategy_used", sa.String(50), nullable=True),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["mapping_id"],
            ["integration_mappings.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_integration_conflicts_mapping",
        "integration_conflicts",
        ["mapping_id"],
    )
    op.create_index(
        "ix_integration_conflicts_status",
        "integration_conflicts",
        ["resolution_status"],
    )
    op.create_index(
        "ix_integration_conflicts_detected",
        "integration_conflicts",
        ["detected_at"],
    )

    # integration_rate_limits
    op.create_table(
        "integration_rate_limits",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("integration_credential_id", sa.String(36), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("api_endpoint", sa.String(255), nullable=False),
        sa.Column("requests_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("requests_limit", sa.Integer(), nullable=False),
        sa.Column("window_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_rate_limited", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("backoff_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.ForeignKeyConstraint(
            ["integration_credential_id"],
            ["integration_credentials.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "uc_credential_endpoint",
        "integration_rate_limits",
        ["integration_credential_id", "api_endpoint"],
    )
    op.create_index(
        "ix_rate_limits_backoff",
        "integration_rate_limits",
        ["backoff_until"],
    )


def downgrade() -> None:
    """Remove external integrations tables."""
    op.drop_table("integration_rate_limits")
    op.drop_table("integration_conflicts")
    op.drop_table("integration_sync_logs")
    op.drop_table("integration_sync_queue")
    op.drop_table("integration_mappings")
    op.drop_table("integration_credentials")
