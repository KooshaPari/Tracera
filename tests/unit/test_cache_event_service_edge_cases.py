"""Phase 15A: Quick Wins - Service Layer Edge Cases.

Focus: Edge cases and boundary conditions for services
Target: EventService, CacheService
Coverage Goal: Increase coverage by testing edge cases
"""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.services.cache_service import CacheService, CacheStats
from tracertm.services.event_service import EventService


class TestCacheServiceEdgeCases:
    """Edge cases for CacheService."""

    def test_cache_service_init_without_redis(self) -> None:
        """Test cache service initialization when redis is not available."""
        with patch("tracertm.services.cache_service.REDIS_AVAILABLE", False):
            service = CacheService()
            assert service.redis_client is None

    def test_cache_service_init_with_default_url(self) -> None:
        """Test cache service initialization with default Redis URL."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True

            CacheService()
            mock_redis.assert_called_once_with("redis://localhost:6379", decode_responses=True)

    def test_cache_service_init_with_custom_url(self) -> None:
        """Test cache service initialization with custom Redis URL."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True

            CacheService(redis_url="redis://custom:6380")
            mock_redis.assert_called_once_with("redis://custom:6380", decode_responses=True)

    def test_cache_service_init_connection_failure(self) -> None:
        """Test cache service handles connection failure gracefully."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_redis.side_effect = Exception("Connection failed")

            service = CacheService()
            assert service.redis_client is None

    def test_cache_service_init_ping_failure(self) -> None:
        """Test cache service handles ping failure gracefully."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.ping.side_effect = Exception("Ping failed")

            service = CacheService()
            assert service.redis_client is None

    def test_cache_service_stats_initialization(self) -> None:
        """Test that stats are properly initialized."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            service = CacheService()
            assert service.stats["hits"] == 0
            assert service.stats["misses"] == 0
            assert service.stats["evictions"] == 0

    def test_generate_key_simple(self) -> None:
        """Test cache key generation with simple parameters."""
        with patch("tracertm.services.cache_service.redis.from_url"):
            service = CacheService()
            key = service._generate_key("prefix", id="123", type="item")

            # Key should be MD5 hash
            assert len(key) == 32  # MD5 hex digest length
            assert isinstance(key, str)

    def test_generate_key_deterministic(self) -> None:
        """Test that key generation is deterministic."""
        with patch("tracertm.services.cache_service.redis.from_url"):
            service = CacheService()
            key1 = service._generate_key("prefix", id="123", type="item")
            key2 = service._generate_key("prefix", id="123", type="item")
            assert key1 == key2

    def test_generate_key_order_independent(self) -> None:
        """Test that key generation is parameter order independent."""
        with patch("tracertm.services.cache_service.redis.from_url"):
            service = CacheService()
            key1 = service._generate_key("prefix", id="123", type="item")
            key2 = service._generate_key("prefix", type="item", id="123")
            assert key1 == key2

    def test_generate_key_different_values(self) -> None:
        """Test that different values generate different keys."""
        with patch("tracertm.services.cache_service.redis.from_url"):
            service = CacheService()
            key1 = service._generate_key("prefix", id="123")
            key2 = service._generate_key("prefix", id="456")
            assert key1 != key2

    def test_generate_key_empty_params(self) -> None:
        """Test key generation with no parameters."""
        with patch("tracertm.services.cache_service.redis.from_url"):
            service = CacheService()
            key = service._generate_key("prefix")
            assert len(key) == 32

    def test_generate_key_special_characters(self) -> None:
        """Test key generation with special characters."""
        with patch("tracertm.services.cache_service.redis.from_url"):
            service = CacheService()
            key = service._generate_key("prefix", value="test@#$%^&*()")
            assert len(key) == 32

    @pytest.mark.asyncio
    async def test_get_without_redis_client(self) -> None:
        """Test get operation when redis client is None."""
        with patch("tracertm.services.cache_service.REDIS_AVAILABLE", False):
            service = CacheService()
            result = await service.get("test-key")
            assert result is None
            assert service.stats["misses"] == 1

    @pytest.mark.asyncio
    async def test_get_cache_hit(self) -> None:
        """Test successful cache hit."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            test_data = {"key": "value"}
            mock_client.get.return_value = json.dumps(test_data)

            service = CacheService()
            result = await service.get("test-key")

            assert result == test_data
            assert service.stats["hits"] == 1
            assert service.stats["misses"] == 0

    @pytest.mark.asyncio
    async def test_get_cache_miss(self) -> None:
        """Test cache miss."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.get.return_value = None

            service = CacheService()
            result = await service.get("test-key")

            assert result is None
            assert service.stats["misses"] == 1
            assert service.stats["hits"] == 0

    @pytest.mark.asyncio
    async def test_get_with_exception(self) -> None:
        """Test get operation when exception occurs."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.get.side_effect = Exception("Redis error")

            service = CacheService()
            result = await service.get("test-key")

            assert result is None
            assert service.stats["misses"] == 1

    @pytest.mark.asyncio
    async def test_get_with_invalid_json(self) -> None:
        """Test get operation with invalid JSON data."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.get.return_value = "invalid json {"

            service = CacheService()
            result = await service.get("test-key")

            # Should return None on JSON decode error
            assert result is None or service.stats["misses"] >= 1

    @pytest.mark.asyncio
    async def test_set_without_redis_client(self) -> None:
        """Test set operation when redis client is None."""
        with patch("tracertm.services.cache_service.REDIS_AVAILABLE", False):
            service = CacheService()
            result = await service.set("test-key", {"data": "value"})
            assert result is False

    @pytest.mark.asyncio
    async def test_set_success(self) -> None:
        """Test successful set operation."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            service = CacheService()
            result = await service.set("test-key", {"data": "value"})

            assert result is True
            mock_client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self) -> None:
        """Test set operation with custom TTL."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            service = CacheService()
            await service.set("test-key", {"data": "value"}, ttl_seconds=7200)

            # Verify TTL parameter
            call_args = mock_client.setex.call_args
            assert call_args[0][1] == 7200  # TTL should be 7200

    @pytest.mark.asyncio
    async def test_set_with_complex_data(self) -> None:
        """Test set operation with complex nested data."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            service = CacheService()
            complex_data = {
                "nested": {"data": [1, 2, 3]},
                "list": ["a", "b", "c"],
                "number": 42,
            }
            result = await service.set("test-key", complex_data)

            assert result is True

    @pytest.mark.asyncio
    async def test_set_with_exception(self) -> None:
        """Test set operation when exception occurs."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.setex.side_effect = Exception("Redis error")

            service = CacheService()
            result = await service.set("test-key", {"data": "value"})

            assert result is False

    @pytest.mark.asyncio
    async def test_delete_without_redis_client(self) -> None:
        """Test delete operation when redis client is None."""
        with patch("tracertm.services.cache_service.REDIS_AVAILABLE", False):
            service = CacheService()
            result = await service.delete("test-key")
            assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self) -> None:
        """Test successful delete operation."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            service = CacheService()
            result = await service.delete("test-key")

            assert result is True
            mock_client.delete.assert_called_once_with("test-key")

    @pytest.mark.asyncio
    async def test_delete_with_exception(self) -> None:
        """Test delete operation when exception occurs."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.delete.side_effect = Exception("Redis error")

            service = CacheService()
            result = await service.delete("test-key")

            assert result is False

    @pytest.mark.asyncio
    async def test_clear_without_redis_client(self) -> None:
        """Test clear operation when redis client is None."""
        with patch("tracertm.services.cache_service.REDIS_AVAILABLE", False):
            service = CacheService()
            result = await service.clear()
            assert result is False

    @pytest.mark.asyncio
    async def test_clear_success(self) -> None:
        """Test successful clear operation."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            service = CacheService()
            service.stats = {"hits": 10, "misses": 5, "evictions": 2}

            result = await service.clear()

            assert result is True
            mock_client.flushdb.assert_called_once()
            # Stats should be reset
            assert service.stats["hits"] == 0
            assert service.stats["misses"] == 0

    @pytest.mark.asyncio
    async def test_clear_with_exception(self) -> None:
        """Test clear operation when exception occurs."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.flushdb.side_effect = Exception("Redis error")

            service = CacheService()
            result = await service.clear()

            assert result is False

    @pytest.mark.asyncio
    async def test_clear_prefix_without_redis_client(self) -> None:
        """Test clear_prefix operation when redis client is None."""
        with patch("tracertm.services.cache_service.REDIS_AVAILABLE", False):
            service = CacheService()
            result = await service.clear_prefix("test")
            assert result == 0

    @pytest.mark.asyncio
    async def test_clear_prefix_no_keys(self) -> None:
        """Test clear_prefix when no keys match."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.keys.return_value = []

            service = CacheService()
            result = await service.clear_prefix("test")

            assert result == 0

    @pytest.mark.asyncio
    async def test_clear_prefix_with_keys(self) -> None:
        """Test clear_prefix when keys are found."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.keys.return_value = ["test:1", "test:2", "test:3"]
            mock_client.delete.return_value = 3

            service = CacheService()
            result = await service.clear_prefix("test")

            assert result == COUNT_THREE
            mock_client.keys.assert_called_once_with("test:*")

    @pytest.mark.asyncio
    async def test_clear_prefix_with_exception(self) -> None:
        """Test clear_prefix operation when exception occurs."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.keys.side_effect = Exception("Redis error")

            service = CacheService()
            result = await service.clear_prefix("test")

            assert result == 0

    @pytest.mark.asyncio
    async def test_get_stats_no_operations(self) -> None:
        """Test get_stats with no cache operations."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            service = CacheService()
            stats = await service.get_stats()

            assert stats.hits == 0
            assert stats.misses == 0
            assert stats.hit_rate == 0
            assert stats.evictions == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_operations(self) -> None:
        """Test get_stats after cache operations."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.get.return_value = json.dumps({"data": "value"})

            service = CacheService()
            service.stats = {"hits": 7, "misses": 3, "evictions": 1}

            stats = await service.get_stats()

            assert stats.hits == 7
            assert stats.misses == COUNT_THREE
            assert stats.hit_rate == 70.0  # 7/10 * 100
            assert stats.evictions == 1

    @pytest.mark.asyncio
    async def test_get_stats_with_memory_info(self) -> None:
        """Test get_stats includes memory information."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.info.return_value = {"used_memory": 1024000}

            service = CacheService()
            stats = await service.get_stats()

            assert stats.total_size_bytes == 1024000

    @pytest.mark.asyncio
    async def test_get_stats_memory_error(self) -> None:
        """Test get_stats when memory info fails."""
        with patch("tracertm.services.cache_service.redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.info.side_effect = Exception("Info error")

            service = CacheService()
            stats = await service.get_stats()

            assert stats.total_size_bytes == 0


class TestEventServiceEdgeCases:
    """Edge cases for EventService."""

    @pytest.mark.asyncio
    async def test_event_service_init(self) -> None:
        """Test event service initialization."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        assert service.session is mock_session
        assert service.events is not None

    @pytest.mark.asyncio
    async def test_log_event_with_item_id(self) -> None:
        """Test logging event with item_id."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        mock_event = Mock()
        service.events.log = AsyncMock(return_value=mock_event)

        result = await service.log_event(
            project_id="proj-1",
            event_type="item_created",
            event_data={"title": "Test"},
            agent_id="agent-1",
            item_id="item-1",
        )

        assert result is mock_event
        service.events.log.assert_called_once_with(
            project_id="proj-1",
            event_type="item_created",
            entity_type="item",
            entity_id="item-1",
            data={"title": "Test"},
            agent_id="agent-1",
        )

    @pytest.mark.asyncio
    async def test_log_event_without_item_id(self) -> None:
        """Test logging event without item_id (project-level event)."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        mock_event = Mock()
        service.events.log = AsyncMock(return_value=mock_event)

        result = await service.log_event(
            project_id="proj-1",
            event_type="project_created",
            event_data={"name": "Test Project"},
            agent_id="agent-1",
        )

        assert result is mock_event
        service.events.log.assert_called_once_with(
            project_id="proj-1",
            event_type="project_created",
            entity_type="project",
            entity_id="proj-1",
            data={"name": "Test Project"},
            agent_id="agent-1",
        )

    @pytest.mark.asyncio
    async def test_log_event_with_empty_data(self) -> None:
        """Test logging event with empty data dictionary."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        mock_event = Mock()
        service.events.log = AsyncMock(return_value=mock_event)

        result = await service.log_event(project_id="proj-1", event_type="ping", event_data={}, agent_id="agent-1")

        assert result is mock_event

    @pytest.mark.asyncio
    async def test_log_event_with_complex_data(self) -> None:
        """Test logging event with complex nested data."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        mock_event = Mock()
        service.events.log = AsyncMock(return_value=mock_event)

        complex_data = {
            "changes": [{"field": "title", "old": "A", "new": "B"}, {"field": "status", "old": "todo", "new": "done"}],
            "metadata": {"user": "test", "timestamp": 123456},
        }

        result = await service.log_event(
            project_id="proj-1",
            event_type="item_updated",
            event_data=complex_data,
            agent_id="agent-1",
            item_id="item-1",
        )

        assert result is mock_event

    @pytest.mark.asyncio
    async def test_get_item_history(self) -> None:
        """Test retrieving item history."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        mock_events = [Mock(), Mock(), Mock()]
        service.events.get_by_entity = AsyncMock(return_value=mock_events)

        result = await service.get_item_history("item-1")

        assert result == mock_events
        service.events.get_by_entity.assert_called_once_with("item-1")

    @pytest.mark.asyncio
    async def test_get_item_history_no_events(self) -> None:
        """Test retrieving history for item with no events."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        service.events.get_by_entity = AsyncMock(return_value=[])

        result = await service.get_item_history("item-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_item_at_time(self) -> None:
        """Test reconstructing item state at specific time."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        mock_state = {"id": "item-1", "title": "Historical State"}
        service.events.get_entity_at_time = AsyncMock(return_value=mock_state)

        at_time = datetime.now() - timedelta(days=1)
        result = await service.get_item_at_time("item-1", at_time)

        assert result == mock_state
        service.events.get_entity_at_time.assert_called_once_with("item-1", at_time)

    @pytest.mark.asyncio
    async def test_get_item_at_time_not_found(self) -> None:
        """Test getting item state when item didn't exist at that time."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        service.events.get_entity_at_time = AsyncMock(return_value=None)

        at_time = datetime.now() - timedelta(days=365)
        result = await service.get_item_at_time("item-1", at_time)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_item_at_time_future_date(self) -> None:
        """Test getting item state with future date."""
        mock_session = AsyncMock()
        service = EventService(mock_session)

        service.events.get_entity_at_time = AsyncMock(return_value={"id": "item-1"})

        future_time = datetime.now() + timedelta(days=1)
        result = await service.get_item_at_time("item-1", future_time)

        assert result is not None


class TestCacheStatsDataclass:
    """Tests for CacheStats dataclass."""

    def test_cache_stats_creation(self) -> None:
        """Test creating CacheStats instance."""
        stats = CacheStats(hits=10, misses=5, hit_rate=66.67, total_size_bytes=1024, evictions=2)

        assert stats.hits == COUNT_TEN
        assert stats.misses == COUNT_FIVE
        assert stats.hit_rate == 66.67
        assert stats.total_size_bytes == 1024
        assert stats.evictions == COUNT_TWO

    def test_cache_stats_zero_values(self) -> None:
        """Test CacheStats with all zero values."""
        stats = CacheStats(hits=0, misses=0, hit_rate=0.0, total_size_bytes=0, evictions=0)

        assert stats.hits == 0
        assert stats.hit_rate == 0.0

    def test_cache_stats_large_values(self) -> None:
        """Test CacheStats with large values."""
        stats = CacheStats(
            hits=1000000,
            misses=500000,
            hit_rate=66.67,
            total_size_bytes=1073741824,  # 1GB
            evictions=10000,
        )

        assert stats.hits == 1000000
        assert stats.total_size_bytes == 1073741824
