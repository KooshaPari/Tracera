"""Pheno Architecture Module.

This module provides architectural patterns and frameworks.
It consolidates generic architectural patterns that can be used across all projects in the Pheno ecosystem.

Key Features:
- Hexagonal Architecture (Ports and Adapters)
- Clean Architecture patterns
- Dependency Injection container
- Domain-driven design support
- Architectural validation
"""

from .hexagonal import (  # Core hexagonal architecture; Dependency injection; Ports and adapters; Configuration; Exceptions
    Adapter,
    AdapterNotFoundError,
    AdapterRegistry,
    ApplicationService,
    CircularDependencyError,
    DIContainer,
    DomainService,
    HexagonalConfig,
    HexagonalError,
    Port,
    PortAdapter,
    PortNotFoundError,
    PortRegistry,
    ServiceConfig,
    ServiceNotFoundError,
    ServiceProvider,
    ServiceRegistry,
    UseCase,
)

__all__ = [
    "Adapter",
    "AdapterNotFoundError",
    "AdapterRegistry",
    "ApplicationService",
    "CircularDependencyError",
    # Dependency injection
    "DIContainer",
    "DomainService",
    # Configuration
    "HexagonalConfig",
    # Exceptions
    "HexagonalError",
    # Core hexagonal architecture
    "Port",
    "PortAdapter",
    "PortNotFoundError",
    # Ports and adapters
    "PortRegistry",
    "ServiceConfig",
    "ServiceNotFoundError",
    "ServiceProvider",
    "ServiceRegistry",
    "UseCase",
]

__version__ = "1.0.0"
