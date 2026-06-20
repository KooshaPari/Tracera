"""Modern pydantic-settings based configuration for TraceRTM.

This module provides type-safe, validated configuration management with support for:
- Environment variables (TRACERTM_* prefix)
- .env files
- YAML configuration files
- CLI overrides
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ViewType = Literal["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
OutputFormat = Literal["table", "json", "yaml", "csv"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(
        default="sqlite:///tracertm.db",
        description="Database URL (postgresql://... or sqlite://...)",
    )
    echo: bool = Field(default=False, description="Enable SQLAlchemy echo mode")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=200, description="Max overflow connections")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "sqlite:///")):
            msg = "Database URL must start with 'postgresql://' or 'sqlite:///'"
            raise ValueError(msg)
        return v


class TraceSettings(BaseSettings):
    """Main TraceRTM settings with pydantic-settings integration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TRACERTM_",
        case_sensitive=False,
        extra="ignore",
    )

    # Project settings
    current_project_id: str | None = Field(None, description="Currently active project ID")
    current_project_name: str | None = Field(None, description="Currently active project name")

    # Display preferences
    default_view: ViewType = Field("FEATURE", description="Default view type")
    output_format: OutputFormat = Field("table", description="Default output format")

    # Performance
    max_agents: int = Field(1000, ge=1, le=10000, description="Max concurrent agents")
    cache_ttl: int = Field(300, ge=0, le=3600, description="Cache TTL in seconds")
    batch_size: int = Field(100, ge=1, le=1000, description="Batch operation size")

    # Logging
    log_level: LogLevel = Field("INFO", description="Logging level")
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )

    # Database
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Paths
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".tracertm",
        description="Data directory path",
    )
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".config" / "tracertm",
        description="Config directory path",
    )

    # Features
    enable_cache: bool = Field(True, description="Enable caching")
    enable_async: bool = Field(True, description="Enable async operations")
    enable_validation: bool = Field(True, description="Enable strict validation")

    def __init__(self, **data: object) -> None:
        """Initialize settings and create directories."""
        super().__init__(**data)  # type: ignore[arg-type]
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config_file(self) -> Path:
        """Get config file path."""
        return self.config_dir / "config.yaml"

    @property
    def env_file_path(self) -> Path:
        """Get .env file path."""
        return Path(".env")


_settings_instance: TraceSettings | None = None


def get_settings() -> TraceSettings:
    """Get or create settings instance (singleton pattern)."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = TraceSettings()
    return _settings_instance


def reset_settings() -> None:
    """Reset settings instance (useful for testing)."""
    global _settings_instance
    _settings_instance = None
