"""Minimal search service placeholder for unit tests.

Functional Requirements: FR-APP-004
"""

from __future__ import annotations

from typing import Any


class SearchService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def search(
        self,
        _query: str | None = None,
        _filters: dict[str, Any] | None = None,
        _project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search; project_id can be passed as kwarg or via filters['project_id']."""
        return []
