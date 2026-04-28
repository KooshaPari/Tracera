"""Minimal repair service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class RepairService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def repair(self, *_args: object, **_kwargs: object) -> dict[str, Any]:
        """Repair."""
        return {"repaired": True}
