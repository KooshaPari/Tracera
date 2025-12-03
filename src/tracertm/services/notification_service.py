"""
Minimal notification service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class NotificationService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def notify(self, message: str) -> bool:
        return True
