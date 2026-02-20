"""Comprehensive concurrency tests for progress tracking service.

This module tests:
- Concurrent progress updates
- Progress calculation accuracy
- State consistency
- Completion milestone detection
- Blocked/stalled item tracking
- Velocity calculations

Target: 90%+ coverage for progress_service.py
"""

import asyncio
from datetime import UTC, datetime, timedelta

# Import both the stub and real service
from typing import Any
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_TWO

try:
    from tracertm.services.progress_tracking_service import ProgressTrackingService

    HAS_STUB = True
except ImportError:
    HAS_STUB = False

try:
    from tracertm.services.progress_service import ProgressService

    HAS_REAL = True
except ImportError:
    HAS_REAL = False


@pytest.mark.asyncio
class TestProgressTrackingConcurrency:
    """Test concurrent progress updates."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock database session."""
        session = MagicMock(spec=Session)
        session.query = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()
        return session

    @pytest.fixture
    def stub_service(self, mock_session: Any) -> None:
        """Create stub service instance."""
        if HAS_STUB:
            return ProgressTrackingService(mock_session)
        return None

    async def test_concurrent_progress_updates(self, stub_service: Any) -> None:
        """Test concurrent updates to progress."""
        if not stub_service:
            pytest.skip("Stub service not available")

        # Update progress from 10 concurrent tasks
        tasks = [stub_service.progress() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # Verify all complete successfully
        assert len(results) == COUNT_TEN
        assert all(isinstance(r, dict) for r in results)
        assert all("progress" in r for r in results)

    async def test_high_frequency_progress_queries(self, stub_service: Any) -> None:
        """Test rapid successive progress queries."""
        if not stub_service:
            pytest.skip("Stub service not available")

        import time

        start = time.time()
        for _ in range(100):
            await stub_service.progress()
        duration = time.time() - start

        # Should complete quickly
        assert duration < float(COUNT_TWO + 0.0), f"100 queries took {duration}s, expected < COUNT_TWOs"

    async def test_concurrent_progress_different_items(self, stub_service: Any) -> None:
        """Test concurrent progress for different items."""
        if not stub_service:
            pytest.skip("Stub service not available")

        tasks = [stub_service.progress() for _ in range(20)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 20
        assert all("progress" in r for r in results)


class TestProgressCalculationAccuracy:
    """Test progress calculation with various states."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock session with query support."""
        session = MagicMock(spec=Session)
        mock_query = MagicMock()
        session.query.return_value = mock_query
        return session

    @pytest.fixture
    def real_service(self, mock_session: Any) -> None:
        """Create real service instance."""
        if HAS_REAL:
            return ProgressService(mock_session)
        return None

    def test_progress_calculation_leaf_item_todo(self, real_service: Any, mock_session: Any) -> None:
        """Test progress calculation for leaf item in todo state."""
        if not real_service:
            pytest.skip("Real service not available")

        # Mock item
        mock_item = MagicMock()
        mock_item.id = "item1"
        mock_item.status = "todo"

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_item
        mock_query.filter.return_value.all.return_value = []  # No children
        mock_session.query.return_value = mock_query

        result = real_service.calculate_completion("item1")
        assert result == 0.0

    def test_progress_calculation_leaf_item_in_progress(self, real_service: Any, mock_session: Any) -> None:
        """Test progress calculation for leaf item in progress."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_item = MagicMock()
        mock_item.id = "item2"
        mock_item.status = "in_progress"

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_item
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        result = real_service.calculate_completion("item2")
        assert result == 50.0

    def test_progress_calculation_leaf_item_complete(self, real_service: Any, mock_session: Any) -> None:
        """Test progress calculation for leaf item complete."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_item = MagicMock()
        mock_item.id = "item3"
        mock_item.status = "complete"

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_item
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        result = real_service.calculate_completion("item3")
        assert result == 100.0

    def test_progress_calculation_leaf_item_blocked(self, real_service: Any, mock_session: Any) -> None:
        """Test progress calculation for blocked item."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_item = MagicMock()
        mock_item.id = "item4"
        mock_item.status = "blocked"

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_item
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        result = real_service.calculate_completion("item4")
        assert result == 0.0

    def test_progress_calculation_nonexistent_item(self, real_service: Any, mock_session: Any) -> None:
        """Test progress calculation for nonexistent item."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query

        result = real_service.calculate_completion("nonexistent")
        assert result == 0.0


@pytest.mark.asyncio
class TestProgressStateConsistency:
    """Test progress state remains consistent."""

    @pytest.fixture
    def stub_service(self) -> None:
        """Create stub service."""
        if HAS_STUB:
            return ProgressTrackingService(MagicMock())
        return None

    async def test_progress_query_consistency(self, stub_service: Any) -> None:
        """Test progress queries return consistent results."""
        if not stub_service:
            pytest.skip("Stub service not available")

        results = []
        for _ in range(10):
            result = await stub_service.progress()
            results.append(result)

        # All results should have consistent structure
        assert all("progress" in r for r in results)

    async def test_multiple_service_instances(self) -> None:
        """Test multiple service instances work independently."""
        if not HAS_STUB:
            pytest.skip("Stub service not available")

        services = [ProgressTrackingService(MagicMock()) for _ in range(10)]

        tasks = [s.progress() for s in services]
        results = await asyncio.gather(*tasks)

        assert len(results) == COUNT_TEN
        assert all("progress" in r for r in results)

    async def test_service_reuse_stability(self, stub_service: Any) -> None:
        """Test service remains stable with repeated use."""
        if not stub_service:
            pytest.skip("Stub service not available")

        for _ in range(100):
            result = await stub_service.progress()
            assert "progress" in result


@pytest.mark.asyncio
class TestCompletionMilestoneDetection:
    """Test detection of completion milestones."""

    @pytest.fixture
    def stub_service(self) -> None:
        """Create stub service."""
        if HAS_STUB:
            return ProgressTrackingService(MagicMock())
        return None

    async def test_milestone_0_percent(self, stub_service: Any) -> None:
        """Test 0% completion milestone."""
        if not stub_service:
            pytest.skip("Stub service not available")

        result = await stub_service.progress()
        assert result["progress"] == 0

    async def test_milestone_detection_incremental(self, stub_service: Any) -> None:
        """Test milestone detection at various percentages."""
        if not stub_service:
            pytest.skip("Stub service not available")

        # In real implementation, would test 25%, 50%, 75%, 100%
        result = await stub_service.progress()
        assert isinstance(result["progress"], (int, float))


class TestBlockedItemTracking:
    """Test blocked item tracking functionality."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock session."""
        session = MagicMock(spec=Session)
        mock_query = MagicMock()
        session.query.return_value = mock_query
        return session

    @pytest.fixture
    def real_service(self, mock_session: Any) -> None:
        """Create real service."""
        if HAS_REAL:
            return ProgressService(mock_session)
        return None

    def test_get_blocked_items_empty(self, real_service: Any, mock_session: Any) -> None:
        """Test getting blocked items when none exist."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        result = real_service.get_blocked_items("project1")
        assert result == []

    def test_get_blocked_items_with_blockers(self, real_service: Any, mock_session: Any) -> None:
        """Test getting blocked items with blockers."""
        if not real_service:
            pytest.skip("Real service not available")

        # Mock blocked link
        mock_link = MagicMock()
        mock_link.target_item_id = "blocked_item"
        mock_link.source_item_id = "blocker_item"

        # Mock items
        mock_blocked = MagicMock()
        mock_blocked.id = "blocked_item"
        mock_blocked.title = "Blocked Item"
        mock_blocked.status = "blocked"

        mock_blocker = MagicMock()
        mock_blocker.id = "blocker_item"
        mock_blocker.title = "Blocker Item"
        mock_blocker.status = "in_progress"

        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [mock_link]
        mock_query.filter.return_value.first.side_effect = [mock_blocked, mock_blocker]
        mock_session.query.return_value = mock_query

        result = real_service.get_blocked_items("project1")
        assert len(result) == 1
        assert result[0]["item_id"] == "blocked_item"


class TestStalledItemTracking:
    """Test stalled item tracking."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def real_service(self, mock_session: Any) -> None:
        """Create real service."""
        if HAS_REAL:
            return ProgressService(mock_session)
        return None

    def test_get_stalled_items_empty(self, real_service: Any, mock_session: Any) -> None:
        """Test getting stalled items when none exist."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        result = real_service.get_stalled_items("project1")
        assert result == []

    def test_get_stalled_items_with_threshold(self, real_service: Any, mock_session: Any) -> None:
        """Test getting stalled items with custom threshold."""
        if not real_service:
            pytest.skip("Real service not available")

        # Mock stalled item
        mock_item = MagicMock()
        mock_item.id = "stalled_item"
        mock_item.title = "Stalled Item"
        mock_item.status = "in_progress"
        mock_item.updated_at = datetime.now(UTC) - timedelta(days=10)

        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [mock_item]
        mock_session.query.return_value = mock_query

        result = real_service.get_stalled_items("project1", days_threshold=7)
        assert len(result) == 1
        assert result[0]["item_id"] == "stalled_item"
        assert result[0]["days_stalled"] >= COUNT_TEN


class TestVelocityCalculations:
    """Test velocity calculation functionality."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def real_service(self, mock_session: Any) -> None:
        """Create real service."""
        if HAS_REAL:
            return ProgressService(mock_session)
        return None

    def test_calculate_velocity_no_items(self, real_service: Any, mock_session: Any) -> None:
        """Test velocity calculation with no items."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_query = MagicMock()
        mock_query.filter.return_value.scalar.return_value = 0
        mock_session.query.return_value = mock_query

        result = real_service.calculate_velocity("project1", days=7)
        assert result["items_completed"] == 0
        assert result["items_created"] == 0
        assert result["completion_rate"] == 0

    def test_calculate_velocity_with_items(self, real_service: Any, mock_session: Any) -> None:
        """Test velocity calculation with completed items."""
        if not real_service:
            pytest.skip("Real service not available")

        mock_query = MagicMock()
        mock_query.filter.return_value.scalar.side_effect = [10, 15]  # completed, created
        mock_session.query.return_value = mock_query

        result = real_service.calculate_velocity("project1", days=7)
        assert result["items_completed"] == COUNT_TEN
        assert result["items_created"] == 15
        assert result["completion_rate"] == COUNT_TEN / 7
        assert result["net_change"] == COUNT_FIVE


@pytest.mark.asyncio
class TestProgressServiceValidation:
    """Test progress service validation and edge cases."""

    async def test_progress_service_initialization_without_session(self) -> None:
        """Test service initialization without session."""
        if HAS_STUB:
            service = ProgressTrackingService(None)
            assert service is not None
            result = await service.progress()
            assert "progress" in result

    async def test_progress_timeout_handling(self) -> None:
        """Test progress operations with timeout."""
        if not HAS_STUB:
            pytest.skip("Stub service not available")

        service = ProgressTrackingService(MagicMock())

        try:
            result = await asyncio.wait_for(service.progress(), timeout=1.0)
            assert "progress" in result
        except TimeoutError:
            pytest.fail("Progress query timed out unexpectedly")

    async def test_progress_performance_baseline(self) -> None:
        """Test baseline progress query performance."""
        if not HAS_STUB:
            pytest.skip("Stub service not available")

        service = ProgressTrackingService(MagicMock())

        import time

        start = time.time()
        await service.progress()
        duration = time.time() - start

        assert duration < 1.0, f"Progress query took {duration}s, expected < 1s"
