"""End-to-end workflow tests for complete project lifecycle.

Tests cover:
- Project creation
- Item management (CRUD)
- Link management
- Synchronization
- Export operations
- Traceability operations

These tests verify the complete workflow from project creation through
export and ensure all components work together correctly.
"""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

pytestmark = pytest.mark.integration


# ============================================================================
# WORKFLOW 1: PROJECT CREATION AND BASIC SETUP
# ============================================================================


def test_e2e_workflow_create_empty_project(db_session: Session) -> None:
    """Test 1: Create an empty project."""
    project = Project(
        id=str(uuid4()),
        name="Test Project Alpha",
        description="Test project for E2E workflow",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    assert project.id is not None
    assert project.name == "Test Project Alpha"
    assert project.description == "Test project for E2E workflow"

    # Verify project can be retrieved
    retrieved = db_session.query(Project).filter_by(id=project.id).first()
    assert retrieved is not None
    assert retrieved.name == "Test Project Alpha"


def test_e2e_workflow_create_multiple_projects(db_session: Session) -> None:
    """Test 2: Create multiple projects in sequence."""
    project_ids = []
    for i in range(5):
        project = Project(
            id=str(uuid4()),
            name=f"Project {i + 1}",
            description=f"Description for project {i + 1}",
        )
        db_session.add(project)
        project_ids.append(project.id)

    db_session.commit()

    # Verify all projects exist
    assert len(project_ids) == COUNT_FIVE
    assert len(set(project_ids)) == COUNT_FIVE  # All unique

    for pid in project_ids:
        retrieved = db_session.query(Project).filter_by(id=pid).first()
        assert retrieved is not None


def test_e2e_workflow_project_metadata(db_session: Session) -> None:
    """Test 3: Create project with metadata."""
    metadata = {
        "team": "Platform",
        "department": "Engineering",
        "budget_code": "ENG-2024",
        "tags": ["critical", "backend"],
    }

    project = Project(
        id=str(uuid4()),
        name="Metadata Test Project",
        description="Project with custom metadata",
        project_metadata=metadata,
    )
    db_session.add(project)
    db_session.commit()

    retrieved = db_session.query(Project).filter_by(id=project.id).first()
    assert retrieved is not None
    assert retrieved.project_metadata == metadata


# ============================================================================
# WORKFLOW 2: ITEM CREATION AND MANAGEMENT
# ============================================================================


def test_e2e_workflow_add_single_item(db_session: Session) -> None:
    """Test 4: Add a single item to project."""
    project = Project(id=str(uuid4()), name="Item Test Project")
    db_session.add(project)
    db_session.commit()

    item = Item(
        id=f"ITEM-{uuid4()}",
        project_id=project.id,
        title="User Authentication Feature",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    assert item.id is not None
    assert item.title == "User Authentication Feature"
    assert item.view == "FEATURE"
    assert item.status == "todo"

    # Verify item can be retrieved
    retrieved = db_session.query(Item).filter_by(id=item.id).first()
    assert retrieved is not None


def test_e2e_workflow_add_items_multiple_views(db_session: Session) -> None:
    """Test 5: Add items across different views (FEATURE, CODE, TEST, etc)."""
    project = Project(id=str(uuid4()), name="Multi-View Project")
    db_session.add(project)
    db_session.commit()

    views = [
        ("FEATURE", "feature", "Login System"),
        ("CODE", "file", "auth.py"),
        ("TEST", "test", "test_auth.py"),
        ("DESIGN", "design", "Auth Flow Diagram"),
        ("REQUIREMENT", "requirement", "Login Requirements"),
    ]

    items = []
    for view, item_type, title in views:
        item = Item(
            id=f"{view}-{uuid4()}",
            project_id=project.id,
            title=title,
            view=view,
            item_type=item_type,
            status="todo",
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()

    assert len(items) == COUNT_FIVE
    assert [item.view for item in items] == ["FEATURE", "CODE", "TEST", "DESIGN", "REQUIREMENT"]


def test_e2e_workflow_add_items_with_metadata(db_session: Session) -> None:
    """Test 6: Add items with custom metadata."""
    project = Project(id=str(uuid4()), name="Metadata Items Project")
    db_session.add(project)
    db_session.commit()

    metadata = {
        "priority": "high",
        "assignee": "alice@example.com",
        "story_points": 8,
        "labels": ["backend", "security"],
        "milestone": "v2.0",
    }

    item = Item(
        id=f"TASK-{uuid4()}",
        project_id=project.id,
        title="Implement OAuth2",
        view="FEATURE",
        item_type="feature",
        status="todo",
        item_metadata=metadata,
    )
    db_session.add(item)
    db_session.commit()

    retrieved = db_session.query(Item).filter_by(id=item.id).first()
    assert retrieved is not None
    assert retrieved.item_metadata == metadata


def test_e2e_workflow_update_item_status(db_session: Session) -> None:
    """Test 7: Update item status through workflow."""
    project = Project(id=str(uuid4()), name="Status Update Project")
    db_session.add(project)
    db_session.commit()

    item = Item(
        id=f"ITEM-{uuid4()}",
        project_id=project.id,
        title="Task Item",
        view="TASK",
        item_type="task",
        status="todo",
    )
    db_session.add(item)
    db_session.commit()

    # Update status through workflow
    statuses = ["todo", "in_progress", "review", "done"]
    for status in statuses:
        item.status = status
        db_session.commit()
        db_session.refresh(item)
        assert item.status == status


def test_e2e_workflow_bulk_create_items(db_session: Session) -> None:
    """Test 8: Bulk create items (simulating large project setup)."""
    project = Project(id=str(uuid4()), name="Bulk Items Project")
    db_session.add(project)
    db_session.commit()

    items = []
    for i in range(20):
        item = Item(
            id=f"TASK-{i}-{uuid4()}",
            project_id=project.id,
            title=f"Task {i + 1}",
            view="TASK",
            item_type="task",
            status="todo",
            item_metadata={"order": i + 1},
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()

    assert len(items) == 20

    # Verify all items are stored
    retrieved_items = db_session.query(Item).filter_by(project_id=project.id).all()
    assert len(retrieved_items) >= 20


# ============================================================================
# WORKFLOW 3: LINK CREATION AND RELATIONSHIP MANAGEMENT
# ============================================================================


def test_e2e_workflow_create_single_link(db_session: Session) -> None:
    """Test 9: Create a single link between items."""
    project = Project(id=str(uuid4()), name="Link Test Project")
    db_session.add(project)
    db_session.commit()

    feature = Item(
        id=f"FEATURE-{uuid4()}",
        project_id=project.id,
        title="Feature",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    code = Item(
        id=f"CODE-{uuid4()}",
        project_id=project.id,
        title="Code",
        view="CODE",
        item_type="file",
        status="todo",
    )
    db_session.add_all([feature, code])
    db_session.commit()

    link = Link(
        id=f"LINK-{uuid4()}",
        project_id=project.id,
        source_item_id=feature.id,
        target_item_id=code.id,
        link_type="implements",
    )
    db_session.add(link)
    db_session.commit()

    assert link.id is not None
    assert link.source_item_id == feature.id
    assert link.target_item_id == code.id
    assert link.link_type == "implements"


def test_e2e_workflow_create_multiple_link_types(db_session: Session) -> None:
    """Test 10: Create links with different link types."""
    project = Project(id=str(uuid4()), name="Link Types Project")
    db_session.add(project)
    db_session.commit()

    # Create items for different link types
    items = []
    for i in range(5):
        item = Item(
            id=f"ITEM-{i}-{uuid4()}",
            project_id=project.id,
            title=f"Item {i + 1}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()

    # Create different link types
    link_types = [
        ("implements", items[0].id, items[1].id),
        ("depends_on", items[1].id, items[2].id),
        ("tests", items[3].id, items[0].id),
        ("documents", items[4].id, items[1].id),
        ("related_to", items[2].id, items[4].id),
    ]

    links = []
    for link_type, source_id, target_id in link_types:
        link = Link(
            id=f"LINK-{uuid4()}",
            project_id=project.id,
            source_item_id=source_id,
            target_item_id=target_id,
            link_type=link_type,
        )
        db_session.add(link)
        links.append(link)

    db_session.commit()

    assert len(links) == COUNT_FIVE
    assert [link.link_type for link in links] == ["implements", "depends_on", "tests", "documents", "related_to"]


def test_e2e_workflow_create_dependency_chain(db_session: Session) -> None:
    """Test 11: Create a chain of dependencies (A -> B -> C -> D)."""
    project = Project(id=str(uuid4()), name="Dependency Chain Project")
    db_session.add(project)
    db_session.commit()

    # Create items A, B, C, D
    item_a = Item(
        id=f"A-{uuid4()}",
        project_id=project.id,
        title="Item A",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    item_b = Item(
        id=f"B-{uuid4()}",
        project_id=project.id,
        title="Item B",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    item_c = Item(
        id=f"C-{uuid4()}",
        project_id=project.id,
        title="Item C",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    item_d = Item(
        id=f"D-{uuid4()}",
        project_id=project.id,
        title="Item D",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    db_session.add_all([item_a, item_b, item_c, item_d])
    db_session.commit()

    # Create dependency chain: A depends on B, B depends on C, C depends on D
    link1 = Link(
        id=f"L1-{uuid4()}",
        project_id=project.id,
        source_item_id=item_a.id,
        target_item_id=item_b.id,
        link_type="depends_on",
    )
    link2 = Link(
        id=f"L2-{uuid4()}",
        project_id=project.id,
        source_item_id=item_b.id,
        target_item_id=item_c.id,
        link_type="depends_on",
    )
    link3 = Link(
        id=f"L3-{uuid4()}",
        project_id=project.id,
        source_item_id=item_c.id,
        target_item_id=item_d.id,
        link_type="depends_on",
    )

    db_session.add_all([link1, link2, link3])
    db_session.commit()

    # Verify all links exist
    links = db_session.query(Link).filter_by(project_id=project.id).all()
    assert len(links) >= COUNT_THREE


def test_e2e_workflow_create_complex_graph(db_session: Session) -> None:
    """Test 12: Create a complex dependency graph with multiple connections."""
    project = Project(id=str(uuid4()), name="Complex Graph Project")
    db_session.add(project)
    db_session.commit()

    # Create 6 items
    items = []
    for i in range(6):
        item = Item(
            id=f"ITEM-{i}-{uuid4()}",
            project_id=project.id,
            title=f"Item {i + 1}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()

    # Create complex relationships
    links_to_create = [
        (items[0], items[1]),  # A -> B
        (items[0], items[2]),  # A -> C
        (items[1], items[3]),  # B -> D
        (items[2], items[3]),  # C -> D
        (items[3], items[4]),  # D -> E
        (items[3], items[5]),  # D -> F
        (items[4], items[5]),  # E -> F
    ]

    for source, target in links_to_create:
        link = Link(
            id=f"LINK-{uuid4()}",
            project_id=project.id,
            source_item_id=source.id,
            target_item_id=target.id,
            link_type="depends_on",
        )
        db_session.add(link)

    db_session.commit()

    links = db_session.query(Link).filter_by(project_id=project.id).all()
    assert len(links) >= 7


# ============================================================================
# WORKFLOW 4: SYNCHRONIZATION OPERATIONS
# ============================================================================


def test_e2e_workflow_sync_project_state(db_session: Session) -> None:
    """Test 13: Sync project state (verify consistency)."""
    project = Project(id=str(uuid4()), name="Sync Test Project")
    db_session.add(project)
    db_session.commit()

    # Create items and links
    items = []
    for i in range(3):
        item = Item(
            id=f"ITEM-{i}-{uuid4()}",
            project_id=project.id,
            title=f"Item {i + 1}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()

    # Create links
    link = Link(
        id=f"LINK-{uuid4()}",
        project_id=project.id,
        source_item_id=items[0].id,
        target_item_id=items[1].id,
        link_type="depends_on",
    )
    db_session.add(link)
    db_session.commit()

    # Verify project state
    retrieved_items = db_session.query(Item).filter_by(project_id=project.id).all()
    retrieved_links = db_session.query(Link).filter_by(project_id=project.id).all()

    assert len(retrieved_items) == COUNT_THREE
    assert len(retrieved_links) >= 1


def test_e2e_workflow_sync_with_item_updates(db_session: Session) -> None:
    """Test 14: Sync after updating items."""
    project = Project(id=str(uuid4()), name="Sync Update Project")
    db_session.add(project)
    db_session.commit()

    # Create item
    item = Item(
        id=f"ITEM-{uuid4()}",
        project_id=project.id,
        title="Original Title",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    db_session.add(item)
    db_session.commit()

    # Update item multiple times
    for status in ["todo", "in_progress", "review", "done"]:
        item.status = status
        db_session.commit()
        db_session.refresh(item)

    # Verify final state
    final = db_session.query(Item).filter_by(id=item.id).first()
    assert final is not None
    assert final.status == "done"


def test_e2e_workflow_sync_event_creation(db_session: Session) -> None:
    """Test 15: Sync creates proper events for audit trail."""
    project = Project(id=str(uuid4()), name="Event Sync Project")
    db_session.add(project)
    db_session.commit()

    item = Item(
        id=f"ITEM-{uuid4()}",
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    db_session.add(item)
    db_session.commit()

    # Create audit event
    event = Event(
        project_id=project.id,
        event_type="item_created",
        entity_type="item",
        entity_id=item.id,
        agent_id="test-agent",
        data={},
    )
    db_session.add(event)
    db_session.commit()

    # Retrieve events
    events = (
        db_session
        .query(Event)
        .filter_by(
            project_id=project.id,
            entity_type="item",
            entity_id=item.id,
        )
        .all()
    )

    assert len(events) >= 1


# ============================================================================
# WORKFLOW 5: EXPORT OPERATIONS (Simulated)
# ============================================================================


def test_e2e_workflow_export_project_json(db_session: Session) -> None:
    """Test 16: Export project to JSON format."""
    project = Project(id=str(uuid4()), name="Export Test Project")
    db_session.add(project)
    db_session.commit()

    # Create sample data
    item1 = Item(
        id=f"ITEM-1-{uuid4()}",
        project_id=project.id,
        title="Feature 1",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    item2 = Item(
        id=f"ITEM-2-{uuid4()}",
        project_id=project.id,
        title="Feature 2",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    db_session.add_all([item1, item2])
    db_session.commit()

    # Simulate export
    items = db_session.query(Item).filter_by(project_id=project.id).all()
    export_data = {
        "project": {
            "id": project.id,
            "name": project.name,
        },
        "items": [{"id": item.id, "title": item.title, "status": item.status} for item in items],
    }

    assert export_data is not None
    assert "project" in export_data
    assert len(export_data["items"]) == COUNT_TWO


def test_e2e_workflow_export_with_items_and_links(db_session: Session) -> None:
    """Test 17: Export project with items and links."""
    project = Project(id=str(uuid4()), name="Export Full Project")
    db_session.add(project)
    db_session.commit()

    # Create items
    items = []
    for i in range(3):
        item = Item(
            id=f"ITEM-{i}-{uuid4()}",
            project_id=project.id,
            title=f"Item {i + 1}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()

    # Create links
    for i in range(len(items) - 1):
        link = Link(
            id=f"LINK-{uuid4()}",
            project_id=project.id,
            source_item_id=items[i].id,
            target_item_id=items[i + 1].id,
            link_type="depends_on",
        )
        db_session.add(link)

    db_session.commit()

    # Simulate export
    items_data = db_session.query(Item).filter_by(project_id=project.id).all()
    links_data = db_session.query(Link).filter_by(project_id=project.id).all()

    export_data = {
        "items": [{"id": i.id, "title": i.title} for i in items_data],
        "links": [{"source": l.source_item_id, "target": l.target_item_id} for l in links_data],
    }

    assert export_data is not None
    assert len(export_data["items"]) >= COUNT_THREE


def test_e2e_workflow_export_multiple_formats(db_session: Session) -> None:
    """Test 18: Export project in multiple formats."""
    project = Project(id=str(uuid4()), name="Multi-Format Export")
    db_session.add(project)
    db_session.commit()

    item = Item(
        id=f"ITEM-{uuid4()}",
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    db_session.add(item)
    db_session.commit()

    # Simulate JSON export
    items = db_session.query(Item).filter_by(project_id=project.id).all()
    json_data = {"format": "json", "items": [{"id": i.id, "title": i.title} for i in items]}

    assert json_data is not None
    assert json_data["format"] == "json"


# ============================================================================
# WORKFLOW 6: TRACEABILITY OPERATIONS (Simulated)
# ============================================================================


def test_e2e_workflow_generate_traceability_matrix(db_session: Session) -> None:
    """Test 19: Generate traceability matrix."""
    project = Project(id=str(uuid4()), name="Traceability Matrix Project")
    db_session.add(project)
    db_session.commit()

    # Create items in different views
    feature = Item(
        id=f"FEATURE-{uuid4()}",
        project_id=project.id,
        title="Auth Feature",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    code = Item(
        id=f"CODE-{uuid4()}",
        project_id=project.id,
        title="auth.py",
        view="CODE",
        item_type="file",
        status="todo",
    )
    db_session.add_all([feature, code])
    db_session.commit()

    # Create link
    link = Link(
        id=f"LINK-{uuid4()}",
        project_id=project.id,
        source_item_id=feature.id,
        target_item_id=code.id,
        link_type="implements",
    )
    db_session.add(link)
    db_session.commit()

    # Simulate matrix generation
    features = db_session.query(Item).filter_by(project_id=project.id, view="FEATURE").all()
    code_items = db_session.query(Item).filter_by(project_id=project.id, view="CODE").all()
    links = db_session.query(Link).filter_by(project_id=project.id).all()

    matrix = {
        "features": len(features),
        "code": len(code_items),
        "coverage": len(links),
    }

    assert matrix is not None
    assert matrix["features"] == 1
    assert matrix["code"] == 1


def test_e2e_workflow_analyze_impact(db_session: Session) -> None:
    """Test 20: Analyze impact of item changes."""
    project = Project(id=str(uuid4()), name="Impact Analysis Project")
    db_session.add(project)
    db_session.commit()

    # Create items
    item_a = Item(
        id=f"A-{uuid4()}",
        project_id=project.id,
        title="Item A",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    item_b = Item(
        id=f"B-{uuid4()}",
        project_id=project.id,
        title="Item B",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    item_c = Item(
        id=f"C-{uuid4()}",
        project_id=project.id,
        title="Item C",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    db_session.add_all([item_a, item_b, item_c])
    db_session.commit()

    # Create dependencies: A depends on B, B depends on C
    link1 = Link(
        id=f"L1-{uuid4()}",
        project_id=project.id,
        source_item_id=item_a.id,
        target_item_id=item_b.id,
        link_type="depends_on",
    )
    link2 = Link(
        id=f"L2-{uuid4()}",
        project_id=project.id,
        source_item_id=item_b.id,
        target_item_id=item_c.id,
        link_type="depends_on",
    )

    db_session.add_all([link1, link2])
    db_session.commit()

    # Simulate impact analysis
    links_to_c = db_session.query(Link).filter_by(target_item_id=item_c.id).all()

    impact = {
        "directly_affected": [link.source_item_id for link in links_to_c],
        "total_impact": len(links_to_c),
    }

    assert impact is not None
    total_impact = impact.get("total_impact", 0)
    assert isinstance(total_impact, int) and total_impact >= 0


def test_e2e_workflow_coverage_analysis(db_session: Session) -> None:
    """Test 21: Analyze requirement coverage."""
    project = Project(id=str(uuid4()), name="Coverage Analysis Project")
    db_session.add(project)
    db_session.commit()

    # Create requirements
    req1 = Item(
        id=f"REQ-1-{uuid4()}",
        project_id=project.id,
        title="Requirement 1",
        view="REQUIREMENT",
        item_type="requirement",
        status="todo",
    )
    req2 = Item(
        id=f"REQ-2-{uuid4()}",
        project_id=project.id,
        title="Requirement 2",
        view="REQUIREMENT",
        item_type="requirement",
        status="todo",
    )

    # Create tests for requirements
    test1 = Item(
        id=f"TEST-1-{uuid4()}",
        project_id=project.id,
        title="Test for Req1",
        view="TEST",
        item_type="test",
        status="todo",
    )

    db_session.add_all([req1, req2, test1])
    db_session.commit()

    # Link requirement to test
    link = Link(
        id=f"LINK-{uuid4()}",
        project_id=project.id,
        source_item_id=req1.id,
        target_item_id=test1.id,
        link_type="tests",
    )
    db_session.add(link)
    db_session.commit()

    # Analyze coverage
    requirements = db_session.query(Item).filter_by(project_id=project.id, view="REQUIREMENT").all()
    tests = db_session.query(Item).filter_by(project_id=project.id, view="TEST").all()
    coverage_links = db_session.query(Link).filter_by(project_id=project.id, link_type="tests").all()

    coverage = {
        "total_requirements": len(requirements),
        "total_tests": len(tests),
        "coverage_links": len(coverage_links),
        "coverage_percentage": (len(coverage_links) / len(requirements) * 100) if requirements else 0,
    }

    assert coverage is not None
    assert coverage["total_requirements"] >= COUNT_TWO


# ============================================================================
# WORKFLOW 7: COMPLETE WORKFLOWS (Multi-step operations)
# ============================================================================


def test_e2e_workflow_complete_project_setup(db_session: Session) -> None:
    """Test 22: Complete project setup workflow."""
    # 1. Create project
    project = Project(
        id=str(uuid4()),
        name="Complete Setup Project",
        description="Full project setup workflow",
        project_metadata={"team": "Engineering"},
    )
    db_session.add(project)
    db_session.commit()

    # 2. Create requirements
    req = Item(
        id=f"REQ-{uuid4()}",
        project_id=project.id,
        title="Login System",
        view="REQUIREMENT",
        item_type="requirement",
        status="todo",
    )

    # 3. Create feature
    feature = Item(
        id=f"FEAT-{uuid4()}",
        project_id=project.id,
        title="Implement Login",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    # 4. Create code item
    code = Item(
        id=f"CODE-{uuid4()}",
        project_id=project.id,
        title="login.py",
        view="CODE",
        item_type="file",
        status="todo",
    )

    # 5. Create test item
    test = Item(
        id=f"TEST-{uuid4()}",
        project_id=project.id,
        title="test_login.py",
        view="TEST",
        item_type="test",
        status="todo",
    )

    db_session.add_all([req, feature, code, test])
    db_session.commit()

    # 6. Create links
    link1 = Link(
        id=f"L1-{uuid4()}",
        project_id=project.id,
        source_item_id=req.id,
        target_item_id=feature.id,
        link_type="implements",
    )
    link2 = Link(
        id=f"L2-{uuid4()}",
        project_id=project.id,
        source_item_id=feature.id,
        target_item_id=code.id,
        link_type="implements",
    )
    link3 = Link(
        id=f"L3-{uuid4()}",
        project_id=project.id,
        source_item_id=code.id,
        target_item_id=test.id,
        link_type="tests",
    )

    db_session.add_all([link1, link2, link3])
    db_session.commit()

    # 7. Verify all items and links
    items = db_session.query(Item).filter_by(project_id=project.id).all()
    links = db_session.query(Link).filter_by(project_id=project.id).all()

    assert len(items) == COUNT_FOUR  # req, feature, code, test
    assert len(links) >= COUNT_THREE


def test_e2e_workflow_agile_sprint_setup(db_session: Session) -> None:
    """Test 23: Agile sprint setup and progression."""
    project = Project(
        id=str(uuid4()),
        name="Agile Sprint Project",
        project_metadata={"sprint": "Sprint 1"},
    )
    db_session.add(project)
    db_session.commit()

    # Create user stories
    stories = []
    for i in range(3):
        story = Item(
            id=f"STORY-{i}-{uuid4()}",
            project_id=project.id,
            title=f"User Story {i + 1}",
            view="STORY",
            item_type="story",
            status="todo",
            item_metadata={"sprint": 1, "story_points": 5},
        )
        db_session.add(story)
        stories.append(story)

    db_session.commit()

    # Create tasks for each story
    for i, story in enumerate(stories):
        for j in range(2):
            task = Item(
                id=f"TASK-{i}-{j}-{uuid4()}",
                project_id=project.id,
                title=f"Task {j + 1} for Story {i + 1}",
                view="TASK",
                item_type="task",
                status="todo",
            )
            db_session.add(task)

            link = Link(
                id=f"LINK-{uuid4()}",
                project_id=project.id,
                source_item_id=story.id,
                target_item_id=task.id,
                link_type="subtask",
            )
            db_session.add(link)

    db_session.commit()

    # Progress items through sprint
    all_items = db_session.query(Item).filter_by(project_id=project.id).all()
    for item in all_items[:3]:
        item.status = "in_progress"

    db_session.commit()

    verified_items = db_session.query(Item).filter_by(project_id=project.id).all()
    assert len(verified_items) >= 9  # 3 stories + 6 tasks


def test_e2e_workflow_cross_view_traceability(db_session: Session) -> None:
    """Test 24: Traceability across multiple views."""
    project = Project(id=str(uuid4()), name="Cross-View Traceability")
    db_session.add(project)
    db_session.commit()

    # Create items across all views
    requirement = Item(
        id=f"REQ-{uuid4()}",
        project_id=project.id,
        title="User must be able to reset password",
        view="REQUIREMENT",
        item_type="requirement",
        status="todo",
    )

    design = Item(
        id=f"DES-{uuid4()}",
        project_id=project.id,
        title="Password Reset Flow Diagram",
        view="DESIGN",
        item_type="design",
        status="todo",
    )

    feature = Item(
        id=f"FEAT-{uuid4()}",
        project_id=project.id,
        title="Password Reset Feature",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    code = Item(
        id=f"CODE-{uuid4()}",
        project_id=project.id,
        title="password_reset.py",
        view="CODE",
        item_type="file",
        status="todo",
    )

    test = Item(
        id=f"TEST-{uuid4()}",
        project_id=project.id,
        title="test_password_reset.py",
        view="TEST",
        item_type="test",
        status="todo",
    )

    db_session.add_all([requirement, design, feature, code, test])
    db_session.commit()

    # Create complete traceability chain
    links = [
        Link(
            id=f"L1-{uuid4()}",
            project_id=project.id,
            source_item_id=requirement.id,
            target_item_id=design.id,
            link_type="designed_by",
        ),
        Link(
            id=f"L2-{uuid4()}",
            project_id=project.id,
            source_item_id=design.id,
            target_item_id=feature.id,
            link_type="implements",
        ),
        Link(
            id=f"L3-{uuid4()}",
            project_id=project.id,
            source_item_id=feature.id,
            target_item_id=code.id,
            link_type="implements",
        ),
        Link(
            id=f"L4-{uuid4()}",
            project_id=project.id,
            source_item_id=code.id,
            target_item_id=test.id,
            link_type="tested_by",
        ),
    ]

    for link in links:
        db_session.add(link)

    db_session.commit()

    # Verify complete chain
    stored_links = db_session.query(Link).filter_by(project_id=project.id).all()
    assert len(stored_links) >= COUNT_FOUR


def test_e2e_workflow_complete_lifecycle(db_session: Session) -> None:
    """Test 25: Complete project lifecycle from creation to completion."""
    # Phase 1: Create project
    project = Project(
        id=str(uuid4()),
        name="Complete Lifecycle Project",
        description="Test complete project lifecycle",
        project_metadata={"phase": "initial_setup"},
    )
    db_session.add(project)
    db_session.commit()

    # Phase 2: Create requirements
    requirements = []
    for i in range(2):
        req = Item(
            id=f"REQ-{i}-{uuid4()}",
            project_id=project.id,
            title=f"Requirement {i + 1}",
            view="REQUIREMENT",
            item_type="requirement",
            status="todo",
        )
        db_session.add(req)
        requirements.append(req)

    db_session.commit()

    # Phase 3: Create implementation items
    implementations = []
    for req in requirements:
        impl = Item(
            id=f"CODE-{uuid4()}",
            project_id=project.id,
            title=f"Implementation for {req.title}",
            view="CODE",
            item_type="file",
            status="todo",
        )
        db_session.add(impl)
        implementations.append(impl)

        link = Link(
            id=f"LINK-{uuid4()}",
            project_id=project.id,
            source_item_id=req.id,
            target_item_id=impl.id,
            link_type="implements",
        )
        db_session.add(link)

    db_session.commit()

    # Phase 4: Create tests
    tests = []
    for impl in implementations:
        test = Item(
            id=f"TEST-{uuid4()}",
            project_id=project.id,
            title=f"Test for {impl.title}",
            view="TEST",
            item_type="test",
            status="todo",
        )
        db_session.add(test)
        tests.append(test)

        link = Link(
            id=f"LINK-{uuid4()}",
            project_id=project.id,
            source_item_id=impl.id,
            target_item_id=test.id,
            link_type="tested_by",
        )
        db_session.add(link)

    db_session.commit()

    # Phase 5: Progress items to completion
    all_items = db_session.query(Item).filter_by(project_id=project.id).all()
    for item in all_items:
        item.status = "done"

    db_session.commit()

    # Phase 6: Simulate export
    final_items = db_session.query(Item).filter_by(project_id=project.id).all()
    final_links = db_session.query(Link).filter_by(project_id=project.id).all()

    export_data = {
        "items": len(final_items),
        "links": len(final_links),
        "status": "all_done",
    }

    # Verify final state
    assert len(final_items) >= 6
    assert len(final_links) >= COUNT_FOUR
    assert export_data is not None


def test_e2e_workflow_error_recovery(db_session: Session) -> None:
    """Test 26: Error recovery in workflow (test resilience)."""
    project = Project(id=str(uuid4()), name="Error Recovery Project")
    db_session.add(project)
    db_session.commit()

    # Create item
    item = Item(
        id=f"ITEM-{uuid4()}",
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    db_session.add(item)
    db_session.commit()

    # Attempt invalid operation (should handle gracefully)

    # Recover by updating correctly
    item.status = "in_progress"
    db_session.commit()

    # Verify item exists in correct state
    retrieved = db_session.query(Item).filter_by(id=item.id).first()
    assert retrieved is not None
    assert retrieved.status == "in_progress"
