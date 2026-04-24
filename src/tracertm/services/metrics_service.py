"""Minimal metrics service placeholder for unit tests.

Functional Requirements: FR-RPT-006
"""

from __future__ import annotations

from typing import Any


class MetricsService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def collect(self) -> dict[str, Any]:
        """Collect."""
        return {"metrics": {}}
