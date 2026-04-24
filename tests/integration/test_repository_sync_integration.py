"""Synchronous Repository Integration Tests for TraceRTM.

These tests validate:
- Repository CRUD operations with real database
- Data integrity and constraints
- Cascading operations and cleanup
- Complex query patterns
- Transaction boundaries

Uses sync database session from conftest fixtures.
Target Coverage: 90%+ for repository layer
"""

import pytest
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

pytestmark = pytest.mark.integration


# ============================================================================
# PROJECT REPOSITORY - BASIC OPERATIONS
# ============================================================================


def test_project_create_and_retrieve(db_session: Session) -> None:
    """Test creating and retrieving a project."""
    project = Project(
        name="Test Project",
        description="Test description",
        project_metadata={"env": "test", "version": "1.0"},
    )
    db_session.add(project)
    db_session.commit()

    # Verify persisted
    found = db_session.query(Project).filter_by(id=project.id).first()
    assert found is not None
    assert found.name == "Test Project"
    assert found.description == "Test description"


def test_project_create_multiple(db_session: Session) -> None:
    """Test creating multiple projects."""
    projects = [
        Project(name="Project A"),
        Project(name="Project B"),
        Project(name="Project C"),
    ]
    db_session.add_all(projects)
    db_session.commit()

    # Verify all created
    all_projects = db_session.query(Project).all()
    assert len(all_projects) >= COUNT_THREE


def test_project_update(db_session: Session) -> None:
    """Test updating a project."""
    project = Project(name="Original", description="Original desc")
    db_session.add(project)
    db_session.commit()

    # Update
    project.name = "Updated"
    project.description = "Updated desc"
    db_session.commit()

    # Verify
    found = db_session.query(Project).filter_by(id=project.id).first()
    assert found is not None
    assert found.name == "Updated"
    assert found.description == "Updated desc"


def test_project_update_metadata(db_session: Session) -> None:
    """Test updating project metadata."""
    metadata = {"version": 1, "env": "dev"}
    project = Project(name="Project", project_metadata=metadata)
    db_session.add(project)
    db_session.commit()

    # Update metadata
    project.project_metadata = {"version": 2, "env": "prod"}
    db_session.commit()

    # Verify
    found = db_session.query(Project).filter_by(id=project.id).first()
    assert found is not None
    assert found.project_metadata == {"version": 2, "env": "prod"}


def test_project_delete(db_session: Session) -> None:
    """Test deleting a project."""
    project = Project(name="To Delete")
    db_session.add(project)
    db_session.commit()

    project_id = project.id

    # Delete
    db_session.delete(project)
    db_session.commit()

    # Verify deleted
    found = db_session.query(Project).filter_by(id=project_id).first()
    assert found is None


# ============================================================================
# ITEM REPOSITORY - BASIC OPERATIONS
# ============================================================================


def test_item_create_and_retrieve(db_session: Session) -> None:
    """Test creating and retrieving an item."""
    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()

    item = Item(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        description="Test description",
        status="todo",
        priority="high",
    )
    db_session.add(item)
    db_session.commit()

    # Verify
    found = db_session.query(Item).filter_by(id=item.id).first()
    assert found is not None
    assert found.title == "Test Item"
    assert found.status == "todo"


def test_item_create_multiple_in_project(db_session: Session) -> None:
    """Test creating multiple items in a project."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    items = []
    for i in range(5):
        item = Item(project_id=project.id, title=f"Item {i}", view="FEATURE", item_type="feature", status="todo")
        items.append(item)

    db_session.add_all(items)
    db_session.commit()

    # Verify all created
    found_items = db_session.query(Item).filter_by(project_id=project.id).all()
    assert len(found_items) == COUNT_FIVE


def test_item_update_status(db_session: Session) -> None:
    """Test updating item status."""
    project = Project(name="Project")
    item = Item(project_id=project.id, title="Item", view="FEATURE", item_type="feature", status="todo")
    db_session.add_all([project, item])
    db_session.commit()

    # Update status
    item.status = "in_progress"
    db_session.commit()

    # Verify
    found = db_session.query(Item).filter_by(id=item.id).first()
    assert found is not None
    assert found.status == "in_progress"


def test_item_update_priority(db_session: Session) -> None:
    """Test updating item priority."""
    project = Project(name="Project")
    item = Item(project_id=project.id, title="Item", view="FEATURE", item_type="feature", priority="medium")
    db_session.add_all([project, item])
    db_session.commit()

    # Update priority
    item.priority = "high"
    db_session.commit()

    # Verify
    found = db_session.query(Item).filter_by(id=item.id).first()
    assert found is not None
    assert found.priority == "high"


def test_item_with_metadata(db_session: Session) -> None:
    """Test item with metadata."""
    project = Project(name="Project")
    metadata = {"assigned_to": "dev@example.com", "epic": "auth"}
    item = Item(project_id=project.id, title="Item", view="FEATURE", item_type="feature", item_metadata=metadata)
    db_session.add_all([project, item])
    db_session.commit()

    # Verify
    found = db_session.query(Item).filter_by(id=item.id).first()
    assert found is not None
    assert found.item_metadata == metadata


def test_item_delete(db_session: Session) -> None:
    """Test deleting an item."""
    project = Project(name="Project")
    item = Item(project_id=project.id, title="Item", view="FEATURE", item_type="feature")
    db_session.add_all([project, item])
    db_session.commit()

    item_id = item.id

    # Delete
    db_session.delete(item)
    db_session.commit()

    # Verify deleted
    found = db_session.query(Item).filter_by(id=item_id).first()
    assert found is None


# ============================================================================
# LINK REPOSITORY - BASIC OPERATIONS
# ============================================================================


def test_link_create_and_retrieve(db_session: Session) -> None:
    """Test creating and retrieving a link."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    item1 = Item(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = Item(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    db_session.add_all([item1, item2])
    db_session.commit()

    link = Link(
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
        link_metadata={"priority": "high"},
    )
    db_session.add(link)
    db_session.commit()

    # Verify
    found = db_session.query(Link).filter_by(id=link.id).first()
    assert found is not None
    assert found.source_item_id == item1.id
    assert found.target_item_id == item2.id
    assert found.link_type == "depends_on"


