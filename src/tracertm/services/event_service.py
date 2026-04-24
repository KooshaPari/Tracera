"""Event service for TraceRTM.

Functional Requirements: FR-INFRA-006
"""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.event import Event
from tracertm.repositories.event_repository import EventRepository


class EventService:
    """Service for event operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.events = EventRepository(session)

    async def log_event(
        self,
        project_id: str,
        event_type: str,
        event_data: dict[str, Any],
        agent_id: str,
        item_id: str | None = None,
    ) -> Event:
        """Log an event."""
        return await self.events.log(
            project_id=project_id,
            event_type=event_type,
            entity_type="item" if item_id else "project",
            entity_id=item_id or project_id,
            data=event_data,
            agent_id=agent_id,
        )

    async def get_item_history(self, item_id: str) -> list[Event]:
        """Get all events for an item."""
        return await self.events.get_by_entity(item_id)

    async def get_item_at_time(
        self,
        item_id: str,
        at_time: datetime,
    ) -> dict[str, Any] | None:
        """Reconstruct item state at a specific time."""
        return await self.events.get_entity_at_time(item_id, at_time)
