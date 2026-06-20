"""Minimal graph analysis service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class GraphAnalysisService:
    """Stub service used in unit tests.

    Functional Requirements:
    - FR-RPT-001

    User Stories:
    - US-GRAPH-001

    Epics:
    - EPIC-006
    """

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def analyze(self, *_args: object, **_kwargs: object) -> dict[str, Any]:
        """Analyze."""
        return {"status": "ok", "nodes": 0, "edges": 0}
