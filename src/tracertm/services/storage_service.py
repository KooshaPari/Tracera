"""
Minimal storage service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class StorageService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def info(self) -> dict:
        return {"status": "ok"}
