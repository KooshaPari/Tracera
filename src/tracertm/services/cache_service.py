"""Caching service for TraceRTM using Redis. Redis is required; fail clearly when unavailable (CLAUDE.md).

Functional Requirements: FR-INFRA-004
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from tracertm.constants import (
    DEFAULT_POOL_SIZE,
    HASH_SIZE_STANDARD,
    TTL_EXTENDED,
    TTL_LONG,
    TTL_MEDIUM,
    TTL_SHORT,
    TTL_STANDARD,
    TTL_VERY_SHORT,
    ZERO,
)

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisUnavailableError(RuntimeError):
    """Raised when Redis is required but unavailable. Fail clearly; do not degrade silently."""


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int
    misses: int
    hit_rate: float
    total_size_bytes: int
    evictions: int


# Cache configuration by data type
CACHE_CONFIG = {
    "projects": {
        "ttl": TTL_EXTENDED,  # 10 minutes - projects list rarely changes
        "prefix": "projects",
    },
    "project": {
        "ttl": TTL_LONG,  # 5 minutes - individual project
        "prefix": "project",
    },
    "items": {
        "ttl": TTL_SHORT,  # 1 minute - items change more frequently
        "prefix": "items",
    },
    "links": {
        "ttl": TTL_SHORT,  # 1 minute - links change frequently
        "prefix": "links",
    },
    "graph": {
        "ttl": TTL_LONG,  # 5 minutes - graph is expensive to compute
        "prefix": "graph",
    },
    "graph_full": {
        "ttl": TTL_EXTENDED,  # 10 minutes - full graph projection
        "prefix": "graph_full",
    },
    "ancestors": {
        "ttl": TTL_LONG,  # 5 minutes - ancestry traversal
        "prefix": "ancestors",
    },
    "descendants": {
        "ttl": TTL_LONG,  # 5 minutes - descendant traversal
        "prefix": "descendants",
    },
    "impact": {
        "ttl": TTL_STANDARD,  # 3 minutes - impact analysis is more volatile
        "prefix": "impact",
    },
    "search": {
        "ttl": TTL_MEDIUM,  # 2 minutes - search results
        "prefix": "search",
    },
    "system": {
        "ttl": TTL_VERY_SHORT,  # 30 seconds - system status
        "prefix": "system",
    },
}


class CacheService:
    """Service for caching using async Redis."""

    _instance: CacheService | None = None

    def __init__(self, redis_url: str | None = None) -> None:
        """Initialize cache service.

        Args:
            redis_url: Redis connection URL (default: redis://localhost:6379)
        """
        if not REDIS_AVAILABLE:
            msg = "Redis client library not available (redis.asyncio)"
            raise RuntimeError(msg)

        redis_url = redis_url or "redis://localhost:6379"
        try:
            self.redis_client = aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=DEFAULT_POOL_SIZE,  # Connection pooling
            )
            logger.info("CacheService initialized with Redis at %s", redis_url)
        except Exception as e:
            # Required dependency: fail clearly, do not degrade silently (CLAUDE.md).
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e

        self.stats = {
            "hits": ZERO,
            "misses": ZERO,
            "evictions": ZERO,
        }

    @classmethod
    def get_instance(cls, redis_url: str | None = None) -> CacheService:
        """Get singleton instance of CacheService."""
        if cls._instance is None:
            cls._instance = cls(redis_url)
        return cls._instance

    def _generate_key(self, cache_type: str, **kwargs: object) -> str:
        """Generate cache key from type and parameters."""
        config = CACHE_CONFIG.get(cache_type, {"prefix": cache_type})
        prefix = config["prefix"]

        # Build key string from sorted kwargs
        key_parts = [f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None]
        key_str = f"{prefix}:" + ":".join(key_parts) if key_parts else prefix

        # Hash for consistent key length (non-cryptographic use)
        key_hash = hashlib.sha256(str(key_str).encode()).hexdigest()[:HASH_SIZE_STANDARD]
        return f"tracertm:{prefix}:{key_hash}"

    def _get_ttl(self, cache_type: str) -> int:
        """Get TTL for cache type."""
        config = CACHE_CONFIG.get(cache_type, {"ttl": TTL_LONG})
        ttl = config.get("ttl", TTL_LONG)
        if isinstance(ttl, (int, float, str)):
            return int(ttl)
        return TTL_LONG

    async def get(self, key: str) -> object | None:
        """Get value from cache. Raises RedisUnavailableError on connection failure (required service)."""
        try:
            value = await self.redis_client.get(key)
            if value:
                self.stats["hits"] += 1
                return json.loads(value)
            self.stats["misses"] += 1
        except (RedisUnavailableError, RuntimeError):
            raise
        except Exception as e:
            # Redis connection/timeout: fail clearly, do not return None (CLAUDE.md).
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e
        else:
            return None

    async def set(
        self,
        key: str,
        value: object,
        ttl_seconds: int | None = None,
        cache_type: str | None = None,
    ) -> bool:
        """Set value in cache. Raises RedisUnavailableError on connection failure (required service)."""
        if ttl_seconds is None and cache_type:
            ttl_seconds = self._get_ttl(cache_type)
        elif ttl_seconds is None:
            ttl_seconds = 300  # Default 5 minutes

        try:
            await self.redis_client.setex(
                key,
                ttl_seconds,
                json.dumps(value, default=str),
            )
        except (RedisUnavailableError, RuntimeError):
            raise
        except Exception as e:
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e
        else:
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache. Raises RedisUnavailableError on connection failure (required service)."""
        try:
            await self.redis_client.delete(key)
        except (RedisUnavailableError, RuntimeError):
            raise
        except Exception as e:
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e
        else:
            return True

    async def invalidate(self, cache_type: str, **kwargs: object) -> bool:
        """Invalidate cache for a specific type and parameters.

        Args:
            cache_type: Type of cache to invalidate
            **kwargs: object: Parameters to identify specific cache entry

        Returns:
            True if successful, False otherwise
        """
        key = self._generate_key(cache_type, **kwargs)
        return await self.delete(key)

    async def clear(self) -> bool:
        """Clear all cache entries. Raises RedisUnavailableError on connection failure (required service)."""
        try:
            await self.redis_client.flushdb()
            self.stats = {"hits": 0, "misses": 0, "evictions": 0}
        except (RedisUnavailableError, RuntimeError):
            raise
        except Exception as e:
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e
        else:
            return True

    async def clear_prefix(self, prefix: str) -> int:
        """Clear all cache entries with given prefix.

        Raises RedisUnavailableError on connection failure (required service).
        """
        try:
            pattern = f"tracertm:{prefix}:*"
            keys = [k async for k in self.redis_client.scan_iter(pattern)]

            if keys:
                deleted: int = await self.redis_client.delete(*keys)
                return deleted
        except (RedisUnavailableError, RuntimeError):
            raise
        except Exception as e:
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e
        else:
            return 0

    async def invalidate_project(self, project_id: str) -> int:
        """Invalidate all cache entries for a project.

        Raises RedisUnavailableError on connection failure (required service).
        """
        total_deleted = 0

        # Invalidate project-specific caches
        for cache_type in ["project", "items", "links", "graph", "graph_full", "ancestors", "descendants", "impact"]:
            key = self._generate_key(cache_type, project_id=project_id)
            if await self.delete(key):
                total_deleted += 1

        # Also clear prefix-based entries
        total_deleted += await self.clear_prefix(f"graph:{project_id}")
        total_deleted += await self.clear_prefix(f"items:{project_id}")

        return total_deleted

    async def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats object
        """
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        try:
            info = await self.redis_client.info("memory")
            total_size = info.get("used_memory", 0)
        except (RedisUnavailableError, RuntimeError):
            raise
        except Exception as e:
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e

        return CacheStats(
            hits=self.stats["hits"],
            misses=self.stats["misses"],
            hit_rate=hit_rate,
            total_size_bytes=total_size,
            evictions=self.stats["evictions"],
        )

    async def health_check(self) -> bool:
        """Check if Redis is healthy. Raises RedisUnavailableError when Redis is down (required service)."""
        try:
            await self.redis_client.ping()
        except (RedisUnavailableError, RuntimeError):
            raise
        except Exception as e:
            msg = f"Redis unavailable: {e}"
            raise RedisUnavailableError(msg) from e
        else:
            return True


# Cached operations helper functions
async def cached_get(
    cache: CacheService,
    cache_type: str,
    fetch_fn: Any,
    **kwargs: object,
) -> object:
    """Get value from cache or fetch and cache it.

    Args:
        cache: CacheService instance
        cache_type: Type of cache for key generation and TTL
        fetch_fn: Async function to fetch data if not cached
        **kwargs: object: Parameters for cache key and fetch function

    Returns:
        Cached or freshly fetched value
    """
    key = cache._generate_key(cache_type, **kwargs)

    # Try cache first
    cached = await cache.get(key)
    if cached is not None:
        return cached

    # Fetch and cache
    result = await fetch_fn()
    await cache.set(key, result, cache_type=cache_type)

    return result


@lru_cache
def get_cache_service() -> CacheService:
    """Get singleton CacheService for dependency injection."""
    return CacheService.get_instance()
