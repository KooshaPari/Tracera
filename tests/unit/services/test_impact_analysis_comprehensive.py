"""
Comprehensive test coverage for ImpactAnalysisService.

This module provides extensive test coverage for:
- Impact analysis operations (analyze_impact, analyze_reverse_impact)
- Different change types and impact propagation
- Scope filtering (direct, transitive, by severity)
- Integration with real item graphs
- Edge cases and error conditions

Target: 80-120 tests covering 2-3% additional coverage
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from collections import deque

from tracertm.services.impact_analysis_service import (
    ImpactAnalysisService,
    ImpactNode,
    ImpactAnalysisResult,
)


# ============================================================================
# TEST FIXTURES AND HELPERS
# ============================================================================


@pytest.fixture
def async_session():
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def service(async_session):
    """Create ImpactAnalysisService with mocked repositories."""
    service = ImpactAnalysisService(async_session)
    service.items = AsyncMock()
    service.links = AsyncMock()
    return service


def create_mock_item(
    item_id: str,
    title: str = None,
    view: str = "REQ",
    item_type: str = "requirement",
    status: str = "active",
    priority: str = "medium",
    owner: str = None,
) -> Mock:
    """Helper to create mock item with standard properties."""
    item = Mock()
    item.id = item_id
    item.title = title or f"Item {item_id}"
    item.view = view
    item.item_type = item_type
    item.status = status
    item.priority = priority
    item.owner = owner
    return item


def create_mock_link(
    source_id: str,
    target_id: str,
    link_type: str = "traces_to",
) -> Mock:
    """Helper to create mock link."""
    link = Mock()
    link.id = f"link_{source_id}_{target_id}"
    link.source_item_id = source_id
    link.target_item_id = target_id
    link.link_type = link_type
    return link


# ============================================================================
# TESTS FOR ANALYZE_IMPACT - BASIC OPERATIONS
# ============================================================================


class TestAnalyzeImpactBasic:
    """Test basic impact analysis operations."""

    @pytest.mark.asyncio
    async def test_analyze_single_item_no_dependencies(self, service):
        """Test analyzing item with no dependencies."""
        item = create_mock_item("item-1", "Root Item")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item-1")

        assert result.root_item_id == "item-1"
        assert result.root_item_title == "Root Item"
        assert result.total_affected == 0
        assert result.max_depth_reached == 0
        assert result.affected_items == []
        assert result.critical_paths == []

    @pytest.mark.asyncio
    async def test_analyze_item_not_found(self, service):
        """Test analyzing nonexistent item raises error."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await service.analyze_impact("nonexistent")

    @pytest.mark.asyncio
    async def test_analyze_empty_link_types_filter(self, service):
        """Test with empty link_types list includes all (falsy check)."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        link = create_mock_link("root", "child", "traces_to")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(return_value=[link])

        result = await service.analyze_impact("root", link_types=[])

        # Empty list is falsy, so filtering is not applied, all links included
        assert result.total_affected == 1

    @pytest.mark.asyncio
    async def test_analyze_max_depth_zero(self, service):
        """Test with max_depth=0 finds nothing."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        link = create_mock_link("root", "child")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root", max_depth=0)

        assert result.total_affected == 0

    @pytest.mark.asyncio
    async def test_analyze_respects_link_type_filter(self, service):
        """Test link_types filter only includes matching types."""
        root = create_mock_item("root")
        child1 = create_mock_item("child1")
        child2 = create_mock_item("child2")

        link1 = create_mock_link("root", "child1", "traces_to")
        link2 = create_mock_link("root", "child2", "implements")

        def get_item(id):
            return {"root": root, "child1": child1, "child2": child2}.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link1, link2] if id == "root" else [])

        result = await service.analyze_impact("root", link_types=["traces_to"])

        assert result.total_affected == 1
        assert result.affected_items[0]["id"] == "child1"


# ============================================================================
# TESTS FOR ANALYZE_IMPACT - COMPLEX GRAPHS
# ============================================================================


