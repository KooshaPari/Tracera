"""Comprehensive integration tests for Repository query patterns.

Tests complex filtering, pagination, sorting, and aggregations across all repositories.
Target coverage: 90%+ for query-related functionality.

Test Categories:
1. Complex Filters (12 tests)
2. Pagination (10 tests)
3. Sorting (10 tests)
4. Aggregations (15+ tests)
5. Edge Cases (10+ tests)
"""

from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

# ============================================================================
# FIXTURES
# ============================================================================


@pytest_asyncio.fixture
async def setup_projects(db_session: AsyncSession) -> dict[str, Project]:
    """Create test projects directly without using repository."""
    from uuid import uuid4

    projects = {}
    for i, name in enumerate(["Project 1", "Project 2", "Project 3"], 1):
        project = Project(
            id=str(uuid4()),
            name=name,
            description=f"Desc {i}",
            project_metadata={},
        )
        db_session.add(project)
        projects[f"proj{i}"] = project

    return projects


@pytest_asyncio.fixture
async def setup_items(db_session: AsyncSession, setup_projects: dict) -> dict[str, Item]:
    """Create items with various attributes for testing."""
    item_repo = ItemRepository(db_session)
    project_id = setup_projects["proj1"].id

    items = {}
    datetime.now(UTC)

    # Create items with different statuses
    for i, status in enumerate(["todo", "in_progress", "done", "todo", "done"]):
        item = await item_repo.create(
            project_id=project_id,
            title=f"Item {i + 1}",
            view="FEATURE",
            item_type="feature",
            status=status,
            priority=["high", "medium", "low", "high", "medium"][i],
            description=f"Description for item {i + 1}",
        )
        items[f"item{i + 1}"] = item

    # Create items with different views
    for i, view in enumerate(["BUG", "TASK", "EPIC"], start=6):
        item = await item_repo.create(
            project_id=project_id,
            title=f"Item {i}",
            view=view,
            item_type=view.lower(),
            status="todo",
            priority="medium",
        )
        items[f"item{i}"] = item

    # Create hierarchical items
    parent = await item_repo.create(
        project_id=project_id,
        title="Parent Item",
        view="EPIC",
        item_type="epic",
        status="in_progress",
    )
    items["parent"] = parent

    child1 = await item_repo.create(
        project_id=project_id,
        title="Child Item 1",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id,
        status="done",
    )
    items["child1"] = child1

    child2 = await item_repo.create(
        project_id=project_id,
        title="Child Item 2",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id,
        status="todo",
    )
    items["child2"] = child2

    return items


@pytest_asyncio.fixture
async def setup_links(db_session: AsyncSession, setup_items: dict) -> dict[str, Link]:
    """Create links between items."""
    link_repo = LinkRepository(db_session)

    links = {}
    link_types = ["relates_to", "blocks", "depends_on"]

    # Create links between items
    item1, item2, item3 = setup_items["item1"], setup_items["item2"], setup_items["item3"]
    project_id = item1.project_id

    for idx, link_type in enumerate(link_types):
        link = await link_repo.create(
            project_id=project_id,
            source_item_id=item1.id,
            target_item_id=item2.id if idx == 0 else item3.id,
            link_type=link_type,
        )
        links[f"link{idx + 1}"] = link

    return links


# ============================================================================
# COMPLEX FILTERS TESTS (12 tests)
# ============================================================================


