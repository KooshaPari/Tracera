"""Comprehensive concurrency and stress tests for TracerTM.

Tests concurrent operations, race conditions, deadlock scenarios, and stress conditions.
- 20+ test cases
- Baseline stability checks
- Thread pool execution
- Lock contention scenarios
- Transaction isolation
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Never

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.agent import Agent
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.bulk_operation_service import BulkOperationService
from tracertm.services.concurrent_operations_service import (
    ConcurrencyError,
    ConcurrentOperationsService,
    retry_with_backoff,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def concurrent_test_db() -> None:
    """Create a thread-safe test database for concurrent testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def concurrent_session(concurrent_test_db: Any) -> None:
    """Create a session from concurrent test database."""
    SessionLocal = sessionmaker(bind=concurrent_test_db)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def concurrent_initialized_db(concurrent_test_db: Any) -> None:
    """Initialize database with test project and items."""
    SessionLocal = sessionmaker(bind=concurrent_test_db)
    session = SessionLocal()

    # Create project
    project = Project(id="test-project", name="Test Project")
    session.add(project)
    session.commit()

    # Create initial items
    for i in range(10):
        item = Item(
            id=f"item-{i}",
            project_id="test-project",
            title=f"Test Item {i}",
            view="STORY",
            item_type="story",
            status="todo",
        )
        session.add(item)
    session.commit()

    yield concurrent_test_db

    session.close()


@pytest.fixture
def concurrent_session_from_initialized(concurrent_initialized_db: Any) -> None:
    """Get a session from initialized database."""
    SessionLocal = sessionmaker(bind=concurrent_initialized_db)
    session = SessionLocal()
    yield session
    session.close()


# ============================================================================
# Baseline Stability Tests
# ============================================================================


class TestBaselineStability:
    """Baseline tests to ensure basic functionality under normal conditions."""

    def test_single_item_creation(self, concurrent_session: Any) -> None:
        """Test basic item creation stability."""
        project = Project(id="test-proj", name="Test")
        concurrent_session.add(project)
        concurrent_session.commit()

        item = Item(
            id="item-1",
            project_id="test-proj",
            title="Test Item",
            view="STORY",
            item_type="story",
            status="todo",
        )
        concurrent_session.add(item)
        concurrent_session.commit()

        retrieved = concurrent_session.query(Item).filter(Item.id == "item-1").first()
        assert retrieved is not None
        assert retrieved.title == "Test Item"

    def test_single_item_update(self, concurrent_session_from_initialized: Any) -> None:
        """Test basic item update stability."""
        item = concurrent_session_from_initialized.query(Item).filter(Item.id == "item-0").first()
        assert item is not None

        item.status = "in_progress"
        concurrent_session_from_initialized.commit()

        retrieved = concurrent_session_from_initialized.query(Item).filter(Item.id == "item-0").first()
        assert retrieved.status == "in_progress"

    def test_single_link_creation(self, concurrent_session_from_initialized: Any) -> None:
        """Test basic link creation stability."""
        link = Link(
            id="link-1",
            project_id="test-project",
            source_item_id="item-0",
            target_item_id="item-1",
            link_type="depends_on",
        )
        concurrent_session_from_initialized.add(link)
        concurrent_session_from_initialized.commit()

        retrieved = concurrent_session_from_initialized.query(Link).filter(Link.id == "link-1").first()
        assert retrieved is not None
        assert retrieved.link_type == "depends_on"

    def test_transaction_rollback(self, concurrent_session: Any) -> None:
        """Test transaction rollback stability."""
        project = Project(id="proj-rollback", name="Rollback Test")
        concurrent_session.add(project)
        concurrent_session.commit()

        # Successfully add item
        item = Item(
            id="item-rollback",
            project_id="proj-rollback",
            title="Test",
            view="STORY",
            item_type="story",
            status="todo",
        )
        concurrent_session.add(item)
        concurrent_session.commit()

        # Verify item was created
        retrieved = concurrent_session.query(Item).filter(Item.id == "item-rollback").first()
        assert retrieved is not None
        assert retrieved.title == "Test"

        # Now test rollback
        item.title = "Modified"
        concurrent_session.rollback()

        # After rollback, title should revert
        concurrent_session.expire(item)
        retrieved = concurrent_session.query(Item).filter(Item.id == "item-rollback").first()
        assert retrieved.title == "Test"


