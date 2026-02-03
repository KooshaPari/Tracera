"""Configuration management for TraceRTM."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration."""

    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(default="tracertm")
    username: str = Field(default="tracertm")
    password: str = Field(default="tracertm")
    # Connection pool settings optimized for performance
    pool_size: int = Field(default=20)  # Base number of connections
    max_overflow: int = Field(default=30)  # Extra connections when pool exhausted
    pool_timeout: int = Field(default=30)  # Seconds to wait for available connection
    pool_recycle: int = Field(default=1800)  # Recycle connections after 30 minutes

    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class UIConfig(BaseModel):
    """UI configuration."""

    theme: str = Field(default="developer-focus")  # or "high-contrast"
    force_bold: bool = Field(default=False)
    use_symbols: bool = Field(default=True)


class Config(BaseModel):
    """TraceRTM configuration."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".tracertm")
    current_project: str | None = None

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """Load configuration from file."""
        if config_path is None:
            config_path = Path.home() / ".tracertm" / "config.yaml"

        if not config_path.exists():
            # Create default config
            config = cls()
            config.save(config_path)
            return config

        with config_path.open() as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def save(self, config_path: Path | None = None) -> None:
        """Save configuration to file."""
        if config_path is None:
            config_path = Path.home() / ".tracertm" / "config.yaml"

        config_path.parent.mkdir(parents=True, exist_ok=True)

        with config_path.open("w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def set_config(config: Config) -> None:
    """Set global config instance."""
    global _config
    _config = config
