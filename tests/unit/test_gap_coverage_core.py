"""Gap coverage tests for core modules with low coverage.

Targets: core/concurrency.py, services/event_service.py.
"""

import asyncio
from datetime import datetime
from typing import Any, Never
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO


class TestConcurrencyError:
    """Tests for ConcurrencyError exception."""

    def test_concurrency_error_import(self) -> None:
        """Test ConcurrencyError can be imported."""
        from tracertm.core.concurrency import ConcurrencyError

        assert ConcurrencyError is not None

    def test_concurrency_error_can_be_raised(self) -> Never:
        """Test ConcurrencyError can be raised and caught."""
        from tracertm.core.concurrency import ConcurrencyError

        with pytest.raises(ConcurrencyError):
            msg = "version mismatch"
            raise ConcurrencyError(msg)

    def test_concurrency_error_message(self) -> Never:
        """Test ConcurrencyError preserves message."""
        from tracertm.core.concurrency import ConcurrencyError

        with pytest.raises(ConcurrencyError, match="test message"):
            msg = "test message"
            raise ConcurrencyError(msg)


class TestUpdateWithRetry:
    """Tests for update_with_retry function."""

    @pytest.mark.asyncio
    async def test_update_with_retry_success_first_try(self) -> None:
        """Test update succeeds on first try."""
        from tracertm.core.concurrency import update_with_retry

        mock_fn = AsyncMock(return_value="success")

        result = await update_with_retry(mock_fn)

        assert result == "success"
        assert mock_fn.call_count == 1

    @pytest.mark.asyncio
    async def test_update_with_retry_success_after_retries(self) -> None:
        """Test update succeeds after retries."""
        from tracertm.core.concurrency import ConcurrencyError, update_with_retry

        call_count = 0

        async def flaky_fn() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "version conflict"
                raise ConcurrencyError(msg)
            return "success"

        with patch("asyncio.sleep", new=AsyncMock()):
            result = await update_with_retry(flaky_fn, max_retries=3, base_delay=0.01)

        assert result == "success"
        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_update_with_retry_max_retries_exceeded(self) -> None:
        """Test raises after max retries exceeded."""
        from tracertm.core.concurrency import ConcurrencyError, update_with_retry

        async def always_fails() -> Never:
            await asyncio.sleep(0)
            msg = "always fails"
            raise ConcurrencyError(msg)

        with patch("asyncio.sleep", new=AsyncMock()), pytest.raises(ConcurrencyError) as exc_info:
            await update_with_retry(always_fails, max_retries=3, base_delay=0.01)

        assert "Failed after 3 retries" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_with_retry_exponential_backoff(self) -> None:
        """Test exponential backoff is applied."""
        from tracertm.core.concurrency import ConcurrencyError, update_with_retry

        sleep_calls = []

        async def mock_sleep(duration: Any) -> None:
            await asyncio.sleep(0)
            sleep_calls.append(duration)

        async def always_fails() -> Never:
            await asyncio.sleep(0)
            msg = "fail"
            raise ConcurrencyError(msg)

        with patch("asyncio.sleep", side_effect=mock_sleep), pytest.raises(ConcurrencyError):
            await update_with_retry(always_fails, max_retries=3, base_delay=0.1)

        # Should have slept twice (before retry 2 and 3)
        assert len(sleep_calls) == COUNT_TWO
        # First sleep should be base_delay + jitter
        assert 0.1 <= sleep_calls[0] <= 0.12  # 0.1 + up to 10% jitter
        # Second sleep should be 2*base_delay + jitter
        assert 0.2 <= sleep_calls[1] <= 0.24


class TestEventService:
    """Tests for EventService."""

    def test_event_service_import(self) -> None:
        """Test EventService can be imported."""
        from tracertm.services.event_service import EventService

        assert EventService is not None

    def test_event_service_init(self) -> None:
        """Test EventService initialization."""
        from tracertm.services.event_service import EventService

        mock_session = MagicMock()
        service = EventService(mock_session)

        assert service.session == mock_session
        assert service.events is not None

    @pytest.mark.asyncio
    async def test_event_service_log_event_with_item(self) -> None:
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
    async def test_event_service_log_event_without_item(self) -> None:
        """Test log_event without item_id (project-level)."""
        from tracertm.services.event_service import EventService

        mock_session = MagicMock()
        service = EventService(mock_session)

        mock_event = MagicMock()
        service.events.log = AsyncMock(return_value=mock_event)

        await service.log_event(
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
    async def test_event_service_get_item_history(self) -> None:
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
    async def test_event_service_get_item_at_time(self) -> None:
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

    def test_performance_optimization_service_import(self) -> None:
        """Test PerformanceOptimizationService can be imported."""
        from tracertm.services.performance_optimization_service import PerformanceOptimizationService

        assert PerformanceOptimizationService is not None

    def test_performance_optimization_service_init(self) -> None:
        """Test PerformanceOptimizationService initialization."""
        from tracertm.services.performance_optimization_service import PerformanceOptimizationService

        mock_session = MagicMock()
        service = PerformanceOptimizationService(session=mock_session)
        assert service.session == mock_session
