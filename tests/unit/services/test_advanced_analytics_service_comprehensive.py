"""
Comprehensive tests for AdvancedAnalyticsService.

Tests all methods: project_metrics, team_analytics, trend_analysis,
dependency_metrics, quality_metrics, generate_report.

Coverage target: 85%+
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from tracertm.services.advanced_analytics_service import AdvancedAnalyticsService


class TestProjectMetrics:
    """Test project_metrics method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = AdvancedAnalyticsService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_empty_project(self, service):
        """Test metrics for empty project."""
        service.items.query = AsyncMock(return_value=[])

        result = await service.project_metrics("proj-1")

        assert result["project_id"] == "proj-1"
        assert result["total_items"] == 0
        assert result["by_status"] == {}
        assert result["by_view"] == {}
        assert result["completion_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_project_with_items(self, service):
        """Test metrics with items."""
        item1 = Mock()
        item1.status = "done"
        item1.view = "REQ"

        item2 = Mock()
        item2.status = "in_progress"
        item2.view = "REQ"

        item3 = Mock()
        item3.status = "todo"
        item3.view = "DEV"

        service.items.query = AsyncMock(return_value=[item1, item2, item3])

        result = await service.project_metrics("proj-1")

        assert result["total_items"] == 3
        assert result["by_status"]["done"] == 1
        assert result["by_status"]["in_progress"] == 1
        assert result["by_status"]["todo"] == 1
        assert result["by_view"]["REQ"] == 2
        assert result["by_view"]["DEV"] == 1

    @pytest.mark.asyncio
    async def test_completion_rate_calculation(self, service):
        """Test completion rate is calculated correctly."""
        items = []
        for _ in range(3):
            item = Mock()
            item.status = "done"
            item.view = "REQ"
            items.append(item)

        for _ in range(7):
            item = Mock()
            item.status = "todo"
            item.view = "REQ"
            items.append(item)

        service.items.query = AsyncMock(return_value=items)

        result = await service.project_metrics("proj-1")

        assert result["completion_rate"] == 30.0  # 3 done out of 10

    @pytest.mark.asyncio
    async def test_item_without_status_attribute(self, service):
        """Test handling item without status attribute."""
        item = Mock(spec=[])  # No attributes

        service.items.query = AsyncMock(return_value=[item])

        result = await service.project_metrics("proj-1")

        assert result["by_status"]["unknown"] == 1


class TestTeamAnalytics:
    """Test team_analytics method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = AdvancedAnalyticsService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_no_events(self, service):
        """Test analytics with no events."""
        service.events.get_by_project = AsyncMock(return_value=[])

        result = await service.team_analytics("proj-1")

        assert result["project_id"] == "proj-1"
        assert result["total_agents"] == 0
        assert result["agent_activity"] == {}
        assert result["total_events"] == 0

    @pytest.mark.asyncio
    async def test_events_with_agents(self, service):
        """Test analytics with agent events."""
        event1 = Mock()
        event1.agent_id = "agent-1"

        event2 = Mock()
        event2.agent_id = "agent-1"

        event3 = Mock()
        event3.agent_id = "agent-2"

        service.events.get_by_project = AsyncMock(return_value=[event1, event2, event3])

        result = await service.team_analytics("proj-1")

        assert result["total_agents"] == 2
        assert result["agent_activity"]["agent-1"] == 2
        assert result["agent_activity"]["agent-2"] == 1
        assert result["total_events"] == 3

    @pytest.mark.asyncio
    async def test_event_without_agent_id(self, service):
        """Test handling event without agent_id."""
        event = Mock(spec=[])  # No attributes

        service.events.get_by_project = AsyncMock(return_value=[event])

        result = await service.team_analytics("proj-1")

        assert result["agent_activity"]["unknown"] == 1


class TestTrendAnalysis:
    """Test trend_analysis method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = AdvancedAnalyticsService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_empty_events(self, service):
        """Test trends with no events."""
        service.items.query = AsyncMock(return_value=[])
        service.events.get_by_project = AsyncMock(return_value=[])

        result = await service.trend_analysis("proj-1", days=30)

        assert result["project_id"] == "proj-1"
        assert result["days"] == 30
        assert result["daily_events"] == {}
        assert result["total_events"] == 0

    @pytest.mark.asyncio
    async def test_events_grouped_by_day(self, service):
        """Test events are grouped by day."""
        now = datetime.utcnow()

        event1 = Mock()
        event1.created_at = now

        event2 = Mock()
        event2.created_at = now

        event3 = Mock()
        event3.created_at = now - timedelta(days=1)

        service.items.query = AsyncMock(return_value=[])
        service.events.get_by_project = AsyncMock(return_value=[event1, event2, event3])

        result = await service.trend_analysis("proj-1", days=7)

        assert len(result["daily_events"]) >= 1
        assert result["total_events"] == 3

    @pytest.mark.asyncio
    async def test_events_outside_window_excluded(self, service):
        """Test events outside time window are excluded."""
        old_event = Mock()
        old_event.created_at = datetime.utcnow() - timedelta(days=60)

        service.items.query = AsyncMock(return_value=[])
        service.events.get_by_project = AsyncMock(return_value=[old_event])

        result = await service.trend_analysis("proj-1", days=30)

        # Old event outside 30-day window should be excluded from daily_events
        assert result["daily_events"] == {}

    @pytest.mark.asyncio
    async def test_average_daily_events(self, service):
        """Test average daily events calculation."""
        events = [Mock(created_at=datetime.utcnow()) for _ in range(14)]

        service.items.query = AsyncMock(return_value=[])
        service.events.get_by_project = AsyncMock(return_value=events)

        result = await service.trend_analysis("proj-1", days=7)

        assert result["average_daily_events"] == 2.0  # 14 events / 7 days

    @pytest.mark.asyncio
    async def test_zero_days_no_division_error(self, service):
        """Test zero days doesn't cause division error."""
        service.items.query = AsyncMock(return_value=[])
        service.events.get_by_project = AsyncMock(return_value=[])

        result = await service.trend_analysis("proj-1", days=0)

        assert result["average_daily_events"] == 0


class TestDependencyMetrics:
    """Test dependency_metrics method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = AdvancedAnalyticsService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_no_items(self, service):
        """Test metrics with no items."""
        service.items.query = AsyncMock(return_value=[])

        result = await service.dependency_metrics("proj-1")

        assert result["project_id"] == "proj-1"
        assert result["total_links"] == 0
        assert result["total_items"] == 0
        assert result["average_links_per_item"] == 0
        assert result["link_types"] == {}

    @pytest.mark.asyncio
    async def test_items_with_links(self, service):
        """Test metrics with linked items."""
        link1 = Mock()
        link1.link_type = "depends_on"

        link2 = Mock()
        link2.link_type = "depends_on"

        link3 = Mock()
        link3.link_type = "relates_to"

        item = Mock()
        item.outgoing_links = [link1, link2, link3]

        service.items.query = AsyncMock(return_value=[item])

        result = await service.dependency_metrics("proj-1")

        assert result["total_links"] == 3
        assert result["link_types"]["depends_on"] == 2
        assert result["link_types"]["relates_to"] == 1
        assert result["average_links_per_item"] == 3.0

    @pytest.mark.asyncio
    async def test_items_without_links(self, service):
        """Test handling items without outgoing_links attribute."""
        item = Mock(spec=["id"])  # No outgoing_links

        service.items.query = AsyncMock(return_value=[item])

        result = await service.dependency_metrics("proj-1")

        assert result["total_links"] == 0


class TestQualityMetrics:
    """Test quality_metrics method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = AdvancedAnalyticsService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_no_items(self, service):
        """Test metrics with no items."""
        service.items.query = AsyncMock(return_value=[])

        result = await service.quality_metrics("proj-1")

        assert result["project_id"] == "proj-1"
        assert result["total_items"] == 0
        assert result["description_coverage"] == 0
        assert result["link_coverage"] == 0

    @pytest.mark.asyncio
    async def test_items_with_descriptions(self, service):
        """Test metrics for items with descriptions."""
        item1 = Mock()
        item1.description = "Has description"
        item1.outgoing_links = []

        item2 = Mock()
        item2.description = ""
        item2.outgoing_links = []

        item3 = Mock()
        item3.description = None
        item3.outgoing_links = []

        service.items.query = AsyncMock(return_value=[item1, item2, item3])

        result = await service.quality_metrics("proj-1")

        assert result["items_with_description"] == 1
        assert result["description_coverage"] == pytest.approx(33.33, rel=0.1)

    @pytest.mark.asyncio
    async def test_items_with_links(self, service):
        """Test metrics for items with links."""
        item1 = Mock()
        item1.description = ""
        item1.outgoing_links = [Mock()]

        item2 = Mock()
        item2.description = ""
        item2.outgoing_links = []

        service.items.query = AsyncMock(return_value=[item1, item2])

        result = await service.quality_metrics("proj-1")

        assert result["items_with_links"] == 1
        assert result["link_coverage"] == 50.0

    @pytest.mark.asyncio
    async def test_full_coverage(self, service):
        """Test 100% coverage metrics."""
        item = Mock()
        item.description = "Full description"
        item.outgoing_links = [Mock()]

        service.items.query = AsyncMock(return_value=[item])

        result = await service.quality_metrics("proj-1")

        assert result["description_coverage"] == 100.0
        assert result["link_coverage"] == 100.0


class TestGenerateReport:
    """Test generate_report method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = AdvancedAnalyticsService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_report_structure(self, service):
        """Test report has all sections."""
        service.items.query = AsyncMock(return_value=[])
        service.events.get_by_project = AsyncMock(return_value=[])

        result = await service.generate_report("proj-1")

        assert result["project_id"] == "proj-1"
        assert "generated_at" in result
        assert "project_metrics" in result
        assert "team_analytics" in result
        assert "trend_analysis" in result
        assert "dependency_metrics" in result
        assert "quality_metrics" in result

    @pytest.mark.asyncio
    async def test_report_generated_at_is_iso_format(self, service):
        """Test generated_at is ISO format string."""
        service.items.query = AsyncMock(return_value=[])
        service.events.get_by_project = AsyncMock(return_value=[])

        result = await service.generate_report("proj-1")

        # Should be parseable as ISO datetime
        datetime.fromisoformat(result["generated_at"])


class TestCalculateCompletionRate:
    """Test _calculate_completion_rate method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return AdvancedAnalyticsService(session)

    def test_empty_counts(self, service):
        """Test with empty status counts."""
        result = service._calculate_completion_rate({})
        assert result == 0.0

    def test_all_done(self, service):
        """Test with all items done."""
        result = service._calculate_completion_rate({"done": 10})
        assert result == 100.0

    def test_all_complete(self, service):
        """Test with all items complete."""
        result = service._calculate_completion_rate({"complete": 5})
        assert result == 100.0

    def test_mixed_statuses(self, service):
        """Test with mixed statuses."""
        result = service._calculate_completion_rate({
            "done": 2,
            "complete": 3,
            "todo": 5,
        })
        assert result == 50.0  # 5 out of 10

    def test_no_completed_items(self, service):
        """Test with no completed items."""
        result = service._calculate_completion_rate({
            "todo": 5,
            "in_progress": 3,
        })
        assert result == 0.0


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_repositories(self):
        """Test initialization creates repositories."""
        session = AsyncMock()
        service = AdvancedAnalyticsService(session)

        assert service.session == session
        assert service.items is not None
        assert service.links is not None
        assert service.events is not None
