"""
Comprehensive tests for CycleDetectionService.

Tests all methods including:
- has_cycle
- detect_cycles
- detect_cycles_async
- _build_dependency_graph
- _build_dependency_graph_async
- _can_reach
- _find_cycles

Coverage target: 90%+
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.models.link import Link


class TestHasCycle:
    """Test has_cycle method."""

    @pytest.fixture
    def mock_async_session(self):
        """Create mock async session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_sync_session(self):
        """Create mock sync session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service_async(self, mock_async_session):
        """Create service with async session."""
        return CycleDetectionService(mock_async_session)

    def test_has_cycle_non_depends_on(self, service_async):
        """Test has_cycle returns False for non-depends_on link types."""
        result = service_async.has_cycle("proj-1", "A", "B", link_type="blocks")

        assert result is False

    def test_has_cycle_simple_cycle(self, mock_sync_session):
        """Test detection of simple cycle."""
        # Setup: A -> B, B -> C, adding C -> A would create cycle
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]

        mock_sync_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_sync_session)
        result = service.has_cycle("proj-1", "C", "A", link_type="depends_on")

        assert result is True

    def test_has_cycle_no_cycle(self, mock_sync_session):
        """Test when no cycle exists."""
        # Setup: A -> B, B -> C, adding A -> D won't create cycle
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]

        mock_sync_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_sync_session)
        result = service.has_cycle("proj-1", "A", "D", link_type="depends_on")

        assert result is False

    def test_has_cycle_self_loop(self, mock_sync_session):
        """Test detection of self-loop."""
        mock_sync_session.query.return_value.filter.return_value.all.return_value = []

        service = CycleDetectionService(mock_sync_session)
        result = service.has_cycle("proj-1", "A", "A", link_type="depends_on")

        # Self-loop is detected by _can_reach
        assert result is True

    def test_has_cycle_empty_graph(self, mock_sync_session):
        """Test with empty dependency graph."""
        mock_sync_session.query.return_value.filter.return_value.all.return_value = []

        service = CycleDetectionService(mock_sync_session)
        result = service.has_cycle("proj-1", "A", "B", link_type="depends_on")

        assert result is False


class TestDetectCycles:
    """Test detect_cycles method (sync version)."""

    @pytest.fixture
    def mock_sync_session(self):
        """Create mock sync session."""
        return Mock(spec=Session)

    def test_detect_no_cycles(self, mock_sync_session):
        """Test when no cycles exist."""
        # Linear chain: A -> B -> C
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]

        mock_sync_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_sync_session)
        result = service.detect_cycles("proj-1")

        assert result.has_cycles is False
        assert result.cycle_count == 0
        assert len(result.cycles) == 0

    def test_detect_simple_cycle(self, mock_sync_session):
        """Test detection of simple cycle."""
        # Cycle: A -> B -> C -> A
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="A", link_type="depends_on"),
        ]

        mock_sync_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_sync_session)
        result = service.detect_cycles("proj-1")

        assert result.has_cycles is True
        assert result.cycle_count > 0

    def test_detect_cycles_with_link_types(self, mock_sync_session):
        """Test detection with specific link types."""
        # The sync version uses _build_dependency_graph which queries with a single link_type
        # So we need to return only depends_on links (simulating what DB would return)
        depends_on_links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]

        mock_sync_session.query.return_value.filter.return_value.all.return_value = depends_on_links

        service = CycleDetectionService(mock_sync_session)
        result = service.detect_cycles("proj-1", link_types=["depends_on"])

        # Should not detect cycle since there's only A -> B (no cycle)
        assert result.has_cycles is False

    def test_detect_cycles_empty_project(self, mock_sync_session):
        """Test with empty project."""
        mock_sync_session.query.return_value.filter.return_value.all.return_value = []

        service = CycleDetectionService(mock_sync_session)
        result = service.detect_cycles("proj-1")

        assert result.has_cycles is False
        assert result.total_cycles == 0


class TestDetectCyclesAsync:
    """Test detect_cycles_async method."""

    @pytest.fixture
    def mock_async_session(self):
        """Create mock async session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_links_repo(self):
        """Create mock links repository."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_detect_async_no_cycles(self, mock_async_session, mock_links_repo):
        """Test async detection with no cycles."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        result = await service.detect_cycles_async("proj-1")

        assert result.has_cycles is False
        assert result.cycle_count == 0

    @pytest.mark.asyncio
    async def test_detect_async_with_cycles(self, mock_async_session, mock_links_repo):
        """Test async detection with cycles."""
        # Cycle: A -> B -> A
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        result = await service.detect_cycles_async("proj-1")

        assert result.has_cycles is True
        assert result.cycle_count > 0

    @pytest.mark.asyncio
    async def test_detect_async_with_link_types(self, mock_async_session, mock_links_repo):
        """Test async detection filtering by link types."""
        # Create a true cycle with depends_on links only: A -> B -> C -> A
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="A", link_type="depends_on"),
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        result = await service.detect_cycles_async("proj-1", link_types=["depends_on"])

        # Should detect cycle through depends_on links
        assert result.has_cycles is True

    @pytest.mark.asyncio
    async def test_detect_async_empty(self, mock_async_session, mock_links_repo):
        """Test async detection with no links."""
        mock_links_repo.get_by_project = AsyncMock(return_value=[])

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        result = await service.detect_cycles_async("proj-1")

        assert result.has_cycles is False


