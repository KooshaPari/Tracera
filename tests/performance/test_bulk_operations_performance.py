"""Bulk operation performance benchmarks.

Tests measure throughput and performance of:
- Bulk item creation (100, 500, 1000 items)
- Bulk item updates
- Bulk item deletion
- Bulk link creation
- Performance degradation with scale
"""

from typing import Any

import pytest
from sqlalchemy.orm import Session

pytestmark = pytest.mark.performance


# ============================================================
# Bulk Item Creation Performance
# ============================================================


def test_bulk_create_100_items(benchmark: Any, db_session: Session, _perf_tracker: Any) -> None:
    """Benchmark creation of 100 items."""
    from uuid import uuid4

    from tracertm.models.item import Item

    def create() -> None:
        for i in range(100):
            item = Item(
                id=f"create-100-{uuid4().hex[:8]}-{i}",
                project_id="bulk-perf-proj",
                title=f"Bulk Create Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="medium",
                version=1,
            )
            db_session.add(item)
        db_session.commit()

    benchmark(create)


def test_bulk_create_500_items(benchmark: Any, db_session: Session, _perf_tracker: Any) -> None:
    """Benchmark creation of 500 items."""
    from uuid import uuid4

    from tracertm.models.item import Item

    def create() -> None:
        for i in range(500):
            item = Item(
                id=f"create-500-{uuid4().hex[:8]}-{i}",
                project_id="bulk-perf-proj",
                title=f"Bulk Create Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="medium",
                version=1,
            )
            db_session.add(item)
        db_session.commit()

    benchmark(create)


def test_bulk_create_1000_items(benchmark: Any, db_session: Session, _perf_tracker: Any) -> None:
    """Benchmark creation of 1000 items."""
    from uuid import uuid4

    from tracertm.models.item import Item

    def create() -> None:
        for i in range(1000):
            item = Item(
                id=f"create-1000-{uuid4().hex[:8]}-{i}",
                project_id="bulk-perf-proj",
                title=f"Bulk Create Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="medium",
                version=1,
            )
            db_session.add(item)
        db_session.commit()

    benchmark(create)


def test_bulk_create_with_batch_insert(benchmark: Any, db_session: Session) -> None:
    """Benchmark bulk insert using batch operation (optimized)."""
    from uuid import uuid4

    from tracertm.models.item import Item

    def create() -> None:
        items = [
            Item(
                id=f"batch-create-{uuid4().hex[:8]}-{i}",
                project_id="bulk-perf-proj",
                title=f"Batch Create Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="medium",
                version=1,
            )
            for i in range(500)
        ]
        db_session.bulk_save_objects(items)
        db_session.commit()

    benchmark(create)


# ============================================================
# Bulk Update Performance
# ============================================================


