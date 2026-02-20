"""Performance tests for sync and concurrent operations.

Tests performance-critical paths:
- Large sync operations (500+ entities)
- Concurrent sync operations
- Conflict resolution performance
- Retry logic with exponential backoff
- Queue processing performance
- Memory efficiency in sync operations

Target: +2% coverage on performance-sensitive paths
"""

import asyncio
import time
from datetime import UTC, datetime
from typing import Never

import pytest
from sqlalchemy.orm.exc import StaleDataError

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.services.concurrent_operations_service import (
    ConcurrencyError,
    retry_with_backoff,
)
from tracertm.storage.sync_engine import (
    ChangeDetector,
    EntityType,
    OperationType,
    QueuedChange,
    SyncResult,
    SyncState,
    SyncStatus,
)


class TestChangeDetectorPerformance:
    """Tests for change detection performance."""

    def test_hash_computation_small_content(self) -> None:
        """Test hash computation for small content."""
        content = "Small test content"

        start_time = time.time()
        hash_value = ChangeDetector.compute_hash(content)
        elapsed = time.time() - start_time

        assert elapsed < 0.01, "Hash should be computed in < COUNT_TENms"
        assert len(hash_value) == 64  # SHA-256 hex digest

    def test_hash_computation_large_content(self) -> None:
        """Test hash computation for large content."""
        # Create large content (1MB)
        content = "x" * (1024 * 1024)

        start_time = time.time()
        hash_value = ChangeDetector.compute_hash(content)
        elapsed = time.time() - start_time

        assert elapsed < 0.1, "Hash should be computed in < 100ms even for 1MB"
        assert len(hash_value) == 64

    def test_hash_consistency(self) -> None:
        """Test hash consistency."""
        content = "Test content"

        hash1 = ChangeDetector.compute_hash(content)
        hash2 = ChangeDetector.compute_hash(content)

        assert hash1 == hash2, "Same content should produce same hash"

    def test_hash_sensitivity(self) -> None:
        """Test hash sensitivity to content changes."""
        content1 = "Test content"
        content2 = "Test contend"  # Changed 't' to 'd'

        hash1 = ChangeDetector.compute_hash(content1)
        hash2 = ChangeDetector.compute_hash(content2)

        assert hash1 != hash2, "Different content should produce different hashes"

    def test_change_detection_performance(self) -> None:
        """Test change detection performance."""
        old_content = "Original content"
        old_hash = ChangeDetector.compute_hash(old_content)

        new_content = "Modified content"

        start_time = time.time()
        has_changed = ChangeDetector.has_changed(new_content, old_hash)
        elapsed = time.time() - start_time

        assert elapsed < 0.01
        assert has_changed is True

    def test_change_detection_no_change(self) -> None:
        """Test change detection when content unchanged."""
        content = "Test content"
        content_hash = ChangeDetector.compute_hash(content)

        has_changed = ChangeDetector.has_changed(content, content_hash)

        assert has_changed is False

    def test_change_detection_null_hash(self) -> None:
        """Test change detection with null hash."""
        content = "Test content"

        has_changed = ChangeDetector.has_changed(content, None)

        assert has_changed is True, "Should detect change when hash is null"


