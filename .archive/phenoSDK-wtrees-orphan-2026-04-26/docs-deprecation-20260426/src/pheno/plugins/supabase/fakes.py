"""
Test doubles for Supabase integrations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InMemorySupabaseClient:
    """
    Very small in-memory store that mimics Supabase table operations.
    """

    tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def from_(self, table: str) -> InMemorySupabaseQuery:
        return InMemorySupabaseQuery(self.tables.setdefault(table, []))


class InMemorySupabaseQuery:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows
        self._filters: dict[str, Any] = {}
        self._updates: dict[str, Any] = {}
        self._insert_payload: list[dict[str, Any]] | None = None

    # Filter helpers ----------------------------------------------------
    def eq(self, key: str, value: Any):
        self._filters[key] = value
        return self

    def select(self, _: str):
        return self

    def limit(self, _: int):
        return self

    def single(self):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def range(self, *_args, **_kwargs):
        return self

    def update(self, data: dict[str, Any]):
        self._updates = data
        return self

    def delete(self):
        self._updates = {"__delete__": True}
        return self

    def insert(self, data: dict[str, Any] | list[dict[str, Any]]):
        if isinstance(data, dict):
            self._insert_payload = [data]
        else:
            self._insert_payload = data
        return self

    # Execution ---------------------------------------------------------
    def execute(self):
        if self._insert_payload is not None:
            self._rows.extend(self._insert_payload)
            return _Result(self._insert_payload)

        if self._updates:
            if self._updates.get("__delete__"):
                before = len(self._rows)
                self._rows[:] = [row for row in self._rows if not self._match(row)]
                deleted = before - len(self._rows)
                return _Result([{"deleted": deleted}])
            updated = []
            for row in self._rows:
                if self._match(row):
                    row.update(self._updates)
                    updated.append(row)
            return _Result(updated)

        data = [row for row in self._rows if self._match(row)]
        return _Result(data)

    # ------------------------------------------------------------------
    def _match(self, row: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in self._filters.items())


@dataclass
class InMemorySupabaseAuth:
    """
    Simple auth helper with a mapping of access tokens to user payloads.
    """

    users: dict[str, dict[str, Any]] = field(default_factory=dict)

    def register_user(self, token: str, payload: dict[str, Any]) -> None:
        self.users[token] = payload

    def get_user(self, token: str) -> dict[str, Any] | None:
        return self.users.get(token)


class _Result:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


__all__ = ["InMemorySupabaseAuth", "InMemorySupabaseClient"]
