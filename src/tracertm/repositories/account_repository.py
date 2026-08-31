"""Account repository.

Recreated minimal implementation to repair an import regression where the
`tracertm.repositories.account_repository` module was removed from the tree
while two callers still imported it:

- `tracertm.repositories.__init__` re-exports `AccountRepository`
- `tracertm.api.routers.auth` instantiates it and calls `list_by_user(user_id)`

This module is intentionally additive: it provides the smallest surface area
that satisfies those callers so the FastAPI app can boot. Real persistence
can be re-wired later by binding the optional `_table` attribute to a
SQLAlchemy mapped class.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class _AccountRow:
    """Lightweight row shape compatible with `auth.get_current_user`.

    The auth router only reads `.id` and `.name` from returned rows, so a
    minimal dataclass satisfies that contract without depending on a
    specific ORM model.
    """

    id: Any
    name: Any


class AccountRepository:
    """Repository for account lookups keyed by user id.

    The constructor accepts an async SQLAlchemy session, mirroring the
    pattern used by sibling repositories in this package. When no mapped
    `Account` ORM model is registered, `list_by_user` returns an empty list
    rather than raising, which keeps the `/auth/me` endpoint functional and
    lets it fall back to JWT-claim-derived account data.
    """

    def __init__(self, session: Any) -> None:
        self._session = session
        # Optional SQLAlchemy mapped class for the `accounts` table. Bind at
        # app startup if/when the Account ORM model is reintroduced.
        self._table: Any | None = None

    async def list_by_user(self, user_id: Any) -> list[_AccountRow]:
        """Return accounts owned by ``user_id``.

        With no bound ORM table this is a safe no-op so the API can boot.
        When a real `Account` model is wired in, populate `self._table` from
        the model's class and this method will delegate to it.
        """
        if self._table is None:
            return []

        result = await self._session.execute(
            self._table.__table__.select().where(
                self._table.user_id == user_id  # type: ignore[attr-defined]
            )
        )
        rows = result.fetchall()
        return [
            _AccountRow(id=getattr(row, "id", None), name=getattr(row, "name", None))
            for row in rows
        ]


__all__ = ["AccountRepository"]