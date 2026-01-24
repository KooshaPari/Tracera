"""
Minimal verification service placeholder for unit tests.
"""

from __future__ import annotations

from typing import Any


class VerificationService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: Any | None = None):
        self.db_session = db_session

    async def verify(self, *args: Any, **kwargs: Any) -> dict[str, bool]:
        return {"verified": True}
