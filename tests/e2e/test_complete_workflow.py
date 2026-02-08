"""End-to-end tests for complete workflows."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_TWO
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.services.agent_coordination_service import AgentCoordinationService
from tracertm.services.bulk_service import BulkOperationService
from tracertm.services.event_sourcing_service import EventSourcingService
from tracertm.services.traceability_service import TraceabilityService


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_project_workflow(db_session: AsyncSession) -> None:
    """Test complete project workflow from creation to traceability."""
    # 1. Create project
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(
        name="E2E Test Project",
        description="Complete workflow test",
    )

    # 2. Create items
    item_repo = ItemRepository(db_session)
    feature = await item_repo.create(
        project_id=str(project.id),
        title="User Authentication",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    code = await item_repo.create(
        project_id=str(project.id),
        title="auth.py",
        view="CODE",
        item_type="file",
        status="todo",
    )

    test = await item_repo.create(
        project_id=str(project.id),
        title="test_auth.py",
        view="TEST",
        item_type="test",
        status="todo",
    )

    # 3. Create links
    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(feature.id),
        target_item_id=str(code.id),
        link_type="implements",
    )

    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(code.id),
        target_item_id=str(test.id),
        link_type="tests",
    )

    # 4. Generate traceability matrix
    traceability = TraceabilityService(db_session)
    matrix = await traceability.generate_matrix(str(project.id), "FEATURE", "CODE")

    assert matrix.coverage_percentage == 100.0
    assert len(matrix.links) == 1

    # 5. Analyze impact
    impact = await traceability.analyze_impact(str(feature.id))
    assert len(impact.directly_affected) == 1
    assert len(impact.indirectly_affected) == 1

    # 6. Update items
    updated_feature = await item_repo.update(
        item_id=str(feature.id),
        expected_version=feature.version,
        status="in_progress",
    )

    assert updated_feature.status == "in_progress"
    assert updated_feature.version == COUNT_TWO


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_bulk_operation_workflow(db_session: AsyncSession) -> None:
    """Test bulk operation workflow."""
    # 1. Create project with items
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Bulk Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    for i in range(5):
        await item_repo.create(
            project_id=str(project.id),
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

    # 2. Preview bulk update
    bulk_service = BulkOperationService(db_session)
    preview = await bulk_service.preview_bulk_update(
        project_id=str(project.id),
        filters={"status": "todo"},
        updates={"status": "in_progress"},
    )

    assert preview.total_count == COUNT_FIVE
    assert preview.is_safe()

    # 3. Execute bulk update
    updated = await bulk_service.execute_bulk_update(
        project_id=str(project.id),
        filters={"status": "todo"},
        updates={"status": "in_progress"},
        agent_id="test-agent",
        skip_preview=True,
    )

    assert len(updated) == COUNT_FIVE
    assert all(item.status == "in_progress" for item in updated)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_agent_coordination_workflow(db_session: AsyncSession) -> None:
    """Test agent coordination workflow."""
    # 1. Create project
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Agent Test Project", description="Test")

    # 2. Register agents
    agent_service = AgentCoordinationService(db_session)
    agent1 = await agent_service.register_agent(
        project_id=str(project.id),
        name="Agent-1",
        agent_type="cli",
    )

    agent2 = await agent_service.register_agent(
        project_id=str(project.id),
        name="Agent-2",
        agent_type="api",
    )

    assert agent1.status == "active"
    assert agent2.status == "active"

    # 3. Get agent activity
    activity1 = await agent_service.get_agent_activity(str(agent1.id))
    assert len(activity1) > 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_event_sourcing_workflow(db_session: AsyncSession) -> None:
    """Test event sourcing and audit trail workflow."""
    # 1. Create project and items
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Event Test Project", description="Test")

    event_repo = EventRepository(db_session)

    # 2. Log events
    await event_repo.log(
        project_id=str(project.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-1",
        data={"title": "Test Item", "status": "todo"},
    )

    await event_repo.log(
        project_id=str(project.id),
        event_type="item_updated",
        entity_type="item",
        entity_id="item-1",
        data={"status": "in_progress"},
    )

    # 3. Get audit trail
    sourcing = EventSourcingService(db_session)
    trail = await sourcing.get_audit_trail(str(project.id))
    assert len(trail) == COUNT_TWO

    # 4. Replay events
    result = await sourcing.replay_events(str(project.id), "item-1")
    assert result.replayed_events == COUNT_TWO
    assert result.final_state["status"] == "in_progress"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_agent_concurrent_workflow(db_session: AsyncSession) -> None:
    """Test multi-agent concurrent operations."""
    # 1. Create project
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Concurrent Test", description="Test")

    # 2. Create items
    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(
        project_id=str(project.id),
        title="Item 1",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    item2 = await item_repo.create(
        project_id=str(project.id),
        title="Item 2",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    # 3. Register agents
    agent_repo = AgentRepository(db_session)
    await agent_repo.create(str(project.id), "Agent-1", "cli")
    await agent_repo.create(str(project.id), "Agent-2", "api")

    # 4. Simulate concurrent updates
    updated1 = await item_repo.update(
        item_id=str(item1.id),
        expected_version=item1.version,
        status="in_progress",
    )

    updated2 = await item_repo.update(
        item_id=str(item2.id),
        expected_version=item2.version,
        status="in_progress",
    )

    assert updated1.status == "in_progress"
    assert updated2.status == "in_progress"