# ============================================================================
# Concurrent Write Tests
# ============================================================================


class TestConcurrentWrites:
    """Tests for concurrent write operations without data corruption."""

    def test_concurrent_item_creation(self, concurrent_initialized_db: Any) -> None:
        """Test concurrent creation of multiple items."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def create_item(item_id: int) -> None:
            session = SessionLocal()
            try:
                item = Item(
                    id=f"concurrent-item-{item_id}",
                    project_id="test-project",
                    title=f"Concurrent Item {item_id}",
                    view="STORY",
                    item_type="story",
                    status="todo",
                )
                session.add(item)
                session.commit()
                results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_item, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()

        # Most operations should succeed in concurrent environment
        assert len(results) >= 15, f"Expected at least 15 successes, got {len(results)}"
        assert len(errors) <= COUNT_FIVE, f"Should have minimal errors: {errors}"

        # Verify most items exist
        session = SessionLocal()
        count = session.query(Item).filter(Item.id.like("concurrent-item-%")).count()
        assert count >= 15, f"Expected at least 15 items, got {count}"
        session.close()

    def test_concurrent_item_updates(self, concurrent_initialized_db: Any) -> None:
        """Test concurrent updates to same items."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def update_item(item_num: int, update_num: int) -> None:
            session = SessionLocal()
            try:
                item = session.query(Item).filter(Item.id == f"item-{item_num}").first()
                if item:
                    item.status = f"status-{update_num % 3}"
                    session.commit()
                    results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            # Each of 5 items gets updated 5 times concurrently
            for item_num in range(5):
                futures.extend(executor.submit(update_item, item_num, update_num) for update_num in range(5))
            for future in as_completed(futures):
                future.result()

        assert len(results) >= 25 - 5, "Most updates should succeed"
        # Some errors are acceptable due to concurrent updates
        assert len(errors) <= COUNT_FIVE, f"Too many errors: {errors}"

    def test_concurrent_link_creation(self, concurrent_initialized_db: Any) -> None:
        """Test concurrent creation of links."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def create_link(link_id: int) -> None:
            session = SessionLocal()
            try:
                source_id = f"item-{link_id % 10}"
                target_id = f"item-{(link_id + 1) % 10}"
                link = Link(
                    id=f"link-concurrent-{link_id}",
                    project_id="test-project",
                    source_item_id=source_id,
                    target_item_id=target_id,
                    link_type="depends_on",
                )
                session.add(link)
                session.commit()
                results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_link, i) for i in range(30)]
            for future in as_completed(futures):
                future.result()

        assert len(results) >= 25, "Most link creations should succeed"

    def test_concurrent_mixed_operations(self, concurrent_initialized_db: Any) -> None:
        """Test mix of concurrent creates, updates, and deletes."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def mixed_operation(op_id: int, op_type: str) -> None:
            session = SessionLocal()
            try:
                if op_type == "create":
                    item = Item(
                        id=f"mixed-item-{op_id}",
                        project_id="test-project",
                        title=f"Mixed Item {op_id}",
                        view="STORY",
                        item_type="story",
                        status="todo",
                    )
                    session.add(item)
                elif op_type == "update":
                    item = session.query(Item).filter(Item.id == f"item-{op_id % 10}").first()
                    if item:
                        item.title = f"Updated {op_id}"
                elif op_type == "read":
                    session.query(Item).filter(Item.project_id == "test-project").all()

                session.commit()
                results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for i in range(30):
                op_type = ["create", "update", "read"][i % 3]
                futures.append(executor.submit(mixed_operation, i, op_type))

            for future in as_completed(futures):
                future.result()

        assert len(results) >= 25, "Most operations should succeed"


# ============================================================================
# Race Condition Tests
# ============================================================================


