"""
Fluent query filter builder utilities.
"""

from __future__ import annotations

from typing import Any


class QueryFilter:
    """
    Fluent query filter builder.
    """

    def __init__(self) -> None:
        self._filters: dict[str, Any] = {}

    def eq(self, field: str, value: Any) -> QueryFilter:
        self._filters[field] = value
        return self

    def neq(self, field: str, value: Any) -> QueryFilter:
        self._filters[field] = {"neq": value}
        return self

    def gt(self, field: str, value: Any) -> QueryFilter:
        self._filters[field] = {"gt": value}
        return self

    def gte(self, field: str, value: Any) -> QueryFilter:
        self._filters[field] = {"gte": value}
        return self

    def lt(self, field: str, value: Any) -> QueryFilter:
        self._filters[field] = {"lt": value}
        return self

    def lte(self, field: str, value: Any) -> QueryFilter:
        self._filters[field] = {"lte": value}
        return self

    def like(self, field: str, pattern: str) -> QueryFilter:
        self._filters[field] = {"like": pattern}
        return self

    def ilike(self, field: str, pattern: str) -> QueryFilter:
        self._filters[field] = {"ilike": pattern}
        return self

    def in_(self, field: str, values: list[Any]) -> QueryFilter:
        self._filters[field] = {"in": values}
        return self

    def is_null(self, field: str) -> QueryFilter:
        self._filters[field] = None
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._filters.copy()


__all__ = ["QueryFilter"]
