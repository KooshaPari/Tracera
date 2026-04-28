"""
Abstract database adapter base class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pheno.dev.utils.logging import get_logger

from ..cache import QueryCache

logger = get_logger(__name__)


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters.
    """

    def __init__(self, cache_ttl: int = 30) -> None:
        self._cache = QueryCache(ttl=cache_ttl)
        self._access_token: str | None = None

    def set_access_token(self, token: str) -> None:
        self._access_token = token

    @abstractmethod
    async def query(
        self,
        table: str,
        *,
        select: str | None = None,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a query on a table.
        """

    @abstractmethod
    async def get_single(
        self,
        table: str,
        *,
        select: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Get a single record from a table.
        """

    @abstractmethod
    async def insert(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        *,
        returning: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Insert one or more records.
        """

    @abstractmethod
    async def update(
        self,
        table: str,
        data: dict[str, Any],
        filters: dict[str, Any],
        *,
        returning: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Update records.
        """

    @abstractmethod
    async def delete(self, table: str, filters: dict[str, Any]) -> int:
        """
        Delete records.
        """

    @abstractmethod
    async def count(self, table: str, filters: dict[str, Any] | None = None) -> int:
        """
        Count records in a table.
        """


__all__ = ["DatabaseAdapter"]