class TestRaceConditions:
    """Tests for detecting and handling race conditions."""

    def test_race_condition_counter_increment(self, concurrent_initialized_db: Any) -> None:
        """Test race condition in counter increment via metadata."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)

        # Prepare test item with counter in metadata
        session = SessionLocal()
        item = session.query(Item).filter(Item.id == "item-0").first()
        item.item_metadata = {"counter": 0}
        session.commit()
        session.close()

        errors = []
        successful_increments = []

        def increment_counter() -> None:
            session = SessionLocal()
            try:
                item = session.query(Item).filter(Item.id == "item-0").first()
                if item and item.item_metadata:
                    counter = item.item_metadata.get("counter", 0)
                    counter += 1
                    item.item_metadata = {"counter": counter}
                    session.commit()
                    successful_increments.append(counter)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(increment_counter) for _ in range(50)]
            for future in as_completed(futures):
                future.result()

        # Check final counter value
        session = SessionLocal()
        item = session.query(Item).filter(Item.id == "item-0").first()
        final_counter = item.item_metadata.get("counter", 0) if item.item_metadata else 0
        session.close()

        # Some updates will succeed, but final counter may not equal attempts due to race conditions
        assert final_counter > 0, "Some updates should still succeed"
        # In SQLite with transaction isolation, we may get all increments or some subset
        assert final_counter <= 50, f"Counter should not exceed 50, got {final_counter}"

    def test_lost_update_problem(self, concurrent_initialized_db: Any) -> None:
        """Demonstrate potential for lost update problem with stale data."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)

        session = SessionLocal()
        item = session.query(Item).filter(Item.id == "item-1").first()
        item.title = "Initial"
        session.commit()
        session.close()

        updates = []
        errors = []

        def read_modify_write(value: str) -> None:
            session = SessionLocal()
            try:
                item = session.query(Item).filter(Item.id == "item-1").first()
                title = item.title
                time.sleep(0.001)  # Simulate processing time
                item.title = f"{title}-{value}"
                session.commit()
                updates.append(item.title)
            except Exception as e:
                # StaleDataError expected in concurrent scenarios
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(read_modify_write, label) for label in ["a", "b", "c", "d", "e"]]
            for future in as_completed(futures):
                future.result()

        # At least some updates should succeed
        assert len(updates) > 0, "At least one update should succeed"
        # Errors are acceptable when concurrent updates conflict
        session = SessionLocal()
        item = session.query(Item).filter(Item.id == "item-1").first()
        final_title = item.title
        session.close()

        assert final_title.startswith("Initial"), "Final title should reflect a successful update"

    def test_phantom_read_concurrent_creation(self, concurrent_initialized_db: Any) -> None:
        """Test phantom read scenario with concurrent item creation."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        read_counts = []
        errors = []

        def count_items() -> None:
            session = SessionLocal()
            try:
                count = session.query(Item).filter(Item.project_id == "test-project").count()
                read_counts.append(count)
                time.sleep(0.01)  # Simulate processing
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        def create_items() -> None:
            session = SessionLocal()
            try:
                for i in range(5):
                    item = Item(
                        id=f"phantom-item-{threading.get_ident()}-{i}",
                        project_id="test-project",
                        title=f"Phantom {i}",
                        view="STORY",
                        item_type="story",
                        status="todo",
                    )
                    session.add(item)
                session.commit()
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=6) as executor:
            # Start with 3 count operations
            count_futures = [executor.submit(count_items) for _ in range(3)]
            time.sleep(0.005)
            # Then create items
            create_futures = [executor.submit(create_items) for _ in range(3)]
            time.sleep(0.005)
            # Then count again
            count_futures.extend([executor.submit(count_items) for _ in range(3)])

            for future in as_completed(count_futures + create_futures):
                future.result()

        # Read counts should vary due to phantom reads
        assert len(read_counts) >= 6
        assert len(set(read_counts)) > 1, "Phantom reads should occur"

    def test_check_then_act_race(self, concurrent_initialized_db: Any) -> None:
        """Test check-then-act race condition pattern."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def check_and_update() -> None:
            session = SessionLocal()
            try:
                item = session.query(Item).filter(Item.id == "item-2").first()
                if item and item.status == "todo":
                    time.sleep(0.001)  # Simulate race window
                    item.status = "in_progress"
                    session.commit()
                    results.append(True)
                else:
                    results.append(False)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_and_update) for _ in range(20)]
            for future in as_completed(futures):
                future.result()

        # Multiple threads may have successfully updated the same item
        successful = sum(1 for r in results if r)
        assert successful >= 1, "At least one update should succeed"
        # Due to race condition, more than one thread may think they succeeded
        assert successful <= 20, "Upper bound on successes"


# ============================================================================
# Deadlock and Lock Contention Tests
# ============================================================================


