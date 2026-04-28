"""
Compatibility layer re-exporting the configuration toolkit.
"""

from .config_file_watcher import ConfigFileHandler
from .config_manager import ConfigManager, create_example_config, load_config
from .config_migration import ConfigMigration
from .config_profiles import ConfigProfile
from .config_schemas import (
    AppConfig,
    CacheConfig,
    ConfigSchema,
    DatabaseConfig,
    LoggingConfig,
)

__all__ = [
    "AppConfig",
    "CacheConfig",
    "ConfigFileHandler",
    "ConfigManager",
    "ConfigMigration",
    "ConfigProfile",
    "ConfigSchema",
    "DatabaseConfig",
    "LoggingConfig",
    "create_example_config",
    "load_config",
]
