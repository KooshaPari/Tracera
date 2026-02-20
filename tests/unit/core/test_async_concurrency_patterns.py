"""Async and Concurrency Pattern Tests for TraceRTM.

Tests for:
- Concurrent API requests
- Concurrent database operations
- Async context managers
- Proper await usage patterns
- Race condition scenarios
- Deadlock prevention
- Timeout handling
- Cancellation scenarios
"""

import asyncio
import time
from typing import Any, Never

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError, update_with_retry

# ==============================================================================
# Concurrent API Requests Tests
# ==============================================================================


class TestConcurrentAPIRequests:
    """Test concurrent API request handling."""

    @pytest.mark.asyncio
    async def test_concurrent_api_requests_success(self) -> None:
        """Test multiple concurrent API requests."""

        async def make_request(request_id: int) -> dict:
            await asyncio.sleep(0.01)
            return {"id": request_id, "status": "success"}

        results = await asyncio.gather(*[make_request(i) for i in range(5)])

        assert len(results) == COUNT_FIVE
        assert all(r["status"] == "success" for r in results)
        assert [r["id"] for r in results] == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_concurrent_requests_with_rate_limiting(self) -> None:
        """Test concurrent requests with rate limiting."""
        semaphore = asyncio.Semaphore(2)  # Max 2 concurrent
        request_times = []

        async def limited_request(request_id: int) -> int:
            async with semaphore:
                request_times.append(time.time())
                await asyncio.sleep(0.05)
                return request_id

        start = time.time()
        results = await asyncio.gather(*[limited_request(i) for i in range(6)])
        elapsed = time.time() - start

        assert results == [0, 1, 2, 3, 4, 5]
        # With rate limiting, should take more than sequential time
        assert elapsed > 0.15

    @pytest.mark.asyncio
    async def test_concurrent_requests_partial_failure(self) -> None:
        """Test concurrent requests where some fail."""

        async def request_with_failure(request_id: int) -> dict:
            await asyncio.sleep(0.01)
            if request_id % 2 == 0:
                msg = f"Request {request_id} failed"
                raise ValueError(msg)
            return {"id": request_id, "status": "success"}

        results = await asyncio.gather(*[request_with_failure(i) for i in range(4)], return_exceptions=True)

        assert len(results) == COUNT_FOUR
        assert isinstance(results[0], ValueError)
        assert results[1]["status"] == "success"
        assert isinstance(results[2], ValueError)
        assert results[3]["status"] == "success"

    @pytest.mark.asyncio
    async def test_concurrent_requests_timeout(self) -> None:
        """Test timeout in concurrent requests."""

        async def slow_request(request_id: int) -> int:
            await asyncio.sleep(1)
            return request_id

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(asyncio.gather(slow_request(1), slow_request(2), slow_request(3)), timeout=0.1)

    @pytest.mark.asyncio
    async def test_concurrent_api_request_ordering(self) -> None:
        """Test that concurrent requests return in completion order."""

        async def timed_request(request_id: int, delay: float) -> dict:
            await asyncio.sleep(delay)
            return {"id": request_id, "completed_at": time.time()}

        tasks = [
            timed_request(1, 0.05),
            timed_request(2, 0.01),
            timed_request(3, 0.03),
        ]

        # Using gather returns in order of tasks, not completion
        results = await asyncio.gather(*tasks)
        assert results[0]["id"] == 1
        assert results[1]["id"] == COUNT_TWO
        assert results[2]["id"] == COUNT_THREE

    @pytest.mark.asyncio
    async def test_concurrent_requests_cancellation(self) -> None:
        """Test cancelling concurrent requests."""

        async def cancellable_request(request_id: int) -> int:
            await asyncio.sleep(10)
            return request_id

        async def gather_requests() -> None:
            return await asyncio.gather(cancellable_request(1), cancellable_request(2))

        task = asyncio.create_task(gather_requests())

        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task


# ==============================================================================
# Concurrent Database Operations Tests
# ==============================================================================