class TestBuildDependencyGraph:
    """Test _build_dependency_graph method (sync)."""

    @pytest.fixture
    def mock_sync_session(self):
        """Create mock sync session."""
        return Mock(spec=Session)

    def test_build_graph_success(self, mock_sync_session):
        """Test building dependency graph."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]

        mock_sync_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_sync_session)
        graph = service._build_dependency_graph("proj-1", "depends_on")

        assert "A" in graph
        assert "B" in graph["A"]
        assert "C" in graph["B"]

    def test_build_graph_operational_error(self, mock_sync_session):
        """Test handling of OperationalError (table not exists)."""
        mock_sync_session.query.return_value.filter.return_value.all.side_effect = OperationalError(
            "table does not exist", None, None
        )

        service = CycleDetectionService(mock_sync_session)
        graph = service._build_dependency_graph("proj-1", "depends_on")

        # Should return empty graph on error
        assert graph == {}

    def test_build_graph_empty(self, mock_sync_session):
        """Test building graph with no links."""
        mock_sync_session.query.return_value.filter.return_value.all.return_value = []

        service = CycleDetectionService(mock_sync_session)
        graph = service._build_dependency_graph("proj-1", "depends_on")

        assert graph == {}

    def test_build_graph_async_session_returns_empty(self, ):
        """Test that async session returns empty graph in sync method."""
        mock_async_session = AsyncMock(spec=AsyncSession)

        service = CycleDetectionService(mock_async_session)
        graph = service._build_dependency_graph("proj-1", "depends_on")

        # Should return empty for async sessions
        assert graph == {}


class TestBuildDependencyGraphAsync:
    """Test _build_dependency_graph_async method."""

    @pytest.fixture
    def mock_async_session(self):
        """Create mock async session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_links_repo(self):
        """Create mock links repository."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_build_graph_async_success(self, mock_async_session, mock_links_repo):
        """Test async graph building."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        graph = await service._build_dependency_graph_async("proj-1", ["depends_on"])

        assert "A" in graph
        assert "B" in graph["A"]

    @pytest.mark.asyncio
    async def test_build_graph_async_filter_types(self, mock_async_session, mock_links_repo):
        """Test async graph building filters by link types."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="blocks"),
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        graph = await service._build_dependency_graph_async("proj-1", ["depends_on"])

        # Should only include depends_on link
        assert "A" in graph
        assert "B" in graph
        assert "C" not in graph.get("B", set())

    @pytest.mark.asyncio
    async def test_build_graph_async_empty(self, mock_async_session, mock_links_repo):
        """Test async graph building with no links."""
        mock_links_repo.get_by_project = AsyncMock(return_value=[])

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        graph = await service._build_dependency_graph_async("proj-1", ["depends_on"])

        assert graph == {}


class TestCanReach:
    """Test _can_reach method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CycleDetectionService(Mock())

    def test_can_reach_direct(self, service):
        """Test reachability with direct connection."""
        graph = {"A": {"B"}, "B": set()}

        assert service._can_reach(graph, "A", "B") is True

    def test_can_reach_indirect(self, service):
        """Test reachability through multiple hops."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}

        assert service._can_reach(graph, "A", "C") is True

    def test_can_reach_not_reachable(self, service):
        """Test when target is not reachable."""
        graph = {"A": {"B"}, "B": set(), "C": set()}

        assert service._can_reach(graph, "A", "C") is False

    def test_can_reach_same_node(self, service):
        """Test reachability to same node."""
        graph = {"A": set()}

        assert service._can_reach(graph, "A", "A") is True

    def test_can_reach_cycle(self, service):
        """Test reachability in cyclic graph."""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}

        assert service._can_reach(graph, "A", "C") is True
        assert service._can_reach(graph, "C", "A") is True

    def test_can_reach_empty_graph(self, service):
        """Test with empty graph."""
        graph = {}

        assert service._can_reach(graph, "A", "B") is False

    def test_can_reach_node_not_in_graph(self, service):
        """Test when start node not in graph."""
        graph = {"A": {"B"}, "B": set()}

        assert service._can_reach(graph, "C", "A") is False


class TestFindCycles:
    """Test _find_cycles method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CycleDetectionService(Mock())

    def test_find_no_cycles(self, service):
        """Test finding cycles in acyclic graph."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}

        cycles = service._find_cycles(graph)

        assert len(cycles) == 0

    def test_find_simple_cycle(self, service):
        """Test finding simple cycle."""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}

        cycles = service._find_cycles(graph)

        assert len(cycles) > 0

    def test_find_self_loop(self, service):
        """Test finding self-loop."""
        graph = {"A": {"A"}}

        cycles = service._find_cycles(graph)

        assert len(cycles) > 0

    def test_find_multiple_cycles(self, service):
        """Test finding multiple cycles."""
        # Two separate cycles
        graph = {
            "A": {"B"},
            "B": {"A"},
            "C": {"D"},
            "D": {"C"},
        }

        cycles = service._find_cycles(graph)

        assert len(cycles) >= 1

    def test_find_cycles_empty_graph(self, service):
        """Test with empty graph."""
        graph = {}

        cycles = service._find_cycles(graph)

        assert len(cycles) == 0
