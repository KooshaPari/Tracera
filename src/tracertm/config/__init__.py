"""
Configuration management for TraceRTM.

Provides both legacy (schema.py) and modern (settings.py) configuration approaches.
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
                                      # Legacy
                                      "ConfigManager",
                                      "DatabaseSettings",
                                      "LogLevel",
                                      "OutputFormat",
                                      # Modern pydantic-settings
                                      "TraceSettings",
                                      "ViewType",
                                      "get_settings",
                                      "reset_settings",
]
