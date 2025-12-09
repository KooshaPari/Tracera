"""
Comprehensive tests for AdvancedTraceabilityService and AdvancedTraceabilityEnhancementsService.

Full coverage of all methods including path finding, transitive closure, impact analysis,
circular dependency detection, coverage gaps, and bidirectional analysis.
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from tracertm.services.advanced_traceability_service import (
    AdvancedTraceabilityService,
    TraceabilityPath,
    ImpactAnalysis,
)
from tracertm.services.advanced_traceability_enhancements_service import (
    AdvancedTraceabilityEnhancementsService,
)


class TestAdvancedTraceabilityService:
    """Test AdvancedTraceabilityService."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = AsyncMock()
        service = AdvancedTraceabilityService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_find_all_paths_direct(self, service):
        """Test finding direct path between items."""
        # Setup mock link
        mock_link = Mock()
        mock_link.target_item_id = "item-2"
        service.links.get_by_source = AsyncMock(return_value=[mock_link])

        # Execute
        paths = await service.find_all_paths("item-1", "item-2", max_depth=10)

        # Assert
        assert len(paths) > 0
        assert paths[0].source_id == "item-1"
        assert paths[0].target_id == "item-2"
        assert paths[0].distance == 1

    @pytest.mark.asyncio
    async def test_find_all_paths_indirect(self, service):
        """Test finding indirect paths through intermediates."""
        # Setup: item-1 -> item-2 -> item-3
        async def mock_get_by_source(item_id):
            if item_id == "item-1":
                link = Mock()
                link.target_item_id = "item-2"
                return [link]
            elif item_id == "item-2":
                link = Mock()
                link.target_item_id = "item-3"
                return [link]
            return []

        service.links.get_by_source = mock_get_by_source

        # Execute
        paths = await service.find_all_paths("item-1", "item-3", max_depth=10)

        # Assert
        assert len(paths) > 0
        assert paths[0].distance == 2  # Two hops

    @pytest.mark.asyncio
    async def test_find_all_paths_max_depth(self, service):
        """Test max depth limit is respected."""
        # Setup deep chain
        async def mock_get_by_source(item_id):
            if item_id == "item-1":
                link = Mock()
                link.target_item_id = "item-2"
                return [link]
            elif item_id == "item-2":
                link = Mock()
                link.target_item_id = "item-3"
                return [link]
            return []

        service.links.get_by_source = mock_get_by_source

        # Execute with max_depth=1
        paths = await service.find_all_paths("item-1", "item-3", max_depth=1)

        # Assert - should not find path
        assert len(paths) == 0

    @pytest.mark.asyncio
    async def test_find_all_paths_no_path_exists(self, service):
        """Test when no path exists."""
        service.links.get_by_source = AsyncMock(return_value=[])

        paths = await service.find_all_paths("item-1", "item-2", max_depth=10)

        assert len(paths) == 0

    @pytest.mark.asyncio
    async def test_transitive_closure(self, service):
        """Test computing transitive closure."""
        # Setup items
        items = [
            Mock(id="item-1"),
            Mock(id="item-2"),
            Mock(id="item-3"),
        ]
        service.items.query = AsyncMock(return_value=items)

        # Setup links: item-1 -> item-2 -> item-3
        async def mock_get_by_source(item_id):
            if item_id == "item-1":
                link = Mock()
                link.target_item_id = "item-2"
                return [link]
            elif item_id == "item-2":
                link = Mock()
                link.target_item_id = "item-3"
                return [link]
            return []

        service.links.get_by_source = mock_get_by_source

        # Execute
        closure = await service.transitive_closure("proj-1")

        # Assert
        assert "item-1" in closure
        assert "item-2" in closure["item-1"]
        assert "item-3" in closure["item-1"]  # Transitive

    @pytest.mark.asyncio
    async def test_bidirectional_impact(self, service):
        """Test bidirectional impact analysis."""
        # Setup forward links
        forward_link = Mock()
        forward_link.target_item_id = "item-2"
        service.links.get_by_source = AsyncMock(return_value=[forward_link])

        # Setup backward links
        backward_link = Mock()
        backward_link.source_item_id = "item-0"
        service.links.get_by_target = AsyncMock(return_value=[backward_link])

        # Execute
        result = await service.bidirectional_impact("item-1")

        # Assert
        assert result["entity_id"] == "item-1"
        assert "item-2" in result["forward_impact"]
        assert "item-0" in result["backward_impact"]
        assert result["total_impact"] == 2

    @pytest.mark.asyncio
    async def test_coverage_gaps(self, service):
        """Test finding coverage gaps between views."""
        # Setup source items
        source_items = [
            Mock(id="source-1", view="FEATURE"),
            Mock(id="source-2", view="FEATURE"),
        ]
        service.items.get_by_view = AsyncMock(return_value=source_items)

        # Setup links - source-1 has link to target view, source-2 doesn't
        async def mock_get_by_source(item_id):
            if item_id == "source-1":
                link = Mock()
                link.target_item_id = "target-1"
                return [link]
            return []

        service.links.get_by_source = mock_get_by_source

        # Mock get_by_id to return target with CODE view
        async def mock_get_by_id(item_id):
            if item_id == "target-1":
                return Mock(id="target-1", view="CODE")
            return None

        service.items.get_by_id = mock_get_by_id

        # Execute
        gaps = await service.coverage_gaps("proj-1", "FEATURE", "CODE")

        # Assert source-2 is in gaps
        assert "source-2" in gaps
        assert "source-1" not in gaps

    @pytest.mark.asyncio
    async def test_circular_dependency_check(self, service):
        """Test detecting circular dependencies."""
        # Setup items
        items = [
            Mock(id="item-1"),
            Mock(id="item-2"),
            Mock(id="item-3"),
        ]
        service.items.query = AsyncMock(return_value=items)

        # Setup circular links: item-1 -> item-2 -> item-3 -> item-1
        async def mock_get_by_source(item_id):
            if item_id == "item-1":
                return [Mock(target_item_id="item-2")]
            elif item_id == "item-2":
                return [Mock(target_item_id="item-3")]
            elif item_id == "item-3":
                return [Mock(target_item_id="item-1")]
            return []

        service.links.get_by_source = mock_get_by_source

        # Execute
        cycles = await service.circular_dependency_check("proj-1")

        # Assert cycle detected
        assert len(cycles) > 0
        # Cycle should contain all three items
        assert any(len(cycle) == 4 for cycle in cycles)  # item-1 -> item-2 -> item-3 -> item-1


