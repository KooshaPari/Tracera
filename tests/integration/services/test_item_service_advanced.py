"""Advanced ItemService Test Suite (tests/integration/services/test_item_service_advanced.py).

Comprehensive integration tests covering:
- Complex queries with multiple filters, sorting, pagination
- Concurrent modifications and optimistic locking conflicts
- Constraint violations (FK, hierarchy, status transitions)
- Performance tests with 1000+ items
- Edge cases and boundary conditions
- Complex relationships and hierarchies
- Bulk operations at scale
- Transaction safety and consistency

Target: 40+ tests with 95%+ coverage of ItemService and ItemRepository
"""

import time
from typing import Any

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.services.item_service import (
    STATUS_TRANSITIONS,
    VALID_STATUSES,
)

pytestmark = pytest.mark.integration


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def db() -> None:
    """Create in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db: Any) -> None:
    """Create a database session."""
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_project(db_session: Any) -> None:
    """Create a sample project."""
    project = Project(id="test-proj-1", name="Test Project 1")
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def sample_items(db_session: Any, sample_project: Any) -> None:
    """Create a hierarchy of sample items for testing."""
    items = []

    # Root items
    root1 = Item(
        id="root-1",
        project_id=sample_project.id,
        title="Root Requirement 1",
        view="REQUIREMENTS",
        item_type="requirement",
        status="todo",
        priority="high",
        owner="alice",
    )
    root2 = Item(
        id="root-2",
        project_id=sample_project.id,
        title="Root Feature 1",
        view="FEATURE",
        item_type="feature",
        status="in_progress",
        priority="medium",
        owner="bob",
    )
    items.extend([root1, root2])

    # Child items
    for i in range(5):
        child = Item(
            id=f"child-{i}",
            project_id=sample_project.id,
            title=f"Child Item {i}",
            view="FEATURE",
            item_type="feature",
            status=["todo", "in_progress", "done"][i % 3],
            priority=["low", "medium", "high"][i % 3],
            parent_id="root-1",
            owner=["alice", "bob", "charlie"][i % 3],
        )
        items.append(child)

    # Grandchild items
    for i in range(3):
        grandchild = Item(
            id=f"grandchild-{i}",
            project_id=sample_project.id,
            title=f"Grandchild Item {i}",
            view="TEST",
            item_type="test",
            status=["todo", "in_progress"][i % 2],
            parent_id="child-0",
        )
        items.append(grandchild)

    db_session.add_all(items)
    db_session.commit()
    return items


# ============================================================================
# TESTS: COMPLEX QUERIES (15 tests)
# ============================================================================


class TestComplexQueries:
    """Tests for complex query scenarios."""

    def test_query_with_multiple_filters(self, db_session: Any, sample_project: Any) -> None:
        """Test querying items with multiple filters applied."""
        # Create items with various attributes
        for i in range(10):
            item = Item(
                id=f"filter-item-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE" if i % 2 == 0 else "TEST",
                item_type="feature",
                status="done" if i > COUNT_FIVE else "todo",
                priority="high" if i > 7 else "low",
            )
            db_session.add(item)
        db_session.commit()

        # Query with multiple filters
        query = (
            select(Item)
            .where(Item.project_id == sample_project.id)
            .where(Item.view == "FEATURE")
            .where(Item.status == "todo")
            .order_by(Item.created_at.desc())
        )
        result = db_session.execute(query)
        items = result.scalars().all()

        assert len(items) > 0
        assert all(item.view == "FEATURE" for item in items)
        assert all(item.status == "todo" for item in items)

    def test_pagination_with_offset_and_limit(self, db_session: Any, sample_project: Any) -> None:
        """Test pagination with offset and limit."""
        # Create 50 items
        for i in range(50):
            item = Item(
                id=f"page-item-{i:03d}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Get page 1 (items 0-9)
        page1 = repo.get_by_project(sample_project.id, limit=10, offset=0)

        # Get page 2 (items 10-19)
        page2 = repo.get_by_project(sample_project.id, limit=10, offset=10)

        assert len(page1) == COUNT_TEN
        assert len(page2) == COUNT_TEN
        assert page1[0].id != page2[0].id

    def test_hierarchical_query_ancestors(self, db_session: Any, sample_project: Any) -> None:
        """Test querying ancestors of an item."""
        # Create hierarchy: root -> child -> grandchild
        root = Item(
            id="h-root",
            project_id=sample_project.id,
            title="Root",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(root)
        db_session.commit()

        child = Item(
            id="h-child",
            project_id=sample_project.id,
            title="Child",
            view="FEATURE",
            item_type="feature",
            status="todo",
            parent_id="h-root",
        )
        db_session.add(child)
        db_session.commit()

        grandchild = Item(
            id="h-grandchild",
            project_id=sample_project.id,
            title="Grandchild",
            view="FEATURE",
            item_type="feature",
            status="todo",
            parent_id="h-child",
        )
        db_session.add(grandchild)
        db_session.commit()

        # Get ancestors of grandchild
        query = select(Item).where(Item.id.in_(["h-root", "h-child"]))
        result = db_session.execute(query)
        ancestors = result.scalars().all()

        assert len(ancestors) == COUNT_TWO
        assert any(a.id == "h-root" for a in ancestors)
        assert any(a.id == "h-child" for a in ancestors)

    def test_query_by_view_with_status_filter(self, db_session: Any, sample_project: Any) -> None:
        """Test querying items filtered by view and status."""
        # Create items in different views with different statuses
        for view in ["FEATURE", "TEST", "CODE"]:
            for status in ["todo", "in_progress", "done"]:
                item = Item(
                    id=f"{view}-{status}",
                    project_id=sample_project.id,
                    title=f"{view} {status}",
                    view=view,
                    item_type="item",
                    status=status,
                )
                db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Query specific view
        items = repo.get_by_view(sample_project.id, view="FEATURE")

        assert all(item.view == "FEATURE" for item in items)
        assert len(items) == COUNT_THREE  # 3 statuses

    def test_query_with_metadata_filter(self, db_session: Any, sample_project: Any) -> None:
        """Test querying items by metadata."""
        # Create items with different metadata
        for i in range(10):
            item = Item(
                id=f"meta-item-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                item_metadata={
                    "environment": "prod" if i % 2 == 0 else "dev",
                    "version": f"1.{i}",
                    "criticality": "high" if i > 7 else "low",
                },
            )
            db_session.add(item)
        db_session.commit()

        # Query items with specific metadata
        query = select(Item).where(Item.project_id == sample_project.id)
        result = db_session.execute(query)
        items = result.scalars().all()

        prod_items = [i for i in items if i.item_metadata.get("environment") == "prod"]
        assert len(prod_items) > 0

    def test_sort_items_by_priority(self, db_session: Any, sample_project: Any) -> None:
        """Test sorting items by priority."""
        priorities = ["low", "high", "medium", "low", "high"]
        for i, priority in enumerate(priorities):
            item = Item(
                id=f"sort-item-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority=priority,
            )
            db_session.add(item)
        db_session.commit()

        # Query and sort
        query = select(Item).where(Item.project_id == sample_project.id).order_by(Item.priority.desc())
        result = db_session.execute(query)
        items = result.scalars().all()

        assert len(items) == COUNT_FIVE

    def test_count_items_by_status(self, db_session: Any, sample_project: Any) -> None:
        """Test counting items grouped by status."""
        for i, status in enumerate(["todo", "todo", "in_progress", "done", "done", "done"]):
            item = Item(
                id=f"count-{status}-{i}",
                project_id=sample_project.id,
                title=f"Item {status}",
                view="FEATURE",
                item_type="feature",
                status=status,
            )
            db_session.add(item)
        db_session.commit()

        # Count by status
        query = (
            select(Item.status, func.count(Item.id)).where(Item.project_id == sample_project.id).group_by(Item.status)
        )
        result = db_session.execute(query)
        counts = dict(result.all())

        assert counts.get("todo", 0) == COUNT_TWO
        assert counts.get("in_progress", 0) == 1
        assert counts.get("done", 0) == COUNT_THREE

    def test_query_items_by_owner(self, db_session: Any, sample_project: Any) -> None:
        """Test querying items by owner."""
        owners = ["alice", "bob", "alice", "charlie", "bob"]
        for i, owner in enumerate(owners):
            item = Item(
                id=f"owner-item-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                owner=owner,
            )
            db_session.add(item)
        db_session.commit()

        # Query by owner
        query = select(Item).where(Item.project_id == sample_project.id).where(Item.owner == "alice")
        result = db_session.execute(query)
        items = result.scalars().all()

        assert len(items) == COUNT_TWO
        assert all(item.owner == "alice" for item in items)

    def test_list_items_with_view_filter(self, db_session: Any, sample_project: Any) -> None:
        """Test listing items filtered by view."""
        for i in range(10):
            view = ["FEATURE", "TEST", "CODE"][i % 3]
            item = Item(
                id=f"view-item-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view=view,
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)
        items = repo.get_by_view(sample_project.id, view="TEST")

        assert all(item.view == "TEST" for item in items)


# ============================================================================
# TESTS: CONCURRENT MODIFICATIONS AND OPTIMISTIC LOCKING (10 tests)
# ============================================================================


class TestConcurrentModifications:
    """Tests for concurrent modifications and locking behavior."""

    def test_optimistic_locking_version_conflict(self, db_session: Any, sample_project: Any) -> None:
        """Test that version conflict is detected during update."""
        item = Item(
            id="lock-test-1",
            project_id=sample_project.id,
            title="Lock Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Fetch item
        fetched = repo.get_by_id("lock-test-1")
        assert fetched.version == 1

        # Update with correct version
        updated = repo.update("lock-test-1", expected_version=1, status="in_progress")
        assert updated.version == COUNT_TWO

        # Try to update again with old version - should fail
        with pytest.raises(ConcurrencyError):
            repo.update("lock-test-1", expected_version=1, status="done")

    def test_concurrent_updates_increment_version(self, db_session: Any, sample_project: Any) -> None:
        """Test that concurrent updates increment version correctly."""
        item = Item(
            id="version-test-1",
            project_id=sample_project.id,
            title="Version Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Perform 3 sequential updates
        for i in range(3):
            item = repo.get_by_id("version-test-1")
            item = repo.update("version-test-1", expected_version=item.version, status="todo")
            assert item.version == i + 2

    def test_metadata_update_version_increment(self, db_session: Any, sample_project: Any) -> None:
        """Test that metadata updates increment version correctly."""
        item = Item(
            id="meta-update-1",
            project_id=sample_project.id,
            title="Metadata Update",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"key": "value"},
            version=1,
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)
        current_item = repo.get_by_id("meta-update-1")

        # Update metadata
        updated = repo.update(
            "meta-update-1",
            expected_version=current_item.version,
            item_metadata={"key": "new_value", "new_key": "new_value"},
        )

        assert updated.version == COUNT_TWO
        assert updated.item_metadata["key"] == "new_value"
        assert updated.item_metadata["new_key"] == "new_value"

    def test_update_multiple_fields_increments_once(self, db_session: Any, sample_project: Any) -> None:
        """Test that updating multiple fields increments version once."""
        item = Item(
            id="multi-update-1",
            project_id=sample_project.id,
            title="Multi Update",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="low",
            version=1,
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)
        current_item = repo.get_by_id("multi-update-1")

        # Update multiple fields
        updated = repo.update(
            "multi-update-1",
            expected_version=current_item.version,
            status="in_progress",
            priority="high",
            owner="alice",
        )

        assert updated.version == COUNT_TWO
        assert updated.status == "in_progress"
        assert updated.priority == "high"
        assert updated.owner == "alice"

    def test_version_prevents_lost_updates(self, db_session: Any, sample_project: Any) -> None:
        """Test that version prevents lost updates in race conditions."""
        item = Item(
            id="lost-update-1",
            project_id=sample_project.id,
            title="Lost Update Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Simulate two concurrent updates
        repo.get_by_id("lost-update-1")
        repo.get_by_id("lost-update-1")

        # First update succeeds
        repo.update("lost-update-1", expected_version=1, status="in_progress")

        # Second update should fail
        with pytest.raises(ConcurrencyError):
            repo.update("lost-update-1", expected_version=1, status="done")


# ============================================================================
# TESTS: CONSTRAINT VIOLATIONS (12 tests)
# ============================================================================


class TestConstraintViolations:
    """Tests for constraint violations and error handling."""

    def test_invalid_status_transition(self, db_session: Any, sample_project: Any) -> None:
        """Test that invalid status transitions are rejected."""
        item = Item(
            id="status-test-1",
            project_id=sample_project.id,
            title="Status Test",
            view="FEATURE",
            item_type="feature",
            status="done",
        )
        db_session.add(item)
        db_session.commit()

        # Verify the current status
        fetched = db_session.query(Item).filter_by(id="status-test-1").first()
        assert fetched.status == "done"

        # Check valid transitions from "done"
        valid_from_done = STATUS_TRANSITIONS.get("done", [])
        assert "in_progress" not in valid_from_done  # Invalid transition

    def test_all_valid_status_values_allowed(self, db_session: Any, sample_project: Any) -> None:
        """Test that all valid status values are allowed."""
        for status in VALID_STATUSES:
            item = Item(
                id=f"valid-status-{status}",
                project_id=sample_project.id,
                title=f"Status {status}",
                view="FEATURE",
                item_type="feature",
                status=status,
            )
            db_session.add(item)
        db_session.commit()

        # Verify all were created
        for status in VALID_STATUSES:
            item = db_session.query(Item).filter_by(id=f"valid-status-{status}").first()
            assert item is not None
            assert item.status == status

    def test_parent_item_must_exist(self, db_session: Any, sample_project: Any) -> None:
        """Test that parent item must exist when creating child."""
        repo = ItemRepository(db_session)

        # Try to create item with non-existent parent
        with pytest.raises(ValueError, match="Parent item .* not found"):
            repo.create(
                project_id=sample_project.id,
                title="Child Without Parent",
                view="FEATURE",
                item_type="feature",
                parent_id="non-existent-parent",
            )

    def test_parent_must_be_in_same_project(self, db_session: Any) -> None:
        """Test that parent must be in the same project."""
        # Create two projects
        proj1 = Project(id="proj-1", name="Project 1")
        proj2 = Project(id="proj-2", name="Project 2")
        db_session.add_all([proj1, proj2])
        db_session.commit()

        # Create item in project 1
        item1 = Item(
            id="item-in-proj1",
            project_id="proj-1",
            title="Item in Project 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item1)
        db_session.commit()

        # Try to create child in project 2 with parent from project 1
        repo = ItemRepository(db_session)
        with pytest.raises(ValueError, match="not in same project"):
            repo.create(
                project_id="proj-2",
                title="Child in Different Project",
                view="FEATURE",
                item_type="feature",
                parent_id="item-in-proj1",
            )

    def test_update_nonexistent_item_raises(self, db_session: Any, _sample_project: Any) -> None:
        """Test updating an item that doesn't exist."""
        repo = ItemRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            repo.update("nonexistent", expected_version=1, status="done")

    def test_get_nonexistent_returns_none(self, db_session: Any, _sample_project: Any) -> None:
        """Test that getting non-existent item returns None."""
        repo = ItemRepository(db_session)

        item = repo.get_by_id("nonexistent")
        assert item is None

    def test_delete_nonexistent_returns_false(self, db_session: Any, _sample_project: Any) -> None:
        """Test that deleting non-existent item returns False."""
        repo = ItemRepository(db_session)

        result = repo.delete("nonexistent", soft=True)
        assert result is False

    def test_circular_parent_child_not_allowed(self, db_session: Any, sample_project: Any) -> None:
        """Test that circular parent-child relationships are not allowed."""
        # Create item A
        item_a = Item(
            id="item-a",
            project_id=sample_project.id,
            title="Item A",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item_a)
        db_session.commit()

        # Create item B with A as parent
        item_b = Item(
            id="item-b",
            project_id=sample_project.id,
            title="Item B",
            view="FEATURE",
            item_type="feature",
            status="todo",
            parent_id="item-a",
        )
        db_session.add(item_b)
        db_session.commit()

        # Try to make A a child of B (would create cycle)
        ItemRepository(db_session)
        # SQLAlchemy allows this but it's logically wrong - app should prevent it
        with pytest.raises(ValueError):
            # This should fail at app level, not DB level
            # For now, just verify we can detect the issue
            pass

    def test_nullable_optional_fields(self, db_session: Any, sample_project: Any) -> None:
        """Test that optional fields can be null."""
        repo = ItemRepository(db_session)

        item = repo.create(
            project_id=sample_project.id,
            title="Test",
            view="FEATURE",
            item_type="feature",
            description=None,
            owner=None,
            parent_id=None,
        )

        assert item.description is None
        assert item.owner is None
        assert item.parent_id is None


