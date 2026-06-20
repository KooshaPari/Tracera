"""Service for managing plugins.

Functional Requirements: FR-AI-004
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PluginType(StrEnum):
    """Plugin types."""

    VIEW = "view"
    LINK_TYPE = "link_type"
    EXPORT_FORMAT = "export_format"
    QUERY_FILTER = "query_filter"
    CUSTOM = "custom"


@dataclass
class Plugin:
    """Plugin definition."""

    name: str
    version: str
    plugin_type: PluginType
    description: str
    author: str
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class RegisterPluginInput:
    """Input for registering a plugin."""

    name: str
    version: str
    plugin_type: PluginType
    description: str
    author: str
    config: dict[str, Any] | None = None


class PluginService:
    """Service for managing plugins."""

    def __init__(self) -> None:
        """Initialize."""
        self.plugins: dict[str, Plugin] = {}
        self.hooks: dict[str, list[Callable]] = {}

    def register_plugin(self, input: RegisterPluginInput) -> Plugin:
        """Register a new plugin."""
        plugin = Plugin(
            name=input.name,
            version=input.version,
            plugin_type=input.plugin_type,
            description=input.description,
            author=input.author,
            config=input.config or {},
        )
        self.plugins[input.name] = plugin
        return plugin

    def unregister_plugin(self, name: str) -> bool:
        """Unregister a plugin."""
        if name in self.plugins:
            del self.plugins[name]
            return True
        return False

    def get_plugin(self, name: str) -> Plugin | None:
        """Get plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self, plugin_type: PluginType | None = None) -> list[Plugin]:
        """List all plugins, optionally filtered by type."""
        plugins = list(self.plugins.values())

        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]

        return plugins

    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = True
            return True
        return False

    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = False
            return True
        return False

    def update_plugin_config(
        self,
        name: str,
        config: dict[str, Any],
    ) -> Plugin | None:
        """Update plugin configuration."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.config.update(config)
            return plugin
        return None

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a hook callback."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    def unregister_hook(self, hook_name: str, callback: Callable) -> bool:
        """Unregister a hook callback."""
        if hook_name in self.hooks:
            try:
                self.hooks[hook_name].remove(callback)
            except ValueError:
                return False
            else:
                return True
        return False

    def execute_hook(self, hook_name: str, *args: object, **kwargs: object) -> list[object]:
        """Execute all callbacks for a hook."""
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except (ImportError, ModuleNotFoundError, AttributeError) as e:
                    results.append({"error": str(e)})
        return results

    def get_plugin_stats(self) -> dict[str, Any]:
        """Get plugin statistics."""
        total = len(self.plugins)
        enabled = len([p for p in self.plugins.values() if p.enabled])
        disabled = total - enabled

        by_type: dict[str, int] = {}
        for plugin in self.plugins.values():
            plugin_type = plugin.plugin_type.value
            by_type[plugin_type] = by_type.get(plugin_type, 0) + 1

        return {
            "total_plugins": total,
            "enabled": enabled,
            "disabled": disabled,
            "by_type": by_type,
            "total_hooks": len(self.hooks),
        }

    def validate_plugin(self, plugin: Plugin) -> list[str]:
        """Validate plugin configuration."""
        errors = []

        if not plugin.name:
            errors.append("Plugin name is required")

        if not plugin.version:
            errors.append("Plugin version is required")

        if not plugin.author:
            errors.append("Plugin author is required")

        if not plugin.description:
            errors.append("Plugin description is required")

        return errors
