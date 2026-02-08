"""Minimal progress tracking service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class ProgressTrackingService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def progress(self) -> dict[str, object]:
        return {"progress": 0}
