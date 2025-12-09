"""
Comprehensive tests for CacheService.

Tests all methods: get, set, delete, clear, clear_prefix, get_stats.

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

from tracertm.services.cache_service import CacheService, CacheStats, REDIS_AVAILABLE


class TestCacheStats:
    """Test CacheStats dataclass."""

    def test_cache_stats_fields(self):
        """Test CacheStats has correct fields."""
        stats = CacheStats(
            hits=10,
            misses=5,
            hit_rate=66.67,
            total_size_bytes=1024,
            evictions=2,
        )
        assert stats.hits == 10
        assert stats.misses == 5
        assert stats.hit_rate == 66.67
        assert stats.total_size_bytes == 1024
        assert stats.evictions == 2


class TestCacheServiceInit:
    """Test CacheService initialization."""

    @patch.dict("tracertm.services.cache_service.__dict__", {"REDIS_AVAILABLE": False})
    def test_init_without_redis_available(self):
        """Test initialization when redis not installed."""
        with patch("tracertm.services.cache_service.REDIS_AVAILABLE", False):
            service = CacheService()
            assert service.redis_client is None

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    def test_init_with_redis_connection_success(self, mock_redis):
        """Test initialization with successful Redis connection."""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        service = CacheService("redis://localhost:6379")

        mock_redis.from_url.assert_called_once()
        mock_client.ping.assert_called_once()

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    def test_init_with_redis_connection_failure(self, mock_redis):
        """Test initialization with Redis connection failure."""
        mock_redis.from_url.side_effect = Exception("Connection failed")

        service = CacheService()

        assert service.redis_client is None

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    def test_init_default_url(self, mock_redis):
        """Test initialization uses default URL when none provided."""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        service = CacheService()

        mock_redis.from_url.assert_called_with(
            "redis://localhost:6379", decode_responses=True
        )


class TestGenerateKey:
    """Test _generate_key method."""

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    def test_generate_key_creates_hash(self):
        """Test key generation creates MD5 hash."""
        service = CacheService()

        key = service._generate_key("prefix", param1="value1", param2="value2")

        assert len(key) == 32  # MD5 hash length
        assert isinstance(key, str)

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    def test_generate_key_deterministic(self):
        """Test key generation is deterministic."""
        service = CacheService()

        key1 = service._generate_key("test", a="1", b="2")
        key2 = service._generate_key("test", a="1", b="2")

        assert key1 == key2

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    def test_generate_key_different_params_different_key(self):
        """Test different params produce different keys."""
        service = CacheService()

        key1 = service._generate_key("test", a="1")
        key2 = service._generate_key("test", a="2")

        assert key1 != key2


class TestCacheGet:
    """Test get method."""

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    @pytest.mark.asyncio
    async def test_get_without_redis(self):
        """Test get returns None when Redis unavailable."""
        service = CacheService()
        # Manually set stats since it's only initialized when Redis is available
        service.stats = {"hits": 0, "misses": 0, "evictions": 0}

        result = await service.get("some_key")

        assert result is None
        assert service.stats["misses"] == 1

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_get_cache_hit(self, mock_redis):
        """Test get returns cached value on hit."""
        mock_client = Mock()
        mock_client.get.return_value = '{"key": "value"}'
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.get("my_key")

        assert result == {"key": "value"}
        assert service.stats["hits"] == 1

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_get_cache_miss(self, mock_redis):
        """Test get returns None on cache miss."""
        mock_client = Mock()
        mock_client.get.return_value = None
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.get("missing_key")

        assert result is None
        assert service.stats["misses"] == 1

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_get_handles_exception(self, mock_redis):
        """Test get handles Redis exceptions."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.get("error_key")

        assert result is None
        assert service.stats["misses"] == 1


class TestCacheSet:
    """Test set method."""

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    @pytest.mark.asyncio
    async def test_set_without_redis(self):
        """Test set returns False when Redis unavailable."""
        service = CacheService()

        result = await service.set("key", "value")

        assert result is False

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_set_success(self, mock_redis):
        """Test successful cache set."""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.set("my_key", {"data": "test"}, ttl_seconds=60)

        assert result is True
        mock_client.setex.assert_called_once_with(
            "my_key", 60, '{"data": "test"}'
        )

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_set_default_ttl(self, mock_redis):
        """Test set uses default TTL."""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        await service.set("key", "value")

        # Default TTL is 3600 seconds
        call_args = mock_client.setex.call_args
        assert call_args[0][1] == 3600

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_set_handles_exception(self, mock_redis):
        """Test set handles Redis exceptions."""
        mock_client = Mock()
        mock_client.setex.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.set("key", "value")

        assert result is False


