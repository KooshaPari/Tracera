"""
Gap coverage tests for core modules with low coverage.
Targets: core/concurrency.py, services/event_service.py
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime


class TestConcurrencyError:
    """Tests for ConcurrencyError exception."""

    def test_concurrency_error_import(self):
        """Test ConcurrencyError can be imported."""
        from tracertm.core.concurrency import ConcurrencyError
        assert ConcurrencyError is not None

    def test_concurrency_error_can_be_raised(self):
        """Test ConcurrencyError can be raised and caught."""
        from tracertm.core.concurrency import ConcurrencyError

        with pytest.raises(ConcurrencyError):
            raise ConcurrencyError("version mismatch")

    def test_concurrency_error_message(self):
        """Test ConcurrencyError preserves message."""
        from tracertm.core.concurrency import ConcurrencyError

        try:
            raise ConcurrencyError("test message")
        except ConcurrencyError as e:
            assert "test message" in str(e)


class TestUpdateWithRetry:
    """Tests for update_with_retry function."""

    @pytest.mark.asyncio
    async def test_update_with_retry_success_first_try(self):
        """Test update succeeds on first try."""
        from tracertm.core.concurrency import update_with_retry

        mock_fn = AsyncMock(return_value="success")

        result = await update_with_retry(mock_fn)

        assert result == "success"
        assert mock_fn.call_count == 1

    @pytest.mark.asyncio
    async def test_update_with_retry_success_after_retries(self):
        """Test update succeeds after retries."""
        from tracertm.core.concurrency import update_with_retry, ConcurrencyError

        call_count = 0

        async def flaky_fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConcurrencyError("version conflict")
            return "success"

        with patch("asyncio.sleep", new=AsyncMock()):
            result = await update_with_retry(flaky_fn, max_retries=3, base_delay=0.01)

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_update_with_retry_max_retries_exceeded(self):
        """Test raises after max retries exceeded."""
        from tracertm.core.concurrency import update_with_retry, ConcurrencyError

        async def always_fails():
            raise ConcurrencyError("always fails")

        with patch("asyncio.sleep", new=AsyncMock()):
            with pytest.raises(ConcurrencyError) as exc_info:
                await update_with_retry(always_fails, max_retries=3, base_delay=0.01)

        assert "Failed after 3 retries" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_with_retry_exponential_backoff(self):
        """Test exponential backoff is applied."""
        from tracertm.core.concurrency import update_with_retry, ConcurrencyError

        sleep_calls = []

        async def mock_sleep(duration):
            sleep_calls.append(duration)

        async def always_fails():
            raise ConcurrencyError("fail")

        with patch("asyncio.sleep", side_effect=mock_sleep):
            with pytest.raises(ConcurrencyError):
                await update_with_retry(always_fails, max_retries=3, base_delay=0.1)

        # Should have slept twice (before retry 2 and 3)
        assert len(sleep_calls) == 2
        # First sleep should be base_delay + jitter
        assert 0.1 <= sleep_calls[0] <= 0.12  # 0.1 + up to 10% jitter
        # Second sleep should be 2*base_delay + jitter
        assert 0.2 <= sleep_calls[1] <= 0.24


class TestEventService:
    """Tests for EventService."""

    def test_event_service_import(self):
        """Test EventService can be imported."""
        from tracertm.services.event_service import EventService
        assert EventService is not None

    def test_event_service_init(self):
        """Test EventService initialization."""
        from tracertm.services.event_service import EventService

        mock_session = MagicMock()
        service = EventService(mock_session)

        assert service.session == mock_session
        assert service.events is not None

    @pytest.mark.asyncio
    async def test_event_service_log_event_with_item(self):
        """Test log_event with item_id."""
        from tracertm.services.event_service import EventService

        mock_session = MagicMock()
        service = EventService(mock_session)

        mock_event = MagicMock()
        service.events.log = AsyncMock(return_value=mock_event)

        result = await service.log_event(
            project_id="project-1",
            event_type="item_created",
            event_data={"name": "Test Item"},
            agent_id="agent-1",
            item_id="item-1",
        )

        assert result == mock_event
        service.events.log.assert_called_once_with(
            project_id="project-1",
            event_type="item_created",
            entity_type="item",
            entity_id="item-1",
            data={"name": "Test Item"},
            agent_id="agent-1",
        )

    @pytest.mark.asyncio
    async def test_event_service_log_event_without_item(self):
        """Test log_event without item_id (project-level)."""
        from tracertm.services.event_service import EventService

        mock_session = MagicMock()
        service = EventService(mock_session)

        mock_event = MagicMock()
        service.events.log = AsyncMock(return_value=mock_event)

        result = await service.log_event(
            project_id="project-1",
            event_type="project_created",
            event_data={"name": "Test Project"},
            agent_id="agent-1",
        )

        service.events.log.assert_called_once_with(
            project_id="project-1",
            event_type="project_created",
            entity_type="project",
            entity_id="project-1",
            data={"name": "Test Project"},
            agent_id="agent-1",
        )

    @pytest.mark.asyncio
    async def test_event_service_get_item_history(self):
        """Test get_item_history method."""
        from tracertm.services.event_service import EventService

        mock_session = MagicMock()
        service = EventService(mock_session)

        mock_events = [MagicMock(), MagicMock()]
        service.events.get_by_entity = AsyncMock(return_value=mock_events)

        result = await service.get_item_history("item-1")

        assert result == mock_events
        service.events.get_by_entity.assert_called_once_with("item-1")

    @pytest.mark.asyncio
    async def test_event_service_get_item_at_time(self):
        """Test get_item_at_time method."""
        from tracertm.services.event_service import EventService

        mock_session = MagicMock()
        service = EventService(mock_session)

        mock_state = {"name": "Old Name"}
        service.events.get_entity_at_time = AsyncMock(return_value=mock_state)

        at_time = datetime(2024, 1, 1, 12, 0)
        result = await service.get_item_at_time("item-1", at_time)

        assert result == mock_state
        service.events.get_entity_at_time.assert_called_once_with("item-1", at_time)


class TestPerformanceOptimizationService:
    """Tests for PerformanceOptimizationService."""

    def test_performance_optimization_service_import(self):
        """Test PerformanceOptimizationService can be imported."""
        from tracertm.services.performance_optimization_service import PerformanceOptimizationService
        assert PerformanceOptimizationService is not None

    def test_performance_optimization_service_init(self):
        """Test PerformanceOptimizationService initialization."""
        from tracertm.services.performance_optimization_service import PerformanceOptimizationService

        mock_session = MagicMock()
        service = PerformanceOptimizationService(session=mock_session)
        assert service.session == mock_session
