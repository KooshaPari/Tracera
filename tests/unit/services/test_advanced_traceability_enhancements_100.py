"""100% coverage tests for AdvancedTraceabilityEnhancementsService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession



@pytest.fixture
def mock_session():
    """Create mock session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_item():
    """Create mock item."""
    item = MagicMock()
    item.id = "item1"
    item.title = "Test Item"
    item.view = "requirements"
    item.outgoing_links = []
    return item


@pytest.fixture
def mock_link():
    """Create mock link."""
    link = MagicMock()
    link.target_item_id = "item2"
    link.link_type = "depends_on"
    return link


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_circular_dependencies_no_cycles(mock_session, mock_item):
    """Test detecting circular dependencies with no cycles."""
    from tracertm.services.advanced_traceability_enhancements_service import (
        AdvancedTraceabilityEnhancementsService,
    )

    service = AdvancedTraceabilityEnhancementsService(mock_session)

    with patch.object(service.items, 'query', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = [mock_item]
        result = await service.detect_circular_dependencies("proj1")

        assert result["project_id"] == "proj1"
        assert result["has_cycles"] is False
        assert result["cycle_count"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_coverage_gap_analysis(mock_session, mock_item):
    """Test coverage gap analysis."""
    from tracertm.services.advanced_traceability_enhancements_service import (
        AdvancedTraceabilityEnhancementsService,
    )

    service = AdvancedTraceabilityEnhancementsService(mock_session)

    with patch.object(service.items, 'query', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = [mock_item]
        result = await service.coverage_gap_analysis("proj1", "requirements", "design")

        assert result["source_view"] == "requirements"
        assert result["target_view"] == "design"
        assert "coverage_percent" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_bidirectional_link_analysis_item_found(mock_session, mock_item, mock_link):
    """Test bidirectional link analysis when item is found."""
    from tracertm.services.advanced_traceability_enhancements_service import (
        AdvancedTraceabilityEnhancementsService,
    )

    service = AdvancedTraceabilityEnhancementsService(mock_session)
    mock_item.outgoing_links = [mock_link]

    with patch.object(service.items, 'get_by_id', new_callable=AsyncMock) as mock_get:
        with patch.object(service.items, 'query', new_callable=AsyncMock) as mock_query:
            mock_get.return_value = mock_item
            mock_query.return_value = [mock_item]
            result = await service.bidirectional_link_analysis("proj1", "item1")

            assert result["item_id"] == "item1"
            assert "incoming_links" in result
            assert "outgoing_links" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_bidirectional_link_analysis_item_not_found(mock_session):
    """Test bidirectional link analysis when item is not found."""
    from tracertm.services.advanced_traceability_enhancements_service import (
        AdvancedTraceabilityEnhancementsService,
    )

    service = AdvancedTraceabilityEnhancementsService(mock_session)

    with patch.object(service.items, 'get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        result = await service.bidirectional_link_analysis("proj1", "nonexistent")

        assert "error" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_traceability_matrix_generation(mock_session, mock_item, mock_link):
    """Test traceability matrix generation."""
    from tracertm.services.advanced_traceability_enhancements_service import (
        AdvancedTraceabilityEnhancementsService,
    )

    service = AdvancedTraceabilityEnhancementsService(mock_session)
    mock_item.outgoing_links = [mock_link]

    with patch.object(service.items, 'query', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = [mock_item]
        result = await service.traceability_matrix_generation("proj1", "requirements", "design")

        assert result["source_view"] == "requirements"
        assert result["target_view"] == "design"
        assert "matrix" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_impact_propagation_analysis(mock_session, mock_item):
    """Test impact propagation analysis."""
    from tracertm.services.advanced_traceability_enhancements_service import (
        AdvancedTraceabilityEnhancementsService,
    )

    service = AdvancedTraceabilityEnhancementsService(mock_session)

    with patch.object(service.items, 'get_by_id', new_callable=AsyncMock) as mock_get:
        with patch.object(service.items, 'query', new_callable=AsyncMock) as mock_query:
            mock_get.return_value = mock_item
            mock_query.return_value = [mock_item]
            result = await service.impact_propagation_analysis("proj1", "item1", max_depth=5)

            assert result["item_id"] == "item1"
            assert "total_impacted" in result
            assert "impact_levels" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_impact_propagation_analysis_item_not_found(mock_session):
    """Test impact propagation analysis when item not found."""
    from tracertm.services.advanced_traceability_enhancements_service import (
        AdvancedTraceabilityEnhancementsService,
    )

    service = AdvancedTraceabilityEnhancementsService(mock_session)

    with patch.object(service.items, 'get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        result = await service.impact_propagation_analysis("proj1", "nonexistent")

        assert "error" in result