def test_link_create_multiple(db_session: Session) -> None:
    """Test creating multiple links."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    items = []
    for i in range(4):
        item = Item(project_id=project.id, title=f"Item {i}", view="FEATURE", item_type="feature")
        items.append(item)

    db_session.add_all(items)
    db_session.commit()

    # Create chain: 0->1->2->3
    links = []
    for i in range(len(items) - 1):
        link = Link(source_item_id=items[i].id, target_item_id=items[i + 1].id, link_type="depends_on")
        links.append(link)

    db_session.add_all(links)
    db_session.commit()

    # Verify
    all_links = db_session.query(Link).all()
    assert len(all_links) >= COUNT_THREE


def test_link_query_by_source(db_session: Session) -> None:
    """Test querying links by source item."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    item1 = Item(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = Item(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    db_session.add_all([item1, item2])
    db_session.commit()

    link = Link(source_item_id=item1.id, target_item_id=item2.id, link_type="depends_on")
    db_session.add(link)
    db_session.commit()

    # Query
    found_links = db_session.query(Link).filter_by(source_item_id=item1.id).all()
    assert len(found_links) >= 1
    assert found_links[0].source_item_id == item1.id


def test_link_query_by_target(db_session: Session) -> None:
    """Test querying links by target item."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    item1 = Item(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = Item(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    db_session.add_all([item1, item2])
    db_session.commit()

    link = Link(source_item_id=item1.id, target_item_id=item2.id, link_type="depends_on")
    db_session.add(link)
    db_session.commit()

    # Query
    found_links = db_session.query(Link).filter_by(target_item_id=item2.id).all()
    assert len(found_links) >= 1
    assert found_links[0].target_item_id == item2.id


def test_link_delete(db_session: Session) -> None:
    """Test deleting a link."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    item1 = Item(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = Item(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    db_session.add_all([item1, item2])
    db_session.commit()

    link = Link(source_item_id=item1.id, target_item_id=item2.id, link_type="depends_on")
    db_session.add(link)
    db_session.commit()

    link_id = link.id

    # Delete
    db_session.delete(link)
    db_session.commit()

    # Verify
    found = db_session.query(Link).filter_by(id=link_id).first()
    assert found is None


# ============================================================================
# CROSS-ENTITY RELATIONSHIPS
# ============================================================================