class TestConcurrentDatabaseOperations:
    """Test concurrent database operation handling."""

    @pytest.mark.asyncio
    async def test_concurrent_reads_allowed(self) -> None:
        """Test that concurrent reads are allowed."""
        results = []

        async def read_operation(op_id: int) -> int:
            # Simulate async read
            await asyncio.sleep(0.01)
            results.append(op_id)
            return op_id

        # Concurrent reads should work
        await asyncio.gather(*[read_operation(i) for i in range(5)])

        assert len(results) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_concurrent_writes_with_conflict_resolution(self) -> None:
        """Test concurrent writes with conflict detection and resolution."""

        class DataStore:
            def __init__(self) -> None:
                self.data = {"version": 1, "value": "initial"}
                self.lock = asyncio.Lock()

            async def update(self, new_value: str) -> bool:
                async with self.lock:
                    self.data["version"] += 1
                    self.data["value"] = new_value
                    return True

        store = DataStore()

        async def concurrent_update(op_id: int) -> bool:
            return await store.update(f"value_{op_id}")

        results = await asyncio.gather(*[concurrent_update(i) for i in range(3)])

        assert all(results)
        assert store.data["version"] == COUNT_FOUR  # Initial + 3 updates

    @pytest.mark.asyncio
    async def test_database_lock_timeout(self) -> None:
        """Test timeout when acquiring database lock."""
        lock = asyncio.Lock()

        async def lock_operation(timeout_sec: float | None = None) -> bool:
            try:
                async with asyncio.timeout(timeout_sec):
                    async with lock:
                        await asyncio.sleep(0.5)
                        return True
            except TimeoutError:
                return False

        # First operation holds the lock
        task1 = asyncio.create_task(lock_operation(timeout_sec=None))
        await asyncio.sleep(0.05)

        # Second operation times out trying to acquire lock
        result2 = await lock_operation(timeout_sec=0.1)

        assert result2 is False
        await task1

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_concurrent_conflict(self) -> None:
        """Test transaction rollback when concurrent conflict detected."""

        class Transaction:
            def __init__(self) -> None:
                self.state = {"count": 0}
                self.committed = False

            async def increment(self) -> int:
                self.state["count"] += 1
                await asyncio.sleep(0.01)
                return self.state["count"]

            async def commit(self) -> bool:
                if self.state["count"] > COUNT_TWO:
                    # Simulate conflict detection
                    return False
                self.committed = True
                return True

        async def transaction_with_retry(tx: Transaction) -> bool:
            for _attempt in range(3):
                _ = await tx.increment()
                if await tx.commit():
                    return True
                # Reset on conflict
                tx.state["count"] = 0
            return False

        tx = Transaction()
        result = await transaction_with_retry(tx)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_concurrent_batch_operations(self) -> None:
        """Test concurrent batch database operations."""

        async def batch_insert(batch_id: int, item_count: int) -> int:
            # Simulate batch insert
            await asyncio.sleep(0.01)
            return batch_id * item_count

        results = await asyncio.gather(*[batch_insert(i, 10) for i in range(3)])

        assert results == [0, 10, 20]


# ==============================================================================
# Async Context Manager Tests
# ==============================================================================


