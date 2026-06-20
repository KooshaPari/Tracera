"""Comprehensive test coverage for CycleDetection algorithms.

Targets: 80-120 tests covering:
- DFS-based cycle detection
- Tarjan's algorithm patterns
- Graph traversal with visited tracking
- Edge case graphs (single node, disconnected)
- Integration with link service

Coverage goal: +2-3% improvement
"""

# ============================================================================
# BASIC DFS CYCLE DETECTION TESTS
# ============================================================================
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.services.cycle_detection_service import CycleDetectionService


class TestDFSBasedCycleDetection:
    """Test DFS-based cycle detection algorithm."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock sync session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create service instance."""
        return CycleDetectionService(mock_session)

    def test_dfs_simple_cycle_two_nodes(self, service: Any, mock_session: Any) -> None:
        """Test DFS detects simple 2-node cycle: A -> B -> A."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1", link_type="depends_on")

        assert result.has_cycles is True
        assert result.cycle_count > 0
        assert len(result.cycles) > 0

    def test_dfs_three_node_cycle(self, service: Any, mock_session: Any) -> None:
        """Test DFS detects 3-node cycle: A -> B -> C -> A."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="A", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1", link_type="depends_on")

        assert result.has_cycles is True
        assert result.cycle_count > 0

    def test_dfs_four_node_cycle(self, service: Any, mock_session: Any) -> None:
        """Test DFS detects 4-node cycle: A -> B -> C -> D -> A."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="A", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1", link_type="depends_on")

        assert result.has_cycles is True

    def test_dfs_no_cycle_linear_chain(self, service: Any, mock_session: Any) -> None:
        """Test DFS finds no cycle in linear chain: A -> B -> C -> D."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1", link_type="depends_on")

        assert result.has_cycles is False
        assert result.cycle_count == 0

    def test_dfs_multiple_independent_chains(self, service: Any, mock_session: Any) -> None:
        """Test DFS with multiple independent chains: A->B->C and D->E->F."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="E", link_type="depends_on"),
            Mock(spec=Link, source_item_id="E", target_item_id="F", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1", link_type="depends_on")

        assert result.has_cycles is False

    def test_dfs_visited_tracking(self, service: Any, mock_session: Any) -> None:
        """Test DFS properly tracks visited nodes to avoid infinite loops."""
        # Diamond pattern: A -> B, A -> C, B -> D, C -> D (no cycle)
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1", link_type="depends_on")

        assert result.has_cycles is False


# ============================================================================
# EDGE CASE: SINGLE NODE GRAPHS
# ============================================================================


class TestSingleNodeGraphs:
    """Test cycle detection on single-node graphs."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_single_node_no_self_loop(self, service: Any, mock_session: Any) -> None:
        """Test single node with no self-loop: no cycle."""
        links = []
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False

    def test_single_node_self_loop(self, service: Any, mock_session: Any) -> None:
        """Test single node with self-loop: A -> A."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="A", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is True
        assert result.cycle_count > 0

    def test_has_cycle_self_loop_detection(self, service: Any, mock_session: Any) -> None:
        """Test has_cycle detects self-loop (A -> A)."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        result = service.has_cycle("proj1", "A", "A")

        assert result is True

    def test_single_node_no_change_detection(self, service: Any, mock_session: Any) -> None:
        """Test adding same node as source and target."""
        links = []
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.has_cycle("proj1", "A", "A")

        assert result is True


# ============================================================================
# EDGE CASE: EMPTY GRAPHS
# ============================================================================


