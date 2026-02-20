"""Minimal notification service placeholder for unit tests.

Functional Requirements: FR-COLLAB-003
"""

from __future__ import annotations


class NotificationService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def notify(self, _message: str) -> bool:
        """Notify."""
        return True
