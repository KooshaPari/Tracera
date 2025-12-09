"""
Comprehensive tests for TraceabilityService.

Coverage target: 85%+
Tests all methods: create_link, generate_matrix, analyze_impact.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import Any

from tracertm.services.traceability_service import (
    TraceabilityService,
    TraceabilityMatrix,
    ImpactAnalysis,
)


class TestTraceabilityMatrix:
    """Test TraceabilityMatrix dataclass."""

    def test_create_matrix(self):
        """Test creating a TraceabilityMatrix."""
        matrix = TraceabilityMatrix(
            source_view="REQ",
            target_view="DEV",
            links=[{"source_id": "1", "target_id": "2"}],
            coverage_percentage=75.0,
            gaps=[{"id": "3", "title": "Uncovered"}],
        )

        assert matrix.source_view == "REQ"
        assert matrix.target_view == "DEV"
        assert len(matrix.links) == 1
        assert matrix.coverage_percentage == 75.0
        assert len(matrix.gaps) == 1


class TestImpactAnalysis:
    """Test ImpactAnalysis dataclass."""

    def test_create_impact_analysis(self):
        """Test creating an ImpactAnalysis."""
        item1 = Mock(id="item-1")
        item2 = Mock(id="item-2")

        analysis = ImpactAnalysis(
            item_id="root",
            directly_affected=[item1],
            indirectly_affected=[item2],
            total_impact_count=2,
        )

        assert analysis.item_id == "root"
        assert len(analysis.directly_affected) == 1
        assert len(analysis.indirectly_affected) == 1
        assert analysis.total_impact_count == 2


class TestTraceabilityServiceInit:
    """Test TraceabilityService initialization."""

    @pytest.mark.asyncio
    async def test_init_creates_repositories(self):
        """Test that initialization creates repositories."""
        session = AsyncMock()

        with patch("tracertm.services.traceability_service.ItemRepository") as mock_item_repo, \
             patch("tracertm.services.traceability_service.LinkRepository") as mock_link_repo:

            service = TraceabilityService(session)

            assert service.session == session
            mock_item_repo.assert_called_once_with(session)
            mock_link_repo.assert_called_once_with(session)


class TestCreateLink:
    """Test create_link method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = TraceabilityService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_create_link_success(self, service):
        """Test successful link creation."""
        source = Mock(id="source-1")
        target = Mock(id="target-1")
        link = Mock(id="link-1", source_item_id="source-1", target_item_id="target-1")

        service.items.get_by_id = AsyncMock(side_effect=[source, target])
        service.links.create = AsyncMock(return_value=link)

        result = await service.create_link(
            project_id="proj-1",
            source_item_id="source-1",
            target_item_id="target-1",
            link_type="depends_on",
        )

        assert result.id == "link-1"
        service.links.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_link_with_metadata(self, service):
        """Test link creation with metadata."""
        source = Mock(id="source-1")
        target = Mock(id="target-1")
        link = Mock(id="link-1")

        service.items.get_by_id = AsyncMock(side_effect=[source, target])
        service.links.create = AsyncMock(return_value=link)

        result = await service.create_link(
            project_id="proj-1",
            source_item_id="source-1",
            target_item_id="target-1",
            link_type="relates_to",
            metadata={"reason": "related"},
        )

        assert result.id == "link-1"
        call_kwargs = service.links.create.call_args[1]
        assert call_kwargs["metadata"] == {"reason": "related"}

    @pytest.mark.asyncio
    async def test_create_link_source_not_found(self, service):
        """Test link creation fails when source not found."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Source item .* not found"):
            await service.create_link(
                project_id="proj-1",
                source_item_id="nonexistent",
                target_item_id="target-1",
                link_type="depends_on",
            )

    @pytest.mark.asyncio
    async def test_create_link_target_not_found(self, service):
        """Test link creation fails when target not found."""
        source = Mock(id="source-1")
        service.items.get_by_id = AsyncMock(side_effect=[source, None])

        with pytest.raises(ValueError, match="Target item .* not found"):
            await service.create_link(
                project_id="proj-1",
                source_item_id="source-1",
                target_item_id="nonexistent",
                link_type="depends_on",
            )


class TestGenerateMatrix:
    """Test generate_matrix method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = TraceabilityService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_generate_matrix_empty_views(self, service):
        """Test matrix generation with empty views."""
        service.items.get_by_view = AsyncMock(return_value=[])

        result = await service.generate_matrix("proj-1", "REQ", "DEV")

        assert result.source_view == "REQ"
        assert result.target_view == "DEV"
        assert result.links == []
        assert result.coverage_percentage == 0
        assert result.gaps == []

    @pytest.mark.asyncio
    async def test_generate_matrix_with_links(self, service):
        """Test matrix generation with linked items."""
        source1 = Mock(id="src-1", title="Source 1")
        source2 = Mock(id="src-2", title="Source 2")
        target1 = Mock(id="tgt-1", title="Target 1", view="DEV")

        link1 = Mock(target_item_id="tgt-1", link_type="traces_to")

        service.items.get_by_view = AsyncMock(side_effect=[
            [source1, source2],  # Source items
            [target1],  # Target items
        ])

        async def get_links_by_source(item_id):
            if item_id == "src-1":
                return [link1]
            return []

        service.links.get_by_source = AsyncMock(side_effect=get_links_by_source)
        service.items.get_by_id = AsyncMock(return_value=target1)

        result = await service.generate_matrix("proj-1", "REQ", "DEV")

        assert result.source_view == "REQ"
        assert result.target_view == "DEV"
        assert len(result.links) == 1
        assert result.coverage_percentage == 50.0  # 1 of 2 source items linked
        assert len(result.gaps) == 1  # source2 has no links

    @pytest.mark.asyncio
    async def test_generate_matrix_full_coverage(self, service):
        """Test matrix generation with full coverage."""
        source1 = Mock(id="src-1", title="Source 1")
        target1 = Mock(id="tgt-1", title="Target 1", view="DEV")

        link1 = Mock(target_item_id="tgt-1", link_type="traces_to")

        service.items.get_by_view = AsyncMock(side_effect=[
            [source1],
            [target1],
        ])

        service.links.get_by_source = AsyncMock(return_value=[link1])
        service.items.get_by_id = AsyncMock(return_value=target1)

        result = await service.generate_matrix("proj-1", "REQ", "DEV")

        assert result.coverage_percentage == 100.0
        assert len(result.gaps) == 0

    @pytest.mark.asyncio
    async def test_generate_matrix_filters_by_target_view(self, service):
        """Test that matrix only includes links to target view."""
        source1 = Mock(id="src-1", title="Source 1")
        target_dev = Mock(id="tgt-dev", title="Target DEV", view="DEV")
        target_test = Mock(id="tgt-test", title="Target TEST", view="TEST")

        link1 = Mock(target_item_id="tgt-dev", link_type="traces_to")
        link2 = Mock(target_item_id="tgt-test", link_type="traces_to")

        service.items.get_by_view = AsyncMock(side_effect=[
            [source1],
            [target_dev],  # Only DEV targets
        ])

        service.links.get_by_source = AsyncMock(return_value=[link1, link2])

        async def get_by_id(item_id):
            if item_id == "tgt-dev":
                return target_dev
            elif item_id == "tgt-test":
                return target_test
            return None

        service.items.get_by_id = AsyncMock(side_effect=get_by_id)

        result = await service.generate_matrix("proj-1", "REQ", "DEV")

        # Should only include link to DEV view
        assert len(result.links) == 1
        assert result.links[0]["target_id"] == "tgt-dev"


