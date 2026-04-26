"""Base configuration settings for Phenotype services.

Provides a BaseConfig class using Pydantic BaseSettings for environment-aware
configuration loading. Inheriting from BaseConfig enables projects to define
their own settings with automatic support for environment variables, .env files,
and validation.

Example:
    >>> from phenotype_config import BaseConfig
    >>> class MySettings(BaseConfig):
    ...     api_key: str
    ...     debug: bool = False
    >>>
    >>> # Automatically loads from environment and .env file
    >>> settings = MySettings()
"""

import os
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration class for Phenotype services.

    Provides environment variable loading, .env file support, and common
    configuration patterns. Subclass this to define service-specific settings.

    Environment variables are loaded with optional prefix (e.g., MYSERVICE_).
    Configuration can be provided via:
    - Environment variables
    - .env file (in current directory or PHENOTYPE_ENV_PATH)
    - Direct instantiation
    """

    # Common settings applicable to all services
    environment: str = Field(
        default="development",
        description="Deployment environment (development, staging, production)",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    service_name: str | None = Field(
        default=None,
        description="Service identifier for logging and tracing",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_settings,
    ):
        """Customize settings source resolution order.

        Priority order:
        1. Explicit init arguments
        2. Environment variables
        3. .env file
        4. Default values
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_settings,
        )

    def validate_setup(self) -> None:
        """Validate configuration on startup.

        Override in subclasses to add service-specific validation.
        Should raise ValueError or RuntimeError if configuration is invalid.
        """
        pass


# Global settings cache
_settings_cache: dict[type, Any] = {}


def get_settings(settings_class: type[BaseConfig]) -> BaseConfig:
    """Get or create cached settings instance.

    Caches settings to avoid repeated parsing and validation on every access.
    Call with your settings class to get a typed, cached instance.

    Args:
        settings_class: Your BaseConfig subclass

    Returns:
        Cached instance of the settings class
    """
    if settings_class not in _settings_cache:
        instance = settings_class()
        instance.validate_setup()
        _settings_cache[settings_class] = instance
    return _settings_cache[settings_class]


def clear_settings_cache() -> None:
    """Clear the settings cache.

    Useful for testing or resetting configuration.
    """
    _settings_cache.clear()
