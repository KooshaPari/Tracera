"""
Performance tests for bulk operations - Story 2.8, FR14.

Tests performance-critical paths:
- Bulk updates (100+ items)
- Bulk preview generation
- Large batch operations
- Memory efficiency during bulk ops
- Concurrent bulk operations

Target: +2% coverage on performance-sensitive paths
"""

import pytest
import time
import asyncio
import sys
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tracertm.services.bulk_operation_service import BulkOperationService
from tracertm.models.item import Item
from tracertm.models.project import Project


@pytest.fixture
async def mock_db_session() -> AsyncMock:
    """Create mock async database session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def create_items(num_items: int = 100):
    """Factory for creating test items."""
    def _create_items(project_id: str, base_title: str = "Item") -> list[Item]:
        items = []
        for i in range(num_items):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.project_id = project_id
            item.title = f"{base_title} {i}"
            item.description = f"Test item {i}"
            item.status = ["todo", "in_progress", "done"][i % 3]
            item.priority = ["low", "medium", "high"][i % 3]
            item.owner = f"user-{i % 5}"
            item.view = ["requirements", "design", "test"][i % 3]
            item.item_type = ["requirement", "test", "artifact"][i % 3]
            item.created_at = datetime.now(timezone.utc)
            item.deleted_at = None
            items.append(item)
        return items
    return _create_items


class TestBulkOperationsPerformance:
    """Tests for bulk operation performance."""

    @pytest.mark.asyncio
    async def test_bulk_preview_100_items(self, mock_db_session):
        """Test bulk preview with 100 items."""
        project_id = "proj-001"
        items = [MagicMock(spec=Item) for _ in range(100)]
        for i, item in enumerate(items):
            item.id = f"item-{i:04d}"
            item.title = f"Item {i}"
            item.status = "todo"
            item.priority = "medium"
            item.owner = "user1"

        # Mock query chain
        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=100)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=items[:5])

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        # Measure performance
        start_time = time.time()
        result = service.bulk_update_preview(
            project_id=project_id,
            filters={"status": "todo"},
            updates={"priority": "high"},
            limit=5
        )
        elapsed = time.time() - start_time

        # Assert performance - should be sub-100ms for 100 items
        assert elapsed < 0.1, f"Preview took {elapsed}s, should be < 0.1s"
        assert result["total_count"] == 100
        assert result["samples"] is not None
        assert len(result["samples"]) <= 5

    @pytest.mark.asyncio
    async def test_bulk_preview_1000_items(self, mock_db_session):
        """Test bulk preview with 1000 items (stress test)."""
        project_id = "proj-002"
        items = [MagicMock(spec=Item) for _ in range(10)]  # Sample only
        for i, item in enumerate(items):
            item.id = f"item-{i:04d}"
            item.title = f"Item {i}"
            item.status = "todo"
            item.priority = "medium"
            item.owner = "user1"

        # Mock query
        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=1000)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=items)

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        start_time = time.time()
        result = service.bulk_update_preview(
            project_id=project_id,
            filters={"status": "todo"},
            updates={"priority": "high"},
            limit=10
        )
        elapsed = time.time() - start_time

        # Should handle 1000 items efficiently
        assert elapsed < 0.2, f"Preview took {elapsed}s, should be < 0.2s"
        assert result["total_count"] == 1000
        assert "warnings" in result

    @pytest.mark.asyncio
    async def test_bulk_update_concurrent(self, mock_db_session):
        """Test concurrent bulk updates."""
        project_id = "proj-003"

        service = BulkOperationService(mock_db_session)

        async def run_bulk_update(update_id: int):
            """Run single bulk update."""
            query_mock = AsyncMock()
            query_mock.filter = MagicMock(return_value=query_mock)
            query_mock.count = MagicMock(return_value=50)
            query_mock.limit = MagicMock(return_value=query_mock)
            items = [MagicMock(spec=Item) for _ in range(5)]
            for i, item in enumerate(items):
                item.id = f"item-{update_id}-{i}"
                item.title = f"Item {i}"
                item.status = "todo"
            query_mock.all = AsyncMock(return_value=items)

            mock_db_session.query = MagicMock(return_value=query_mock)

            return service.bulk_update_preview(
                project_id=project_id,
                filters={"owner": f"user-{update_id}"},
                updates={"status": "done"}
            )

        # Run 10 concurrent bulk operations
        start_time = time.time()
        results = await asyncio.gather(*[run_bulk_update(i) for i in range(10)])
        elapsed = time.time() - start_time

        # All should complete efficiently
        assert len(results) == 10
        assert elapsed < 2.0, f"Concurrent updates took {elapsed}s"
        assert all(r["total_count"] == 50 for r in results)

    @pytest.mark.asyncio
    async def test_bulk_preview_memory_efficiency(self, mock_db_session):
        """Test memory efficiency during bulk preview."""
        project_id = "proj-004"
        large_items = [MagicMock(spec=Item) for _ in range(5)]
        for i, item in enumerate(large_items):
            item.id = f"item-{i}"
            item.title = f"Item {i}" * 100  # Large title
            item.description = f"Description {i}" * 200
            item.status = "todo"
            item.priority = "high"
            item.owner = f"user-{i}"

        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=500)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=large_items)

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        import tracemalloc
        tracemalloc.start()

        snapshot_before = tracemalloc.take_snapshot()

        result = service.bulk_update_preview(
            project_id=project_id,
            filters={},
            updates={"priority": "high"},
            limit=5
        )

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Memory increase should be reasonable
        stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        total_increase = sum(stat.size_diff for stat in stats) / (1024 * 1024)  # MB

        # Should use < 5MB for this operation
        assert total_increase < 5.0, f"Memory increase {total_increase}MB is too high"

    @pytest.mark.asyncio
    async def test_bulk_filter_performance_multiple_filters(self, mock_db_session):
        """Test performance with multiple filter combinations."""
        project_id = "proj-005"
        items = [MagicMock(spec=Item) for _ in range(20)]
        for i, item in enumerate(items):
            item.id = f"item-{i}"
            item.title = f"Item {i}"
            item.status = ["todo", "in_progress", "done"][i % 3]
            item.priority = ["low", "medium", "high"][i % 3]
            item.owner = f"user-{i % 5}"
            item.view = ["req", "design", "test"][i % 3]
            item.item_type = "requirement"

        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=100)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=items)

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        # Test with multiple filters
        start_time = time.time()
        result = service.bulk_update_preview(
            project_id=project_id,
            filters={
                "status": "todo",
                "priority": "high",
                "owner": "user1",
                "view": "requirements"
            },
            updates={"status": "in_progress"}
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1
        assert result is not None
        assert query_mock.filter.call_count >= 5  # base + 4 filters

    @pytest.mark.asyncio
    async def test_bulk_large_update_payload(self, mock_db_session):
        """Test bulk update with large payload."""
        project_id = "proj-006"
        items = [MagicMock(spec=Item) for _ in range(100)]
        for i, item in enumerate(items):
            item.id = f"item-{i}"
            item.title = f"Item {i}"
            item.status = "todo"
            item.priority = "medium"
            item.owner = "user1"

        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=100)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=items)

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        # Large update payload
        large_updates = {
            f"field_{i}": f"value_{i}" * 10 for i in range(50)
        }

        start_time = time.time()
        result = service.bulk_update_preview(
            project_id=project_id,
            filters={"status": "todo"},
            updates=large_updates
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.15
        assert result is not None

    @pytest.mark.asyncio
    async def test_bulk_preview_warning_generation(self, mock_db_session):
        """Test warning generation performance for large operations."""
        project_id = "proj-007"
        items = [MagicMock(spec=Item) for _ in range(100)]
        for i, item in enumerate(items):
            item.id = f"item-{i}"
            item.title = f"Item {i}"
            item.status = ["todo", "in_progress"][i % 2]  # Mixed statuses
            item.priority = "high"
            item.owner = "user1"

        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=500)  # > 100, should warn
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=items)

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        result = service.bulk_update_preview(
            project_id=project_id,
            filters={},
            updates={"status": "done"}
        )

        assert "warnings" in result
        assert len(result["warnings"]) > 0
        assert "Large operation" in result["warnings"][0]

    @pytest.mark.asyncio
    async def test_bulk_estimated_duration(self, mock_db_session):
        """Test estimated duration calculation accuracy."""
        project_id = "proj-008"
        items = [MagicMock(spec=Item) for _ in range(5)]

        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=200)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=items)

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        result = service.bulk_update_preview(
            project_id=project_id,
            filters={},
            updates={}
        )

        # 200 items * 10ms = 2000ms
        assert result["estimated_duration_ms"] == 2000

    @pytest.mark.asyncio
    async def test_bulk_sequential_operations(self, mock_db_session):
        """Test sequential bulk operations performance."""
        project_id = "proj-009"

        service = BulkOperationService(mock_db_session)

        async def run_preview(batch_id: int, count: int):
            """Run preview for batch."""
            items = [MagicMock(spec=Item) for _ in range(min(5, count))]
            for i, item in enumerate(items):
                item.id = f"item-batch{batch_id}-{i}"
                item.title = f"Item {i}"
                item.status = "todo"
                item.priority = "medium"

            query_mock = AsyncMock()
            query_mock.filter = MagicMock(return_value=query_mock)
            query_mock.count = MagicMock(return_value=count)
            query_mock.limit = MagicMock(return_value=query_mock)
            query_mock.all = AsyncMock(return_value=items)

            mock_db_session.query = MagicMock(return_value=query_mock)

            return service.bulk_update_preview(
                project_id=project_id,
                filters={"view": f"view-{batch_id}"},
                updates={"status": "done"}
            )

        # Sequential operations
        start_time = time.time()
        for batch_id in range(5):
            result = await run_preview(batch_id, (batch_id + 1) * 50)
            assert result is not None
        elapsed = time.time() - start_time

        # 5 sequential operations should complete in < 0.5s
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_bulk_mixed_item_types(self, mock_db_session):
        """Test bulk operations with mixed item types."""
        project_id = "proj-010"
        items = [MagicMock(spec=Item) for _ in range(100)]
        for i, item in enumerate(items):
            item.id = f"item-{i}"
            item.title = f"Item {i}"
            item.item_type = ["requirement", "test", "design", "artifact"][i % 4]
            item.status = "todo"
            item.priority = "medium"
            item.owner = f"user-{i % 5}"

        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=100)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=items)

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        result = service.bulk_update_preview(
            project_id=project_id,
            filters={"item_type": "requirement"},
            updates={"status": "in_progress"}
        )

        assert result["total_count"] == 100
        assert len(result["samples"]) > 0

    @pytest.mark.asyncio
    async def test_bulk_empty_result(self, mock_db_session):
        """Test bulk preview with no matching items."""
        project_id = "proj-011"

        query_mock = AsyncMock()
        query_mock.filter = MagicMock(return_value=query_mock)
        query_mock.count = MagicMock(return_value=0)
        query_mock.limit = MagicMock(return_value=query_mock)
        query_mock.all = AsyncMock(return_value=[])

        mock_db_session.query = MagicMock(return_value=query_mock)

        service = BulkOperationService(mock_db_session)

        result = service.bulk_update_preview(
            project_id=project_id,
            filters={"status": "nonexistent"},
            updates={}
        )

        assert result["total_count"] == 0
        assert result["samples"] == []