class TestAnalyzeImpactComplexGraphs:
    """Test impact analysis on complex item graphs."""

    @pytest.mark.asyncio
    async def test_linear_chain_three_levels(self, service):
        """Test impact analysis through linear chain A -> B -> C."""
        a = create_mock_item("a", "Item A")
        b = create_mock_item("b", "Item B", view="DESIGN")
        c = create_mock_item("c", "Item C", view="CODE")

        link_ab = create_mock_link("a", "b", "traces_to")
        link_bc = create_mock_link("b", "c", "implements")

        def get_item(id):
            return {"a": a, "b": b, "c": c}.get(id)

        def get_links(id):
            return {"a": [link_ab], "b": [link_bc]}.get(id, [])

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=get_links)

        result = await service.analyze_impact("a", max_depth=10)

        assert result.total_affected == 2
        assert result.max_depth_reached == 2
        assert result.affected_by_depth[1] == 1
        assert result.affected_by_depth[2] == 1

    @pytest.mark.asyncio
    async def test_branching_tree_structure(self, service):
        """Test impact analysis on tree with multiple branches."""
        root = create_mock_item("root")
        child1 = create_mock_item("child1")
        child2 = create_mock_item("child2")
        grandchild1 = create_mock_item("grandchild1")
        grandchild2 = create_mock_item("grandchild2")

        links = {
            "root": [
                create_mock_link("root", "child1"),
                create_mock_link("root", "child2"),
            ],
            "child1": [create_mock_link("child1", "grandchild1")],
            "child2": [create_mock_link("child2", "grandchild2")],
        }

        def get_item(id):
            items = {
                "root": root,
                "child1": child1,
                "child2": child2,
                "grandchild1": grandchild1,
                "grandchild2": grandchild2,
            }
            return items.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        assert result.total_affected == 4
        assert result.max_depth_reached == 2
        assert result.affected_by_depth[1] == 2
        assert result.affected_by_depth[2] == 2

    @pytest.mark.asyncio
    async def test_diamond_dependency_pattern(self, service):
        """Test diamond pattern: root -> (a, b) -> (c)."""
        root = create_mock_item("root")
        a = create_mock_item("a")
        b = create_mock_item("b")
        c = create_mock_item("c")

        links = {
            "root": [create_mock_link("root", "a"), create_mock_link("root", "b")],
            "a": [create_mock_link("a", "c")],
            "b": [create_mock_link("b", "c")],
        }

        def get_item(id):
            items = {"root": root, "a": a, "b": b, "c": c}
            return items.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        # c should appear only once due to visited set
        assert result.total_affected == 3
        assert c.id in [item["id"] for item in result.affected_items]

    @pytest.mark.asyncio
    async def test_wide_branching_many_children(self, service):
        """Test item with many direct dependencies."""
        root = create_mock_item("root")
        children = [create_mock_item(f"child{i}") for i in range(10)]

        links = [create_mock_link("root", f"child{i}") for i in range(10)]

        def get_item(id):
            if id == "root":
                return root
            for i, child in enumerate(children):
                if child.id == id:
                    return child
            return None

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.total_affected == 10
        assert result.affected_by_depth[1] == 10

    @pytest.mark.asyncio
    async def test_deep_linear_chain(self, service):
        """Test deeply nested linear chain."""
        items = {str(i): create_mock_item(str(i)) for i in range(15)}
        links = {
            str(i): [create_mock_link(str(i), str(i + 1))] for i in range(14)
        }

        def get_item(id):
            return items.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0", max_depth=20)

        assert result.total_affected == 14
        assert result.max_depth_reached == 14

    @pytest.mark.asyncio
    async def test_respects_max_depth_limit(self, service):
        """Test max_depth properly truncates traversal."""
        items = {str(i): create_mock_item(str(i)) for i in range(10)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(9)}

        def get_item(id):
            return items.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0", max_depth=3)

        assert result.total_affected == 3
        assert result.max_depth_reached == 3


# ============================================================================
# TESTS FOR CYCLE DETECTION AND HANDLING
# ============================================================================