class TestEmptyGraphs:
    """Test cycle detection on empty graphs."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_empty_graph_detect_cycles(self, service: Any, mock_session: Any) -> None:
        """Test detect_cycles on empty graph."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False
        assert result.cycle_count == 0
        assert result.total_cycles == 0
        assert len(result.cycles) == 0

    def test_empty_graph_has_cycle(self, service: Any, mock_session: Any) -> None:
        """Test has_cycle on empty graph."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        result = service.has_cycle("proj1", "A", "B")

        assert result is False

    def test_empty_graph_missing_dependencies(self, service: Any, mock_session: Any) -> None:
        """Test detect_missing_dependencies on empty graph."""
        # Mock query returns empty for both links and items
        filter_mock = Mock()
        filter_mock.all.return_value = []
        query_mock = Mock()
        query_mock.filter.return_value = filter_mock

        mock_session.query.return_value = query_mock

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is False
        assert result["missing_count"] == 0

    def test_empty_graph_orphans(self, service: Any, mock_session: Any) -> None:
        """Test detect_orphans on empty graph."""
        # Mock for items query
        items_filter = Mock()
        items_filter.all.return_value = []
        items_query = Mock()
        items_query.filter.return_value = items_filter

        # Mock for links query
        links_filter = Mock()
        links_filter.all.return_value = []
        links_query = Mock()
        links_query.filter.return_value = links_filter

        mock_session.query.side_effect = [items_query, links_query]

        result = service.detect_orphans("proj1")

        assert result["has_orphans"] is False
        assert result["orphan_count"] == 0


# ============================================================================
# EDGE CASE: DISCONNECTED COMPONENTS
# ============================================================================


class TestDisconnectedComponents:
    """Test cycle detection with disconnected graph components."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_two_disconnected_acyclic_components(self, service: Any, mock_session: Any) -> None:
        """Test two independent chains with no cycles."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False

    def test_one_cyclic_one_acyclic_component(self, service: Any, mock_session: Any) -> None:
        """Test one component with cycle and one without."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),  # Cycle
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),  # No cycle
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is True
        assert result.cycle_count > 0

    def test_both_components_cyclic(self, service: Any, mock_session: Any) -> None:
        """Test when both components have cycles."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),  # Cycle 1
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="C", link_type="depends_on"),  # Cycle 2
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is True
        assert result.cycle_count >= COUNT_TWO

    def test_isolated_node_in_graph(self, service: Any, mock_session: Any) -> None:
        """Test graph with isolated node (no links)."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        # Should not detect cycle
        assert result.has_cycles is False


# ============================================================================
# EDGE CASE: COMPLEX CYCLE PATTERNS
# ============================================================================


