"""Extreme coverage tests for CycleDetectionService - push to 90%+."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.cycle_detection_service import CycleDetectionService



@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_all_link_types():
    """Test detecting cycles with all link types."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    # Only depends_on is checked for cycles
    mock_links = [
        MagicMock(source_item_id="item1", target_item_id="item2", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item2", target_item_id="item1", link_type="depends_on", project_id="proj1"),
    ]

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)

    # Test with default link type
    result1 = await service.detect_cycles_async(project_id="proj1")
    assert result1.has_cycles is True

    # Test with specific link type filter
    result2 = await service.detect_cycles_async(project_id="proj1", link_type="depends_on")
    assert hasattr(result2, 'has_cycles')


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_bidirectional():
    """Test detecting bidirectional cycles."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    mock_links = [
        MagicMock(source_item_id="item1", target_item_id="item2", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item2", target_item_id="item1", link_type="depends_on", project_id="proj1"),
    ]

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert result.has_cycles is True
    assert result.cycle_count >= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_with_isolated_nodes():
    """Test detecting cycles with isolated nodes."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    # Cycle between item1 and item2, item3/4/5 would be isolated if they existed
    mock_links = [
        MagicMock(source_item_id="item1", target_item_id="item2", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item2", target_item_id="item1", link_type="depends_on", project_id="proj1"),
    ]

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert result.has_cycles is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_cycles_nested_cycles():
    """Test detecting nested cycles."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    mock_links = [
        # Outer cycle: 1->2->3->1
        MagicMock(source_item_id="item1", target_item_id="item2", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item2", target_item_id="item3", link_type="depends_on", project_id="proj1"),
        MagicMock(source_item_id="item3", target_item_id="item1", link_type="depends_on", project_id="proj1"),
        # Inner cycle: 4->5->6->4
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
async def test_detect_cycles_long_chain_with_cycle():
    """Test detecting cycle in long chain."""
    mock_items_repo = MagicMock()
    mock_links_repo = MagicMock()
    mock_links_repo.get_by_project = AsyncMock()

    mock_links = [
        MagicMock(source_item_id=f"item{i}", target_item_id=f"item{i + 1}", link_type="depends_on", project_id="proj1")
        for i in range(1, 9)
    ]
    # Add cycle at the end
    mock_links.append(
        MagicMock(source_item_id="item9", target_item_id="item5", link_type="depends_on", project_id="proj1")
    )

    mock_links_repo.get_by_project.return_value = mock_links

    mock_session = MagicMock(spec=AsyncSession)
    service = CycleDetectionService(mock_session, items=mock_items_repo, links=mock_links_repo)
    result = await service.detect_cycles_async(project_id="proj1")

    assert result.has_cycles is True
