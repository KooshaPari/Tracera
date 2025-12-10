"""
Extended Impact Analysis Service Coverage Tests.

This module provides additional test coverage for ImpactAnalysisService
targeting +3% coverage improvement.

Focus Areas:
- Complex graph topologies
- Performance edge cases
- Metrics validation
- Boundary conditions
- Integration patterns

Target: 30-50 additional test cases
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from collections import deque

from tracertm.services.impact_analysis_service import (
    ImpactAnalysisService,
    ImpactNode,
    ImpactAnalysisResult,
)


# ============================================================================
# FIXTURES AND HELPERS
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
) -> Mock:
    """Helper to create mock item."""
    item = Mock()
    item.id = item_id
    item.title = title or f"Item {item_id}"
    item.view = view
    item.item_type = item_type
    item.status = status
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
# COMPLEX TOPOLOGY TESTS
# ============================================================================


class TestComplexTopologies:
    """Test impact analysis on complex graph topologies."""

    @pytest.mark.asyncio
    async def test_star_topology(self, service):
        """Test star topology: one central hub with many spokes."""
        hub = create_mock_item("hub", "Central Hub")
        spokes = [create_mock_item(f"spoke{i}") for i in range(8)]

        items = {"hub": hub}
        items.update({spoke.id: spoke for spoke in spokes})

        links = [create_mock_link("hub", spoke.id) for spoke in spokes]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "hub" else [])

        result = await service.analyze_impact("hub")

        assert result.total_affected == 8
        assert result.affected_by_depth[1] == 8
        assert len(result.critical_paths) == 8

    @pytest.mark.asyncio
    async def test_fully_connected_subgraph(self, service):
        """Test fully connected subgraph (complete graph)."""
        items_dict = {str(i): create_mock_item(str(i)) for i in range(5)}

        links_dict = {}
        for i in range(5):
            links_dict[str(i)] = [
                create_mock_link(str(i), str(j))
                for j in range(5)
                if i != j
            ]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items_dict.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links_dict.get(id, []))

        result = await service.analyze_impact("0")

        # BFS visits nodes in breadth-first order
        assert result.total_affected > 0
        assert result.max_depth_reached > 0

    @pytest.mark.asyncio
    async def test_bipartite_graph(self, service):
        """Test bipartite graph: two sets with cross-links."""
        set_a = [create_mock_item(f"a{i}", view="REQ") for i in range(3)]
        set_b = [create_mock_item(f"b{i}", view="DESIGN") for i in range(3)]

        items = {}
        items.update({item.id: item for item in set_a})
        items.update({item.id: item for item in set_b})

        links_dict = {}
        for a in set_a:
            links_dict[a.id] = [create_mock_link(a.id, b.id) for b in set_b]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links_dict.get(id, []))

        result = await service.analyze_impact("a0")

        assert result.total_affected == 3  # reaches set_b
        assert result.affected_by_view["DESIGN"] == 3

    @pytest.mark.asyncio
    async def test_mesh_network_pattern(self, service):
        """Test mesh network with redundant paths."""
        items_dict = {}
        for i in range(6):
            items_dict[str(i)] = create_mock_item(str(i))

        # Create mesh: each node connects to next 2 nodes
        links_dict = {}
        for i in range(6):
            links_dict[str(i)] = [
                create_mock_link(str(i), str((i + 1) % 6)),
                create_mock_link(str(i), str((i + 2) % 6)),
            ]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items_dict.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links_dict.get(id, []))

        result = await service.analyze_impact("0", max_depth=10)

        # Should handle cyclic paths without infinite loop
        assert result.total_affected <= 5  # excluding root
        assert "0" not in [item["id"] for item in result.affected_items]

    @pytest.mark.asyncio
    async def test_grid_graph_pattern(self, service):
        """Test grid graph: 3x3 grid of items."""
        items_dict = {}
        links_dict = {}

        for i in range(3):
            for j in range(3):
                node_id = f"{i}_{j}"
                items_dict[node_id] = create_mock_item(node_id)
                links_dict[node_id] = []

                # Connect right
                if j < 2:
                    links_dict[node_id].append(
                        create_mock_link(node_id, f"{i}_{j+1}")
                    )
                # Connect down
                if i < 2:
                    links_dict[node_id].append(
                        create_mock_link(node_id, f"{i+1}_{j}")
                    )

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items_dict.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links_dict.get(id, []))

        result = await service.analyze_impact("0_0", max_depth=10)

        assert result.total_affected == 8  # 9 items minus root
        assert result.max_depth_reached > 0


# ============================================================================
# METRICS VALIDATION TESTS
# ============================================================================


class TestMetricsValidation:
    """Test correctness of impact analysis metrics."""

    @pytest.mark.asyncio
    async def test_affected_by_depth_consistency(self, service):
        """Test affected_by_depth metrics consistency."""
        root = create_mock_item("root")
        level1 = [create_mock_item(f"l1_{i}") for i in range(3)]
        level2 = [create_mock_item(f"l2_{i}") for i in range(2)]

        items = {"root": root}
        items.update({item.id: item for item in level1 + level2})

        links = {
            "root": [create_mock_link("root", item.id) for item in level1],
        }
        for i, item in enumerate(level1):
            if i < 2:
                links[item.id] = [create_mock_link(item.id, level2[i].id)]
            else:
                links[item.id] = []

        for item in level2:
            links[item.id] = []

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        # Verify depth consistency
        depth_total = sum(result.affected_by_depth.values())
        assert depth_total == result.total_affected

    @pytest.mark.asyncio
    async def test_affected_by_view_accuracy(self, service):
        """Test view-based metrics accuracy."""
        items = {}
        for view in ["REQ", "DESIGN", "CODE", "TEST"]:
            for i in range(2):
                items[f"{view}_{i}"] = create_mock_item(f"{view}_{i}", view=view)

        root = create_mock_item("root", view="ROOT")
        items["root"] = root

        links = {
            "root": [
                create_mock_link("root", f"{view}_{i}")
                for view in ["REQ", "DESIGN", "CODE", "TEST"]
                for i in range(2)
            ]
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        # Verify view counts
        for view in ["REQ", "DESIGN", "CODE", "TEST"]:
            assert result.affected_by_view[view] == 2

    @pytest.mark.asyncio
    async def test_max_depth_reached_accuracy(self, service):
        """Test max_depth_reached is correctly calculated."""
        num_items = 7
        items = {str(i): create_mock_item(str(i)) for i in range(num_items)}
        links = {
            str(i): [create_mock_link(str(i), str(i + 1))]
            for i in range(num_items - 1)
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0", max_depth=50)

        assert result.max_depth_reached == num_items - 1

    @pytest.mark.asyncio
    async def test_total_affected_count_accuracy(self, service):
        """Test total_affected matches actual affected items."""
        root = create_mock_item("root")
        children = [create_mock_item(f"child{i}") for i in range(5)]
        grandchildren = [create_mock_item(f"grand{i}") for i in range(3)]

        items = {"root": root}
        items.update({child.id: child for child in children})
        items.update({grand.id: grand for grand in grandchildren})

        links = {
            "root": [create_mock_link("root", child.id) for child in children],
        }
        for i, child in enumerate(children):
            if i < len(grandchildren):
                links[child.id] = [create_mock_link(child.id, grandchildren[i].id)]
            else:
                links[child.id] = []

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        assert result.total_affected == len(result.affected_items)


# ============================================================================
# BOUNDARY CONDITION TESTS
# ============================================================================


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    @pytest.mark.asyncio
    async def test_max_depth_equal_one(self, service):
        """Test with max_depth exactly 1."""
        root = create_mock_item("root")
        child = create_mock_item("child")
        grandchild = create_mock_item("grandchild")

        items = {"root": root, "child": child, "grandchild": grandchild}
        links = {
            "root": [create_mock_link("root", "child")],
            "child": [create_mock_link("child", "grandchild")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root", max_depth=1)

        assert result.total_affected == 1
        assert "child" in [item["id"] for item in result.affected_items]
        assert "grandchild" not in [item["id"] for item in result.affected_items]

    @pytest.mark.asyncio
    async def test_single_link_type_filter(self, service):
        """Test filtering by single link type."""
        root = create_mock_item("root")
        child1 = create_mock_item("child1")
        child2 = create_mock_item("child2")

        items = {"root": root, "child1": child1, "child2": child2}
        links = [
            create_mock_link("root", "child1", "traces_to"),
            create_mock_link("root", "child2", "depends_on"),
        ]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root", link_types=["traces_to"])

        assert result.total_affected == 1
        assert result.affected_items[0]["id"] == "child1"

    @pytest.mark.asyncio
    async def test_empty_result_fields_populated(self, service):
        """Test all fields populated even with empty results."""
        item = create_mock_item("item")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item")

        assert isinstance(result.affected_by_depth, dict)
        assert isinstance(result.affected_by_view, dict)
        assert isinstance(result.affected_items, list)
        assert isinstance(result.critical_paths, list)
        assert len(result.affected_by_depth) == 0
        assert len(result.affected_by_view) == 0

    @pytest.mark.asyncio
    async def test_max_int_depth(self, service):
        """Test with very large max_depth value."""
        items = {str(i): create_mock_item(str(i)) for i in range(5)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(4)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0", max_depth=999999)

        assert result.total_affected == 4


# ============================================================================
# REVERSE IMPACT EXTENDED TESTS
# ============================================================================


class TestReverseImpactExtended:
    """Extended tests for reverse impact analysis."""

    @pytest.mark.asyncio
    async def test_reverse_diamond_pattern(self, service):
        """Test reverse impact on diamond pattern."""
        a = create_mock_item("a")
        b = create_mock_item("b")
        c = create_mock_item("c")
        center = create_mock_item("center")

        items = {"a": a, "b": b, "c": c, "center": center}

        # Diamond converging to center: a,b,c -> center
        links = {
            "center": [
                create_mock_link("a", "center"),
                create_mock_link("b", "center"),
                create_mock_link("c", "center"),
            ]
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_reverse_impact("center")

        assert result.total_affected == 3
        affected_ids = {item["id"] for item in result.affected_items}
        assert affected_ids == {"a", "b", "c"}

    @pytest.mark.asyncio
    async def test_reverse_with_missing_intermediate(self, service):
        """Test reverse impact skips missing items."""
        target = create_mock_item("target")
        source = create_mock_item("source")

        items = {"target": target, "source": source}

        # Link from missing item
        links = {
            "target": [create_mock_link("missing", "target")]
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_target = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_reverse_impact("target")

        # Missing item not added to results
        assert result.total_affected == 0


# ============================================================================
# CRITICAL PATH EXTRACTION TESTS
# ============================================================================


class TestCriticalPathExtraction:
    """Test critical path identification."""

    @pytest.mark.asyncio
    async def test_multiple_critical_paths_complex_tree(self, service):
        """Test multiple critical paths in complex tree."""
        root = create_mock_item("root")

        # Create tree with multiple branches
        # root -> [a, b] -> [c, d, e]
        a = create_mock_item("a")
        b = create_mock_item("b")
        c = create_mock_item("c")
        d = create_mock_item("d")
        e = create_mock_item("e")

        items = {"root": root, "a": a, "b": b, "c": c, "d": d, "e": e}

        links = {
            "root": [create_mock_link("root", "a"), create_mock_link("root", "b")],
            "a": [create_mock_link("a", "c"), create_mock_link("a", "d")],
            "b": [create_mock_link("b", "e")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        # Should have critical paths to c, d, e (leaf nodes)
        assert len(result.critical_paths) == 3

    @pytest.mark.asyncio
    async def test_critical_paths_validation(self, service):
        """Test critical paths are valid and complete."""
        items = {str(i): create_mock_item(str(i)) for i in range(4)}
        links = {
            "0": [create_mock_link("0", "1")],
            "1": [create_mock_link("1", "2"), create_mock_link("1", "3")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        # All critical paths should start with root
        for path in result.critical_paths:
            assert path[0] == "0"
            # All paths should end at leaf nodes
            assert len(path) >= 1


# ============================================================================
# LINK TYPE HANDLING ADVANCED TESTS
# ============================================================================


class TestLinkTypeHandlingAdvanced:
    """Advanced link type handling tests."""

    @pytest.mark.asyncio
    async def test_null_link_types_in_filter(self, service):
        """Test items with None link_type are filtered correctly."""
        root = create_mock_item("root")
        child = create_mock_item("child")

        link = Mock()
        link.target_item_id = "child"
        link.link_type = None

        items = {"root": root, "child": child}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        # Filter for specific type should exclude None links
        result = await service.analyze_impact("root", link_types=["traces_to"])

        assert result.total_affected == 0

    @pytest.mark.asyncio
    async def test_link_type_case_sensitivity(self, service):
        """Test link type filtering is case-sensitive."""
        root = create_mock_item("root")
        child = create_mock_item("child")

        link = create_mock_link("root", "child", "Traces_To")

        items = {"root": root, "child": child}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        # Case mismatch should not match
        result = await service.analyze_impact("root", link_types=["traces_to"])

        assert result.total_affected == 0


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================


class TestDataValidation:
    """Test data validation and integrity."""

    @pytest.mark.asyncio
    async def test_all_affected_items_have_valid_paths(self, service):
        """Test all affected items have valid path structure."""
        items = {str(i): create_mock_item(str(i)) for i in range(5)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(4)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        for item in result.affected_items:
            assert isinstance(item["path"], list)
            assert len(item["path"]) > 0
            assert item["path"][0] == "0"
            assert item["path"][-1] == item["id"]

    @pytest.mark.asyncio
    async def test_depth_matches_path_length_minus_one(self, service):
        """Test depth calculation is consistent with path."""
        items = {str(i): create_mock_item(str(i)) for i in range(5)}
        links = {str(i): [create_mock_link(str(i), str(i + 1))] for i in range(4)}

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0")

        for item in result.affected_items:
            assert item["depth"] == len(item["path"]) - 1

    @pytest.mark.asyncio
    async def test_item_properties_preserved(self, service):
        """Test item properties are preserved in results."""
        item = create_mock_item("item", title="Custom Title", view="CUSTOM",
                               item_type="custom_type", status="pending")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item")

        assert result.root_item_title == "Custom Title"


# ============================================================================
# PERFORMANCE EDGE CASES
# ============================================================================


class TestPerformanceEdgeCases:
    """Test performance on edge case scenarios."""

    @pytest.mark.asyncio
    async def test_extremely_wide_graph(self, service):
        """Test performance with extremely wide graph."""
        root = create_mock_item("root")
        num_children = 100
        children = [create_mock_item(f"child{i}") for i in range(num_children)]

        items = {"root": root}
        items.update({child.id: child for child in children})

        links = [create_mock_link("root", f"child{i}") for i in range(num_children)]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.total_affected == num_children

    @pytest.mark.asyncio
    async def test_very_deep_chain(self, service):
        """Test performance on very deep chain."""
        num_items = 50
        items = {str(i): create_mock_item(str(i)) for i in range(num_items)}
        links = {
            str(i): [create_mock_link(str(i), str(i + 1))]
            for i in range(num_items - 1)
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("0", max_depth=100)

        assert result.total_affected == num_items - 1
        assert result.max_depth_reached == num_items - 1


# ============================================================================
# VIEW-BASED FILTERING TESTS
# ============================================================================


class TestViewBasedFiltering:
    """Test view-specific filtering and analysis."""

    @pytest.mark.asyncio
    async def test_view_distribution_accuracy(self, service):
        """Test accurate view distribution counting."""
        root = create_mock_item("root", view="ROOT")
        req_items = [create_mock_item(f"req{i}", view="REQ") for i in range(2)]
        design_items = [create_mock_item(f"des{i}", view="DESIGN") for i in range(3)]
        code_items = [create_mock_item(f"code{i}", view="CODE") for i in range(1)]

        items = {"root": root}
        items.update({item.id: item for item in req_items + design_items + code_items})

        links = {
            "root": [
                *[create_mock_link("root", item.id) for item in req_items],
                *[create_mock_link("root", item.id) for item in design_items],
                *[create_mock_link("root", item.id) for item in code_items],
            ]
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        assert result.affected_by_view["REQ"] == 2
        assert result.affected_by_view["DESIGN"] == 3
        assert result.affected_by_view["CODE"] == 1


# ============================================================================
# STATUS TRACKING TESTS
# ============================================================================


class TestStatusTracking:
    """Test status-based tracking and analysis."""

    @pytest.mark.asyncio
    async def test_items_with_all_status_types(self, service):
        """Test items with different status values are tracked."""
        root = create_mock_item("root", status="active")
        items_by_status = {
            "todo": create_mock_item("todo", status="todo"),
            "in_progress": create_mock_item("in_progress", status="in_progress"),
            "done": create_mock_item("done", status="done"),
            "blocked": create_mock_item("blocked", status="blocked"),
        }

        items = {"root": root}
        items.update(items_by_status)

        links = {
            "root": [create_mock_link("root", id) for id in items_by_status.keys()]
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("root")

        statuses = {item["status"] for item in result.affected_items}
        assert statuses == {"todo", "in_progress", "done", "blocked"}


# ============================================================================
# INTEGRATION PATTERN TESTS
# ============================================================================


class TestIntegrationPatterns:
    """Test common integration patterns."""

    @pytest.mark.asyncio
    async def test_sequential_dependency_chain(self, service):
        """Test sequential dependency pattern."""
        # Simulate requirement -> design -> implementation -> test
        req = create_mock_item("req", item_type="requirement", view="REQ")
        design = create_mock_item("design", item_type="design", view="DESIGN")
        impl = create_mock_item("impl", item_type="implementation", view="CODE")
        test = create_mock_item("test", item_type="test", view="TEST")

        items = {"req": req, "design": design, "impl": impl, "test": test}

        links = {
            "req": [create_mock_link("req", "design", "traces_to")],
            "design": [create_mock_link("design", "impl", "implements")],
            "impl": [create_mock_link("impl", "test", "verifies")],
        }

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("req")

        assert result.total_affected == 3
        assert result.affected_by_depth[1] == 1  # design
        assert result.affected_by_depth[2] == 1  # impl
        assert result.affected_by_depth[3] == 1  # test

    @pytest.mark.asyncio
    async def test_multi_requirement_hierarchy(self, service):
        """Test multi-level requirement hierarchy."""
        epic = create_mock_item("epic", view="REQ", item_type="epic")
        features = [create_mock_item(f"feat{i}", view="REQ", item_type="feature")
                   for i in range(3)]
        stories = [create_mock_item(f"story{i}", view="REQ", item_type="story")
                  for i in range(6)]

        items = {"epic": epic}
        items.update({f.id: f for f in features})
        items.update({s.id: s for s in stories})

        links = {
            "epic": [create_mock_link("epic", f.id) for f in features],
        }
        for i, feat in enumerate(features):
            links[feat.id] = [
                create_mock_link(feat.id, stories[i*2].id),
                create_mock_link(feat.id, stories[i*2 + 1].id),
            ]

        service.items.get_by_id = AsyncMock(side_effect=lambda id: items.get(id))
        service.links.get_by_source = AsyncMock(side_effect=lambda id: links.get(id, []))

        result = await service.analyze_impact("epic")

        assert result.total_affected == 9  # 3 features + 6 stories
        assert result.affected_by_depth[1] == 3
        assert result.affected_by_depth[2] == 6
