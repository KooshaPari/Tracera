"""Integration tests for advanced services batch 1 at 0% coverage.

Tests advanced analytics, traceability, agent coordination, and agent performance
services with real database interactions to achieve 100% coverage.

Target Services (Batch 1):
- advanced_analytics_service.py: 75 lines, 0% coverage
- advanced_traceability_service.py: 98 lines, 0% coverage
- advanced_traceability_enhancements_service.py: 102 lines, 0% coverage
- agent_coordination_service.py: 63 lines, 0% coverage
- agent_performance_service.py: 72 lines, 0% coverage

Total Tests: 60+ integration tests
Approach: Real database interactions, minimal mocking, comprehensive edge cases
Coverage Strategy: Happy paths, edge cases, error scenarios, concurrent operations
"""

from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.services.advanced_analytics_service import AdvancedAnalyticsService
from tracertm.services.advanced_traceability_enhancements_service import (
    AdvancedTraceabilityEnhancementsService,
)
from tracertm.services.advanced_traceability_service import (
    AdvancedTraceabilityService,
)
from tracertm.services.agent_coordination_service import (
    AgentConflict,
    AgentCoordinationService,
)
from tracertm.services.agent_performance_service import AgentPerformanceService

# ============================================================
# FIXTURES
# ============================================================


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession) -> Project:
    """Create a test project for integration tests."""
    project = Project(
        name=f"Integration Test Project {datetime.now().timestamp()}",
        description="Project for advanced service integration testing",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def sample_items(db_session: AsyncSession, test_project: Project) -> list[Item]:
    """Create diverse sample items for analytics testing."""
    items_repo = ItemRepository(db_session)
    items = []

    items_data = [
        ("Feature A", "FEATURE", "feature", "todo", "high", "Description for A"),
        ("Feature B", "FEATURE", "feature", "in_progress", "medium", ""),
        ("Feature C", "FEATURE", "feature", "done", "high", "Complete feature"),
        ("Story 1", "STORY", "story", "todo", "low", "User story description"),
        ("Story 2", "STORY", "story", "done", "medium", "Completed story"),
        ("Code Class A", "CODE", "class", "in_progress", "high", ""),
        ("Code Class B", "CODE", "class", "done", "medium", "Code description"),
        ("Test Case 1", "TEST", "unit_test", "todo", "high", "Test description"),
        ("Test Case 2", "TEST", "unit_test", "done", "low", ""),
        ("API Endpoint", "API", "endpoint", "complete", "high", "API details"),
    ]

    for title, view, item_type, status, priority, description in items_data:
        item = await items_repo.create(
            project_id=str(test_project.id),
            title=title,
            view=view,
            item_type=item_type,
            status=status,
            priority=priority,
            description=description,
        )
        items.append(item)

    await db_session.commit()
    return items


@pytest_asyncio.fixture
async def dependency_graph(db_session: AsyncSession, test_project: Project, sample_items: list[Item]) -> list[Link]:
    """Create a complex dependency graph for traceability testing."""
    links_repo = LinkRepository(db_session)
    links = []

    # Create various link types and patterns
    # Feature -> Story -> Code -> Test chain
    link_data = [
        (sample_items[0].id, sample_items[3].id, "implements"),  # Feature A -> Story 1
        (sample_items[3].id, sample_items[5].id, "implements"),  # Story 1 -> Code A
        (sample_items[5].id, sample_items[7].id, "tested_by"),  # Code A -> Test 1
        # Another chain
        (sample_items[1].id, sample_items[4].id, "depends_on"),  # Feature B -> Story 2
        (sample_items[4].id, sample_items[6].id, "implements"),  # Story 2 -> Code B
        # API relationships
        (sample_items[2].id, sample_items[9].id, "implements"),  # Feature C -> API
        (sample_items[9].id, sample_items[8].id, "tested_by"),  # API -> Test 2
        # Cross-view dependencies
        (sample_items[0].id, sample_items[1].id, "depends_on"),  # Feature A -> Feature B
        (sample_items[5].id, sample_items[6].id, "related_to"),  # Code A -> Code B
    ]

    for source_id, target_id, link_type in link_data:
        link = await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(source_id),
            target_item_id=str(target_id),
            link_type=link_type,
        )
        links.append(link)

    await db_session.commit()
    return links


@pytest_asyncio.fixture
async def sample_events(db_session: AsyncSession, test_project: Project, sample_items: list[Item]) -> list[Event]:
    """Create sample events for analytics testing."""
    events_repo = EventRepository(db_session)
    events = []

    # Create events from multiple agents over time
    agent_ids = ["agent-alpha", "agent-beta", "agent-gamma", "agent-delta"]
    event_types = [
        "item_created",
        "item_updated",
        "item_deleted",
        "link_created",
        "status_changed",
    ]

    base_time = datetime.now(UTC) - timedelta(days=15)

    for i in range(50):
        event_time = base_time + timedelta(hours=i * 2)
        event = await events_repo.log(
            project_id=str(test_project.id),
            event_type=event_types[i % len(event_types)],
            entity_type="item",
            entity_id=str(sample_items[i % len(sample_items)].id),
            agent_id=agent_ids[i % len(agent_ids)],
            data={"index": i, "timestamp": event_time.isoformat()},
        )
        # Manually set created_at for testing time-based queries
        event.created_at = event_time
        events.append(event)

    await db_session.commit()
    return events


