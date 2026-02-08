"""Minimal drill-down service placeholder for tests."""

from __future__ import annotations

from typing import Any


class DrillDownService:
    """Stub service used in unit tests; real drill-down logic TBD."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def drill(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Return a minimal drill-down result."""
        return {"status": "ok", "items": []}
