"""
Repository port definitions.
"""

from typing import Generic, Protocol, TypeVar

from pheno.domain.entities import Configuration, Deployment, Service, User
from pheno.domain.value_objects import (
    ConfigKey,
    DeploymentId,
    Email,
    ServiceId,
    ServiceName,
    UserId,
)

# Generic type variable for entities
T = TypeVar("T")


class Repository(Protocol, Generic[T]):
    """Generic repository protocol.

    Defines the contract for data persistence operations. All repositories should
    implement this interface.
    """

    async def save(self, entity: T) -> None:
        """Save an entity.

        Args:
            entity: Entity to save

        Raises:
            RepositoryError: If save operation fails
        """
        ...

    async def find_by_id(self, entity_id: str) -> T | None:
        """Find entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity if found, None otherwise

        Raises:
            RepositoryError: If find operation fails
        """
        ...

    async def delete(self, entity_id: str) -> None:
        """Delete an entity.

        Args:
            entity_id: Entity identifier

        Raises:
            EntityNotFoundError: If entity doesn't exist
            RepositoryError: If delete operation fails
        """
        ...

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Find all entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities

        Raises:
            RepositoryError: If find operation fails
        """
        ...


class UserRepository(Protocol):
    """User repository protocol.

    Defines the contract for user persistence operations.
    """

    async def save(self, user: User) -> None:
        """
        Save a user.
        """
        ...

    async def find_by_id(self, user_id: UserId) -> User | None:
        """
        Find user by ID.
        """
        ...

    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email.

        Args:
            email: User email address

        Returns:
            User if found, None otherwise
        """
        ...

    async def delete(self, user_id: UserId) -> None:
        """
        Delete a user.
        """
        ...

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
    ) -> list[User]:
        """Find all users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            active_only: If True, return only active users

        Returns:
            List of users
        """
        ...

    async def count(self, active_only: bool = False) -> int:
        """Count total users.

        Args:
            active_only: If True, count only active users

        Returns:
            Total number of users
        """
        ...


class DeploymentRepository(Protocol):
    """Deployment repository protocol.

    Defines the contract for deployment persistence operations.
    """

    async def save(self, deployment: Deployment) -> None:
        """
        Save a deployment.
        """
        ...

    async def find_by_id(self, deployment_id: DeploymentId) -> Deployment | None:
        """
        Find deployment by ID.
        """
        ...

    async def delete(self, deployment_id: DeploymentId) -> None:
        """
        Delete a deployment.
        """
        ...

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        environment: str | None = None,
        status: str | None = None,
    ) -> list[Deployment]:
        """Find all deployments with pagination and filtering.

        Args:
            limit: Maximum number of deployments to return
            offset: Number of deployments to skip
            environment: Filter by environment (optional)
            status: Filter by status (optional)

        Returns:
            List of deployments
        """
        ...

    async def find_active(self) -> list[Deployment]:
        """Find all active deployments.

        Returns:
            List of active deployments
        """
        ...

    async def count(
        self,
        environment: str | None = None,
        status: str | None = None,
    ) -> int:
        """Count total deployments.

        Args:
            environment: Filter by environment (optional)
            status: Filter by status (optional)

        Returns:
            Total number of deployments
        """
        ...


class ServiceRepository(Protocol):
    """Service repository protocol.

    Defines the contract for service persistence operations.
    """

    async def save(self, service: Service) -> None:
        """
        Save a service.
        """
        ...

    async def find_by_id(self, service_id: ServiceId) -> Service | None:
        """
        Find service by ID.
        """
        ...

    async def find_by_name(self, name: ServiceName) -> Service | None:
        """Find service by name.

        Args:
            name: Service name

        Returns:
            Service if found, None otherwise
        """
        ...

    async def delete(self, service_id: ServiceId) -> None:
        """
        Delete a service.
        """
        ...

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
    ) -> list[Service]:
        """Find all services with pagination and filtering.

        Args:
            limit: Maximum number of services to return
            offset: Number of services to skip
            status: Filter by status (optional)

        Returns:
            List of services
        """
        ...

    async def find_running(self) -> list[Service]:
        """Find all running services.

        Returns:
            List of running services
        """
        ...

    async def count(self, status: str | None = None) -> int:
        """Count total services.

        Args:
            status: Filter by status (optional)

        Returns:
            Total number of services
        """
        ...


class ConfigurationRepository(Protocol):
    """Configuration repository protocol.

    Defines the contract for configuration persistence operations.
    """

    async def save(self, config: Configuration) -> None:
        """
        Save a configuration.
        """
        ...

    async def find_by_key(self, key: ConfigKey) -> Configuration | None:
        """Find configuration by key.

        Args:
            key: Configuration key

        Returns:
            Configuration if found, None otherwise
        """
        ...

    async def delete(self, key: ConfigKey) -> None:
        """
        Delete a configuration.
        """
        ...

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        namespace: str | None = None,
    ) -> list[Configuration]:
        """Find all configurations with pagination and filtering.

        Args:
            limit: Maximum number of configurations to return
            offset: Number of configurations to skip
            namespace: Filter by namespace (optional)

        Returns:
            List of configurations
        """
        ...

    async def find_by_namespace(self, namespace: str) -> list[Configuration]:
        """Find all configurations in a namespace.

        Args:
            namespace: Configuration namespace

        Returns:
            List of configurations in the namespace
        """
        ...

    async def count(self, namespace: str | None = None) -> int:
        """Count total configurations.

        Args:
            namespace: Filter by namespace (optional)

        Returns:
            Total number of configurations
        """
        ...
