"""Ports - interface definitions (ISP)."""
from abc import ABC, abstractmethod
from uuid import UUID
from .entities import Entity


class Repository(ABC):
    """Repository port - outbound interface for persistence."""

    @abstractmethod
    async def save(self, entity: Entity) -> None:
        """Save an entity."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Entity | None:
        """Find an entity by ID."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete an entity."""
        raise NotImplementedError

    @abstractmethod
    async def list(self, page: int = 1, page_size: int = 20) -> list[Entity]:
        """List entities with pagination."""
        raise NotImplementedError


class EventPublisher(ABC):
    """Event publisher port - outbound interface for messaging."""

    @abstractmethod
    async def publish(self, subject: str, data: bytes) -> None:
        """Publish an event."""
        raise NotImplementedError
