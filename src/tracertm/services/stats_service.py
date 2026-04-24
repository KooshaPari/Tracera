"""Minimal stats service placeholder for unit tests.

Functional Requirements: FR-RPT-001
"""

from __future__ import annotations

from typing import Any


class StatsService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def stats(self) -> dict[str, Any]:
        """Stats."""
        return {"counts": {}}
