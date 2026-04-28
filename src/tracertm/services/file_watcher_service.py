"""Minimal file watcher service placeholder for tests.

Functional Requirements: FR-DISC-008
"""

from __future__ import annotations

from typing import Any


class FileWatcherService:
    """Stub service used in unit tests; replace with real implementation when ready."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def watch(self, path: str) -> dict[str, Any]:
        """Return a simple status payload."""
        return {"status": "watching", "path": path}