class TestAdvancedTraceabilityEnhancementsService:
    """Test AdvancedTraceabilityEnhancementsService."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = AsyncMock()
        service = AdvancedTraceabilityEnhancementsService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_detect_circular_dependencies(self, service):
        """Test circular dependency detection."""
        # Setup items with circular links
        item1 = Mock(id="item-1")
        item1.outgoing_links = [Mock(target_item_id="item-2")]
        item2 = Mock(id="item-2")
        item2.outgoing_links = [Mock(target_item_id="item-1")]

        service.items.query = AsyncMock(return_value=[item1, item2])

        # Execute
        result = await service.detect_circular_dependencies("proj-1")

        # Assert
        assert result["has_cycles"] is True
        assert result["cycle_count"] > 0

    @pytest.mark.asyncio
    async def test_detect_no_circular_dependencies(self, service):
        """Test when no circular dependencies exist."""
        # Setup items with no cycles
        item1 = Mock(id="item-1")
        item1.outgoing_links = [Mock(target_item_id="item-2")]
        item2 = Mock(id="item-2")
        item2.outgoing_links = []

        service.items.query = AsyncMock(return_value=[item1, item2])

        # Execute
        result = await service.detect_circular_dependencies("proj-1")

        # Assert
        assert result["has_cycles"] is False

    @pytest.mark.asyncio
    async def test_coverage_gap_analysis(self, service):
        """Test coverage gap analysis between views."""
        # Setup source and target items
        source1 = Mock(id="source-1", view="FEATURE")
        source1.outgoing_links = [Mock(target_item_id="target-1")]
        source2 = Mock(id="source-2", view="FEATURE")
        source2.outgoing_links = []

        target1 = Mock(id="target-1", view="CODE")

        items = [source1, source2, target1]
        service.items.query = AsyncMock(return_value=items)

        # Execute
        result = await service.coverage_gap_analysis(
            "proj-1", "FEATURE", "CODE"
        )

        # Assert
        assert result["total_source_items"] == 2
        assert result["covered_items"] == 1
        assert result["uncovered_items"] == 1
        assert result["coverage_percent"] == 50.0
        assert "source-2" in result["uncovered_item_ids"]

    @pytest.mark.asyncio
    async def test_coverage_gap_analysis_full_coverage(self, service):
        """Test when all items are covered."""
        source1 = Mock(id="source-1", view="FEATURE")
        source1.outgoing_links = [Mock(target_item_id="target-1")]
        target1 = Mock(id="target-1", view="CODE")

        service.items.query = AsyncMock(return_value=[source1, target1])

        result = await service.coverage_gap_analysis("proj-1", "FEATURE", "CODE")

        # Assert
        assert result["coverage_percent"] == 100.0
        assert result["uncovered_items"] == 0

    @pytest.mark.asyncio
    async def test_bidirectional_link_analysis(self, service):
        """Test bidirectional link analysis for an item."""
        # Setup item
        item = Mock(id="item-1")
        item.outgoing_links = [
            Mock(target_item_id="outgoing-1", link_type="depends_on"),
            Mock(target_item_id="outgoing-2", link_type="relates_to"),
        ]
        service.items.get_by_id = AsyncMock(return_value=item)

        # Setup other items with incoming links
        other_item = Mock(id="other-1")
        other_item.outgoing_links = [
            Mock(target_item_id="item-1", link_type="implements")
        ]
        service.items.query = AsyncMock(return_value=[other_item])

        # Execute
        result = await service.bidirectional_link_analysis("proj-1", "item-1")

        # Assert
        assert result["item_id"] == "item-1"
        assert result["outgoing_links"] == 2
        assert result["incoming_links"] == 1
        assert result["total_connections"] == 3

    @pytest.mark.asyncio
    async def test_bidirectional_link_analysis_item_not_found(self, service):
        """Test error when item not found."""
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service.bidirectional_link_analysis("proj-1", "nonexistent")

        assert "error" in result
        assert result["error"] == "Item not found"

    @pytest.mark.asyncio
    async def test_traceability_matrix_generation(self, service):
        """Test generating traceability matrix."""
        # Setup source and target items
        source1 = Mock(id="source-1", title="Feature 1", view="FEATURE")
        source1.outgoing_links = [
            Mock(target_item_id="target-1", link_type="implements"),
            Mock(target_item_id="target-2", link_type="tests"),
        ]

        source2 = Mock(id="source-2", title="Feature 2", view="FEATURE")
        source2.outgoing_links = []

        target1 = Mock(id="target-1", view="CODE")
        target2 = Mock(id="target-2", view="CODE")

        items = [source1, source2, target1, target2]
        service.items.query = AsyncMock(return_value=items)

        # Execute
        result = await service.traceability_matrix_generation(
            "proj-1", "FEATURE", "CODE"
        )

        # Assert
        assert result["source_view"] == "FEATURE"
        assert result["target_view"] == "CODE"
        assert result["total_rows"] == 2
        assert result["total_columns"] == 2

        # Check matrix content
        matrix = result["matrix"]
        assert len(matrix) == 2
        assert matrix[0]["source_id"] == "source-1"
        assert len(matrix[0]["targets"]) == 2
        assert matrix[1]["source_id"] == "source-2"
        assert len(matrix[1]["targets"]) == 0

    @pytest.mark.asyncio
    async def test_impact_propagation_analysis(self, service):
        """Test impact propagation through dependency graph."""
        # Setup item
        item = Mock(id="item-1")
        service.items.get_by_id = AsyncMock(return_value=item)

        # Setup chain: item-1 <- item-2 <- item-3
        item2 = Mock(id="item-2")
        item2.outgoing_links = [Mock(target_item_id="item-1")]

        item3 = Mock(id="item-3")
        item3.outgoing_links = [Mock(target_item_id="item-2")]

        service.items.query = AsyncMock(return_value=[item2, item3])

        # Execute
        result = await service.impact_propagation_analysis(
            "proj-1", "item-1", max_depth=5
        )

        # Assert
        assert result["item_id"] == "item-1"
        assert result["total_impacted"] >= 2  # item-2 and item-3
        assert "item-2" in result["impact_levels"]
        assert "item-3" in result["impact_levels"]

    @pytest.mark.asyncio
    async def test_impact_propagation_max_depth(self, service):
        """Test impact propagation respects max depth."""
        item = Mock(id="item-1")
        service.items.get_by_id = AsyncMock(return_value=item)

        # Setup deep chain
        items = []
        for i in range(10):
            item = Mock(id=f"item-{i}")
            if i > 0:
                item.outgoing_links = [Mock(target_item_id=f"item-{i-1}")]
            else:
                item.outgoing_links = []
            items.append(item)

        service.items.query = AsyncMock(return_value=items)

        # Execute with max_depth=3
        result = await service.impact_propagation_analysis(
            "proj-1", "item-1", max_depth=3
        )

        # Assert max depth is respected
        assert result["max_depth_reached"] <= 3

    @pytest.mark.asyncio
    async def test_impact_propagation_item_not_found(self, service):
        """Test error when item not found."""
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service.impact_propagation_analysis(
            "proj-1", "nonexistent"
        )

        assert "error" in result
        assert result["error"] == "Item not found"


class TestTraceabilityPath:
    """Test TraceabilityPath dataclass."""

    def test_create_path(self):
        """Test creating a traceability path."""
        path = TraceabilityPath(
            source_id="source-1",
            target_id="target-1",
            path=["source-1", "intermediate-1", "target-1"],
            distance=2,
        )

        assert path.source_id == "source-1"
        assert path.target_id == "target-1"
        assert len(path.path) == 3
        assert path.distance == 2


class TestImpactAnalysis:
    """Test ImpactAnalysis dataclass."""

    def test_create_impact_analysis(self):
        """Test creating impact analysis result."""
        impact = ImpactAnalysis(
            entity_id="entity-1",
            direct_impact=["item-1", "item-2"],
            indirect_impact=["item-3", "item-4", "item-5"],
            total_impact=5,
            impact_depth=3,
        )

        assert impact.entity_id == "entity-1"
        assert len(impact.direct_impact) == 2
        assert len(impact.indirect_impact) == 3
        assert impact.total_impact == 5
        assert impact.impact_depth == 3
