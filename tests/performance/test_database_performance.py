"""Database query performance benchmarks.

Tests measure performance of:
- Single row lookups (indexed)
- Multi-row queries with filtering
- Join operations
- Aggregation queries
- Bulk insert performance
"""

from typing import Any
from tests.test_constants import COUNT_THREE


import pytest
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

pytestmark = pytest.mark.performance


# ============================================================
# Test Fixtures
# ============================================================


@pytest.fixture
def seed_items_1000(db_session: Session) -> list[dict[str, Any]]:
    """Seed 1000 items in database."""
    from tracertm.models.item import Item

    items = []
    for i in range(1000):
        item = Item(
            id=f"item-{i}",
            project_id="perf-proj",
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature" if i % 2 == 0 else "requirement",
            status=["todo", "in_progress", "done"][i % 3],
            priority=["low", "medium", "high"][i % 3],
            owner=f"user-{i % 10}" if i % 2 == 0 else None,
            version=1,
        )
        items.append(item)
        db_session.add(item)

    db_session.commit()
    return items


@pytest.fixture
def seed_items_with_links(db_session: Session):
    """Seed items with link relationships."""
    from tracertm.models.item import Item
    from tracertm.models.link import Link

    # Create 100 items
    items = []
    for i in range(100):
        item = Item(
            id=f"item-{i}",
            project_id="perf-proj",
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        items.append(item)
        db_session.add(item)

    db_session.flush()

    # Create links between items
    for i in range(50):
        link = Link(
            id=f"link-{i}",
            project_id="perf-proj",
            source_id=f"item-{i}",
            target_id=f"item-{(i + 1) % 100}",
            link_type="depends_on",
        )
        db_session.add(link)

    db_session.commit()
    return {"items": items, "link_count": 50}


# ============================================================
# Index Lookup Performance
# ============================================================


def test_item_lookup_by_id_indexed(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark indexed primary key lookup."""
    from tracertm.models.item import Item

    def lookup():
        result = db_session.query(Item).filter(Item.id == "item-500").first()
        return result is not None

    result = benchmark(lookup)
    assert result is True


def test_item_lookup_by_project_indexed(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark indexed project_id lookup."""
    from tracertm.models.item import Item

    def lookup():
        result = db_session.query(Item).filter(Item.project_id == "perf-proj").first()
        return result is not None

    result = benchmark(lookup)
    assert result is True


def test_item_lookup_by_status_indexed(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark status index lookup."""
    from tracertm.models.item import Item

    def lookup():
        result = db_session.query(Item).filter(Item.status == "done").first()
        return result is not None

    result = benchmark(lookup)
    assert result is True


# ============================================================
# Multi-Row Query Performance
# ============================================================


def test_query_all_items_1000(benchmark, db_session: Session, seed_items_1000, perf_tracker) -> None:  # noqa: ARG001
    """Benchmark querying all 1000 items."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(Item).all()

    result = benchmark(query)
    assert len(result) == 1000


def test_query_items_with_filter_status_500(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark filtering query returning ~333 items."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(Item).filter(Item.status == "todo").all()

    result = benchmark(query)
    assert len(result) == 334  # 1000 % 3 == 334 items with "todo" status


def test_query_items_with_multiple_filters(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark query with multiple filter conditions."""
    from tracertm.models.item import Item

    def query():
        return (
            db_session
            .query(Item)
            .filter(and_(Item.status == "todo", Item.item_type == "feature", Item.priority == "high"))
            .all()
        )

    result = benchmark(query)
    assert len(result) > 0


def test_query_items_with_or_conditions(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark query with OR conditions."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(Item).filter(or_(Item.status == "done", Item.priority == "high")).all()

    result = benchmark(query)
    assert len(result) > 0


# ============================================================
# Pagination Performance
# ============================================================


def test_query_items_pagination_first_page(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark paginated query - first page."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(Item).limit(20).offset(0).all()

    result = benchmark(query)
    assert len(result) == 20


def test_query_items_pagination_middle_page(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark paginated query - middle page."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(Item).limit(20).offset(500).all()

    result = benchmark(query)
    assert len(result) == 20


def test_query_items_pagination_last_page(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark paginated query - last page."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(Item).limit(20).offset(980).all()

    result = benchmark(query)
    assert len(result) == 20


# ============================================================
# Join Query Performance
# ============================================================


def test_query_items_with_links_join(benchmark, db_session: Session, seed_items_with_links) -> None:  # noqa: ARG001
    """Benchmark query with join."""
    from tracertm.models.item import Item
    from tracertm.models.link import Link

    def query():
        return db_session.query(Item).join(Link, Item.id == Link.source_item_id).all()

    result = benchmark(query)
    assert len(result) == 50  # Number of items with outgoing links


# ============================================================
# Aggregation Query Performance
# ============================================================


def test_aggregation_count_items(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark count aggregation."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(func.count(Item.id)).scalar()

    result = benchmark(query)
    assert result == 1000


def test_aggregation_group_by_status(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark group by aggregation."""
    from tracertm.models.item import Item

    def query():
        return db_session.query(Item.status, func.count(Item.id)).group_by(Item.status).all()

    result = benchmark(query)
    assert len(result) == COUNT_THREE  # 3 different statuses


def test_aggregation_multiple_grouping(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark multi-column group by."""
    from tracertm.models.item import Item

    def query():
        return (
            db_session
            .query(Item.status, Item.item_type, func.count(Item.id))
            .group_by(Item.status, Item.item_type)
            .all()
        )

    result = benchmark(query)
    assert len(result) > 0


# ============================================================
# Bulk Insert Performance
# ============================================================


def test_bulk_insert_100_items(benchmark, db_session: Session, perf_tracker) -> None:
    """Benchmark bulk insert of 100 items."""
    from tracertm.models.item import Item

    def insert() -> None:
        for i in range(100):
            item = Item(
                id=f"bulk-item-{i}",
                project_id="perf-proj-bulk",
                title=f"Bulk Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            db_session.add(item)
        db_session.commit()

    benchmark(insert)
    perf_tracker.record("bulk_insert_100", benchmark.stats.mean * 1000)


def test_bulk_insert_batch_500_items(benchmark, db_session: Session) -> None:
    """Benchmark bulk insert with batching - 500 items."""
    from tracertm.models.item import Item

    def insert() -> None:
        items = [
            Item(
                id=f"batch-item-{i}",
                project_id="perf-proj-batch",
                title=f"Batch Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            for i in range(500)
        ]
        db_session.bulk_save_objects(items)
        db_session.commit()

    benchmark(insert)


# ============================================================
# Update Performance
# ============================================================


def test_single_item_update(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark single item update."""
    from tracertm.models.item import Item

    def update() -> None:
        item = db_session.query(Item).filter(Item.id == "item-0").first()
        item.status = "done"
        db_session.commit()

    benchmark(update)


def test_bulk_update_100_items(benchmark, db_session: Session) -> None:
    """Benchmark bulk update of 100 items."""
    from tracertm.models.item import Item

    # Create items first
    for i in range(100):
        item = Item(
            id=f"update-item-{i}",
            project_id="perf-proj-update",
            title=f"Update Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
    db_session.commit()

    def update() -> None:
        db_session.query(Item).filter(Item.project_id == "perf-proj-update").update({"status": "done"})
        db_session.commit()

    benchmark(update)


# ============================================================
# Delete Performance
# ============================================================


_delete_call_count = [0]


def test_single_item_delete(benchmark, db_session: Session, seed_items_1000) -> None:  # noqa: ARG001
    """Benchmark single item delete."""
    from tracertm.models.item import Item

    # Counter to get different items each time
    _delete_call_count[0] += 1
    item_id = f"item-{900 + _delete_call_count[0]}"

    def delete() -> None:
        db_session.query(Item).filter(Item.id == item_id).delete()
        db_session.commit()

    benchmark(delete)
