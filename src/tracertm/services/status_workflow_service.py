"""Status workflow service for Epic 2 (Story 2.7, FR13).

Handles status transitions, validation, and progress auto-update.


Functional Requirements: FR-APP-003
"""

from typing import Any

from sqlalchemy.orm import Session

from tracertm.models.event import Event
from tracertm.models.item import Item

# Valid statuses
VALID_STATUSES = ["todo", "in_progress", "blocked", "done", "archived"]

# Valid status transitions
STATUS_TRANSITIONS: dict[str, list[str]] = {
    "todo": ["in_progress", "blocked"],
    "in_progress": ["done", "blocked", "todo"],
    "blocked": ["todo", "in_progress"],
    "done": ["todo"],  # Allow reopening
    "archived": [],  # Terminal state
}

# Progress mapping (for auto-update)
STATUS_PROGRESS: dict[str, int] = {
    "todo": 0,
    "in_progress": 50,
    "blocked": 0,  # Blocked items don't progress
    "done": 100,
    "archived": 100,
}


class StatusWorkflowService:
    """Service for managing item status workflows (Story 2.7, FR13)."""

    def __init__(self, session: Session) -> None:
        """Initialize status workflow service."""
        self.session = session

    def validate_transition(self, current_status: str, new_status: str) -> bool:
        """Validate status transition (Story 2.7, FR13).

        Args:
            current_status: Current item status
            new_status: Desired new status

        Returns:
            True if transition is valid, False otherwise
        """
        if new_status not in VALID_STATUSES:
            return False

        if current_status not in STATUS_TRANSITIONS:
            return False

        allowed = STATUS_TRANSITIONS.get(current_status, [])
        return new_status in allowed

    def update_item_status(
        self,
        item_id: str,
        new_status: str,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        """Update item status with validation and progress auto-update (Story 2.7, FR13).

        Args:
            item_id: Item ID
            new_status: New status
            agent_id: Optional agent ID for logging

        Returns:
            Dictionary with update result

        Raises:
            ValueError: If transition is invalid
        """
        item = self.session.query(Item).filter(Item.id == item_id).first()
        if not item:
            msg = f"Item not found: {item_id}"
            raise ValueError(msg)

        current_status = item.status or "todo"

        # Validate transition
        if not self.validate_transition(current_status, new_status):
            msg = (
                f"Invalid status transition: {current_status} → {new_status}. "
                f"Allowed transitions from {current_status}: {STATUS_TRANSITIONS.get(current_status, [])}"
            )
            raise ValueError(
                msg,
            )

        # Update status
        old_status = item.status
        item.status = new_status

        # Auto-update progress based on status
        if new_status in STATUS_PROGRESS:
            # Note: Progress calculation is handled by ProgressService
            # This just ensures status-based progress is considered
            pass

        # Log status change event
        event = Event(
            project_id=item.project_id,
            event_type="status_changed",
            entity_type="item",
            entity_id=item.id,
            agent_id=agent_id,
            data={
                "old_status": old_status,
                "new_status": new_status,
                "item_id": item.id,
                "item_title": item.title,
            },
        )
        self.session.add(event)

        self.session.commit()

        return {
            "item_id": item.id,
            "old_status": old_status,
            "new_status": new_status,
            "progress": STATUS_PROGRESS.get(new_status, 0),
        }

    def get_status_history(self, item_id: str) -> list[dict[str, Any]]:
        """Get status change history for an item (Story 2.7, FR13).

        Args:
            item_id: Item ID

        Returns:
            List of status change events
        """
        events = (
            self.session
            .query(Event)
            .filter(
                Event.entity_type == "item",
                Event.entity_id == item_id,
                Event.event_type == "status_changed",
            )
            .order_by(Event.created_at.desc())
            .all()
        )

        return [
            {
                "timestamp": event.created_at.isoformat() if event.created_at else None,
                "old_status": event.data.get("old_status"),
                "new_status": event.data.get("new_status"),
                "agent_id": event.agent_id,
            }
            for event in events
        ]
