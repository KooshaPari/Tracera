"""Unit tests for LinkRepository.

Functional Requirements Coverage:
    - FR-DISC-003: Auto-Link Suggestion (partial - link creation)
    - FR-APP-001: Bidirectional Link Navigation (partial)

Epics:
    - EPIC-003: Traceability Matrix Core

Tests verify link creation, retrieval, queries by item, link type filtering,
and relationship navigation between traceability items.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

# Use link_test_setup fixture to auto-create graphs when projects are created
pytestmark = pytest.mark.usefixtures("link_test_setup")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link(db_session: AsyncSession) -> None:
    """Test creating a link between items.

    Tests: FR-DISC-003, FR-APP-001
    """
    # Setup: Create project and items
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target Item",
        view="CODE",
        item_type="file",
        status="todo",
    )

    # Test: Create link
    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    assert link.id is not None
    assert link.source_item_id == source.id
    assert link.target_item_id == target.id
    assert link.link_type == "implements"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession) -> None:
    """Test retrieving a link by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    created = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    retrieved = await link_repo.get_by_id(str(created.id))
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_links_for_item(db_session: AsyncSession) -> None:
    """Test getting all links for an item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    feature = await item_repo.create(
        project_id=str(project.id),
        title="Feature",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    code1 = await item_repo.create(
        project_id=str(project.id),
        title="Code 1",
        view="CODE",
        item_type="file",
        status="todo",
    )
    code2 = await item_repo.create(
        project_id=str(project.id),
        title="Code 2",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(feature.id),
        target_item_id=str(code1.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(feature.id),
        target_item_id=str(code2.id),
        link_type="implements",
    )

    links = await link_repo.get_by_item(str(feature.id))
    assert len(links) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_link(db_session: AsyncSession) -> None:
    """Test deleting a link."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    await link_repo.delete(str(link.id))

    deleted = await link_repo.get_by_id(str(link.id))
    assert deleted is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_source(db_session: AsyncSession) -> None:
    """Test getting links by source item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target1 = await item_repo.create(
        project_id=str(project.id),
        title="Target 1",
        view="CODE",
        item_type="file",
        status="todo",
    )
    target2 = await item_repo.create(
        project_id=str(project.id),
        title="Target 2",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target1.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target2.id),
        link_type="implements",
    )

    links = await link_repo.get_by_source(str(source.id))
    assert len(links) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_target(db_session: AsyncSession) -> None:
    """Test getting links by target item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source1 = await item_repo.create(
        project_id=str(project.id),
        title="Source 1",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    source2 = await item_repo.create(
        project_id=str(project.id),
        title="Source 2",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source1.id),
        target_item_id=str(target.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source2.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    links = await link_repo.get_by_target(str(target.id))
    assert len(links) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_link_with_metadata(db_session: AsyncSession) -> None:
    """Test creating link with metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
        metadata={"priority": "high", "verified": True},
    )

    meta = getattr(link, "link_metadata", None) or {}
    assert meta.get("priority") == "high"
    assert meta.get("verified") is True


# =============================================================================
# Graph ID Resolution Tests (lines 28-59)
# =============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_with_explicit_graph_id(db_session: AsyncSession) -> None:
    """Test creating a link with an explicit graph_id (skips resolution logic)."""
    from uuid import uuid4

    from tracertm.models.graph import Graph

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    # Create a custom graph (not default)
    custom_graph = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="custom-graph",
        graph_type="custom",
        description="Custom graph for testing",
    )
    db_session.add(custom_graph)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
        graph_id=str(custom_graph.id),  # Explicit graph_id
    )

    assert link.graph_id == custom_graph.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_resolves_graph_from_source_item_view(db_session: AsyncSession) -> None:
    """Test that graph_id is resolved from source item's primary view."""
    from uuid import uuid4

    from tracertm.models.graph import Graph
    from tracertm.models.view import View

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    # Create a View with name "FEATURE" - ItemRepository.create will use this view
    # when creating an item with view="FEATURE"
    view = View(
        id=str(uuid4()),
        project_id=str(project.id),
        name="FEATURE",
        description="Feature view",
    )
    db_session.add(view)
    await db_session.flush()

    # Create a Graph with graph_type matching the view name
    feature_graph = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="feature-graph",
        graph_type="FEATURE",  # Matches view name
        description="Feature graph",
    )
    db_session.add(feature_graph)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    # ItemRepository.create will automatically create ItemView with is_primary=True
    # linking source item to the "FEATURE" view we created above
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    # Now create link without graph_id - should resolve from source item's view
    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
        # No graph_id - should be resolved
    )

    assert link.graph_id == feature_graph.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_falls_back_to_default_graph(db_session: AsyncSession) -> None:
    """Test that link creation falls back to 'default' graph when source view lookup fails."""
    from uuid import uuid4

    from tracertm.models.graph import Graph

    # Manually create project
    from tracertm.models.project import Project

    # Create project WITHOUT auto-creating default graph (don't use link_test_setup)
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test",
    )
    db_session.add(project)
    await db_session.flush()

    # Create ONLY a default graph (no view-based graph)
    default_graph = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="default",
        graph_type="default",
        description="Default graph",
    )
    db_session.add(default_graph)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    # No ItemView exists for source, so view-based lookup will fail
    # Should fall back to default graph
    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    assert link.graph_id == default_graph.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_raises_error_when_no_graph_found(db_session: AsyncSession) -> None:
    """Test that link creation raises ValueError when no graph can be resolved."""
    from uuid import uuid4

    from tracertm.models.project import Project

    # Create project without any graphs
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test",
    )
    db_session.add(project)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)

    with pytest.raises(ValueError, match="graph_id is required and could not be resolved"):
        await link_repo.create(
            project_id=str(project.id),
            source_item_id=str(source.id),
            target_item_id=str(target.id),
            link_type="implements",
        )