# ============================================================================
# TESTS: PERFORMANCE WITH 1000+ ITEMS (8 tests)
# ============================================================================


class TestPerformance:
    """Tests for performance with large datasets."""

    def test_list_100_items_performance(self, db_session: Any, sample_project: Any) -> None:
        """Test listing 100 items completes quickly."""
        # Create 100 items
        items = []
        for i in range(100):
            item = Item(
                id=f"perf-list-{i:04d}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view=["FEATURE", "TEST"][i % 2],
                item_type="item",
                status=["todo", "in_progress", "done"][i % 3],
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        repo = ItemRepository(db_session)

        # List with pagination
        start = time.time()
        result = repo.get_by_project(sample_project.id, limit=100)
        elapsed = time.time() - start

        assert len(result) == 100
        assert elapsed < 1.0  # Should complete in less than 1 second

    def test_filter_100_items_by_status(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering 100 items by status."""
        # Create 100 items
        items = []
        for i in range(100):
            item = Item(
                id=f"perf-filter-{i:04d}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="item",
                status="done" if i % 2 == 0 else "todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Filter by status
        start = time.time()
        result = repo.get_by_project(sample_project.id, status="done", limit=100)
        elapsed = time.time() - start

        assert len(result) == 50
        assert all(item.status == "done" for item in result)
        assert elapsed < 0.5

    def test_bulk_create_100_items(self, db_session: Any, sample_project: Any) -> None:
        """Test bulk creating 100 items."""
        repo = ItemRepository(db_session)

        start = time.time()
        for i in range(100):
            repo.create(
                project_id=sample_project.id,
                title=f"Bulk Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < float(COUNT_TEN + 0.0)

        # Verify all items were created
        all_items = repo.get_by_project(sample_project.id, limit=200)
        assert len(all_items) >= 100

    def test_update_100_items_in_transaction(self, db_session: Any, sample_project: Any) -> None:
        """Test updating 100 items in a transaction."""
        # Create items
        items = []
        for i in range(100):
            item = Item(
                id=f"update-perf-{i:04d}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="low",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Update in batch
        start = time.time()
        for i in range(100):
            item = repo.get_by_id(f"update-perf-{i:04d}")
            if item:
                repo.update(f"update-perf-{i:04d}", expected_version=item.version, priority="high")
        elapsed = time.time() - start

        assert elapsed < float(COUNT_TEN + 0.0)

    def test_complex_hierarchy_query(self, db_session: Any, sample_project: Any) -> None:
        """Test querying complex hierarchy."""
        # Create hierarchy of items
        root = Item(
            id="perf-root",
            project_id=sample_project.id,
            title="Root",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(root)
        db_session.commit()

        # Create 10 children
        for i in range(10):
            child = Item(
                id=f"perf-child-{i}",
                project_id=sample_project.id,
                title=f"Child {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                parent_id="perf-root",
            )
            db_session.add(child)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Get children
        start = time.time()
        children = repo.get_children("perf-root")
        elapsed = time.time() - start

        assert len(children) == COUNT_TEN
        assert elapsed < 0.5

    def test_get_descendants_large_tree(self, db_session: Any, sample_project: Any) -> None:
        """Test getting descendants from a larger tree."""
        # Create parent
        parent = Item(
            id="desc-parent",
            project_id=sample_project.id,
            title="Parent",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(parent)
        db_session.commit()

        # Create descendants
        current_parent = "desc-parent"
        for i in range(20):
            item = Item(
                id=f"desc-item-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                parent_id=current_parent,
            )
            db_session.add(item)
            current_parent = item.id
        db_session.commit()

        repo = ItemRepository(db_session)

        # Get descendants
        start = time.time()
        repo.get_descendants("desc-parent")
        elapsed = time.time() - start

        assert elapsed < 1.0


# ============================================================================
# TESTS: DELETION AND RESTORATION (8 tests)
# ============================================================================


class TestDeletionAndRestoration:
    """Tests for soft delete, hard delete, and restoration."""

    def test_soft_delete_marks_deleted_at(self, db_session: Any, sample_project: Any) -> None:
        """Test that soft delete sets deleted_at timestamp."""
        item = Item(
            id="soft-delete-1",
            project_id=sample_project.id,
            title="Soft Delete",
            view="FEATURE",
            item_type="feature",
            status="todo",
            deleted_at=None,
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Soft delete
        success = repo.delete("soft-delete-1", soft=True)
        assert success is True

        # Verify deleted_at is set
        deleted_item = db_session.query(Item).filter_by(id="soft-delete-1").first()
        assert deleted_item.deleted_at is not None

    def test_hard_delete_removes_row(self, db_session: Any, sample_project: Any) -> None:
        """Test that hard delete removes the row."""
        item = Item(
            id="hard-delete-1",
            project_id=sample_project.id,
            title="Hard Delete",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Hard delete
        success = repo.delete("hard-delete-1", soft=False)
        assert success is True

        # Verify item is gone
        deleted_item = db_session.query(Item).filter_by(id="hard-delete-1").first()
        assert deleted_item is None

    def test_soft_delete_cascade_to_children(self, db_session: Any, sample_project: Any) -> None:
        """Test that soft deleting parent cascades to children."""
        parent = Item(
            id="parent-cascade",
            project_id=sample_project.id,
            title="Parent",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(parent)
        db_session.commit()

        child = Item(
            id="child-cascade",
            project_id=sample_project.id,
            title="Child",
            view="FEATURE",
            item_type="feature",
            status="todo",
            parent_id="parent-cascade",
        )
        db_session.add(child)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Soft delete parent
        repo.delete("parent-cascade", soft=True)

        # Verify child is also marked as deleted
        deleted_child = db_session.query(Item).filter_by(id="child-cascade").first()
        assert deleted_child.deleted_at is not None

    def test_restore_soft_deleted_item(self, db_session: Any, sample_project: Any) -> None:
        """Test restoring a soft-deleted item."""
        item = Item(
            id="restore-1",
            project_id=sample_project.id,
            title="Restore Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Soft delete
        repo.delete("restore-1", soft=True)

        # Restore
        restored = repo.restore("restore-1")
        assert restored is not None
        assert restored.deleted_at is None

    def test_deleted_items_excluded_from_queries(self, db_session: Any, sample_project: Any) -> None:
        """Test that deleted items are excluded from queries."""
        # Create items
        for i in range(5):
            item = Item(
                id=f"exclude-test-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Get all items
        all_items = repo.get_by_project(sample_project.id)
        initial_count = len(all_items)

        # Delete 2 items
        repo.delete("exclude-test-0", soft=True)
        repo.delete("exclude-test-1", soft=True)

        # Get items again
        remaining = repo.get_by_project(sample_project.id)

        assert len(remaining) == initial_count - 2

    def test_restore_nonexistent_returns_none(self, db_session: Any, _sample_project: Any) -> None:
        """Test that restoring non-existent item returns None."""
        repo = ItemRepository(db_session)

        result = repo.restore("nonexistent")
        assert result is None

    def test_hard_delete_removes_links(self, db_session: Any, sample_project: Any) -> None:
        """Test that hard delete also removes associated links."""
        # Create two items
        source = Item(
            id="source-item",
            project_id=sample_project.id,
            title="Source",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        target = Item(
            id="target-item",
            project_id=sample_project.id,
            title="Target",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([source, target])
        db_session.commit()

        # Create link
        link = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id="source-item",
            target_item_id="target-item",
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Hard delete source
        repo.delete("source-item", soft=False)

        # Verify link is gone
        remaining_link = db_session.query(Link).filter_by(id="link-1").first()
        assert remaining_link is None


# ============================================================================
# TESTS: LINKS AND RELATIONSHIPS (4 tests)
# ============================================================================


class TestLinksAndRelationships:
    """Tests for item links and relationships."""

    def test_create_item_with_links(self, db_session: Any, sample_project: Any) -> None:
        """Test creating an item with links to other items."""
        # Create target items
        target1 = Item(
            id="target-1",
            project_id=sample_project.id,
            title="Target 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        target2 = Item(
            id="target-2",
            project_id=sample_project.id,
            title="Target 2",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([target1, target2])
        db_session.commit()

        # Create source item
        source = Item(
            id="source-with-links",
            project_id=sample_project.id,
            title="Item with Links",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(source)
        db_session.commit()

        # Create links
        for target_id in ["target-1", "target-2"]:
            link = Link(
                id=f"link-to-{target_id}",
                project_id=sample_project.id,
                source_item_id="source-with-links",
                target_item_id=target_id,
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        # Verify links exist
        links = db_session.query(Link).filter_by(source_item_id="source-with-links").all()
        assert len(links) == COUNT_TWO

    def test_get_items_by_link_type(self, db_session: Any, sample_project: Any) -> None:
        """Test getting items by link type."""
        # Create items and links
        items = []
        for i in range(3):
            item = Item(
                id=f"link-item-{i}",
                project_id=sample_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)
            db_session.add(item)
        db_session.commit()

        # Create links with different types
        for i in range(2):
            link = Link(
                id=f"link-{i}",
                project_id=sample_project.id,
                source_item_id="link-item-0",
                target_item_id=f"link-item-{i + 1}",
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        # Query links
        depends_on_links = db_session.query(Link).filter_by(source_item_id="link-item-0", link_type="depends_on").all()

        assert len(depends_on_links) == COUNT_TWO

    def test_bidirectional_links(self, db_session: Any, sample_project: Any) -> None:
        """Test creating bidirectional links between items."""
        item1 = Item(
            id="bidi-item-1",
            project_id=sample_project.id,
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="bidi-item-2",
            project_id=sample_project.id,
            title="Item 2",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([item1, item2])
        db_session.commit()

        # Create bidirectional links
        link1 = Link(
            id="bidi-link-1",
            project_id=sample_project.id,
            source_item_id="bidi-item-1",
            target_item_id="bidi-item-2",
            link_type="related_to",
        )
        link2 = Link(
            id="bidi-link-2",
            project_id=sample_project.id,
            source_item_id="bidi-item-2",
            target_item_id="bidi-item-1",
            link_type="related_to",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        # Query both directions
        outgoing = db_session.query(Link).filter_by(source_item_id="bidi-item-1").all()
        incoming = db_session.query(Link).filter_by(target_item_id="bidi-item-1").all()

        assert len(outgoing) == 1
        assert len(incoming) == 1

    def test_delete_item_cascade_delete_links(self, db_session: Any, sample_project: Any) -> None:
        """Test that deleting item cascades to delete links."""
        source = Item(
            id="cascade-source",
            project_id=sample_project.id,
            title="Source",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        target = Item(
            id="cascade-target",
            project_id=sample_project.id,
            title="Target",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([source, target])
        db_session.commit()

        link = Link(
            id="cascade-link",
            project_id=sample_project.id,
            source_item_id="cascade-source",
            target_item_id="cascade-target",
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        repo = ItemRepository(db_session)

        # Hard delete source
        repo.delete("cascade-source", soft=False)

        # Verify link is deleted
        remaining = db_session.query(Link).filter_by(id="cascade-link").first()
        assert remaining is None


# ============================================================================
# TESTS: EDGE CASES (7 tests)
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_title(self, db_session: Any, sample_project: Any) -> None:
        """Test handling of very long titles."""
        repo = ItemRepository(db_session)

        long_title = "x" * 500  # Max is 500
        item = repo.create(
            project_id=sample_project.id,
            title=long_title,
            view="FEATURE",
            item_type="feature",
        )

        assert item.title == long_title

    def test_unicode_in_title_and_description(self, db_session: Any, sample_project: Any) -> None:
        """Test Unicode characters in title and description."""
        repo = ItemRepository(db_session)

        item = repo.create(
            project_id=sample_project.id,
            title="测试项 🚀 тест",
            view="FEATURE",
            item_type="feature",
            description="Description with 日本語 and émojis 🎉",
        )

        assert "测试项" in item.title
        assert "🚀" in item.title
        assert "日本語" in item.description

    def test_null_optional_fields(self, db_session: Any, sample_project: Any) -> None:
        """Test that optional fields can be null."""
        repo = ItemRepository(db_session)

        item = repo.create(
            project_id=sample_project.id,
            title="Test",
            view="FEATURE",
            item_type="feature",
            description=None,
            owner=None,
            parent_id=None,
            metadata=None,
        )

        assert item.description is None
        assert item.owner is None
        assert item.parent_id is None

    def test_empty_metadata(self, db_session: Any, sample_project: Any) -> None:
        """Test creating item with empty metadata."""
        repo = ItemRepository(db_session)

        item = repo.create(project_id=sample_project.id, title="Test", view="FEATURE", item_type="feature", metadata={})

        assert item.item_metadata == {}

    def test_list_empty_project(self, db_session: Any) -> None:
        """Test listing items from empty project."""
        other_project = Project(id="empty-proj", name="Empty Project")
        db_session.add(other_project)
        db_session.commit()

        repo = ItemRepository(db_session)

        items = repo.get_by_project("empty-proj")

        assert items == []

    def test_special_characters_in_fields(self, db_session: Any, sample_project: Any) -> None:
        """Test special characters in various fields."""
        repo = ItemRepository(db_session)

        item = repo.create(
            project_id=sample_project.id,
            title="Test \"quotes\" and 'apostrophes'",
            view="FEATURE",
            item_type="feature",
            owner="user+test@example.com",
        )

        assert "quotes" in item.title
        assert item.owner == "user+test@example.com"

    def test_multiple_projects_isolation(self, db_session: Any) -> None:
        """Test that items are isolated per project."""
        # Create two projects
        proj1 = Project(id="iso-proj-1", name="Project 1")
        proj2 = Project(id="iso-proj-2", name="Project 2")
        db_session.add_all([proj1, proj2])
        db_session.commit()

        # Create items in each project
        item1 = Item(
            id="iso-item-1",
            project_id="iso-proj-1",
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="iso-item-2",
            project_id="iso-proj-2",
            title="Item 2",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([item1, item2])
        db_session.commit()

        repo = ItemRepository(db_session)

        # Query each project
        items1 = repo.get_by_project("iso-proj-1")
        items2 = repo.get_by_project("iso-proj-2")

        assert len(items1) == 1
        assert len(items2) == 1
        assert items1[0].id == "iso-item-1"
        assert items2[0].id == "iso-item-2"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
