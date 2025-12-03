"""
Minimal dependency analysis service placeholder for tests.
"""

from __future__ import annotations

from typing import Any


class DependencyAnalysisService:
    """Stub service used in unit tests; real logic not yet implemented."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def analyze(self, *args, **kwargs) -> dict:
        """Return a minimal analysis result."""
        return {"status": "ok", "dependencies": []}
