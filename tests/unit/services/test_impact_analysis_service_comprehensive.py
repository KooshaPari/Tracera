"""
Comprehensive tests for ImpactAnalysisService.

Tests all methods: analyze_impact, analyze_reverse_impact, _find_critical_paths.
Tests ImpactNode and ImpactAnalysisResult dataclasses.

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, AsyncMock

from tracertm.services.impact_analysis_service import (
    ImpactAnalysisService,
    ImpactNode,
    ImpactAnalysisResult,
)


class TestImpactNode:
    """Test ImpactNode dataclass."""

    def test_impact_node_basic(self):
        """Test ImpactNode creation."""
        item = Mock()
        item.id = "item-1"
        item.title = "Test Item"

        node = ImpactNode(
            item=item,
            depth=2,
            path=["root", "item-1"],
        )

        assert node.item == item
        assert node.depth == 2
        assert node.path == ["root", "item-1"]
        assert node.link_type is None

    def test_impact_node_with_link_type(self):
        """Test ImpactNode with link_type."""
        item = Mock()
        node = ImpactNode(
            item=item,
            depth=1,
            path=["root", "child"],
            link_type="traces_to",
        )

        assert node.link_type == "traces_to"


class TestImpactAnalysisResult:
    """Test ImpactAnalysisResult dataclass."""

    def test_result_fields(self):
        """Test ImpactAnalysisResult fields."""
        result = ImpactAnalysisResult(
            root_item_id="root-1",
            root_item_title="Root Item",
            total_affected=5,
            max_depth_reached=3,
            affected_by_depth={1: 2, 2: 2, 3: 1},
            affected_by_view={"REQ": 3, "DESIGN": 2},
            affected_items=[
                {"id": "item-1", "title": "Item 1", "depth": 1},
            ],
            critical_paths=[["root-1", "item-1"]],
        )

        assert result.root_item_id == "root-1"
        assert result.root_item_title == "Root Item"
        assert result.total_affected == 5
        assert result.max_depth_reached == 3
        assert result.affected_by_depth[1] == 2
        assert result.affected_by_view["REQ"] == 3
        assert len(result.affected_items) == 1
        assert len(result.critical_paths) == 1


class TestAnalyzeImpact:
    """Test analyze_impact method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = ImpactAnalysisService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_item_not_found(self, service):
        """Test analyzing impact of nonexistent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await service.analyze_impact("nonexistent")

    @pytest.mark.asyncio
    async def test_no_downstream_links(self, service):
        """Test analyzing item with no downstream links."""
        root = Mock()
        root.id = "root"
        root.title = "Root Item"

        service.items.get_by_id = AsyncMock(return_value=root)
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("root")

        assert result.root_item_id == "root"
        assert result.total_affected == 0
        assert result.max_depth_reached == 0
        assert result.affected_items == []

    @pytest.mark.asyncio
    async def test_single_downstream_link(self, service):
        """Test analyzing item with one downstream link."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        child = Mock()
        child.id = "child"
        child.title = "Child"
        child.view = "REQ"
        child.item_type = "requirement"
        child.status = "active"

        link = Mock()
        link.target_item_id = "child"
        link.link_type = "traces_to"

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else child)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link] if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.total_affected == 1
        assert result.max_depth_reached == 1
        assert result.affected_by_depth[1] == 1
        assert len(result.affected_items) == 1
        assert result.affected_items[0]["id"] == "child"

    @pytest.mark.asyncio
    async def test_multiple_depths(self, service):
        """Test analyzing item with multiple depth levels."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        child1 = Mock()
        child1.id = "child1"
        child1.title = "Child 1"
        child1.view = "REQ"
        child1.item_type = "requirement"
        child1.status = "active"

        grandchild = Mock()
        grandchild.id = "grandchild"
        grandchild.title = "Grandchild"
        grandchild.view = "DESIGN"
        grandchild.item_type = "design"
        grandchild.status = "done"

        link1 = Mock()
        link1.target_item_id = "child1"
        link1.link_type = "traces_to"

        link2 = Mock()
        link2.target_item_id = "grandchild"
        link2.link_type = "implements"

        def get_item(id):
            return {"root": root, "child1": child1, "grandchild": grandchild}.get(id)

        def get_links(id):
            return {"root": [link1], "child1": [link2]}.get(id, [])

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=get_links)

        result = await service.analyze_impact("root")

        assert result.total_affected == 2
        assert result.max_depth_reached == 2
        assert result.affected_by_depth[1] == 1
        assert result.affected_by_depth[2] == 1

    @pytest.mark.asyncio
    async def test_respects_max_depth(self, service):
        """Test analyzing respects max_depth parameter."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        child = Mock()
        child.id = "child"
        child.title = "Child"
        child.view = "REQ"
        child.item_type = "requirement"
        child.status = "active"

        grandchild = Mock()
        grandchild.id = "grandchild"
        grandchild.title = "Grandchild"
        grandchild.view = "DESIGN"
        grandchild.item_type = "design"
        grandchild.status = "done"

        link1 = Mock()
        link1.target_item_id = "child"
        link1.link_type = "traces_to"

        link2 = Mock()
        link2.target_item_id = "grandchild"
        link2.link_type = "implements"

        def get_item(id):
            return {"root": root, "child": child, "grandchild": grandchild}.get(id)

        def get_links(id):
            return {"root": [link1], "child": [link2]}.get(id, [])

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=get_links)

        result = await service.analyze_impact("root", max_depth=1)

        assert result.total_affected == 1
        assert result.max_depth_reached == 1

    @pytest.mark.asyncio
    async def test_filters_by_link_type(self, service):
        """Test analyzing filters by link_types parameter."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        child1 = Mock()
        child1.id = "child1"
        child1.title = "Child 1"
        child1.view = "REQ"
        child1.item_type = "requirement"
        child1.status = "active"

        child2 = Mock()
        child2.id = "child2"
        child2.title = "Child 2"
        child2.view = "DESIGN"
        child2.item_type = "design"
        child2.status = "active"

        link1 = Mock()
        link1.target_item_id = "child1"
        link1.link_type = "traces_to"

        link2 = Mock()
        link2.target_item_id = "child2"
        link2.link_type = "relates_to"

        def get_item(id):
            return {"root": root, "child1": child1, "child2": child2}.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(return_value=[link1, link2])

        result = await service.analyze_impact("root", link_types=["traces_to"])

        assert result.total_affected == 1
        assert result.affected_items[0]["id"] == "child1"

    @pytest.mark.asyncio
    async def test_handles_cycles(self, service):
        """Test analyzing handles cyclic dependencies."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        child = Mock()
        child.id = "child"
        child.title = "Child"
        child.view = "REQ"
        child.item_type = "requirement"
        child.status = "active"

        # Link from root to child
        link1 = Mock()
        link1.target_item_id = "child"
        link1.link_type = "traces_to"

        # Link back from child to root (cycle)
        link2 = Mock()
        link2.target_item_id = "root"
        link2.link_type = "relates_to"

        def get_item(id):
            return {"root": root, "child": child}.get(id)

        def get_links(id):
            return {"root": [link1], "child": [link2]}.get(id, [])

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=get_links)

        result = await service.analyze_impact("root")

        # Should not infinite loop, visited set prevents cycles
        assert result.total_affected == 1  # Only child, root is visited

    @pytest.mark.asyncio
    async def test_handles_missing_downstream_item(self, service):
        """Test analyzing handles missing downstream item."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        link = Mock()
        link.target_item_id = "missing"
        link.link_type = "traces_to"

        service.items.get_by_id = AsyncMock(side_effect=lambda id: root if id == "root" else None)
        service.links.get_by_source = AsyncMock(return_value=[link])

        result = await service.analyze_impact("root")

        # Missing item is visited but skipped
        assert result.total_affected == 0

    @pytest.mark.asyncio
    async def test_affected_by_view_counts(self, service):
        """Test affected_by_view counts items correctly."""
        root = Mock()
        root.id = "root"
        root.title = "Root"

        child1 = Mock()
        child1.id = "child1"
        child1.title = "Child 1"
        child1.view = "REQ"
        child1.item_type = "requirement"
        child1.status = "active"

        child2 = Mock()
        child2.id = "child2"
        child2.title = "Child 2"
        child2.view = "REQ"
        child2.item_type = "requirement"
        child2.status = "active"

        child3 = Mock()
        child3.id = "child3"
        child3.title = "Child 3"
        child3.view = "DESIGN"
        child3.item_type = "design"
        child3.status = "done"

        link1 = Mock()
        link1.target_item_id = "child1"
        link1.link_type = "traces_to"

        link2 = Mock()
        link2.target_item_id = "child2"
        link2.link_type = "traces_to"

        link3 = Mock()
        link3.target_item_id = "child3"
        link3.link_type = "traces_to"

        def get_item(id):
            return {"root": root, "child1": child1, "child2": child2, "child3": child3}.get(id)

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_source = AsyncMock(side_effect=lambda id: [link1, link2, link3] if id == "root" else [])

        result = await service.analyze_impact("root")

        assert result.affected_by_view["REQ"] == 2
        assert result.affected_by_view["DESIGN"] == 1


class TestAnalyzeReverseImpact:
    """Test analyze_reverse_impact method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = ImpactAnalysisService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_item_not_found(self, service):
        """Test reverse impact of nonexistent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await service.analyze_reverse_impact("nonexistent")

    @pytest.mark.asyncio
    async def test_no_upstream_links(self, service):
        """Test item with no upstream links."""
        item = Mock()
        item.id = "item"
        item.title = "Item"

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.analyze_reverse_impact("item")

        assert result.total_affected == 0
        assert result.max_depth_reached == 0

    @pytest.mark.asyncio
    async def test_single_upstream_link(self, service):
        """Test item with one upstream link."""
        target = Mock()
        target.id = "target"
        target.title = "Target"

        source = Mock()
        source.id = "source"
        source.title = "Source"
        source.view = "REQ"
        source.item_type = "requirement"
        source.status = "active"

        link = Mock()
        link.source_item_id = "source"
        link.link_type = "traces_to"

        def get_item(id):
            return {"target": target, "source": source}.get(id)

        def get_links(id):
            return [link] if id == "target" else []

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_target = AsyncMock(side_effect=get_links)

        result = await service.analyze_reverse_impact("target")

        assert result.total_affected == 1
        assert result.affected_items[0]["id"] == "source"

    @pytest.mark.asyncio
    async def test_respects_max_depth(self, service):
        """Test reverse impact respects max_depth."""
        target = Mock()
        target.id = "target"
        target.title = "Target"

        parent = Mock()
        parent.id = "parent"
        parent.title = "Parent"
        parent.view = "REQ"
        parent.item_type = "requirement"
        parent.status = "active"

        grandparent = Mock()
        grandparent.id = "grandparent"
        grandparent.title = "Grandparent"
        grandparent.view = "DESIGN"
        grandparent.item_type = "design"
        grandparent.status = "done"

        link1 = Mock()
        link1.source_item_id = "parent"
        link1.link_type = "traces_to"

        link2 = Mock()
        link2.source_item_id = "grandparent"
        link2.link_type = "traces_to"

        def get_item(id):
            return {"target": target, "parent": parent, "grandparent": grandparent}.get(id)

        def get_links(id):
            return {"target": [link1], "parent": [link2]}.get(id, [])

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_target = AsyncMock(side_effect=get_links)

        result = await service.analyze_reverse_impact("target", max_depth=1)

        assert result.total_affected == 1

    @pytest.mark.asyncio
    async def test_handles_cycles(self, service):
        """Test reverse impact handles cycles."""
        item1 = Mock()
        item1.id = "item1"
        item1.title = "Item 1"

        item2 = Mock()
        item2.id = "item2"
        item2.title = "Item 2"
        item2.view = "REQ"
        item2.item_type = "requirement"
        item2.status = "active"

        link1 = Mock()
        link1.source_item_id = "item2"
        link1.link_type = "traces_to"

        link2 = Mock()
        link2.source_item_id = "item1"
        link2.link_type = "traces_to"

        def get_item(id):
            return {"item1": item1, "item2": item2}.get(id)

        def get_links(id):
            return {"item1": [link1], "item2": [link2]}.get(id, [])

        service.items.get_by_id = AsyncMock(side_effect=get_item)
        service.links.get_by_target = AsyncMock(side_effect=get_links)

        result = await service.analyze_reverse_impact("item1")

        # Should handle cycle without infinite loop
        assert result.total_affected >= 1


class TestFindCriticalPaths:
    """Test _find_critical_paths method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return ImpactAnalysisService(session)

    def test_no_nodes(self, service):
        """Test finding critical paths with no nodes."""
        result = service._find_critical_paths([])

        assert result == []

    def test_single_node(self, service):
        """Test finding critical paths with single node."""
        item = Mock()
        item.id = "child"

        node = ImpactNode(
            item=item,
            depth=1,
            path=["root", "child"],
        )

        result = service._find_critical_paths([node])

        assert len(result) == 1
        assert result[0] == ["root", "child"]

    def test_multiple_leaf_nodes(self, service):
        """Test finding critical paths with multiple leaf nodes."""
        item1 = Mock()
        item1.id = "child1"

        item2 = Mock()
        item2.id = "child2"

        node1 = ImpactNode(
            item=item1,
            depth=1,
            path=["root", "child1"],
        )

        node2 = ImpactNode(
            item=item2,
            depth=1,
            path=["root", "child2"],
        )

        result = service._find_critical_paths([node1, node2])

        assert len(result) == 2

    def test_non_leaf_nodes_excluded(self, service):
        """Test non-leaf nodes are excluded from critical paths."""
        parent = Mock()
        parent.id = "parent"

        child = Mock()
        child.id = "child"

        parent_node = ImpactNode(
            item=parent,
            depth=1,
            path=["root", "parent"],
        )

        child_node = ImpactNode(
            item=child,
            depth=2,
            path=["root", "parent", "child"],
        )

        result = service._find_critical_paths([parent_node, child_node])

        # Only child is a leaf
        assert len(result) == 1
        assert result[0] == ["root", "parent", "child"]


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_repositories(self):
        """Test initialization creates repositories."""
        session = AsyncMock()
        service = ImpactAnalysisService(session)

        assert service.session == session
        assert service.items is not None
        assert service.links is not None
