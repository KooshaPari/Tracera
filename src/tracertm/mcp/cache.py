"""Caching layer for MCP tools with TTL and invalidation support.

Provides a simple in-memory cache with:
- TTL-based expiration (default 5 minutes)
- LRU eviction (max 1000 entries)
- Cache invalidation on writes
- Thread-safe operations
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class CacheEntry:
    """Cache entry with TTL support."""

    def __init__(self, value: object, ttl: int) -> None:
        """Initialize cache entry.

        Args:
            value: Value to cache
            ttl: Time to live in seconds
        """
        self.value = value
        self.expires_at = time.time() + ttl
        self.created_at = time.time()

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.expires_at


class QueryCache:
    """Thread-safe query cache with TTL and LRU eviction.

    Features:
    - Automatic TTL expiration
    - LRU eviction when max_size reached
    - Pattern-based invalidation
    - Cache hit/miss statistics
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300) -> None:
        """Initialize cache.

        Args:
            max_size: Maximum number of entries (LRU eviction)
            default_ttl: Default TTL in seconds (default 5 minutes)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    def _make_key(self, prefix: str, *args: object, **kwargs: object) -> str:
        """Generate cache key from arguments."""
        # Create a stable string representation
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items()),
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def get(self, prefix: str, *args: object, **kwargs: object) -> object | None:
        """Get value from cache.

        Args:
            prefix: Cache key prefix (e.g., "project_list", "item_query")
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation

        Returns:
            Cached value or None if not found/expired
        """
        key = self._make_key(prefix, *args, **kwargs)

        async with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

    async def set(self, prefix: str, value: object, ttl: int | None = None, *args: object, **kwargs: object) -> None:
        """Set value in cache.

        Args:
            prefix: Cache key prefix
            value: Value to cache
            ttl: Time to live in seconds (uses default_ttl if None)
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation
        """
        key = self._make_key(prefix, *args, **kwargs)
        ttl = ttl if ttl is not None else self.default_ttl

        async with self._lock:
            # LRU eviction if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)

            self._cache[key] = CacheEntry(value, ttl)
            self._cache.move_to_end(key)

    async def invalidate(self, prefix: str | None = None) -> None:
        """Invalidate cache entries.

        Args:
            prefix: If provided, only invalidate entries with this prefix.
                   If None, clear entire cache.
        """
        async with self._lock:
            if prefix is None:
                self._cache.clear()
            else:
                # Find and remove entries matching prefix
                to_remove = [key for key in self._cache if key.startswith(prefix)]
                for key in to_remove:
                    del self._cache[key]

    async def get_or_compute(
        self,
        prefix: str,
        compute_fn: Callable[..., object],
        ttl: int | None = None,
        *args: object,
        **kwargs: object,
    ) -> object:
        """Get from cache or compute and cache the result.

        Args:
            prefix: Cache key prefix
            compute_fn: Async function to compute value if not cached
            ttl: Time to live in seconds
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation

        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = await self.get(prefix, *args, **kwargs)
        if value is not None:
            return value

        # Compute value
        if asyncio.iscoroutinefunction(compute_fn):
            value = await compute_fn()
        else:
            value = compute_fn()

        # Cache result
        await self.set(prefix, value, ttl, *args, **kwargs)
        return value

    async def cleanup_expired(self) -> None:
        """Remove all expired entries."""
        async with self._lock:
            to_remove = [key for key, entry in self._cache.items() if entry.is_expired()]
            for key in to_remove:
                del self._cache[key]

    def get_stats(self) -> dict[str, object]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / max(1, total_requests)

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

    async def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0


# Global cache instance
_query_cache: QueryCache | None = None


def get_query_cache() -> QueryCache:
    """Get or create the global query cache instance."""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache(max_size=1000, default_ttl=300)
    return _query_cache


def invalidate_cache(prefix: str | None = None) -> None:
    """Invalidate cache entries (sync wrapper)."""
    cache = get_query_cache()
    # Run in event loop
    loop = asyncio.get_event_loop()
    if loop.is_running():
        _ = asyncio.create_task(cache.invalidate(prefix))
    else:
        asyncio.run(cache.invalidate(prefix))


__all__ = ["CacheEntry", "QueryCache", "get_query_cache", "invalidate_cache"]