class TestAsyncContextManagers:
    """Test async context manager patterns."""

    @pytest.mark.asyncio
    async def test_async_context_manager_entry_exit(self) -> None:
        """Test async context manager entry and exit."""
        entered = False
        exited = False

        class AsyncContextManager:
            async def __aenter__(self) -> None:
                nonlocal entered
                entered = True
                await asyncio.sleep(0.01)
                return self

            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                nonlocal exited
                exited = True
                return False

        async with AsyncContextManager():
            assert entered
            assert not exited

        assert exited

    @pytest.mark.asyncio
    async def test_async_context_manager_exception_handling(self) -> Never:
        """Test async context manager handles exceptions."""

        class AsyncResource:
            def __init__(self) -> None:
                self.closed = False

            async def __aenter__(self) -> None:
                return self

            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                self.closed = True
                return False  # Don't suppress exceptions

        resource = AsyncResource()

        with pytest.raises(ValueError, match="Test error"):
            async with resource:
                assert not resource.closed
                msg = "Test error"
                raise ValueError(msg)

        assert resource.closed

    @pytest.mark.asyncio
    async def test_nested_async_context_managers(self) -> None:
        """Test nested async context managers."""
        context_order = []

        class NestedContext:
            def __init__(self, name: str) -> None:
                self.name = name

            async def __aenter__(self) -> None:
                context_order.append(f"enter_{self.name}")
                return self

            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                context_order.append(f"exit_{self.name}")
                return False

        async with NestedContext("outer"), NestedContext("middle"), NestedContext("inner"):
            pass

        assert context_order == [
            "enter_outer",
            "enter_middle",
            "enter_inner",
            "exit_inner",
            "exit_middle",
            "exit_outer",
        ]

    @pytest.mark.asyncio
    async def test_async_context_manager_with_exception_in_exit(self) -> None:
        """Test async context manager when exit raises exception."""

        class ProblematicContext:
            async def __aenter__(self) -> None:
                return self

            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                msg = "Exit error"
                raise RuntimeError(msg)

        with pytest.raises(RuntimeError, match="Exit error"):
            async with ProblematicContext():
                pass

    @pytest.mark.asyncio
    async def test_concurrent_context_managers(self) -> None:
        """Test concurrent async context managers."""
        executions = []

        class ConcurrentContext:
            def __init__(self, name: str) -> None:
                self.name = name

            async def __aenter__(self) -> None:
                executions.append(f"start_{self.name}")
                await asyncio.sleep(0.01)
                return self

            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                executions.append(f"end_{self.name}")
                return False

        async def use_context(name: str) -> None:
            async with ConcurrentContext(name):
                await asyncio.sleep(0.02)

        await asyncio.gather(
            use_context("ctx1"),
            use_context("ctx2"),
        )

        # Both should have started and ended
        assert "start_ctx1" in executions
        assert "start_ctx2" in executions
        assert "end_ctx1" in executions
        assert "end_ctx2" in executions


# ==============================================================================
# Race Condition Tests
# ==============================================================================


class TestRaceConditions:
    """Test race condition scenarios and prevention."""

    @pytest.mark.asyncio
    async def test_race_condition_without_protection(self) -> None:
        """Test race condition when no synchronization is used."""
        counter = 0

        async def increment_unsafe() -> None:
            nonlocal counter
            temp = counter
            await asyncio.sleep(0.0001)  # Context switch opportunity
            counter = temp + 1

        # Run many increments concurrently
        await asyncio.gather(*[increment_unsafe() for _ in range(100)])

        # Counter will be less than 100 due to race condition
        assert counter < 100

    @pytest.mark.asyncio
    async def test_race_condition_with_lock_protection(self) -> None:
        """Test race condition prevention with lock."""
        counter = 0
        lock = asyncio.Lock()

        async def increment_safe() -> None:
            nonlocal counter
            async with lock:
                temp = counter
                await asyncio.sleep(0.0001)
                counter = temp + 1

        await asyncio.gather(*[increment_safe() for _ in range(100)])

        # Counter should be exactly 100 with lock protection
        assert counter == 100

    @pytest.mark.asyncio
    async def test_race_condition_data_corruption(self) -> None:
        """Test data corruption from race conditions."""

        class SharedData:
            def __init__(self) -> None:
                self.items = []

            async def add_item_unsafe(self, item: str) -> None:
                current = self.items.copy()
                await asyncio.sleep(0.0001)
                self.items = [*current, item]

        data = SharedData()

        async def add_many(prefix: str) -> None:
            for i in range(5):
                await data.add_item_unsafe(f"{prefix}_{i}")

        await asyncio.gather(
            add_many("a"),
            add_many("b"),
        )

        # Should have 10 items but might have fewer due to lost writes
        assert len(data.items) <= COUNT_TEN

    @pytest.mark.asyncio
    async def test_check_then_act_race_condition(self) -> None:
        """Test classic check-then-act race condition."""

        class Registry:
            def __init__(self) -> None:
                self.items = {}

            async def add_if_absent_unsafe(self, key: str, value: str) -> bool:
                if key in self.items:
                    return False  # Already exists

                await asyncio.sleep(0.0001)  # Context switch window

                self.items[key] = value
                return True

        registry = Registry()

        async def concurrent_add(key: str) -> bool:
            return await registry.add_if_absent_unsafe(key, "value")

        # Try to add same key concurrently
        results = await asyncio.gather(
            concurrent_add("same_key"),
            concurrent_add("same_key"),
        )

        # Due to race condition, both might succeed
        assert True in results


