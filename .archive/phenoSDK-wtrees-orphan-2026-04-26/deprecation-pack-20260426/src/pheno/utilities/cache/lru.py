from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from typing import TYPE_CHECKING, Any

from pheno.utilities.cache.base import (
    CacheMetricsProtocol,
    CacheProtocol,
    NullCacheMetrics,
)

if TYPE_CHECKING:
    from collections.abc import Hashable


class LruCache(CacheProtocol):
    """
    Async-friendly LRU cache with optional TTL and metrics instrumentation.
    """

    def __init__(
        self,
        *,
        max_entries: int = 1024,
        ttl: float | None = None,
        namespace: str = "default",
        metrics: CacheMetricsProtocol | None = None,
    ) -> None:
        if max_entries <= 0:
            raise ValueError("max_entries must be > 0")
        self._max_entries = max_entries
        self._ttl = ttl
        self._namespace = namespace
        self._metrics = metrics or NullCacheMetrics()
        self._lock = asyncio.Lock()
        self._store: OrderedDict[Hashable, tuple[Any, float | None]] = OrderedDict()

    async def get(self, key: Hashable) -> Any | None:
        async with self._lock:
            value = self._store.get(key)
            if value is None:
                self._metrics.record_miss(self._namespace)
                return None
            payload, expires_at = value
            if expires_at is not None and expires_at < time.time():
                self._store.pop(key, None)
                self._metrics.record_miss(self._namespace)
                return None
            self._store.move_to_end(key)
            self._metrics.record_hit(self._namespace)
            return payload

    async def set(self, key: Hashable, value: Any, *, ttl: float | None = None) -> None:
        expiry = self._compute_expiry(ttl)
        async with self._lock:
            self._store[key] = (value, expiry)
            self._store.move_to_end(key)
            self._trim_locked()
            self._metrics.record_set(self._namespace)

    async def delete(self, key: Hashable) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    def _compute_expiry(self, ttl: float | None) -> float | None:
        ttl_to_use = ttl if ttl is not None else self._ttl
        if ttl_to_use is None:
            return None
        return time.time() + ttl_to_use

    def _trim_locked(self) -> None:
        while len(self._store) > self._max_entries:
            _key, _ = self._store.popitem(last=False)
            self._metrics.record_eviction(self._namespace)
