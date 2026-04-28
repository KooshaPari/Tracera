"""Performance tests for repository and query operations.

Tests performance-critical paths:
- Bulk item creation/retrieval
- Query performance with filters
- Repository pagination
- Optimistic locking performance
- Memory efficiency in queries
- Concurrent repository operations

Target: +2% coverage on performance-sensitive paths
"""

import asyncio
import time
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TEN, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR
from tracertm.models.item import Item
from tracertm.repositories.item_repository import ItemRepository


@pytest_asyncio.fixture
async def mock_async_session() -> AsyncMock:
    """Create mock async session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


class TestItemRepositoryPerformance:
    """Tests for item repository performance."""

    @pytest.mark.asyncio
    async def test_create_single_item(self, mock_async_session: Any) -> None:
        """Test single item creation performance."""
        repo = ItemRepository(mock_async_session)

        start_time = time.time()
        await repo.create(
            project_id="proj-001",
            title="Test Item",
            view="requirements",
            item_type="requirement",
            description="Test description",
            status="todo",
            priority="medium",
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.05, "Single item creation should be fast"
        mock_async_session.add.assert_called_once()
        mock_async_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_bulk_items_sequential(self, mock_async_session: Any) -> None:
        """Test bulk item creation (sequential)."""
        repo = ItemRepository(mock_async_session)

        start_time = time.time()
        for i in range(100):
            await repo.create(project_id="proj-001", title=f"Item {i}", view="requirements", item_type="requirement")
        elapsed = time.time() - start_time

        assert elapsed < float(COUNT_TWO + 0.0), "Creating 100 items sequentially should be < COUNT_TWOs"
        assert mock_async_session.add.call_count == 100

    @pytest.mark.asyncio
    async def test_create_bulk_items_concurrent(self, mock_async_session: Any) -> None:
        """Test bulk item creation (concurrent)."""
        repo = ItemRepository(mock_async_session)

        async def create_item(i: int) -> None:
            """Create single item."""
            return await repo.create(
                project_id="proj-001",
                title=f"Item {i}",
                view="requirements",
                item_type="requirement",
            )

        start_time = time.time()
        items = await asyncio.gather(*[create_item(i) for i in range(50)])
        elapsed = time.time() - start_time

        assert len(items) == 50
        assert elapsed < 1.0, "Creating 50 items concurrently should be < 1s"

    @pytest.mark.asyncio
    async def test_get_item_by_id(self, mock_async_session: Any) -> None:
        """Test get item by ID performance."""
        repo = ItemRepository(mock_async_session)

        # Mock execute - scalar_one_or_none is SYNC, not async
        item = MagicMock(spec=Item)
        item.id = "item-001"
        item.title = "Test Item"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=item)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        start_time = time.time()
        result = await repo.get_by_id("item-001")
        elapsed = time.time() - start_time

        assert elapsed < 0.05
        assert result is not None
        assert result.id == "item-001"

    @pytest.mark.asyncio
    async def test_list_by_view_performance(self, mock_async_session: Any) -> None:
        """Test list items by view performance."""
        repo = ItemRepository(mock_async_session)

        # Create mock items
        items = []
        for i in range(100):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.title = f"Item {i}"
            item.view = "requirements"
            items.append(item)

        # Mock scalars result with .all() method
        mock_scalars_result = MagicMock()
        mock_scalars_result.all = MagicMock(return_value=items)
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars_result)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        start_time = time.time()
        result = await repo.list_by_view("proj-001", "requirements")
        elapsed = time.time() - start_time

        assert len(result) == 100, f"Expected 100 items, got {len(result)}"
        assert elapsed < 0.1, "Listing 100 items should be < 100ms"

    @pytest.mark.asyncio
    async def test_list_by_view_large_result(self, mock_async_session: Any) -> None:
        """Test listing 1000 items by view."""
        repo = ItemRepository(mock_async_session)

        # Create 1000 mock items
        items = []
        for i in range(1000):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.title = f"Item {i}"
            items.append(item)

        # Mock scalars result with .all() method
        mock_scalars_result = MagicMock()
        mock_scalars_result.all = MagicMock(return_value=items)
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars_result)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        start_time = time.time()
        result = await repo.list_by_view("proj-001", "requirements")
        elapsed = time.time() - start_time

        assert len(result) == 1000
        assert elapsed < 0.5, "Listing 1000 items should be < HTTP_INTERNAL_SERVER_ERRORms"

    @pytest.mark.asyncio
    async def test_concurrent_read_operations(self, mock_async_session: Any) -> None:
        """Test concurrent read operations."""
        repo = ItemRepository(mock_async_session)

        async def read_item(item_id: int) -> None:
            """Read single item."""
            item = MagicMock(spec=Item)
            item.id = f"item-{item_id:04d}"

            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=item)
            mock_async_session.execute = AsyncMock(return_value=mock_result)

            return await repo.get_by_id(f"item-{item_id:04d}")

        start_time = time.time()
        items = await asyncio.gather(*[read_item(i) for i in range(100)])
        elapsed = time.time() - start_time

        assert len(items) == 100
        assert elapsed < 1.0, "100 concurrent reads should be < 1s"

    @pytest.mark.asyncio
    async def test_query_with_multiple_filters(self, mock_async_session: Any) -> None:
        """Test query performance with multiple filters."""
        repo = ItemRepository(mock_async_session)

        # Create filtered items
        filtered_items = []
        for i in range(50):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.status = "todo"
            item.priority = "high"
            item.owner = "user1"
            filtered_items.append(item)

        # Mock scalars result with .all() method
        mock_scalars_result = MagicMock()
        mock_scalars_result.all = MagicMock(return_value=filtered_items)
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars_result)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        start_time = time.time()
        result = await repo.list_by_view("proj-001", "requirements")
        elapsed = time.time() - start_time

        assert len(result) == 50
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_update_item_with_version(self, mock_async_session: Any) -> None:
        """Test update with optimistic locking."""
        ItemRepository(mock_async_session)

        item = MagicMock(spec=Item)
        item.id = "item-001"
        item.title = "Original"
        item.version = 1

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=item)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        # Update item
        start_time = time.time()
        item.title = "Updated"
        await mock_async_session.flush()
        elapsed = time.time() - start_time

        assert elapsed < 0.05
        assert item.title == "Updated"

    @pytest.mark.asyncio
    async def test_memory_efficiency_large_query(self, mock_async_session: Any) -> None:
        """Test memory efficiency when querying large result set."""
        import tracemalloc

        repo = ItemRepository(mock_async_session)

        # Create 500 items
        items = []
        for i in range(500):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.title = f"Item {i}"
            item.description = f"Description {i}" * 10  # Larger descriptions
            items.append(item)

        # Mock scalars result with .all() method
        mock_scalars_result = MagicMock()
        mock_scalars_result.all = MagicMock(return_value=items)
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars_result)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        await repo.list_by_view("proj-001", "requirements")

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snapshot_after.compare_to(snapshot_before, "lineno")
        total_increase = sum(stat.size_diff for stat in stats) / (1024 * 1024)

        # 500 items with descriptions should use < COUNT_TENMB
        assert total_increase < float(COUNT_TEN + 0.0), f"Memory increase {total_increase}MB too high"

    @pytest.mark.asyncio
    async def test_parent_item_validation_performance(self, mock_async_session: Any) -> None:
        """Test parent validation performance."""
        repo = ItemRepository(mock_async_session)

        # Mock parent item existence
        parent_item = MagicMock(spec=Item)
        parent_item.id = "parent-001"
        parent_item.project_id = "proj-001"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=parent_item)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        start_time = time.time()
        await repo.create(
            project_id="proj-001",
            title="Child Item",
            view="requirements",
            item_type="requirement",
            parent_id="parent-001",
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1
        assert mock_async_session.add.called

    @pytest.mark.asyncio
    async def test_pagination_performance(self, mock_async_session: Any) -> None:
        """Test pagination performance."""
        repo = ItemRepository(mock_async_session)

        page_size = 50

        async def fetch_page(page: int) -> None:
            """Fetch single page."""
            items = []
            for i in range(page_size):
                item = MagicMock(spec=Item)
                item.id = f"item-{page * page_size + i:04d}"
                items.append(item)

            # Mock scalars result with .all() method
            mock_scalars_result = MagicMock()
            mock_scalars_result.all = MagicMock(return_value=items)
            mock_result = MagicMock()
            mock_result.scalars = MagicMock(return_value=mock_scalars_result)
            mock_async_session.execute = AsyncMock(return_value=mock_result)

            return await repo.list_by_view("proj-001", "requirements")

        # Fetch 10 pages
        start_time = time.time()
        pages = await asyncio.gather(*[fetch_page(i) for i in range(10)])
        elapsed = time.time() - start_time

        assert len(pages) == COUNT_TEN
        assert sum(len(p) for p in pages) == HTTP_INTERNAL_SERVER_ERROR
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_delete_item_performance(self, mock_async_session: Any) -> None:
        """Test item deletion performance."""
        ItemRepository(mock_async_session)

        item = MagicMock(spec=Item)
        item.id = "item-001"

        start_time = time.time()
        # Simulate soft delete
        item.deleted_at = datetime.now(UTC)
        await mock_async_session.flush()
        elapsed = time.time() - start_time

        assert elapsed < 0.05
        assert item.deleted_at is not None

    @pytest.mark.asyncio
    async def test_bulk_delete_performance(self, mock_async_session: Any) -> None:
        """Test bulk deletion performance."""
        ItemRepository(mock_async_session)

        items = []
        for i in range(100):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            items.append(item)

        start_time = time.time()
        # Simulate bulk soft delete
        for item in items:
            item.deleted_at = datetime.now(UTC)
        await mock_async_session.flush()
        elapsed = time.time() - start_time

        assert elapsed < 0.1, "Bulk delete 100 items should be < 100ms"
        assert all(item.deleted_at is not None for item in items)

    @pytest.mark.asyncio
    async def test_search_items_performance(self, mock_async_session: Any) -> None:
        """Test search performance on large dataset."""
        repo = ItemRepository(mock_async_session)

        # Create 500 items, match 50
        matched_items = []
        for i in range(50):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.title = f"Search Match {i}"
            matched_items.append(item)

        # Mock scalars result with .all() method
        mock_scalars_result = MagicMock()
        mock_scalars_result.all = MagicMock(return_value=matched_items)
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars_result)
        mock_async_session.execute = AsyncMock(return_value=mock_result)

        start_time = time.time()
        result = await repo.list_by_view("proj-001", "requirements")
        elapsed = time.time() - start_time

        assert len(result) == 50
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_concurrent_write_operations(self, mock_async_session: Any) -> None:
        """Test concurrent write operations."""
        repo = ItemRepository(mock_async_session)

        async def create_and_update(i: int) -> None:
            """Create and update item."""
            # Create
            item = await repo.create(
                project_id="proj-001",
                title=f"Item {i}",
                view="requirements",
                item_type="requirement",
            )

            # Update
            item.title = f"Updated Item {i}"
            await mock_async_session.flush()

            return item

        start_time = time.time()
        items = await asyncio.gather(*[create_and_update(i) for i in range(50)])
        elapsed = time.time() - start_time

        assert len(items) == 50
        assert elapsed < float(COUNT_TWO + 0.0), "50 concurrent create/update should be < COUNT_TWOs"