# =============================================================================
# Graph ID Filter Tests for Query Methods (lines 87, 95, 103, 113)
# =============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_with_graph_id_filter(db_session: AsyncSession) -> None:
    """Test get_by_project with graph_id filter."""
    from uuid import uuid4

    from tracertm.models.graph import Graph

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    # Create two graphs
    graph1 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph1",
        graph_type="type1",
    )
    graph2 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph2",
        graph_type="type2",
    )
    db_session.add(graph1)
    db_session.add(graph2)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)

    # Create links in different graphs
    link1 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
        graph_id=str(graph1.id),
    )
    link2 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="references",
        graph_id=str(graph2.id),
    )

    # Test: get_by_project without filter returns all links
    all_links = await link_repo.get_by_project(str(project.id))
    assert len(all_links) == COUNT_TWO

    # Test: get_by_project with graph_id filter returns only matching links
    graph1_links = await link_repo.get_by_project(str(project.id), graph_id=str(graph1.id))
    assert len(graph1_links) == 1
    assert graph1_links[0].id == link1.id

    graph2_links = await link_repo.get_by_project(str(project.id), graph_id=str(graph2.id))
    assert len(graph2_links) == 1
    assert graph2_links[0].id == link2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_source_with_graph_id_filter(db_session: AsyncSession) -> None:
    """Test get_by_source with graph_id filter."""
    from uuid import uuid4

    from tracertm.models.graph import Graph

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    # Create two graphs
    graph1 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph1",
        graph_type="type1",
    )
    graph2 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph2",
        graph_type="type2",
    )
    db_session.add(graph1)
    db_session.add(graph2)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target1 = await item_repo.create(
        project_id=str(project.id),
        title="Target 1",
        view="CODE",
        item_type="file",
        status="todo",
    )
    target2 = await item_repo.create(
        project_id=str(project.id),
        title="Target 2",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)

    # Create links from same source in different graphs
    link1 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target1.id),
        link_type="implements",
        graph_id=str(graph1.id),
    )
    link2 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target2.id),
        link_type="references",
        graph_id=str(graph2.id),
    )

    # Test: get_by_source without filter returns all links from source
    all_links = await link_repo.get_by_source(str(source.id))
    assert len(all_links) == COUNT_TWO

    # Test: get_by_source with graph_id filter
    graph1_links = await link_repo.get_by_source(str(source.id), graph_id=str(graph1.id))
    assert len(graph1_links) == 1
    assert graph1_links[0].id == link1.id

    graph2_links = await link_repo.get_by_source(str(source.id), graph_id=str(graph2.id))
    assert len(graph2_links) == 1
    assert graph2_links[0].id == link2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_target_with_graph_id_filter(db_session: AsyncSession) -> None:
    """Test get_by_target with graph_id filter."""
    from uuid import uuid4

    from tracertm.models.graph import Graph

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    # Create two graphs
    graph1 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph1",
        graph_type="type1",
    )
    graph2 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph2",
        graph_type="type2",
    )
    db_session.add(graph1)
    db_session.add(graph2)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    source1 = await item_repo.create(
        project_id=str(project.id),
        title="Source 1",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    source2 = await item_repo.create(
        project_id=str(project.id),
        title="Source 2",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)

    # Create links to same target in different graphs
    link1 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source1.id),
        target_item_id=str(target.id),
        link_type="implements",
        graph_id=str(graph1.id),
    )
    link2 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source2.id),
        target_item_id=str(target.id),
        link_type="references",
        graph_id=str(graph2.id),
    )

    # Test: get_by_target without filter returns all links to target
    all_links = await link_repo.get_by_target(str(target.id))
    assert len(all_links) == COUNT_TWO

    # Test: get_by_target with graph_id filter
    graph1_links = await link_repo.get_by_target(str(target.id), graph_id=str(graph1.id))
    assert len(graph1_links) == 1
    assert graph1_links[0].id == link1.id

    graph2_links = await link_repo.get_by_target(str(target.id), graph_id=str(graph2.id))
    assert len(graph2_links) == 1
    assert graph2_links[0].id == link2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_item_with_graph_id_filter(db_session: AsyncSession) -> None:
    """Test get_by_item with graph_id filter."""
    from uuid import uuid4

    from tracertm.models.graph import Graph

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    # Create two graphs
    graph1 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph1",
        graph_type="type1",
    )
    graph2 = Graph(
        id=str(uuid4()),
        project_id=str(project.id),
        name="graph2",
        graph_type="type2",
    )
    db_session.add(graph1)
    db_session.add(graph2)
    await db_session.flush()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=str(project.id),
        title="Central Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    other1 = await item_repo.create(
        project_id=str(project.id),
        title="Other 1",
        view="CODE",
        item_type="file",
        status="todo",
    )
    other2 = await item_repo.create(
        project_id=str(project.id),
        title="Other 2",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)

    # Create links where item is source (graph1) and target (graph2)
    link1 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item.id),
        target_item_id=str(other1.id),
        link_type="implements",
        graph_id=str(graph1.id),
    )
    link2 = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(other2.id),
        target_item_id=str(item.id),
        link_type="references",
        graph_id=str(graph2.id),
    )

    # Test: get_by_item without filter returns all links connected to item
    all_links = await link_repo.get_by_item(str(item.id))
    assert len(all_links) == COUNT_TWO

    # Test: get_by_item with graph_id filter
    graph1_links = await link_repo.get_by_item(str(item.id), graph_id=str(graph1.id))
    assert len(graph1_links) == 1
    assert graph1_links[0].id == link1.id

    graph2_links = await link_repo.get_by_item(str(item.id), graph_id=str(graph2.id))
    assert len(graph2_links) == 1
    assert graph2_links[0].id == link2.id


