"""Conflict resolution service for Epic 5 (Story 5.5, FR43).

Provides conflict detection and resolution strategies.


Functional Requirements: FR-COLLAB-001
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from tracertm.models.event import Event
from tracertm.models.item import Item

MIN_EVENTS_FOR_CONFLICT = 2


class ConflictResolutionService:
    """Service for detecting and resolving conflicts (Story 5.5, FR43)."""

    def __init__(self, session: Session) -> None:
        """Initialize conflict resolution service."""
        self.session = session

    def detect_conflicts(
        self,
        project_id: str,
        item_id: str | None = None,
        time_window_seconds: int = 60,
    ) -> list[dict[str, Any]]:
        """Detect conflicts for items (Story 5.5).

        Args:
            project_id: Project ID
            item_id: Optional specific item ID
            time_window_seconds: Time window for conflict detection

        Returns:
            List of conflict dictionaries
        """
        conflicts = []

        # Find recent update events
        time_threshold = datetime.now(UTC) - timedelta(seconds=time_window_seconds)

        query = self.session.query(Event).filter(
            Event.project_id == project_id,
            Event.event_type.in_(["item_updated", "conflict_detected"]),
            Event.created_at >= time_threshold,
        )

        if item_id:
            query = query.filter(Event.entity_id == item_id)

        events = query.order_by(Event.created_at.desc()).all()

        # Group by entity_id and detect multiple agents updating same item
        entity_events: dict[str, list[Event]] = {}
        for event in events:
            if event.entity_id not in entity_events:
                entity_events[event.entity_id] = []
            entity_events[event.entity_id].append(event)

        # Find conflicts (multiple agents updating same item)
        for entity_id, events_list in entity_events.items():
            if len(events_list) > 1:
                # Multiple updates to same item - potential conflict
                agent_ids = [e.agent_id for e in events_list if e.agent_id]
                if len(set(agent_ids)) > 1:
                    conflicts.append({
                        "entity_id": entity_id,
                        "entity_type": events_list[0].entity_type,
                        "conflicting_agents": list(set(agent_ids)),
                        "event_count": len(events_list),
                        "first_event": events_list[-1].created_at.isoformat() if events_list[-1].created_at else None,
                        "last_event": events_list[0].created_at.isoformat() if events_list[0].created_at else None,
                    })

        return conflicts

    def resolve_conflict(
        self,
        project_id: str,
        item_id: str,
        strategy: str = "last_write_wins",
    ) -> dict[str, Any]:
        """Resolve a conflict using specified strategy (Story 5.5).

        Args:
            project_id: Project ID
            item_id: Item ID with conflict
            strategy: Resolution strategy (last_write_wins, merge, manual)

        Returns:
            Resolution result dictionary
        """
        item = self.session.query(Item).filter(Item.id == item_id, Item.project_id == project_id).first()

        if not item:
            msg = f"Item not found: {item_id}"
            raise ValueError(msg)

        # Get recent events for this item
        events = (
            self.session
            .query(Event)
            .filter(
                Event.project_id == project_id,
                Event.entity_id == item_id,
                Event.event_type.in_(["item_updated", "conflict_detected"]),
            )
            .order_by(Event.created_at.desc())
            .limit(10)
            .all()
        )

        if len(events) < MIN_EVENTS_FOR_CONFLICT:
            return {
                "resolved": False,
                "reason": "No conflict detected",
            }

        if strategy == "last_write_wins":
            # Use the most recent update
            latest_event = events[0]
            return {
                "resolved": True,
                "strategy": "last_write_wins",
                "winner_agent": latest_event.agent_id,
                "item_version": item.version,
            }

        if strategy == "merge":
            # Attempt to merge changes (simplified - would need field-level merging)
            return {
                "resolved": True,
                "strategy": "merge",
                "note": "Merge strategy requires manual review",
            }

        msg = f"Unknown resolution strategy: {strategy}"
        raise ValueError(msg)
