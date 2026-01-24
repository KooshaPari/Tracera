"""
Minimal metrics service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class MetricsService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def collect(self) -> dict[str, object]:
        return {"metrics": {}}
