"""Chaos Test: Cache (Redis) Resilience.

Tests that the CacheService fails clearly when Redis is unavailable (per CLAUDE.md:
required dependencies must fail explicitly, not degrade silently). Also tests the
cached_get helper to ensure it propagates Redis errors correctly.

Uses unittest.mock to simulate Redis failures without a live Redis instance.
"""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from tracertm.services.cache_service import (
    CacheService,
    RedisUnavailableError,
    cached_get,
)


@pytest.fixture
def cache_service() -> None:
    """Build a CacheService with a mocked Redis client (no real connection)."""
    with patch("tracertm.services.cache_service.aioredis") as mock_aioredis:
        mock_client = AsyncMock()
        mock_aioredis.from_url.return_value = mock_client
        svc = CacheService(redis_url="redis://fake:6379")
        yield svc, mock_client


@pytest.mark.chaos
class TestCacheGetFailure:
    """CacheService.get() must raise RedisUnavailableError when Redis is down."""

    @pytest.mark.asyncio
    async def test_get_raises_on_connection_refused(self, cache_service: Any) -> None:
        """Simulate ConnectionRefusedError from Redis -- must surface as RedisUnavailableError."""
        svc, mock_client = cache_service
        mock_client.get.side_effect = ConnectionRefusedError("Connection refused")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.get("some:key")

    @pytest.mark.asyncio
    async def test_get_raises_on_timeout(self, cache_service: Any) -> None:
        """Simulate a timeout from Redis -- must surface as RedisUnavailableError."""
        svc, mock_client = cache_service
        mock_client.get.side_effect = TimeoutError("Read timed out")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.get("some:key")

    @pytest.mark.asyncio
    async def test_get_raises_on_broken_pipe(self, cache_service: Any) -> None:
        """Simulate BrokenPipeError mid-read -- must surface as RedisUnavailableError."""
        svc, mock_client = cache_service
        mock_client.get.side_effect = BrokenPipeError("Broken pipe")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.get("some:key")


@pytest.mark.chaos
class TestCacheSetFailure:
    """CacheService.set() must raise RedisUnavailableError when Redis is down."""

    @pytest.mark.asyncio
    async def test_set_raises_on_connection_refused(self, cache_service: Any) -> None:
        svc, mock_client = cache_service
        mock_client.setex.side_effect = ConnectionRefusedError("Connection refused")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.set("key", {"data": 1}, ttl_seconds=60)

    @pytest.mark.asyncio
    async def test_set_raises_on_os_error(self, cache_service: Any) -> None:
        svc, mock_client = cache_service
        mock_client.setex.side_effect = OSError("Network unreachable")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.set("key", {"data": 1}, ttl_seconds=60)


@pytest.mark.chaos
class TestCacheDeleteAndClearFailure:
    """delete() and clear() must raise RedisUnavailableError when Redis is down."""

    @pytest.mark.asyncio
    async def test_delete_raises_on_connection_error(self, cache_service: Any) -> None:
        svc, mock_client = cache_service
        mock_client.delete.side_effect = ConnectionRefusedError("Connection refused")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.delete("key")

    @pytest.mark.asyncio
    async def test_clear_raises_on_connection_error(self, cache_service: Any) -> None:
        svc, mock_client = cache_service
        mock_client.flushdb.side_effect = ConnectionRefusedError("Connection refused")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.clear()


@pytest.mark.chaos
class TestCacheHealthCheckFailure:
    """health_check must raise RedisUnavailableError when ping fails."""

    @pytest.mark.asyncio
    async def test_health_check_raises_on_unreachable(self, cache_service: Any) -> None:
        svc, mock_client = cache_service
        mock_client.ping.side_effect = ConnectionRefusedError("Connection refused")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.health_check()

    @pytest.mark.asyncio
    async def test_health_check_passes_when_healthy(self, cache_service: Any) -> None:
        svc, mock_client = cache_service
        mock_client.ping.return_value = True

        result = await svc.health_check()
        assert result is True


@pytest.mark.chaos
class TestCachedGetHelperResilience:
    """cached_get must propagate RedisUnavailableError from the underlying cache, not swallow it."""

    @pytest.mark.asyncio
    async def test_cached_get_propagates_redis_error_on_read(self, cache_service: Any) -> None:
        """If cache.get() fails with RedisUnavailableError, cached_get must re-raise."""
        svc, mock_client = cache_service
        mock_client.get.side_effect = ConnectionRefusedError("Connection refused")

        fetch_fn = AsyncMock(return_value={"items": []})

        with pytest.raises(RedisUnavailableError):
            await cached_get(svc, "items", fetch_fn, project_id="p1")

        # fetch_fn must NOT have been called -- the error happened before fallthrough
        fetch_fn.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cached_get_propagates_redis_error_on_write(self, cache_service: Any) -> None:
        """If cache.get() returns None (miss) but cache.set() fails, cached_get must re-raise."""
        svc, mock_client = cache_service
        # Cache miss
        mock_client.get.return_value = None
        # Write fails
        mock_client.setex.side_effect = ConnectionRefusedError("Connection refused")

        fetch_fn = AsyncMock(return_value={"items": [1, 2, 3]})

        with pytest.raises(RedisUnavailableError):
            await cached_get(svc, "items", fetch_fn, project_id="p1")

        # fetch_fn should have been called (cache miss triggers fetch)
        fetch_fn.assert_awaited_once()


@pytest.mark.chaos
class TestCacheStatsUnderFailure:
    """get_stats must raise RedisUnavailableError when info() call fails."""

    @pytest.mark.asyncio
    async def test_get_stats_raises_on_connection_error(self, cache_service: Any) -> None:
        svc, mock_client = cache_service
        mock_client.info.side_effect = ConnectionRefusedError("Connection refused")

        with pytest.raises(RedisUnavailableError, match="Redis unavailable"):
            await svc.get_stats()


@pytest.mark.chaos
class TestCacheKeyGeneration:
    """Key generation must be deterministic and handle edge cases."""

    def test_generate_key_is_deterministic(self, cache_service: Any) -> None:
        svc, _ = cache_service
        k1 = svc._generate_key("items", project_id="abc")
        k2 = svc._generate_key("items", project_id="abc")
        assert k1 == k2

    def test_generate_key_different_inputs_different_keys(self, cache_service: Any) -> None:
        svc, _ = cache_service
        k1 = svc._generate_key("items", project_id="abc")
        k2 = svc._generate_key("items", project_id="xyz")
        assert k1 != k2

    def test_generate_key_includes_prefix(self, cache_service: Any) -> None:
        svc, _ = cache_service
        key = svc._generate_key("graph", project_id="p1")
        assert key.startswith("tracertm:graph:")
