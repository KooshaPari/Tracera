"""Advanced tests for CycleDetectionService - push to 85%+ coverage."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.cycle_detection_service import CycleDetectionService



@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_complex_graph():
    """Test detecting cycles in complex graph."""
    # Create mock repositories
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    # Create a complex graph with multiple cycles
    mock_links = [
        MagicMock(source_item_id="item1", target_item_id="item2", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item2", target_item_id="item3", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item3", target_item_id="item1", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item3", target_item_id="item4", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item4", target_item_id="item5", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item5", target_item_id="item3", link_type="depends_on", project_id="proj1"),
    ]

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert result.has_cycles is True
    assert result.cycle_count >= 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_self_loop():
    """Test detecting self-loop cycle."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    mock_links = [
        MagicMock(source_item_id="item1", target_item_id="item1", link_type="depends_on", project_id="proj1"),
    ]

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert result.has_cycles is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_multiple_link_types():
    """Test detecting cycles with multiple link types."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    # Only depends_on creates cycles in current implementation
    mock_links = [
        MagicMock(source_item_id="item1", target_item_id="item2", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item2", target_item_id="item1", link_type="depends_on", project_id="proj1"),
    ]

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert hasattr(result, 'has_cycles')
    assert result.has_cycles is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_disconnected_components():
    """Test detecting cycles in disconnected graph components."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    # Two separate cycles
    mock_links = [
        MagicMock(source_item_id="item1", target_item_id="item2", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item2", target_item_id="item1", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item4", target_item_id="item5", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item5", target_item_id="item6", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item6", target_item_id="item4", link_type="depends_on", project_id="proj1"),
    ]

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert result.has_cycles is True
    assert result.cycle_count >= 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_large_graph():
    """Test detecting cycles in large graph."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    # Create a large graph with cycle
    mock_links = [
        MagicMock(source_item_id=f"item{i}", target_item_id=f"item{i + 1}", link_type="depends_on", project_id="proj1")
        for i in range(1, 19)
    ]
    # Add cycle at the end
    mock_links.append(
        MagicMock(source_item_id="item19", target_item_id="item1", link_type="depends_on", project_id="proj1")
    )

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert result.has_cycles is True
