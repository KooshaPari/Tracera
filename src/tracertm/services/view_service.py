"""Minimal view service placeholder for unit tests."""

from __future__ import annotations


class ViewService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def list_views(self) -> list[str]:
        """List views."""
        return []