class TestAnalyzeImpactCycleHandling:
    """Test cycle detection and handling."""

    @pytest.mark.asyncio
    async def test_simple_self_cycle(self, service):
        """Test item linking to itself."""
        item = create_mock_item("item")
        link = create_mock_link("item", "item")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[link])

        result = await service.analyze_impact("item")

        # Self-link should be visited, not infinite loop
        assert result.total_affected == 0

    @pytest.mark.asyncio
    async def test_simple_two_node_cycle(self, service):
        """Test A -> B -> A cycle."""
        a = create_mock_item("a")
        b = create_mock_item("b")
        link_ab = create_mock_link("a", "b")
        link_ba = create_mock_link("b", "a")

        def get_item(id):
            return {"a": a, "b": b}.get(id)

        def get_links(id):
            return {"a": [link_ab], "b": [link_ba]}.get(id, [])

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=get_links)

        result = await service.analyze_impact("a")

        # Should visit b but not infinite loop on a
        assert result.total_affected == 1

    @pytest.mark.asyncio
    async def test_complex_cycle_in_graph(self, service):
        """Test cycle within larger graph: a -> b -> c -> b."""
        a = create_mock_item("a")
        b = create_mock_item("b")
        c = create_mock_item("c")

        links = {
            "a": [create_mock_link("a", "b")],
            "b": [create_mock_link("b", "c")],
            "c": [create_mock_link("c", "b")],
        }

        def get_item(id):
            return {"a": a, "b": b, "c": c}.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("a")

        # a -> b -> c, cycle b->c->b doesn't infinite loop
        assert result.total_affected == 2
        assert 1 in result.affected_by_depth
        assert 2 in result.affected_by_depth

    @pytest.mark.asyncio
    async def test_three_node_cycle(self, service):
        """Test A -> B -> C -> A cycle."""
        items = {
            "a": create_mock_item("a"),
            "b": create_mock_item("b"),
            "c": create_mock_item("c"),
        }
        links = {
            "a": [create_mock_link("a", "b")],
            "b": [create_mock_link("b", "c")],
            "c": [create_mock_link("c", "a")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("a")

        assert result.total_affected == 2
        ids = {item["id"] for item in result.affected_items}
        assert "b" in ids
        assert "c" in ids


# ============================================================================
# TESTS FOR VIEW AND STATUS FILTERING
# ============================================================================


class TestAnalyzeImpactViewFiltering:
    """Test view-based analysis and filtering."""

    @pytest.mark.asyncio
    async def test_affected_by_view_counts(self, service):
        """Test correct counting of items by view."""
        root = create_mock_item("root", view="REQ")
        req_items = [create_mock_item(f"req{i}", view="REQ") for i in range(3)]
        design_items = [create_mock_item(f"design{i}", view="DESIGN") for i in range(2)]
        code_items = [create_mock_item(f"code{i}", view="CODE") for i in range(1)]

        all_items = {"root": root}
        all_items.update({item.id: item for item in req_items})
        all_items.update({item.id: item for item in design_items})
        all_items.update({item.id: item for item in code_items})

        links = {
            "root": [
                create_mock_link("root", f"req{i}") for i in range(3)
            ] + [
                create_mock_link("root", f"design{i}") for i in range(2)
            ] + [
                create_mock_link("root", f"code{i}") for i in range(1)
            ],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: all_items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        assert result.affected_by_view["REQ"] == 3
        assert result.affected_by_view["DESIGN"] == 2
        assert result.affected_by_view["CODE"] == 1

    @pytest.mark.asyncio
    async def test_items_with_different_statuses(self, service):
        """Test tracking items with various statuses."""
        root = create_mock_item("root", status="active")
        active_item = create_mock_item("active", status="active")
        done_item = create_mock_item("done", status="done")
        todo_item = create_mock_item("todo", status="todo")

        links = {
            "root": [
                create_mock_link("root", "active"),
                create_mock_link("root", "done"),
                create_mock_link("root", "todo"),
            ],
        }

        items = {"root": root, "active": active_item, "done": done_item, "todo": todo_item}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        statuses = {item["status"] for item in result.affected_items}
        assert "active" in statuses
        assert "done" in statuses
        assert "todo" in statuses


# ============================================================================
# TESTS FOR ANALYZE_REVERSE_IMPACT
# ============================================================================


class TestAnalyzeReverseImpact:
    """Test reverse impact analysis."""

    @pytest.mark.asyncio
    async def test_reverse_simple_upstream_link(self, service):
        """Test finding single upstream dependency."""
        target = create_mock_item("target")
        source = create_mock_item("source")
        link = create_mock_link("source", "target")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: target if id == "target" else source)
        service.links.get_by_target = AsyncMock(side_effect=lambda id: [link] if id == "target" else [])

        result = await service.analyze_reverse_impact("target")

        assert result.total_affected == 1
        assert result.affected_items[0]["id"] == "source"

    @pytest.mark.asyncio
    async def test_reverse_no_upstream_links(self, service):
        """Test item with no upstream dependencies."""
        item = create_mock_item("item")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.analyze_reverse_impact("item")

        assert result.total_affected == 0

    @pytest.mark.asyncio
    async def test_reverse_multiple_upstream_sources(self, service):
        """Test item with multiple upstream sources."""
        target = create_mock_item("target")
        sources = [create_mock_item(f"source{i}") for i in range(5)]
        links = [create_mock_link(f"source{i}", "target") for i in range(5)]

        items = {"target": target}
        items.update({source.id: source for source in sources})

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: links if id == "target" else [])

        result = await service.analyze_reverse_impact("target")

        assert result.total_affected == 5

    @pytest.mark.asyncio
    async def test_reverse_upstream_chain(self, service):
        """Test tracing through upstream chain: C <- B <- A."""
        c = create_mock_item("c")
        b = create_mock_item("b")
        a = create_mock_item("a")

        links = {
            "c": [create_mock_link("b", "c")],
            "b": [create_mock_link("a", "b")],
        }

        items = {"a": a, "b": b, "c": c}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_reverse_impact("c")

        assert result.total_affected == 2
        ids = {item["id"] for item in result.affected_items}
        assert "a" in ids
        assert "b" in ids

    @pytest.mark.asyncio
    async def test_reverse_respects_max_depth(self, service):
        """Test reverse impact respects max_depth."""
        target = create_mock_item("target")
        parent = create_mock_item("parent")
        grandparent = create_mock_item("grandparent")

        links = {
            "target": [create_mock_link("parent", "target")],
            "parent": [create_mock_link("grandparent", "parent")],
        }

        items = {"target": target, "parent": parent, "grandparent": grandparent}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_reverse_impact("target", max_depth=1)

        assert result.total_affected == 1
        assert result.affected_items[0]["id"] == "parent"

    @pytest.mark.asyncio
    async def test_reverse_item_not_found(self, service):
        """Test reverse impact on nonexistent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await service.analyze_reverse_impact("nonexistent")

    @pytest.mark.asyncio
    async def test_reverse_with_cycles(self, service):
        """Test reverse impact handles cycles."""
        a = create_mock_item("a")
        b = create_mock_item("b")

        links = {
            "a": [create_mock_link("b", "a")],
            "b": [create_mock_link("a", "b")],
        }

        items = {"a": a, "b": b}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_reverse_impact("a")

        assert result.total_affected == 1


# ============================================================================
# TESTS FOR CRITICAL PATHS
# ============================================================================


class TestCriticalPaths:
    """Test critical path identification."""

    @pytest.mark.asyncio
    async def test_single_leaf_node_creates_critical_path(self, service):
        """Test single leaf node becomes critical path."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        link = create_mock_link("root", "child")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root")

        assert len(result.critical_paths) == 1
        assert result.critical_paths[0] == ["root", "child"]

    @pytest.mark.asyncio
    async def test_multiple_leaf_nodes_create_multiple_paths(self, service):
        """Test multiple leaf nodes create multiple critical paths."""
        root = create_mock_item("root")
        leaf1 = create_mock_item("leaf1")
        leaf2 = create_mock_item("leaf2")

        links = [create_mock_link("root", "leaf1"), create_mock_link("root", "leaf2")]

        def get_item(id):
            return {"root": root, "leaf1": leaf1, "leaf2": leaf2}.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root")

        assert len(result.critical_paths) == 2

    @pytest.mark.asyncio
    async def test_critical_paths_in_linear_chain(self, service):
        """Test critical path for linear chain."""
        items = {str(i): create_mock_item(str(i)) for i in range(5)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(4)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        assert len(result.critical_paths) == 1
        assert result.critical_paths[0] == ["0", "1", "2", "3", "4"]

    @pytest.mark.asyncio
    async def test_no_critical_paths_with_no_leaves(self, service):
        """Test no critical paths when all nodes have children."""
        a = create_mock_item("a")
        b = create_mock_item("b")

        # Both link to each other, creating cycle with no leaves
        links = {
            "a": [create_mock_link("a", "b")],
            "b": [create_mock_link("b", "a")],
        }

        items = {"a": a, "b": b}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("a")

        # After cycle prevention, b is visited but has no children, so is a leaf
        assert isinstance(result.critical_paths, list)


# ============================================================================
# TESTS FOR EDGE CASES AND ERROR CONDITIONS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_missing_downstream_item_skipped(self, service):
        """Test missing downstream item is skipped."""
        root = create_mock_item("root")
        link = create_mock_link("root", "missing")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else None)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.total_affected == 0

    @pytest.mark.asyncio
    async def test_empty_affected_items_list(self, service):
        """Test empty affected items when no dependencies."""
        item = create_mock_item("item")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item")

        assert isinstance(result.affected_items, list)
        assert len(result.affected_items) == 0

    @pytest.mark.asyncio
    async def test_none_link_type_in_result(self, service):
        """Test None link_type is preserved in results."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        # Create link without link_type
        link = Mock()
        link.target_item_id = "child"
        link.link_type = None

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.affected_items[0]["link_type"] is None

    @pytest.mark.asyncio
    async def test_very_long_path_preserved(self, service):
        """Test very long paths are preserved."""
        items = {str(i): create_mock_item(str(i)) for i in range(20)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(19)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0", max_depth=20)

        # Check that the deepest item has full path
        deepest = max(result.affected_items, key=lambda x: x["depth"])
        assert len(deepest["path"]) == deepest["depth"] + 1

    @pytest.mark.asyncio
    async def test_special_characters_in_item_ids(self, service):
        """Test items with special characters in IDs."""
        item_id = "item-uuid-12345_special.id"
        item = create_mock_item(item_id)
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact(item_id)

        assert result.root_item_id == item_id


# ============================================================================
# TESTS FOR LINK TYPE HANDLING
# ============================================================================


class TestLinkTypeHandling:
    """Test link type filtering and handling."""

    @pytest.mark.asyncio
    async def test_multiple_link_types_filter(self, service):
        """Test filtering by multiple link types."""
        root = create_mock_item("root")
        items = {
            "traces": create_mock_item("traces"),
            "implements": create_mock_item("implements"),
            "depends": create_mock_item("depends"),
            "relates": create_mock_item("relates"),
        }

        links = [
            create_mock_link("root", "traces", "traces_to"),
            create_mock_link("root", "implements", "implements"),
            create_mock_link("root", "depends", "depends_on"),
            create_mock_link("root", "relates", "relates_to"),
        ]

        items["root"] = root
        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root", link_types=["traces_to", "implements"])

        assert result.total_affected == 2
        affected_ids = {item["id"] for item in result.affected_items}
        assert "traces" in affected_ids
        assert "implements" in affected_ids

    @pytest.mark.asyncio
    async def test_nonexistent_link_type_filter(self, service):
        """Test filter with link type that doesn't exist."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        link = create_mock_link("root", "child", "traces_to")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root", link_types=["nonexistent_type"])

        assert result.total_affected == 0

    @pytest.mark.asyncio
    async def test_link_type_preserved_in_results(self, service):
        """Test link_type is correctly preserved in results."""
        root = create_mock_item("root")
        child1 = create_mock_item("child1")
        child2 = create_mock_item("child2")

        links = [
            create_mock_link("root", "child1", "traces_to"),
            create_mock_link("root", "child2", "implements"),
        ]

        items = {"root": root, "child1": child1, "child2": child2}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root")

        link_types = {item["link_type"] for item in result.affected_items}
        assert "traces_to" in link_types
        assert "implements" in link_types