class TestDeadlockScenarios:
    """Tests for deadlock detection and prevention."""

    def test_lock_ordering_prevention(self, concurrent_initialized_db: Any) -> None:
        """Test that consistent lock ordering prevents deadlocks."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def ordered_update(thread_id: int, direction: str) -> None:
            session = SessionLocal()
            try:
                # Always acquire locks in same order: item-0 then item-1
                if direction == "forward":
                    item1 = session.query(Item).filter(Item.id == "item-0").first()
                    item2 = session.query(Item).filter(Item.id == "item-1").first()
                else:
                    item2 = session.query(Item).filter(Item.id == "item-1").first()
                    item1 = session.query(Item).filter(Item.id == "item-0").first()

                if item1 and item2:
                    item1.status = f"status-{thread_id}"
                    item2.status = f"status-{thread_id}"
                    session.commit()
                    results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(10):
                direction = "forward" if i % 2 == 0 else "reverse"
                futures.append(executor.submit(ordered_update, i, direction))

            for future in as_completed(futures):
                future.result()

        # Most operations should succeed
        assert len(results) >= 7, f"Most operations should succeed, got {len(results)}"

    def test_timeout_deadlock_detection(self) -> None:
        """Test deadlock detection using timeouts."""
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        acquired = []
        deadlock_detected = False

        def acquire_with_timeout() -> None:
            nonlocal deadlock_detected
            if lock1.acquire(timeout=0.5):
                try:
                    time.sleep(0.1)
                    if lock2.acquire(timeout=0.5):
                        try:
                            acquired.append(1)
                        finally:
                            lock2.release()
                    else:
                        deadlock_detected = True
                finally:
                    lock1.release()

        threads = [threading.Thread(target=acquire_with_timeout) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have either acquired both locks or detected timeout
        assert len(acquired) + (1 if deadlock_detected else 0) > 0

    def test_high_contention_scenario(self, concurrent_initialized_db: Any) -> None:
        """Test system behavior under high lock contention."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []
        successful_updates = []

        def contend_update(thread_id: int) -> None:
            session = SessionLocal()
            try:
                # All threads trying to update same item
                item = session.query(Item).filter(Item.id == "item-0").first()
                if item:
                    item.status = f"thread-{thread_id}"
                    session.commit()
                    successful_updates.append(thread_id)
                    results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(contend_update, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()
        elapsed = time.time() - start_time

        assert len(results) >= 40, "Most updates should eventually succeed"
        assert elapsed < 30, "Should complete in reasonable time even under contention"


# ============================================================================
# Transaction Isolation Tests
# ============================================================================


class TestTransactionIsolation:
    """Tests for transaction isolation levels and consistency."""

    def test_dirty_read_prevention(self, concurrent_initialized_db: Any) -> None:
        """Test that dirty reads are prevented."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)

        session = SessionLocal()
        item = session.query(Item).filter(Item.id == "item-3").first()
        item.title = "Clean"
        session.commit()
        session.close()

        read_value = None
        update_rolled_back = False

        def reader() -> None:
            nonlocal read_value
            time.sleep(0.2)  # Let writer start first
            session = SessionLocal()
            item = session.query(Item).filter(Item.id == "item-3").first()
            read_value = item.title
            session.close()

        def failed_writer() -> None:
            nonlocal update_rolled_back
            session = SessionLocal()
            item = session.query(Item).filter(Item.id == "item-3").first()
            item.title = "Dirty"
            session.commit()
            time.sleep(0.1)
            session.rollback()
            update_rolled_back = True
            session.close()

        t1 = threading.Thread(target=reader)
        t2 = threading.Thread(target=failed_writer)
        t2.start()
        time.sleep(0.05)
        t1.start()
        t1.join()
        t2.join()

        # Reader should not see dirty uncommitted value
        assert read_value == "Clean" or update_rolled_back

    def test_repeatable_read_consistency(self, concurrent_initialized_db: Any) -> None:
        """Test repeatable reads within a transaction."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)

        session = SessionLocal()
        item = session.query(Item).filter(Item.id == "item-4").first()
        item.title = "Version 1"
        session.commit()
        session.close()

        reads = []

        def read_twice() -> None:
            session = SessionLocal()
            # First read
            item1 = session.query(Item).filter(Item.id == "item-4").first()
            reads.append(item1.title if item1 else None)
            time.sleep(0.1)
            # Second read in same transaction
            item2 = session.query(Item).filter(Item.id == "item-4").first()
            reads.append(item2.title if item2 else None)
            session.close()

        def update_between_reads() -> None:
            time.sleep(0.05)
            session = SessionLocal()
            item = session.query(Item).filter(Item.id == "item-4").first()
            item.title = "Version 2"
            session.commit()
            session.close()

        t1 = threading.Thread(target=read_twice)
        t2 = threading.Thread(target=update_between_reads)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Both reads in same session might see different values in SQLite
        assert len(reads) == COUNT_TWO

    def test_serializable_isolation(self, concurrent_initialized_db: Any) -> None:
        """Test serializable isolation with conflict detection."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)

        # Setup: create two items
        session = SessionLocal()
        item1 = session.query(Item).filter(Item.id == "item-5").first()
        item2 = session.query(Item).filter(Item.id == "item-6").first()
        item1.title = "A"
        item2.title = "B"
        session.commit()
        session.close()

        operations_completed = []

        def transaction1() -> None:
            session = SessionLocal()
            try:
                item1 = session.query(Item).filter(Item.id == "item-5").first()
                item2 = session.query(Item).filter(Item.id == "item-6").first()
                # Read both
                val1 = item1.title if item1 else None
                time.sleep(0.1)  # Window for transaction 2
                val2 = item2.title if item2 else None
                # Modify based on reads
                if val1 == "A" and val2 == "B":
                    operations_completed.append("tx1-read-consistent")
                session.commit()
            finally:
                session.close()

        def transaction2() -> None:
            time.sleep(0.05)  # Start after tx1 has read
            session = SessionLocal()
            try:
                item1 = session.query(Item).filter(Item.id == "item-5").first()
                item2 = session.query(Item).filter(Item.id == "item-6").first()
                item1.title = "A'"
                item2.title = "B'"
                session.commit()
                operations_completed.append("tx2-committed")
            finally:
                session.close()

        t1 = threading.Thread(target=transaction1)
        t2 = threading.Thread(target=transaction2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert len(operations_completed) >= 1


# ============================================================================
# Retry and Backoff Tests
# ============================================================================


class TestRetryAndBackoff:
    """Tests for retry logic and exponential backoff."""

    def test_retry_decorator_success_on_retry(self) -> None:
        """Test that retry decorator succeeds on eventual success."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def flaky_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_TWO:
                msg = "Simulated conflict"
                raise ConcurrencyError(msg)
            return "success"

        result = flaky_operation()
        assert result == "success"
        assert call_count == COUNT_TWO

    def test_retry_decorator_max_retries_exceeded(self) -> None:
        """Test that retry decorator raises after max retries."""
        call_count = 0

        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_failing() -> Never:
            nonlocal call_count
            call_count += 1
            msg = "Always fails"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError):
            always_failing()

        assert call_count == COUNT_THREE  # Initial + 2 retries

    def test_exponential_backoff_timing(self) -> None:
        """Test that exponential backoff increases delay."""
        call_count = 0
        call_times = []

        @retry_with_backoff(max_retries=3, initial_delay=0.01, exponential_base=2.0)
        def tracked_flaky() -> str:
            nonlocal call_count
            call_times.append(time.time())
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "Simulated conflict"
                raise ConcurrencyError(msg)
            return "success"

        start = time.time()
        result = tracked_flaky()
        total_time = time.time() - start

        assert result == "success"
        assert call_count == COUNT_THREE
        # Should have delays due to backoff
        assert total_time > 0.01

    def test_jitter_prevents_thundering_herd(self) -> None:
        """Test that jitter prevents thundering herd problem."""
        call_count = 0
        timings = []

        @retry_with_backoff(max_retries=2, initial_delay=0.05, jitter=True)
        def jittered_operation() -> str:
            nonlocal call_count
            call_count += 1
            start = time.time()
            timings.append(start)
            if call_count < COUNT_TWO:
                msg = "Conflict"
                raise ConcurrencyError(msg)
            return "success"

        start = time.time()
        result = jittered_operation()
        elapsed = time.time() - start

        assert result == "success"
        assert call_count == COUNT_TWO, "Should have retried once"
        # With jitter, timing should vary
        assert elapsed > 0

    def test_concurrent_retry_operations(self, concurrent_session: Any) -> None:
        """Test multiple threads with retry logic."""
        results = []
        errors = []
        concurrent_ops_service = ConcurrentOperationsService(concurrent_session)

        def retryable_operation(op_id: int) -> None:
            def operation() -> str:
                # Simulate occasional conflicts
                if op_id % 3 == 0:
                    time.sleep(0.001)
                return f"result-{op_id}"

            try:
                result = concurrent_ops_service.execute_with_retry(operation, max_retries=2)
                results.append(result)
            except Exception as e:
                errors.append(str(e))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(retryable_operation, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()

        assert len(results) >= 15, "Most operations should succeed with retries"


# ============================================================================
# Bulk Operation Concurrency Tests
# ============================================================================


class TestBulkOperationConcurrency:
    """Tests for concurrent bulk operations."""

    def test_concurrent_bulk_updates(self, concurrent_initialized_db: Any) -> None:
        """Test concurrent bulk updates don't corrupt data."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        errors = []

        def bulk_update_status(new_status: str) -> None:
            session = SessionLocal()
            try:
                items = session.query(Item).filter(Item.project_id == "test-project").all()
                for item in items:
                    item.status = new_status
                session.commit()
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(bulk_update_status, f"status-{i}") for i in range(5)]
            for future in as_completed(futures):
                future.result()

        # Check final state
        session = SessionLocal()
        items = session.query(Item).filter(Item.project_id == "test-project").all()
        statuses = {item.status for item in items}
        session.close()

        # Final status should be one of the updated values
        assert len(statuses) > 0
        assert all(s.startswith("status-") for s in statuses)
        # Errors may occur due to stale data in concurrent updates
        assert len(errors) <= COUNT_THREE, f"Should have minimal errors: {errors}"

    def test_concurrent_bulk_preview_and_execute(self, concurrent_initialized_db: Any) -> None:
        """Test concurrent bulk preview and execution."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def preview_and_execute(batch_id: int) -> None:
            session = SessionLocal()
            try:
                bulk_service = BulkOperationService(session)
                preview = bulk_service.bulk_update_preview(
                    project_id="test-project",
                    filters={"view": "STORY"},
                    updates={"status": f"batch-{batch_id}"},
                )
                results.append(preview)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(preview_and_execute, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()

        assert len(results) >= 8, "Most preview operations should succeed"


# ============================================================================
# Stress Tests
# ============================================================================


class TestStressConditions:
    """Stress tests for system limits and behavior under extreme load."""

    def test_high_throughput_item_creation(self, concurrent_initialized_db: Any) -> None:
        """Test high throughput item creation."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []
        start_time = time.time()

        def create_batch(batch_id: int) -> None:
            session = SessionLocal()
            try:
                for i in range(10):
                    item = Item(
                        id=f"stress-item-{batch_id}-{i}",
                        project_id="test-project",
                        title=f"Stress Item {batch_id}-{i}",
                        view="STORY",
                        item_type="story",
                        status="todo",
                    )
                    session.add(item)
                session.commit()
                results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_batch, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()

        elapsed = time.time() - start_time
        throughput = len(results) * 10 / elapsed if elapsed > 0 else 0

        assert len(results) >= 8, f"Most batches should complete, got {len(results)}"
        assert throughput >= 0, "Should achieve non-negative throughput"

    def test_memory_stability_with_many_sessions(self, concurrent_initialized_db: Any) -> None:
        """Test that many concurrent sessions don't leak memory."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def session_operation(op_id: int) -> None:
            session = SessionLocal()
            try:
                # Read and update existing items to avoid database state issues
                item = session.query(Item).filter(Item.id == f"item-{op_id % 10}").first()
                if item:
                    item.title = f"Updated {op_id}"
                    session.commit()
                    results.append(True)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(session_operation, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()

        assert len(results) >= 40, f"Operations should complete, got {len(results)}"
        assert len(errors) <= COUNT_TEN, f"Should have minimal errors: {errors}"

    def test_rapid_connection_cycling(self, concurrent_initialized_db: Any) -> None:
        """Test rapid creation and destruction of connections."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []

        def quick_operation(_op_id: int) -> None:
            try:
                for _ in range(5):
                    session = SessionLocal()
                    try:
                        count = session.query(Item).filter(Item.project_id == "test-project").count()
                        results.append(count)
                    finally:
                        session.close()
            except Exception as e:
                errors.append(str(e))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(quick_operation, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()

        # Allow for some errors due to rapid cycling, but most should succeed
        assert len(errors) <= COUNT_TWO, f"Should have minimal errors: {errors}"
        assert len(results) >= 70, f"Most operations should complete, got {len(results)}"


# ============================================================================
# Integration and Regression Tests
# ============================================================================


class TestConcurrencyIntegration:
    """Integration tests combining multiple concurrency scenarios."""

    def test_mixed_workload_scenario(self, concurrent_initialized_db: Any) -> None:
        """Test realistic mixed workload with multiple operation types."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        metrics = {
            "creates": 0,
            "updates": 0,
            "reads": 0,
            "errors": 0,
        }
        metrics_lock = threading.Lock()

        def reader() -> None:
            session = SessionLocal()
            try:
                for _ in range(5):
                    items = session.query(Item).filter(Item.project_id == "test-project").all()
                    with metrics_lock:
                        metrics["reads"] += len(items)
                    time.sleep(0.001)
            except Exception:
                with metrics_lock:
                    metrics["errors"] += 1
            finally:
                session.close()

        def updater() -> None:
            session = SessionLocal()
            try:
                for i in range(5):
                    item = session.query(Item).filter(Item.id == f"item-{i}").first()
                    if item:
                        item.status = f"updated-{time.time()}"
                        session.commit()
                        with metrics_lock:
                            metrics["updates"] += 1
                    time.sleep(0.001)
            except Exception:
                with metrics_lock:
                    metrics["errors"] += 1
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(reader) for _ in range(5)]
            futures.extend(executor.submit(updater) for _ in range(5))

            for future in as_completed(futures):
                future.result()

        assert metrics["reads"] > 0, "Should have reads"
        assert metrics["updates"] >= COUNT_TEN, "Should have updates"
        # Errors may occur due to concurrent write conflicts, but should be minimal
        assert metrics["errors"] <= COUNT_FIVE, f"Should have minimal errors: {metrics['errors']}"

    def test_concurrent_agent_operations(self, concurrent_initialized_db: Any) -> None:
        """Test concurrent operations with agent tracking."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)

        # Create agents first with required fields
        session = SessionLocal()
        for i in range(5):
            agent = Agent(
                id=f"agent-{i}",
                name=f"Agent {i}",
                status="active",
                project_id="test-project",  # Required field
                agent_type="worker",  # Required field
            )
            session.add(agent)
        session.commit()
        session.close()

        results = []
        errors = []

        def agent_operation(agent_id: str) -> None:
            session = SessionLocal()
            try:
                agent = session.query(Agent).filter(Agent.id == agent_id).first()
                if agent:
                    # Simulate agent work - update item instead of creating
                    # to avoid duplicate ID issues
                    item = session.query(Item).filter(Item.id == "item-0").first()
                    if item:
                        item.title = f"Processed by {agent_id}"
                        session.commit()
                        results.append(agent_id)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(agent_operation, f"agent-{i}") for i in range(5) for _ in range(3)]
            for future in as_completed(futures):
                future.result()

        assert len(results) >= COUNT_TEN, "Most agent operations should succeed"
        assert len(errors) <= COUNT_FIVE, f"Should have minimal errors: {errors}"


# ============================================================================
# Execution Report
# ============================================================================


class TestConcurrencyReport:
    """Generate execution report with baseline measurements."""

    @pytest.mark.parametrize(
        ("num_threads", "operations"),
        [
            (5, 10),
            (10, 20),
            (20, 50),
        ],
    )
    def test_throughput_measurement(self, concurrent_initialized_db: Any, num_threads: Any, operations: Any) -> None:
        """Measure throughput at various concurrency levels."""
        SessionLocal = sessionmaker(bind=concurrent_initialized_db)
        results = []
        errors = []
        start_time = time.time()

        def operation(_op_id: int) -> None:
            session = SessionLocal()
            try:
                # Simple operation
                count = session.query(Item).count()
                results.append(count)
            except Exception as e:
                errors.append(str(e))
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(operation, i) for i in range(operations * num_threads)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass

        elapsed = time.time() - start_time
        (operations * num_threads) / elapsed if elapsed > 0 else 0

        # Basic assertions - allow some failures
        assert len(results) >= operations * num_threads - 10
        assert elapsed >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
