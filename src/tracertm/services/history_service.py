"""Minimal history service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class HistoryService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def get_history(self, *args: Any, **kwargs: Any) -> list[dict[str, object]]:
        return []