def test_bulk_update_100_items(benchmark: Any, db_session: Session, _perf_tracker: Any) -> None:
    """Benchmark update of 100 items."""
    from tracertm.models.item import Item

    # Create items first
    for i in range(100):
        item = Item(
            id=f"update-100-{i}",
            project_id="bulk-update-proj",
            title=f"Update Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
    db_session.commit()

    def update() -> None:
        items = db_session.query(Item).filter(Item.project_id == "bulk-update-proj").all()

        for i, item in enumerate(items):
            item.status = ["todo", "in_progress", "done"][i % 3]
            item.priority = ["low", "medium", "high"][i % 3]

        db_session.commit()

    benchmark(update)


def test_bulk_update_500_items(benchmark: Any, db_session: Session) -> None:
    """Benchmark update of 500 items."""
    from tracertm.models.item import Item

    # Create items
    for i in range(500):
        item = Item(
            id=f"update-500-{i}",
            project_id="bulk-update-500-proj",
            title=f"Update Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
    db_session.commit()

    def update() -> None:
        items = db_session.query(Item).filter(Item.project_id == "bulk-update-500-proj").all()

        for i, item in enumerate(items):
            item.status = ["todo", "in_progress", "done"][i % 3]

        db_session.commit()

    benchmark(update)


def test_bulk_update_with_query_update(benchmark: Any, db_session: Session) -> None:
    """Benchmark bulk update using query.update() (optimized)."""
    from tracertm.models.item import Item

    # Create items
    for i in range(100):
        item = Item(
            id=f"query-update-{i}",
            project_id="query-update-proj",
            title=f"Query Update Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
    db_session.commit()

    def update() -> None:
        db_session.query(Item).filter(Item.project_id == "query-update-proj").update({"status": "done"})
        db_session.commit()

    benchmark(update)


# ============================================================
# Bulk Delete Performance
# ============================================================


def test_bulk_delete_100_items(benchmark: Any, db_session: Session) -> None:
    """Benchmark deletion of 100 items."""
    from tracertm.models.item import Item

    # Create items
    for i in range(100):
        item = Item(
            id=f"delete-100-{i}",
            project_id="bulk-delete-100-proj",
            title=f"Delete Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
    db_session.commit()

    def delete() -> None:
        db_session.query(Item).filter(Item.project_id == "bulk-delete-100-proj").delete()
        db_session.commit()

    benchmark(delete)


def test_bulk_delete_500_items(benchmark: Any, db_session: Session) -> None:
    """Benchmark deletion of 500 items."""
    from tracertm.models.item import Item

    # Create items
    for i in range(500):
        item = Item(
            id=f"delete-500-{i}",
            project_id="bulk-delete-500-proj",
            title=f"Delete Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        db_session.add(item)
    db_session.commit()

    def delete() -> None:
        db_session.query(Item).filter(Item.project_id == "bulk-delete-500-proj").delete()
        db_session.commit()

    benchmark(delete)


# ============================================================
# Bulk Link Creation Performance
# ============================================================


def test_bulk_create_links_100(benchmark: Any, db_session: Session) -> None:
    """Benchmark creation of 100 links."""
    from uuid import uuid4

    from tracertm.models.item import Item
    from tracertm.models.link import Link

    # Create source and target items with stable IDs
    source_ids = []
    target_ids = []
    for i in range(10):
        source_id = f"link-source-100-{i}"
        item = Item(
            id=source_id,
            project_id="bulk-link-proj",
            title=f"Link Source {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        source_ids.append(source_id)
        db_session.add(item)

        target_id = f"link-target-100-{i}"
        item = Item(
            id=target_id,
            project_id="bulk-link-proj",
            title=f"Link Target {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        target_ids.append(target_id)
        db_session.add(item)

    db_session.commit()

    def create() -> None:
        for i in range(100):
            link = Link(
                id=f"bulk-link-100-{uuid4().hex[:8]}-{i}",
                project_id="bulk-link-proj",
                source_id=source_ids[i % 10],
                target_id=target_ids[i % 10],
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

    benchmark(create)


def test_bulk_create_links_500(benchmark: Any, db_session: Session) -> None:
    """Benchmark creation of 500 links."""
    from uuid import uuid4

    from tracertm.models.item import Item
    from tracertm.models.link import Link

    # Create source and target items with stable IDs
    source_ids = []
    target_ids = []
    for i in range(50):
        source_id = f"link-source-500-{i}"
        item = Item(
            id=source_id,
            project_id="bulk-link-500-proj",
            title=f"Link Source {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        source_ids.append(source_id)
        db_session.add(item)

        target_id = f"link-target-500-{i}"
        item = Item(
            id=target_id,
            project_id="bulk-link-500-proj",
            title=f"Link Target {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        target_ids.append(target_id)
        db_session.add(item)

    db_session.commit()

    def create() -> None:
        for i in range(500):
            link = Link(
                id=f"bulk-link-500-{uuid4().hex[:8]}-{i}",
                project_id="bulk-link-500-proj",
                source_id=source_ids[i % 50],
                target_id=target_ids[(i + 1) % 50],
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

    benchmark(create)


# ============================================================
# Performance Degradation Analysis
# ============================================================


def test_memory_efficiency_large_batch(benchmark: Any, db_session: Session) -> None:
    """Test memory efficiency with large batch operation."""
    from uuid import uuid4

    from tracertm.models.item import Item

    def create_large_batch() -> None:
        # Create 1000 items in a single session
        items = [
            Item(
                id=f"memory-test-{uuid4().hex[:8]}-{i}",
                project_id="memory-proj",
                title=f"Memory Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            for i in range(1000)
        ]
        db_session.bulk_save_objects(items)
        db_session.commit()

    benchmark(create_large_batch)
