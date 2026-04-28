"""
Dependency injection container - infrastructure for composing applications.

Consolidated DI container with features from adapter-kit and pheno.adapters:
- Auto-wiring via type hints
- Lifecycle management (singleton, transient, scoped)
- Circular dependency detection
- Constructor injection

This is an adapter implementation for dependency injection. The domain
(layer above) doesn't know about this concrete implementation - it only
knows about ports and the composition happens in the app layer.
"""

import inspect
import logging
from collections.abc import Callable
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Lifecycle(Enum):
    """
    Service lifecycle strategies.
    """

    SINGLETON = "singleton"  # One instance for the lifetime of the container
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"  # One instance per scope


class ServiceDefinition:
    """
    Definition of a service in the container.
    """

    def __init__(self, factory: Callable, lifecycle: Lifecycle = Lifecycle.TRANSIENT):
        self.factory = factory
        self.lifecycle = lifecycle
        self._instance: Any | None = None
        self._id = id(self)  # Unique ID for hashing

    def __hash__(self):
        """
        Make ServiceDefinition hashable for use in scope dictionaries.
        """
        return self._id

    def __eq__(self, other):
        """
        Equality based on identity.
        """
        return isinstance(other, ServiceDefinition) and self._id == other._id

    def get_instance(self, container, scope=None):
        """
        Get service instance based on lifecycle.
        """
        if self.lifecycle == Lifecycle.SINGLETON:
            if self._instance is None:
                self._instance = self.factory(container)
            return self._instance
        if self.lifecycle == Lifecycle.SCOPED:
            if scope is None:
                raise ValueError("Scoped service requires a scope")
            return scope.get_or_create(self, container)
        # TRANSIENT
        return self.factory(container)


class Scope:
    """
    Scope for scoped service instances.
    """

    def __init__(self):
        self._instances: dict[ServiceDefinition, Any] = {}

    def get_or_create(self, definition: ServiceDefinition, container):
        """
        Get or create instance for this scope.
        """
        if definition not in self._instances:
            self._instances[definition] = definition.factory(container)
        return self._instances[definition]

    def clear(self):
        """
        Clear all scoped instances.
        """
        self._instances.clear()


