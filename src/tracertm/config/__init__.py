"""Configuration management for TraceRTM.

Provides schema.py (Config, ConfigManager) and settings.py (TraceSettings) configuration.
New code should use the pydantic-settings based TraceSettings from settings.py.
"""

from tracertm.config.manager import ConfigManager
from tracertm.config.schema import Config
from tracertm.config.settings import (
    DatabaseSettings,
    LogLevel,
    OutputFormat,
    TraceSettings,
    ViewType,
    get_settings,
    reset_settings,
)

__all__ = [
    "Config",
    "ConfigManager",
    "DatabaseSettings",
    "LogLevel",
    "OutputFormat",
    "TraceSettings",
    "ViewType",
    "get_settings",
    "reset_settings",
]
