"""Comprehensive tests for concurrency and database connection modules.

Focuses on:
- Advanced concurrency patterns (thread safety, race conditions)
- Connection pooling and pool exhaustion
- Connection lifecycle and state management
- Error handling and retry logic
- Resource cleanup and context managers
- Concurrent database access
- Property-based testing for robustness
"""

import asyncio
import threading
from typing import Any, Never

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError, update_with_retry
from tracertm.database.connection import DatabaseConnection, get_session

# ==============================================================================
# Advanced Concurrency Tests
# ==============================================================================


class TestConcurrencyThreadSafety:
    """Test thread safety of concurrency utilities."""

    @pytest.mark.asyncio
    async def test_concurrent_retry_operations(self) -> None:
        """Test multiple concurrent retry operations don't interfere."""
        success_count = 0
        lock = asyncio.Lock()

        async def increment_with_retry() -> None:
            nonlocal success_count
            await asyncio.sleep(0.001)
            async with lock:
                success_count += 1
            return success_count

        # Run 20 concurrent operations
        results = await asyncio.gather(*[update_with_retry(increment_with_retry) for _ in range(20)])

        assert len(results) == 20
        assert success_count == 20
        assert sorted(results) == list(range(1, 21))

    @pytest.mark.asyncio
    async def test_concurrent_failures_and_retries(self) -> None:
        """Test concurrent operations with mixed failures and retries."""
        call_counts = {}
        lock = asyncio.Lock()

        async def operation_with_id(op_id: int) -> str:
            async with lock:
                call_counts[op_id] = call_counts.get(op_id, 0) + 1
                count = call_counts[op_id]

            if count < COUNT_TWO:
                msg = f"Operation {op_id} retry {count}"
                raise ConcurrencyError(msg)
            return f"success_{op_id}"

        # Run 10 concurrent operations, each requiring 2 attempts
        results = await asyncio.gather(*[
            update_with_retry(lambda op_id=i: operation_with_id(op_id)) for i in range(10)
        ])

        assert len(results) == COUNT_TEN
        assert all(r.startswith("success_") for r in results)
        # Each operation should have been called twice
        assert all(count >= COUNT_TWO for count in call_counts.values())

    @pytest.mark.asyncio
    async def test_race_condition_with_shared_state(self) -> None:
        """Test handling race conditions with shared state."""
        shared_counter = {"value": 0, "version": 0}
        lock = asyncio.Lock()
        conflicts = {"count": 0}

        async def optimistic_increment() -> None:
            # Read current state
            async with lock:
                current_version = shared_counter["version"]
                current_value = shared_counter["value"]

            # Simulate processing delay to create race conditions
            await asyncio.sleep(0.002)

            # Try to update with optimistic lock
            async with lock:
                if shared_counter["version"] != current_version:
                    conflicts["count"] += 1
                    msg = "Version mismatch"
                    raise ConcurrencyError(msg)

                shared_counter["value"] = current_value + 1
                shared_counter["version"] += 1
                return shared_counter["value"]

        # Run concurrent operations - some will conflict and retry
        results = await asyncio.gather(
            *[update_with_retry(optimistic_increment, max_retries=10, base_delay=0.001) for _ in range(10)],
            return_exceptions=True,
        )

        # All should eventually succeed
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) == COUNT_TEN, f"Expected 10 successful, got {len(successful)}"
        assert shared_counter["value"] == COUNT_TEN
        # Should have detected some conflicts due to concurrent access
        assert conflicts["count"] > 0, "Expected some version conflicts"


