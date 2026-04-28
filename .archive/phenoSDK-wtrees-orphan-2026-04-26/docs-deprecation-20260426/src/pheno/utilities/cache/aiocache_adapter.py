"""
Adapter to use aiocache caches with CacheProtocol.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pheno.utilities.cache.base import CacheProtocol

if TYPE_CHECKING:
    from collections.abc import Hashable

try:  # pragma: no cover - optional dependency
    from aiocache import caches  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    caches = None


class AiocacheAdapter(CacheProtocol):
    """
    Wrap an aiocache cache to satisfy CacheProtocol.
    """

    def __init__(self, cache_name: str = "default") -> None:
        if caches is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("aiocache is not installed. Install with `pip install aiocache`.")
        self._cache = caches.get(cache_name)

    async def get(self, key: Hashable) -> Any | None:
        return await self._cache.get(key)

    async def set(self, key: Hashable, value: Any, *, ttl: float | None = None) -> None:
        await self._cache.set(key, value, ttl=ttl)

    async def delete(self, key: Hashable) -> None:
        await self._cache.delete(key)

    async def clear(self) -> None:
        await self._cache.clear()
