"""Event sourcing service for TraceRTM."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import OperationalError

from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.event import Event


@dataclass
class AuditTrailEntry:
    """Entry in the audit trail."""

    timestamp: str
    event_type: str
    entity_type: str
    entity_id: str
    agent_id: str | None
    data: dict[str, Any]


@dataclass
class ReplayResult:
    """Result of event replay."""

    total_events: int
    replayed_events: int
    failed_events: int
    final_state: dict[str, Any]


class EventSourcingService:
    """Service for event sourcing and replay."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.events = EventRepository(session)
        self.items = ItemRepository(session)

    async def get_audit_trail(
        self,
        project_id: str | uuid.UUID,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditTrailEntry]:
        """Get audit trail for a project or entity."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        if entity_id:
            events = await self.events.get_by_entity(entity_id)
        else:
            events = await self.events.get_by_project(pid, limit=limit)

        return [
            AuditTrailEntry(
                timestamp=(e.created_at.isoformat() if hasattr(e.created_at, "isoformat") else str(e.created_at)),
                event_type=e.event_type,
                entity_type=e.entity_type,
                entity_id=e.entity_id,
                agent_id=e.agent_id,
                data=e.data,
            )
            for e in events
        ]

    async def replay_events(
        self,
        _project_id: str | uuid.UUID,
        entity_id: str,
        up_to_timestamp: str | None = None,
    ) -> ReplayResult:
        """Replay events to reconstruct entity state."""
        # Get all events for entity (project_id not used for get_by_entity)
        events = await self.events.get_by_entity(entity_id)

        # Filter by timestamp if provided
        if up_to_timestamp:
            cutoff = datetime.fromisoformat(up_to_timestamp)
            events = [e for e in events if datetime.fromisoformat(str(e.created_at)) <= cutoff]

        # Replay events
        state: dict[str, Any] = {}
        replayed = 0
        failed = 0

        for event in events:
            try:
                state = await self._apply_event(state, event)
                replayed += 1
            except (ValueError, KeyError, OperationalError):
                failed += 1

        return ReplayResult(
            total_events=len(events),
            replayed_events=replayed,
            failed_events=failed,
            final_state=state,
        )

    async def _apply_event(
        self,
        state: dict[str, Any],
        event: Event,
    ) -> dict[str, Any]:
        """Apply an event to the state."""
        if event.event_type == "item_created":
            state.update({
                "id": event.entity_id,
                "title": event.data.get("title"),
                "status": "created",
                "version": 1,
            })

        elif event.event_type == "item_updated":
            state.update(event.data)
            state["version"] = state.get("version", 1) + 1

        elif event.event_type == "item_deleted":
            state["deleted"] = True
            state["deleted_at"] = event.data.get("deleted_at")

        elif event.event_type == "link_created":
            if "links" not in state:
                state["links"] = []
            state["links"].append({
                "target_id": event.data.get("target_item_id"),
                "type": event.data.get("link_type"),
            })

        return state

    async def get_event_history(
        self,
        entity_id: str,
        event_type: str | None = None,
    ) -> list[Event]:
        """Get event history for an entity."""
        events = await self.events.get_by_entity(entity_id)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events

    async def get_changes_between(
        self,
        entity_id: str,
        start_timestamp: str,
        end_timestamp: str,
    ) -> list[AuditTrailEntry]:
        """Get changes to an entity between two timestamps."""
        events = await self.events.get_by_entity(entity_id)

        start = datetime.fromisoformat(start_timestamp)
        end = datetime.fromisoformat(end_timestamp)

        filtered = [e for e in events if start <= datetime.fromisoformat(str(e.created_at)) <= end]

        return [
            AuditTrailEntry(
                timestamp=str(e.created_at),
                event_type=e.event_type,
                entity_type=e.entity_type,
                entity_id=e.entity_id,
                agent_id=e.agent_id,
                data=e.data,
            )
            for e in filtered
        ]
