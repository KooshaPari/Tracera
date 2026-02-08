"""Minimal repair service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class RepairService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def repair(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"repaired": True}