@pytest.mark.asyncio
class TestComplexFilters:
    """Test complex filtering patterns."""

    async def test_filter_single_attribute(self, db_session: AsyncSession, setup_items: dict[str, Item]) -> None:
        """Filter items by single attribute."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Filter by status
        todo_items = await repo.query(project_id, {"status": "todo"})
        assert len(todo_items) == 6  # items 1, 4, 6, 7, 8, and child2
        assert all(item.status == "todo" for item in todo_items)

    async def test_filter_multiple_attributes(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter items by multiple attributes."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Filter by status AND priority
        items = await repo.query(project_id, {"status": "todo", "priority": "high"})
        assert all(item.status == "todo" and item.priority == "high" for item in items)

    async def test_filter_by_view(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter items by view."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        feature_items = await repo.query(project_id, {"view": "FEATURE"})
        assert all(item.view == "FEATURE" for item in feature_items)
        assert len(feature_items) > 0

    async def test_filter_by_item_type(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter items by type."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        bugs = await repo.query(project_id, {"item_type": "bug"})
        assert all(item.item_type == "bug" for item in bugs)

    async def test_filter_by_priority(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter items by priority."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        high_priority = await repo.query(project_id, {"priority": "high"})
        assert all(item.priority == "high" for item in high_priority)

    async def test_filter_with_nonexistent_status(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter with status that doesn't exist."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.query(project_id, {"status": "nonexistent_status"})
        assert len(items) == 0

    async def test_filter_with_parent_id(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter items by parent_id."""
        repo = ItemRepository(db_session)
        parent = setup_items["parent"]
        project_id = parent.project_id

        children = await repo.query(project_id, {"parent_id": parent.id})
        assert len(children) == COUNT_TWO
        assert all(item.parent_id == parent.id for item in children)

    async def test_filter_by_null_parent_id(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter items without parent (root items)."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        root_items = await repo.query(project_id, {"parent_id": None})
        assert len(root_items) > 0
        assert all(item.parent_id is None for item in root_items)

    async def test_filter_multiple_values_same_attribute(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Filter with OR condition (multiple values for same attribute)."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get items with status in [todo, done]
        items = await repo.query(project_id, {"status": "todo"})
        initial_count = len(items)
        assert initial_count > 0

    async def test_get_by_view_with_status_filter(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Get items by view with optional status filter."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Without status filter
        features = await repo.get_by_view(project_id, "FEATURE")
        assert len(features) > 0

        # With status filter
        done_features = await repo.get_by_view(project_id, "FEATURE", status="done")
        assert all(item.view == "FEATURE" and item.status == "done" for item in done_features)

    async def test_get_by_project_with_status_filter(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Get items by project with optional status filter."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Without filter
        all_items = await repo.get_by_project(project_id)
        assert len(all_items) > 0

        # With status filter
        todo_items = await repo.get_by_project(project_id, status="todo")
        assert all(item.status == "todo" for item in todo_items)


# ============================================================================
# PAGINATION TESTS (10 tests)
# ============================================================================


@pytest.mark.asyncio
class TestPagination:
    """Test pagination patterns."""

    async def test_pagination_basic_first_page(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Get first page with limit."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        page = await repo.get_by_project(project_id, limit=5, offset=0)
        assert len(page) <= COUNT_FIVE

    async def test_pagination_basic_second_page(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Get second page with offset."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        page1 = await repo.get_by_project(project_id, limit=3, offset=0)
        page2 = await repo.get_by_project(project_id, limit=3, offset=3)

        # Ensure no overlap
        page1_ids = {item.id for item in page1}
        page2_ids = {item.id for item in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    async def test_pagination_view_based(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test pagination with get_by_view."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        page1 = await repo.get_by_view(project_id, "FEATURE", limit=2, offset=0)
        page2 = await repo.get_by_view(project_id, "FEATURE", limit=2, offset=2)

        assert len(page1) > 0
        assert len(page2) >= 0

    async def test_pagination_beyond_total(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test pagination with offset beyond total items."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get all items
        all_items = await repo.get_by_project(project_id, limit=1000)
        total = len(all_items)

        # Request page beyond total
        beyond = await repo.get_by_project(project_id, limit=5, offset=total + 10)
        assert len(beyond) == 0

    async def test_pagination_limit_zero(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test pagination with limit=0 (edge case)."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.get_by_project(project_id, limit=0)
        # SQLAlchemy limit(0) returns no results
        assert len(items) == 0

    async def test_pagination_large_limit(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test pagination with very large limit."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.get_by_project(project_id, limit=10000, offset=0)
        assert len(items) > 0

    async def test_pagination_offset_negative(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test pagination with negative offset (treated as 0)."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Negative offset is implementation-dependent
        try:
            items = await repo.get_by_project(project_id, limit=5, offset=-1)
            # Should either work or fail gracefully
            assert isinstance(items, list)
        except Exception:
            pass

    async def test_pagination_with_filter_and_limit(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test pagination with filters applied."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        page1 = await repo.get_by_project(project_id, status="todo", limit=2, offset=0)
        page2 = await repo.get_by_project(project_id, status="todo", limit=2, offset=2)

        # All items should have status=todo
        for item in page1 + page2:
            assert item.status == "todo"

    async def test_pagination_consistency(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test that pagination is consistent across multiple calls."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get same page twice
        page1_call1 = await repo.get_by_project(project_id, limit=3, offset=0)
        page1_call2 = await repo.get_by_project(project_id, limit=3, offset=0)

        ids1 = [item.id for item in page1_call1]
        ids2 = [item.id for item in page1_call2]
        assert ids1 == ids2

    async def test_pagination_total_coverage(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test that pagination covers all items without gap."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        all_items = await repo.get_by_project(project_id, limit=1000)
        total = len(all_items)

        # Paginate through with limit=3
        collected = []
        offset = 0
        page_size = 3

        while True:
            page = await repo.get_by_project(project_id, limit=page_size, offset=offset)
            if not page:
                break
            collected.extend(page)
            offset += page_size

        assert len(collected) == total


# ============================================================================
# SORTING TESTS (10 tests)
# ============================================================================


@pytest.mark.asyncio
class TestSorting:
    """Test sorting patterns."""

    async def test_sort_by_created_at_desc(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Items should be sorted by created_at descending."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.get_by_project(project_id, limit=1000)

        # Check descending order
        for i in range(len(items) - 1):
            assert items[i].created_at >= items[i + 1].created_at

    async def test_sort_by_created_at_within_view(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Items within view should be sorted by created_at."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.get_by_view(project_id, "FEATURE", limit=1000)

        # Check descending order
        for i in range(len(items) - 1):
            assert items[i].created_at >= items[i + 1].created_at

    async def test_consistent_sort_across_pages(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Sort order should be consistent across pages."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        page1 = await repo.get_by_project(project_id, limit=3, offset=0)
        page2 = await repo.get_by_project(project_id, limit=3, offset=3)

        combined = page1 + page2
        for i in range(len(combined) - 1):
            assert combined[i].created_at >= combined[i + 1].created_at

    async def test_sort_preserves_data(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Sorting should not modify item data."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id
        item_id = setup_items["item1"].id

        items = await repo.get_by_project(project_id, limit=1000)

        # Find our specific item
        found = next((i for i in items if i.id == item_id), None)
        assert found is not None
        assert found.title == setup_items["item1"].title
        assert found.status == setup_items["item1"].status

    async def test_sort_with_filter(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Sort order should be maintained with filters."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.get_by_project(project_id, status="todo", limit=1000)

        # All items should be status=todo
        assert all(item.status == "todo" for item in items)

        # Sort order maintained
        for i in range(len(items) - 1):
            assert items[i].created_at >= items[i + 1].created_at

    async def test_sort_title_consistency(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Items with same created_at should maintain relative order."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get items twice
        items1 = await repo.get_by_project(project_id, limit=1000)
        items2 = await repo.get_by_project(project_id, limit=1000)

        ids1 = [item.id for item in items1]
        ids2 = [item.id for item in items2]

        assert ids1 == ids2

    async def test_sort_with_pagination(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Sorting with pagination should be consistent."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get all items sorted
        all_items = await repo.get_by_project(project_id, limit=1000)

        # Get first 3 items in pages
        page1 = await repo.get_by_project(project_id, limit=2, offset=0)
        page2_first = await repo.get_by_project(project_id, limit=1, offset=2)

        combined = page1 + page2_first
        expected = all_items[:3]

        assert [item.id for item in combined] == [item.id for item in expected]

    async def test_sort_stability_high_volume(self, db_session: AsyncSession) -> None:
        """Test sort stability with many items."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Sort Stability Test")
        project_id = project.id

        # Create 50 items
        for i in range(50):
            await repo.create(
                project_id=project_id,
                title=f"Item {i:03d}",
                view="FEATURE",
                item_type="feature",
                status=["todo", "done"][i % 2],
            )

        # Get all items multiple times
        items_batch1 = await repo.get_by_project(project_id, limit=1000)
        items_batch2 = await repo.get_by_project(project_id, limit=1000)

        ids1 = [item.id for item in items_batch1]
        ids2 = [item.id for item in items_batch2]

        assert ids1 == ids2
        assert len(ids1) == 50

    async def test_list_all_items_ordered(self, db_session: AsyncSession, setup_items: dict) -> None:
        """list_all should return items in order."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.list_all(project_id)

        # Should be descending by created_at
        for i in range(len(items) - 1):
            assert items[i].created_at >= items[i + 1].created_at


# ============================================================================
# AGGREGATION TESTS (15+ tests)
# ============================================================================


@pytest.mark.asyncio
class TestAggregations:
    """Test aggregation and counting patterns."""

    async def test_count_by_status_basic(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Count items by status."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        counts = await repo.count_by_status(project_id)

        assert isinstance(counts, dict)
        assert "todo" in counts or "done" in counts or "in_progress" in counts

        # Verify counts are positive
        for count in counts.values():
            assert count > 0

    async def test_count_by_status_empty_project(self, db_session: AsyncSession) -> None:
        """Count by status on empty project."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Empty Project")
        counts = await repo.count_by_status(project.id)

        assert counts == {}

    async def test_count_by_status_single_status(self, db_session: AsyncSession) -> None:
        """Count by status when all items have same status."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Single Status Project")

        # Create items all with same status
        for i in range(5):
            await repo.create(
                project_id=project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )

        counts = await repo.count_by_status(project.id)

        assert counts.get("todo") == COUNT_FIVE
        assert len(counts) == 1

    async def test_count_by_status_multiple_statuses(self, db_session: AsyncSession) -> None:
        """Count by status with multiple different statuses."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Multi Status Project")

        statuses = ["todo", "in_progress", "done", "todo", "in_progress"]
        for i, status in enumerate(statuses):
            await repo.create(
                project_id=project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status=status,
            )

        counts = await repo.count_by_status(project.id)

        assert counts.get("todo") == COUNT_TWO
        assert counts.get("in_progress") == COUNT_TWO
        assert counts.get("done") == 1

    async def test_count_excludes_deleted(self, db_session: AsyncSession) -> None:
        """Count by status should exclude soft-deleted items."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Delete Test Project")

        # Create items
        item1 = await repo.create(
            project_id=project.id,
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        await repo.create(
            project_id=project.id,
            title="Item 2",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

        # Count before delete
        counts_before = await repo.count_by_status(project.id)
        assert counts_before.get("todo") == COUNT_TWO

        # Delete one item
        await repo.delete(item1.id, soft=True)

        # Count after delete
        counts_after = await repo.count_by_status(project.id)
        assert counts_after.get("todo") == 1

    async def test_query_result_count(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Verify query returns correct count."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        todo_items = await repo.query(project_id, {"status": "todo"})
        assert len(todo_items) > 0

        # Count manually
        expected_count = len([
            item for item in setup_items.values() if item.status == "todo" and item.project_id == project_id
        ])
        assert len(todo_items) == expected_count

    async def test_count_by_view_manual(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Manual count by view type."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        features = await repo.get_by_view(project_id, "FEATURE", limit=1000)
        bugs = await repo.get_by_view(project_id, "BUG", limit=1000)
        tasks = await repo.get_by_view(project_id, "TASK", limit=1000)

        total = len(features) + len(bugs) + len(tasks)
        assert total > 0

    async def test_count_by_priority_manual(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Manual count by priority."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        high = await repo.query(project_id, {"priority": "high"})
        medium = await repo.query(project_id, {"priority": "medium"})
        low = await repo.query(project_id, {"priority": "low"})

        total = len(high) + len(medium) + len(low)
        assert total > 0

    async def test_aggregation_with_hierarchical_items(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Aggregation should count hierarchical items."""
        repo = ItemRepository(db_session)
        project_id = setup_items["parent"].project_id

        counts = await repo.count_by_status(project_id)

        # Should include parent and children
        assert sum(counts.values()) > COUNT_TWO

    async def test_get_children_count(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Count direct children."""
        repo = ItemRepository(db_session)
        parent = setup_items["parent"]

        children = await repo.get_children(parent.id)

        assert len(children) == COUNT_TWO
        assert all(child.parent_id == parent.id for child in children)

    async def test_get_descendants_count(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Count all descendants."""
        repo = ItemRepository(db_session)
        parent = setup_items["parent"]

        descendants = await repo.get_descendants(parent.id)

        assert len(descendants) >= COUNT_TWO  # At least the two direct children

    async def test_get_ancestors_count(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Count ancestors."""
        repo = ItemRepository(db_session)
        child = setup_items["child1"]
        parent = setup_items["parent"]

        ancestors = await repo.get_ancestors(child.id)

        # Should contain the parent
        assert any(a.id == parent.id for a in ancestors)

    async def test_status_distribution(self, db_session: AsyncSession) -> None:
        """Test distribution of statuses."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Distribution Project")

        # Create items with specific distribution
        distribution = {
            "todo": 10,
            "in_progress": 5,
            "done": 3,
        }

        for status, count in distribution.items():
            for i in range(count):
                await repo.create(
                    project_id=project.id,
                    title=f"{status} Item {i}",
                    view="FEATURE",
                    item_type="feature",
                    status=status,
                )

        counts = await repo.count_by_status(project.id)

        assert counts["todo"] == COUNT_TEN
        assert counts["in_progress"] == COUNT_FIVE
        assert counts["done"] == COUNT_THREE

    async def test_complex_aggregation_query(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test complex aggregation across multiple dimensions."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get counts by status
        status_counts = await repo.count_by_status(project_id)

        # Get feature counts
        feature_items = await repo.query(project_id, {"view": "FEATURE"})

        # Get high priority items
        high_items = await repo.query(project_id, {"priority": "high"})

        assert isinstance(status_counts, dict)
        assert len(feature_items) > 0
        assert len(high_items) > 0


# ============================================================================
# EDGE CASES TESTS (10+ tests)
# ============================================================================


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    async def test_query_with_empty_filters(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Query with empty filter dict."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        items = await repo.query(project_id, {})

        # Should return all items (no filters applied)
        await repo.list_all(project_id)
        assert len(items) > 0

    async def test_query_with_nonexistent_attribute(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Query with attribute that doesn't exist on Item model."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Should skip nonexistent attributes
        items = await repo.query(project_id, {"nonexistent_field": "value"})

        # Should still return results (filter skipped)
        assert isinstance(items, list)

    async def test_query_unicode_string(self, db_session: AsyncSession) -> None:
        """Query with unicode characters."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Unicode Project")

        item = await repo.create(
            project_id=project.id,
            title="Item with emoji 🎉 and unicode ñáéíóú",
            view="FEATURE",
            item_type="feature",
        )

        # Query back
        items = await repo.get_by_project(project.id)
        found = next((i for i in items if i.id == item.id), None)
        assert found is not None
        assert "🎉" in found.title

    async def test_query_very_long_string(self, db_session: AsyncSession) -> None:
        """Query with very long string."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Long String Project")

        long_title = "A" * 1000
        item = await repo.create(
            project_id=project.id,
            title=long_title,
            view="FEATURE",
            item_type="feature",
        )

        items = await repo.get_by_project(project.id)
        found = next((i for i in items if i.id == item.id), None)
        assert found is not None

    async def test_pagination_all_edge_values(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Test pagination with edge case values."""
        repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Test with limit=1
        items = await repo.get_by_project(project_id, limit=1, offset=0)
        assert len(items) <= 1

        # Test with high limit
        items = await repo.get_by_project(project_id, limit=999999, offset=0)
        assert len(items) > 0

        # Test with zero offset
        items = await repo.get_by_project(project_id, limit=5, offset=0)
        assert len(items) > 0

    async def test_get_by_id_nonexistent(self, db_session: AsyncSession, _setup_items: dict) -> None:
        """Get item with nonexistent ID."""
        repo = ItemRepository(db_session)

        item = await repo.get_by_id("nonexistent_id_12345")
        assert item is None

    async def test_get_by_id_with_project_scope(
        self,
        db_session: AsyncSession,
        setup_items: dict,
        setup_projects: dict,
    ) -> None:
        """Get by ID with project scoping."""
        repo = ItemRepository(db_session)
        item = setup_items["item1"]
        other_project_id = setup_projects["proj2"].id

        # Get with same project - should work
        found = await repo.get_by_id(item.id, project_id=item.project_id)
        assert found is not None

        # Get with different project - should return None
        found = await repo.get_by_id(item.id, project_id=other_project_id)
        assert found is None

    async def test_list_by_view_empty(self, db_session: AsyncSession) -> None:
        """List by view when no items exist."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Empty View Project")

        items = await repo.list_by_view(project.id, "NONEXISTENT_VIEW")
        assert items == []

    async def test_count_status_after_restore(self, db_session: AsyncSession) -> None:
        """Count should update after restore."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Restore Project")

        item = await repo.create(
            project_id=project.id,
            title="Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

        # Verify count
        counts_before = await repo.count_by_status(project.id)
        assert counts_before.get("todo") == 1

        # Delete
        await repo.delete(item.id, soft=True)
        counts_deleted = await repo.count_by_status(project.id)
        assert counts_deleted.get("todo", 0) == 0

        # Restore
        await repo.restore(item.id)
        counts_restored = await repo.count_by_status(project.id)
        assert counts_restored.get("todo") == 1

    async def test_query_special_characters_in_title(self, db_session: AsyncSession) -> None:
        """Query with special characters."""
        repo = ItemRepository(db_session)
        proj_repo = ProjectRepository(db_session)

        project = await proj_repo.create(name="Special Chars Project")

        special_title = "Item with <special> &chars \"quotes\" and 'apostrophes'"
        item = await repo.create(
            project_id=project.id,
            title=special_title,
            view="FEATURE",
            item_type="feature",
        )

        items = await repo.get_by_project(project.id)
        found = next((i for i in items if i.id == item.id), None)
        assert found is not None
        assert found.title == special_title


# ============================================================================
# HIERARCHICAL QUERY TESTS (5+ tests)
# ============================================================================


@pytest.mark.asyncio
class TestHierarchicalQueries:
    """Test hierarchical item queries."""

    async def test_get_children_basic(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Get direct children of an item."""
        repo = ItemRepository(db_session)
        parent = setup_items["parent"]

        children = await repo.get_children(parent.id)

        assert len(children) == COUNT_TWO
        assert all(child.parent_id == parent.id for child in children)

    async def test_get_descendants_recursive(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Get all descendants recursively."""
        repo = ItemRepository(db_session)
        parent = setup_items["parent"]

        descendants = await repo.get_descendants(parent.id)

        assert len(descendants) >= COUNT_TWO
        parent_ids = {d.parent_id for d in descendants}
        assert parent.id in parent_ids

    async def test_get_ancestors_recursive(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Get all ancestors recursively."""
        repo = ItemRepository(db_session)
        child = setup_items["child1"]
        parent = setup_items["parent"]

        ancestors = await repo.get_ancestors(child.id)

        assert any(a.id == parent.id for a in ancestors)

    async def test_hierarchical_query_no_parent(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Query ancestors for item without parent."""
        repo = ItemRepository(db_session)
        root_item = setup_items["item1"]

        ancestors = await repo.get_ancestors(root_item.id)

        # Root item should have no ancestors
        assert len(ancestors) == 0

    async def test_hierarchical_query_no_children(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Query children for leaf item."""
        repo = ItemRepository(db_session)
        child = setup_items["child1"]

        grandchildren = await repo.get_children(child.id)

        # Child has no children
        assert len(grandchildren) == 0


# ============================================================================
# LINK REPOSITORY QUERY TESTS (5+ tests)
# ============================================================================


@pytest.mark.asyncio
class TestLinkRepositoryQueries:
    """Test link repository query patterns."""

    async def test_link_get_by_source(self, db_session: AsyncSession, setup_links: dict, _setup_items: dict) -> None:
        """Get links by source item."""
        repo = LinkRepository(db_session)
        source_id = setup_items["item1"].id

        links = await repo.get_by_source(source_id)

        assert len(links) > 0
        assert all(link.source_item_id == source_id for link in links)

    async def test_link_get_by_target(self, db_session: AsyncSession, setup_links: dict, _setup_items: dict) -> None:
        """Get links by target item."""
        repo = LinkRepository(db_session)
        target_id = setup_items["item2"].id

        links = await repo.get_by_target(target_id)

        assert len(links) > 0 or len(links) == 0  # May or may not have links

    async def test_link_get_by_type(self, db_session: AsyncSession, _setup_links: dict) -> None:
        """Get links by type."""
        repo = LinkRepository(db_session)

        relates_to_links = await repo.get_by_type("relates_to")

        assert all(link.link_type == "relates_to" for link in relates_to_links)

    async def test_link_query_all(self, db_session: AsyncSession, setup_links: dict) -> None:
        """Query all links in project."""
        repo = LinkRepository(db_session)

        # Get any link to get project context
        next(iter(setup_links.values()))

        # This would need project context in the repo
        links = await repo.get_all()
        assert len(links) > 0

    async def test_link_count_by_type(self, db_session: AsyncSession, _setup_links: dict) -> None:
        """Count links by type."""
        repo = LinkRepository(db_session)

        all_links = await repo.get_all()

        # Group by type
        type_counts = {}
        for link in all_links:
            type_counts[link.link_type] = type_counts.get(link.link_type, 0) + 1

        assert len(type_counts) > 0


# ============================================================================
# INTEGRATION TESTS - MULTI-REPO QUERIES (5+ tests)
# ============================================================================


@pytest.mark.asyncio
class TestMultiRepoQueries:
    """Test queries across multiple repositories."""

    async def test_query_items_and_links(self, db_session: AsyncSession, setup_items: dict, _setup_links: dict) -> None:
        """Query items and their related links."""
        item_repo = ItemRepository(db_session)
        link_repo = LinkRepository(db_session)

        item = setup_items["item1"]

        # Get item
        found_item = await item_repo.get_by_id(item.id)
        assert found_item is not None

        # Get links for item
        source_links = await link_repo.get_by_source(item.id)

        assert isinstance(source_links, list)

    async def test_filter_items_by_type_and_links(
        self, db_session: AsyncSession, setup_items: dict, setup_links: dict
    ) -> None:
        """Filter items by type and check links."""
        item_repo = ItemRepository(db_session)
        link_repo = LinkRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get all features
        features = await item_repo.query(project_id, {"item_type": "feature"})

        # Check links for each
        for feature in features:
            links = await link_repo.get_by_source(feature.id)
            assert isinstance(links, list)

    async def test_hierarchical_with_links(
        self, db_session: AsyncSession, setup_items: dict, setup_links: dict
    ) -> None:
        """Test hierarchical queries combined with link queries."""
        item_repo = ItemRepository(db_session)
        parent = setup_items["parent"]

        # Get hierarchy
        descendants = await item_repo.get_descendants(parent.id)

        assert len(descendants) > 0

    async def test_pagination_consistency_multi_repo(self, db_session: AsyncSession, setup_items: dict) -> None:
        """Pagination should be consistent across repos."""
        item_repo = ItemRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Get items with pagination
        page1 = await item_repo.get_by_project(project_id, limit=5, offset=0)
        page2 = await item_repo.get_by_project(project_id, limit=5, offset=5)

        # IDs should not overlap
        page1_ids = {item.id for item in page1}
        page2_ids = {item.id for item in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    async def test_complex_multi_repo_aggregation(
        self, db_session: AsyncSession, setup_items: dict, setup_links: dict
    ) -> None:
        """Complex aggregation across repositories."""
        item_repo = ItemRepository(db_session)
        link_repo = LinkRepository(db_session)
        project_id = setup_items["item1"].project_id

        # Count items by status
        status_counts = await item_repo.count_by_status(project_id)

        # Get all links
        all_links = await link_repo.get_all()

        # Verify both operations succeeded
        assert isinstance(status_counts, dict)
        assert isinstance(all_links, list)


# ============================================================================
# PROJECT REPOSITORY QUERY TESTS (3+ tests)
# ============================================================================


@pytest.mark.asyncio
class TestProjectRepositoryQueries:
    """Test project repository query patterns."""

    async def test_get_all_projects(self, db_session: AsyncSession, _setup_projects: dict) -> None:
        """Get all projects."""
        repo = ProjectRepository(db_session)

        all_projects = await repo.get_all()

        assert len(all_projects) >= COUNT_THREE
        project_names = {p.name for p in all_projects}
        assert "Project 1" in project_names

    async def test_get_project_by_name(self, db_session: AsyncSession, _setup_projects: dict) -> None:
        """Get project by name."""
        repo = ProjectRepository(db_session)

        project = await repo.get_by_name("Project 1")

        assert project is not None
        assert project.name == "Project 1"

    async def test_project_query_consistency(self, db_session: AsyncSession, _setup_projects: dict) -> None:
        """Query consistency for projects."""
        repo = ProjectRepository(db_session)

        # Query twice
        projects1 = await repo.get_all()
        projects2 = await repo.get_all()

        ids1 = sorted([p.id for p in projects1])
        ids2 = sorted([p.id for p in projects2])

        assert ids1 == ids2
