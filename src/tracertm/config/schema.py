"""Pydantic configuration schema for TraceRTM."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ViewType = Literal["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
OutputFormat = Literal["table", "json", "yaml", "csv"]


class Config(BaseModel):
    """TraceRTM configuration schema.

    Configuration hierarchy (highest to lowest precedence):
    1. CLI flags (--flag)
    2. Environment variables (TRACERTM_*)
    3. Project config (~/.tracertm/projects/<project_id>/config.yaml)
    4. Global config (~/.tracertm/config.yaml)
    """

    # Database
    database_url: str | None = Field(None, description="Database URL (postgresql://... or sqlite://... for testing)")

    # Current project
    current_project_id: str | None = Field(None, description="Currently active project ID")

    current_project_name: str | None = Field(None, description="Currently active project name")

    # Display preferences
    default_view: ViewType = Field("FEATURE", description="Default view when displaying items")

    output_format: OutputFormat = Field("table", description="Default output format for CLI commands")

    # Performance
    max_agents: int = Field(1000, ge=1, le=10000, description="Maximum number of concurrent agents")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field("INFO", description="Logging level")

    # CLI aliases (user-configured)
    aliases: dict[str, str] = Field(default_factory=dict, description="User-configured command aliases")

    # Sync API configuration
    api_url: str = Field("https://api.tracertm.io", description="Backend API URL for sync operations")

    api_token: str | None = Field(None, description="JWT token for API authentication")

    api_timeout: float = Field(30.0, ge=1.0, le=300.0, description="API request timeout in seconds")

    api_max_retries: int = Field(3, ge=1, le=10, description="Maximum number of retry attempts for API requests")

    sync_enabled: bool = Field(True, description="Enable/disable sync with backend")

    sync_interval_seconds: int = Field(300, ge=10, description="Auto-sync interval in seconds (default: 5 minutes)")

    sync_conflict_strategy: Literal["last_write_wins", "local_wins", "remote_wins", "manual"] = Field(
        "last_write_wins",
        description="Default conflict resolution strategy",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str | None) -> str | None:
        """Validate database URL format."""
        if v is None:
            return v

        # Allow PostgreSQL (production) and SQLite (testing/development)
        if not v.startswith(("postgresql://", "sqlite:///")):
            msg = "Database URL must start with 'postgresql://' or 'sqlite:///'"
            raise ValueError(msg)

        return v

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v: str) -> str:
        """Validate API URL format."""
        if not v.startswith(("http://", "https://")):
            msg = "API URL must start with 'http://' or 'https://'"
            raise ValueError(msg)

        return v.rstrip("/")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
