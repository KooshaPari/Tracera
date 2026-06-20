"""Minimal sync service placeholder for unit tests.

Functional Requirements: FR-COLLAB-001
"""

from __future__ import annotations

from typing import Any


class SyncService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def sync(self) -> dict[str, Any]:
        """Sync."""
        return {"synced": True}
