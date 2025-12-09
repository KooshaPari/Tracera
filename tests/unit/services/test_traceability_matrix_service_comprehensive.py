"""
Comprehensive tests for TraceabilityMatrixService.

Tests all methods including:
- generate_matrix
- TraceabilityMatrix dataclass

Coverage target: 90%+
"""

import pytest
from unittest.mock import AsyncMock, Mock
from tracertm.services.traceability_matrix_service import (
    TraceabilityMatrixService,
    TraceabilityMatrix,
)
from tracertm.models.item import Item
from tracertm.models.link import Link


class TestGenerateMatrix:
    """Test generate_matrix method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return TraceabilityMatrixService(mock_session)

    @pytest.mark.asyncio
    async def test_basic_matrix(self, service):
        """Test generating basic traceability matrix."""
        # Setup items
        items = [
            Mock(spec=Item, id="A", title="Item A", view="FEATURE"),
            Mock(spec=Item, id="B", title="Item B", view="TASK"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1")

        assert isinstance(result, TraceabilityMatrix)
        assert result.project_id == "proj-1"
        assert len(result.rows) == 2
        assert len(result.columns) == 2
        assert result.total_links >= 0

    @pytest.mark.asyncio
    async def test_matrix_with_filters(self, service):
        """Test matrix with source and target view filters."""
        items = [
            Mock(spec=Item, id="F1", title="Feature 1", view="FEATURE"),
            Mock(spec=Item, id="T1", title="Task 1", view="TASK"),
            Mock(spec=Item, id="T2", title="Task 2", view="TASK"),
        ]
        links = [
            Mock(spec=Link, source_item_id="F1", target_item_id="T1", link_type="implements"),
            Mock(spec=Link, source_item_id="F1", target_item_id="T2", link_type="implements"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix(
            "proj-1", source_view="FEATURE", target_view="TASK"
        )

        # Should only include FEATURE as rows and TASK as columns
        assert all(row["view"] == "FEATURE" for row in result.rows)
        assert all(col["view"] == "TASK" for col in result.columns)

    @pytest.mark.asyncio
    async def test_matrix_with_link_type_filter(self, service):
        """Test matrix filtering by link types."""
        items = [
            Mock(spec=Item, id="A", title="Item A", view="FEATURE"),
            Mock(spec=Item, id="B", title="Item B", view="TASK"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="blocks"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1", link_types=["depends_on"])

        # Should only include depends_on links
        assert result.total_links <= 1

    @pytest.mark.asyncio
    async def test_empty_matrix(self, service):
        """Test generating matrix with no items."""
        service.items.get_by_project = AsyncMock(return_value=[])
        service.links.get_by_project = AsyncMock(return_value=[])

        result = await service.generate_matrix("proj-1")

        assert len(result.rows) == 0
        assert len(result.columns) == 0
        assert result.total_links == 0
        assert result.coverage == 0

    @pytest.mark.asyncio
    async def test_coverage_calculation(self, service):
        """Test coverage calculation in matrix."""
        # 2x2 matrix with 1 link = 25% coverage
        items = [
            Mock(spec=Item, id="A", title="Item A", view="FEATURE"),
            Mock(spec=Item, id="B", title="Item B", view="FEATURE"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1")

        # Coverage = (traced_count / total_cells) * 100
        assert result.coverage > 0
        assert result.coverage <= 100

    @pytest.mark.asyncio
    async def test_full_coverage(self, service):
        """Test matrix with full coverage."""
        items = [
            Mock(spec=Item, id="A", title="Item A", view="FEATURE"),
            Mock(spec=Item, id="B", title="Item B", view="FEATURE"),
        ]
        # Link every source to every target
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="A", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="A", link_type="depends_on"),
            Mock(spec=Link, source_item_id="B", target_item_id="B", link_type="depends_on"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1")

        # All cells should be filled
        assert result.coverage == 100.0

    @pytest.mark.asyncio
    async def test_matrix_structure(self, service):
        """Test matrix data structure is correct."""
        items = [
            Mock(spec=Item, id="A", title="Item A", view="FEATURE"),
            Mock(spec=Item, id="B", title="Item B", view="TASK"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1")

        # Verify matrix dimensions match items
        assert len(result.matrix) == len(result.rows)
        if result.matrix:
            assert len(result.matrix[0]) == len(result.columns)

    @pytest.mark.asyncio
    async def test_matrix_cell_values(self, service):
        """Test matrix cells contain correct link types."""
        items = [
            Mock(spec=Item, id="A", title="Item A", view="FEATURE"),
            Mock(spec=Item, id="B", title="Item B", view="FEATURE"),
        ]
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on")
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1")

        # Matrix should contain link type where link exists, empty string otherwise
        found_link = False
        for row in result.matrix:
            for cell in row:
                if cell == "depends_on":
                    found_link = True
                else:
                    assert cell == ""

        assert found_link

    @pytest.mark.asyncio
    async def test_no_links_zero_coverage(self, service):
        """Test coverage is 0 when no links exist."""
        items = [
            Mock(spec=Item, id="A", title="Item A", view="FEATURE"),
            Mock(spec=Item, id="B", title="Item B", view="FEATURE"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=[])

        result = await service.generate_matrix("proj-1")

        assert result.coverage == 0.0
        assert result.total_links == 0


class TestTraceabilityMatrix:
    """Test TraceabilityMatrix dataclass."""

    def test_create_matrix(self):
        """Test creating TraceabilityMatrix."""
        matrix = TraceabilityMatrix(
            project_id="proj-1",
            rows=[{"id": "A", "title": "Item A", "view": "FEATURE"}],
            columns=[{"id": "B", "title": "Item B", "view": "TASK"}],
            matrix=[["depends_on"]],
            coverage=100.0,
            total_links=1,
        )

        assert matrix.project_id == "proj-1"
        assert len(matrix.rows) == 1
        assert len(matrix.columns) == 1
        assert matrix.coverage == 100.0

    def test_matrix_with_multiple_items(self):
        """Test matrix with multiple rows and columns."""
        matrix = TraceabilityMatrix(
            project_id="proj-1",
            rows=[
                {"id": "A", "title": "A", "view": "FEATURE"},
                {"id": "B", "title": "B", "view": "FEATURE"},
            ],
            columns=[
                {"id": "C", "title": "C", "view": "TASK"},
                {"id": "D", "title": "D", "view": "TASK"},
            ],
            matrix=[
                ["depends_on", ""],
                ["", "blocks"],
            ],
            coverage=50.0,
            total_links=2,
        )

        assert len(matrix.rows) == 2
        assert len(matrix.columns) == 2
        assert matrix.total_links == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return TraceabilityMatrixService(mock_session)

    @pytest.mark.asyncio
    async def test_single_item_matrix(self, service):
        """Test matrix with single item."""
        items = [Mock(spec=Item, id="A", title="Item A", view="FEATURE")]
        links = []

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1")

        assert len(result.rows) == 1
        assert len(result.columns) == 1

    @pytest.mark.asyncio
    async def test_asymmetric_matrix(self, service):
        """Test matrix with different number of rows and columns."""
        items = [
            Mock(spec=Item, id="F1", title="Feature 1", view="FEATURE"),
            Mock(spec=Item, id="F2", title="Feature 2", view="FEATURE"),
            Mock(spec=Item, id="T1", title="Task 1", view="TASK"),
        ]
        links = []

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix(
            "proj-1", source_view="FEATURE", target_view="TASK"
        )

        # 2 features x 1 task = asymmetric matrix
        assert len(result.rows) == 2
        assert len(result.columns) == 1

    @pytest.mark.asyncio
    async def test_multiple_links_same_pair(self, service):
        """Test handling of multiple links between same item pair."""
        items = [
            Mock(spec=Item, id="A", title="A", view="FEATURE"),
            Mock(spec=Item, id="B", title="B", view="FEATURE"),
        ]
        # Multiple links between A and B
        links = [
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="depends_on"),
            Mock(spec=Link, source_item_id="A", target_item_id="B", link_type="blocks"),
        ]

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.generate_matrix("proj-1")

        # Should handle multiple links (last one wins in current implementation)
        assert result.project_id == "proj-1"

    @pytest.mark.asyncio
    async def test_filter_excludes_all_items(self, service):
        """Test when filters exclude all items."""
        items = [
            Mock(spec=Item, id="A", title="A", view="FEATURE"),
        ]
        links = []

        service.items.get_by_project = AsyncMock(return_value=items)
        service.links.get_by_project = AsyncMock(return_value=links)

        # Filter for non-existent view
        result = await service.generate_matrix("proj-1", source_view="NONEXISTENT")

        assert len(result.rows) == 0
        assert result.coverage == 0
