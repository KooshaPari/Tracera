"""Concurrent operations performance benchmarks.

Tests measure performance under concurrent load:
- Concurrent item creation (10, 50, 100 threads)
- Concurrent item updates
- Concurrent item queries
- Concurrent link operations
- Lock contention analysis
"""

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pytest
from sqlalchemy.orm import sessionmaker

from tests.test_constants import HTTP_INTERNAL_SERVER_ERROR

pytestmark = pytest.mark.performance


# ============================================================
# Concurrent Item Creation
# ============================================================


def test_concurrent_create_10_items_10_threads(benchmark: Any, perf_sync_db_engine: Any) -> None:
    """Benchmark concurrent creation: 10 items across 10 threads."""
    SessionLocal = sessionmaker(bind=perf_sync_db_engine)

    def worker(thread_id: int, item_id: int) -> bool:
        """Worker thread to create item."""
        from tracertm.models.item import Item

        session = SessionLocal()
        try:
            item = Item(
                id=f"concurrent-10-{uuid.uuid4().hex[:8]}-t{thread_id}-{item_id}",
                project_id="concurrent-proj",
                title=f"Concurrent Item {thread_id}-{item_id}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            session.add(item)
            session.commit()
            return True
        finally:
            session.close()

    def run_concurrent() -> None:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i // 10, i % 10) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]
            return all(results)

    result = benchmark(run_concurrent)
    assert result is True


def test_concurrent_create_100_items_10_threads(benchmark: Any, perf_sync_db_engine: Any) -> None:
    """Benchmark concurrent creation: 100 items across 10 threads."""
    SessionLocal = sessionmaker(bind=perf_sync_db_engine)

    def worker(thread_id: int, start_id: int) -> int:
        """Worker thread to create 10 items."""
        from tracertm.models.item import Item

        session = SessionLocal()
        try:
            for i in range(10):
                item = Item(
                    id=f"concurrent-100-{uuid.uuid4().hex[:8]}-t{thread_id}-{start_id + i}",
                    project_id="concurrent-100-proj",
                    title=f"Concurrent Item {thread_id}-{start_id + i}",
                    view="FEATURE",
                    item_type="feature",
                    status="todo",
                    version=1,
                )
                session.add(item)
            session.commit()
            return 10
        finally:
            session.close()

    def run_concurrent() -> None:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i, i * 10) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]
            return sum(results)

    result = benchmark(run_concurrent)
    assert result == 100


def test_concurrent_create_500_items_50_threads(benchmark: Any, perf_sync_db_engine: Any) -> None:
    """Benchmark concurrent creation: 500 items across 50 threads."""
    SessionLocal = sessionmaker(bind=perf_sync_db_engine)

    def worker(thread_id: int, start_id: int) -> int:
        """Worker thread to create items."""
        from tracertm.models.item import Item

        session = SessionLocal()
        try:
            for i in range(10):
                item = Item(
                    id=f"concurrent-500-{uuid.uuid4().hex[:8]}-t{thread_id}-{start_id + i}",
                    project_id="concurrent-500-proj",
                    title=f"Concurrent Item {thread_id}-{start_id + i}",
                    view="FEATURE",
                    item_type="feature",
                    status="todo",
                    version=1,
                )
                session.add(item)
            session.commit()
            return 10
        finally:
            session.close()

    def run_concurrent() -> None:
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(worker, i, i * 10) for i in range(50)]
            results = [f.result() for f in as_completed(futures)]
            return sum(results)

    result = benchmark(run_concurrent)
    assert result == HTTP_INTERNAL_SERVER_ERROR


# ============================================================
# Concurrent Item Updates
# ============================================================


def test_concurrent_update_100_items_10_threads(benchmark: Any, perf_sync_db_engine: Any) -> None:
    """Benchmark concurrent updates: 100 items across 10 threads."""
    SessionLocal = sessionmaker(bind=perf_sync_db_engine)

    # Create items first with stable IDs
    item_ids = []
    session = SessionLocal()
    try:
        from tracertm.models.item import Item

        for i in range(100):
            item_id = f"update-concurrent-100-{i}"
            item = Item(
                id=item_id,
                project_id="update-concurrent-proj",
                title=f"Update Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            item_ids.append(item_id)
            session.add(item)
        session.commit()
    finally:
        session.close()

    def worker(thread_id: int, start_id: int) -> int:
        """Worker thread to update items."""
        from tracertm.models.item import Item

        session = SessionLocal()
        try:
            for i in range(10):
                if start_id + i < len(item_ids):
                    item = session.query(Item).filter(Item.id == item_ids[start_id + i]).first()
                    if item:
                        item.status = ["todo", "in_progress", "done"][thread_id % 3]
                        session.commit()
            return 10
        finally:
            session.close()

    def run_concurrent() -> None:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i, i * 10) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]
            return sum(results)

    result = benchmark(run_concurrent)
    assert result == 100


