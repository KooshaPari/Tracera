"""Performance tests for graph traversal and analysis.

Tests performance-critical paths:
- Large graph traversals (100+ nodes)
- Critical path calculation
- Dependency analysis
- Concurrent graph queries
- Memory efficiency in graph operations

Target: +2% coverage on performance-sensitive paths
"""

import asyncio
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TEN, COUNT_THREE, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.services.critical_path_service import (
    CriticalPathResult,
    CriticalPathService,
)


@pytest.fixture
async def mock_async_session() -> AsyncMock:
    """Create mock async session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def create_graph_items(num_nodes: int = 100) -> None:
    """Create test graph items."""

    def _create_items(project_id: str) -> None:
        items = []
        for i in range(num_nodes):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.project_id = project_id
            item.title = f"Task {i}"
            item.status = "in_progress"
            item.priority = "medium"
            items.append(item)
        return items

    return _create_items


@pytest.fixture
def create_graph_links(num_edges: int = 150) -> None:
    """Create test graph links."""

    def _create_links(project_id: str, num_nodes: int) -> None:
        links = []
        edge_count = 0
        for i in range(num_nodes):
            # Create forward links
            for j in range(1, min(4, num_nodes - i)):
                if edge_count < num_edges:
                    link = MagicMock(spec=Link)
                    link.id = f"link-{edge_count}"
                    link.project_id = project_id
                    link.source_item_id = f"item-{i:04d}"
                    link.target_item_id = f"item-{i + j:04d}"
                    link.link_type = "depends_on"
                    links.append(link)
                    edge_count += 1
        return links

    return _create_links


class TestCriticalPathPerformance:
    """Tests for critical path analysis performance."""

    @pytest.mark.asyncio
    async def test_critical_path_100_items(
        self, mock_async_session: Any, create_graph_items: Any, create_graph_links: Any
    ) -> None:
        """Test critical path with 100 items."""
        project_id = "proj-001"
        items = create_graph_items(100)(project_id)
        links = create_graph_links(150)(project_id, 100)

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=items)

        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=links)

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        start_time = time.time()
        result = await service.calculate_critical_path(project_id)
        elapsed = time.time() - start_time

        # Should complete in < 0.5s for 100 items
        assert elapsed < 0.5, f"Critical path took {elapsed}s"
        assert isinstance(result, CriticalPathResult)
        assert result.project_id == project_id
        assert result.path_length > 0

    @pytest.mark.asyncio
    async def test_critical_path_500_items_stress(self, mock_async_session: Any) -> None:
        """Test critical path with 500 items (stress test)."""
        project_id = "proj-002"

        # Create 500 items
        items = []
        for i in range(500):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            item.project_id = project_id
            items.append(item)

        # Create links (sparse graph: ~1000 edges)
        links = []
        for i in range(0, 500, 2):
            for j in range(1, 3):
                if i + j < HTTP_INTERNAL_SERVER_ERROR:
                    link = MagicMock(spec=Link)
                    link.source_item_id = f"item-{i:04d}"
                    link.target_item_id = f"item-{i + j:04d}"
                    link.link_type = "depends_on"
                    links.append(link)

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=items)

        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=links)

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        start_time = time.time()
        result = await service.calculate_critical_path(project_id)
        elapsed = time.time() - start_time

        # Should complete in < COUNT_TWOs even with 500 items
        assert elapsed < float(COUNT_TWO + 0.0), f"Critical path took {elapsed}s for 500 items"
        assert result is not None

    @pytest.mark.asyncio
    async def test_critical_path_with_link_type_filter(
        self,
        mock_async_session: Any,
        create_graph_items: Any,
        _create_graph_links: Any,
    ) -> None:
        """Test critical path with link type filtering."""
        project_id = "proj-003"
        items = create_graph_items(100)(project_id)

        # Create mixed link types
        links = []
        for i in range(100):
            for j in range(1, 2):
                if i + j < 100:
                    link = MagicMock(spec=Link)
                    link.source_item_id = f"item-{i:04d}"
                    link.target_item_id = f"item-{i + j:04d}"
                    # Vary link types
                    link.link_type = ["depends_on", "implements", "tests"][i % 3]
                    links.append(link)

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=items)

        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=links)

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        start_time = time.time()
        await service.calculate_critical_path(project_id, link_types=["depends_on"])
        elapsed = time.time() - start_time

        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_critical_path_concurrent_queries(self, mock_async_session: Any) -> None:
        """Test concurrent critical path queries."""

        async def run_cp_analysis(project_id: str, num_items: int) -> None:
            """Run single critical path analysis."""
            items = []
            for i in range(num_items):
                item = MagicMock(spec=Item)
                item.id = f"{project_id}-item-{i}"
                items.append(item)

            links = []
            for i in range(0, num_items - 1, 2):
                link = MagicMock(spec=Link)
                link.source_item_id = f"{project_id}-item-{i}"
                link.target_item_id = f"{project_id}-item-{i + 1}"
                link.link_type = "depends_on"
                links.append(link)

            mock_item_repo = AsyncMock()
            mock_item_repo.get_by_project = AsyncMock(return_value=items)
            mock_link_repo = AsyncMock()
            mock_link_repo.get_by_project = AsyncMock(return_value=links)

            service = CriticalPathService(mock_async_session)
            service.items = mock_item_repo
            service.links = mock_link_repo

            return await service.calculate_critical_path(project_id)

        # Run 10 concurrent analyses
        start_time = time.time()
        results = await asyncio.gather(*[run_cp_analysis(f"proj-{i:03d}", 50) for i in range(10)])
        elapsed = time.time() - start_time

        assert len(results) == COUNT_TEN
        assert elapsed < float(COUNT_THREE + 0.0), f"Concurrent analyses took {elapsed}s"
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_critical_path_memory_efficiency(self, mock_async_session: Any) -> None:
        """Test memory efficiency during critical path calculation."""
        project_id = "proj-004"

        # Create 200 items
        items = []
        for i in range(200):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            items.append(item)

        # Create 300 links
        links = []
        for i in range(300):
            link = MagicMock(spec=Link)
            link.source_item_id = f"item-{i % 199:04d}"
            link.target_item_id = f"item-{(i + 1) % 200:04d}"
            link.link_type = "depends_on"
            links.append(link)

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=items)
        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=links)

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        import tracemalloc

        tracemalloc.start()

        snapshot_before = tracemalloc.take_snapshot()
        await service.calculate_critical_path(project_id)
        snapshot_after = tracemalloc.take_snapshot()

        tracemalloc.stop()

        stats = snapshot_after.compare_to(snapshot_before, "lineno")
        total_increase = sum(stat.size_diff for stat in stats) / (1024 * 1024)

        # Should use < COUNT_TENMB for 200 items + 300 links
        assert total_increase < float(COUNT_TEN + 0.0), f"Memory increase {total_increase}MB is too high"

    @pytest.mark.asyncio
    async def test_critical_path_empty_graph(self, mock_async_session: Any) -> None:
        """Test critical path with empty graph."""
        project_id = "proj-005"

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=[])
        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=[])

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        result = await service.calculate_critical_path(project_id)

        assert result.path_length == 0
        assert len(result.critical_items) == 0

    @pytest.mark.asyncio
    async def test_critical_path_single_node(self, mock_async_session: Any) -> None:
        """Test critical path with single node."""
        project_id = "proj-006"

        item = MagicMock(spec=Item)
        item.id = "item-0000"

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=[item])
        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=[])

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        result = await service.calculate_critical_path(project_id)

        assert result is not None
        assert result.path_length > 0

    @pytest.mark.asyncio
    async def test_critical_path_dense_graph(self, mock_async_session: Any) -> None:
        """Test critical path with dense graph (high connectivity)."""
        project_id = "proj-007"

        # Create 50 items
        items = []
        for i in range(50):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            items.append(item)

        # Create dense connections (quadratic)
        links = []
        for i in range(50):
            for j in range(i + 1, min(i + 10, 50)):  # Each node connects to next 9
                link = MagicMock(spec=Link)
                link.source_item_id = f"item-{i:04d}"
                link.target_item_id = f"item-{j:04d}"
                link.link_type = "depends_on"
                links.append(link)

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=items)
        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=links)

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        start_time = time.time()
        result = await service.calculate_critical_path(project_id)
        elapsed = time.time() - start_time

        # Should handle dense graphs efficiently
        assert elapsed < 1.0, f"Dense graph took {elapsed}s"
        assert result is not None

    @pytest.mark.asyncio
    async def test_critical_path_sequential_chain(self, mock_async_session: Any) -> None:
        """Test critical path with sequential chain (linear graph)."""
        project_id = "proj-008"

        # Create 100 items in sequence
        items = []
        for i in range(100):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            items.append(item)

        # Create linear chain
        links = []
        for i in range(99):
            link = MagicMock(spec=Link)
            link.source_item_id = f"item-{i:04d}"
            link.target_item_id = f"item-{i + 1:04d}"
            link.link_type = "depends_on"
            links.append(link)

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=items)
        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=links)

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        result = await service.calculate_critical_path(project_id)

        assert result.path_length == 100
        assert len(result.critical_items) == 100

    @pytest.mark.asyncio
    async def test_critical_path_mixed_structures(self, mock_async_session: Any) -> None:
        """Test critical path with mixed graph structures."""
        project_id = "proj-009"

        # Create 100 items
        items = []
        for i in range(100):
            item = MagicMock(spec=Item)
            item.id = f"item-{i:04d}"
            items.append(item)

        # Create mixed structures: some chains, some branches, some merges
        links = []

        # Linear chains
        for start in [0, 20, 40, 60, 80]:
            for i in range(start, start + 10):
                if i + 1 < 100:
                    link = MagicMock(spec=Link)
                    link.source_item_id = f"item-{i:04d}"
                    link.target_item_id = f"item-{i + 1:04d}"
                    link.link_type = "depends_on"
                    links.append(link)

        # Branches
        for i in [10, 30, 50, 70, 90]:
            for j in [1, 2]:
                if i + j < 100:
                    link = MagicMock(spec=Link)
                    link.source_item_id = f"item-{i:04d}"
                    link.target_item_id = f"item-{i + j:04d}"
                    link.link_type = "depends_on"
                    links.append(link)

        mock_item_repo = AsyncMock()
        mock_item_repo.get_by_project = AsyncMock(return_value=items)
        mock_link_repo = AsyncMock()
        mock_link_repo.get_by_project = AsyncMock(return_value=links)

        service = CriticalPathService(mock_async_session)
        service.items = mock_item_repo
        service.links = mock_link_repo

        result = await service.calculate_critical_path(project_id)

        assert result is not None
        assert result.path_length > 0
