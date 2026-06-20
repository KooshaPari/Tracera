from typing import Any

"""Unit tests for shortest path service caching."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.services.cache_service import CacheService
from tracertm.services.shortest_path_service import ShortestPathService


@pytest.fixture
def mock_cache() -> None:
    """Create a mock cache service."""
    cache = MagicMock(spec=CacheService)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    return cache


@pytest.fixture
def mock_session() -> None:
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def service(mock_session: Any, mock_cache: Any) -> None:
    """Create a shortest path service with mocked dependencies."""
    service = ShortestPathService(mock_session, mock_cache)
    # Mock repository methods
    service.items.get_by_project = AsyncMock(return_value=[])
    service.links.get_by_project = AsyncMock(return_value=[])
    return service


@pytest.mark.asyncio
async def test_cache_hit_returns_cached_result(service: Any, mock_cache: Any) -> None:
    """Test that cache hit returns cached result without computation."""
    # Setup
    project_id = "proj-123"
    source_id = "item-1"
    target_id = "item-2"

    cached_data = {
        "source_id": source_id,
        "target_id": target_id,
        "path": [source_id, target_id],
        "distance": 1,
        "link_types": ["depends_on"],
        "exists": True,
    }
    mock_cache.get.return_value = cached_data

    # Execute
    result = await service.find_shortest_path(project_id, source_id, target_id)

    # Verify
    assert result.source_id == source_id
    assert result.target_id == target_id
    assert result.path == [source_id, target_id]
    assert result.distance == 1
    assert result.exists is True

    # Verify cache was checked with correct key
    expected_key = f"tracertm:graph:{project_id}:path:{source_id}:{target_id}:all"
    mock_cache.get.assert_called_once_with(expected_key)

    # Verify repositories were NOT called (cache hit)
    service.items.get_by_project.assert_not_called()
    service.links.get_by_project.assert_not_called()


@pytest.mark.asyncio
async def test_cache_miss_computes_and_caches(service: Any, mock_cache: Any) -> None:
    """Test that cache miss computes result and caches it."""
    # Setup
    project_id = "proj-123"
    source_id = "item-1"
    target_id = "item-2"

    mock_cache.get.return_value = None  # Cache miss

    # Mock items
    item1 = MagicMock()
    item1.id = source_id
    item2 = MagicMock()
    item2.id = target_id
    service.items.get_by_project.return_value = [item1, item2]

    # Mock link
    link = MagicMock()
    link.source_item_id = source_id
    link.target_item_id = target_id
    link.link_type = "depends_on"
    service.links.get_by_project.return_value = [link]

    # Execute
    result = await service.find_shortest_path(project_id, source_id, target_id)

    # Verify result
    assert result.source_id == source_id
    assert result.target_id == target_id
    assert result.exists is True
    assert result.distance == 1

    # Verify cache was written
    expected_key = f"tracertm:graph:{project_id}:path:{source_id}:{target_id}:all"
    mock_cache.set.assert_called_once()
    call_args = mock_cache.set.call_args
    assert call_args[0][0] == expected_key
    assert call_args[1]["ttl_seconds"] == 300


@pytest.mark.asyncio
async def test_cache_key_includes_link_types(service: Any, mock_cache: Any) -> None:
    """Test that cache key includes link types filter."""
    # Setup
    project_id = "proj-123"
    source_id = "item-1"
    target_id = "item-2"
    link_types = ["depends_on", "implements"]

    mock_cache.get.return_value = None
    service.items.get_by_project.return_value = []
    service.links.get_by_project.return_value = []

    # Execute
    await service.find_shortest_path(project_id, source_id, target_id, link_types)

    # Verify cache key includes sorted link types
    expected_key = f"tracertm:graph:{project_id}:path:{source_id}:{target_id}:depends_on:implements"
    mock_cache.get.assert_called_once_with(expected_key)


@pytest.mark.asyncio
async def test_all_paths_cache_hit(service: Any, mock_cache: Any) -> None:
    """Test that all_paths cache hit returns cached results."""
    # Setup
    project_id = "proj-123"
    source_id = "item-1"

    cached_data = {
        "item-2": {
            "source_id": source_id,
            "target_id": "item-2",
            "path": [source_id, "item-2"],
            "distance": 1,
            "link_types": ["depends_on"],
            "exists": True,
        },
        "item-3": {
            "source_id": source_id,
            "target_id": "item-3",
            "path": [source_id, "item-2", "item-3"],
            "distance": 2,
            "link_types": ["depends_on", "implements"],
            "exists": True,
        },
    }
    mock_cache.get.return_value = cached_data

    # Execute
    results = await service.find_all_shortest_paths(project_id, source_id)

    # Verify
    assert len(results) == COUNT_TWO
    assert "item-2" in results
    assert "item-3" in results
    assert results["item-2"].distance == 1
    assert results["item-3"].distance == COUNT_TWO

    # Verify repositories were NOT called
    service.items.get_by_project.assert_not_called()
    service.links.get_by_project.assert_not_called()


@pytest.mark.asyncio
async def test_graceful_cache_failure(service: Any, mock_cache: Any) -> None:
    """Test that cache failures don't break the service."""
    # Setup
    project_id = "proj-123"
    source_id = "item-1"
    target_id = "item-2"

    # Simulate cache failure
    mock_cache.get.side_effect = Exception("Redis connection failed")

    # Mock items and links
    item1 = MagicMock()
    item1.id = source_id
    item2 = MagicMock()
    item2.id = target_id
    service.items.get_by_project.return_value = [item1, item2]

    link = MagicMock()
    link.source_item_id = source_id
    link.target_item_id = target_id
    link.link_type = "depends_on"
    service.links.get_by_project.return_value = [link]

    # Execute - should not raise exception
    result = await service.find_shortest_path(project_id, source_id, target_id)

    # Verify result is still computed
    assert result.exists is True
    assert result.distance == 1


@pytest.mark.asyncio
async def test_no_cache_service(mock_session: Any) -> None:
    """Test that service works without cache service."""
    # Create service without cache
    service = ShortestPathService(mock_session, cache=None)

    # Mock repositories
    item1 = MagicMock()
    item1.id = "item-1"
    item2 = MagicMock()
    item2.id = "item-2"
    service.items.get_by_project = AsyncMock(return_value=[item1, item2])

    link = MagicMock()
    link.source_item_id = "item-1"
    link.target_item_id = "item-2"
    link.link_type = "depends_on"
    service.links.get_by_project = AsyncMock(return_value=[link])

    # Execute - should work without caching
    result = await service.find_shortest_path("proj-123", "item-1", "item-2")

    # Verify
    assert result.exists is True
    assert result.distance == 1
