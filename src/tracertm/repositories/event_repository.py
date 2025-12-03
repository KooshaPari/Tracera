"""Event repository for TraceRTM."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.event import Event


class EventRepository:
    """Repository for Event operations (event sourcing lite)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        project_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        data: dict[str, Any],
        agent_id: str | None = None,
    ) -> Event:
        """Log an event."""
        # Get next ID by counting existing events
        result = await self.session.execute(
            select(Event.id).order_by(Event.id.desc()).limit(1)
        )
        last_id = result.scalar_one_or_none()
        next_id = (last_id or 0) + 1

        event = Event(
            id=next_id,
            project_id=project_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            agent_id=agent_id,
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_by_entity(
        self,
        entity_id: str,
        limit: int = 100,
    ) -> list[Event]:
        """Get all events for an entity."""
        result = await self.session.execute(
            select(Event)
            .where(Event.entity_id == entity_id)
            .order_by(Event.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_project(
        self,
        project_id: str,
        limit: int = 100,
    ) -> list[Event]:
        """Get all events for a project."""
        result = await self.session.execute(
            select(Event)
            .where(Event.project_id == project_id)
            .order_by(Event.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_agent(
        self,
        agent_id: str,
        limit: int = 100,
    ) -> list[Event]:
        """Get all events by an agent."""
        result = await self.session.execute(
            select(Event)
            .where(Event.agent_id == agent_id)
            .order_by(Event.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_entity_at_time(
        self,
        entity_id: str,
        at_time: datetime,
    ) -> dict[str, Any] | None:
        """Reconstruct entity state at a specific time (event replay)."""
        # Get all events up to that time
        result = await self.session.execute(
            select(Event)
            .where(Event.entity_id == entity_id, Event.created_at <= at_time)
            .order_by(Event.created_at.asc())
        )
        events = list(result.scalars().all())

        if not events:
            return None

        # Replay events to reconstruct state
        state: dict[str, Any] = {}
        for event in events:
            if event.event_type == "created":
                state = event.data
            elif event.event_type == "updated":
                state.update(event.data)
            elif event.event_type == "deleted":
                return None  # Entity was deleted at this point

        return state
