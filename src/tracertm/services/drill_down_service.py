"""Minimal drill-down service placeholder for tests."""

from __future__ import annotations

from typing import Any


class DrillDownService:
    """Stub service used in unit tests; real drill-down logic TBD."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def drill(self, *_args: object, **_kwargs: object) -> dict[str, Any]:
        """Return a minimal drill-down result."""
        return {"status": "ok", "items": []}
