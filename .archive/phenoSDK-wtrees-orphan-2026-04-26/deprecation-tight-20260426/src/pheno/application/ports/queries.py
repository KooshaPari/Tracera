"""
Query port definitions for CQRS pattern.
"""

from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

# Generic type variable for query results
TResult = TypeVar("TResult")


class QueryHandler(Protocol, Generic[TResult]):
    """Generic query handler protocol.

    Defines the contract for handling queries in CQRS pattern. Queries are read-only
    operations that return data.
    """

    async def handle(self, query: Any) -> TResult:
        """Handle a query.

        Args:
            query: Query object

        Returns:
            Query result

        Raises:
            QueryHandlerError: If query handling fails
        """
        ...


@dataclass(frozen=True)
class UserQueryFilter:
    """
    Filter criteria for user queries.
    """

    email: str | None = None
    name: str | None = None
    is_active: bool | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class UserQueryResult:
    """
    Result of a user query.
    """

    id: str
    email: str
    name: str
    is_active: bool
    created_at: str
    updated_at: str


class UserQuery(Protocol):
    """User query protocol.

    Defines the contract for querying user data. Optimized for read operations with
    denormalized data.
    """

    async def find_by_id(self, user_id: str) -> UserQueryResult | None:
        """Find user by ID.

        Args:
            user_id: User identifier

        Returns:
            User query result if found, None otherwise
        """
        ...

    async def find_by_email(self, email: str) -> UserQueryResult | None:
        """Find user by email.

        Args:
            email: User email address

        Returns:
            User query result if found, None otherwise
        """
        ...

    async def find_all(self, filter: UserQueryFilter) -> list[UserQueryResult]:
        """Find all users matching filter criteria.

        Args:
            filter: Query filter criteria

        Returns:
            List of user query results
        """
        ...

    async def count(self, filter: UserQueryFilter) -> int:
        """Count users matching filter criteria.

        Args:
            filter: Query filter criteria

        Returns:
            Total count
        """
        ...


@dataclass(frozen=True)
class DeploymentQueryFilter:
    """
    Filter criteria for deployment queries.
    """

    environment: str | None = None
    status: str | None = None
    strategy: str | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class DeploymentQueryResult:
    """
    Result of a deployment query.
    """

    id: str
    environment: str
    strategy: str
    status: str
    created_at: str
    updated_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None


class DeploymentQuery(Protocol):
    """Deployment query protocol.

    Defines the contract for querying deployment data.
    """

    async def find_by_id(self, deployment_id: str) -> DeploymentQueryResult | None:
        """Find deployment by ID.

        Args:
            deployment_id: Deployment identifier

        Returns:
            Deployment query result if found, None otherwise
        """
        ...

    async def find_all(
        self,
        filter: DeploymentQueryFilter,
    ) -> list[DeploymentQueryResult]:
        """Find all deployments matching filter criteria.

        Args:
            filter: Query filter criteria

        Returns:
            List of deployment query results
        """
        ...

    async def find_active(self) -> list[DeploymentQueryResult]:
        """Find all active deployments.

        Returns:
            List of active deployment query results
        """
        ...

    async def count(self, filter: DeploymentQueryFilter) -> int:
        """Count deployments matching filter criteria.

        Args:
            filter: Query filter criteria

        Returns:
            Total count
        """
        ...

    async def get_statistics(
        self,
        environment: str | None = None,
    ) -> dict[str, Any]:
        """Get deployment statistics.

        Args:
            environment: Filter by environment (optional)

        Returns:
            Statistics dictionary with counts, success rates, etc.
        """
        ...


@dataclass(frozen=True)
class ServiceQueryFilter:
    """
    Filter criteria for service queries.
    """

    name: str | None = None
    status: str | None = None
    port: int | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class ServiceQueryResult:
    """
    Result of a service query.
    """

    id: str
    name: str
    port: int
    protocol: str
    status: str
    created_at: str
    updated_at: str
    started_at: str | None = None
    stopped_at: str | None = None
    error_message: str | None = None


class ServiceQuery(Protocol):
    """Service query protocol.

    Defines the contract for querying service data.
    """

    async def find_by_id(self, service_id: str) -> ServiceQueryResult | None:
        """Find service by ID.

        Args:
            service_id: Service identifier

        Returns:
            Service query result if found, None otherwise
        """
        ...

    async def find_by_name(self, name: str) -> ServiceQueryResult | None:
        """Find service by name.

        Args:
            name: Service name

        Returns:
            Service query result if found, None otherwise
        """
        ...

    async def find_all(self, filter: ServiceQueryFilter) -> list[ServiceQueryResult]:
        """Find all services matching filter criteria.

        Args:
            filter: Query filter criteria

        Returns:
            List of service query results
        """
        ...

    async def find_running(self) -> list[ServiceQueryResult]:
        """Find all running services.

        Returns:
            List of running service query results
        """
        ...

    async def count(self, filter: ServiceQueryFilter) -> int:
        """Count services matching filter criteria.

        Args:
            filter: Query filter criteria

        Returns:
            Total count
        """
        ...

    async def get_health_status(self) -> dict[str, Any]:
        """Get overall service health status.

        Returns:
            Health status dictionary with running/stopped/failed counts
        """
        ...