class TestCacheDelete:
    """Test delete method."""

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    @pytest.mark.asyncio
    async def test_delete_without_redis(self):
        """Test delete returns False when Redis unavailable."""
        service = CacheService()

        result = await service.delete("key")

        assert result is False

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_delete_success(self, mock_redis):
        """Test successful cache delete."""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.delete("my_key")

        assert result is True
        mock_client.delete.assert_called_once_with("my_key")

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_delete_handles_exception(self, mock_redis):
        """Test delete handles Redis exceptions."""
        mock_client = Mock()
        mock_client.delete.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.delete("key")

        assert result is False


class TestCacheClear:
    """Test clear method."""

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    @pytest.mark.asyncio
    async def test_clear_without_redis(self):
        """Test clear returns False when Redis unavailable."""
        service = CacheService()

        result = await service.clear()

        assert result is False

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_clear_success(self, mock_redis):
        """Test successful cache clear."""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        service.stats["hits"] = 10
        service.stats["misses"] = 5

        result = await service.clear()

        assert result is True
        mock_client.flushdb.assert_called_once()
        assert service.stats["hits"] == 0
        assert service.stats["misses"] == 0

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_clear_handles_exception(self, mock_redis):
        """Test clear handles Redis exceptions."""
        mock_client = Mock()
        mock_client.flushdb.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.clear()

        assert result is False


class TestCacheClearPrefix:
    """Test clear_prefix method."""

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    @pytest.mark.asyncio
    async def test_clear_prefix_without_redis(self):
        """Test clear_prefix returns 0 when Redis unavailable."""
        service = CacheService()

        result = await service.clear_prefix("prefix")

        assert result == 0

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_clear_prefix_success(self, mock_redis):
        """Test successful prefix clear."""
        mock_client = Mock()
        mock_client.keys.return_value = ["prefix:key1", "prefix:key2", "prefix:key3"]
        mock_client.delete.return_value = 3
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.clear_prefix("prefix")

        assert result == 3
        mock_client.keys.assert_called_once_with("prefix:*")

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_clear_prefix_no_matches(self, mock_redis):
        """Test clear_prefix with no matching keys."""
        mock_client = Mock()
        mock_client.keys.return_value = []
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.clear_prefix("nonexistent")

        assert result == 0
        mock_client.delete.assert_not_called()

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_clear_prefix_handles_exception(self, mock_redis):
        """Test clear_prefix handles Redis exceptions."""
        mock_client = Mock()
        mock_client.keys.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        result = await service.clear_prefix("prefix")

        assert result == 0


class TestGetStats:
    """Test get_stats method."""

    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", False)
    @pytest.mark.asyncio
    async def test_get_stats_without_redis(self):
        """Test get_stats without Redis connection."""
        service = CacheService()
        service.stats = {"hits": 5, "misses": 10, "evictions": 0}

        result = await service.get_stats()

        assert result.hits == 5
        assert result.misses == 10
        assert result.hit_rate == pytest.approx(33.33, rel=0.1)
        assert result.total_size_bytes == 0

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_get_stats_with_redis(self, mock_redis):
        """Test get_stats with Redis connection."""
        mock_client = Mock()
        mock_client.info.return_value = {"used_memory": 2048}
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        service.stats["hits"] = 8
        service.stats["misses"] = 2

        result = await service.get_stats()

        assert result.hits == 8
        assert result.misses == 2
        assert result.hit_rate == 80.0
        assert result.total_size_bytes == 2048

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_get_stats_zero_requests(self, mock_redis):
        """Test get_stats with zero cache requests."""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        service = CacheService()

        result = await service.get_stats()

        assert result.hit_rate == 0.0

    @patch("tracertm.services.cache_service.redis")
    @patch("tracertm.services.cache_service.REDIS_AVAILABLE", True)
    @pytest.mark.asyncio
    async def test_get_stats_handles_info_exception(self, mock_redis):
        """Test get_stats handles Redis info exception."""
        mock_client = Mock()
        mock_client.info.side_effect = Exception("Info error")
        mock_redis.from_url.return_value = mock_client

        service = CacheService()
        service.stats["hits"] = 5
        service.stats["misses"] = 5

        result = await service.get_stats()

        # Should return 0 for size on error
        assert result.total_size_bytes == 0
        assert result.hit_rate == 50.0
