"""Minimal progress tracking service placeholder for unit tests.

Functional Requirements: FR-APP-010
"""

from __future__ import annotations

from typing import Any


class ProgressTrackingService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def progress(self) -> dict[str, Any]:
        """Progress."""
        return {"progress": 0}