# ============================================================
# Concurrent Item Queries
# ============================================================


def test_concurrent_query_100_items_10_threads(benchmark: Any, perf_sync_db_engine: Any) -> None:
    """Benchmark concurrent queries: 100 items across 10 threads."""
    SessionLocal = sessionmaker(bind=perf_sync_db_engine)

    # Create items first
    session = SessionLocal()
    try:
        from tracertm.models.item import Item

        for i in range(100):
            item = Item(
                id=f"query-concurrent-100-{uuid.uuid4().hex[:8]}-{i}",
                project_id="query-concurrent-proj",
                title=f"Query Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            session.add(item)
        session.commit()
    finally:
        session.close()

    def worker(_thread_id: int) -> int:
        """Worker thread to query items."""
        from tracertm.models.item import Item

        session = SessionLocal()
        try:
            items = session.query(Item).filter(Item.project_id == "query-concurrent-proj").all()
            return len(items)
        finally:
            session.close()

    def run_concurrent() -> None:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]
            return sum(results)

    result = benchmark(run_concurrent)
    assert result == 1000  # 10 threads × 100 items each


# ============================================================
# Concurrent Link Operations
# ============================================================


def test_concurrent_create_links_50_threads(benchmark: Any, perf_sync_db_engine: Any) -> None:
    """Benchmark concurrent link creation: 500 links across 50 threads."""
    SessionLocal = sessionmaker(bind=perf_sync_db_engine)

    # Create items first with stable IDs
    source_ids = []
    target_ids = []
    session = SessionLocal()
    try:
        from tracertm.models.item import Item

        for i in range(100):
            source_id = f"link-source-{i}"
            item = Item(
                id=source_id,
                project_id="link-concurrent-proj",
                title=f"Link Source {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            source_ids.append(source_id)
            session.add(item)

            target_id = f"link-target-{i}"
            item = Item(
                id=target_id,
                project_id="link-concurrent-proj",
                title=f"Link Target {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            target_ids.append(target_id)
            session.add(item)
        session.commit()
    finally:
        session.close()

    def worker(thread_id: int, start_id: int) -> int:
        """Worker thread to create links."""
        from tracertm.models.link import Link

        session = SessionLocal()
        try:
            for i in range(10):
                link = Link(
                    id=f"link-concurrent-{uuid.uuid4().hex[:8]}-t{thread_id}-{start_id + i}",
                    project_id="link-concurrent-proj",
                    source_id=source_ids[(start_id + i) % 100],
                    target_id=target_ids[(start_id + i + 1) % 100],
                    link_type="depends_on",
                )
                session.add(link)
            session.commit()
            return 10
        finally:
            session.close()

    def run_concurrent() -> None:
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(worker, i, i * 10) for i in range(50)]
            results = [f.result() for f in as_completed(futures)]
            return sum(results)

    result = benchmark(run_concurrent)
    assert result == HTTP_INTERNAL_SERVER_ERROR


# ============================================================
# Lock Contention Analysis
# ============================================================


def test_high_contention_single_item_updates(benchmark: Any, perf_sync_db_engine: Any) -> None:
    """Test high contention: 50 threads updating same item."""
    SessionLocal = sessionmaker(bind=perf_sync_db_engine)

    # Create single item
    session = SessionLocal()
    try:
        from tracertm.models.item import Item

        item = Item(
            id="contention-item",
            project_id="contention-proj",
            title="Contention Test Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )
        session.add(item)
        session.commit()
    finally:
        session.close()

    def worker(thread_id: int) -> bool:
        """Worker thread updating same item."""
        from tracertm.models.item import Item

        session = SessionLocal()
        try:
            item = session.query(Item).filter(Item.id == "contention-item").first()
            if item:
                item.priority = ["low", "medium", "high"][thread_id % 3]
                session.commit()
            return True
        finally:
            session.close()

    def run_concurrent() -> None:
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(worker, i) for i in range(50)]
            results = [f.result() for f in as_completed(futures)]
            return all(results)

    result = benchmark(run_concurrent)
    assert result is True