class TestAnalyzeImpact:
    """Test analyze_impact method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = TraceabilityService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_analyze_impact_no_links(self, service):
        """Test impact analysis with no downstream links."""
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service.analyze_impact("item-1")

        assert result.item_id == "item-1"
        assert result.directly_affected == []
        assert result.indirectly_affected == []
        assert result.total_impact_count == 0

    @pytest.mark.asyncio
    async def test_analyze_impact_direct_only(self, service):
        """Test impact analysis with direct links only (max_depth=1)."""
        target = Mock(id="target-1")
        link = Mock(target_item_id="target-1")

        service.links.get_by_source = AsyncMock(return_value=[link])
        service.items.get_by_id = AsyncMock(return_value=target)

        result = await service.analyze_impact("item-1", max_depth=1)

        assert result.item_id == "item-1"
        assert len(result.directly_affected) == 1
        assert result.indirectly_affected == []
        assert result.total_impact_count == 1

    @pytest.mark.asyncio
    async def test_analyze_impact_with_indirect(self, service):
        """Test impact analysis with indirect (transitive) links."""
        direct_target = Mock(id="direct-1")
        indirect_target = Mock(id="indirect-1")

        direct_link = Mock(target_item_id="direct-1")
        indirect_link = Mock(target_item_id="indirect-1")

        async def get_links(item_id):
            if item_id == "item-1":
                return [direct_link]
            elif item_id == "direct-1":
                return [indirect_link]
            return []

        service.links.get_by_source = AsyncMock(side_effect=get_links)

        async def get_item(item_id):
            if item_id == "direct-1":
                return direct_target
            elif item_id == "indirect-1":
                return indirect_target
            return None

        service.items.get_by_id = AsyncMock(side_effect=get_item)

        result = await service.analyze_impact("item-1", max_depth=2)

        assert result.item_id == "item-1"
        assert len(result.directly_affected) == 1
        assert len(result.indirectly_affected) == 1
        assert result.total_impact_count == 2

    @pytest.mark.asyncio
    async def test_analyze_impact_respects_max_depth(self, service):
        """Test that max_depth limits traversal."""
        target = Mock(id="target-1")
        link = Mock(target_item_id="target-1")

        service.links.get_by_source = AsyncMock(return_value=[link])
        service.items.get_by_id = AsyncMock(return_value=target)

        result = await service.analyze_impact("item-1", max_depth=1)

        # With max_depth=1, no indirect affected items should be found
        assert result.indirectly_affected == []


class TestGetDownstreamItems:
    """Test _get_downstream_items helper method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = TraceabilityService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_downstream_depth_zero(self, service):
        """Test that depth 0 returns empty list."""
        result = await service._get_downstream_items("item-1", set(), 0)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_downstream_no_links(self, service):
        """Test downstream with no links."""
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service._get_downstream_items("item-1", set(), 1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_downstream_skips_visited(self, service):
        """Test that already visited items are skipped."""
        link = Mock(target_item_id="already-visited")
        service.links.get_by_source = AsyncMock(return_value=[link])

        visited = {"item-1", "already-visited"}
        result = await service._get_downstream_items("item-1", visited, 1)

        # Should skip already-visited
        assert result == []

    @pytest.mark.asyncio
    async def test_get_downstream_recursive(self, service):
        """Test recursive downstream traversal."""
        item1 = Mock(id="child-1")
        item2 = Mock(id="grandchild-1")

        link1 = Mock(target_item_id="child-1")
        link2 = Mock(target_item_id="grandchild-1")

        async def get_links(item_id):
            if item_id == "root":
                return [link1]
            elif item_id == "child-1":
                return [link2]
            return []

        service.links.get_by_source = AsyncMock(side_effect=get_links)

        async def get_item(item_id):
            if item_id == "child-1":
                return item1
            elif item_id == "grandchild-1":
                return item2
            return None

        service.items.get_by_id = AsyncMock(side_effect=get_item)

        visited = {"root"}
        result = await service._get_downstream_items("root", visited, 2)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_downstream_handles_missing_items(self, service):
        """Test handling of links to non-existent items."""
        link = Mock(target_item_id="missing")
        service.links.get_by_source = AsyncMock(return_value=[link])
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service._get_downstream_items("item-1", set(), 1)

        # Missing item should not be in result
        assert result == []
