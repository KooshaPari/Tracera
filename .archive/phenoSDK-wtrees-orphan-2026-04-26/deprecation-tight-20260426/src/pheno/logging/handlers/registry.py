"""Handler registry for managing log handlers.

This module provides a centralized registry for all log handlers, making it easy to
register, discover, and create handlers.
"""

from typing import Any

from ..core.interfaces import LogHandler
from ..core.types import ConfigurationError


class HandlerRegistry:
    """
    Central registry for log handlers.
    """

    def __init__(self):
        self._handlers: dict[str, type[LogHandler]] = {}
        self._instances: dict[str, LogHandler] = {}

    def register_handler(self, name: str, handler_class: type[LogHandler]) -> None:
        """Register a handler class.

        Args:
            name: Handler name
            handler_class: Handler class to register
        """
        if not issubclass(handler_class, LogHandler):
            raise ValueError("Handler class must inherit from LogHandler")

        self._handlers[name] = handler_class

    def get_handler_class(self, name: str) -> type[LogHandler] | None:
        """Get a handler class by name.

        Args:
            name: Handler name

        Returns:
            Handler class or None if not found
        """
        return self._handlers.get(name)

    def create_handler(self, name: str, config: dict[str, Any]) -> LogHandler:
        """Create a handler instance.

        Args:
            name: Handler name
            config: Handler configuration

        Returns:
            Handler instance

        Raises:
            ConfigurationError: If handler not found or creation fails
        """
        handler_class = self.get_handler_class(name)
        if not handler_class:
            raise ConfigurationError(f"Handler '{name}' not found")

        try:
            return handler_class(name, config)
        except Exception as e:
            raise ConfigurationError(f"Failed to create handler '{name}': {e}")

    def get_or_create_handler(self, name: str, config: dict[str, Any]) -> LogHandler:
        """Get existing handler instance or create new one.

        Args:
            name: Handler name
            config: Handler configuration

        Returns:
            Handler instance
        """
        instance_key = f"{name}:{id(config)}"

        if instance_key not in self._instances:
            self._instances[instance_key] = self.create_handler(name, config)

        return self._instances[instance_key]

    def list_handlers(self) -> list[str]:
        """List all registered handler names.

        Returns:
            List of handler names
        """
        return list(self._handlers.keys())

    def unregister_handler(self, name: str) -> None:
        """Unregister a handler.

        Args:
            name: Handler name to unregister
        """
        if name in self._handlers:
            del self._handlers[name]

        # Remove any instances of this handler
        keys_to_remove = [k for k in self._instances if k.startswith(f"{name}:")]
        for key in keys_to_remove:
            del self._instances[key]

    def clear(self) -> None:
        """
        Clear all registered handlers and instances.
        """
        self._handlers.clear()
        self._instances.clear()


# Global registry instance
_global_registry = HandlerRegistry()


def get_registry() -> HandlerRegistry:
    """
    Get the global handler registry.
    """
    return _global_registry


def register_handler(name: str, handler_class: type[LogHandler]) -> None:
    """
    Register a handler with the global registry.
    """
    _global_registry.register_handler(name, handler_class)


def create_handler(name: str, config: dict[str, Any]) -> LogHandler:
    """
    Create a handler using the global registry.
    """
    return _global_registry.create_handler(name, config)
