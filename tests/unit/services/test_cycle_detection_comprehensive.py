"""
Comprehensive tests for CycleDetectionService.

Coverage target: 85%+
Tests all methods: has_cycle, detect_cycles, detect_cycles_async,
detect_missing_dependencies, detect_orphans, analyze_impact.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from sqlalchemy.exc import OperationalError

from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.models.item import Item
from tracertm.models.link import Link


class TestCycleDetectionServiceInit:
    """Test CycleDetectionService initialization."""

    def test_init_with_sync_session(self):
        """Test initialization with sync session."""
        session = Mock()
        service = CycleDetectionService(session)

        assert service.session == session
        assert service.items is None
        assert service.links is None

    def test_init_with_sync_session_and_repos(self):
        """Test initialization with sync session and repositories."""
        session = Mock()
        items_repo = Mock()
        links_repo = Mock()

        service = CycleDetectionService(session, items=items_repo, links=links_repo)

        assert service.items == items_repo
        assert service.links == links_repo


class TestHasCycle:
    """Test has_cycle method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        return CycleDetectionService(session)

    def test_has_cycle_non_depends_on_returns_false(self, service):
        """Test that non-depends_on link types always return False."""
        result = service.has_cycle(
            project_id="proj1",
            source_id="item1",
            target_id="item2",
            link_type="references"
        )

        assert result is False

    def test_has_cycle_no_cycle_empty_graph(self, service):
        """Test no cycle in empty graph."""
        # Mock empty query result
        service.session.query.return_value.filter.return_value.all.return_value = []

        result = service.has_cycle(
            project_id="proj1",
            source_id="item1",
            target_id="item2"
        )

        assert result is False

    def test_has_cycle_self_loop(self, service):
        """Test self-referencing creates cycle."""
        # Same source and target
        service.session.query.return_value.filter.return_value.all.return_value = []

        # _can_reach with start == target returns True
        result = service.has_cycle(
            project_id="proj1",
            source_id="item1",
            target_id="item1"  # Same as source
        )

        assert result is True

    def test_has_cycle_existing_path(self, service):
        """Test cycle detection when path exists from target to source."""
        # Create mock links: item1 -> item2 -> item3
        link1 = Mock()
        link1.source_item_id = "item1"
        link1.target_item_id = "item2"

        link2 = Mock()
        link2.source_item_id = "item2"
        link2.target_item_id = "item3"

        service.session.query.return_value.filter.return_value.all.return_value = [link1, link2]

        # Adding item3 -> item1 would create a cycle
        result = service.has_cycle(
            project_id="proj1",
            source_id="item3",
            target_id="item1"
        )

        # item1 can reach item3 through the existing path
        assert result is True

    def test_has_cycle_no_path(self, service):
        """Test no cycle when no path exists from target to source."""
        # Create mock link: item1 -> item2
        link1 = Mock()
        link1.source_item_id = "item1"
        link1.target_item_id = "item2"

        service.session.query.return_value.filter.return_value.all.return_value = [link1]

        # Adding item2 -> item3 wouldn't create a cycle
        result = service.has_cycle(
            project_id="proj1",
            source_id="item2",
            target_id="item3"
        )

        assert result is False