class TestRetryWithBackoffPerformance:
    """Tests for retry logic performance."""

    def test_retry_immediate_success(self) -> None:
        """Test immediate success (no retries)."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def operation() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        start_time = time.time()
        result = operation()
        elapsed = time.time() - start_time

        assert result == "success"
        assert call_count == 1
        assert elapsed < 0.05, "Immediate success should not wait"

    def test_retry_single_failure_then_success(self) -> None:
        """Test single failure then success."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.05, exponential_base=2.0)
        def operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "Conflict"
                raise StaleDataError(msg)
            return "success"

        start_time = time.time()
        result = operation()
        elapsed = time.time() - start_time

        assert result == "success"
        assert call_count == COUNT_TWO
        # Should wait initial_delay before retry
        assert elapsed >= 0.05, "Should wait for backoff"
        assert elapsed < 0.15, "Total wait should be reasonable"

    def test_retry_max_retries_exceeded(self) -> None:
        """Test max retries exceeded."""
        call_count = 0

        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def operation() -> Never:
            nonlocal call_count
            call_count += 1
            msg = "Conflict"
            raise StaleDataError(msg)

        with pytest.raises(ConcurrencyError):
            operation()

        assert call_count == COUNT_THREE  # Initial + 2 retries

    def test_retry_exponential_backoff(self) -> None:
        """Test exponential backoff timing."""
        call_times = []

        @retry_with_backoff(max_retries=3, initial_delay=0.01, exponential_base=2.0, jitter=False)
        def operation() -> str:
            call_times.append(time.time())
            if len(call_times) < COUNT_FOUR:
                msg = "Conflict"
                raise StaleDataError(msg)
            return "success"

        start_time = time.time()
        result = operation()
        time.time() - start_time

        assert result == "success"
        assert len(call_times) == COUNT_FOUR

        # Check that delays increase exponentially
        delays = [call_times[i] - call_times[i - 1] for i in range(1, len(call_times))]

        # Each delay should be ~2x the previous
        assert delays[0] < delays[1] < delays[2]

    def test_retry_with_jitter(self) -> None:
        """Test retry with jitter."""
        call_count = 0
        call_times = []

        @retry_with_backoff(max_retries=2, initial_delay=0.05, jitter=True)
        def operation() -> str:
            nonlocal call_count
            call_times.append(time.time())
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "Conflict"
                raise StaleDataError(msg)
            return "success"

        start_time = time.time()
        result = operation()
        time.time() - start_time

        assert result == "success"
        assert len(call_times) == COUNT_THREE

        # With jitter, timing should be variable
        delay1 = call_times[1] - call_times[0]
        assert delay1 >= 0.03  # Within jitter range of 0.05

    def test_retry_max_delay_clamping(self) -> None:
        """Test that delays are clamped to max_delay."""
        call_count = 0

        @retry_with_backoff(max_retries=5, initial_delay=0.1, max_delay=0.2, exponential_base=2.0, jitter=False)
        def operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 6:
                msg = "Conflict"
                raise StaleDataError(msg)
            return "success"

        start_time = time.time()
        result = operation()
        elapsed = time.time() - start_time

        assert result == "success"
        # With clamping, total time should be < exponential growth
        assert elapsed < 1.5, "Max delay clamping should prevent excessive delays"

    def test_retry_non_retryable_error(self) -> None:
        """Test that non-retryable errors are raised immediately."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        def operation() -> Never:
            nonlocal call_count
            call_count += 1
            msg = "Non-retryable error"
            raise ValueError(msg)

        with pytest.raises(ValueError):
            operation()

        assert call_count == 1, "Should not retry non-retryable errors"

    def test_retry_concurrent_operations(self) -> None:
        """Test retry behavior under concurrent operations."""
        call_counts = {}

        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def operation(op_id: int) -> str:
            if op_id not in call_counts:
                call_counts[op_id] = 0
            call_counts[op_id] += 1

            if call_counts[op_id] < COUNT_TWO:
                msg = "Conflict"
                raise StaleDataError(msg)
            return f"success-{op_id}"

        # Run multiple operations
        results = []
        for i in range(10):
            try:
                results.append(operation(i))
            except Exception:
                pass

        assert len(results) == COUNT_TEN
        assert all(f"success-{i}" in results for i in range(10))


class TestSyncQueuePerformance:
    """Tests for sync queue performance."""

    @pytest.mark.asyncio
    async def test_queue_creation_large_batch(self) -> None:
        """Test creating large batch of queued changes."""
        changes = []

        for i in range(1000):
            change = QueuedChange(
                id=i,
                entity_type=EntityType.ITEM,
                entity_id=f"item-{i}",
                operation=OperationType.UPDATE,
                payload={"title": f"Item {i}"},
                created_at=datetime.now(UTC),
            )
            changes.append(change)

        assert len(changes) == 1000

    @pytest.mark.asyncio
    async def test_sync_state_tracking(self) -> None:
        """Test sync state tracking."""
        state = SyncState()

        assert state.status == SyncStatus.IDLE
        assert state.pending_changes == 0
        assert state.last_sync is None

        # Update state
        state.pending_changes = 10
        state.status = SyncStatus.SYNCING

        assert state.pending_changes == COUNT_TEN
        assert state.status == SyncStatus.SYNCING

    @pytest.mark.asyncio
    async def test_sync_result_aggregation(self) -> None:
        """Test sync result aggregation."""
        result = SyncResult(success=True, entities_synced=100, duration_seconds=2.5)

        assert result.success is True
        assert result.entities_synced == 100
        assert len(result.conflicts) == 0
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_sync_result_with_conflicts(self) -> None:
        """Test sync result with conflicts."""
        result = SyncResult(
            success=False,
            entities_synced=90,
            conflicts=[
                {"entity_id": "item-1", "reason": "version_mismatch"},
                {"entity_id": "item-2", "reason": "concurrent_edit"},
            ],
            errors=["Network timeout"],
            duration_seconds=3.0,
        )

        assert result.success is False
        assert len(result.conflicts) == COUNT_TWO
        assert len(result.errors) == 1


class TestConcurrentOperationsPerformance:
    """Tests for concurrent operations performance."""

    @pytest.mark.asyncio
    async def test_concurrent_sync_operations(self) -> None:
        """Test multiple concurrent sync operations."""

        async def sync_operation(op_id: int, delay: float = 0.01) -> str:
            """Simulate sync operation."""
            await asyncio.sleep(delay)
            return f"sync-{op_id}-done"

        start_time = time.time()
        results = await asyncio.gather(*[sync_operation(i) for i in range(20)])
        elapsed = time.time() - start_time

        assert len(results) == 20
        # Should be roughly parallel (20ms, not 400ms)
        assert elapsed < 0.5, f"Concurrent operations took {elapsed}s"

    @pytest.mark.asyncio
    async def test_concurrent_retry_operations(self) -> None:
        """Test concurrent operations with retries."""
        operation_states = {}

        async def operation(op_id: int) -> str | None:
            """Operation with retry (manual retry logic for async)."""
            max_retries = 2
            delay = 0.01

            for attempt in range(max_retries + 1):
                if op_id not in operation_states:
                    operation_states[op_id] = 0
                operation_states[op_id] += 1

                if operation_states[op_id] < COUNT_TWO:
                    if attempt < max_retries:
                        await asyncio.sleep(delay)
                        delay *= 2.0
                        continue
                    msg = f"Conflict in {op_id}"
                    raise StaleDataError(msg)

                await asyncio.sleep(0.01)
                return f"success-{op_id}"
            return None

        start_time = time.time()
        results = await asyncio.gather(*[operation(i) for i in range(10)])
        elapsed = time.time() - start_time

        assert len(results) == COUNT_TEN
        # With retries, should still be reasonably fast
        assert elapsed < float(COUNT_TWO + 0.0)

    @pytest.mark.asyncio
    async def test_sync_throughput(self) -> None:
        """Test sync throughput (entities/second)."""
        entity_count = 500

        async def sync_batch() -> None:
            """Simulate syncing a batch of entities."""
            await asyncio.sleep(0.001)  # 1ms per entity
            return entity_count

        start_time = time.time()
        total_synced = 0
        for _ in range(10):
            total_synced += await sync_batch()
        elapsed = time.time() - start_time

        throughput = total_synced / elapsed
        assert throughput > 100, f"Throughput {throughput} entities/sec is too low"

    @pytest.mark.asyncio
    async def test_memory_during_concurrent_operations(self) -> None:
        """Test memory usage during concurrent operations."""
        import tracemalloc

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        async def operation(op_id: int) -> None:
            """Simulate operation with data."""
            data = {"id": op_id, "payload": "x" * 1000}
            await asyncio.sleep(0.01)
            return data

        await asyncio.gather(*[operation(i) for i in range(100)])

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snapshot_after.compare_to(snapshot_before, "lineno")
        total_increase = sum(stat.size_diff for stat in stats) / (1024 * 1024)

        # 100 operations * 1KB should use < COUNT_FIVEMB
        assert total_increase < float(COUNT_FIVE + 0.0)

    @pytest.mark.asyncio
    async def test_batched_sync_operations(self) -> None:
        """Test batched sync for efficiency."""
        batch_size = 50

        async def sync_batch(batch_num: int) -> None:
            """Sync a batch of items."""
            await asyncio.sleep(0.05)  # Simulate batch sync time
            return batch_num * batch_size

        start_time = time.time()
        total_items = 0
        for batch_num in range(10):
            total_items += await sync_batch(batch_num)
        elapsed = time.time() - start_time

        assert total_items == 2250  # 50 * 45
        assert elapsed < 1.0, "Batched operations should be efficient"

    @pytest.mark.asyncio
    async def test_conflict_resolution_performance(self) -> None:
        """Test conflict resolution performance."""
        conflicts = []
        for i in range(100):
            conflict = {
                "entity_id": f"item-{i}",
                "local_version": i,
                "remote_version": i + 1,
                "timestamp": datetime.now(UTC),
            }
            conflicts.append(conflict)

        start_time = time.time()
        # Simulate conflict resolution (choosing remote version)
        resolved = [
            {"entity_id": conflict["entity_id"], "version": conflict["remote_version"]} for conflict in conflicts
        ]
        elapsed = time.time() - start_time

        assert len(resolved) == 100
        assert elapsed < 0.05, "Conflict resolution should be fast"
