"""
Minimal graph analysis service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class GraphAnalysisService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def analyze(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"status": "ok", "nodes": 0, "edges": 0}
