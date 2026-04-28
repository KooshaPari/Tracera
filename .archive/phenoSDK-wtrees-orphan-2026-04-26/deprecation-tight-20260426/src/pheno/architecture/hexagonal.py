"""
Hexagonal Architecture (Ports and Adapters) implementation.
"""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    Any,
    TypeVar,
)

from pheno.logging.core.logger import get_logger

logger = get_logger("pheno.architecture.hexagonal")

T = TypeVar("T")


class HexagonalError(Exception):
    """
    Base exception for hexagonal architecture errors.
    """



class PortNotFoundError(HexagonalError):
    """
    Raised when a port is not found.
    """



class AdapterNotFoundError(HexagonalError):
    """
    Raised when an adapter is not found.
    """



class ServiceNotFoundError(HexagonalError):
    """
    Raised when a service is not found.
    """



class CircularDependencyError(HexagonalError):
    """
    Raised when circular dependency is detected.
    """



@dataclass(slots=True)
class ServiceConfig:
    """
    Configuration for a service.
    """

    service_type: type
    implementation: Any
    singleton: bool = True
    dependencies: list[type] = field(default_factory=list)
    name: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class HexagonalConfig:
    """
    Configuration for hexagonal architecture.
    """

    enable_validation: bool = True
    enable_circular_dependency_check: bool = True
    auto_wire: bool = True
    strict_mode: bool = False


class Port(ABC):
    """
    Abstract base class for ports (interfaces).
    """

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """
        Port interface method.
        """


class Adapter(ABC):
    """
    Abstract base class for adapters.
    """

    def __init__(self, port: Port):
        self.port = port

    @abstractmethod
    def adapt(self, *args, **kwargs) -> Any:
        """
        Adapt external interface to port.
        """


