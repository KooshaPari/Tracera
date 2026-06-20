"""Minimal history service placeholder for unit tests.

Functional Requirements: FR-APP-009
"""

from __future__ import annotations

from typing import Any


class HistoryService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def get_history(self, *_args: object, **_kwargs: object) -> list[dict[str, Any]]:
        """Get history."""
        return []
