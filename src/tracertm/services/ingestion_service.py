"""Minimal ingestion service placeholder for unit tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


class IngestionService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def ingest(self, items: Iterable[dict[str, object]]) -> dict[str, object]:
        """Pretend to ingest items."""
        count = len(list(items)) if items is not None else 0
        return {"ingested": count}