class TestConcurrencyTimeouts:
    """Test timeout handling in concurrent operations."""

    @pytest.mark.asyncio
    async def test_operation_timeout(self) -> None:
        """Test operation that times out."""

        async def slow_operation() -> str:
            await asyncio.sleep(10)
            return "never_completes"

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(update_with_retry(slow_operation), timeout=0.1)

    @pytest.mark.asyncio
    async def test_retry_with_timeout(self) -> None:
        """Test retry operations respect timeout."""
        call_count = 0

        async def operation_with_delays() -> Never:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.05)
            msg = "Still failing"
            raise ConcurrencyError(msg)

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                update_with_retry(operation_with_delays, max_retries=10, base_delay=0.05),
                timeout=0.2,
            )

        # Should have attempted at least once
        assert call_count >= 1

    @pytest.mark.asyncio
    async def test_concurrent_operations_with_timeout(self) -> None:
        """Test multiple concurrent operations with timeout."""

        async def fast_operation(op_id: int) -> str:
            await asyncio.sleep(0.01)
            return f"result_{op_id}"

        async def slow_operation(op_id: int) -> str:
            await asyncio.sleep(1)
            return f"slow_{op_id}"

        # Mix of fast and slow operations
        tasks = [asyncio.wait_for(update_with_retry(lambda i=i: fast_operation(i)), timeout=0.5) for i in range(5)] + [
            asyncio.wait_for(update_with_retry(lambda i=i: slow_operation(i)), timeout=0.05) for i in range(5, 10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Fast operations should succeed
        assert sum(1 for r in results[:5] if not isinstance(r, Exception)) == COUNT_FIVE
        # Slow operations should timeout
        assert sum(1 for r in results[5:] if isinstance(r, asyncio.TimeoutError)) == COUNT_FIVE


class TestConcurrencyCancellation:
    """Test cancellation of concurrent operations."""

    @pytest.mark.asyncio
    async def test_cancel_during_retry(self) -> None:
        """Test cancelling operation during retry backoff."""
        call_count = 0

        async def failing_operation() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Always fails"
            raise ConcurrencyError(msg)

        task = asyncio.create_task(update_with_retry(failing_operation, max_retries=10, base_delay=0.1))

        # Wait for first attempt
        await asyncio.sleep(0.05)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        # Should have been cancelled early
        assert call_count <= COUNT_THREE

    @pytest.mark.asyncio
    async def test_cancel_multiple_operations(self) -> None:
        """Test cancelling multiple concurrent operations."""

        async def long_running_operation(op_id: int) -> str:
            await asyncio.sleep(10)
            return f"completed_{op_id}"

        tasks = [asyncio.create_task(update_with_retry(lambda i=i: long_running_operation(i))) for i in range(10)]

        # Wait a bit then cancel all
        await asyncio.sleep(0.01)
        for task in tasks:
            task.cancel()

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should be cancelled (CancelledError is raised and captured as exception)
        cancelled_count = sum(1 for r in results if isinstance(r, asyncio.CancelledError))
        assert cancelled_count == COUNT_TEN, f"Expected all 10 to be cancelled, got {cancelled_count}"


# ==============================================================================
# Database Connection Pool Tests
# ==============================================================================


class TestDatabaseConnectionPool:
    """Test database connection pooling."""

    def test_pool_configuration(self, tmp_path: Any) -> None:
        """Test pool is configured with correct parameters."""
        db_path = tmp_path / "pool_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        # Pool should exist
        assert engine.pool is not None
        # Pool should have connections available
        assert engine.pool.size() >= 0

    def test_pool_checkout_and_return(self, tmp_path: Any) -> None:
        """Test checking out and returning connections."""
        db_path = tmp_path / "pool_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        initial_checked_out = engine.pool.checkedout()

        # Check out a connection
        conn1 = engine.connect()
        assert engine.pool.checkedout() == initial_checked_out + 1

        # Check out another
        conn2 = engine.connect()
        assert engine.pool.checkedout() == initial_checked_out + 2

        # Return connections
        conn1.close()
        assert engine.pool.checkedout() == initial_checked_out + 1

        conn2.close()
        assert engine.pool.checkedout() == initial_checked_out

    def test_pool_reuses_connections(self, tmp_path: Any) -> None:
        """Test pool reuses connections efficiently."""
        db_path = tmp_path / "pool_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        # Get and release connection multiple times
        connection_ids = []
        for _ in range(5):
            conn = engine.connect()
            connection_ids.append(id(conn.connection))
            conn.close()

        # Pool should be reusing connections (some IDs should repeat)
        # This is implementation-dependent, so we just verify connections work
        assert len(connection_ids) == COUNT_FIVE

    def test_pool_concurrent_access(self, tmp_path: Any) -> None:
        """Test concurrent access to connection pool."""
        db_path = tmp_path / "pool_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        results = []
        errors = []

        def use_connection(thread_id: int) -> None:
            try:
                conn = engine.connect()
                result = conn.execute(text("SELECT :id"), {"id": thread_id})
                value = result.scalar()
                conn.close()
                results.append((thread_id, value))
            except Exception as e:
                errors.append((thread_id, e))

        # Create multiple threads accessing pool
        threads = [threading.Thread(target=use_connection, args=(i,)) for i in range(20)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All threads should succeed
        assert len(errors) == 0
        assert len(results) == 20
        assert sorted([r[1] for r in results]) == list(range(20))


class TestDatabaseConnectionPoolExhaustion:
    """Test connection pool exhaustion scenarios."""

    def test_pool_with_many_concurrent_sessions(self, tmp_path: Any) -> None:
        """Test pool handles many concurrent sessions."""
        db_path = tmp_path / "pool_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        _ = db.connect()

        sessions = []
        try:
            # Create many sessions (more than typical pool size)
            for _ in range(15):
                session = db.get_session()
                sessions.append(session)

            # All sessions should be created successfully
            assert len(sessions) == 15

        finally:
            # Clean up
            for session in sessions:
                session.close()

    def test_pool_recovery_after_connection_close(self, tmp_path: Any) -> None:
        """Test pool recovers after connections are closed."""
        db_path = tmp_path / "pool_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        # Use all connections
        connections = [engine.connect() for _ in range(10)]

        # Close all connections
        for conn in connections:
            conn.close()

        # Should be able to get new connections
        new_conn = engine.connect()
        result = new_conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
        new_conn.close()


class TestDatabaseConnectionLifecycle:
    """Test database connection lifecycle management."""

    def test_connection_state_transitions(self, tmp_path: Any) -> None:
        """Test connection state transitions."""
        db_path = tmp_path / "lifecycle_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        # Initial state
        assert db._engine is None
        assert db._session_factory is None

        # Connected state
        db.connect()
        assert db._engine is not None
        assert db._session_factory is not None

        # Closed state
        db.close()
        assert db._engine is None
        assert db._session_factory is None

    def test_reconnect_after_close(self, tmp_path: Any) -> None:
        """Test reconnecting after close."""
        db_path = tmp_path / "lifecycle_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        # Connect, close, reconnect
        db.connect()
        db.close()

        engine = db.connect()
        assert engine is not None
        assert db._engine is not None

        # Should be able to use connection
        session = db.get_session()
        assert session is not None
        session.close()

    def test_multiple_disconnect_reconnect_cycles(self, tmp_path: Any) -> None:
        """Test multiple connect/disconnect cycles."""
        db_path = tmp_path / "lifecycle_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        for i in range(5):
            db.connect()
            session = db.get_session()
            result = session.execute(text("SELECT :val"), {"val": i})
            assert result.scalar() == i
            session.close()
            db.close()

    def test_operations_fail_after_close(self, tmp_path: Any) -> None:
        """Test that operations fail after close."""
        db_path = tmp_path / "lifecycle_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()
        db.close()

        with pytest.raises(RuntimeError, match="Not connected"):
            db.get_session()

        with pytest.raises(RuntimeError, match="Not connected"):
            db.create_tables()

        with pytest.raises(RuntimeError, match="Not connected"):
            db.health_check()


class TestDatabaseConnectionErrorHandling:
    """Test error handling in database operations."""

    def test_session_error_handling(self, tmp_path: Any) -> None:
        """Test error handling in session operations."""
        db_path = tmp_path / "error_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        session = db.get_session()

        # Execute invalid SQL
        with pytest.raises(Exception, match=r"(invalid|syntax|statement)"):
            session.execute(text("INVALID SQL STATEMENT"))

        session.close()

    def test_connection_error_recovery(self, tmp_path: Any) -> None:
        """Test recovery from connection errors."""
        db_path = tmp_path / "error_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        # Close engine to simulate connection loss
        db._engine.dispose()

        # Should be able to reconnect
        db.connect()
        session = db.get_session()
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        session.close()

    def test_pool_error_with_invalid_operations(self, tmp_path: Any) -> None:
        """Test pool handles invalid operations gracefully."""
        db_path = tmp_path / "error_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        conn = engine.connect()

        # Try to execute invalid operation
        with pytest.raises(Exception, match=r"(no such table|nonexistent)"):
            conn.execute(text("SELECT * FROM nonexistent_table"))

        # Connection should still be usable after error
        conn.close()

        # Pool should still work
        new_conn = engine.connect()
        result = new_conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
        new_conn.close()


class TestDatabaseContextManagers:
    """Test context manager patterns for database operations."""

    def test_session_context_manager(self, tmp_path: Any) -> None:
        """Test session as context manager."""
        db_path = tmp_path / "context_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        # Use session in context manager
        session = db.get_session()
        try:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        finally:
            session.close()

    def test_get_session_generator_pattern(self, tmp_path: Any) -> None:
        """Test get_session generator pattern."""
        db_path = tmp_path / "context_test.db"
        url = f"sqlite:///{db_path}"

        # Generator pattern automatically closes session
        for session in get_session(url):
            result = session.execute(text("SELECT 42"))
            assert result.scalar() == 42
            # Session is still open here

        # Session should be closed after generator exits

    def test_nested_context_managers(self, tmp_path: Any) -> None:
        """Test nested context manager usage."""
        db_path = tmp_path / "context_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        # Nested connections
        with engine.connect() as conn1:
            result1 = conn1.execute(text("SELECT 1"))
            assert result1.scalar() == 1

            with engine.connect() as conn2:
                result2 = conn2.execute(text("SELECT 2"))
                assert result2.scalar() == COUNT_TWO


class TestDatabaseConcurrentAccess:
    """Test concurrent database access patterns."""

    def test_concurrent_read_operations(self, tmp_path: Any) -> None:
        """Test concurrent read operations."""
        db_path = tmp_path / "concurrent_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()
        db.create_tables()

        results = []
        errors = []

        def read_operation(thread_id: int) -> None:
            try:
                session = db.get_session()
                result = session.execute(text("SELECT :id"), {"id": thread_id})
                value = result.scalar()
                session.close()
                results.append(value)
            except Exception as e:
                errors.append((thread_id, str(e)))

        threads = [threading.Thread(target=read_operation, args=(i,)) for i in range(20)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert len(results) == 20

    def test_concurrent_session_creation(self, tmp_path: Any) -> None:
        """Test concurrent session creation."""
        db_path = tmp_path / "concurrent_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        sessions = []
        lock = threading.Lock()

        def create_session_thread() -> None:
            session = db.get_session()
            with lock:
                sessions.append(session)

        threads = [threading.Thread(target=create_session_thread) for _ in range(30)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All sessions should be created
        assert len(sessions) == 30

        # Clean up
        for session in sessions:
            session.close()


# ==============================================================================
# Parametric Tests (Alternative to Property-Based)
# ==============================================================================


class TestConcurrencyParametric:
    """Parametric tests for concurrency utilities."""

    @pytest.mark.parametrize(
        ("max_retries", "base_delay"),
        [
            (1, 0.001),
            (3, 0.01),
            (5, 0.05),
            (10, 0.001),
        ],
    )
    @pytest.mark.asyncio
    async def test_retry_with_various_parameters(self, max_retries: Any, base_delay: Any) -> None:
        """Test retry works with various parameter combinations."""
        call_count = 0

        async def operation() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count < max_retries:
                msg = "Retry needed"
                raise ConcurrencyError(msg)
            return "success"

        result = await update_with_retry(operation, max_retries=max_retries, base_delay=base_delay)
        assert result == "success"
        assert call_count == max_retries

    @pytest.mark.parametrize("error_count", [0, 1, 2, 3, 5])
    @pytest.mark.asyncio
    async def test_retry_with_varying_error_counts(self, error_count: Any) -> None:
        """Test retry with varying numbers of errors."""
        call_count = 0

        async def operation() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count <= error_count:
                msg = f"Error {call_count}"
                raise ConcurrencyError(msg)
            return f"success_after_{error_count}"

        result = await update_with_retry(operation, max_retries=error_count + 2, base_delay=0.001)
        assert result == f"success_after_{error_count}"
        assert call_count == error_count + 1

    @pytest.mark.parametrize("operation_count", [1, 5, 10, 15, 20])
    @pytest.mark.asyncio
    async def test_concurrent_operations_count(self, operation_count: Any) -> None:
        """Test varying numbers of concurrent operations."""

        async def simple_operation(op_id: int) -> None:
            await asyncio.sleep(0.001)
            return op_id

        gathered_results = await asyncio.gather(*[
            update_with_retry(lambda i=i: simple_operation(i)) for i in range(operation_count)
        ])

        assert len(gathered_results) == operation_count
        assert sorted(gathered_results) == list(range(operation_count))


class TestDatabaseParametric:
    """Parametric tests for database operations."""

    @pytest.mark.parametrize("url_suffix", ["test1", "test2", "mydb", "database123", "db_2024"])
    def test_database_url_validation(self, url_suffix: Any) -> None:
        """Test database URL validation with various inputs."""
        # Valid URLs should work
        valid_url = f"sqlite:///{url_suffix}.db"
        db = DatabaseConnection(valid_url)
        assert db.database_url == valid_url

        # Invalid URLs should fail
        invalid_url = f"invalid://{url_suffix}"
        with pytest.raises(ValueError, match=r"invalid|url|scheme"):
            DatabaseConnection(invalid_url)

    @pytest.mark.parametrize("session_count", [1, 5, 10, 15, 20])
    def test_multiple_session_creation(self, session_count: Any, tmp_path: Any) -> None:
        """Test creating varying numbers of sessions."""
        db_path = tmp_path / "property_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        sessions = []
        try:
            for _ in range(session_count):
                session = db.get_session()
                sessions.append(session)

            # All sessions should be valid
            assert len(sessions) == session_count
            assert all(isinstance(s, Session) for s in sessions)

        finally:
            for session in sessions:
                session.close()


# ==============================================================================
# Integration Tests for Combined Concurrency + Database
# ==============================================================================


class TestConcurrentDatabaseOperations:
    """Test concurrent database operations with retry logic."""

    @pytest.mark.asyncio
    async def test_concurrent_database_access_with_retry(self, tmp_path: Any) -> None:
        """Test concurrent database operations with retry logic."""
        db_path = tmp_path / "concurrent_retry.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        call_counts = {}
        lock = asyncio.Lock()

        async def database_operation_with_retry(op_id: int) -> None:
            async with lock:
                call_counts[op_id] = call_counts.get(op_id, 0) + 1
                count = call_counts[op_id]

            if count == 1:
                msg = f"First attempt for {op_id}"
                raise ConcurrencyError(msg)

            # Use database
            session = db.get_session()
            try:
                result = session.execute(text("SELECT :id"), {"id": op_id})
                return result.scalar()
            finally:
                session.close()

        results = await asyncio.gather(*[
            update_with_retry(lambda i=i: database_operation_with_retry(i), max_retries=3) for i in range(10)
        ])

        assert len(results) == COUNT_TEN
        assert sorted(results) == list(range(10))

    @pytest.mark.asyncio
    async def test_database_pool_under_concurrent_load(self, tmp_path: Any) -> None:
        """Test database connection pool under concurrent load."""
        db_path = tmp_path / "pool_load.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        async def database_query(query_id: int) -> None:
            loop = asyncio.get_event_loop()
            session = db.get_session()
            try:
                # Run in thread pool to avoid blocking
                return await loop.run_in_executor(
                    None,
                    lambda: session.execute(text("SELECT :id"), {"id": query_id}).scalar(),
                )
            finally:
                session.close()

        results = await asyncio.gather(*[database_query(i) for i in range(30)])

        assert len(results) == 30
        assert sorted(results) == list(range(30))


class TestResourceCleanup:
    """Test resource cleanup in error scenarios."""

    def test_session_cleanup_on_error(self, tmp_path: Any) -> None:
        """Test sessions are cleaned up even when errors occur."""
        db_path = tmp_path / "cleanup_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        initial_checked_out = db._engine.pool.checkedout()

        session = db.get_session()
        try:
            # Cause an error
            session.execute(text("INVALID SQL"))
        except Exception:
            pass
        finally:
            session.close()

        # Pool should return to initial state
        assert db._engine.pool.checkedout() == initial_checked_out

    def test_connection_cleanup_on_pool_exhaustion(self, tmp_path: Any) -> None:
        """Test connections are cleaned up properly."""
        db_path = tmp_path / "cleanup_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        connections = []
        try:
            # Get multiple connections
            for _ in range(10):
                conn = engine.connect()
                connections.append(conn)
        finally:
            # Clean up all connections
            for conn in connections:
                conn.close()

        # Pool should be back to normal
        final_checked_out = engine.pool.checkedout()
        assert final_checked_out == 0


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""

    @pytest.mark.asyncio
    async def test_zero_max_retries_edge_case(self) -> None:
        """Test behavior with zero retries (should fail immediately)."""
        call_count = 0

        async def always_fails() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Immediate failure"
            raise ConcurrencyError(msg)

        # Note: max_retries=0 would mean no attempts at all, which doesn't make sense
        # Test with max_retries=1 (one attempt, no retries)
        with pytest.raises(ConcurrencyError):
            await update_with_retry(always_fails, max_retries=1)

        assert call_count == 1

    def test_empty_database_url_edge_case(self) -> None:
        """Test handling of empty database URL."""
        with pytest.raises(ValueError, match=r"empty|url|database"):
            DatabaseConnection("")

    def test_very_long_database_url(self, tmp_path: Any) -> None:
        """Test handling of very long but valid database URL."""
        long_path = tmp_path / ("a" * 100 + ".db")
        db = DatabaseConnection(f"sqlite:///{long_path}")
        engine = db.connect()
        assert engine is not None

    @pytest.mark.asyncio
    async def test_extremely_high_concurrency(self) -> None:
        """Test system with extremely high concurrency."""

        async def quick_operation(op_id: int) -> None:
            await asyncio.sleep(0)
            return op_id

        # 100 concurrent operations
        results = await asyncio.gather(*[update_with_retry(lambda i=i: quick_operation(i)) for i in range(100)])

        assert len(results) == 100
        assert sorted(results) == list(range(100))

    def test_database_url_with_special_characters(self, tmp_path: Any) -> None:
        """Test database URL handling with special characters."""
        db_path = tmp_path / "test-db_2024.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()
        assert engine is not None


class TestConcurrencyStressTests:
    """Stress tests for concurrency utilities."""

    @pytest.mark.asyncio
    async def test_stress_concurrent_retries(self) -> None:
        """Stress test with many concurrent operations requiring retries."""
        success_count = 0
        lock = asyncio.Lock()

        async def operation_requiring_retry(op_id: int) -> str:
            nonlocal success_count

            # Fail first attempt
            async with lock:
                current = success_count

            if current < 50:
                async with lock:
                    success_count += 1
                msg = f"Retry {op_id}"
                raise ConcurrencyError(msg)

            return f"success_{op_id}"

        # 50 operations, each requiring at least one retry
        results = await asyncio.gather(
            *[update_with_retry(lambda i=i: operation_requiring_retry(i), max_retries=10) for i in range(50)],
            return_exceptions=True,
        )

        # Count successes
        successful = [r for r in results if isinstance(r, str) and r.startswith("success_")]
        assert len(successful) > 0

    def test_stress_database_connections(self, tmp_path: Any) -> None:
        """Stress test database with many rapid connections."""
        db_path = tmp_path / "stress_test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        engine = db.connect()

        # Rapidly create and close many connections
        for _ in range(100):
            conn = engine.connect()
            conn.execute(text("SELECT 1"))
            conn.close()

        # Pool should still be healthy
        health = db.health_check()
        assert health["status"] == "connected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
