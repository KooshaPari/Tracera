"""
Supabase database adapter implementation.
"""

from __future__ import annotations

from typing import Any

from pheno.dev.utils.logging import get_logger

from ..cache import QueryCache
from .base import DatabaseAdapter

logger = get_logger(__name__)


class SupabaseDatabaseAdapter(DatabaseAdapter):
    """
    Supabase database adapter with caching and RLS support.
    """

    def __init__(self, supabase_client=None, cache_ttl: int = 30) -> None:
        super().__init__(cache_ttl)
        self._client = supabase_client

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from pheno.database.supabase_client import get_supabase

            return get_supabase(access_token=self._access_token)
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Supabase client not available. Either pass supabase_client to constructor or ensure "
                "supabase_client module is available.",
            ) from exc

    def _apply_filters(self, query, filters: dict[str, Any] | None):
        if not filters:
            return query
        for key, value in filters.items():
            if value is None:
                query = query.is_(key, None)
            elif isinstance(value, dict):
                for op, val in value.items():
                    if op == "eq":
                        query = query.eq(key, val)
                    elif op == "neq":
                        query = query.neq(key, val)
                    elif op == "gt":
                        query = query.gt(key, val)
                    elif op == "gte":
                        query = query.gte(key, val)
                    elif op == "lt":
                        query = query.lt(key, val)
                    elif op == "lte":
                        query = query.lte(key, val)
                    elif op == "like":
                        query = query.like(key, val)
                    elif op == "ilike":
                        query = query.ilike(key, val)
                    elif op == "in":
                        query = query.in_(key, val)
                    elif op == "not_in":
                        query = query.not_.in_(key, val)
            else:
                query = query.eq(key, value)
        return query

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
        cache_key = self._build_cache_key(table, select, filters, order_by, limit, offset)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._execute_query(table, select, filters, order_by, limit, offset)
        self._cache.set(cache_key, data)
        return data

    def _build_cache_key(
        self,
        table: str,
        select: str | None,
        filters: dict[str, Any] | None,
        order_by: str | None,
        limit: int | None,
        offset: int | None,
    ) -> str:
        return QueryCache.make_key(
            "query",
            table=table,
            select=select,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

    async def _execute_query(
        self,
        table: str,
        select: str | None,
        filters: dict[str, Any] | None,
        order_by: str | None,
        limit: int | None,
        offset: int | None,
    ) -> list[dict[str, Any]]:
        client = self._get_client()
        query = client.from_(table).select(select or "*")
        query = self._apply_filters(query, filters)
        query = self._apply_ordering(query, order_by)
        query = self._apply_pagination(query, limit, offset)
        result = query.execute()
        return getattr(result, "data", []) or []

    def _apply_ordering(self, query, order_by: str | None):
        if order_by:
            parts = order_by.split(":")
            column = parts[0]
            desc = len(parts) > 1 and parts[1].lower() == "desc"
            query = query.order(column, desc=desc)
        return query

    def _apply_pagination(self, query, limit: int | None, offset: int | None):
        if offset:
            query = query.range(offset, (offset + limit - 1) if limit else None)
        elif limit:
            query = query.limit(limit)
        return query

    async def get_single(
        self,
        table: str,
        *,
        select: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        client = self._get_client()
        query = client.from_(table).select(select or "*")
        query = self._apply_filters(query, filters)
        try:
            result = query.single().execute()
        except Exception as exc:  # pragma: no cover - Supabase specific
            if hasattr(exc, "code") and exc.code == "PGRST116":
                return None
            logger.exception("Get single failed on table %s: %s", table, exc)
            raise
        return getattr(result, "data", None)

    async def insert(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        *,
        returning: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        client = self._get_client()
        result = client.from_(table).insert(data).execute()
        result_data = getattr(result, "data", None)
        if result_data is None:
            raise ValueError("Insert operation returned no data")
        self._cache.invalidate(table)
        if isinstance(data, dict):
            return result_data[0] if result_data else {}
        return result_data

    async def update(
        self,
        table: str,
        data: dict[str, Any],
        filters: dict[str, Any],
        *,
        returning: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        client = self._get_client()
        query = client.from_(table).update(data)
        query = self._apply_filters(query, filters)
        result = query.execute()
        result_data = getattr(result, "data", []) or []
        self._cache.invalidate(table)
        if len(result_data) == 1:
            return result_data[0]
        return result_data

    async def delete(self, table: str, filters: dict[str, Any]) -> int:
        client = self._get_client()
        query = client.from_(table).delete()
        query = self._apply_filters(query, filters)
        result = query.execute()
        deleted_rows = getattr(result, "data", []) or []
        self._cache.invalidate(table)
        return len(deleted_rows)

    async def count(self, table: str, filters: dict[str, Any] | None = None) -> int:
        cache_key = QueryCache.make_key("count", table=table, filters=filters)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        client = self._get_client()
        query = client.from_(table).select("*", count="exact", head=True)
        query = self._apply_filters(query, filters)
        result = query.execute()
        count = getattr(result, "count", 0) or 0
        self._cache.set(cache_key, count)
        return count


__all__ = ["SupabaseDatabaseAdapter"]
