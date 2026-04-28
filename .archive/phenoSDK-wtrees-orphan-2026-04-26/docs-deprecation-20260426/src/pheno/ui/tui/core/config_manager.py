"""
High-level configuration manager implementation.
"""

from __future__ import annotations

import json
import logging
import threading
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import ValidationError
from watchdog.observers import Observer

from .config_file_watcher import ConfigFileHandler
from .config_migration import ConfigMigration
from .config_profiles import ConfigProfile
from .config_schemas import ConfigSchema

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Hierarchical configuration loader with optional hot reload.
    """

    def __init__(self) -> None:
        self._default_config: dict[str, Any] = {}
        self._user_config: dict[str, Any] = {}
        self._project_config: dict[str, Any] = {}
        self._runtime_config: dict[str, Any] = {}
        self._merged_config: dict[str, Any] = {}

        self._config_path: Path | None = None
        self._schema: ConfigSchema | None = None
        self._migration = ConfigMigration()

        self._observer: Observer | None = None
        self._reload_callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._lock = threading.RLock()

        self._register_default_migrations()
        self.load_defaults()

    def _register_default_migrations(self) -> None:
        """
        Seed the migration registry with built-in upgrades.
        """

        def migrate_1_0_to_1_1(payload: dict[str, Any]) -> dict[str, Any]:
            if "logging" not in payload:
                payload["logging"] = {
                    "level": "INFO",
                    "format": "json",
                    "output": "console",
                }
            return payload

        self._migration.register("1.0.0", "1.1.0", migrate_1_0_to_1_1)

    def load_defaults(self) -> None:
        """
        Populate defaults from :class:`ConfigSchema`.
        """

        with self._lock:
            self._default_config = ConfigSchema().dict()
            self._merge_configs()
            logger.debug("Loaded default configuration")

    def load_config(self, path: str | Path, profile: ConfigProfile | None = None) -> None:
        """
        Load configuration from ``path`` and optionally override the profile.
        """

        resolved_path = Path(path).expanduser().resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {resolved_path}")

        with self._lock:
            self._config_path = resolved_path
            with open(resolved_path) as handle:
                data = yaml.safe_load(handle) or {}

            if profile:
                data["profile"] = profile.value

            current_version = data.get("version", "1.0.0")
            target_version = ConfigSchema().version
            if current_version != target_version:
                logger.info("Migrating config from %s to %s", current_version, target_version)
                data = self._migration.migrate(data, current_version, target_version)

            self._project_config = data
            self._merge_configs()
            self.validate()
            logger.info("Loaded configuration from: %s", resolved_path)

    def load_user_config(self, path: str | Path) -> None:
        """
        Merge a user-level configuration file.
        """

        resolved_path = Path(path).expanduser().resolve()
        if not resolved_path.exists():
            logger.warning("User config not found: %s", resolved_path)
            return

        with self._lock:
            with open(resolved_path) as handle:
                self._user_config = yaml.safe_load(handle) or {}
            self._merge_configs()
            logger.info("Loaded user configuration from: %s", resolved_path)

    def load_project_config(self, path: str | Path) -> None:
        """
        Alias for :meth:`load_config` for API parity.
        """

        self.load_config(path)

    def _merge_configs(self) -> None:
        """
        Rebuild the merged configuration snapshot honoring precedence.
        """

        with self._lock:
            merged = deepcopy(self._default_config)
            self._deep_merge(merged, self._user_config)
            self._deep_merge(merged, self._project_config)
            self._deep_merge(merged, self._runtime_config)
            self._merged_config = merged

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = deepcopy(value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the value for ``key`` using dot notation.
        """

        with self._lock:
            current: Any = self._merged_config
            for part in key.split("."):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current

    def set(self, key: str, value: Any) -> None:
        """
        Store ``value`` at ``key`` (runtime override).
        """

        with self._lock:
            current = self._runtime_config
            parts = key.split(".")
            for segment in parts[:-1]:
                current = current.setdefault(segment, {})
            current[parts[-1]] = value
            self._merge_configs()
            logger.debug("Set config: %s = %s", key, value)

    def get_all(self) -> dict[str, Any]:
        """
        Return a deep copy of the merged configuration.
        """

        with self._lock:
            return deepcopy(self._merged_config)

    def save(self, path: str | Path | None = None) -> None:
        """
        Persist the merged configuration to disk.
        """

        target = Path(path).expanduser().resolve() if path else self._config_path
        if target is None:
            raise ValueError("No path specified and no config file loaded")

        with self._lock:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w") as handle:
                yaml.safe_dump(
                    self._merged_config, handle, default_flow_style=False, sort_keys=False, indent=2,
                )
            logger.info("Saved configuration to: %s", target)

    def validate(self) -> bool:
        """
        Validate the merged configuration against the schema.
        """

        with self._lock:
            try:
                self._schema = ConfigSchema(**self._merged_config)
            except ValidationError as exc:  # pragma: no cover - logging side effect
                logger.exception("Configuration validation failed: %s", exc)
                raise
            logger.debug("Configuration validation passed")
            return True

    def switch_profile(self, profile: ConfigProfile) -> None:
        """
        Switch to ``profile`` and apply predefined overrides.
        """

        with self._lock:
            self.set("profile", profile.value)
            if profile == ConfigProfile.PRODUCTION:
                self.set("app.debug", False)
                self.set("logging.level", "WARNING")
            elif profile == ConfigProfile.DEVELOPMENT:
                self.set("app.debug", True)
                self.set("logging.level", "DEBUG")
            elif profile == ConfigProfile.STAGING:
                self.set("app.debug", False)
                self.set("logging.level", "INFO")
            logger.info("Switched to profile: %s", profile.value)

    def enable_hot_reload(self, callback: Callable[[dict[str, Any]], None] | None = None) -> None:
        """
        Start watching the active config file for changes.
        """

        if self._config_path is None:
            logger.warning("No config file loaded, hot-reload not enabled")
            return

        if callback:
            self._reload_callbacks.append(callback)

        if self._observer is None:
            handler = ConfigFileHandler(self._on_file_changed)
            observer = Observer()
            observer.schedule(handler, str(self._config_path.parent), recursive=False)
            observer.start()
            self._observer = observer
            logger.info("Hot-reload enabled")

    def disable_hot_reload(self) -> None:
        """
        Stop the file watcher if it is running.
        """

        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("Hot-reload disabled")

    def _on_file_changed(self, path: str) -> None:
        if Path(path) != self._config_path:
            return

        try:
            self.load_config(self._config_path)
            for callback in list(self._reload_callbacks):
                try:
                    callback(self.get_all())
                except Exception as exc:  # pragma: no cover - defensive logging
                    logger.exception("Reload callback error: %s", exc)
            logger.info("Configuration reloaded")
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to reload configuration: %s", exc)

    def export_schema(self, path: str | Path) -> None:
        """
        Write the JSON schema for the configuration to ``path``.
        """

        target = Path(path).expanduser().resolve()
        with open(target, "w") as handle:
            json.dump(ConfigSchema.schema(), handle, indent=2)
        logger.info("Exported schema to: %s", target)

    def export_example(self, path: str | Path) -> None:
        """
        Write an example YAML configuration to ``path``.
        """

        target = Path(path).expanduser().resolve()
        example = {
            "version": "1.0.0",
            "profile": "development",
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": True,
                "environment": "development",
                "secret_key": "${APP_SECRET_KEY}",
                "host": "0.0.0.0",
                "port": 8000,
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp_dev",
                "username": "admin",
                "password": "secret",
                "pool_size": 10,
                "timeout": 30,
            },
            "cache": {
                "enabled": True,
                "backend": "memory",
                "host": "localhost",
                "port": 6379,
                "ttl": 300,
                "max_size": 1000,
            },
            "logging": {
                "level": "DEBUG",
                "format": "json",
                "output": "console",
                "file_path": "logs/app.log",
                "max_size": 10485760,
                "backup_count": 5,
            },
        }

        with open(target, "w") as handle:
            yaml.safe_dump(example, handle, default_flow_style=False, sort_keys=False, indent=2)
        logger.info("Exported example configuration to: %s", target)

    def __del__(self) -> None:  # pragma: no cover - best effort cleanup
        self.disable_hot_reload()


def load_config(path: str | Path) -> ConfigManager:
    """
    Convenience helper returning a configured :class:`ConfigManager`.
    """

    manager = ConfigManager()
    manager.load_config(path)
    return manager


def create_example_config(path: str | Path) -> None:
    """
    Generate an example configuration YAML file.
    """

    manager = ConfigManager()
    manager.export_example(path)


__all__ = [
    "ConfigManager",
    "create_example_config",
    "load_config",
]