class Container:
    """Dependency injection container with auto-wiring.

    Features:
    - Auto-wiring via type hints
    - Lifecycle management (singleton, transient, scoped)
    - Circular dependency detection
    - Constructor injection
    - Named services and aliases

    Example:
        >>> container = Container()
        >>> container.register(IDatabase, PostgresDatabase, lifecycle=Lifecycle.SINGLETON)
        >>> container.register(IService, UserService, lifecycle=Lifecycle.TRANSIENT)
        >>> service = container.resolve(IService)  # Auto-wires PostgresDatabase
    """

    def __init__(self):
        self._services: dict[str, ServiceDefinition] = {}
        self._aliases: dict[str, str] = {}
        self._resolving: set[str] = set()  # For circular dependency detection
        self._current_scope: Scope | None = None

    def register(
        self,
        service_type: type,
        implementation: type | Callable,
        lifecycle: Lifecycle = Lifecycle.TRANSIENT,
        name: str | None = None,
    ):
        """Register a service with the container.

        Args:
            service_type: The type/interface this service implements
            implementation: Concrete implementation class or factory function
            lifecycle: Service lifecycle (SINGLETON, TRANSIENT, SCOPED)
            name: Optional name for the service

        Example:
            >>> container.register(IDatabase, PostgresDatabase, Lifecycle.SINGLETON)
            >>> container.register(ICache, lambda c: RedisCache(host="localhost"))
        """
        if name is None:
            name = service_type.__name__

        # Create factory with auto-wiring
        if inspect.isclass(implementation):
            factory = self._create_auto_wiring_factory(implementation)
        else:
            factory = implementation

        self._services[name] = ServiceDefinition(factory=factory, lifecycle=lifecycle)

        # Auto-register under type name
        type_name = service_type.__name__
        if type_name not in self._services:
            self._aliases[type_name] = name

    def _create_auto_wiring_factory(self, implementation_class: type) -> Callable:
        """
        Create a factory that auto-wires constructor dependencies.
        """

        def factory(container):
            # Get constructor signature
            sig = inspect.signature(implementation_class.__init__)
            params = {}

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                # Try to resolve by type hint
                if param.annotation != inspect.Parameter.empty:
                    annotation = param.annotation

                    # Handle forward references (strings)
                    if isinstance(annotation, str):
                        # Skip forward references - can't auto-wire them
                        if param.default != inspect.Parameter.empty:
                            params[param_name] = param.default
                        else:
                            logger.warning(
                                f"Cannot auto-wire forward reference '{annotation}' "
                                f"for parameter '{param_name}' in {implementation_class.__name__}",
                            )
                        continue

                    try:
                        params[param_name] = container.resolve(annotation)
                    except ValueError:
                        # If resolution fails and there's a default, use it
                        if param.default != inspect.Parameter.empty:
                            params[param_name] = param.default
                        else:
                            raise ValueError(
                                f"Cannot auto-wire parameter '{param_name}' "
                                f"of type {annotation} for {implementation_class.__name__}",
                            )
                elif param.default != inspect.Parameter.empty:
                    params[param_name] = param.default

            return implementation_class(**params)

        return factory

    def register_singleton(self, service_type: type, instance: Any):
        """Register a pre-created singleton instance.

        Args:
            service_type: The type/interface
            instance: Pre-created instance

        Example:
            >>> db = PostgresDatabase(connection_string)
            >>> container.register_singleton(IDatabase, db)
        """
        name = service_type.__name__
        self._services[name] = ServiceDefinition(
            factory=lambda _: instance, lifecycle=Lifecycle.SINGLETON,
        )
        self._services[name]._instance = instance

    def resolve(self, service_type: type, name: str | None = None):
        """Resolve a service instance with auto-wiring and circular dependency
        detection.

        Args:
            service_type: The type/interface to resolve
            name: Optional name if multiple implementations exist

        Returns:
            Service instance with dependencies auto-wired

        Raises:
            ValueError: If service not registered or circular dependency detected

        Example:
            >>> service = container.resolve(IUserService)
        """
        if name is None:
            name = service_type.__name__

        # Check aliases
        if name in self._aliases:
            name = self._aliases[name]

        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")

        # Circular dependency detection
        if name in self._resolving:
            raise ValueError(
                f"Circular dependency detected: {name} is already being resolved. "
                f"Resolution chain: {' -> '.join(self._resolving)} -> {name}",
            )

        try:
            self._resolving.add(name)
            definition = self._services[name]
            return definition.get_instance(self, self._current_scope)
        finally:
            self._resolving.discard(name)

    def has_service(self, service_type: type, name: str | None = None) -> bool:
        """Check if a service is registered.

        Args:
            service_type: The type/interface to check
            name: Optional name

        Returns:
            True if service is registered
        """
        if name is None:
            name = service_type.__name__

        if name in self._aliases:
            name = self._aliases[name]

        return name in self._services

    def list_services(self) -> set[str]:
        """
        List all registered service names.
        """
        return set(self._services.keys()) | set(self._aliases.keys())

    def create_scope(self) -> Scope:
        """Create a new scope for scoped services.

        Returns:
            New scope instance

        Example:
            >>> with container.create_scope() as scope:
            >>>     container.set_scope(scope)
            >>>     service = container.resolve(IScopedService)
        """
        return Scope()

    def set_scope(self, scope: Scope | None):
        """
        Set the current scope for scoped service resolution.
        """
        self._current_scope = scope

    def clear(self):
        """
        Clear all registered services and reset state.
        """
        self._services.clear()
        self._aliases.clear()
        self._resolving.clear()
        self._current_scope = None


# Global container instance (can be overridden in tests)
_container = Container()


def get_container() -> Container:
    """Get the global dependency container.

    Returns:
        Global container instance

    Example:
        >>> container = get_container()
        >>> container.register(IService, ServiceImpl)
    """
    return _container


def set_container(container: Container):
    """Set the global dependency container (useful for testing).

    Args:
        container: Container instance to set as global

    Example:
        >>> test_container = Container()
        >>> set_container(test_container)
    """
    global _container
    _container = container


def reset_container():
    """
    Reset the global container to a fresh instance.
    """
    global _container
    _container = Container()


# Backward compatibility aliases
DependencyContainer = Container  # For existing code using DependencyContainer


__all__ = [
    "Container",
    "DependencyContainer",  # Backward compatibility
    "Lifecycle",
    "Scope",
    "ServiceDefinition",
    "get_container",
    "reset_container",
    "set_container",
]
