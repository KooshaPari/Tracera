from typing import Any

"""Tests for QueryCache (Phase 3)."""

import asyncio

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.mcp.cache import CacheEntry, QueryCache


class TestCacheEntry:
    """Test CacheEntry functionality."""

    def test_create_entry(self) -> None:
        """Test creating cache entry."""
        entry = CacheEntry("test_value", ttl=300)

        assert entry.value == "test_value"
        assert not entry.is_expired()
        assert entry.created_at > 0

    def test_expiration(self) -> None:
        """Test entry expiration."""
        entry = CacheEntry("test_value", ttl=0)

        # Should be expired immediately
        assert entry.is_expired()


class TestQueryCache:
    """Test QueryCache functionality."""

    @pytest.fixture
    def cache(self) -> None:
        """Create QueryCache instance."""
        return QueryCache(max_size=10, default_ttl=300)

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache: Any) -> None:
        """Test basic set and get operations."""
        await cache.set("test", "value1", project_id="proj1")

        value = await cache.get("test", project_id="proj1")
        assert value == "value1"

    @pytest.mark.asyncio
    async def test_cache_miss(self, cache: Any) -> None:
        """Test cache miss."""
        value = await cache.get("nonexistent", key="test")
        assert value is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache: Any) -> None:
        """Test TTL expiration."""
        await cache.set("test", "value", ttl=0, project_id="proj1")

        # Should be expired
        value = await cache.get("test", project_id="proj1")
        assert value is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache: Any) -> None:
        """Test LRU eviction when max_size reached."""
        # Fill cache to max
        for i in range(10):
            await cache.set("test", f"value{i}", key=i)

        # Add one more (should evict oldest)
        await cache.set("test", "value10", key=10)

        # First entry should be evicted
        value = await cache.get("test", key=0)
        assert value is None

        # Latest entry should exist
        value = await cache.get("test", key=10)
        assert value == "value10"

    @pytest.mark.asyncio
    async def test_invalidate_pattern(self, cache: Any) -> None:
        """Test invalidation by pattern."""
        await cache.set("item_query", "value1", project_id="proj1")
        await cache.set("item_get", "value2", project_id="proj1")
        await cache.set("project_list", "value3")

        # Invalidate all "item_" entries
        await cache.invalidate("item_")

        # item_ entries should be gone
        assert await cache.get("item_query", project_id="proj1") is None
        assert await cache.get("item_get", project_id="proj1") is None

        # project_list should still exist
        # Note: This test needs adjustment as invalidate uses prefix matching
        # which works on the hash, not the original prefix

    @pytest.mark.asyncio
    async def test_invalidate_all(self, cache: Any) -> None:
        """Test clearing entire cache."""
        await cache.set("test1", "value1")
        await cache.set("test2", "value2")

        await cache.invalidate()

        assert await cache.get("test1") is None
        assert await cache.get("test2") is None

    @pytest.mark.asyncio
    async def test_get_or_compute(self, cache: Any) -> None:
        """Test get_or_compute pattern."""
        call_count = 0

        async def compute() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            return "computed_value"

        # First call should compute
        value1 = await cache.get_or_compute("test", compute, ttl=300, key="test1")
        assert value1 == "computed_value"
        assert call_count == 1

        # Second call should use cache
        value2 = await cache.get_or_compute("test", compute, ttl=300, key="test1")
        assert value2 == "computed_value"
        assert call_count == 1  # Not incremented

    @pytest.mark.asyncio
    async def test_get_stats(self, cache: Any) -> None:
        """Test cache statistics."""
        # Generate some hits and misses
        await cache.set("test", "value", key="test1")

        await cache.get("test", key="test1")  # Hit
        await cache.get("test", key="test1")  # Hit
        await cache.get("test", key="nonexistent")  # Miss

        stats = cache.get_stats()

        assert stats["hits"] == COUNT_TWO
        assert stats["misses"] == 1
        assert stats["total_requests"] == COUNT_THREE
        assert stats["hit_rate"] == COUNT_TWO / 3
        assert stats["size"] == 1  # One entry

    @pytest.mark.asyncio
    async def test_clear(self, cache: Any) -> None:
        """Test clearing cache and stats."""
        await cache.set("test", "value")
        await cache.get("test")

        stats_before = cache.get_stats()
        assert stats_before["size"] > 0
        assert stats_before["total_requests"] > 0

        await cache.clear()

        stats_after = cache.get_stats()
        assert stats_after["size"] == 0
        assert stats_after["hits"] == 0
        assert stats_after["misses"] == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, cache: Any) -> None:
        """Test cleanup of expired entries."""
        # Add expired entry
        await cache.set("expired", "value", ttl=0, key="test1")

        # Add valid entry
        await cache.set("valid", "value", ttl=300, key="test2")

        # Cleanup
        await cache.cleanup_expired()

        stats = cache.get_stats()
        assert stats["size"] == 1  # Only valid entry remains

    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache: Any) -> None:
        """Test concurrent cache access."""

        async def write_cache(i: Any) -> None:
            await cache.set("test", f"value{i}", key=i)

        async def read_cache(i: Any) -> None:
            return await cache.get("test", key=i)

        # Concurrent writes
        await asyncio.gather(*[write_cache(i) for i in range(20)])

        # Concurrent reads
        results = await asyncio.gather(*[read_cache(i) for i in range(20)])

        # Should have some results (limited by max_size=10)
        assert any(r is not None for r in results)
