"""Minimal storage service placeholder for unit tests.

Functional Requirements: FR-INFRA-005
"""

from __future__ import annotations

from typing import Any


class StorageService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def info(self) -> dict[str, Any]:
        """Info."""
        return {"status": "ok"}
