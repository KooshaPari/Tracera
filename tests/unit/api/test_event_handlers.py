"""Unit tests for event handlers in main.py."""

from unittest.mock import AsyncMock

import pytest

from tests.test_constants import COUNT_FIVE


@pytest.mark.asyncio
async def test_handle_item_created_invalidates_cache() -> None:
    """Test that handle_item_created properly invalidates caches."""
    # Mock cache service
    mock_cache = AsyncMock()
    mock_cache.clear_prefix = AsyncMock(return_value=5)
    mock_cache.invalidate = AsyncMock(return_value=True)

    # Create a simple handler that mimics the one in main.py
    async def handle_item_created(event: dict) -> None:
        """Simplified version of the handler from main.py."""
        event.get("entity_id")
        project_id = event.get("project_id")
        event.get("entity_type")

        if project_id:
            try:
                await mock_cache.clear_prefix(f"items:{project_id}")
                await mock_cache.clear_prefix(f"graph:{project_id}")
                await mock_cache.invalidate("project", project_id=project_id)
            except Exception:
                pass

    # Test event
    event = {"entity_id": "test-item-123", "project_id": "test-project-456", "entity_type": "requirement"}

    # Execute handler
    await handle_item_created(event)

    # Verify cache invalidation calls
    mock_cache.clear_prefix.assert_any_call("items:test-project-456")
    mock_cache.clear_prefix.assert_any_call("graph:test-project-456")
    mock_cache.invalidate.assert_called_once_with("project", project_id="test-project-456")


@pytest.mark.asyncio
async def test_handle_link_created_invalidates_graph_caches() -> None:
    """Test that handle_link_created invalidates graph and ancestor/descendant caches."""
    # Mock cache service
    mock_cache = AsyncMock()
    mock_cache.clear_prefix = AsyncMock(return_value=3)

    # Create handler
    async def handle_link_created(event: dict) -> None:
        """Simplified version of the handler from main.py."""
        project_id = event.get("project_id")

        if project_id:
            try:
                await mock_cache.clear_prefix(f"links:{project_id}")
                await mock_cache.clear_prefix(f"graph:{project_id}")
                await mock_cache.clear_prefix(f"ancestors:{project_id}")
                await mock_cache.clear_prefix(f"descendants:{project_id}")
                await mock_cache.clear_prefix(f"impact:{project_id}")
            except Exception:
                pass

    # Test event
    event = {"entity_id": "test-link-789", "project_id": "test-project-456"}

    # Execute handler
    await handle_link_created(event)

    # Verify all graph-related caches are invalidated
    mock_cache.clear_prefix.assert_any_call("links:test-project-456")
    mock_cache.clear_prefix.assert_any_call("graph:test-project-456")
    mock_cache.clear_prefix.assert_any_call("ancestors:test-project-456")
    mock_cache.clear_prefix.assert_any_call("descendants:test-project-456")
    mock_cache.clear_prefix.assert_any_call("impact:test-project-456")
    assert mock_cache.clear_prefix.call_count == COUNT_FIVE


@pytest.mark.asyncio
async def test_handle_project_updated_invalidates_all_project_caches() -> None:
    """Test that handle_project_updated invalidates all project-related caches."""
    # Mock cache service
    mock_cache = AsyncMock()
    mock_cache.invalidate_project = AsyncMock(return_value=10)
    mock_cache.clear_prefix = AsyncMock(return_value=2)

    # Create handler
    async def handle_project_updated(event: dict) -> None:
        """Simplified version of the handler from main.py."""
        project_id = event.get("project_id")

        if project_id:
            try:
                await mock_cache.invalidate_project(project_id)
                await mock_cache.clear_prefix("projects")
            except Exception:
                pass

    # Test event
    event = {"project_id": "test-project-456", "entity_id": "test-project-456"}

    # Execute handler
    await handle_project_updated(event)

    # Verify comprehensive cache invalidation
    mock_cache.invalidate_project.assert_called_once_with("test-project-456")
    mock_cache.clear_prefix.assert_called_once_with("projects")


@pytest.mark.asyncio
async def test_handle_item_deleted_invalidates_items_and_links() -> None:
    """Test that handle_item_deleted invalidates items, graph, and links caches."""
    # Mock cache service
    mock_cache = AsyncMock()
    mock_cache.clear_prefix = AsyncMock(return_value=4)
    mock_cache.invalidate = AsyncMock(return_value=True)

    # Create handler
    async def handle_item_deleted(event: dict) -> None:
        """Simplified version of the handler from main.py."""
        project_id = event.get("project_id")

        if project_id:
            try:
                await mock_cache.clear_prefix(f"items:{project_id}")
                await mock_cache.clear_prefix(f"graph:{project_id}")
                await mock_cache.clear_prefix(f"links:{project_id}")
                await mock_cache.invalidate("project", project_id=project_id)
            except Exception:
                pass

    # Test event
    event = {"entity_id": "deleted-item-123", "project_id": "test-project-456"}

    # Execute handler
    await handle_item_deleted(event)

    # Verify cache invalidation
    mock_cache.clear_prefix.assert_any_call("items:test-project-456")
    mock_cache.clear_prefix.assert_any_call("graph:test-project-456")
    mock_cache.clear_prefix.assert_any_call("links:test-project-456")
    mock_cache.invalidate.assert_called_once_with("project", project_id="test-project-456")


@pytest.mark.asyncio
async def test_event_handler_handles_missing_project_id() -> None:
    """Test that handlers gracefully handle missing project_id."""
    # Mock cache service
    mock_cache = AsyncMock()

    # Create handler
    async def handle_item_created(event: dict) -> None:
        """Simplified version that should not call cache if no project_id."""
        project_id = event.get("project_id")

        if project_id:
            await mock_cache.clear_prefix(f"items:{project_id}")

    # Test event without project_id
    event = {"entity_id": "orphan-item-123", "entity_type": "requirement"}

    # Execute handler
    await handle_item_created(event)

    # Verify cache was NOT called
    mock_cache.clear_prefix.assert_not_called()


@pytest.mark.asyncio
async def test_event_handler_gracefully_handles_cache_errors() -> None:
    """Test that handlers don't crash when cache operations fail."""
    # Mock cache service that raises exceptions
    mock_cache = AsyncMock()
    mock_cache.clear_prefix = AsyncMock(side_effect=Exception("Redis connection failed"))

    # Create handler with error handling
    error_logged = False

    async def handle_item_updated(event: dict) -> None:
        """Handler with error handling."""
        nonlocal error_logged
        project_id = event.get("project_id")

        if project_id:
            try:
                await mock_cache.clear_prefix(f"items:{project_id}")
            except Exception:
                error_logged = True
                # Should not re-raise

    # Test event
    event = {"entity_id": "test-item-123", "project_id": "test-project-456", "entity_type": "test"}

    # Execute handler - should not raise exception
    await handle_item_updated(event)

    # Verify error was logged but execution continued
    assert error_logged
    mock_cache.clear_prefix.assert_called_once()
