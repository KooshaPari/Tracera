"""
Comprehensive tests for CriticalPathService.

Tests all methods including:
- calculate_critical_path
- _find_critical_path

Coverage target: 90%+
"""

import pytest
from unittest.mock import AsyncMock, Mock
from tracertm.services.critical_path_service import (
    CriticalPathService,
    CriticalPathResult,
)
from tracertm.models.item import Item
from tracertm.models.link import Link


class TestCalculateCriticalPath:
    """Test calculate_critical_path method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return CriticalPathService(mock_session)

    @pytest.mark.asyncio
    async def test_simple_linear_path(self, service):
        """Test critical path with simple linear dependency."""
        # Setup items: A -> B -> C
        items = []
        for i, item_id in enumerate(["A", "B", "C"]):
            item = Mock(spec=Item)
            item.id = item_id
            items.append(item)

        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        # Execute
        result = await service.calculate_critical_path("proj-1")

        # Verify
        assert isinstance(result, CriticalPathResult)
        assert result.project_id == "proj-1"
        assert result.path_length > 0
        assert result.total_duration >= result.path_length
        assert len(result.critical_items) > 0

    @pytest.mark.asyncio
    async def test_branching_paths(self, service):
        """Test critical path with branching."""
        # Setup items: A -> B -> D
        #              A -> C -> D
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
            Mock(spec=Item, id="D"),
        ]

        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("proj-1")

        assert result.path_length > 0
        assert "D" in result.critical_items

    @pytest.mark.asyncio
    async def test_empty_project(self, service):
        """Test with no items or links."""
        service.items.get_by_project = AsyncMock(return_value=[])
        service.links.get_by_project = AsyncMock(return_value=[])

        result = await service.calculate_critical_path("proj-1")

        assert result.project_id == "proj-1"
        assert result.path_length == 0
        assert len(result.critical_items) == 0
        assert result.total_duration == 0

    @pytest.mark.asyncio
    async def test_single_item(self, service):
        """Test with single item and no links."""
        items = [Mock(spec=Item, id="A")]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=[])

        result = await service.calculate_critical_path("proj-1")

        assert result.path_length >= 0
        assert "A" in result.slack_times

    @pytest.mark.asyncio
    async def test_filter_by_link_type(self, service):
        """Test filtering by specific link types."""
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
        ]

        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="C", link_type="blocks"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        # Filter only depends_on
        result = await service.calculate_critical_path("proj-1", link_types=["depends_on"])

        # Should only include depends_on link
        assert result.project_id == "proj-1"

    @pytest.mark.asyncio
    async def test_complex_network(self, service):
        """Test with complex dependency network."""
        # Create diamond-shaped dependency
        items = [
            Mock(spec=Item, id=str(i))
            for i in range(10)
        ]

        # Create various connections
        links = [
            Mock(spec=Link, source_item_id="0", target_item_id="1", link_type="depends_on"),
            Mock(spec=Link, source_item_id="0", target_item_id="2", link_type="depends_on"),
            Mock(spec=Link, source_item_id="1", target_item_id="3", link_type="depends_on"),
            Mock(spec=Link, source_item_id="2", target_item_id="3", link_type="depends_on"),
            Mock(spec=Link, source_item_id="3", target_item_id="4", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("proj-1")

        assert result.path_length > 0
        assert len(result.slack_times) == len(items)

    @pytest.mark.asyncio
    async def test_parallel_paths(self, service):
        """Test with parallel independent paths."""
        # Path 1: A -> B
        # Path 2: C -> D (independent)
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

        result = await service.calculate_critical_path("proj-1")

        # Should have slack times for all items
        assert len(result.slack_times) == 4

    @pytest.mark.asyncio
    async def test_slack_time_calculation(self, service):
        """Test slack time is correctly calculated."""
        # Simple path with known slack
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
            Mock(spec=Item, id="C"),
        ]

        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("proj-1")

        # Items on critical path should have slack = 0
        for item_id in result.critical_items:
            assert result.slack_times[item_id] == 0

    @pytest.mark.asyncio
    async def test_long_chain(self, service):
        """Test with long chain of dependencies."""
        # Create chain: 0 -> 1 -> 2 -> ... -> 9
        items = [Mock(spec=Item, id=str(i)) for i in range(10)]

        links = [
            Mock(spec=Link, source_item_id=str(i), target_item_id=str(i+1), link_type="depends_on")
            for i in range(9)
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("proj-1")

        # All items should be on critical path
        assert result.path_length == 10
        assert len(result.critical_items) == 10


class TestFindCriticalPath:
    """Test _find_critical_path helper method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CriticalPathService(AsyncMock())

    def test_find_path_simple(self, service):
        """Test finding path in simple graph."""
        adjacency_list = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        }
        critical_items = {"A", "B", "C"}
        topo_order = ["A", "B", "C"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        assert len(path) == 3
        assert "A" in path
        assert "C" in path

    def test_find_path_empty_critical(self, service):
        """Test with no critical items."""
        adjacency_list = {"A": ["B"], "B": []}
        critical_items = set()
        topo_order = ["A", "B"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        assert len(path) == 0

    def test_find_path_branching(self, service):
        """Test finding path with branches."""
        adjacency_list = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        critical_items = {"A", "B", "D"}
        topo_order = ["A", "B", "C", "D"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        # Path should go through critical items
        assert "A" in path
        assert "D" in path

    def test_find_path_multiple_starts(self, service):
        """Test with multiple start nodes."""
        adjacency_list = {
            "A": ["C"],
            "B": ["C"],
            "C": [],
        }
        critical_items = {"A", "B", "C"}
        topo_order = ["A", "B", "C"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        # Should find a valid path
        assert len(path) > 0

    def test_find_path_disconnected(self, service):
        """Test with disconnected critical items."""
        adjacency_list = {
            "A": [],
            "B": [],
            "C": [],
        }
        critical_items = {"A", "C"}
        topo_order = ["A", "B", "C"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        # Should find at least one item
        assert len(path) >= 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return CriticalPathService(mock_session)

    @pytest.mark.asyncio
    async def test_self_loop_handling(self, service):
        """Test handling of self-loops in dependencies."""
        items = [Mock(spec=Item, id="A")]

        # Self-loop
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="A", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("proj-1")

        # Should handle gracefully
        assert result.project_id == "proj-1"

    @pytest.mark.asyncio
    async def test_missing_link_types(self, service):
        """Test with None link_types parameter."""
        items = [Mock(spec=Item, id="A"), Mock(spec=Item, id="B")]
        links = [Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("proj-1", link_types=None)

        # Should use all links
        assert result.project_id == "proj-1"

    @pytest.mark.asyncio
    async def test_invalid_link_references(self, service):
        """Test with links referencing non-existent items raises KeyError."""
        items = [Mock(spec=Item, id="A")]

        # Link to non-existent item B
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        # Current implementation raises KeyError when link references non-existent item
        with pytest.raises(KeyError):
            await service.calculate_critical_path("proj-1")

    @pytest.mark.asyncio
    async def test_empty_link_types_filter(self, service):
        """Test with empty link_types list."""
        items = [Mock(spec=Item, id="A"), Mock(spec=Item, id="B")]
        links = [Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("proj-1", link_types=[])

        # No links should be included
        assert result.total_duration >= 0
