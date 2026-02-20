"""Minimal query service placeholder for unit tests.

Functional Requirements: FR-APP-004
"""

from __future__ import annotations

from typing import Any


class QueryService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def search(self, _criteria: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Search."""
        return []
