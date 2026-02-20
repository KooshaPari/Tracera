"""Minimal dependency analysis service placeholder for tests.

Functional Requirements: FR-QUAL-006
"""

from __future__ import annotations

from typing import Any


class DependencyAnalysisService:
    """Stub service used in unit tests; real logic not yet implemented."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def analyze(self, *_args: object, **_kwargs: object) -> dict[str, Any]:
        """Return a minimal analysis result."""
        return {"status": "ok", "dependencies": []}