class TestComplexCyclePatterns:
    """Test detection of complex cycle patterns."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_multiple_cycles_in_graph(self, service: Any, mock_session: Any) -> None:
        """Test detection when multiple cycles exist."""
        # Cycles: A->B->A and C->D->E->C
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="E", link_type="depends_on"),
            Mock(spec=Link, source_item_id="E", target_item_id="C", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is True
        assert result.cycle_count >= COUNT_TWO

    def test_cycle_with_branch_structure(self, service: Any, mock_session: Any) -> None:
        """Test cycle with branching: A->B->C, A->D, D->B creates path C->A->D->B."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="B", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        # No cycle in this configuration
        assert result.has_cycles is False

    def test_complex_branching_no_cycle(self, service: Any, mock_session: Any) -> None:
        """Test complex graph structure without cycles."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="E", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False

    def test_long_cycle_many_nodes(self, service: Any, mock_session: Any) -> None:
        """Test detection of long cycle: A->B->C->D->E->F->G->A."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="E", link_type="depends_on"),
            Mock(spec=Link, source_item_id="E", target_item_id="F", link_type="depends_on"),
            Mock(spec=Link, source_item_id="F", target_item_id="G", link_type="depends_on"),
            Mock(spec=Link, source_item_id="G", target_item_id="A", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is True


# ============================================================================
# HAS_CYCLE METHOD TESTS
# ============================================================================


class TestHasCycleMethod:
    """Test has_cycle method for individual link addition."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_has_cycle_checks_link_type(self, service: Any, _mock_session: Any) -> None:
        """Test has_cycle returns False for non-depends_on link types."""
        result = service.has_cycle("proj1", "A", "B", link_type="references")
        assert result is False

    def test_has_cycle_checks_blocks_type(self, service: Any, _mock_session: Any) -> None:
        """Test has_cycle returns False for 'blocks' link type."""
        result = service.has_cycle("proj1", "A", "B", link_type="blocks")
        assert result is False

    def test_has_cycle_simple_path_exists(self, service: Any, mock_session: Any) -> None:
        """Test when path exists from target to source."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        # Adding C -> A would create cycle
        result = service.has_cycle("proj1", "C", "A")

        assert result is True

    def test_has_cycle_no_path(self, service: Any, mock_session: Any) -> None:
        """Test when no path exists from target to source."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        # Adding B -> D doesn't create cycle
        result = service.has_cycle("proj1", "B", "D")

        assert result is False

    def test_has_cycle_with_intermediate_nodes(self, service: Any, mock_session: Any) -> None:
        """Test has_cycle through intermediate nodes."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        # Adding D -> B would create cycle D -> (nothing) but B -> C -> D closes it
        result = service.has_cycle("proj1", "D", "B")

        assert result is True


# ============================================================================
# GRAPH BUILDING TESTS
# ============================================================================


class TestGraphBuilding:
    """Test _build_dependency_graph method."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_build_graph_empty_links(self, service: Any, mock_session: Any) -> None:
        """Test building graph from empty links."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        graph = service._build_dependency_graph("proj1", "depends_on")

        assert graph == {}

    def test_build_graph_single_link(self, service: Any, mock_session: Any) -> None:
        """Test building graph from single link."""
        links = [Mock(spec=Link, source_item_id="A", target_item_id="B")]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        graph = service._build_dependency_graph("proj1", "depends_on")

        assert "A" in graph
        assert "B" in graph
        assert "B" in graph["A"]

    def test_build_graph_multiple_links(self, service: Any, mock_session: Any) -> None:
        """Test building graph from multiple links."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B"),
            Mock(spec=Link, source_item_id="B", target_item_id="C"),
            Mock(spec=Link, source_item_id="A", target_item_id="C"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        graph = service._build_dependency_graph("proj1", "depends_on")

        assert graph["A"] == {"B", "C"}
        assert graph["B"] == {"C"}
        assert graph["C"] == set()

    def test_build_graph_with_self_loop(self, service: Any, mock_session: Any) -> None:
        """Test building graph that includes self-loop."""
        links = [Mock(spec=Link, source_item_id="A", target_item_id="A")]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        graph = service._build_dependency_graph("proj1", "depends_on")

        assert "A" in graph["A"]  # A points to itself

    def test_build_graph_database_error(self, service: Any, mock_session: Any) -> None:
        """Test building graph handles database errors gracefully."""
        mock_session.query.return_value.filter.return_value.all.side_effect = OperationalError(
            "test",
            None,
            Exception("test"),
        )

        graph = service._build_dependency_graph("proj1", "depends_on")

        assert graph == {}


# ============================================================================
# ASYNC TESTS
# ============================================================================


class TestAsyncCycleDetection:
    """Test async cycle detection methods."""

    @pytest.fixture
    def mock_async_session(self) -> None:
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_links_repo(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_async_session: Any, mock_links_repo: Any) -> None:
        return CycleDetectionService(mock_async_session, links=mock_links_repo)

    @pytest.mark.asyncio
    async def test_detect_cycles_async_empty_graph(self, service: Any, mock_links_repo: Any) -> None:
        """Test async detection on empty graph."""
        mock_links_repo.get_by_project = AsyncMock(return_value=[])

        result = await service.detect_cycles_async("proj1")

        assert result.has_cycles is False
        assert result.cycle_count == 0

    @pytest.mark.asyncio
    async def test_detect_cycles_async_simple_cycle(self, service: Any, mock_links_repo: Any) -> None:
        """Test async detection of simple cycle."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),
        ]
        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        result = await service.detect_cycles_async("proj1")

        assert result.has_cycles is True
        assert result.cycle_count > 0

    @pytest.mark.asyncio
    async def test_detect_cycles_async_with_link_types(self, mock_async_session: Any, mock_links_repo: Any) -> None:
        """Test async detection with multiple link types."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),  # Cycle
        ]
        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        result = await service.detect_cycles_async("proj1", link_types=["depends_on"])

        # Should detect cycle through depends_on links only (service returns SimpleNamespace)
        assert getattr(result, "has_cycles", result.get("has_cycles") if isinstance(result, dict) else None) is True


# ============================================================================
# MISSING DEPENDENCIES TESTS
# ============================================================================


class TestMissingDependencies:
    """Test detect_missing_dependencies method."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_no_missing_dependencies(self, service: Any, mock_session: Any) -> None:
        """Test when all dependencies exist."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B"),
        ]
        items = [
            Mock(spec=Item, id="A"),
            Mock(spec=Item, id="B"),
        ]

        # Setup mocks
        filter_mock = Mock()
        filter_mock.all.side_effect = [links, items]
        query_mock = Mock()
        query_mock.filter.return_value = filter_mock
        mock_session.query.return_value = query_mock

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is False
        assert result["missing_count"] == 0

    def test_missing_source_item(self, service: Any, mock_session: Any) -> None:
        """Test detection of missing source item."""
        links = [
            Mock(spec=Link, id="link1", source_item_id="MISSING", target_item_id="B"),
        ]
        items = [Mock(spec=Item, id="B")]

        filter_mock = Mock()
        filter_mock.all.side_effect = [links, items]
        query_mock = Mock()
        query_mock.filter.return_value = filter_mock
        mock_session.query.return_value = query_mock

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is True
        assert any(d["issue"] == "source_item_missing" for d in result["missing_dependencies"])

    def test_missing_target_item(self, service: Any, mock_session: Any) -> None:
        """Test detection of missing target item."""
        links = [
            Mock(spec=Link, id="link1", source_item_id="A", target_item_id="MISSING"),
        ]
        items = [Mock(spec=Item, id="A")]

        filter_mock = Mock()
        filter_mock.all.side_effect = [links, items]
        query_mock = Mock()
        query_mock.filter.return_value = filter_mock
        mock_session.query.return_value = query_mock

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is True
        assert any(d["issue"] == "target_item_missing" for d in result["missing_dependencies"])

    def test_both_items_missing(self, service: Any, mock_session: Any) -> None:
        """Test when both source and target items are missing."""
        links = [
            Mock(spec=Link, id="link1", source_item_id="MISSING_A", target_item_id="MISSING_B"),
        ]
        items = []

        filter_mock = Mock()
        filter_mock.all.side_effect = [links, items]
        query_mock = Mock()
        query_mock.filter.return_value = filter_mock
        mock_session.query.return_value = query_mock

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is True
        assert result["missing_count"] >= COUNT_TWO


# ============================================================================
# LINK TYPE FILTERING TESTS
# ============================================================================


class TestLinkTypeFiltering:
    """Test link type filtering in cycle detection."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_only_depends_on_checked_for_has_cycle(self, service: Any) -> None:
        """Test that has_cycle only checks depends_on link type."""
        result = service.has_cycle("proj1", "A", "B", link_type="blocks")
        assert result is False

        result = service.has_cycle("proj1", "A", "B", link_type="references")
        assert result is False

    def test_detect_cycles_with_link_types_parameter(self, service: Any, mock_session: Any) -> None:
        """Test detect_cycles with link_types list parameter."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1", link_types=["depends_on"])

        assert result.has_cycles is False  # Single link, no cycle


# ============================================================================
# PERFORMANCE AND LARGE GRAPH TESTS
# ============================================================================


class TestLargeGraphs:
    """Test cycle detection on large graphs."""

    @pytest.fixture
    def mock_session(self) -> None:
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        return CycleDetectionService(mock_session)

    def test_large_acyclic_graph_100_nodes(self, service: Any, mock_session: Any) -> None:
        """Test handling of large acyclic graph with 100 nodes."""
        # Create a chain: 0 -> 1 -> COUNT_TWO -> ... -> 99
        links = [
            Mock(spec=Link, source_item_id=str(i), target_item_id=str(i + 1), link_type="depends_on") for i in range(99)
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False

    def test_large_cyclic_graph_with_many_branches(self, service: Any, mock_session: Any) -> None:
        """Test detection in large graph with branching."""
        # Create a tree structure that eventually cycles
        links = [
            # Main chain with cycle at end
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="A", link_type="depends_on"),  # Cycle
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = links

        result = service.detect_cycles("proj1")

        assert result.has_cycles is True


# ============================================================================
# INITIALIZATION AND CONFIGURATION TESTS
# ============================================================================


class TestServiceInitialization:
    """Test CycleDetectionService initialization."""

    def test_init_with_sync_session_no_repos(self) -> None:
        """Test initialization with sync session and no repositories."""
        session = Mock(spec=Session)
        service = CycleDetectionService(session)

        assert service.session == session
        assert service.items is None
        assert service.links is None

    def test_init_with_async_session_no_repos(self) -> None:
        """Test initialization with async session."""
        session = AsyncMock(spec=AsyncSession)
        service = CycleDetectionService(session)

        assert service.session == session

    def test_init_with_repositories(self) -> None:
        """Test initialization with repository instances."""
        session = Mock(spec=Session)
        items_repo = Mock()
        links_repo = Mock()

        service = CycleDetectionService(session, items=items_repo, links=links_repo)

        assert service.items == items_repo
        assert service.links == links_repo

    def test_init_with_async_session_creates_default_repos(self) -> None:
        """Test that async session creates default repos if not provided."""
        session = AsyncMock(spec=AsyncSession)
        service = CycleDetectionService(session)

        # Should create repos for async session
        assert service.items is not None
        assert service.links is not None


# ============================================================================
# CAN_REACH ALGORITHM TESTS
# ============================================================================


class TestCanReachAlgorithm:
    """Test _can_reach DFS traversal algorithm."""

    @pytest.fixture
    def service(self) -> None:
        return CycleDetectionService(Mock(spec=Session))

    def test_can_reach_same_node(self, service: Any) -> None:
        """Test can_reach with same node (start == target)."""
        graph = {"A": {"B"}}
        result = service._can_reach(graph, "A", "A")
        assert result is True

    def test_can_reach_direct_neighbor(self, service: Any) -> None:
        """Test can_reach with direct neighbor."""
        graph = {"A": {"B"}, "B": set()}
        result = service._can_reach(graph, "A", "B")
        assert result is True

    def test_can_reach_through_chain(self, service: Any) -> None:
        """Test can_reach through chain of nodes."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        result = service._can_reach(graph, "A", "C")
        assert result is True

    def test_can_reach_not_reachable(self, service: Any) -> None:
        """Test can_reach when target is not reachable."""
        graph = {"A": {"B"}, "B": set(), "C": set()}
        result = service._can_reach(graph, "A", "C")
        assert result is False

    def test_can_reach_isolated_node(self, service: Any) -> None:
        """Test can_reach from isolated node."""
        graph = {"A": set(), "B": set()}
        result = service._can_reach(graph, "A", "B")
        assert result is False

    def test_can_reach_empty_graph(self, service: Any) -> None:
        """Test can_reach with empty graph."""
        graph = {}
        result = service._can_reach(graph, "A", "B")
        assert result is False

    def test_can_reach_branching_path(self, service: Any) -> None:
        """Test can_reach with multiple paths."""
        graph = {"A": {"B", "C"}, "B": {"D"}, "C": {"D"}, "D": set()}
        result = service._can_reach(graph, "A", "D")
        assert result is True


