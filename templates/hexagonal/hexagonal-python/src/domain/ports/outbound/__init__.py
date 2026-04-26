"""Outbound ports (Secondary/Driven ports).

These ports define the interface that the application uses to interact
with external systems. They are "implemented" by adapters.

Following Hexagonal Architecture:
- Outbound ports are the "secondary" or "driven" ports
- They define what the application needs from infrastructure
- Implementation is in the adapters layer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from domain.entities import Order
    from domain.value_objects import OrderId
    from domain.events import DomainEvent


@runtime_checkable
class OrderRepositoryPort(Protocol):
    """Port for order persistence operations.

    This port defines the contract for order storage.
    Implementation can be PostgreSQL, MongoDB, in-memory, etc.
    """

    async def save(self, order: Order) -> None:
        """Save an order to the repository.

        Args:
            order: The order to save
        """
        ...

    async def find_by_id(self, order_id: OrderId) -> Order | None:
        """Find an order by its identifier.

        Args:
            order_id: The order identifier

        Returns:
            The order if found, None otherwise
        """
        ...

    async def find_by_customer(
        self,
        customer_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Order]:
        """Find orders by customer.

        Args:
            customer_id: The customer identifier
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of orders for the customer
        """
        ...


@runtime_checkable
class EventBusPort(Protocol):
    """Port for publishing domain events.

    This port defines the contract for event publishing.
    Implementation can be Kafka, RabbitMQ, in-memory, etc.
    """

    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event.

        Args:
            event: The domain event to publish
        """
        ...

    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events.

        Args:
            events: The domain events to publish
        """
        ...


@runtime_checkable
class CachePort(Protocol):
    """Port for caching operations.

    This port defines the contract for caching.
    Implementation can be Redis, Memcached, in-memory, etc.
    """

    async def get(self, key: str) -> str | None:
        """Get a value from cache.

        Args:
            key: The cache key

        Returns:
            The cached value if found, None otherwise
        """
        ...

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None:
        """Set a value in cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl_seconds: Time-to-live in seconds
        """
        ...

    async def delete(self, key: str) -> None:
        """Delete a value from cache.

        Args:
            key: The cache key
        """
        ...


class UnitOfWorkPort(ABC):
    """Port for transactional operations.

    This port defines the contract for managing transactions.
    It ensures atomic operations across multiple repositories.
    """

    @abstractmethod
    async def __aenter__(self) -> UnitOfWorkPort:
        """Enter the unit of work context."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the unit of work context."""
        ...

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction."""
        ...

    @property
    @abstractmethod
    def orders(self) -> OrderRepositoryPort:
        """Get the order repository."""
        ...


__all__ = [
    "OrderRepositoryPort",
    "EventBusPort",
    "CachePort",
    "UnitOfWorkPort",
]