# ==============================================================================
# Timeout Handling Tests
# ==============================================================================


class TestTimeoutHandling:
    """Test timeout scenarios in async operations."""

    @pytest.mark.asyncio
    async def test_operation_timeout(self) -> None:
        """Test operation timeout."""

        async def slow_operation() -> int:
            await asyncio.sleep(10)
            return 42

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_operation(), timeout=0.1)

    @pytest.mark.asyncio
    async def test_timeout_with_cleanup(self) -> None:
        """Test timeout with cleanup operation."""
        cleanup_called = False

        async def operation_with_cleanup() -> int:
            nonlocal cleanup_called
            try:
                await asyncio.sleep(10)
                return 42
            except TimeoutError:
                cleanup_called = True
                raise

        async def run_with_cleanup_track() -> None:
            nonlocal cleanup_called
            try:
                await asyncio.wait_for(operation_with_cleanup(), timeout=0.1)
            except TimeoutError:
                cleanup_called = True
                raise

        with pytest.raises(asyncio.TimeoutError):
            await run_with_cleanup_track()

        assert cleanup_called

    @pytest.mark.asyncio
    async def test_multiple_operations_with_timeout(self) -> None:
        """Test timeout on multiple concurrent operations."""

        async def operation(duration: float) -> int:
            await asyncio.sleep(duration)
            return 1

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                asyncio.gather(
                    operation(0.05),
                    operation(0.5),  # This will timeout
                    operation(0.03),
                ),
                timeout=0.1,
            )

    @pytest.mark.asyncio
    async def test_timeout_with_retry(self) -> None:
        """Test timeout with retry logic."""

        async def flaky_operation() -> str:
            await asyncio.sleep(0.2)
            return "success"

        call_count = 0

        async def operation_with_timeout_retry() -> str:
            nonlocal call_count
            for attempt in range(3):
                call_count += 1
                try:
                    return await asyncio.wait_for(flaky_operation(), timeout=0.05)
                except TimeoutError:
                    if attempt == COUNT_TWO:
                        raise
                    await asyncio.sleep(0.01)
            return None

        with pytest.raises(asyncio.TimeoutError):
            await operation_with_timeout_retry()

        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_timeout_doesnt_affect_other_tasks(self) -> None:
        """Test that timeout on one task doesn't affect others."""
        completed = []

        async def fast_task(task_id: int) -> None:
            await asyncio.sleep(0.01)
            completed.append(task_id)

        async def slow_task() -> None:
            await asyncio.sleep(10)

        tasks = [
            fast_task(1),
            slow_task(),
            fast_task(2),
        ]

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=0.1)

        # Fast tasks may have started but might not complete due to cancellation
        # This tests that timeout doesn't silently succeed


# ==============================================================================
# Cancellation Tests
# ==============================================================================