class TestDetectCycles:
    """Test detect_cycles method (sync version)."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        return CycleDetectionService(session)

    def test_detect_cycles_empty_graph(self, service):
        """Test cycle detection in empty graph."""
        service.session.query.return_value.filter.return_value.all.return_value = []

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False
        assert result.cycle_count == 0
        assert result.cycles == []

    def test_detect_cycles_no_cycles(self, service):
        """Test detection when no cycles exist."""
        # Linear chain: item1 -> item2 -> item3
        link1 = Mock(source_item_id="item1", target_item_id="item2")
        link2 = Mock(source_item_id="item2", target_item_id="item3")

        service.session.query.return_value.filter.return_value.all.return_value = [link1, link2]

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False
        assert result.cycle_count == 0

    def test_detect_cycles_simple_cycle(self, service):
        """Test detection of simple cycle."""
        # Cycle: item1 -> item2 -> item1
        link1 = Mock(source_item_id="item1", target_item_id="item2")
        link2 = Mock(source_item_id="item2", target_item_id="item1")

        service.session.query.return_value.filter.return_value.all.return_value = [link1, link2]

        result = service.detect_cycles("proj1")

        assert result.has_cycles is True
        assert result.cycle_count >= 1

    def test_detect_cycles_with_link_types(self, service):
        """Test detection with specific link types list."""
        link1 = Mock(source_item_id="item1", target_item_id="item2", link_type="depends_on")

        service.session.query.return_value.filter.return_value.all.return_value = [link1]

        result = service.detect_cycles("proj1", link_types=["depends_on", "requires"])

        assert result.has_cycles is False

    def test_detect_cycles_operational_error(self, service):
        """Test handling of OperationalError (table doesn't exist)."""
        service.session.query.return_value.filter.return_value.all.side_effect = OperationalError("", "", "")

        result = service.detect_cycles("proj1")

        assert result.has_cycles is False
        assert result.cycle_count == 0


class TestDetectCyclesAsync:
    """Test detect_cycles_async method."""

    @pytest.fixture
    def async_service(self):
        """Create service with async mock session and repositories."""
        # Create a class that looks like AsyncSession
        from sqlalchemy.ext.asyncio import AsyncSession
        session = AsyncMock(spec=AsyncSession)

        links_repo = AsyncMock()
        items_repo = AsyncMock()

        service = CycleDetectionService(session, items=items_repo, links=links_repo)
        return service

    @pytest.mark.asyncio
    async def test_detect_cycles_async_no_cycles(self, async_service):
        """Test async cycle detection with no cycles."""
        # Mock repository to return empty list
        async_service.links.get_by_project = AsyncMock(return_value=[])

        result = await async_service.detect_cycles_async("proj1")

        assert result.has_cycles is False
        assert result.cycle_count == 0

    @pytest.mark.asyncio
    async def test_detect_cycles_async_with_cycle(self, async_service):
        """Test async cycle detection with a cycle."""
        # Create mock links forming a cycle
        link1 = Mock(source_item_id="a", target_item_id="b", link_type="depends_on")
        link2 = Mock(source_item_id="b", target_item_id="a", link_type="depends_on")

        async_service.links.get_by_project = AsyncMock(return_value=[link1, link2])

        result = await async_service.detect_cycles_async("proj1")

        assert result.has_cycles is True
        assert result.cycle_count >= 1

    @pytest.mark.asyncio
    async def test_detect_cycles_async_filters_by_link_type(self, async_service):
        """Test async detection filters by specified link types."""
        # Create links of different types
        link1 = Mock(source_item_id="a", target_item_id="b", link_type="depends_on")
        link2 = Mock(source_item_id="b", target_item_id="a", link_type="references")  # Different type

        async_service.links.get_by_project = AsyncMock(return_value=[link1, link2])

        # Only check depends_on
        result = await async_service.detect_cycles_async("proj1", link_types=["depends_on"])

        # Should not detect cycle since only one depends_on link
        assert result.has_cycles is False


class TestBuildDependencyGraph:
    """Test _build_dependency_graph method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        return CycleDetectionService(session)

    def test_build_graph_from_links(self, service):
        """Test graph building from links."""
        link1 = Mock(source_item_id="a", target_item_id="b")
        link2 = Mock(source_item_id="b", target_item_id="c")
        link3 = Mock(source_item_id="a", target_item_id="c")

        service.session.query.return_value.filter.return_value.all.return_value = [link1, link2, link3]

        graph = service._build_dependency_graph("proj1", "depends_on")

        assert "a" in graph
        assert "b" in graph["a"]
        assert "c" in graph["a"]
        assert "c" in graph["b"]

    def test_build_graph_includes_targets_without_outgoing(self, service):
        """Test that target nodes are included even with no outgoing edges."""
        link1 = Mock(source_item_id="a", target_item_id="b")

        service.session.query.return_value.filter.return_value.all.return_value = [link1]

        graph = service._build_dependency_graph("proj1", "depends_on")

        assert "b" in graph
        assert len(graph["b"]) == 0  # No outgoing edges


class TestCanReach:
    """Test _can_reach method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        return CycleDetectionService(Mock())

    def test_can_reach_self(self, service):
        """Test that a node can reach itself."""
        graph = {}
        result = service._can_reach(graph, "a", "a")

        assert result is True

    def test_can_reach_direct_edge(self, service):
        """Test reaching via direct edge."""
        graph = {"a": {"b"}}
        result = service._can_reach(graph, "a", "b")

        assert result is True

    def test_can_reach_transitive(self, service):
        """Test reaching via transitive path."""
        graph = {"a": {"b"}, "b": {"c"}, "c": set()}
        result = service._can_reach(graph, "a", "c")

        assert result is True

    def test_cannot_reach_no_path(self, service):
        """Test when no path exists."""
        graph = {"a": {"b"}, "b": set(), "c": set()}
        result = service._can_reach(graph, "a", "c")

        assert result is False

    def test_can_reach_handles_cycles(self, service):
        """Test DFS handles cycles in graph without infinite loop."""
        graph = {"a": {"b"}, "b": {"a"}}  # Cycle
        result = service._can_reach(graph, "a", "c")  # c doesn't exist

        assert result is False


class TestFindCycles:
    """Test _find_cycles method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        return CycleDetectionService(Mock())

    def test_find_no_cycles_in_dag(self, service):
        """Test no cycles found in directed acyclic graph."""
        graph = {"a": {"b"}, "b": {"c"}, "c": set()}
        cycles = service._find_cycles(graph)

        assert len(cycles) == 0

    def test_find_simple_cycle(self, service):
        """Test finding simple 2-node cycle."""
        graph = {"a": {"b"}, "b": {"a"}}
        cycles = service._find_cycles(graph)

        assert len(cycles) >= 1

    def test_find_self_loop(self, service):
        """Test finding self-referencing node."""
        graph = {"a": {"a"}}
        cycles = service._find_cycles(graph)

        assert len(cycles) >= 1

    def test_find_complex_cycle(self, service):
        """Test finding cycle in larger graph."""
        graph = {"a": {"b"}, "b": {"c"}, "c": {"d"}, "d": {"b"}}  # b->c->d->b cycle
        cycles = service._find_cycles(graph)

        assert len(cycles) >= 1


class TestDetectMissingDependencies:
    """Test detect_missing_dependencies method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        return CycleDetectionService(session)

    def test_no_missing_dependencies(self, service):
        """Test when all links point to existing items."""
        link = Mock(id="link1", source_item_id="item1", target_item_id="item2")
        item1 = Mock()
        item1.id = "item1"
        item2 = Mock()
        item2.id = "item2"

        # Mock link query
        service.session.query.return_value.filter.return_value.all.side_effect = [
            [link],  # Links query
            [item1, item2],  # Items query
        ]

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is False
        assert result["missing_count"] == 0

    def test_source_item_missing(self, service):
        """Test detection of missing source item."""
        link = Mock(id="link1", source_item_id="missing", target_item_id="item2")
        item2 = Mock()
        item2.id = "item2"

        service.session.query.return_value.filter.return_value.all.side_effect = [
            [link],
            [item2],  # Only item2 exists
        ]

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is True
        assert result["missing_count"] == 1
        assert result["missing_dependencies"][0]["issue"] == "source_item_missing"

    def test_target_item_missing(self, service):
        """Test detection of missing target item."""
        link = Mock(id="link1", source_item_id="item1", target_item_id="missing")
        item1 = Mock()
        item1.id = "item1"

        service.session.query.return_value.filter.return_value.all.side_effect = [
            [link],
            [item1],  # Only item1 exists
        ]

        result = service.detect_missing_dependencies("proj1")

        assert result["has_missing_dependencies"] is True
        assert result["missing_count"] == 1
        assert result["missing_dependencies"][0]["issue"] == "target_item_missing"

    def test_both_items_missing(self, service):
        """Test when both source and target are missing."""
        link = Mock(id="link1", source_item_id="missing1", target_item_id="missing2")

        service.session.query.return_value.filter.return_value.all.side_effect = [
            [link],
            [],  # No items exist
        ]

        result = service.detect_missing_dependencies("proj1")

        assert result["missing_count"] == 2


class TestDetectOrphans:
    """Test detect_orphans method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        return CycleDetectionService(session)

    def test_no_orphans(self, service):
        """Test when all items have links."""
        item1 = Mock(id="item1", title="Item 1", view="REQ", item_type="requirement", status="todo")
        link = Mock(source_item_id="item1", target_item_id="item2")

        # Mock items query first, then links query
        service.session.query.return_value.filter.return_value.all.side_effect = [
            [item1],  # Items
            [link],   # Links
        ]

        result = service.detect_orphans("proj1")

        assert result["has_orphans"] is False
        assert result["orphan_count"] == 0

    def test_orphan_detection(self, service):
        """Test detection of orphaned items."""
        item1 = Mock(id="item1", title="Item 1", view="REQ", item_type="requirement", status="todo")
        item2 = Mock(id="item2", title="Item 2", view="REQ", item_type="requirement", status="todo")
        link = Mock(source_item_id="item1", target_item_id="item3")  # item3, not item2

        service.session.query.return_value.filter.return_value.all.side_effect = [
            [item1, item2],  # Items
            [link],          # Links
        ]

        result = service.detect_orphans("proj1")

        assert result["has_orphans"] is True
        assert result["orphan_count"] == 1
        assert result["orphans"][0]["item_id"] == "item2"

    def test_detect_orphans_with_link_type_filter(self, service):
        """Test orphan detection with specific link type filter."""
        item1 = Mock(id="item1", title="Item 1", view="REQ", item_type="requirement", status="todo")

        # Query chain for items
        items_query = Mock()
        items_query.all.return_value = [item1]

        # Query chain for links (with additional filter for link_type)
        links_query = Mock()
        links_query.filter.return_value = links_query
        links_query.all.return_value = []

        # Setup mock to return different results based on query type
        def query_side_effect(model):
            result = Mock()
            if model == Item:
                result.filter.return_value = items_query
            else:
                result.filter.return_value = links_query
            return result

        service.session.query.side_effect = query_side_effect

        result = service.detect_orphans("proj1", link_type="depends_on")

        assert result["has_orphans"] is True


class TestAnalyzeImpact:
    """Test analyze_impact method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        return CycleDetectionService(session)

    def test_analyze_impact_no_dependents(self, service):
        """Test impact analysis with no dependent items."""
        root_item = Mock(id="root", title="Root Item", view="REQ", item_type="requirement", status="todo")

        # Empty link list
        service.session.query.return_value.filter.return_value.all.return_value = []
        service.session.query.return_value.filter.return_value.first.return_value = root_item

        result = service.analyze_impact("proj1", "root")

        assert result["root_item_id"] == "root"
        assert result["root_item_title"] == "Root Item"
        assert result["total_affected"] == 0

    def test_analyze_impact_with_dependents(self, service):
        """Test impact analysis with dependent items."""
        # Create links: root <- dependent (dependent depends on root)
        link = Mock(source_item_id="dependent", target_item_id="root")

        root_item = Mock(id="root", title="Root", view="REQ", item_type="requirement", status="todo")
        dependent_item = Mock(id="dependent", title="Dependent", view="REQ", item_type="requirement", status="todo")

        # Setup query mocks
        def filter_side_effect(*args, **kwargs):
            filter_mock = Mock()
            # Different behavior based on filter arguments
            filter_mock.all.return_value = [link]
            filter_mock.first.side_effect = lambda: root_item if "root" in str(args) else dependent_item
            return filter_mock

        service.session.query.return_value.filter.side_effect = filter_side_effect

        result = service.analyze_impact("proj1", "root")

        assert result["root_item_id"] == "root"

    def test_analyze_impact_max_depth(self, service):
        """Test that max_depth limits traversal."""
        # Empty graph for simplicity
        service.session.query.return_value.filter.return_value.all.return_value = []
        service.session.query.return_value.filter.return_value.first.return_value = None

        result = service.analyze_impact("proj1", "root", max_depth=2)

        assert result["total_affected"] == 0
        assert result["max_depth_reached"] == 0

    def test_analyze_impact_root_not_found(self, service):
        """Test impact analysis when root item doesn't exist."""
        service.session.query.return_value.filter.return_value.all.return_value = []
        service.session.query.return_value.filter.return_value.first.return_value = None

        result = service.analyze_impact("proj1", "nonexistent")

        assert result["root_item_title"] == "Unknown"
        assert result["total_affected"] == 0


class TestBuildDependencyGraphAsync:
    """Test _build_dependency_graph_async method."""

    @pytest.fixture
    def async_service(self):
        """Create service with async repositories."""
        from sqlalchemy.ext.asyncio import AsyncSession
        session = AsyncMock(spec=AsyncSession)

        links_repo = AsyncMock()
        items_repo = AsyncMock()

        return CycleDetectionService(session, items=items_repo, links=links_repo)

    @pytest.mark.asyncio
    async def test_async_graph_filters_link_types(self, async_service):
        """Test async graph building filters by link types."""
        link1 = Mock(source_item_id="a", target_item_id="b", link_type="depends_on")
        link2 = Mock(source_item_id="c", target_item_id="d", link_type="references")

        async_service.links.get_by_project = AsyncMock(return_value=[link1, link2])

        graph = await async_service._build_dependency_graph_async("proj1", ["depends_on"])

        assert "a" in graph
        assert "b" in graph["a"]
        assert "c" not in graph  # references link not included

    @pytest.mark.asyncio
    async def test_async_graph_handles_empty_result(self, async_service):
        """Test async graph handles empty link list."""
        async_service.links.get_by_project = AsyncMock(return_value=[])

        graph = await async_service._build_dependency_graph_async("proj1", ["depends_on"])

        assert graph == {}
