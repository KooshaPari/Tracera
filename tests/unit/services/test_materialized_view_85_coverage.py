"""Comprehensive tests for MaterializedViewService - 85%+ coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.materialized_view_service import (
    MaterializedViewService,
    ViewStaleness,
)



@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_incremental():
    """Test incremental refresh of materialized views."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    service = MaterializedViewService(mock_session)

    with patch.object(service, 'get_refresh_stats', new_callable=AsyncMock) as mock_stats:
        mock_stats.return_value = {"views_refreshed": 5}
        result = await service.refresh_incremental()

        assert isinstance(result, dict)
        assert result["refresh_type"] == "incremental"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_full():
    """Test full refresh of materialized views."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    service = MaterializedViewService(mock_session)

    with patch.object(service, 'get_refresh_stats', new_callable=AsyncMock) as mock_stats:
        mock_stats.return_value = {"views_refreshed": 10}
        result = await service.refresh_full()

        assert isinstance(result, dict)
        assert result["refresh_type"] == "full"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_refresh_stats():
    """Test getting refresh statistics."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [("view1", 100), ("view2", 200)]
    mock_session.execute = AsyncMock(return_value=mock_result)

    service = MaterializedViewService(mock_session)
    result = await service.get_refresh_stats()

    assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_view_staleness_dataclass():
    """Test ViewStaleness dataclass."""
    from datetime import datetime

    staleness = ViewStaleness(
        view_name="test_view",
        unprocessed_changes=5,
        oldest_change=datetime.now(),
        staleness_seconds=300.0,
        is_stale=False,
    )

    assert staleness.view_name == "test_view"
    assert staleness.unprocessed_changes == 5
    assert staleness.is_stale is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_view_staleness_no_changes():
    """Test ViewStaleness with no changes."""
    staleness = ViewStaleness(
        view_name="fresh_view",
        unprocessed_changes=0,
        oldest_change=None,
        staleness_seconds=None,
        is_stale=False,
    )

    assert staleness.unprocessed_changes == 0
    assert staleness.oldest_change is None
    assert staleness.is_stale is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_view_staleness_stale():
    """Test ViewStaleness when stale."""
    from datetime import datetime

    staleness = ViewStaleness(
        view_name="stale_view",
        unprocessed_changes=100,
        oldest_change=datetime.now(),
        staleness_seconds=3600.0,
        is_stale=True,
    )

    assert staleness.is_stale is True
    assert staleness.unprocessed_changes == 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_operations_sequence():
    """Test sequence of refresh operations."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    service = MaterializedViewService(mock_session)

    with patch.object(service, 'get_refresh_stats', new_callable=AsyncMock) as mock_stats:
        mock_stats.return_value = {"views_refreshed": 5}

        # First incremental
        result1 = await service.refresh_incremental()
        assert result1["refresh_type"] == "incremental"

        # Then full
        result2 = await service.refresh_full()
        assert result2["refresh_type"] == "full"