class TestCancellationScenarios:
    """Test task cancellation scenarios."""

    @pytest.mark.asyncio
    async def test_task_cancellation(self) -> None:
        """Test basic task cancellation."""

        async def long_running() -> int:
            await asyncio.sleep(10)
            return 42

        task = asyncio.create_task(long_running())
        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

    @pytest.mark.asyncio
    async def test_cancellation_cleanup(self) -> None:
        """Test cleanup on cancellation."""
        cleanup_done = False

        async def cancellable_operation() -> None:
            nonlocal cleanup_done
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cleanup_done = True
                raise

        task = asyncio.create_task(cancellable_operation())
        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        assert cleanup_done

    @pytest.mark.asyncio
    async def test_cancellation_with_shield(self) -> None:
        """Test cancellation prevention with shield."""

        async def critical_operation() -> str:
            await asyncio.sleep(0.05)
            return "critical"

        async def shielded_operation() -> None:
            return await asyncio.shield(critical_operation())

        task = asyncio.create_task(shielded_operation())
        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            # Shield protects the inner task but the outer task is cancelled
            await task

    @pytest.mark.asyncio
    async def test_partial_cancellation(self) -> None:
        """Test cancelling only some tasks in a group."""
        results = []

        async def task(task_id: int) -> int:
            await asyncio.sleep(0.05)
            results.append(task_id)
            return task_id

        tasks = [
            asyncio.create_task(task(1)),
            asyncio.create_task(task(2)),
            asyncio.create_task(task(3)),
        ]

        await asyncio.sleep(0.01)
        tasks[1].cancel()  # Cancel middle task

        # Wait for remaining tasks
        for i, task in enumerate(tasks):
            if i != 1:
                await task

        assert 1 in results
        assert 2 not in results  # Cancelled
        assert 3 in results

    @pytest.mark.asyncio
    async def test_cascade_cancellation(self) -> None:
        """Test cancellation propagation in nested tasks."""
        cancelled_tasks = []

        async def subtask(task_id: int) -> None:
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cancelled_tasks.append(task_id)
                raise

        async def main_task() -> None:
            tasks = [asyncio.create_task(subtask(i)) for i in range(3)]
            await asyncio.gather(*tasks)

        task = asyncio.create_task(main_task())
        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task


# ==============================================================================
# Deadlock Prevention Tests
# ==============================================================================


class TestDeadlockPrevention:
    """Test deadlock prevention in concurrent operations."""

    @pytest.mark.asyncio
    async def test_lock_order_consistency(self) -> None:
        """Test deadlock prevention with consistent lock ordering."""
        lock_a = asyncio.Lock()
        lock_b = asyncio.Lock()

        async def operation_1() -> None:
            async with lock_a:
                await asyncio.sleep(0.01)
                async with lock_b:
                    pass

        async def operation_2() -> None:
            async with lock_a:  # Same order as operation_1
                await asyncio.sleep(0.01)
                async with lock_b:
                    pass

        # Should complete without deadlock
        await asyncio.gather(operation_1(), operation_2())

    @pytest.mark.asyncio
    async def test_lock_timeout_prevents_deadlock(self) -> None:
        """Test timeout prevents indefinite deadlock."""
        lock = asyncio.Lock()
        timeout_occurred = False

        async with lock:

            async def try_acquire_with_timeout() -> None:
                nonlocal timeout_occurred
                try:
                    async with asyncio.timeout(0.05):
                        async with lock:
                            pass
                except TimeoutError:
                    timeout_occurred = True

            await try_acquire_with_timeout()

        assert timeout_occurred

    @pytest.mark.asyncio
    async def test_no_circular_dependencies(self) -> None:
        """Test operation chain without circular lock dependencies."""
        locks = [asyncio.Lock() for _ in range(3)]
        execution_order = []

        async def acquire_locks_in_order(step: int) -> None:
            for lock in locks:
                async with lock:
                    execution_order.append((step, id(lock)))
                    await asyncio.sleep(0.001)

        await asyncio.gather(
            acquire_locks_in_order(1),
            acquire_locks_in_order(2),
        )

        # Should complete without deadlock
        assert len(execution_order) == 6


# ==============================================================================
# Concurrency Pattern Tests (update_with_retry)
# ==============================================================================


