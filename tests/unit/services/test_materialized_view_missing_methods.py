"""Tests for missing MaterializedViewService methods."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.materialized_view_service import MaterializedViewService



@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_staleness():
    """Test getting staleness information."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    service = MaterializedViewService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("view1", 10, None, 300.0)
        mock_execute.return_value = mock_result

        result = await service.get_staleness()

        assert result.view_name == "view1"
        assert result.unprocessed_changes == 10


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_staleness_empty():
    """Test getting staleness when no data."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    service = MaterializedViewService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_execute.return_value = mock_result

        result = await service.get_staleness()

        assert result.view_name == "materialized_views"
        assert result.unprocessed_changes == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cleanup_change_log():
    """Test cleaning up change log."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    service = MaterializedViewService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        with patch.object(mock_session, 'commit', new_callable=AsyncMock):
            mock_result = MagicMock()
            mock_result.scalar.return_value = 100
            mock_execute.return_value = mock_result

            result = await service.cleanup_change_log(days_to_keep=30)

            assert result == 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cleanup_change_log_zero_deleted():
    """Test cleanup when no entries deleted."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    service = MaterializedViewService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        with patch.object(mock_session, 'commit', new_callable=AsyncMock):
            mock_result = MagicMock()
            mock_result.scalar.return_value = 0
            mock_execute.return_value = mock_result

            result = await service.cleanup_change_log()

            assert result == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auto_refresh_if_stale_true():
    """Test auto refresh when stale."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    service = MaterializedViewService(mock_session)

    with patch.object(service, 'get_staleness', new_callable=AsyncMock) as mock_staleness:
        with patch.object(service, 'refresh_incremental', new_callable=AsyncMock):
            mock_staleness_obj = MagicMock()
            mock_staleness_obj.staleness_seconds = 10.0
            mock_staleness.return_value = mock_staleness_obj

            result = await service.auto_refresh_if_stale(max_staleness_seconds=5.0)

            assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auto_refresh_if_stale_false():
    """Test auto refresh when not stale."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    service = MaterializedViewService(mock_session)

    with patch.object(service, 'get_staleness', new_callable=AsyncMock) as mock_staleness:
        mock_staleness_obj = MagicMock()
        mock_staleness_obj.staleness_seconds = 2.0
        mock_staleness.return_value = mock_staleness_obj

        result = await service.auto_refresh_if_stale(max_staleness_seconds=5.0)

        assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auto_refresh_if_stale_none_staleness():
    """Test auto refresh when staleness is None."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    service = MaterializedViewService(mock_session)

    with patch.object(service, 'get_staleness', new_callable=AsyncMock) as mock_staleness:
        mock_staleness_obj = MagicMock()
        mock_staleness_obj.staleness_seconds = None
        mock_staleness.return_value = mock_staleness_obj

        result = await service.auto_refresh_if_stale()

        assert result is False
