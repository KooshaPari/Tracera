"""Minimal sync service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class SyncService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def sync(self) -> dict[str, object]:
        return {"synced": True}