def test_item_parent_child_relationship(db_session: Session) -> None:
    """Test parent-child relationship between items."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    parent = Item(project_id=project.id, title="Parent", view="FEATURE", item_type="feature")
    db_session.add(parent)
    db_session.commit()

    child = Item(project_id=project.id, title="Child", view="FEATURE", item_type="feature", parent_id=parent.id)
    db_session.add(child)
    db_session.commit()

    # Verify relationship
    found_child = db_session.query(Item).filter_by(id=child.id).first()
    assert found_child is not None
    assert found_child.parent_id == parent.id


def test_item_project_isolation(db_session: Session) -> None:
    """Test that items are isolated by project."""
    proj1 = Project(name="Project 1")
    proj2 = Project(name="Project 2")
    db_session.add_all([proj1, proj2])
    db_session.commit()

    item1 = Item(project_id=proj1.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = Item(project_id=proj2.id, title="Item 2", view="FEATURE", item_type="feature")
    db_session.add_all([item1, item2])
    db_session.commit()

    # Verify isolation
    proj1_items = db_session.query(Item).filter_by(project_id=proj1.id).all()
    proj2_items = db_session.query(Item).filter_by(project_id=proj2.id).all()

    assert len(proj1_items) >= 1
    assert len(proj2_items) >= 1
    assert all(i.project_id == proj1.id for i in proj1_items)
    assert all(i.project_id == proj2.id for i in proj2_items)


# ============================================================================
# TRANSACTION AND ROLLBACK TESTS
# ============================================================================


def test_transaction_commit(db_session: Session) -> None:
    """Test that commits persist data."""
    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()

    project_id = project.id

    # Verify persisted
    found = db_session.query(Project).filter_by(id=project_id).first()
    assert found is not None


def test_transaction_rollback(db_session: Session) -> None:
    """Test that rollback reverts changes."""
    project = Project(name="Original Name")
    db_session.add(project)
    db_session.commit()

    # Modify
    project.name = "Modified Name"

    # Rollback
    db_session.rollback()

    # Verify original state
    found = db_session.query(Project).filter_by(id=project.id).first()
    assert found is not None
    assert found.name == "Original Name"


# ============================================================================
# QUERY PATTERN TESTS
# ============================================================================


def test_query_items_by_status(db_session: Session) -> None:
    """Test querying items by status."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    for status in ["todo", "in_progress", "done"]:
        for i in range(2):
            item = Item(
                project_id=project.id,
                title=f"{status} Item {i}",
                view="FEATURE",
                item_type="feature",
                status=status,
            )
            db_session.add(item)

    db_session.commit()

    # Query by status
    todos = db_session.query(Item).filter_by(status="todo").all()
    in_progress = db_session.query(Item).filter_by(status="in_progress").all()
    done = db_session.query(Item).filter_by(status="done").all()

    assert len(todos) >= COUNT_TWO
    assert len(in_progress) >= COUNT_TWO
    assert len(done) >= COUNT_TWO


def test_query_items_by_priority(db_session: Session) -> None:
    """Test querying items by priority."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    for priority in ["high", "medium", "low"]:
        item = Item(
            project_id=project.id,
            title=f"{priority} Item",
            view="FEATURE",
            item_type="feature",
            priority=priority,
        )
        db_session.add(item)

    db_session.commit()

    # Query by priority
    high = db_session.query(Item).filter_by(priority="high").all()
    medium = db_session.query(Item).filter_by(priority="medium").all()
    low = db_session.query(Item).filter_by(priority="low").all()

    assert len(high) >= 1
    assert len(medium) >= 1
    assert len(low) >= 1


def test_query_items_by_view(db_session: Session) -> None:
    """Test querying items by view type."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    views = ["FEATURE", "REQUIREMENT", "BUG"]
    for view in views:
        item = Item(project_id=project.id, title=f"{view} Item", view=view, item_type=view.lower())
        db_session.add(item)

    db_session.commit()

    # Query by view
    features = db_session.query(Item).filter_by(view="FEATURE").all()
    requirements = db_session.query(Item).filter_by(view="REQUIREMENT").all()
    bugs = db_session.query(Item).filter_by(view="BUG").all()

    assert len(features) >= 1
    assert len(requirements) >= 1
    assert len(bugs) >= 1


def test_query_items_with_multiple_filters(db_session: Session) -> None:
    """Test querying items with multiple filters."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    item = Item(
        project_id=project.id,
        title="High Priority Todo",
        view="FEATURE",
        item_type="feature",
        status="todo",
        priority="high",
    )
    db_session.add(item)
    db_session.commit()

    # Query with multiple filters
    found = db_session.query(Item).filter_by(status="todo", priority="high", view="FEATURE").all()

    assert len(found) >= 1
    assert found[0].status == "todo"
    assert found[0].priority == "high"


# ============================================================================
# COUNTING AND AGGREGATION TESTS
# ============================================================================


def test_count_items_by_project(db_session: Session) -> None:
    """Test counting items in a project."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    for i in range(5):
        item = Item(project_id=project.id, title=f"Item {i}", view="FEATURE", item_type="feature")
        db_session.add(item)

    db_session.commit()

    # Count
    count = db_session.query(Item).filter_by(project_id=project.id).count()
    assert count == COUNT_FIVE


def test_count_links_by_source(db_session: Session) -> None:
    """Test counting links by source item."""
    project = Project(name="Project")
    db_session.add(project)
    db_session.commit()

    item1 = Item(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    db_session.add(item1)
    db_session.commit()

    # Create multiple links from item1
    for i in range(3):
        item = Item(project_id=project.id, title=f"Item {i}", view="FEATURE", item_type="feature")
        db_session.add(item)

    db_session.commit()

    # Get all items except first
    target_items = db_session.query(Item).filter(Item.id != item1.id).all()

    for target in target_items:
        link = Link(source_item_id=item1.id, target_item_id=target.id, link_type="depends_on")
        db_session.add(link)

    db_session.commit()

    # Count
    count = db_session.query(Link).filter_by(source_item_id=item1.id).count()
    assert count >= 1
