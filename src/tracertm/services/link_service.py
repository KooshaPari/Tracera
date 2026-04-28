"""Minimal link service placeholder for unit tests."""

from __future__ import annotations

from typing import Any


class LinkService:
    """Stub service used in unit tests.

    Functional Requirements:
    - FR-APP-006
    - FR-APP-007
    - FR-APP-008
    - FR-APP-009
    - FR-APP-010

    User Stories:
    - US-LINK-001
    - US-LINK-002
    - US-LINK-003
    - US-LINK-004
    - US-LINK-005

    Epics:
    - EPIC-004
    """

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def list_links(self, *_args: object, **_kwargs: object) -> list[dict[str, Any]]:
        """List links.

        Functional Requirements:
        - FR-APP-010

        User Stories:
        - US-LINK-005

        Epics:
        - EPIC-004
        """
        return []