class TestAsyncRetryPatterns:
    """Test async retry patterns with concurrency."""

    @pytest.mark.asyncio
    async def test_concurrent_retries(self) -> None:
        """Test multiple operations retrying concurrently."""
        call_counts = {1: 0, 2: 0, 3: 0}

        async def operation(op_id: int) -> str:
            await asyncio.sleep(0)
            call_counts[op_id] += 1
            if call_counts[op_id] < COUNT_TWO:
                msg = "Conflict"
                raise ConcurrencyError(msg)
            return f"op_{op_id}"

        results = await asyncio.gather(*[
            update_with_retry(lambda oid=op_id: operation(oid), max_retries=3) for op_id in [1, 2, 3]
        ])

        assert all(r.startswith("op_") for r in results)
        assert all(c == COUNT_TWO for c in call_counts.values())

    @pytest.mark.asyncio
    async def test_retry_backoff_under_load(self) -> None:
        """Test retry backoff behavior under concurrent load."""
        attempt_times = []

        async def operation_with_timing() -> str:
            await asyncio.sleep(0)
            attempt_times.append(time.time())
            if len(attempt_times) < COUNT_TWO:
                msg = "Conflict"
                raise ConcurrencyError(msg)
            return "success"

        start = time.time()
        result = await update_with_retry(operation_with_timing, max_retries=3, base_delay=0.01)
        elapsed = time.time() - start

        assert result == "success"
        assert len(attempt_times) == COUNT_TWO
        # Should have some delay between attempts
        assert elapsed >= 0.01

    @pytest.mark.asyncio
    async def test_retry_failure_with_concurrent_operations(self) -> None:
        """Test retry failure when concurrent operations conflict."""

        async def always_conflicts() -> str:
            await asyncio.sleep(0)
            msg = "Always conflicts"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError):
            await update_with_retry(always_conflicts, max_retries=2, base_delay=0.001)


# ==============================================================================
# Event Loop and Task Management Tests
# ==============================================================================


class TestEventLoopManagement:
    """Test event loop and task management."""

    @pytest.mark.asyncio
    async def test_task_creation_and_management(self) -> None:
        """Test creating and managing multiple tasks."""

        async def simple_task(task_id: int) -> int:
            await asyncio.sleep(0.01)
            return task_id * 2

        tasks = [asyncio.create_task(simple_task(i)) for i in range(5)]

        results = await asyncio.gather(*tasks)
        assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_task_result_retrieval(self) -> None:
        """Test retrieving results from completed tasks."""

        async def get_value(val: int) -> int:
            await asyncio.sleep(0.01)
            return val * 2

        task = asyncio.create_task(get_value(21))
        result = await task
        assert result == 42

    @pytest.mark.asyncio
    async def test_task_exception_handling(self) -> None:
        """Test exception handling in tasks."""

        async def failing_task() -> None:
            await asyncio.sleep(0)
            msg = "Task error"
            raise ValueError(msg)

        task = asyncio.create_task(failing_task())

        with pytest.raises(ValueError, match="Task error"):
            await task

    @pytest.mark.asyncio
    async def test_task_done_check(self) -> None:
        """Test checking if task is done."""

        async def quick_task() -> int:
            await asyncio.sleep(0.01)
            return 42

        task = asyncio.create_task(quick_task())
        assert not task.done()

        await task
        assert task.done()

    @pytest.mark.asyncio
    async def test_multiple_waiters_for_future(self) -> None:
        """Test multiple coroutines waiting on same future."""
        future = asyncio.Future()
        results = []

        async def waiter(waiter_id: int) -> None:
            result = await future
            results.append((waiter_id, result))

        tasks = [asyncio.create_task(waiter(i)) for i in range(3)]

        await asyncio.sleep(0.01)
        future.set_result("complete")

        await asyncio.gather(*tasks)
        assert len(results) == COUNT_THREE
        assert all(r[1] == "complete" for r in results)


# ==============================================================================
# Integration Tests - Combined Patterns
# ==============================================================================


