"""Add execution system for QA Integration.

Creates tables for tracking test/recording executions, artifacts,
Codex agent interactions, and per-project environment configuration.

Revision ID: 019_add_execution_system
Revises: 018
Create Date: 2026-01-28 00:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.sqlite import JSON

from alembic import op

# revision identifiers, used by Alembic.
revision = "019_add_execution_system"
down_revision = "018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create execution system tables."""
    # Execution: Tracks test/recording runs
    op.create_table(
        "executions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_run_id",
            sa.String(255),
            sa.ForeignKey("test_runs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Execution type: vhs, playwright, codex, custom
        sa.Column("execution_type", sa.String(50), nullable=False),
        # Trigger source: github_pr, github_push, webhook, manual
        sa.Column("trigger_source", sa.String(50), nullable=False),
        sa.Column("trigger_ref", sa.String(255), nullable=True),
        # Status: pending, running, passed, failed, cancelled
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        # Docker container tracking
        sa.Column("container_id", sa.String(64), nullable=True),
        sa.Column("container_image", sa.String(255), nullable=True),
        # Configuration
        sa.Column("config", JSON, nullable=True),
        sa.Column("environment", sa.Text, nullable=True),  # Encrypted env vars
        # Timing
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        # Results
        sa.Column("exit_code", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("output_summary", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # ExecutionArtifact: Screenshots, videos, GIFs, logs, traces
    op.create_table(
        "execution_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "execution_id",
            sa.String(36),
            sa.ForeignKey("executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Artifact type: screenshot, video, gif, log, trace, tape
        sa.Column("artifact_type", sa.String(50), nullable=False),
        # File paths (local filesystem)
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("thumbnail_path", sa.String(500), nullable=True),
        # File metadata
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("artifact_metadata", JSON, nullable=True),  # dimensions, duration
        # Timestamps
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # CodexAgentInteraction: AI agent task history
    op.create_table(
        "codex_agent_interactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "execution_id",
            sa.String(36),
            sa.ForeignKey("executions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "artifact_id",
            sa.String(36),
            sa.ForeignKey("execution_artifacts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Task type: review_image, review_video, code_review, generate_test
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("input_data", JSON, nullable=True),
        sa.Column("output_data", JSON, nullable=True),
        sa.Column("prompt", sa.Text, nullable=True),
        sa.Column("response", sa.Text, nullable=True),
        # Status: pending, running, completed, failed, cancelled
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        # Timing
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        # Usage
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("model_used", sa.String(50), nullable=True),
        # Error handling
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        # Timestamp
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ExecutionEnvironmentConfig: Per-project settings
    op.create_table(
        "execution_environment_configs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Docker configuration
        sa.Column(
            "docker_image",
            sa.String(255),
            nullable=False,
            server_default="node:20-alpine",
        ),
        sa.Column("resource_limits", JSON, nullable=True),
        sa.Column("environment_vars", sa.Text, nullable=True),  # Encrypted
        sa.Column("working_directory", sa.String(500), nullable=True),
        sa.Column("network_mode", sa.String(50), nullable=False, server_default="bridge"),
        # Feature toggles
        sa.Column("vhs_enabled", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("playwright_enabled", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("codex_enabled", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("auto_screenshot", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("auto_video", sa.Boolean, nullable=False, server_default="0"),
        # VHS settings
        sa.Column("vhs_theme", sa.String(100), nullable=False, server_default="Dracula"),
        sa.Column("vhs_font_size", sa.Integer, nullable=False, server_default="14"),
        sa.Column("vhs_width", sa.Integer, nullable=False, server_default="1200"),
        sa.Column("vhs_height", sa.Integer, nullable=False, server_default="600"),
        sa.Column("vhs_framerate", sa.Integer, nullable=False, server_default="30"),
        # Playwright settings
        sa.Column(
            "playwright_browser",
            sa.String(50),
            nullable=False,
            server_default="chromium",
        ),
        sa.Column("playwright_headless", sa.Boolean, nullable=False, server_default="1"),
        sa.Column(
            "playwright_viewport_width",
            sa.Integer,
            nullable=False,
            server_default="1280",
        ),
        sa.Column(
            "playwright_viewport_height",
            sa.Integer,
            nullable=False,
            server_default="720",
        ),
        sa.Column("playwright_video_size", JSON, nullable=True),
        # Codex settings
        sa.Column(
            "codex_sandbox_mode",
            sa.String(50),
            nullable=False,
            server_default="workspace-write",
        ),
        sa.Column("codex_full_auto", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("codex_timeout", sa.Integer, nullable=False, server_default="300"),
        # Storage settings
        sa.Column("artifact_retention_days", sa.Integer, nullable=False, server_default="30"),
        sa.Column("storage_path", sa.String(500), nullable=True),
        sa.Column("max_artifact_size_mb", sa.Integer, nullable=False, server_default="100"),
        # Execution limits
        sa.Column(
            "max_concurrent_executions",
            sa.Integer,
            nullable=False,
            server_default="3",
        ),
        sa.Column("execution_timeout", sa.Integer, nullable=False, server_default="600"),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create indexes for performance
    op.create_index("idx_executions_project_id", "executions", ["project_id"])
    op.create_index("idx_executions_status", "executions", ["status"])
    op.create_index("idx_executions_execution_type", "executions", ["execution_type"])
    op.create_index("idx_executions_trigger_source", "executions", ["trigger_source"])
    op.create_index("idx_executions_test_run_id", "executions", ["test_run_id"])
    op.create_index("idx_executions_item_id", "executions", ["item_id"])

    op.create_index("idx_execution_artifacts_execution_id", "execution_artifacts", ["execution_id"])
    op.create_index("idx_execution_artifacts_item_id", "execution_artifacts", ["item_id"])
    op.create_index(
        "idx_execution_artifacts_artifact_type",
        "execution_artifacts",
        ["artifact_type"],
    )

    op.create_index(
        "idx_codex_interactions_project_id",
        "codex_agent_interactions",
        ["project_id"],
    )
    op.create_index(
        "idx_codex_interactions_execution_id",
        "codex_agent_interactions",
        ["execution_id"],
    )
    op.create_index("idx_codex_interactions_status", "codex_agent_interactions", ["status"])
    op.create_index(
        "idx_codex_interactions_task_type",
        "codex_agent_interactions",
        ["task_type"],
    )
    op.create_index(
        "idx_codex_interactions_artifact_id",
        "codex_agent_interactions",
        ["artifact_id"],
    )


def downgrade() -> None:
    """Drop execution system tables."""
    # Drop indexes first
    op.drop_index("idx_codex_interactions_artifact_id")
    op.drop_index("idx_codex_interactions_task_type")
    op.drop_index("idx_codex_interactions_status")
    op.drop_index("idx_codex_interactions_execution_id")
    op.drop_index("idx_codex_interactions_project_id")

    op.drop_index("idx_execution_artifacts_artifact_type")
    op.drop_index("idx_execution_artifacts_item_id")
    op.drop_index("idx_execution_artifacts_execution_id")

    op.drop_index("idx_executions_item_id")
    op.drop_index("idx_executions_test_run_id")
    op.drop_index("idx_executions_trigger_source")
    op.drop_index("idx_executions_execution_type")
    op.drop_index("idx_executions_status")
    op.drop_index("idx_executions_project_id")

    # Drop tables in reverse order (foreign key dependencies)
    op.drop_table("execution_environment_configs")
    op.drop_table("codex_agent_interactions")
    op.drop_table("execution_artifacts")
    op.drop_table("executions")
