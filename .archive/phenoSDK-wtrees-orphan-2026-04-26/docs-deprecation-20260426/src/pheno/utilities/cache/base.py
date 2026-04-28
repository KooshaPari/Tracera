from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Hashable


@runtime_checkable
class CacheProtocol(Protocol):
    """
    Minimal async cache protocol used by analytics utilities.
    """

    async def get(self, key: Hashable) -> Any | None: ...

    async def set(self, key: Hashable, value: Any, *, ttl: float | None = None) -> None: ...

    async def delete(self, key: Hashable) -> None: ...

    async def clear(self) -> None: ...


class NullCache(CacheProtocol):
    """
    No-op cache implementation.
    """

    async def get(self, key: Hashable) -> Any | None:
        return None

    async def set(self, key: Hashable, value: Any, *, ttl: float | None = None) -> None:
        return None

    async def delete(self, key: Hashable) -> None:
        return None

    async def clear(self) -> None:
        return None


class CacheMetricsProtocol(Protocol):
    """
    Optional metrics hooks for cache implementations.
    """

    def record_hit(self, namespace: str) -> None: ...

    def record_miss(self, namespace: str) -> None: ...

    def record_set(self, namespace: str) -> None: ...

    def record_eviction(self, namespace: str) -> None: ...


class NullCacheMetrics(CacheMetricsProtocol):
    """
    Fallback metrics collector.
    """

    def record_hit(self, namespace: str) -> None:
        return None

    def record_miss(self, namespace: str) -> None:
        return None

    def record_set(self, namespace: str) -> None:
        return None

    def record_eviction(self, namespace: str) -> None:
        return None