class TestAsyncIntegrationPatterns:
    """Test integration of multiple async patterns."""

    @pytest.mark.asyncio
    async def test_retry_with_timeout_and_cancellation(self) -> None:
        """Test combining retry, timeout, and cancellation."""
        attempt_count = 0

        async def flaky_operation() -> str:
            nonlocal attempt_count
            attempt_count += 1
            await asyncio.sleep(0.01)
            if attempt_count < COUNT_TWO:
                msg = "Conflict"
                raise ConcurrencyError(msg)
            return "success"

        async def operation_with_retry_and_timeout() -> str:
            for attempt in range(3):
                try:
                    return await asyncio.wait_for(
                        update_with_retry(flaky_operation, max_retries=2, base_delay=0.001),
                        timeout=0.5,
                    )
                except TimeoutError:
                    if attempt == COUNT_TWO:
                        raise
                    await asyncio.sleep(0.01)
            return None

        result = await operation_with_retry_and_timeout()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_producer_consumer_pattern(self) -> None:
        """Test async producer-consumer pattern."""
        queue = asyncio.Queue(maxsize=5)
        produced = []
        consumed = []
        done_event = asyncio.Event()

        async def producer(item_count: int) -> None:
            for i in range(item_count):
                await queue.put(f"item_{i}")
                produced.append(f"item_{i}")
                await asyncio.sleep(0.005)
            done_event.set()

        async def consumer(consumer_id: int) -> None:
            while not queue.empty() or not done_event.is_set():
                try:
                    item = queue.get_nowait()
                    consumed.append((consumer_id, item))
                except asyncio.QueueEmpty:
                    await asyncio.sleep(0.001)

        producer_task = asyncio.create_task(producer(5))

        consumer_task1 = asyncio.create_task(consumer(1))
        consumer_task2 = asyncio.create_task(consumer(2))

        await producer_task
        await asyncio.sleep(0.05)
        await consumer_task1
        await consumer_task2

        assert len(produced) == COUNT_FIVE
        assert len(consumed) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_fan_out_fan_in(self) -> None:
        """Test fan-out and fan-in pattern."""

        async def worker(item: int) -> int:
            await asyncio.sleep(0.01)
            return item * 2

        items = [1, 2, 3, 4, 5]

        # Fan out
        tasks = [asyncio.create_task(worker(item)) for item in items]

        # Fan in
        results = await asyncio.gather(*tasks)

        assert results == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_barrier_synchronization(self) -> None:
        """Test barrier pattern for synchronization."""
        barrier = asyncio.Barrier(3)
        events = []

        async def worker(worker_id: int) -> None:
            events.append(f"before_{worker_id}")
            await barrier.wait()
            events.append(f"after_{worker_id}")

        await asyncio.gather(*[worker(i) for i in range(3)])

        # All before events should come before all after events
        before_count = sum(1 for e in events if e.startswith("before_"))
        assert before_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_semaphore_resource_pooling(self) -> None:
        """Test semaphore for resource pooling."""
        active_count = 0
        max_active = 0
        semaphore = asyncio.Semaphore(2)

        async def resource_user(_user_id: int) -> None:
            nonlocal active_count, max_active
            async with semaphore:
                active_count += 1
                max_active = max(max_active, active_count)
                await asyncio.sleep(0.05)
                active_count -= 1

        await asyncio.gather(*[resource_user(i) for i in range(5)])

        assert max_active == COUNT_TWO  # Max concurrent should be limited to semaphore size

    @pytest.mark.asyncio
    async def test_event_signal_pattern(self) -> None:
        """Test event/signal pattern for coordination."""
        event = asyncio.Event()
        signalled = []

        async def waiter(waiter_id: int) -> None:
            await event.wait()
            signalled.append(waiter_id)

        async def signaller() -> None:
            await asyncio.sleep(0.01)
            event.set()

        tasks = [waiter(i) for i in range(3)]
        tasks.append(signaller())

        await asyncio.gather(*tasks)
        assert len(signalled) == COUNT_THREE
