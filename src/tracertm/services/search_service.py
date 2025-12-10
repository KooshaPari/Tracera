"""
Minimal search service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class SearchService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def search(self, query: str | None = None, filters: dict | None = None) -> list[dict]:
        return []
