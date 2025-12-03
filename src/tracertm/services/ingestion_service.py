"""
Minimal ingestion service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any, Iterable


class IngestionService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def ingest(self, items: Iterable[dict]) -> dict:
        """Pretend to ingest items."""
        count = len(list(items)) if items is not None else 0
        return {"ingested": count}
