"""Execution Environment Configuration model for QA Integration system.

Per-project settings for Docker containers, VHS, Playwright, and Codex.
"""

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_config_uuid() -> str:
    """Generate a UUID string for config ID."""
    return str(uuid.uuid4())


class ExecutionEnvironmentConfig(Base, TimestampMixin):
    """Execution Environment Configuration model.

    Per-project settings for Docker execution, VHS recording,
    Playwright testing, and Codex AI agent integration.
    """

    __tablename__ = "execution_environment_configs"

    __table_args__ = (
        Index("idx_exec_env_config_project_id", "project_id", unique=True),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_config_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Docker configuration
    docker_image: Mapped[str] = mapped_column(String(255), nullable=False, default="node:20-alpine")
    resource_limits: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)  # CPU, memory limits
    environment_vars: Mapped[str | None] = mapped_column(Text, nullable=True)  # Encrypted env vars
    working_directory: Mapped[str | None] = mapped_column(String(500), nullable=True)
    network_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="bridge")

    # Feature toggles
    vhs_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    playwright_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    codex_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_screenshot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_video: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # VHS settings
    vhs_theme: Mapped[str] = mapped_column(String(100), nullable=False, default="Dracula")
    vhs_font_size: Mapped[int] = mapped_column(Integer, nullable=False, default=14)
    vhs_width: Mapped[int] = mapped_column(Integer, nullable=False, default=1200)
    vhs_height: Mapped[int] = mapped_column(Integer, nullable=False, default=600)
    vhs_framerate: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    # Playwright settings
    playwright_browser: Mapped[str] = mapped_column(String(50), nullable=False, default="chromium")
    playwright_headless: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    playwright_viewport_width: Mapped[int] = mapped_column(Integer, nullable=False, default=1280)
    playwright_viewport_height: Mapped[int] = mapped_column(Integer, nullable=False, default=720)
    playwright_video_size: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # Codex settings
    codex_sandbox_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="workspace-write")
    codex_full_auto: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    codex_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=300)  # seconds

    # Storage settings
    artifact_retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    max_artifact_size_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    # Execution limits
    max_concurrent_executions: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    execution_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=600)  # seconds

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ExecutionEnvironmentConfig(id={self.id!r}, project_id={self.project_id!r})>"