# =============================================================================
# Additional Edge Case Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_with_none_graph_id(db_session: AsyncSession) -> None:
    """Test get_by_project explicitly passing graph_id=None returns all links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    # Explicitly pass graph_id=None
    links = await link_repo.get_by_project(str(project.id), graph_id=None)
    assert len(links) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_source_with_none_graph_id(db_session: AsyncSession) -> None:
    """Test get_by_source explicitly passing graph_id=None returns all links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    # Explicitly pass graph_id=None
    links = await link_repo.get_by_source(str(source.id), graph_id=None)
    assert len(links) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_target_with_none_graph_id(db_session: AsyncSession) -> None:
    """Test get_by_target explicitly passing graph_id=None returns all links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    # Explicitly pass graph_id=None
    links = await link_repo.get_by_target(str(target.id), graph_id=None)
    assert len(links) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_item_with_none_graph_id(db_session: AsyncSession) -> None:
    """Test get_by_item explicitly passing graph_id=None returns all links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
    )

    # Explicitly pass graph_id=None
    links = await link_repo.get_by_item(str(source.id), graph_id=None)
    assert len(links) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_by_item(db_session: AsyncSession) -> None:
    """Test deleting all links connected to an item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=str(project.id),
        title="Central Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    other1 = await item_repo.create(
        project_id=str(project.id),
        title="Other 1",
        view="CODE",
        item_type="file",
        status="todo",
    )
    other2 = await item_repo.create(
        project_id=str(project.id),
        title="Other 2",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)

    # Create links where item is both source and target
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item.id),
        target_item_id=str(other1.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(other2.id),
        target_item_id=str(item.id),
        link_type="references",
    )

    # Verify links exist
    links_before = await link_repo.get_by_item(str(item.id))
    assert len(links_before) == COUNT_TWO

    # Delete all links connected to item
    deleted_count = await link_repo.delete_by_item(str(item.id))
    assert deleted_count == COUNT_TWO

    # Verify links are deleted
    links_after = await link_repo.get_by_item(str(item.id))
    assert len(links_after) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all(db_session: AsyncSession) -> None:
    """Test getting all links in the database."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target1 = await item_repo.create(
        project_id=str(project.id),
        title="Target 1",
        view="CODE",
        item_type="file",
        status="todo",
    )
    target2 = await item_repo.create(
        project_id=str(project.id),
        title="Target 2",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target1.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target2.id),
        link_type="references",
    )

    all_links = await link_repo.get_all()
    assert len(all_links) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_type(db_session: AsyncSession) -> None:
    """Test getting links by link type."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target1 = await item_repo.create(
        project_id=str(project.id),
        title="Target 1",
        view="CODE",
        item_type="file",
        status="todo",
    )
    target2 = await item_repo.create(
        project_id=str(project.id),
        title="Target 2",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target1.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target2.id),
        link_type="references",
    )

    # Get by type
    implements_links = await link_repo.get_by_type("implements")
    assert len(implements_links) == 1
    assert implements_links[0].link_type == "implements"

    references_links = await link_repo.get_by_type("references")
    assert len(references_links) == 1
    assert references_links[0].link_type == "references"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_with_link_metadata_parameter(db_session: AsyncSession) -> None:
    """Test creating link using link_metadata parameter (alternative to metadata)."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=str(project.id),
        title="Source",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=str(project.id),
        title="Target",
        view="CODE",
        item_type="file",
        status="todo",
    )

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="implements",
        link_metadata={"confidence": 0.95, "automated": True},  # Using link_metadata
    )

    assert link.link_metadata["confidence"] == 0.95
    assert link.link_metadata["automated"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_returns_false_for_nonexistent_link(db_session: AsyncSession) -> None:
    """Test that delete returns False when link doesn't exist."""
    link_repo = LinkRepository(db_session)

    result = await link_repo.delete("nonexistent-link-id")
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_nonexistent_link(db_session: AsyncSession) -> None:
    """Test that get_by_id returns None when link doesn't exist."""
    link_repo = LinkRepository(db_session)

    result = await link_repo.get_by_id("nonexistent-link-id")
    assert result is None
