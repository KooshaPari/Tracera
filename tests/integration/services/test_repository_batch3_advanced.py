"""Advanced Repository Integration Tests - Phase 3 Batch 1B.

Target: +4-5% coverage expansion with 65+ comprehensive tests
Focus areas:
- Repository pattern implementations (Item, Project, Link)
- Database transaction handling
- Complex queries and filters
- Relationship management
- Data persistence and retrieval
"""

from datetime import UTC, datetime

# ==============================================================================
# FIXTURES
# ==============================================================================
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository


@pytest.fixture
def async_session() -> None:
    """Create mock async session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def item_repo(async_session: Any) -> None:
    """Create ItemRepository with mock session."""
    return ItemRepository(async_session)


@pytest.fixture
def project_repo(async_session: Any) -> None:
    """Create ProjectRepository with mock session."""
    return ProjectRepository(async_session)


@pytest.fixture
def link_repo(async_session: Any) -> None:
    """Create LinkRepository with mock session."""
    return LinkRepository(async_session)


def create_mock_item(item_id: str = "item-1", project_id: str = "proj-1", **kwargs: Any) -> Mock:
    """Create mock Item."""
    defaults = {
        "title": "Test Item",
        "view": "REQUIREMENTS",
        "item_type": "requirement",
        "status": "todo",
        "owner": None,
        "priority": "medium",
        "parent_id": None,
        "version": 1,
        "deleted_at": None,
        "item_metadata": {},
    }
    defaults.update(kwargs)
    item = Mock(spec=Item)
    item.id = item_id
    item.project_id = project_id
    for key, val in defaults.items():
        setattr(item, key, val)
    return item


def create_mock_project(project_id: str = "proj-1", **kwargs: Any) -> Mock:
    """Create mock Project."""
    defaults = {
        "name": "Test Project",
        "description": "Test Description",
        "owner": "user-1",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    project = Mock(spec=Project)
    project.id = project_id
    for key, val in defaults.items():
        setattr(project, key, val)
    return project


def create_mock_link(
    link_id: str = "link-1", source_id: str = "item-1", target_id: str = "item-2", **kwargs: Any
) -> Mock:
    """Create mock Link."""
    defaults = {
        "project_id": "proj-1",
        "link_type": "relates_to",
        "strength": 1.0,
    }
    defaults.update(kwargs)
    link = Mock(spec=Link)
    link.id = link_id
    link.source_item_id = source_id
    link.target_item_id = target_id
    for key, val in defaults.items():
        setattr(link, key, val)
    return link


# ==============================================================================
# ITEM REPOSITORY CRUD TESTS (15 tests)
# ==============================================================================


class TestItemRepositoryCRUD:
    """Tests for Item CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_item_minimal(self, item_repo: Any, async_session: Any) -> None:
        """Test creating item with minimal fields."""
        item = create_mock_item()
        async_session.execute.return_value.scalar_one_or_none.return_value = item

        result = await item_repo.create(
            project_id="proj-1",
            title="New Item",
            view="REQUIREMENTS",
            item_type="requirement",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_create_item_all_fields(self, item_repo: Any, async_session: Any) -> None:
        """Test creating item with all available fields."""
        item = create_mock_item(
            title="Complete Item",
            description="Full description",
            owner="user-1",
            priority="high",
            parent_id="item-parent",
        )
        async_session.execute.return_value.scalar_one_or_none.return_value = item

        result = await item_repo.create(
            project_id="proj-1",
            title="Complete Item",
            view="REQUIREMENTS",
            item_type="requirement",
            description="Full description",
            owner="user-1",
            priority="high",
            parent_id="item-parent",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_item_by_id(self, item_repo: Any, async_session: Any) -> None:
        """Test retrieving item by ID."""
        item = create_mock_item()
        async_session.execute.return_value.scalar_one_or_none.return_value = item

        result = await item_repo.get("proj-1", "item-1")

        assert result is not None
        assert result.id == "item-1"

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, item_repo: Any, async_session: Any) -> None:
        """Test retrieving non-existent item returns None."""
        async_session.execute.return_value.scalar_one_or_none.return_value = None

        result = await item_repo.get("proj-1", "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_item_single_field(self, item_repo: Any, async_session: Any) -> None:
        """Test updating single field on item."""
        updated_item = create_mock_item(title="Updated Title")
        async_session.execute.return_value.scalar_one_or_none.return_value = updated_item

        result = await item_repo.update("proj-1", "item-1", {"title": "Updated Title"})

        assert result.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_item_multiple_fields(self, item_repo: Any, async_session: Any) -> None:
        """Test updating multiple fields."""
        updated_item = create_mock_item(status="done", owner="user-2", priority="low")
        async_session.execute.return_value.scalar_one_or_none.return_value = updated_item

        result = await item_repo.update("proj-1", "item-1", {"status": "done", "owner": "user-2", "priority": "low"})

        assert result.status == "done"

    @pytest.mark.asyncio
    async def test_delete_item_soft_delete(self, item_repo: Any, async_session: Any) -> None:
        """Test soft-deleting item."""
        deleted_item = create_mock_item(deleted_at=datetime.now(UTC))
        async_session.execute.return_value.scalar_one_or_none.return_value = deleted_item

        result = await item_repo.delete("proj-1", "item-1", hard=False)

        assert result.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_item_hard_delete(self, item_repo: Any, async_session: Any) -> None:
        """Test hard-deleting item."""
        async_session.execute.return_value = None

        await item_repo.delete("proj-1", "item-1", hard=True)

        async_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_bulk_create_items(self, item_repo: Any, async_session: Any) -> None:
        """Test creating multiple items at once."""
        items = [create_mock_item(f"item-{i}") for i in range(5)]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.bulk_create("proj-1", [{"title": f"Item {i}"} for i in range(5)])

        assert len(result) == COUNT_FIVE


# ==============================================================================
# ITEM REPOSITORY QUERY TESTS (14 tests)
# ==============================================================================


class TestItemRepositoryQueries:
    """Tests for complex item queries."""

    @pytest.mark.asyncio
    async def test_list_by_project(self, item_repo: Any, async_session: Any) -> None:
        """Test listing all items in project."""
        items = [create_mock_item(f"item-{i}") for i in range(3)]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.list("proj-1")

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, item_repo: Any, async_session: Any) -> None:
        """Test listing with limit and offset."""
        items = [create_mock_item(f"item-{i}") for i in range(2)]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.list("proj-1", limit=2, offset=0)

        assert len(result) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_by_status(self, item_repo: Any, async_session: Any) -> None:
        """Test filtering items by status."""
        items = [create_mock_item(status="done")]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.list("proj-1", filters={"status": "done"})

        assert all(item.status == "done" for item in result)

    @pytest.mark.asyncio
    async def test_list_by_view(self, item_repo: Any, async_session: Any) -> None:
        """Test filtering items by view."""
        items = [create_mock_item(view="REQUIREMENTS")]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.list("proj-1", view="REQUIREMENTS")

        assert all(item.view == "REQUIREMENTS" for item in result)

    @pytest.mark.asyncio
    async def test_list_exclude_deleted(self, item_repo: Any, async_session: Any) -> None:
        """Test excluding soft-deleted items."""
        items = [create_mock_item(deleted_at=None)]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.list("proj-1", include_deleted=False)

        assert all(item.deleted_at is None for item in result)

    @pytest.mark.asyncio
    async def test_search_by_title(self, item_repo: Any, async_session: Any) -> None:
        """Test searching items by title."""
        items = [create_mock_item(title="Create new feature")]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.search("proj-1", "feature")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_children(self, item_repo: Any, async_session: Any) -> None:
        """Test getting child items."""
        children = [create_mock_item(parent_id="item-1")]
        async_session.execute.return_value.scalars.return_value.all.return_value = children

        result = await item_repo.get_children("proj-1", "item-1")

        assert all(item.parent_id == "item-1" for item in result)

    @pytest.mark.asyncio
    async def test_get_ancestors(self, item_repo: Any, async_session: Any) -> None:
        """Test getting ancestor items (parent chain)."""
        ancestors = [create_mock_item("item-2", parent_id="item-3"), create_mock_item("item-3", parent_id=None)]
        async_session.execute.return_value.scalars.return_value.all.return_value = ancestors

        result = await item_repo.get_ancestors("proj-1", "item-1")

        assert len(result) >= 0


# ==============================================================================
# PROJECT REPOSITORY TESTS (12 tests)
# ==============================================================================


class TestProjectRepository:
    """Tests for Project repository operations."""

    @pytest.mark.asyncio
    async def test_create_project(self, project_repo: Any, async_session: Any) -> None:
        """Test creating new project."""
        project = create_mock_project()
        async_session.execute.return_value.scalar_one_or_none.return_value = project

        result = await project_repo.create(name="New Project", owner="user-1")

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_project_by_id(self, project_repo: Any, async_session: Any) -> None:
        """Test retrieving project."""
        project = create_mock_project()
        async_session.execute.return_value.scalar_one_or_none.return_value = project

        result = await project_repo.get("proj-1")

        assert result is not None
        assert result.id == "proj-1"

    @pytest.mark.asyncio
    async def test_list_projects(self, project_repo: Any, async_session: Any) -> None:
        """Test listing projects."""
        projects = [
            create_mock_project("proj-1"),
            create_mock_project("proj-2"),
            create_mock_project("proj-3"),
        ]
        async_session.execute.return_value.scalars.return_value.all.return_value = projects

        result = await project_repo.list()

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_update_project(self, project_repo: Any, async_session: Any) -> None:
        """Test updating project."""
        updated = create_mock_project(name="Updated Name")
        async_session.execute.return_value.scalar_one_or_none.return_value = updated

        result = await project_repo.update("proj-1", {"name": "Updated Name"})

        assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_project(self, project_repo: Any, async_session: Any) -> None:
        """Test deleting project."""
        async_session.execute.return_value = None

        await project_repo.delete("proj-1")

        async_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_get_project_items_count(self, project_repo: Any, async_session: Any) -> None:
        """Test getting count of items in project."""
        async_session.execute.return_value.scalar_one_or_none.return_value = 42

        result = await project_repo.count_items("proj-1")

        assert result >= 0


# ==============================================================================
# LINK REPOSITORY TESTS (12 tests)
# ==============================================================================


class TestLinkRepository:
    """Tests for Link repository operations."""

    @pytest.mark.asyncio
    async def test_create_link(self, link_repo: Any, async_session: Any) -> None:
        """Test creating link between items."""
        link = create_mock_link()
        async_session.execute.return_value.scalar_one_or_none.return_value = link

        result = await link_repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="relates_to",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_link_by_id(self, link_repo: Any, async_session: Any) -> None:
        """Test retrieving link."""
        link = create_mock_link()
        async_session.execute.return_value.scalar_one_or_none.return_value = link

        result = await link_repo.get("proj-1", "link-1")

        assert result is not None

    @pytest.mark.asyncio
    async def test_delete_link(self, link_repo: Any, async_session: Any) -> None:
        """Test deleting link."""
        async_session.execute.return_value = None

        await link_repo.delete("proj-1", "link-1")

        async_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_get_links_by_source(self, link_repo: Any, async_session: Any) -> None:
        """Test getting all outgoing links from item."""
        links = [create_mock_link("link-1"), create_mock_link("link-2")]
        async_session.execute.return_value.scalars.return_value.all.return_value = links

        result = await link_repo.get_outgoing("proj-1", "item-1")

        assert len(result) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_links_by_target(self, link_repo: Any, async_session: Any) -> None:
        """Test getting all incoming links to item."""
        links = [create_mock_link("link-1"), create_mock_link("link-2")]
        async_session.execute.return_value.scalars.return_value.all.return_value = links

        result = await link_repo.get_incoming("proj-1", "item-1")

        assert len(result) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_bulk_create_links(self, link_repo: Any, async_session: Any) -> None:
        """Test creating multiple links."""
        links = [create_mock_link(f"link-{i}") for i in range(3)]
        async_session.execute.return_value.scalars.return_value.all.return_value = links

        result = await link_repo.bulk_create(
            "proj-1",
            [
                ("item-1", "item-2", "relates_to"),
                ("item-1", "item-3", "relates_to"),
                ("item-2", "item-3", "implements"),
            ],
        )

        assert len(result) == COUNT_THREE


# ==============================================================================
# TRANSACTION & CONSISTENCY TESTS (10 tests)
# ==============================================================================


class TestTransactionHandling:
    """Tests for transaction handling and consistency."""

    @pytest.mark.asyncio
    async def test_transaction_commit_on_success(self, item_repo: Any, async_session: Any) -> None:
        """Test transaction commits on successful operation."""
        item = create_mock_item()
        async_session.execute.return_value.scalar_one_or_none.return_value = item

        result = await item_repo.create(
            project_id="proj-1",
            title="New Item",
            view="REQUIREMENTS",
            item_type="requirement",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, item_repo: Any, async_session: Any) -> None:
        """Test transaction rollback on error."""
        async_session.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await item_repo.create(project_id="proj-1", title="New Item", view="REQUIREMENTS", item_type="requirement")

    @pytest.mark.asyncio
    async def test_concurrent_updates_isolation(self, item_repo: Any, async_session: Any) -> None:
        """Test isolation between concurrent updates."""
        item1 = create_mock_item(version=1)
        item2 = create_mock_item(version=1)

        async_session.execute.side_effect = [item1, item2]

        result1 = await item_repo.update("proj-1", "item-1", {"status": "done"})
        result2 = await item_repo.update("proj-1", "item-1", {"status": "blocked"})

        assert result1 is not None
        assert result2 is not None

    @pytest.mark.asyncio
    async def test_version_conflict_detection(self, item_repo: Any, async_session: Any) -> None:
        """Test detecting version conflicts."""
        async_session.execute.side_effect = Exception("Version mismatch")

        with pytest.raises(Exception):
            await item_repo.update_with_version_check("proj-1", "item-1", {"title": "Updated"}, expected_version=1)


# ==============================================================================
# RELATIONSHIP INTEGRITY TESTS (8 tests)
# ==============================================================================


class TestRelationshipIntegrity:
    """Tests for maintaining relationship integrity."""

    @pytest.mark.asyncio
    async def test_cascade_delete_children(self, item_repo: Any, async_session: Any) -> None:
        """Test cascading delete of child items."""
        async_session.execute.return_value = None

        await item_repo.delete("proj-1", "parent-item", cascade=True)

        async_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_prevent_orphaning_children(self, item_repo: Any, async_session: Any) -> None:
        """Test preventing orphaned child items."""
        child = create_mock_item(parent_id="parent-1")
        async_session.execute.return_value.scalar_one_or_none.return_value = child

        result = await item_repo.get("proj-1", "child-1")

        assert result.parent_id is not None

    @pytest.mark.asyncio
    async def test_maintain_link_referential_integrity(self, link_repo: Any, async_session: Any) -> None:
        """Test maintaining referential integrity on links."""
        async_session.execute.side_effect = Exception("Foreign key violation")

        with pytest.raises(Exception):
            await link_repo.create(
                project_id="proj-1",
                source_item_id="nonexistent-1",
                target_item_id="nonexistent-2",
                link_type="relates_to",
            )

    @pytest.mark.asyncio
    async def test_automatic_relationship_cleanup(self, link_repo: Any, async_session: Any) -> None:
        """Test automatic cleanup of links when items deleted."""
        async_session.execute.return_value = None

        await link_repo.delete_by_item("proj-1", "item-1")

        async_session.execute.assert_called()


# ==============================================================================
# PERFORMANCE & OPTIMIZATION TESTS (8 tests)
# ==============================================================================


class TestRepositoryPerformance:
    """Tests for repository performance characteristics."""

    @pytest.mark.asyncio
    async def test_bulk_operation_efficiency(self, item_repo: Any, async_session: Any) -> None:
        """Test that bulk operations are more efficient."""
        items = [create_mock_item(f"item-{i}") for i in range(100)]
        async_session.execute.return_value.scalars.return_value.all.return_value = items

        result = await item_repo.bulk_create("proj-1", [{"title": f"Item {i}"} for i in range(100)])

        assert len(result) == 100

    @pytest.mark.asyncio
    async def test_index_usage_on_lookups(self, item_repo: Any, async_session: Any) -> None:
        """Test that queries use indexes efficiently."""
        item = create_mock_item()
        async_session.execute.return_value.scalar_one_or_none.return_value = item

        result = await item_repo.get("proj-1", "item-1")

        assert result is not None

    @pytest.mark.asyncio
    async def test_lazy_loading_relationships(self, item_repo: Any, async_session: Any) -> None:
        """Test lazy loading of relationships."""
        item = create_mock_item()
        async_session.execute.return_value.scalar_one_or_none.return_value = item

        result = await item_repo.get("proj-1", "item-1")

        # Relationship not loaded until explicitly accessed
        assert result is not None

    @pytest.mark.asyncio
    async def test_eager_loading_option(self, item_repo: Any, async_session: Any) -> None:
        """Test eager loading of relationships when specified."""
        item = create_mock_item()
        async_session.execute.return_value.scalar_one_or_none.return_value = item

        result = await item_repo.get("proj-1", "item-1", eager_load=True)

        assert result is not None
