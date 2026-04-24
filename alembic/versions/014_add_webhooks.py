"""Add webhook integrations tables.

Revision ID: 014_add_webhooks
Revises: 013_fix_denorm
Create Date: 2026-01-28
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "014_add_webhooks"
down_revision = "013_fix_denorm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Create webhook_integrations table
    op.create_table(
        "webhook_integrations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Basic info
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # Provider configuration
        sa.Column(
            "provider",
            sa.Enum(
                "github_actions",
                "gitlab_ci",
                "jenkins",
                "azure_devops",
                "circleci",
                "travis_ci",
                "custom",
                name="webhookprovider",
            ),
            nullable=False,
            server_default="custom",
        ),
        sa.Column(
            "status",
            sa.Enum("active", "paused", "disabled", name="webhookstatus"),
            nullable=False,
            server_default="active",
        ),
        # Authentication
        sa.Column("webhook_secret", sa.String(64), nullable=False),
        sa.Column("api_key", sa.String(128), nullable=True),
        # Event configuration
        sa.Column("enabled_events", sa.JSON(), nullable=True),
        sa.Column("event_filters", sa.JSON(), nullable=True),
        # Target configuration
        sa.Column("callback_url", sa.String(1000), nullable=True),
        sa.Column("callback_headers", sa.JSON(), nullable=True),
        # Default mapping
        sa.Column(
            "default_suite_id",
            sa.String(36),
            sa.ForeignKey("test_suites.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Rate limiting
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("last_rate_limit_reset", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requests_in_window", sa.Integer(), nullable=False, server_default="0"),
        # Statistics
        sa.Column("total_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("successful_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_request_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        # Settings
        sa.Column("auto_create_run", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("auto_complete_run", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("verify_signatures", sa.Boolean(), nullable=False, server_default="true"),
        # Extensible metadata
        sa.Column("webhook_metadata", sa.JSON(), nullable=True),
        # Optimistic locking
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Create indexes for webhook_integrations
    op.create_index(
        "ix_webhook_integrations_project_id",
        "webhook_integrations",
        ["project_id"],
    )
    op.create_index(
        "ix_webhook_integrations_provider",
        "webhook_integrations",
        ["provider"],
    )
    op.create_index(
        "ix_webhook_integrations_status",
        "webhook_integrations",
        ["status"],
    )

    # Create webhook_logs table
    op.create_table(
        "webhook_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "webhook_id",
            sa.String(36),
            sa.ForeignKey("webhook_integrations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Request details
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=True),
        sa.Column("http_method", sa.String(10), nullable=False, server_default="POST"),
        sa.Column("source_ip", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        # Payload
        sa.Column("request_headers", sa.JSON(), nullable=True),
        sa.Column("request_body_preview", sa.Text(), nullable=True),
        sa.Column("payload_size_bytes", sa.Integer(), nullable=True),
        # Processing result
        sa.Column("success", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status_code", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        # Associated entities
        sa.Column("test_run_id", sa.String(36), nullable=True),
        sa.Column("results_submitted", sa.Integer(), nullable=False, server_default="0"),
        # Timestamp
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create indexes for webhook_logs
    op.create_index(
        "ix_webhook_logs_webhook_id",
        "webhook_logs",
        ["webhook_id"],
    )
    op.create_index(
        "ix_webhook_logs_created_at",
        "webhook_logs",
        ["created_at"],
    )
    op.create_index(
        "ix_webhook_logs_success",
        "webhook_logs",
        ["success"],
    )
    op.create_index(
        "ix_webhook_logs_event_type",
        "webhook_logs",
        ["event_type"],
    )


def downgrade() -> None:
    """Downgrade."""
    # Drop indexes
    op.drop_index("ix_webhook_logs_event_type", table_name="webhook_logs")
    op.drop_index("ix_webhook_logs_success", table_name="webhook_logs")
    op.drop_index("ix_webhook_logs_created_at", table_name="webhook_logs")
    op.drop_index("ix_webhook_logs_webhook_id", table_name="webhook_logs")

    op.drop_index("ix_webhook_integrations_status", table_name="webhook_integrations")
    op.drop_index("ix_webhook_integrations_provider", table_name="webhook_integrations")
    op.drop_index("ix_webhook_integrations_project_id", table_name="webhook_integrations")

    # Drop tables
    op.drop_table("webhook_logs")
    op.drop_table("webhook_integrations")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS webhookstatus")
    op.execute("DROP TYPE IF EXISTS webhookprovider")
