"""
Pydantic models describing the configuration schema.
"""

from typing import Any

from pydantic import BaseModel, Field, validator

from .config_profiles import ConfigProfile


class DatabaseConfig(BaseModel):
    """
    Database connection settings.
    """

    host: str = Field(default="localhost", description="Database host address")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port number")
    name: str = Field(default="myapp", description="Database name")
    username: str = Field(default="", description="Database username")
    password: str = Field(default="", description="Database password")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    timeout: int = Field(default=30, ge=1, description="Connection timeout in seconds")

    @validator("name")
    def validate_name(self, value: str) -> str:
        if not value:
            raise ValueError("Database name cannot be empty")
        return value


class CacheConfig(BaseModel):
    """
    Cache backend configuration.
    """

    enabled: bool = Field(default=True, description="Enable/disable caching")
    backend: str = Field(default="memory", description="Cache backend type")
    host: str = Field(default="localhost", description="Cache server host")
    port: int = Field(default=6379, ge=1, le=65535, description="Cache server port")
    ttl: int = Field(default=300, ge=0, description="Default time-to-live in seconds")
    max_size: int = Field(default=1000, ge=1, description="Maximum cache size")

    @validator("backend")
    def validate_backend(self, value: str) -> str:
        allowed = ["memory", "redis", "memcached"]
        if value not in allowed:
            raise ValueError(f"Backend must be one of {allowed}")
        return value


class LoggingConfig(BaseModel):
    """
    Logging output configuration.
    """

    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(default="json", description="Log format")
    output: str = Field(default="console", description="Log output target")
    file_path: str = Field(default="logs/app.log", description="Log file path")
    max_size: int = Field(default=10485760, ge=1024, description="Maximum log file size in bytes")
    backup_count: int = Field(default=5, ge=0, description="Number of backup log files to keep")

    @validator("level")
    def validate_level(self, value: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        upper = value.upper()
        if upper not in allowed:
            raise ValueError(f"Level must be one of {allowed}")
        return upper


class AppConfig(BaseModel):
    """
    Core application settings.
    """

    name: str = Field(default="MyApp", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="production", description="Environment name")
    secret_key: str = Field(default="", description="Secret key for encryption")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")

    @validator("secret_key")
    def validate_secret_key(self, value: str, values: dict[str, Any]) -> str:
        if values.get("environment") == "production" and not value:
            raise ValueError("Secret key is required in production")
        return value


class ConfigSchema(BaseModel):
    """
    Root configuration schema.
    """

    version: str = Field(default="1.0.0", description="Schema version")
    profile: ConfigProfile = Field(default=ConfigProfile.DEVELOPMENT, description="Active profile")
    app: AppConfig = Field(default_factory=AppConfig, description="Application configuration")
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig, description="Database configuration",
    )
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache configuration")
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig, description="Logging configuration",
    )
    custom: dict[str, Any] = Field(default_factory=dict, description="Custom configuration fields")

    class Config:
        use_enum_values = True


__all__ = [
    "AppConfig",
    "CacheConfig",
    "ConfigSchema",
    "DatabaseConfig",
    "LoggingConfig",
]
