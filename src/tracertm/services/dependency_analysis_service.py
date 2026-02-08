"""Minimal dependency analysis service placeholder for tests."""

from __future__ import annotations

from typing import Any


class DependencyAnalysisService:
    """Stub service used in unit tests; real logic not yet implemented."""

    def __init__(self, db_session: Any | None = None) -> None:
        self.db_session = db_session

    async def analyze(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002 - stub for future implementation
        """Return a minimal analysis result."""
        return {"status": "ok", "dependencies": []}
