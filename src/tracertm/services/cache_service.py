"""Caching service for TraceRTM using Redis."""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int
    misses: int
    hit_rate: float
    total_size_bytes: int
    evictions: int


class CacheService:
    """Service for caching using Redis."""

    def __init__(self, redis_url: str | None = None):
        """
        Initialize cache service.

        Args:
            redis_url: Redis connection URL (default: redis://localhost:6379)
        """
        if not REDIS_AVAILABLE:
            self.redis_client = None
            return

        redis_url = redis_url or "redis://localhost:6379"
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
        except Exception:
            self.redis_client = None

        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }

    def _generate_key(self, prefix: str, **kwargs: Any) -> str:
        """Generate cache key from prefix and parameters."""
        key_str = f"{prefix}:" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.redis_client:
            self.stats["misses"] += 1
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                self.stats["hits"] += 1
                return json.loads(value)
            else:
                self.stats["misses"] += 1
                return None
        except Exception:
            self.stats["misses"] += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 3600,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.setex(
                key,
                ttl_seconds,
                json.dumps(value),
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False

    async def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            self.stats = {"hits": 0, "misses": 0, "evictions": 0}
            return True
        except Exception:
            return False

    async def clear_prefix(self, prefix: str) -> int:
        """
        Clear all cache entries with given prefix.

        Args:
            prefix: Cache key prefix

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        try:
            pattern = f"{prefix}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted: int = self.redis_client.delete(*keys)
                return deleted
            return 0
        except Exception:
            return 0

    async def get_stats(self) -> CacheStats:
        """
        Get cache statistics.

        Returns:
            CacheStats object
        """
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        total_size = 0
        if self.redis_client:
            try:
                info = self.redis_client.info("memory")
                total_size = info.get("used_memory", 0)
            except Exception:
                pass

        return CacheStats(
            hits=self.stats["hits"],
            misses=self.stats["misses"],
            hit_rate=hit_rate,
            total_size_bytes=total_size,
            evictions=self.stats["evictions"],
        )
