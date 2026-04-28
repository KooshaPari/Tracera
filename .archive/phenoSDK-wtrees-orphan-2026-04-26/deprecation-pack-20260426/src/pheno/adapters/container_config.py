"""Container configuration for Pheno SDK hexagonal architecture.

This module configures the DI container with all necessary adapters, repositories, and
use cases for the hexagonal architecture.
"""

from __future__ import annotations

from pheno.adapters.cli.adapter import CLIAdapter
from pheno.adapters.cli.commands import (
    ConfigurationCommands,
    DeploymentCommands,
    ServiceCommands,
    UserCommands,
)
from pheno.adapters.container import Container, Lifecycle
from pheno.adapters.events.memory_publisher import InMemoryEventPublisher
from pheno.adapters.persistence.memory import (
    InMemoryConfigurationRepository,
    InMemoryDeploymentRepository,
    InMemoryServiceRepository,
    InMemoryUserRepository,
)
from pheno.application.ports.events import EventPublisher
from pheno.application.ports.repositories import (
    ConfigurationRepository,
    DeploymentRepository,
    ServiceRepository,
    UserRepository,
)


def configure_in_memory_container() -> Container:
    """Configure container with in-memory implementations.

    This is useful for testing and development.

    Returns:
        Configured container with in-memory implementations
    """
    container = Container()

    # Register repositories as singletons
    container.register(
        UserRepository,
        InMemoryUserRepository,
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        DeploymentRepository,
        InMemoryDeploymentRepository,
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ServiceRepository,
        InMemoryServiceRepository,
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ConfigurationRepository,
        InMemoryConfigurationRepository,
        lifecycle=Lifecycle.SINGLETON,
    )

    # Register event publisher as singleton
    container.register(
        EventPublisher,
        InMemoryEventPublisher,
        lifecycle=Lifecycle.SINGLETON,
    )

    # Register CLI adapter (auto-wired with dependencies)
    container.register(
        CLIAdapter,
        lambda: CLIAdapter(
            user_repository=container.resolve(UserRepository),
            deployment_repository=container.resolve(DeploymentRepository),
            service_repository=container.resolve(ServiceRepository),
            configuration_repository=container.resolve(ConfigurationRepository),
            event_publisher=container.resolve(EventPublisher),
        ),
        lifecycle=Lifecycle.SINGLETON,
    )

    # Register CLI command handlers
    container.register(
        UserCommands,
        lambda: UserCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        DeploymentCommands,
        lambda: DeploymentCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ServiceCommands,
        lambda: ServiceCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ConfigurationCommands,
        lambda: ConfigurationCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )

    return container


def configure_production_container(
    user_repo: UserRepository | None = None,
    deployment_repo: DeploymentRepository | None = None,
    service_repo: ServiceRepository | None = None,
    config_repo: ConfigurationRepository | None = None,
    event_publisher: EventPublisher | None = None,
) -> Container:
    """Configure container with production implementations.

    Args:
        user_repo: User repository implementation (defaults to in-memory)
        deployment_repo: Deployment repository implementation (defaults to in-memory)
        service_repo: Service repository implementation (defaults to in-memory)
        config_repo: Configuration repository implementation (defaults to in-memory)
        event_publisher: Event publisher implementation (defaults to in-memory)

    Returns:
        Configured container with production implementations
    """
    container = Container()

    # Register repositories (use provided or default to in-memory)
    container.register(
        UserRepository,
        lambda: user_repo or InMemoryUserRepository(),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        DeploymentRepository,
        lambda: deployment_repo or InMemoryDeploymentRepository(),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ServiceRepository,
        lambda: service_repo or InMemoryServiceRepository(),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ConfigurationRepository,
        lambda: config_repo or InMemoryConfigurationRepository(),
        lifecycle=Lifecycle.SINGLETON,
    )

    # Register event publisher
    container.register(
        EventPublisher,
        lambda: event_publisher or InMemoryEventPublisher(),
        lifecycle=Lifecycle.SINGLETON,
    )

    # Register CLI adapter
    container.register(
        CLIAdapter,
        lambda: CLIAdapter(
            user_repository=container.resolve(UserRepository),
            deployment_repository=container.resolve(DeploymentRepository),
            service_repository=container.resolve(ServiceRepository),
            configuration_repository=container.resolve(ConfigurationRepository),
            event_publisher=container.resolve(EventPublisher),
        ),
        lifecycle=Lifecycle.SINGLETON,
    )

    # Register CLI command handlers
    container.register(
        UserCommands,
        lambda: UserCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        DeploymentCommands,
        lambda: DeploymentCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ServiceCommands,
        lambda: ServiceCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )
    container.register(
        ConfigurationCommands,
        lambda: ConfigurationCommands(container.resolve(CLIAdapter)),
        lifecycle=Lifecycle.SINGLETON,
    )

    return container


# Global container instance
_global_container: Container | None = None


def get_container() -> Container:
    """Get the global container instance.

    Creates a default in-memory container if none exists.

    Returns:
        The global container
    """
    global _global_container
    if _global_container is None:
        _global_container = configure_in_memory_container()
    return _global_container


def set_container(container: Container) -> None:
    """Set the global container instance.

    Args:
        container: The container to use globally
    """
    global _global_container
    _global_container = container


def reset_container() -> None:
    """
    Reset the global container.
    """
    global _global_container
    _global_container = None