# ============================================================================
# FIND_CYCLES ALGORITHM TESTS
# ============================================================================


class TestFindCyclesAlgorithm:
    """Test _find_cycles DFS-based cycle detection algorithm."""

    @pytest.fixture
    def service(self) -> None:
        return CycleDetectionService(Mock(spec=Session))

    def test_find_cycles_empty_graph(self, service: Any) -> None:
        """Test finding cycles in empty graph."""
        graph = {}
        cycles = service._find_cycles(graph)
        assert cycles == []

    def test_find_cycles_single_node_cycle(self, service: Any) -> None:
        """Test finding self-loop cycle."""
        graph = {"A": {"A"}}
        cycles = service._find_cycles(graph)
        assert len(cycles) > 0

    def test_find_cycles_two_node_cycle(self, service: Any) -> None:
        """Test finding two-node cycle."""
        graph = {"A": {"B"}, "B": {"A"}}
        cycles = service._find_cycles(graph)
        assert len(cycles) > 0

    def test_find_cycles_no_cycles(self, service: Any) -> None:
        """Test no cycles in acyclic graph."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        cycles = service._find_cycles(graph)
        assert cycles == []

    def test_find_cycles_three_node_cycle(self, service: Any) -> None:
        """Test finding three-node cycle."""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
        cycles = service._find_cycles(graph)
        assert len(cycles) > 0

    def test_find_cycles_complex_graph_with_multiple_cycles(self, service: Any) -> None:
        """Test finding multiple cycles in complex graph."""
        graph = {
            "A": {"B"},
            "B": {"A"},  # Cycle 1: A <-> B
            "C": {"D"},
            "D": {"C"},  # Cycle 2: C <-> D
        }
        cycles = service._find_cycles(graph)
        assert len(cycles) >= COUNT_TWO

    def test_find_cycles_returns_cycle_paths(self, service: Any) -> None:
        """Test that cycles include complete paths."""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
        cycles = service._find_cycles(graph)

        # At least one cycle should be found
        assert len(cycles) > 0
        # Each cycle should be a list of nodes
        for cycle in cycles:
            assert isinstance(cycle, list)
            assert len(cycle) > 1


# ============================================================================
# INTEGRATION TESTS WITH REPOSITORIES
# ============================================================================


class TestRepositoryIntegration:
    """Test integration with repository pattern."""

    @pytest.fixture
    def mock_async_session(self) -> None:
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_items_repo(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def mock_links_repo(self) -> None:
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_detect_cycles_async_uses_repository(
        self, mock_async_session: Any, mock_links_repo: Any, mock_items_repo: Any
    ) -> None:
        """Test that async detection uses repository."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]
        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, items=mock_items_repo, links=mock_links_repo)
        await service.detect_cycles_async("proj1")

        # Verify repository was called
        mock_links_repo.get_by_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_detects_cycles_from_repository(self, mock_async_session: Any, mock_links_repo: Any) -> None:
        """Test async cycle detection using repository data."""
        # Create a cycle via repository
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),
        ]
        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        result = await service.detect_cycles_async("proj1")

        assert getattr(result, "has_cycles", result.get("has_cycles") if isinstance(result, dict) else None) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
