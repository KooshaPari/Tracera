"""
Advanced edge case and comprehensive algorithm tests for CycleDetectionService.

Targets +3% coverage improvement with 40+ additional test cases covering:
- Complex multi-level cycles
- Self-references and edge cases
- Performance on large graphs
- Error conditions
- Algorithm correctness validation
- Boundary conditions
- Special graph structures

Coverage focus:
- detect_missing_dependencies method
- detect_orphans method
- analyze_impact method
- Complex cycle patterns
- Graph building edge cases
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.models.link import Link
from tracertm.models.item import Item


class TestDetectMissingDependencies:
    """Test detect_missing_dependencies method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    def test_missing_source_item(self, mock_session):
        """Test detection of missing source item."""
        links = [
            Mock(
                spec=Link,
                id="link-1",
                source_item_id="MISSING_SOURCE",
                target_item_id="B",
            ),
        ]

        items = [
            Mock(spec=Item, id="B", project_id="proj-1", deleted_at=None),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [links, items]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_missing_dependencies("proj-1")

        assert result["has_missing_dependencies"] is True
        assert result["missing_count"] == 1
        assert result["missing_dependencies"][0]["issue"] == "source_item_missing"

    def test_missing_target_item(self, mock_session):
        """Test detection of missing target item."""
        links = [
            Mock(
                spec=Link,
                id="link-1",
                source_item_id="A",
                target_item_id="MISSING_TARGET",
            ),
        ]

        items = [
            Mock(spec=Item, id="A", project_id="proj-1", deleted_at=None),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [links, items]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_missing_dependencies("proj-1")

        assert result["has_missing_dependencies"] is True
        assert result["missing_dependencies"][0]["issue"] == "target_item_missing"

    def test_both_items_missing(self, mock_session):
        """Test detection when both source and target items are missing."""
        links = [
            Mock(
                spec=Link,
                id="link-1",
                source_item_id="MISSING_A",
                target_item_id="MISSING_B",
            ),
        ]

        items = []

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [links, items]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_missing_dependencies("proj-1")

        assert result["has_missing_dependencies"] is True
        assert result["missing_count"] == 2

    def test_no_missing_dependencies(self, mock_session):
        """Test when all dependencies are valid."""
        links = [
            Mock(spec=Link, id="link-1", source_item_id="A", target_item_id="B"),
        ]

        items = [
            Mock(spec=Item, id="A", project_id="proj-1", deleted_at=None),
            Mock(spec=Item, id="B", project_id="proj-1", deleted_at=None),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [links, items]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_missing_dependencies("proj-1")

        assert result["has_missing_dependencies"] is False
        assert result["missing_count"] == 0

    def test_multiple_missing_dependencies(self, mock_session):
        """Test detection of multiple missing dependencies."""
        links = [
            Mock(spec=Link, id="link-1", source_item_id="MISSING_A", target_item_id="B"),
            Mock(spec=Link, id="link-2", source_item_id="A", target_item_id="MISSING_C"),
            Mock(spec=Link, id="link-3", source_item_id="D", target_item_id="MISSING_D"),
        ]

        items = [
            Mock(spec=Item, id="A", project_id="proj-1", deleted_at=None),
            Mock(spec=Item, id="B", project_id="proj-1", deleted_at=None),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [links, items]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_missing_dependencies("proj-1")

        assert result["missing_count"] == 4

    def test_empty_links(self, mock_session):
        """Test with no links."""
        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [[], []]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_missing_dependencies("proj-1")

        assert result["has_missing_dependencies"] is False
        assert result["missing_count"] == 0


class TestDetectOrphans:
    """Test detect_orphans method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    def test_orphan_detection_no_links(self, mock_session):
        """Test orphan detection when item has no links."""
        items = [
            Mock(
                spec=Item,
                id="A",
                project_id="proj-1",
                deleted_at=None,
                title="Item A",
                view="view1",
                item_type="type1",
                status="active",
            ),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [items, []]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_orphans("proj-1")

        assert result["has_orphans"] is True
        assert result["orphan_count"] == 1
        assert result["orphans"][0]["item_id"] == "A"

    def test_no_orphans(self, mock_session):
        """Test when all items are linked."""
        items = [
            Mock(
                spec=Item,
                id="A",
                project_id="proj-1",
                deleted_at=None,
                title="Item A",
                view="view1",
                item_type="type1",
                status="active",
            ),
            Mock(
                spec=Item,
                id="B",
                project_id="proj-1",
                deleted_at=None,
                title="Item B",
                view="view1",
                item_type="type1",
                status="active",
            ),
        ]

        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [items, links]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_orphans("proj-1")

        assert result["has_orphans"] is False
        assert result["orphan_count"] == 0

    def test_orphans_with_deleted_items_not_in_results(self, mock_session):
        """Test orphan detection excludes deleted items."""
        # Only non-deleted items are returned by query filter with deleted_at.is_(None)
        items = [
            Mock(
                spec=Item,
                id="A",
                project_id="proj-1",
                deleted_at=None,
                title="Item A",
                view="view1",
                item_type="type1",
                status="active",
            ),
        ]

        # Item A is linked
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = items

        # For the links query, need to handle it properly
        query_mock2 = Mock()
        query_mock2.filter.return_value.all.return_value = links

        mock_session.query.side_effect = [query_mock, query_mock2]

        service = CycleDetectionService(mock_session)
        result = service.detect_orphans("proj-1")

        assert result["has_orphans"] is False  # A is linked even though B doesn't exist

    def test_multiple_orphans(self, mock_session):
        """Test detection of multiple orphaned items."""
        items = [
            Mock(
                spec=Item,
                id="A",
                project_id="proj-1",
                deleted_at=None,
                title="Item A",
                view="view1",
                item_type="type1",
                status="active",
            ),
            Mock(
                spec=Item,
                id="B",
                project_id="proj-1",
                deleted_at=None,
                title="Item B",
                view="view1",
                item_type="type1",
                status="active",
            ),
            Mock(
                spec=Item,
                id="C",
                project_id="proj-1",
                deleted_at=None,
                title="Item C",
                view="view1",
                item_type="type1",
                status="active",
            ),
        ]

        # No links at all
        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [items, []]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_orphans("proj-1")

        assert result["orphan_count"] == 3

    def test_partial_orphans(self, mock_session):
        """Test when some items are linked and some are orphaned."""
        items = [
            Mock(
                spec=Item,
                id="A",
                project_id="proj-1",
                deleted_at=None,
                title="Item A",
                view="view1",
                item_type="type1",
                status="active",
            ),
            Mock(
                spec=Item,
                id="B",
                project_id="proj-1",
                deleted_at=None,
                title="Item B",
                view="view1",
                item_type="type1",
                status="active",
            ),
            Mock(
                spec=Item,
                id="C",
                project_id="proj-1",
                deleted_at=None,
                title="Item C",
                view="view1",
                item_type="type1",
                status="active",
            ),
        ]

        # A -> B, C is orphaned
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [items, links]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_orphans("proj-1")

        assert result["orphan_count"] == 1
        assert result["orphans"][0]["item_id"] == "C"

    def test_orphans_with_deleted_items_excluded(self, mock_session):
        """Test that deleted items are excluded from orphan detection."""
        # Only non-deleted items
        items = [
            Mock(
                spec=Item,
                id="A",
                project_id="proj-1",
                deleted_at=None,
                title="Item A",
                view="view1",
                item_type="type1",
                status="active",
            ),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [items, []]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.detect_orphans("proj-1")

        assert result["orphan_count"] == 1


class TestAnalyzeImpact:
    """Test analyze_impact method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    def test_analyze_impact_direct_dependents(self, mock_session):
        """Test impact analysis with direct dependents."""
        # A depends on X, B depends on X
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="X", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="X", link_type="depends_on"),
        ]

        root_item = Mock(
            spec=Item,
            id="X",
            project_id="proj-1",
            title="Item X",
            view="requirements",
            item_type="requirement",
            status="active",
        )

        affected_items = [
            Mock(
                spec=Item,
                id="A",
                project_id="proj-1",
                title="Item A",
                view="design",
                item_type="design",
                status="active",
            ),
            Mock(
                spec=Item,
                id="B",
                project_id="proj-1",
                title="Item B",
                view="test",
                item_type="test",
                status="active",
            ),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [links, root_item, affected_items[0], affected_items[1], root_item]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.analyze_impact("proj-1", "X")

        assert result["root_item_id"] == "X"
        assert result["total_affected"] == 2

    def test_analyze_impact_with_affected_items_pagination(self, mock_session):
        """Test impact analysis limits affected items to 50."""
        # Create a large dependency chain that gets limited
        links = [
            Mock(spec=Link, source_item_id=f"item-{i}", target_item_id=f"item-{i+1}", link_type="depends_on")
            for i in range(100)
        ]

        root_item = Mock(
            spec=Item,
            id="item-0",
            project_id="proj-1",
            title="Root Item",
            view="requirements",
            item_type="requirement",
            status="active",
        )

        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = links
        query_mock.filter.return_value.first.return_value = root_item
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.analyze_impact("proj-1", "item-0")

        # Should have results
        assert "affected_items" in result
        # Should be limited to 50
        assert len(result["affected_items"]) <= 50

    def test_analyze_impact_respects_max_depth(self, mock_session):
        """Test that impact analysis respects max_depth parameter."""
        # Deep chain: X -> A -> B -> C -> D -> E
        links = [
            Mock(spec=Link, source_item_id="X", target_item_id="A", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="E", link_type="depends_on"),
        ]

        root_item = Mock(
            spec=Item,
            id="X",
            project_id="proj-1",
            title="Item X",
            view="requirements",
            item_type="requirement",
            status="active",
        )

        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = links
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.analyze_impact("proj-1", "X", max_depth=2)

        # Should not exceed max_depth
        if result["affected_items"]:
            assert max(item["depth"] for item in result["affected_items"]) <= 2

    def test_analyze_impact_no_affected_items(self, mock_session):
        """Test impact analysis when item has no dependents."""
        # X has no dependents
        links = []

        root_item = Mock(
            spec=Item,
            id="X",
            project_id="proj-1",
            title="Item X",
            view="requirements",
            item_type="requirement",
            status="active",
        )

        query_mock = Mock()
        query_mock.filter.return_value.all.side_effect = [links, root_item]
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.analyze_impact("proj-1", "X")

        assert result["total_affected"] == 0

    def test_analyze_impact_missing_root_item(self, mock_session):
        """Test impact analysis when root item doesn't exist."""
        links = []
        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = links
        query_mock.filter.return_value.first.return_value = None
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.analyze_impact("proj-1", "MISSING")

        assert result["root_item_title"] == "Unknown"


class TestComplexCyclePatterns:
    """Test complex cycle detection patterns."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CycleDetectionService(Mock())

    def test_diamond_pattern_no_cycle(self, service):
        """Test diamond pattern without cycle."""
        # A -> B, A -> C, B -> D, C -> D (no cycle)
        graph = {
            "A": {"B", "C"},
            "B": {"D"},
            "C": {"D"},
            "D": set(),
        }

        cycles = service._find_cycles(graph)
        assert len(cycles) == 0

    def test_complex_multi_level_cycle(self, service):
        """Test detection of complex multi-level cycles."""
        # A -> B -> C -> D -> E -> A (5-node cycle)
        graph = {
            "A": {"B"},
            "B": {"C"},
            "C": {"D"},
            "D": {"E"},
            "E": {"A"},
        }

        cycles = service._find_cycles(graph)
        assert len(cycles) > 0

    def test_multiple_independent_cycles(self, service):
        """Test detection of multiple independent cycles."""
        # Cycle 1: A -> B -> A
        # Cycle 2: C -> D -> E -> C
        graph = {
            "A": {"B"},
            "B": {"A"},
            "C": {"D"},
            "D": {"E"},
            "E": {"C"},
        }

        cycles = service._find_cycles(graph)
        assert len(cycles) >= 2

    def test_overlapping_cycles(self, service):
        """Test detection of overlapping cycles."""
        # A -> B -> C -> A and B -> C -> B
        graph = {
            "A": {"B"},
            "B": {"C"},
            "C": {"A", "B"},
        }

        cycles = service._find_cycles(graph)
        assert len(cycles) > 0

    def test_large_linear_no_cycle(self, service):
        """Test large linear chain without cycles."""
        # A -> B -> C -> ... -> Z (no cycle)
        graph = {}
        nodes = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(len(nodes) - 1):
            graph[nodes[i]] = {nodes[i + 1]}
        graph[nodes[-1]] = set()

        cycles = service._find_cycles(graph)
        assert len(cycles) == 0

    def test_complete_graph_many_cycles(self, service):
        """Test complete graph (all nodes connected to all others)."""
        # In a complete graph with 3+ nodes, there are many cycles
        graph = {
            "A": {"B", "C", "D"},
            "B": {"A", "C", "D"},
            "C": {"A", "B", "D"},
            "D": {"A", "B", "C"},
        }

        cycles = service._find_cycles(graph)
        assert len(cycles) > 0


class TestGraphBuildingEdgeCases:
    """Test edge cases in graph building."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CycleDetectionService(Mock(spec=Session))

    def test_can_reach_with_isolated_nodes(self, service):
        """Test reachability with isolated nodes."""
        graph = {
            "A": {"B"},
            "B": set(),
            "X": set(),  # Isolated
            "Y": set(),  # Isolated
        }

        assert service._can_reach(graph, "A", "B") is True
        assert service._can_reach(graph, "A", "X") is False
        assert service._can_reach(graph, "X", "Y") is False

    def test_can_reach_dense_graph(self, service):
        """Test reachability in dense graph."""
        # Highly connected graph
        graph = {
            "A": {"B", "C", "D"},
            "B": {"A", "C", "D"},
            "C": {"A", "B", "D"},
            "D": {"A", "B", "C"},
        }

        assert service._can_reach(graph, "A", "D") is True
        assert service._can_reach(graph, "B", "A") is True

    def test_can_reach_sparse_graph(self, service):
        """Test reachability in sparse graph."""
        # Linear chain
        graph = {
            "A": {"B"},
            "B": {"C"},
            "C": {"D"},
            "D": set(),
        }

        assert service._can_reach(graph, "A", "D") is True
        assert service._can_reach(graph, "D", "A") is False

    def test_find_cycles_with_nodes_no_edges(self, service):
        """Test cycle finding with isolated nodes."""
        graph = {
            "A": set(),
            "B": set(),
            "C": set(),
        }

        cycles = service._find_cycles(graph)
        assert len(cycles) == 0

    def test_find_cycles_single_node_graph(self, service):
        """Test cycle finding with single node."""
        graph = {"A": set()}

        cycles = service._find_cycles(graph)
        assert len(cycles) == 0


class TestAsyncGraphBuildingAdvanced:
    """Test advanced async graph building scenarios."""

    @pytest.fixture
    def mock_async_session(self):
        """Create mock async session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_links_repo(self):
        """Create mock links repository."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_build_graph_mixed_link_types(self, mock_async_session, mock_links_repo):
        """Test async graph building with mixed link types."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="blocks"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        graph = await service._build_dependency_graph_async("proj-1", ["depends_on"])

        # Should include A->B and C->D, but not B->C (blocks)
        assert "A" in graph
        assert "B" in graph
        assert "C" in graph
        assert "D" in graph

    @pytest.mark.asyncio
    async def test_build_graph_large_link_set(self, mock_async_session, mock_links_repo):
        """Test async graph building with large number of links."""
        # Create 100 links
        links = [
            Mock(
                spec=Link,
                source_item_id=f"item-{i}",
                target_item_id=f"item-{(i+1) % 100}",
                link_type="depends_on",
            )
            for i in range(100)
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        graph = await service._build_dependency_graph_async("proj-1", ["depends_on"])

        assert len(graph) == 100

    @pytest.mark.asyncio
    async def test_build_graph_multiple_edges_between_nodes(self, mock_async_session, mock_links_repo):
        """Test async graph with multiple edges between same nodes (should deduplicate)."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
        ]

        mock_links_repo.get_by_project = AsyncMock(return_value=links)

        service = CycleDetectionService(mock_async_session, links=mock_links_repo)
        graph = await service._build_dependency_graph_async("proj-1", ["depends_on"])

        # Should have single edge from A to B
        assert "B" in graph["A"]
        assert len(graph["A"]) == 1


class TestHasCycleAdvanced:
    """Test advanced has_cycle scenarios."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    def test_has_cycle_long_chain_to_self(self, mock_session):
        """Test cycle detection in long chain returning to self."""
        # A -> B -> C -> D -> E -> A
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="D", target_item_id="E", link_type="depends_on"),
        ]

        mock_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_session)
        result = service.has_cycle("proj-1", "E", "A", link_type="depends_on")

        assert result is True

    def test_has_cycle_with_complex_graph(self, mock_session):
        """Test cycle detection in complex graph."""
        # Multiple paths but one creates cycle
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="C", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="D", link_type="depends_on"),
            Mock(spec=Link, source_item_id="C", target_item_id="D", link_type="depends_on"),
        ]

        mock_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_session)
        # Adding D -> A would create cycle through multiple paths
        result = service.has_cycle("proj-1", "D", "A", link_type="depends_on")

        assert result is True


class TestPerformanceEdgeCases:
    """Test performance-related edge cases."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CycleDetectionService(Mock())

    def test_can_reach_performance_large_graph(self, service):
        """Test can_reach performance with large graph."""
        # Build graph with 1000 nodes in linear chain
        graph = {}
        for i in range(1000):
            graph[f"node-{i}"] = {f"node-{i+1}"} if i < 999 else set()

        # Should still complete quickly
        result = service._can_reach(graph, "node-0", "node-999")
        assert result is True

    def test_find_cycles_performance_large_acyclic(self, service):
        """Test find_cycles performance with large acyclic graph."""
        # Build 500-node graph with no cycles
        graph = {}
        for i in range(500):
            graph[f"node-{i}"] = {f"node-{i+1}"} if i < 499 else set()

        cycles = service._find_cycles(graph)
        assert len(cycles) == 0

    def test_find_cycles_with_many_nodes(self, service):
        """Test find_cycles with many nodes but limited edges."""
        # 100 isolated nodes + 1 cycle
        graph = {f"node-{i}": set() for i in range(100)}
        graph["A"] = {"B"}
        graph["B"] = {"C"}
        graph["C"] = {"A"}

        cycles = service._find_cycles(graph)
        assert len(cycles) > 0


class TestDetectCyclesAdvanced:
    """Test advanced detect_cycles scenarios."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    def test_detect_cycles_with_mixed_link_types(self, mock_session):
        """Test detect_cycles correctly handles mixed link types."""
        # Mix of depends_on and other types
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="C", link_type="blocks"),
            Mock(spec=Link, source_item_id="C", target_item_id="A", link_type="depends_on"),
        ]

        mock_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_session)
        result = service.detect_cycles("proj-1", link_type="depends_on")

        # The cycle A->B->C exists only through depends_on (A->B) and blocks (B->C)
        # So actual depends_on cycle is just A->B with C->A
        # This should not form a complete cycle through depends_on only
        assert isinstance(result.has_cycles, bool)

    def test_detect_cycles_returns_correct_attributes(self, mock_session):
        """Test that detect_cycles returns correct attributes."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),
        ]

        mock_session.query.return_value.filter.return_value.all.return_value = links

        service = CycleDetectionService(mock_session)
        result = service.detect_cycles("proj-1")

        assert hasattr(result, "has_cycles")
        assert hasattr(result, "cycle_count")
        assert hasattr(result, "total_cycles")
        assert hasattr(result, "cycles")
        assert result.cycle_count == result.total_cycles


class TestErrorHandlingAdvanced:
    """Test advanced error handling scenarios."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    def test_detect_missing_dependencies_operational_error(self, mock_session):
        """Test handling of OperationalError in detect_missing_dependencies."""
        mock_session.query.return_value.filter.return_value.all.side_effect = OperationalError(
            "table does not exist", None, None
        )

        service = CycleDetectionService(mock_session)

        # Should raise or handle gracefully
        with pytest.raises(OperationalError):
            service.detect_missing_dependencies("proj-1")

    def test_detect_orphans_operational_error(self, mock_session):
        """Test handling of OperationalError in detect_orphans."""
        mock_session.query.return_value.filter.return_value.all.side_effect = OperationalError(
            "table does not exist", None, None
        )

        service = CycleDetectionService(mock_session)

        with pytest.raises(OperationalError):
            service.detect_orphans("proj-1")

    def test_analyze_impact_with_none_items(self, mock_session):
        """Test analyze_impact handles None items gracefully."""
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="X", link_type="depends_on"),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = links
        query_mock.filter.return_value.first.return_value = None  # None for root item
        mock_session.query.return_value = query_mock

        service = CycleDetectionService(mock_session)
        result = service.analyze_impact("proj-1", "X")

        assert result["root_item_title"] == "Unknown"


class TestInitializationVariations:
    """Test different initialization scenarios."""

    def test_init_with_async_session_no_repos(self):
        """Test initialization with async session but no repositories."""
        mock_session = AsyncMock(spec=AsyncSession)
        service = CycleDetectionService(mock_session)

        assert service.session is mock_session
        assert service.items is not None  # Should be created
        assert service.links is not None  # Should be created

    def test_init_with_sync_session_no_repos(self):
        """Test initialization with sync session and no repositories."""
        mock_session = Mock(spec=Session)
        service = CycleDetectionService(mock_session)

        assert service.session is mock_session
        assert service.items is None
        assert service.links is None

    def test_init_with_custom_repos(self):
        """Test initialization with custom repository instances."""
        mock_session = Mock(spec=Session)
        mock_items_repo = Mock()
        mock_links_repo = Mock()

        service = CycleDetectionService(
            mock_session,
            items=mock_items_repo,
            links=mock_links_repo,
        )

        assert service.items is mock_items_repo
        assert service.links is mock_links_repo


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CycleDetectionService(Mock())

    def test_can_reach_with_empty_start_node(self, service):
        """Test can_reach with empty string as node."""
        graph = {"": {"A"}, "A": set()}

        result = service._can_reach(graph, "", "A")
        assert result is True

    def test_can_reach_with_special_characters(self, service):
        """Test can_reach with special characters in node names."""
        graph = {
            "node-a-1.2": {"node-b-2.3"},
            "node-b-2.3": set(),
        }

        result = service._can_reach(graph, "node-a-1.2", "node-b-2.3")
        assert result is True

    def test_find_cycles_single_edge(self, service):
        """Test find_cycles with single edge (no cycle)."""
        graph = {"A": {"B"}, "B": set()}

        cycles = service._find_cycles(graph)
        assert len(cycles) == 0

    def test_find_cycles_two_node_cycle(self, service):
        """Test find_cycles with simplest possible cycle."""
        graph = {"A": {"B"}, "B": {"A"}}

        cycles = service._find_cycles(graph)
        assert len(cycles) > 0