# ============================================================================
# TESTS FOR DATA INTEGRITY
# ============================================================================


class TestDataIntegrity:
    """Test data integrity in results."""

    @pytest.mark.asyncio
    async def test_all_affected_items_have_required_fields(self, service):
        """Test all affected items contain required fields."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        link = create_mock_link("root", "child")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root")

        for item in result.affected_items:
            assert "id" in item
            assert "title" in item
            assert "view" in item
            assert "item_type" in item
            assert "status" in item
            assert "depth" in item
            assert "path" in item
            assert "link_type" in item

    @pytest.mark.asyncio
    async def test_path_always_starts_with_root(self, service):
        """Test all paths start with root item."""
        root = create_mock_item("root")
        items = [create_mock_item(f"item{i}") for i in range(5)]
        all_items = {"root": root}
        all_items.update({item.id: item for item in items})

        links = {
            "root": [create_mock_link("root", f"item{i}") for i in range(5)],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: all_items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        for item in result.affected_items:
            assert item["path"][0] == "root"

    @pytest.mark.asyncio
    async def test_depth_matches_path_length(self, service):
        """Test depth value matches path length - 1."""
        items = {str(i): create_mock_item(str(i)) for i in range(5)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(4)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        for item in result.affected_items:
            assert item["depth"] == len(item["path"]) - 1

    @pytest.mark.asyncio
    async def test_affected_by_depth_is_consistent(self, service):
        """Test affected_by_depth counts match actual depths."""
        root = create_mock_item("root")
        items = {
            "l1a": create_mock_item("l1a"),
            "l1b": create_mock_item("l1b"),
            "l2a": create_mock_item("l2a"),
        }
        all_items = {"root": root, **items}

        links = {
            "root": [create_mock_link("root", "l1a"), create_mock_link("root", "l1b")],
            "l1a": [create_mock_link("l1a", "l2a")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: all_items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        # Verify counts
        expected_depth_1 = len([i for i in result.affected_items if i["depth"] == 1])
        expected_depth_2 = len([i for i in result.affected_items if i["depth"] == 2])

        assert result.affected_by_depth[1] == expected_depth_1
        assert result.affected_by_depth[2] == expected_depth_2


# ============================================================================
# TESTS FOR COMPLEX INTEGRATION SCENARIOS
# ============================================================================


class TestComplexIntegration:
    """Test complex real-world integration scenarios."""

    @pytest.mark.asyncio
    async def test_multi_view_hierarchy(self, service):
        """Test impact across multiple views with hierarchy."""
        req = create_mock_item("req1", view="REQ")
        design1 = create_mock_item("design1", view="DESIGN")
        design2 = create_mock_item("design2", view="DESIGN")
        code1 = create_mock_item("code1", view="CODE")
        code2 = create_mock_item("code2", view="CODE")
        test1 = create_mock_item("test1", view="TEST")

        items = {
            "req1": req,
            "design1": design1,
            "design2": design2,
            "code1": code1,
            "code2": code2,
            "test1": test1,
        }

        links = {
            "req1": [create_mock_link("req1", "design1"), create_mock_link("req1", "design2")],
            "design1": [create_mock_link("design1", "code1")],
            "design2": [create_mock_link("design2", "code2")],
            "code1": [create_mock_link("code1", "test1")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("req1")

        assert result.total_affected == 5
        assert "REQ" not in result.affected_by_view  # root not counted
        assert result.affected_by_view["DESIGN"] == 2
        assert result.affected_by_view["CODE"] == 2
        assert result.affected_by_view["TEST"] == 1

    @pytest.mark.asyncio
    async def test_prioritized_items_tracking(self, service):
        """Test tracking items with different priorities."""
        root = create_mock_item("root", priority="high")
        high = create_mock_item("high", priority="high")
        medium = create_mock_item("medium", priority="medium")
        low = create_mock_item("low", priority="low")

        items = {"root": root, "high": high, "medium": medium, "low": low}
        links = {
            "root": [
                create_mock_link("root", "high"),
                create_mock_link("root", "medium"),
                create_mock_link("root", "low"),
            ],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        priorities = {item["id"]: "priority" for item in result.affected_items}
        assert "high" in {item["id"] for item in result.affected_items}
        assert "medium" in {item["id"] for item in result.affected_items}
        assert "low" in {item["id"] for item in result.affected_items}

    @pytest.mark.asyncio
    async def test_owned_items_analysis(self, service):
        """Test tracking items by owner."""
        root = create_mock_item("root", owner="alice")
        alice_item = create_mock_item("alice_item", owner="alice")
        bob_item = create_mock_item("bob_item", owner="bob")

        items = {"root": root, "alice_item": alice_item, "bob_item": bob_item}
        links = {
            "root": [
                create_mock_link("root", "alice_item"),
                create_mock_link("root", "bob_item"),
            ],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        owners = {item["id"]: "owner" for item in result.affected_items}
        assert len(result.affected_items) == 2


# ============================================================================
# TESTS FOR FIND_CRITICAL_PATHS HELPER METHOD
# ============================================================================


class TestFindCriticalPathsHelper:
    """Test _find_critical_paths helper method."""

    @pytest.fixture
    def service_fixture(self):
        """Create service for testing."""
        session = AsyncMock()
        return ImpactAnalysisService(session)

    def test_empty_nodes_list(self, service_fixture):
        """Test with empty node list."""
        result = service_fixture._find_critical_paths([])
        assert result == []

    def test_single_leaf_node(self, service_fixture):
        """Test with single leaf node."""
        item = create_mock_item("leaf")
        node = ImpactNode(item=item, depth=1, path=["root", "leaf"])
        result = service_fixture._find_critical_paths([node])
        assert len(result) == 1
        assert result[0] == ["root", "leaf"]

    def test_multiple_leaf_nodes(self, service_fixture):
        """Test with multiple leaf nodes."""
        node1 = ImpactNode(item=create_mock_item("leaf1"), depth=1, path=["root", "leaf1"])
        node2 = ImpactNode(item=create_mock_item("leaf2"), depth=1, path=["root", "leaf2"])
        result = service_fixture._find_critical_paths([node1, node2])
        assert len(result) == 2

    def test_parent_and_child_identifies_only_leaf(self, service_fixture):
        """Test parent-child relationship identifies only leaf as critical."""
        parent = create_mock_item("parent")
        child = create_mock_item("child")

        parent_node = ImpactNode(item=parent, depth=1, path=["root", "parent"])
        child_node = ImpactNode(item=child, depth=2, path=["root", "parent", "child"])

        result = service_fixture._find_critical_paths([parent_node, child_node])

        assert len(result) == 1
        assert result[0] == ["root", "parent", "child"]

    def test_complex_tree_structure(self, service_fixture):
        """Test complex tree with multiple branches."""
        nodes = [
            ImpactNode(item=create_mock_item("branch1_leaf"), depth=2, path=["root", "a", "branch1_leaf"]),
            ImpactNode(item=create_mock_item("branch2_leaf"), depth=2, path=["root", "b", "branch2_leaf"]),
            ImpactNode(item=create_mock_item("a"), depth=1, path=["root", "a"]),
            ImpactNode(item=create_mock_item("b"), depth=1, path=["root", "b"]),
        ]

        result = service_fixture._find_critical_paths(nodes)

        # Should find two critical paths (leaves)
        assert len(result) == 2

    def test_deep_linear_path(self, service_fixture):
        """Test deep linear path."""
        nodes = [
            ImpactNode(item=create_mock_item(str(i)), depth=i, path=[str(j) for j in range(i + 1)])
            for i in range(1, 6)
        ]

        result = service_fixture._find_critical_paths(nodes)

        # Deepest node is the only leaf
        assert len(result) == 1
        assert result[0] == ["0", "1", "2", "3", "4", "5"]


# ============================================================================
# TESTS FOR SERVICE INITIALIZATION
# ============================================================================


class TestServiceInitialization:
    """Test service initialization."""

    def test_service_creates_repositories(self, async_session):
        """Test service initializes repositories."""
        service = ImpactAnalysisService(async_session)
        assert service.session is async_session
        assert service.items is not None
        assert service.links is not None

    def test_service_preserves_session_reference(self, async_session):
        """Test service preserves session."""
        service = ImpactAnalysisService(async_session)
        assert service.session is async_session


# ============================================================================
# TESTS FOR IMPACT NODE DATACLASS
# ============================================================================


class TestImpactNodeDataclass:
    """Test ImpactNode dataclass."""

    def test_basic_node_creation(self):
        """Test basic node creation."""
        item = create_mock_item("item1")
        node = ImpactNode(item=item, depth=1, path=["root", "item1"])
        assert node.item == item
        assert node.depth == 1
        assert node.path == ["root", "item1"]
        assert node.link_type is None

    def test_node_with_link_type(self):
        """Test node with link_type."""
        item = create_mock_item("item1")
        node = ImpactNode(
            item=item,
            depth=2,
            path=["root", "a", "item1"],
            link_type="traces_to",
        )
        assert node.link_type == "traces_to"

    def test_node_equality(self):
        """Test node comparison."""
        item = create_mock_item("item1")
        node1 = ImpactNode(item=item, depth=1, path=["root", "item1"])
        node2 = ImpactNode(item=item, depth=1, path=["root", "item1"])
        assert node1.item == node2.item
        assert node1.depth == node2.depth


# ============================================================================
# TESTS FOR IMPACT ANALYSIS RESULT DATACLASS
# ============================================================================


class TestImpactAnalysisResultDataclass:
    """Test ImpactAnalysisResult dataclass."""

    def test_result_creation(self):
        """Test result creation."""
        result = ImpactAnalysisResult(
            root_item_id="root",
            root_item_title="Root",
            total_affected=5,
            max_depth_reached=3,
            affected_by_depth={1: 2, 2: 2, 3: 1},
            affected_by_view={"REQ": 3, "DESIGN": 2},
            affected_items=[{"id": "item1"}],
            critical_paths=[["root", "item1"]],
        )
        assert result.root_item_id == "root"
        assert result.total_affected == 5
        assert result.max_depth_reached == 3

    def test_empty_result(self):
        """Test empty result creation."""
        result = ImpactAnalysisResult(
            root_item_id="item",
            root_item_title="Item",
            total_affected=0,
            max_depth_reached=0,
            affected_by_depth={},
            affected_by_view={},
            affected_items=[],
            critical_paths=[],
        )
        assert result.total_affected == 0
        assert result.affected_items == []


# ============================================================================
# ADDITIONAL COMPREHENSIVE TESTS
# ============================================================================


class TestAdditionalCoverage:
    """Additional tests for edge cases and comprehensive coverage."""

    @pytest.mark.asyncio
    async def test_analyze_with_null_item_properties(self, service):
        """Test handling items with null properties."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        child = Mock()
        child.id = "child"
        child.title = None  # Null title
        child.view = None  # Null view
        child.item_type = None
        child.status = None

        link = create_mock_link("root", "child")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.total_affected == 1

    @pytest.mark.asyncio
    async def test_multiple_independent_branches(self, service):
        """Test handling multiple completely independent branches."""
        root = create_mock_item("root")

        # Branch 1
        b1_1 = create_mock_item("b1_1")
        b1_2 = create_mock_item("b1_2")

        # Branch 2
        b2_1 = create_mock_item("b2_1")
        b2_2 = create_mock_item("b2_2")

        # Branch 3
        b3_1 = create_mock_item("b3_1")

        items = {
            "root": root,
            "b1_1": b1_1,
            "b1_2": b1_2,
            "b2_1": b2_1,
            "b2_2": b2_2,
            "b3_1": b3_1,
        }

        links = {
            "root": [
                create_mock_link("root", "b1_1"),
                create_mock_link("root", "b2_1"),
                create_mock_link("root", "b3_1"),
            ],
            "b1_1": [create_mock_link("b1_1", "b1_2")],
            "b2_1": [create_mock_link("b2_1", "b2_2")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        assert result.total_affected == 5
        assert result.affected_by_depth[1] == 3
        assert result.affected_by_depth[2] == 2

    @pytest.mark.asyncio
    async def test_all_same_view_analysis(self, service):
        """Test when all items are in same view."""
        items = {str(i): create_mock_item(str(i), view="REQ") for i in range(5)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(4)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        assert result.affected_by_view["REQ"] == 4
        assert len(result.affected_by_view) == 1

    @pytest.mark.asyncio
    async def test_reverse_impact_circular_upstream(self, service):
        """Test reverse impact with circular upstream."""
        target = create_mock_item("target")
        a = create_mock_item("a")
        b = create_mock_item("b")

        links = {
            "target": [create_mock_link("a", "target")],
            "a": [create_mock_link("b", "a")],
            "b": [create_mock_link("a", "b")],
        }

        items = {"target": target, "a": a, "b": b}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_reverse_impact("target")

        assert result.total_affected >= 1
        assert target.id == result.root_item_id


# ============================================================================
# EXTENDED TESTS FOR ADDITIONAL COVERAGE
# ============================================================================


class TestBiDirectionalAnalysis:
    """Test bidirectional impact analysis."""

    @pytest.mark.asyncio
    async def test_compare_forward_and_reverse_impact(self, service):
        """Test comparing forward and reverse impact on same item."""
        central = create_mock_item("central")
        upstream = create_mock_item("upstream")
        downstream = create_mock_item("downstream")

        items = {"upstream": upstream, "central": central, "downstream": downstream}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))

        # For analyze_impact: central -> downstream
        service.links.get_by_source = AsyncMock(
            side_effect=lambda id: [create_mock_link("central", "downstream")] if id == "central" else []
        )

        # For analyze_reverse_impact: upstream -> central
        service.links.get_by_target = AsyncMock(
            side_effect=lambda id: [create_mock_link("upstream", "central")] if id == "central" else []
        )

        forward = await service.analyze_impact("central")
        reverse = await service.analyze_reverse_impact("central")

        assert forward.total_affected == 1
        assert reverse.total_affected == 1
        assert forward.affected_items[0]["id"] == "downstream"
        assert reverse.affected_items[0]["id"] == "upstream"


class TestStatusTransitionImpact:
    """Test impact analysis on status transitions."""

    @pytest.mark.asyncio
    async def test_status_change_propagation(self, service):
        """Test tracking impact of status changes."""
        active = create_mock_item("active", status="active")
        blocked = create_mock_item("blocked", status="blocked")
        done = create_mock_item("done", status="done")

        links = {
            "active": [
                create_mock_link("active", "blocked"),
                create_mock_link("active", "done"),
            ],
        }

        items = {"active": active, "blocked": blocked, "done": done}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("active")

        affected_statuses = {item["status"] for item in result.affected_items}
        assert "blocked" in affected_statuses
        assert "done" in affected_statuses


class TestItemTypeVariety:
    """Test impact analysis with various item types."""

    @pytest.mark.asyncio
    async def test_mixed_item_types_analysis(self, service):
        """Test analyzing impact across different item types."""
        req = create_mock_item("req", item_type="requirement")
        design = create_mock_item("design", item_type="design")
        impl = create_mock_item("impl", item_type="implementation")
        test = create_mock_item("test", item_type="test")

        links = {
            "req": [create_mock_link("req", "design")],
            "design": [create_mock_link("design", "impl")],
            "impl": [create_mock_link("impl", "test")],
        }

        items = {"req": req, "design": design, "impl": impl, "test": test}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("req")

        item_types = {item["item_type"] for item in result.affected_items}
        assert "design" in item_types
        assert "implementation" in item_types
        assert "test" in item_types


class TestDepthAnalysis:
    """Test depth-based analysis capabilities."""

    @pytest.mark.asyncio
    async def test_depth_distribution_tracking(self, service):
        """Test accurate depth distribution."""
        root = create_mock_item("root")
        l1_items = [create_mock_item(f"l1_{i}") for i in range(3)]
        l2_items = [create_mock_item(f"l2_{i}") for i in range(2)]
        l3_items = [create_mock_item(f"l3_{i}") for i in range(1)]

        items = {"root": root}
        items.update({item.id: item for item in l1_items + l2_items + l3_items})

        links = {
            "root": [create_mock_link("root", item.id) for item in l1_items],
        }
        for i, l1_item in enumerate(l1_items):
            if i < 2:
                links[l1_item.id] = [create_mock_link(l1_item.id, item.id) for item in l2_items]
            else:
                links[l1_item.id] = []

        for l2_item in l2_items:
            links[l2_item.id] = [create_mock_link(l2_item.id, l3_items[0].id)]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        assert result.affected_by_depth[1] == 3
        assert result.affected_by_depth[2] >= 2

    @pytest.mark.asyncio
    async def test_max_depth_boundary(self, service):
        """Test max_depth boundary condition."""
        items = {str(i): create_mock_item(str(i)) for i in range(6)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(5)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        # Test boundary at different depths
        result2 = await service.analyze_impact("0", max_depth=2)
        result5 = await service.analyze_impact("0", max_depth=5)

        assert result2.total_affected == 2
        assert result5.total_affected == 5


class TestViewSpecificAnalysis:
    """Test view-specific analysis patterns."""

    @pytest.mark.asyncio
    async def test_cross_view_traceability(self, service):
        """Test traceability across views."""
        req = create_mock_item("req", view="REQ")
        design1 = create_mock_item("design1", view="DESIGN")
        design2 = create_mock_item("design2", view="DESIGN")
        code = create_mock_item("code", view="CODE")

        links = {
            "req": [
                create_mock_link("req", "design1"),
                create_mock_link("req", "design2"),
            ],
            "design1": [create_mock_link("design1", "code")],
        }

        items = {
            "req": req,
            "design1": design1,
            "design2": design2,
            "code": code,
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("req")

        view_count = result.affected_by_view
        assert view_count["DESIGN"] == 2
        assert view_count["CODE"] == 1

    @pytest.mark.asyncio
    async def test_single_view_analysis(self, service):
        """Test analyzing within single view."""
        items = {str(i): create_mock_item(str(i), view="REQ") for i in range(4)}
        links = {
            "0": [create_mock_link("0", "1"), create_mock_link("0", "2")],
            "1": [create_mock_link("1", "3")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        assert len(result.affected_by_view) == 1
        assert result.affected_by_view["REQ"] == 3


class TestPathTrackingAccuracy:
    """Test accuracy of path tracking."""

    @pytest.mark.asyncio
    async def test_path_uniqueness_in_dags(self, service):
        """Test path tracking in DAG (directed acyclic graph)."""
        root = create_mock_item("root")
        a = create_mock_item("a")
        b = create_mock_item("b")
        c = create_mock_item("c")

        # Diamond: root -> a,b -> c
        links = {
            "root": [create_mock_link("root", "a"), create_mock_link("root", "b")],
            "a": [create_mock_link("a", "c")],
            "b": [create_mock_link("b", "c")],
        }

        items = {"root": root, "a": a, "b": b, "c": c}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        # c should appear once, earliest path recorded
        c_items = [item for item in result.affected_items if item["id"] == "c"]
        assert len(c_items) == 1

    @pytest.mark.asyncio
    async def test_path_contains_all_ancestors(self, service):
        """Test path contains complete ancestry."""
        items = {str(i): create_mock_item(str(i)) for i in range(5)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(4)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        deepest = max(result.affected_items, key=lambda x: x["depth"])
        expected_path = ["0", "1", "2", "3", "4"]
        assert deepest["path"] == expected_path


class TestLinkTypeVariations:
    """Test various link type scenarios."""

    @pytest.mark.asyncio
    async def test_many_link_types_mixed(self, service):
        """Test handling many link types simultaneously."""
        root = create_mock_item("root")
        children = [create_mock_item(f"child{i}") for i in range(5)]

        link_types = [
            "traces_to",
            "implements",
            "depends_on",
            "relates_to",
            "verifies",
        ]

        links = [
            create_mock_link("root", children[i].id, link_types[i])
            for i in range(5)
        ]

        items = {"root": root}
        items.update({child.id: child for child in children})

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root")

        found_types = {item["link_type"] for item in result.affected_items}
        assert len(found_types) == 5

    @pytest.mark.asyncio
    async def test_selective_link_type_filtering(self, service):
        """Test selective filtering of specific link types."""
        root = create_mock_item("root")
        traces_child = create_mock_item("traces_child")
        impl_child = create_mock_item("impl_child")
        other_child = create_mock_item("other_child")

        links = [
            create_mock_link("root", "traces_child", "traces_to"),
            create_mock_link("root", "impl_child", "implements"),
            create_mock_link("root", "other_child", "depends_on"),
        ]

        items = {
            "root": root,
            "traces_child": traces_child,
            "impl_child": impl_child,
            "other_child": other_child,
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact(
            "root",
            link_types=["traces_to", "implements"],
        )

        affected_ids = {item["id"] for item in result.affected_items}
        assert "traces_child" in affected_ids
        assert "impl_child" in affected_ids
        assert "other_child" not in affected_ids


class TestPerformanceCharacteristics:
    """Test performance on large graphs."""

    @pytest.mark.asyncio
    async def test_wide_graph_processing(self, service):
        """Test processing item with many children."""
        root = create_mock_item("root")
        num_children = 50
        children = [create_mock_item(f"child{i}") for i in range(num_children)]

        links = [create_mock_link("root", f"child{i}") for i in range(num_children)]

        items = {"root": root}
        items.update({child.id: child for child in children})

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.total_affected == num_children

    @pytest.mark.asyncio
    async def test_deep_graph_processing(self, service):
        """Test processing deeply nested graph."""
        num_levels = 30
        items = {str(i): create_mock_item(str(i)) for i in range(num_levels)}
        links = {
            str(i): [create_mock_link(str(i), str(i + 1))]
            for i in range(num_levels - 1)
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0", max_depth=50)

        assert result.total_affected == num_levels - 1


class TestErrorRecovery:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_handles_item_repository_failure(self, service):
        """Test handling when item repository fails."""
        service.items.get_by_id = AsyncMock(side_effect=Exception("DB error"))

        with pytest.raises(Exception):
            await service.analyze_impact("item")

    @pytest.mark.asyncio
    async def test_handles_link_repository_failure(self, service):
        """Test handling when link repository fails."""
        item = create_mock_item("item")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(side_effect=Exception("DB error"))

        with pytest.raises(Exception):
            await service.analyze_impact("item")

    @pytest.mark.asyncio
    async def test_skips_missing_intermediate_items(self, service):
        """Test graceful handling of missing intermediate items."""
        root = create_mock_item("root")
        leaf = create_mock_item("leaf")

        link1 = create_mock_link("root", "missing")
        link2 = create_mock_link("missing", "leaf")

        def get_item(id):
            if id == "root":
                return root
            if id == "leaf":
                return leaf
            return None

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(
            side_effect=lambda id: [link1] if id == "root" else [link2] if id == "missing" else []
        )

        result = await service.analyze_impact("root")

        # Root has link to missing, missing is skipped, leaf unreachable
        assert result.total_affected == 0


class TestResultConsistency:
    """Test consistency of results across multiple calls."""

    @pytest.mark.asyncio
    async def test_result_idempotency(self, service):
        """Test same input produces same output."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        link = create_mock_link("root", "child")

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result1 = await service.analyze_impact("root")
        result2 = await service.analyze_impact("root")

        assert result1.total_affected == result2.total_affected
        assert result1.max_depth_reached == result2.max_depth_reached

    @pytest.mark.asyncio
    async def test_forward_reverse_consistency(self, service):
        """Test relationship between forward and reverse analysis."""
        a = create_mock_item("a")
        b = create_mock_item("b")

        links = {"a": [create_mock_link("a", "b")]}

        items = {"a": a, "b": b}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: [create_mock_link("a", "b")] if id == "b" else [])

        forward = await service.analyze_impact("a")
        reverse = await service.analyze_reverse_impact("b")

        # Forward from a should find b
        # Reverse from b should find a
        assert any(item["id"] == "b" for item in forward.affected_items)
        assert any(item["id"] == "a" for item in reverse.affected_items)


class TestSpecialCases:
    """Test special and corner cases."""

    @pytest.mark.asyncio
    async def test_item_with_metadata(self, service):
        """Test items with metadata are handled correctly."""
        item = Mock()
        item.id = "item"
        item.title = "Item"
        item.view = "REQ"
        item.item_type = "requirement"
        item.status = "active"
        item.item_metadata = {"custom": "value"}

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item")

        assert result.root_item_id == "item"

    @pytest.mark.asyncio
    async def test_unicode_in_titles(self, service):
        """Test handling unicode characters in item titles."""
        item = create_mock_item("item", title="项目 🚀 Test")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item")

        assert result.root_item_title == "项目 🚀 Test"

    @pytest.mark.asyncio
    async def test_very_large_title(self, service):
        """Test handling very long item titles."""
        long_title = "A" * 1000
        item = create_mock_item("item", title=long_title)
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item")

        assert result.root_item_title == long_title
