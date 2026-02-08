"""Minimal search service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class SearchService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def search(
        self,
        query: str | None = None,  # noqa: ARG002
        filters: dict[str, object] | None = None,  # noqa: ARG002
        project_id: str | None = None,  # noqa: ARG002
    ) -> list[dict[str, object]]:
        """Search; project_id can be passed as kwarg or via filters['project_id']."""
        return []
