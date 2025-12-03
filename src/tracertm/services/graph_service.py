"""
Minimal graph service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class GraphService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def get_graph(self, *args, **kwargs) -> dict:
        return {"nodes": [], "links": []}