class UseCase(ABC):
    """
    Abstract base class for use cases.
    """

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute use case.
        """


class DomainService(ABC):
    """
    Abstract base class for domain services.
    """

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """
        Process domain logic.
        """


class ApplicationService(ABC):
    """
    Abstract base class for application services.
    """

    @abstractmethod
    def handle(self, *args, **kwargs) -> Any:
        """
        Handle application logic.
        """


class ServiceRegistry:
    """
    Registry for managing services.
    """

    def __init__(self):
        self._services: dict[type, ServiceConfig] = {}
        self._instances: dict[type, Any] = {}
        self._by_name: dict[str, type] = {}
        self._by_tag: dict[str, list[type]] = defaultdict(list)

    def register(
        self,
        service_type: type,
        implementation: Any,
        singleton: bool = True,
        name: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """
        Register a service.
        """
        if tags is None:
            tags = []

        # Get dependencies from type hints
        dependencies = self._get_dependencies(implementation)

        config = ServiceConfig(
            service_type=service_type,
            implementation=implementation,
            singleton=singleton,
            dependencies=dependencies,
            name=name,
            tags=tags,
        )

        self._services[service_type] = config

        if name:
            self._by_name[name] = service_type

        for tag in tags:
            self._by_tag[tag].append(service_type)

        logger.debug(f"Registered service: {service_type.__name__}")

    def register_instance(
        self, service_type: type, instance: Any, name: str | None = None, tags: list[str] | None = None,
    ) -> None:
        """
        Register a service instance.
        """
        if tags is None:
            tags = []

        config = ServiceConfig(
            service_type=service_type,
            implementation=instance,
            singleton=True,
            dependencies=[],
            name=name,
            tags=tags,
        )

        self._services[service_type] = config
        self._instances[service_type] = instance

        if name:
            self._by_name[name] = service_type

        for tag in tags:
            self._by_tag[tag].append(service_type)

        logger.debug(f"Registered service instance: {service_type.__name__}")

    def get(self, service_type: type) -> Any:
        """
        Get service instance.
        """
        if service_type not in self._services:
            raise ServiceNotFoundError(f"Service {service_type.__name__} not found")

        config = self._services[service_type]

        # Return existing instance if singleton
        if config.singleton and service_type in self._instances:
            return self._instances[service_type]

        # Create new instance
        instance = self._create_instance(service_type, config)

        # Store instance if singleton
        if config.singleton:
            self._instances[service_type] = instance

        return instance

    def get_by_name(self, name: str) -> Any:
        """
        Get service by name.
        """
        if name not in self._by_name:
            raise ServiceNotFoundError(f"Service with name '{name}' not found")

        service_type = self._by_name[name]
        return self.get(service_type)

    def get_by_tag(self, tag: str) -> list[Any]:
        """
        Get services by tag.
        """
        if tag not in self._by_tag:
            return []

        return [self.get(service_type) for service_type in self._by_tag[tag]]

    def _create_instance(self, service_type: type, config: ServiceConfig) -> Any:
        """
        Create service instance.
        """
        if config.singleton and service_type in self._instances:
            return self._instances[service_type]

        # Resolve dependencies
        dependencies = {}
        for dep_type in config.dependencies:
            dependencies[dep_type] = self.get(dep_type)

        # Create instance
        if inspect.isclass(config.implementation):
            # Class - instantiate with dependencies
            sig = inspect.signature(config.implementation.__init__)
            params = {}

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                param_type = param.annotation
                if param_type in dependencies:
                    params[param_name] = dependencies[param_type]

            instance = config.implementation(**params)
        else:
            # Instance or callable
            instance = config.implementation

        return instance

    def _get_dependencies(self, implementation: Any) -> list[type]:
        """
        Get dependencies from type hints.
        """
        dependencies = []

        if inspect.isclass(implementation):
            sig = inspect.signature(implementation.__init__)
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                param_type = param.annotation
                if param_type != inspect.Parameter.empty:
                    dependencies.append(param_type)

        return dependencies

    def is_registered(self, service_type: type) -> bool:
        """
        Check if service is registered.
        """
        return service_type in self._services

    def unregister(self, service_type: type) -> bool:
        """
        Unregister service.
        """
        if service_type not in self._services:
            return False

        config = self._services[service_type]

        # Remove from registries
        del self._services[service_type]

        if service_type in self._instances:
            del self._instances[service_type]

        # Remove from name registry
        if config.name and config.name in self._by_name:
            del self._by_name[config.name]

        # Remove from tag registry
        for tag in config.tags:
            if tag in self._by_tag and service_type in self._by_tag[tag]:
                self._by_tag[tag].remove(service_type)

        logger.debug(f"Unregistered service: {service_type.__name__}")
        return True


class DIContainer:
    """
    Dependency injection container.
    """

    def __init__(self, config: HexagonalConfig | None = None):
        self.config = config or HexagonalConfig()
        self.registry = ServiceRegistry()
        self._validation_cache: dict[type, bool] = {}

    def register(
        self,
        service_type: type,
        implementation: Any,
        singleton: bool = True,
        name: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """
        Register a service.
        """
        self.registry.register(service_type, implementation, singleton, name, tags)

        if self.config.auto_wire:
            self._auto_wire_dependencies(service_type)

    def register_instance(
        self, service_type: type, instance: Any, name: str | None = None, tags: list[str] | None = None,
    ) -> None:
        """
        Register a service instance.
        """
        self.registry.register_instance(service_type, instance, name, tags)

    def get(self, service_type: type) -> Any:
        """
        Get service instance.
        """
        if self.config.enable_validation:
            self._validate_service(service_type)

        return self.registry.get(service_type)

    def get_by_name(self, name: str) -> Any:
        """
        Get service by name.
        """
        return self.registry.get_by_name(name)

    def get_by_tag(self, tag: str) -> list[Any]:
        """
        Get services by tag.
        """
        return self.registry.get_by_tag(tag)

    def _auto_wire_dependencies(self, service_type: type) -> None:
        """
        Auto-wire dependencies for a service.
        """
        if service_type in self._validation_cache:
            return

        try:
            # Get service config
            if service_type not in self.registry._services:
                return

            config = self.registry._services[service_type]

            # Check if all dependencies are registered
            for dep_type in config.dependencies:
                if not self.registry.is_registered(dep_type):
                    logger.warning(
                        f"Dependency {dep_type.__name__} not registered for {service_type.__name__}",
                    )

            self._validation_cache[service_type] = True

        except Exception as e:
            logger.exception(f"Auto-wiring failed for {service_type.__name__}: {e}")

    def _validate_service(self, service_type: type) -> None:
        """
        Validate service and its dependencies.
        """
        if service_type in self._validation_cache:
            return

        if self.config.enable_circular_dependency_check:
            self._check_circular_dependencies(service_type, set())

        self._validation_cache[service_type] = True

    def _check_circular_dependencies(self, service_type: type, visited: set) -> None:
        """
        Check for circular dependencies.
        """
        if service_type in visited:
            raise CircularDependencyError(f"Circular dependency detected: {service_type.__name__}")

        if service_type not in self.registry._services:
            return

        visited.add(service_type)

        config = self.registry._services[service_type]
        for dep_type in config.dependencies:
            self._check_circular_dependencies(dep_type, visited.copy())

    def create_scope(self) -> DIContainer:
        """
        Create a new scope with fresh instances.
        """
        new_container = DIContainer(self.config)
        new_container.registry = self.registry
        return new_container


class PortRegistry:
    """
    Registry for ports.
    """

    def __init__(self):
        self._ports: dict[str, Port] = {}

    def register(self, name: str, port: Port) -> None:
        """
        Register a port.
        """
        self._ports[name] = port
        logger.debug(f"Registered port: {name}")

    def get(self, name: str) -> Port:
        """
        Get port by name.
        """
        if name not in self._ports:
            raise PortNotFoundError(f"Port '{name}' not found")
        return self._ports[name]

    def unregister(self, name: str) -> bool:
        """
        Unregister port.
        """
        if name in self._ports:
            del self._ports[name]
            logger.debug(f"Unregistered port: {name}")
            return True
        return False


class AdapterRegistry:
    """
    Registry for adapters.
    """

    def __init__(self):
        self._adapters: dict[str, Adapter] = {}
        self._port_adapters: dict[str, list[str]] = defaultdict(list)

    def register(self, name: str, adapter: Adapter, port_name: str) -> None:
        """
        Register an adapter.
        """
        self._adapters[name] = adapter
        self._port_adapters[port_name].append(name)
        logger.debug(f"Registered adapter: {name} for port: {port_name}")

    def get(self, name: str) -> Adapter:
        """
        Get adapter by name.
        """
        if name not in self._adapters:
            raise AdapterNotFoundError(f"Adapter '{name}' not found")
        return self._adapters[name]

    def get_by_port(self, port_name: str) -> list[Adapter]:
        """
        Get adapters by port name.
        """
        if port_name not in self._port_adapters:
            return []

        return [self._adapters[name] for name in self._port_adapters[port_name]]

    def unregister(self, name: str) -> bool:
        """
        Unregister adapter.
        """
        if name in self._adapters:
            self._adapters[name]
            del self._adapters[name]

            # Remove from port mapping
            for adapter_names in self._port_adapters.values():
                if name in adapter_names:
                    adapter_names.remove(name)

            logger.debug(f"Unregistered adapter: {name}")
            return True
        return False


class PortAdapter:
    """
    Port-adapter connector.
    """

    def __init__(self, port_registry: PortRegistry, adapter_registry: AdapterRegistry):
        self.port_registry = port_registry
        self.adapter_registry = adapter_registry
        self._connections: dict[str, str] = {}  # port_name -> adapter_name

    def connect(self, port_name: str, adapter_name: str) -> None:
        """
        Connect a port to an adapter.
        """
        # Validate port exists
        self.port_registry.get(port_name)

        # Validate adapter exists
        self.adapter_registry.get(adapter_name)

        self._connections[port_name] = adapter_name
        logger.debug(f"Connected port '{port_name}' to adapter '{adapter_name}'")

    def disconnect(self, port_name: str) -> bool:
        """
        Disconnect a port from its adapter.
        """
        if port_name in self._connections:
            del self._connections[port_name]
            logger.debug(f"Disconnected port '{port_name}'")
            return True
        return False

    def get_adapter_for_port(self, port_name: str) -> Adapter | None:
        """
        Get adapter connected to a port.
        """
        if port_name not in self._connections:
            return None

        adapter_name = self._connections[port_name]
        return self.adapter_registry.get(adapter_name)

    def call_port(self, port_name: str, *args, **kwargs) -> Any:
        """
        Call a port through its connected adapter.
        """
        adapter = self.get_adapter_for_port(port_name)
        if not adapter:
            raise PortNotFoundError(f"No adapter connected to port '{port_name}'")

        return adapter.adapt(*args, **kwargs)


class ServiceProvider:
    """
    Service provider for hexagonal architecture.
    """

    def __init__(self, container: DIContainer, port_adapter: PortAdapter):
        self.container = container
        self.port_adapter = port_adapter

    def get_service(self, service_type: type) -> Any:
        """
        Get service from container.
        """
        return self.container.get(service_type)

    def get_port(self, port_name: str) -> Port:
        """
        Get port from registry.
        """
        return self.port_adapter.port_registry.get(port_name)

    def call_port(self, port_name: str, *args, **kwargs) -> Any:
        """
        Call port through adapter.
        """
        return self.port_adapter.call_port(port_name, *args, **kwargs)

    def get_adapters_for_port(self, port_name: str) -> list[Adapter]:
        """
        Get all adapters for a port.
        """
        return self.port_adapter.adapter_registry.get_by_port(port_name)
