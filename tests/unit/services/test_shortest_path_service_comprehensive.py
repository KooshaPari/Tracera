"""
Comprehensive tests for ShortestPathService.

Tests all methods including:
- find_shortest_path
- PathResult dataclass

Coverage target: 90%+
"""

import pytest
from unittest.mock import AsyncMock, Mock
from tracertm.services.shortest_path_service import ShortestPathService, PathResult
from tracertm.models.item import Item
from tracertm.models.link import Link


class TestFindShortestPath:
    """Test find_shortest_path method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ShortestPathService(mock_session)

    @pytest.mark.asyncio
    async def test_direct_path(self, service):
        """Test shortest path with direct connection."""
        # Setup: A -> B
        items = [Mock(spec=Item, id="A"), Mock(spec=Item, id="B")]
        links = [Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "B")

        assert result.exists is True
        assert result.source_id == "A"
        assert result.target_id == "B"
        assert result.distance == 1
        assert "B" in result.path

    @pytest.mark.asyncio
    async def test_multi_hop_path(self, service):
        """Test shortest path through multiple hops."""
        # Setup: A -> B -> C -> D
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
            Mock(spec=Item, id="D"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "D")

        assert result.exists is True
        assert result.distance == 3

    @pytest.mark.asyncio
    async def test_no_path_exists(self, service):
        """Test when no path exists between items."""
        # Setup: A -> B, C -> D (disconnected)
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
            Mock(spec=Item, id="D"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "D")

        assert result.exists is False

    @pytest.mark.asyncio
    async def test_same_source_and_target(self, service):
        """Test path from item to itself."""
        items = [Mock(spec=Item, id="A")]
        links = []

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "A")

        assert result.distance == 0
        assert "A" in result.path

    @pytest.mark.asyncio
    async def test_filter_by_link_types(self, service):
        """Test filtering paths by link types."""
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="blocks"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        # Only follow depends_on links
        result = await service.find_shortest_path(
            "proj-1", "A", "C", link_types=["depends_on"]
        )

        # Should not find path since blocks link is filtered out
        assert result.exists is False

    @pytest.mark.asyncio
    async def test_multiple_paths_finds_shortest(self, service):
        """Test finds shortest path when multiple paths exist."""
        # Setup: A -> B -> D (2 hops)
        #        A -> C -> E -> D (3 hops)
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
            Mock(spec=Item, id="D"),
            Mock(spec=Item, id="E"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="E", link_type="depends_on"),
            Mock(spec=Link, source_item_id="E", target_item_id="D", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "D")

        # Should find shorter path (2 hops instead of 3)
        assert result.distance == 2

    @pytest.mark.asyncio
    async def test_empty_project(self, service):
        """Test with empty project."""
        service.items.get_by_project = AsyncMock(return_value=[])
        service.links.get_by_project = AsyncMock(return_value=[])

        result = await service.find_shortest_path("proj-1", "A", "B")

        assert result.exists is False

    @pytest.mark.asyncio
    async def test_link_types_tracking(self, service):
        """Test that result includes link types used in path."""
        items = [Mock(spec=Item, id="A"), Mock(spec=Item, id="B")]
        links = [Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "B")

        assert "depends_on" in result.link_types


class TestPathResult:
    """Test PathResult dataclass."""

    def test_create_path_result(self):
        """Test creating PathResult."""
        result = PathResult(
            source_id="A",
            target_id="B",
            path=["A", "B"],
            distance=1,
            link_types=["depends_on"],
            exists=True,
        )

        assert result.source_id == "A"
        assert result.target_id == "B"
        assert result.distance == 1
        assert result.exists is True

    def test_path_result_no_path(self):
        """Test PathResult when no path exists."""
        result = PathResult(
            source_id="A",
            target_id="Z",
            path=[],
            distance=0,
            link_types=[],
            exists=False,
        )

        assert result.exists is False
        assert len(result.path) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ShortestPathService(mock_session)

    @pytest.mark.asyncio
    async def test_cyclic_graph(self, service):
        """Test shortest path in graph with cycles."""
        # Setup: A -> B -> C -> A (cycle)
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="A", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "C")

        # Should still find shortest path despite cycle
        assert result.exists is True
        assert result.distance == 2

    @pytest.mark.asyncio
    async def test_isolated_items(self, service):
        """Test with isolated items (no links)."""
        items = [Mock(spec=Item, id="A"), Mock(spec=Item, id="B")]
        links = []

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.find_shortest_path("proj-1", "A", "B")

        assert result.exists is False
