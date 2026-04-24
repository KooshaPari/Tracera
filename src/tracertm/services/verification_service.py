"""Minimal verification service placeholder for unit tests.

Functional Requirements: FR-VERIF-001, FR-VERIF-002, FR-VERIF-008
"""

from __future__ import annotations


class VerificationService:
    """Stub service used in unit tests."""

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def verify(self, *_args: object, **_kwargs: object) -> dict[str, bool]:
        """Verify."""
        return {"verified": True}
