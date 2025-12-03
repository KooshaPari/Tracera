"""
Minimal purge service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class PurgeService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def purge(self, *args, **kwargs) -> dict:
        return {"purged": True}