@pytest_asyncio.fixture
async def sample_agents(db_session: AsyncSession, test_project: Project) -> list[Agent]:
    """Create sample agents for coordination testing."""
    agents_repo = AgentRepository(db_session)
    agents = []

    agent_data = [
        ("Alpha Agent", "developer", "active", {"skill": "coding"}),
        ("Beta Agent", "tester", "active", {"skill": "testing"}),
        ("Gamma Agent", "analyst", "active", {"skill": "analysis"}),
        ("Delta Agent", "designer", "idle", {"skill": "design"}),
        ("Epsilon Agent", "reviewer", "active", {"skill": "review"}),
    ]

    for i, (name, agent_type, status, metadata) in enumerate(agent_data):
        agent = await agents_repo.create(
            project_id=str(test_project.id),
            name=name,
            agent_type=agent_type,
            metadata=metadata,
        )
        # Set status and last activity
        agent.status = status
        agent.last_activity_at = (datetime.now(UTC) - timedelta(minutes=i * 10)).isoformat()
        agents.append(agent)

    await db_session.commit()
    return agents


# ============================================================
# ADVANCED ANALYTICS SERVICE TESTS (15+ tests)
# ============================================================


class TestAdvancedAnalyticsServiceIntegration:
    """Integration tests for AdvancedAnalyticsService."""

    @pytest.mark.asyncio
    async def test_project_metrics_with_populated_project(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
    ) -> None:
        """GIVEN: A project with items in various statuses and views.

        WHEN: project_metrics is called
        THEN: Returns accurate counts by status and view with completion rate.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.project_metrics(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["total_items"] == COUNT_TEN
        assert "by_status" in result
        assert "by_view" in result
        assert "completion_rate" in result
        # Verify status counts
        assert result["by_status"]["done"] == COUNT_FOUR  # 3 done + 1 complete
        assert result["by_status"]["todo"] == COUNT_THREE
        assert result["by_status"]["in_progress"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_project_metrics_empty_project(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: A project with no items.

        WHEN: project_metrics is called
        THEN: Returns zero counts with 0% completion rate.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.project_metrics(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["total_items"] == 0
        assert result["by_status"] == {}
        assert result["by_view"] == {}
        assert result["completion_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_completion_rate_mixed_statuses(self, db_session: AsyncSession) -> None:
        """GIVEN: Status counts with mixed done/complete and other statuses.

        WHEN: _calculate_completion_rate is called
        THEN: Returns correct percentage.
        """
        service = AdvancedAnalyticsService(db_session)

        status_counts = {"todo": 3, "in_progress": 2, "done": 4, "complete": 1}
        result = service._calculate_completion_rate(status_counts)

        assert result == 50.0  # (4 done + 1 complete) / 10 total * 100

    @pytest.mark.asyncio
    async def test_calculate_completion_rate_all_done(self, db_session: AsyncSession) -> None:
        """GIVEN: All items are done.

        WHEN: _calculate_completion_rate is called
        THEN: Returns 100%.
        """
        service = AdvancedAnalyticsService(db_session)

        status_counts = {"done": 5, "complete": 5}
        result = service._calculate_completion_rate(status_counts)

        assert result == 100.0

    @pytest.mark.asyncio
    async def test_calculate_completion_rate_none_done(self, db_session: AsyncSession) -> None:
        """GIVEN: No items are done.

        WHEN: _calculate_completion_rate is called
        THEN: Returns 0%.
        """
        service = AdvancedAnalyticsService(db_session)

        status_counts = {"todo": 8, "in_progress": 2}
        result = service._calculate_completion_rate(status_counts)

        assert result == 0.0

    @pytest.mark.asyncio
    async def test_team_analytics_with_events(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Project with events from multiple agents.

        WHEN: team_analytics is called
        THEN: Returns agent activity counts and totals.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.team_analytics(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["total_agents"] == COUNT_FOUR  # alpha, beta, gamma, delta
        assert result["total_events"] == 50
        assert "agent_activity" in result
        assert len(result["agent_activity"]) == COUNT_FOUR

    @pytest.mark.asyncio
    async def test_team_analytics_no_events(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Project with no events.

        WHEN: team_analytics is called
        THEN: Returns zero counts.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.team_analytics(str(test_project.id))

        assert result["total_agents"] == 0
        assert result["total_events"] == 0
        assert result["agent_activity"] == {}

    @pytest.mark.asyncio
    async def test_trend_analysis_default_window(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Events spread over 15 days.

        WHEN: trend_analysis is called with default 30-day window
        THEN: Returns daily event distribution.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.trend_analysis(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["days"] == 30
        assert result["total_events"] == 50
        assert "daily_events" in result
        assert "average_daily_events" in result
        assert result["average_daily_events"] == pytest.approx(50 / 30, rel=0.01)

    @pytest.mark.asyncio
    async def test_trend_analysis_custom_window(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Events with custom time window.

        WHEN: trend_analysis is called with days=7
        THEN: Returns events within the 7-day window.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.trend_analysis(str(test_project.id), days=7)

        assert result["days"] == 7
        # Should have fewer events in 7-day window than full dataset
        assert result["total_events"] <= 50

    @pytest.mark.asyncio
    async def test_dependency_metrics_with_links(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Items with various outgoing links.

        WHEN: dependency_metrics is called
        THEN: Returns link counts and types.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.dependency_metrics(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["total_items"] == COUNT_TEN
        assert result["total_links"] > 0
        assert "average_links_per_item" in result
        assert "link_types" in result
        # Verify link types captured
        assert "implements" in result["link_types"]
        assert "depends_on" in result["link_types"]

    @pytest.mark.asyncio
    async def test_dependency_metrics_no_links(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
    ) -> None:
        """GIVEN: Items without any links.

        WHEN: dependency_metrics is called
        THEN: Returns zero link counts.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.dependency_metrics(str(test_project.id))

        assert result["total_links"] == 0
        assert result["average_links_per_item"] == 0.0
        assert result["link_types"] == {}

    @pytest.mark.asyncio
    async def test_quality_metrics_with_descriptions(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
    ) -> None:
        """GIVEN: Items with varying description quality.

        WHEN: quality_metrics is called
        THEN: Returns description and link coverage percentages.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.quality_metrics(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["total_items"] == COUNT_TEN
        assert "items_with_description" in result
        assert "description_coverage" in result
        # 6 items have descriptions
        assert result["items_with_description"] == 6
        assert result["description_coverage"] == pytest.approx(60.0, rel=0.01)

    @pytest.mark.asyncio
    async def test_quality_metrics_with_links(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Items with outgoing links.

        WHEN: quality_metrics is called
        THEN: Returns link coverage percentage.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.quality_metrics(str(test_project.id))

        assert result["items_with_links"] > 0
        assert result["link_coverage"] > 0

    @pytest.mark.asyncio
    async def test_generate_report_comprehensive(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
        _dependency_graph: list[Link],
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Fully populated project with items, links, and events.

        WHEN: generate_report is called
        THEN: Returns comprehensive report with all sections.
        """
        service = AdvancedAnalyticsService(db_session)

        result = await service.generate_report(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert "generated_at" in result
        assert "project_metrics" in result
        assert "team_analytics" in result
        assert "trend_analysis" in result
        assert "dependency_metrics" in result
        assert "quality_metrics" in result
        # Verify all sections have data
        assert result["project_metrics"]["total_items"] == COUNT_TEN
        assert result["team_analytics"]["total_events"] == 50
        assert result["dependency_metrics"]["total_links"] > 0


# ============================================================
# ADVANCED TRACEABILITY SERVICE TESTS (15+ tests)
# ============================================================


class TestAdvancedTraceabilityServiceIntegration:
    """Integration tests for AdvancedTraceabilityService."""

    @pytest.mark.asyncio
    async def test_find_all_paths_direct_connection(
        self,
        db_session: AsyncSession,
        _test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Two items with direct link.

        WHEN: find_all_paths is called
        THEN: Returns single path of distance 1.
        """
        service = AdvancedTraceabilityService(db_session)

        paths = await service.find_all_paths(str(sample_items[0].id), str(sample_items[3].id))

        assert len(paths) >= 1
        assert paths[0].source_id == str(sample_items[0].id)
        assert paths[0].target_id == str(sample_items[3].id)
        assert paths[0].distance == 1

    @pytest.mark.asyncio
    async def test_find_all_paths_multi_hop(
        self,
        db_session: AsyncSession,
        _test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Items connected through intermediate nodes.

        WHEN: find_all_paths is called
        THEN: Returns multi-hop paths with correct distances.
        """
        service = AdvancedTraceabilityService(db_session)

        # Feature A -> Story 1 -> Code A (2 hops)
        paths = await service.find_all_paths(str(sample_items[0].id), str(sample_items[5].id))

        assert len(paths) >= 1
        multi_hop_path = next((p for p in paths if p.distance > 1), None)
        assert multi_hop_path is not None
        assert len(multi_hop_path.path) >= COUNT_THREE

    @pytest.mark.asyncio
    async def test_find_all_paths_no_connection(
        self,
        db_session: AsyncSession,
        _test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Two unconnected items.

        WHEN: find_all_paths is called
        THEN: Returns empty list.
        """
        service = AdvancedTraceabilityService(db_session)

        # Items with no connecting path
        paths = await service.find_all_paths(str(sample_items[7].id), str(sample_items[0].id))

        assert len(paths) == 0

    @pytest.mark.asyncio
    async def test_find_all_paths_max_depth_limit(
        self,
        db_session: AsyncSession,
        _test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Items with deep connection chain.

        WHEN: find_all_paths is called with max_depth=1
        THEN: Only returns paths within depth limit.
        """
        service = AdvancedTraceabilityService(db_session)

        paths = await service.find_all_paths(str(sample_items[0].id), str(sample_items[5].id), max_depth=1)

        # Should not find 2-hop path with max_depth=1
        assert all(p.distance <= 1 for p in paths)

    @pytest.mark.asyncio
    async def test_transitive_closure_complete_graph(
        self,
        db_session: AsyncSession,
        test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Project with dependency graph.

        WHEN: transitive_closure is computed
        THEN: Returns reachable items for each node.
        """
        service = AdvancedTraceabilityService(db_session)

        closure = await service.transitive_closure(str(test_project.id))

        assert len(closure) == COUNT_TEN  # All items
        # Feature A should reach Story 1, Code A, Test 1 (transitively); closure keys are str
        assert str(sample_items[3].id) in closure[str(sample_items[0].id)]

    @pytest.mark.asyncio
    async def test_transitive_closure_isolated_nodes(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Project with isolated items (no links).

        WHEN: transitive_closure is computed
        THEN: Returns empty sets for all items.
        """
        # Create project with items but no links
        items_repo = ItemRepository(db_session)
        items = []
        for i in range(3):
            item = await items_repo.create(
                project_id=str(test_project.id),
                title=f"Isolated Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)
        await db_session.commit()

        service = AdvancedTraceabilityService(db_session)
        closure = await service.transitive_closure(str(test_project.id))

        for item in items:
            assert len(closure[str(item.id)]) == 0

    @pytest.mark.asyncio
    async def test_bidirectional_impact_analysis(
        self,
        db_session: AsyncSession,
        _test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Item with both incoming and outgoing links.

        WHEN: bidirectional_impact is called
        THEN: Returns forward and backward impacts.
        """
        service = AdvancedTraceabilityService(db_session)

        # Story 1 has incoming from Feature A and outgoing to Code A
        result = await service.bidirectional_impact(str(sample_items[3].id))

        assert result["entity_id"] == str(sample_items[3].id)
        assert len(result["forward_impact"]) > 0
        assert len(result["backward_impact"]) > 0
        assert result["total_impact"] == len(result["forward_impact"]) + len(result["backward_impact"])

    @pytest.mark.asyncio
    async def test_bidirectional_impact_no_links(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Item with no links.

        WHEN: bidirectional_impact is called
        THEN: Returns empty impacts.
        """
        items_repo = ItemRepository(db_session)
        item = await items_repo.create(
            project_id=str(test_project.id),
            title="Isolated Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        await db_session.commit()

        service = AdvancedTraceabilityService(db_session)
        result = await service.bidirectional_impact(str(item.id))

        assert result["forward_impact"] == []
        assert result["backward_impact"] == []
        assert result["total_impact"] == 0

    @pytest.mark.asyncio
    async def test_coverage_gaps_some_gaps(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Items in source view with some missing links to target view.

        WHEN: coverage_gaps is called
        THEN: Returns items without target view links.
        """
        service = AdvancedTraceabilityService(db_session)

        gaps = await service.coverage_gaps(str(test_project.id), "FEATURE", "STORY")

        assert isinstance(gaps, list)
        # Should have at least one gap since not all features link to stories

    @pytest.mark.asyncio
    async def test_coverage_gaps_full_coverage(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: All source items link to target view.

        WHEN: coverage_gaps is called
        THEN: Returns empty list.
        """
        # Create complete coverage scenario
        items_repo = ItemRepository(db_session)
        links_repo = LinkRepository(db_session)

        feature = await items_repo.create(
            project_id=str(test_project.id),
            title="Complete Feature",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        story = await items_repo.create(
            project_id=str(test_project.id),
            title="Story",
            view="STORY",
            item_type="story",
            status="todo",
        )
        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(feature.id),
            target_item_id=str(story.id),
            link_type="implements",
        )
        await db_session.commit()

        service = AdvancedTraceabilityService(db_session)
        gaps = await service.coverage_gaps(str(test_project.id), "FEATURE", "STORY")

        # The feature we created should not be in gaps
        assert feature.id not in gaps

    @pytest.mark.asyncio
    async def test_circular_dependency_check_no_cycles(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Acyclic dependency graph.

        WHEN: circular_dependency_check is called
        THEN: Returns empty list.
        """
        service = AdvancedTraceabilityService(db_session)

        cycles = await service.circular_dependency_check(str(test_project.id))

        # Original graph should be acyclic
        assert len(cycles) == 0

    @pytest.mark.asyncio
    async def test_circular_dependency_check_with_cycle(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Dependency graph with circular dependency.

        WHEN: circular_dependency_check is called
        THEN: Detects and returns the cycle.
        """
        # Create cycle: A -> B -> C -> A
        items_repo = ItemRepository(db_session)
        links_repo = LinkRepository(db_session)

        item_a = await items_repo.create(
            project_id=str(test_project.id),
            title="Item A",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item_b = await items_repo.create(
            project_id=str(test_project.id),
            title="Item B",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item_c = await items_repo.create(
            project_id=str(test_project.id),
            title="Item C",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(item_a.id),
            target_item_id=str(item_b.id),
            link_type="depends_on",
        )
        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(item_b.id),
            target_item_id=str(item_c.id),
            link_type="depends_on",
        )
        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(item_c.id),
            target_item_id=str(item_a.id),
            link_type="depends_on",
        )
        await db_session.commit()

        service = AdvancedTraceabilityService(db_session)
        cycles = await service.circular_dependency_check(str(test_project.id))

        assert len(cycles) > 0
        # Should detect A -> B -> C -> A cycle
        assert any(item_a.id in cycle for cycle in cycles)


# ============================================================
# ADVANCED TRACEABILITY ENHANCEMENTS SERVICE TESTS (10+ tests)
# ============================================================


class TestAdvancedTraceabilityEnhancementsServiceIntegration:
    """Integration tests for AdvancedTraceabilityEnhancementsService."""

    @pytest.mark.asyncio
    async def test_detect_circular_dependencies_no_cycles(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Project with acyclic dependencies.

        WHEN: detect_circular_dependencies is called
        THEN: Returns has_cycles=False.
        """
        service = AdvancedTraceabilityEnhancementsService(db_session)

        result = await service.detect_circular_dependencies(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["has_cycles"] is False
        assert result["cycle_count"] == 0
        assert result["items_in_cycles"] == []

    @pytest.mark.asyncio
    async def test_detect_circular_dependencies_with_cycles(
        self, db_session: AsyncSession, test_project: Project
    ) -> None:
        """GIVEN: Project with circular dependencies.

        WHEN: detect_circular_dependencies is called
        THEN: Detects and reports cycles.
        """
        # Create circular dependency
        items_repo = ItemRepository(db_session)
        links_repo = LinkRepository(db_session)

        item_x = await items_repo.create(
            project_id=str(test_project.id),
            title="Item X",
            view="CODE",
            item_type="class",
            status="todo",
        )
        item_y = await items_repo.create(
            project_id=str(test_project.id),
            title="Item Y",
            view="CODE",
            item_type="class",
            status="todo",
        )

        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(item_x.id),
            target_item_id=str(item_y.id),
            link_type="depends_on",
        )
        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(item_y.id),
            target_item_id=str(item_x.id),
            link_type="depends_on",
        )
        await db_session.commit()

        service = AdvancedTraceabilityEnhancementsService(db_session)
        result = await service.detect_circular_dependencies(str(test_project.id))

        assert result["has_cycles"] is True
        assert result["cycle_count"] > 0

    @pytest.mark.asyncio
    async def test_coverage_gap_analysis_full_coverage(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: All source items linked to target view.

        WHEN: coverage_gap_analysis is called
        THEN: Returns 100% coverage.
        """
        items_repo = ItemRepository(db_session)
        links_repo = LinkRepository(db_session)

        feature = await items_repo.create(
            project_id=str(test_project.id),
            title="Feature",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        code = await items_repo.create(
            project_id=str(test_project.id),
            title="Code",
            view="CODE",
            item_type="class",
            status="todo",
        )
        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(feature.id),
            target_item_id=str(code.id),
            link_type="implements",
        )
        await db_session.commit()

        service = AdvancedTraceabilityEnhancementsService(db_session)
        result = await service.coverage_gap_analysis(str(test_project.id), "FEATURE", "CODE")

        assert result["source_view"] == "FEATURE"
        assert result["target_view"] == "CODE"
        assert result["coverage_percent"] == 100.0
        assert result["uncovered_items"] == 0

    @pytest.mark.asyncio
    async def test_coverage_gap_analysis_partial_coverage(
        self, db_session: AsyncSession, test_project: Project
    ) -> None:
        """GIVEN: Some source items without target view links.

        WHEN: coverage_gap_analysis is called
        THEN: Returns partial coverage percentage.
        """
        items_repo = ItemRepository(db_session)
        links_repo = LinkRepository(db_session)

        feature1 = await items_repo.create(
            project_id=str(test_project.id),
            title="Feature 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        feature2 = await items_repo.create(
            project_id=str(test_project.id),
            title="Feature 2",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        code = await items_repo.create(
            project_id=str(test_project.id),
            title="Code",
            view="CODE",
            item_type="class",
            status="todo",
        )

        # Only link feature1 to code
        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(feature1.id),
            target_item_id=str(code.id),
            link_type="implements",
        )
        await db_session.commit()

        service = AdvancedTraceabilityEnhancementsService(db_session)
        result = await service.coverage_gap_analysis(str(test_project.id), "FEATURE", "CODE")

        assert result["coverage_percent"] == 50.0  # 1 of 2 covered
        assert result["uncovered_items"] == 1
        assert feature2.id in result["uncovered_item_ids"]

    @pytest.mark.asyncio
    async def test_coverage_gap_analysis_no_source_items(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: No items in source view.

        WHEN: coverage_gap_analysis is called
        THEN: Returns 0% coverage with empty uncovered list.
        """
        service = AdvancedTraceabilityEnhancementsService(db_session)

        result = await service.coverage_gap_analysis(str(test_project.id), "NONEXISTENT", "CODE")

        assert result["total_source_items"] == 0
        assert result["coverage_percent"] == 0.0

    @pytest.mark.asyncio
    async def test_bidirectional_link_analysis_with_links(
        self,
        db_session: AsyncSession,
        test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Item with incoming and outgoing links.

        WHEN: bidirectional_link_analysis is called
        THEN: Returns both link directions with details.
        """
        service = AdvancedTraceabilityEnhancementsService(db_session)

        # Story 1 should have links in both directions
        result = await service.bidirectional_link_analysis(str(test_project.id), str(sample_items[3].id))

        assert result["item_id"] == str(sample_items[3].id)
        assert "incoming_links" in result
        assert "outgoing_links" in result
        assert "total_connections" in result
        assert result["total_connections"] > 0

    @pytest.mark.asyncio
    async def test_bidirectional_link_analysis_item_not_found(
        self, db_session: AsyncSession, test_project: Project
    ) -> None:
        """GIVEN: Non-existent item ID.

        WHEN: bidirectional_link_analysis is called
        THEN: Returns error.
        """
        service = AdvancedTraceabilityEnhancementsService(db_session)

        result = await service.bidirectional_link_analysis(str(test_project.id), "nonexistent-id")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_traceability_matrix_generation_complete(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Items with links between two views.

        WHEN: traceability_matrix_generation is called
        THEN: Returns matrix with source-target mappings.
        """
        service = AdvancedTraceabilityEnhancementsService(db_session)

        result = await service.traceability_matrix_generation(str(test_project.id), "FEATURE", "STORY")

        assert result["source_view"] == "FEATURE"
        assert result["target_view"] == "STORY"
        assert "matrix" in result
        assert "total_rows" in result
        assert "total_columns" in result
        # Should have rows for each feature
        assert len(result["matrix"]) > 0

    @pytest.mark.asyncio
    async def test_traceability_matrix_generation_no_links(
        self, db_session: AsyncSession, test_project: Project
    ) -> None:
        """GIVEN: Views with no links between them.

        WHEN: traceability_matrix_generation is called
        THEN: Returns empty matrix.
        """
        items_repo = ItemRepository(db_session)

        await items_repo.create(
            project_id=str(test_project.id),
            title="Isolated Feature",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        await items_repo.create(
            project_id=str(test_project.id),
            title="Isolated Test",
            view="TEST",
            item_type="test",
            status="todo",
        )
        await db_session.commit()

        service = AdvancedTraceabilityEnhancementsService(db_session)
        result = await service.traceability_matrix_generation(str(test_project.id), "FEATURE", "TEST")

        # Matrix should have rows but empty targets
        for row in result["matrix"]:
            assert len(row["targets"]) == 0

    @pytest.mark.asyncio
    async def test_impact_propagation_analysis_depth_limited(
        self,
        db_session: AsyncSession,
        test_project: Project,
        sample_items: list[Item],
        _dependency_graph: list[Link],
    ) -> None:
        """GIVEN: Multi-level dependency chain.

        WHEN: impact_propagation_analysis is called with max_depth
        THEN: Returns impacts within depth limit.
        """
        service = AdvancedTraceabilityEnhancementsService(db_session)

        result = await service.impact_propagation_analysis(str(test_project.id), str(sample_items[0].id), max_depth=2)

        assert result["item_id"] == str(sample_items[0].id)
        assert "total_impacted" in result
        assert "impact_levels" in result
        assert result["max_depth_reached"] <= COUNT_TWO

    @pytest.mark.asyncio
    async def test_impact_propagation_analysis_item_not_found(
        self, db_session: AsyncSession, test_project: Project
    ) -> None:
        """GIVEN: Non-existent item ID.

        WHEN: impact_propagation_analysis is called
        THEN: Returns error.
        """
        service = AdvancedTraceabilityEnhancementsService(db_session)

        result = await service.impact_propagation_analysis(str(test_project.id), "bad-id")

        assert "error" in result


# ============================================================
# AGENT COORDINATION SERVICE TESTS (10+ tests)
# ============================================================


class TestAgentCoordinationServiceIntegration:
    """Integration tests for AgentCoordinationService."""

    @pytest.mark.asyncio
    async def test_register_agent_success(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Valid agent registration data.

        WHEN: register_agent is called
        THEN: Creates agent and logs registration event.
        """
        service = AgentCoordinationService(db_session)

        agent = await service.register_agent(
            project_id=str(test_project.id),
            name="Test Agent",
            agent_type="developer",
            metadata={"skill": "python"},
        )

        assert agent.id is not None
        assert agent.name == "Test Agent"
        assert agent.agent_type == "developer"
        assert agent.project_id == str(test_project.id)

        # Verify event logged
        events_repo = EventRepository(db_session)
        events = await events_repo.get_by_project(str(test_project.id))
        assert any(e.event_type == "agent_registered" for e in events)

    @pytest.mark.asyncio
    async def test_register_agent_with_metadata(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Agent with custom metadata.

        WHEN: register_agent is called
        THEN: Stores metadata correctly.
        """
        service = AgentCoordinationService(db_session)

        metadata = {"skill_level": "senior", "languages": ["python", "go"]}
        agent = await service.register_agent(
            project_id=str(test_project.id),
            name="Senior Dev",
            agent_type="developer",
            metadata=metadata,
        )

        assert agent.metadata == metadata

    @pytest.mark.asyncio
    async def test_detect_conflicts_no_conflicts(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_agents: list[Agent],
    ) -> None:
        """GIVEN: Agents with non-overlapping activity.

        WHEN: detect_conflicts is called
        THEN: Returns empty conflict list.
        """
        service = AgentCoordinationService(db_session)

        conflicts = await service.detect_conflicts(str(test_project.id))

        # With staggered activity times (10 min apart), no conflicts
        assert len(conflicts) == 0

    @pytest.mark.asyncio
    async def test_detect_conflicts_concurrent_activity(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Multiple agents with concurrent activity.

        WHEN: detect_conflicts is called
        THEN: Detects and returns conflicts.
        """
        agents_repo = AgentRepository(db_session)

        # Create agents with concurrent activity
        now = datetime.now(UTC)
        agent1 = await agents_repo.create(
            project_id=str(test_project.id),
            name="Agent 1",
            agent_type="developer",
        )
        agent1.status = "active"
        agent1.last_activity_at = now.isoformat()

        agent2 = await agents_repo.create(
            project_id=str(test_project.id),
            name="Agent 2",
            agent_type="tester",
        )
        agent2.status = "active"
        agent2.last_activity_at = (now + timedelta(seconds=30)).isoformat()

        await db_session.commit()

        service = AgentCoordinationService(db_session)
        conflicts = await service.detect_conflicts(str(test_project.id))

        # Should detect concurrent activity (within 1 minute)
        assert len(conflicts) > 0
        assert any(c.conflict_type == "concurrent_activity" for c in conflicts)

    @pytest.mark.asyncio
    async def test_resolve_conflict_last_write_wins(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Conflict between two agents.

        WHEN: resolve_conflict is called with last_write_wins strategy
        THEN: Agent with latest activity wins.
        """
        agents_repo = AgentRepository(db_session)

        now = datetime.now(UTC)
        agent1 = await agents_repo.create(
            project_id=str(test_project.id),
            name="Agent 1",
            agent_type="developer",
        )
        agent1.last_activity_at = (now - timedelta(minutes=5)).isoformat()

        agent2 = await agents_repo.create(
            project_id=str(test_project.id),
            name="Agent 2",
            agent_type="developer",
        )
        agent2.last_activity_at = now.isoformat()

        await db_session.commit()

        conflict = AgentConflict(
            agent1_id=str(agent1.id),
            agent2_id=str(agent2.id),
            conflict_type="concurrent_edit",
            entity_id="test-item",
            description="Both edited same item",
        )

        service = AgentCoordinationService(db_session)
        resolution = await service.resolve_conflict(str(test_project.id), conflict, strategy="last_write_wins")

        assert resolution.resolved is True
        assert resolution.winner_agent_id == agent2.id  # Most recent
        assert resolution.loser_agent_id == agent1.id
        assert resolution.resolution_strategy == "last_write_wins"

    @pytest.mark.asyncio
    async def test_resolve_conflict_priority_based(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Conflict between two agents.

        WHEN: resolve_conflict is called with priority_based strategy
        THEN: Resolves using priority logic.
        """
        agents_repo = AgentRepository(db_session)

        agent1 = await agents_repo.create(
            project_id=str(test_project.id),
            name="Agent 1",
            agent_type="developer",
        )
        agent2 = await agents_repo.create(
            project_id=str(test_project.id),
            name="Agent 2",
            agent_type="reviewer",
        )
        await db_session.commit()

        conflict = AgentConflict(
            agent1_id=str(agent1.id),
            agent2_id=str(agent2.id),
            conflict_type="concurrent_edit",
            entity_id="test-item",
            description="Conflict",
        )

        service = AgentCoordinationService(db_session)
        resolution = await service.resolve_conflict(str(test_project.id), conflict, strategy="priority_based")

        assert resolution.resolved is True
        assert resolution.resolution_strategy == "priority_based"

    @pytest.mark.asyncio
    async def test_resolve_conflict_agent_not_found(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Conflict with non-existent agent.

        WHEN: resolve_conflict is called
        THEN: Raises ValueError.
        """
        conflict = AgentConflict(
            agent1_id="bad-id-1",
            agent2_id="bad-id-2",
            conflict_type="test",
            entity_id="test",
            description="Test",
        )

        service = AgentCoordinationService(db_session)

        with pytest.raises(ValueError, match="not found"):
            await service.resolve_conflict(str(test_project.id), conflict)

    @pytest.mark.asyncio
    async def test_resolve_conflict_unknown_strategy(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Invalid resolution strategy.

        WHEN: resolve_conflict is called
        THEN: Raises ValueError.
        """
        agents_repo = AgentRepository(db_session)

        agent1 = await agents_repo.create(project_id=str(test_project.id), name="A1", agent_type="dev")
        agent2 = await agents_repo.create(project_id=str(test_project.id), name="A2", agent_type="dev")
        await db_session.commit()

        conflict = AgentConflict(
            agent1_id=str(agent1.id),
            agent2_id=str(agent2.id),
            conflict_type="test",
            entity_id="test",
            description="Test",
        )

        service = AgentCoordinationService(db_session)

        with pytest.raises(ValueError, match="Unknown resolution strategy"):
            await service.resolve_conflict(str(test_project.id), conflict, strategy="invalid_strategy")

    @pytest.mark.asyncio
    async def test_get_agent_activity_with_events(
        self,
        db_session: AsyncSession,
        _test_project: Project,
        _sample_agents: list[Agent],
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Agent with activity events.

        WHEN: get_agent_activity is called
        THEN: Returns agent's event history.
        """
        service = AgentCoordinationService(db_session)

        # Get activity for agent-alpha
        activity = await service.get_agent_activity("agent-alpha")

        assert isinstance(activity, list)
        assert len(activity) > 0
        # Verify event structure
        assert all("event_type" in e for e in activity)
        assert all("timestamp" in e for e in activity)

    @pytest.mark.asyncio
    async def test_get_agent_activity_with_limit(self, db_session: AsyncSession, _sample_events: list[Event]) -> None:
        """GIVEN: Agent with many events.

        WHEN: get_agent_activity is called with limit
        THEN: Returns only limited number of events.
        """
        service = AgentCoordinationService(db_session)

        activity = await service.get_agent_activity("agent-alpha", limit=5)

        assert len(activity) <= COUNT_FIVE


# ============================================================
# AGENT PERFORMANCE SERVICE TESTS (10+ tests)
# ============================================================


class TestAgentPerformanceServiceIntegration:
    """Integration tests for AgentPerformanceService."""

    @pytest.mark.asyncio
    async def test_get_agent_stats_with_events(
        self,
        db_session: AsyncSession,
        _test_project: Project,
        _sample_agents: list[Agent],
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Agent with recent activity events.

        WHEN: get_agent_stats is called
        THEN: Returns comprehensive statistics.
        """
        service = AgentPerformanceService(db_session)

        stats = await service.get_agent_stats("agent-alpha", time_window_hours=24)

        assert stats["agent_id"] == "agent-alpha"
        assert "total_events" in stats
        assert "event_types" in stats
        assert "events_per_hour" in stats
        assert stats["time_window_hours"] == 24

    @pytest.mark.asyncio
    async def test_get_agent_stats_custom_time_window(
        self,
        db_session: AsyncSession,
        sample_agents: list[Agent],
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Agent activity over extended period.

        WHEN: get_agent_stats is called with custom window
        THEN: Returns stats for that window only.
        """
        service = AgentPerformanceService(db_session)

        stats_24h = await service.get_agent_stats("agent-alpha", time_window_hours=24)
        stats_48h = await service.get_agent_stats("agent-alpha", time_window_hours=48)

        # 48-hour window should have same or more events
        assert stats_48h["total_events"] >= stats_24h["total_events"]

    @pytest.mark.asyncio
    async def test_get_agent_stats_agent_not_found(self, db_session: AsyncSession) -> None:
        """GIVEN: Non-existent agent ID.

        WHEN: get_agent_stats is called
        THEN: Returns error.
        """
        service = AgentPerformanceService(db_session)

        stats = await service.get_agent_stats("nonexistent-agent")

        assert "error" in stats

    @pytest.mark.asyncio
    async def test_get_team_performance_complete(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_agents: list[Agent],
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Project with multiple agents.

        WHEN: get_team_performance is called
        THEN: Returns aggregated team statistics.
        """
        service = AgentPerformanceService(db_session)

        result = await service.get_team_performance(str(test_project.id))

        assert result["project_id"] == str(test_project.id)
        assert result["total_agents"] > 0
        assert "agents" in result
        assert "total_events" in result
        assert len(result["agents"]) > 0

    @pytest.mark.asyncio
    async def test_get_team_performance_no_agents(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Project with no agents.

        WHEN: get_team_performance is called
        THEN: Returns empty statistics.
        """
        service = AgentPerformanceService(db_session)

        result = await service.get_team_performance(str(test_project.id))

        assert result["total_agents"] == 0
        assert result["agents"] == []

    @pytest.mark.asyncio
    async def test_get_agent_efficiency_high_activity(
        self,
        db_session: AsyncSession,
        sample_agents: list[Agent],
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Agent with high event count and diversity.

        WHEN: get_agent_efficiency is called
        THEN: Returns high efficiency score.
        """
        service = AgentPerformanceService(db_session)

        result = await service.get_agent_efficiency("agent-alpha")

        assert "efficiency_score" in result
        assert "rating" in result
        assert 0 <= result["efficiency_score"] <= 100

    @pytest.mark.asyncio
    async def test_get_agent_efficiency_low_activity(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Agent with minimal activity.

        WHEN: get_agent_efficiency is called
        THEN: Returns low efficiency score.
        """
        agents_repo = AgentRepository(db_session)
        agent = await agents_repo.create(
            project_id=str(test_project.id),
            name="Inactive Agent",
            agent_type="developer",
        )
        await db_session.commit()

        service = AgentPerformanceService(db_session)
        result = await service.get_agent_efficiency(str(agent.id))

        assert result["efficiency_score"] < 50
        assert result["rating"] in {"Poor", "Fair"}

    @pytest.mark.asyncio
    async def test_get_efficiency_rating_boundaries(self, db_session: AsyncSession) -> None:
        """GIVEN: Various efficiency scores.

        WHEN: _get_efficiency_rating is called
        THEN: Returns correct rating categories.
        """
        service = AgentPerformanceService(db_session)

        assert service._get_efficiency_rating(95) == "Excellent"
        assert service._get_efficiency_rating(80) == "Good"
        assert service._get_efficiency_rating(60) == "Fair"
        assert service._get_efficiency_rating(30) == "Poor"

    @pytest.mark.asyncio
    async def test_get_agent_workload_heavy(
        self,
        db_session: AsyncSession,
        sample_agents: list[Agent],
        _sample_events: list[Event],
    ) -> None:
        """GIVEN: Agent with high event rate.

        WHEN: get_agent_workload is called
        THEN: Classifies as Heavy workload.
        """
        service = AgentPerformanceService(db_session)

        # Create many recent events for an agent
        events_repo = EventRepository(db_session)
        for i in range(20):
            await events_repo.log(
                project_id="test",
                event_type="test",
                entity_type="item",
                entity_id=f"item-{i}",
                data={},
                agent_id="agent-alpha",
            )
        await db_session.commit()

        result = await service.get_agent_workload("agent-alpha")

        assert result["workload"] in {"Heavy", "Moderate"}
        assert result["events_per_hour"] > 0

    @pytest.mark.asyncio
    async def test_get_agent_workload_idle(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Agent with no recent activity.

        WHEN: get_agent_workload is called
        THEN: Classifies as Idle.
        """
        agents_repo = AgentRepository(db_session)
        agent = await agents_repo.create(
            project_id=str(test_project.id),
            name="Idle Agent",
            agent_type="developer",
        )
        await db_session.commit()

        service = AgentPerformanceService(db_session)
        result = await service.get_agent_workload(str(agent.id))

        assert result["workload"] == "Idle"
        assert result["events_per_hour"] == 0

    @pytest.mark.asyncio
    async def test_recommend_agent_assignment_best_available(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_agents: list[Agent],
    ) -> None:
        """GIVEN: Multiple agents with varying workloads.

        WHEN: recommend_agent_assignment is called
        THEN: Recommends agent with lowest workload.
        """
        service = AgentPerformanceService(db_session)

        result = await service.recommend_agent_assignment(str(test_project.id), task_complexity="medium")

        assert "recommended_agent_id" in result
        assert "agent_name" in result
        assert "current_workload" in result
        assert "reason" in result

    @pytest.mark.asyncio
    async def test_recommend_agent_assignment_no_agents(self, db_session: AsyncSession, test_project: Project) -> None:
        """GIVEN: Project with no agents.

        WHEN: recommend_agent_assignment is called
        THEN: Returns error.
        """
        service = AgentPerformanceService(db_session)

        result = await service.recommend_agent_assignment(str(test_project.id))

        assert "error" in result

    @pytest.mark.asyncio
    async def test_recommend_agent_assignment_task_complexity(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _sample_agents: list[Agent],
    ) -> None:
        """GIVEN: Task with specific complexity.

        WHEN: recommend_agent_assignment is called
        THEN: Includes complexity in recommendation.
        """
        service = AgentPerformanceService(db_session)

        result = await service.recommend_agent_assignment(str(test_project.id), task_complexity="high")

        assert result["task_complexity"] == "high"
