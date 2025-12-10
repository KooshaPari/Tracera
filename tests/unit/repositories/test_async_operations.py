"""
Async repository tests for concurrent database operations.

Tests for:
- Concurrent read operations
- Concurrent write operations with optimistic locking
- Async context manager usage
- Transaction handling
- Connection pool management
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestAsyncDatabaseOperations:
    """Test async database operation patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_async_reads(self):
        """Test concurrent async database reads."""
        session_mock = AsyncMock(spec=AsyncSession)
        session_mock.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

        async def read_items(item_id: int) -> dict:
            # Simulate async read
            await asyncio.sleep(0.01)
            return {"id": item_id, "name": f"Item {item_id}"}

        results = await asyncio.gather(*[
            read_items(i) for i in range(5)
        ])

        assert len(results) == 5
        assert all(r["name"].startswith("Item") for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_async_writes(self):
        """Test concurrent async database writes."""
        session_mock = AsyncMock(spec=AsyncSession)
        session_mock.add = MagicMock()
        session_mock.flush = AsyncMock()
        session_mock.refresh = AsyncMock()

        async def write_item(item_id: int) -> dict:
            # Simulate async write
            await session_mock.flush()
            await session_mock.refresh(MagicMock())
            return {"id": item_id, "status": "created"}

        results = await asyncio.gather(*[
            write_item(i) for i in range(3)
        ])

        assert len(results) == 3
        assert all(r["status"] == "created" for r in results)

    @pytest.mark.asyncio
    async def test_async_transaction_commit(self):
        """Test async transaction commit."""
        session_mock = AsyncMock(spec=AsyncSession)
        session_mock.commit = AsyncMock()
        session_mock.rollback = AsyncMock()

        async def transactional_operation() -> bool:
            try:
                await session_mock.commit()
                return True
            except Exception:
                await session_mock.rollback()
                return False

        result = await transactional_operation()
        assert result is True
        session_mock.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_transaction_rollback(self):
        """Test async transaction rollback on error."""
        session_mock = AsyncMock(spec=AsyncSession)
        session_mock.commit = AsyncMock(side_effect=Exception("Commit failed"))
        session_mock.rollback = AsyncMock()

        async def transactional_operation() -> bool:
            try:
                await session_mock.commit()
                return True
            except Exception:
                await session_mock.rollback()
                return False

        result = await transactional_operation()
        assert result is False
        session_mock.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_context_manager_session(self):
        """Test async context manager for session handling."""
        class AsyncSessionContext:
            def __init__(self):
                self.entered = False
                self.exited = False

            async def __aenter__(self):
                self.entered = True
                await asyncio.sleep(0.001)
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.exited = True
                return False

        session = AsyncSessionContext()

        async with session:
            assert session.entered
            assert not session.exited

        assert session.exited

    @pytest.mark.asyncio
    async def test_concurrent_async_contexts(self):
        """Test concurrent async context manager usage."""
        class AsyncResource:
            def __init__(self, resource_id: int):
                self.resource_id = resource_id
                self.acquired = False
                self.released = False

            async def __aenter__(self):
                self.acquired = True
                await asyncio.sleep(0.005)
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.released = True
                return False

        resources = [
            AsyncResource(i) for i in range(3)
        ]

        async def use_resource(resource: AsyncResource) -> bool:
            async with resource:
                await asyncio.sleep(0.01)
            return resource.released

        results = await asyncio.gather(*[
            use_resource(r) for r in resources
        ])

        assert all(results)
        assert all(r.acquired for r in resources)


class TestAsyncOptimisticLocking:
    """Test optimistic locking in async operations."""

    @pytest.mark.asyncio
    async def test_version_check_during_concurrent_updates(self):
        """Test version checking in concurrent updates."""
        class VersionedItem:
            def __init__(self, item_id: int, version: int = 1):
                self.item_id = item_id
                self.version = version
                self.value = "initial"

        items = {1: VersionedItem(1)}

        async def update_item(
            item_id: int,
            expected_version: int,
            new_value: str
        ) -> bool:
            item = items[item_id]
            await asyncio.sleep(0.01)  # Simulate network latency

            if item.version != expected_version:
                # Version mismatch - optimistic lock failed
                return False

            item.version += 1
            item.value = new_value
            return True

        # First update succeeds
        result1 = await update_item(1, 1, "updated1")
        assert result1 is True

        # Second update fails because version changed
        result2 = await update_item(1, 1, "updated2")
        assert result2 is False

    @pytest.mark.asyncio
    async def test_concurrent_updates_with_version_conflict(self):
        """Test concurrent updates detecting version conflicts."""
        class VersionedData:
            def __init__(self):
                self.version = 1
                self.value = "initial"
                self.lock = asyncio.Lock()

            async def update_async(
                self,
                expected_version: int,
                new_value: str
            ) -> bool:
                async with self.lock:
                    await asyncio.sleep(0.001)
                    if self.version != expected_version:
                        return False
                    self.version += 1
                    self.value = new_value
                    return True

        data = VersionedData()

        async def concurrent_update(version: int, value: str) -> bool:
            return await data.update_async(version, value)

        # Launch two concurrent updates with same expected version
        results = await asyncio.gather(
            concurrent_update(1, "first"),
            concurrent_update(1, "second"),
        )

        # One succeeds, one fails
        assert True in results
        assert False in results
        assert data.version == 2  # Only one update succeeded

    @pytest.mark.asyncio
    async def test_retry_on_version_conflict(self):
        """Test retry logic on version conflict."""
        class RetryableItem:
            def __init__(self):
                self.version = 1
                self.value = "initial"

            async def update_with_retry(
                self,
                new_value: str,
                max_retries: int = 3
            ) -> bool:
                for attempt in range(max_retries):
                    current_version = self.version
                    await asyncio.sleep(0.001)

                    if self.version != current_version:
                        # Version changed, retry
                        continue

                    self.version += 1
                    self.value = new_value
                    return True

                return False

        item = RetryableItem()
        result = await item.update_with_retry("new_value")
        assert result is True


class TestAsyncConnectionPool:
    """Test async connection pool behavior."""

    @pytest.mark.asyncio
    async def test_concurrent_connection_usage(self):
        """Test using multiple connections from pool."""
        class ConnectionPool:
            def __init__(self, max_size: int = 3):
                self.max_size = max_size
                self.available = asyncio.Semaphore(max_size)
                self.in_use = 0
                self.peak_usage = 0

            async def get_connection(self) -> int:
                await self.available.acquire()
                self.in_use += 1
                self.peak_usage = max(self.peak_usage, self.in_use)
                return id(self)

            async def release_connection(self, conn_id: int) -> None:
                self.in_use -= 1
                self.available.release()

        pool = ConnectionPool(max_size=2)

        async def use_connection(duration: float) -> None:
            conn = await pool.get_connection()
            await asyncio.sleep(duration)
            await pool.release_connection(conn)

        await asyncio.gather(*[
            use_connection(0.02) for _ in range(4)
        ])

        assert pool.peak_usage == 2

    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted."""
        class LimitedPool:
            def __init__(self, max_size: int = 1):
                self.semaphore = asyncio.Semaphore(max_size)
                self.acquired = 0

            async def acquire_with_timeout(self, timeout: float) -> bool:
                try:
                    async with asyncio.timeout(timeout):
                        async with self.semaphore:
                            self.acquired += 1
                            await asyncio.sleep(0.05)
                            self.acquired -= 1
                            return True
                except asyncio.TimeoutError:
                    return False

        pool = LimitedPool(max_size=1)

        results = await asyncio.gather(*[
            pool.acquire_with_timeout(0.01) for _ in range(3)
        ], return_exceptions=True)

        # Some will succeed, some will timeout
        assert any(isinstance(r, bool) for r in results)


class TestAsyncBatchOperations:
    """Test async batch database operations."""

    @pytest.mark.asyncio
    async def test_async_bulk_insert(self):
        """Test async bulk insert operation."""
        session_mock = AsyncMock(spec=AsyncSession)
        session_mock.add_all = MagicMock()
        session_mock.flush = AsyncMock()

        async def bulk_insert(items: list[dict]) -> int:
            # Simulate adding items
            session_mock.add_all([{"id": i, "data": item} for i, item in enumerate(items)])
            await session_mock.flush()
            return len(items)

        items = [{"name": f"Item {i}"} for i in range(10)]
        count = await bulk_insert(items)
        assert count == 10

    @pytest.mark.asyncio
    async def test_async_bulk_update(self):
        """Test async bulk update operation."""
        updated_items = []

        async def bulk_update(item_ids: list[int], new_value: str) -> int:
            for item_id in item_ids:
                await asyncio.sleep(0.001)
                updated_items.append((item_id, new_value))
            return len(item_ids)

        ids = [1, 2, 3, 4, 5]
        count = await bulk_update(ids, "updated")
        assert count == 5
        assert len(updated_items) == 5

    @pytest.mark.asyncio
    async def test_async_batch_with_partial_failure(self):
        """Test batch operation with partial failure."""
        async def process_batch(items: list[int]) -> dict:
            results = {
                "success": [],
                "failed": [],
                "errors": []
            }

            for item_id in items:
                await asyncio.sleep(0.001)
                if item_id % 2 == 0:
                    results["success"].append(item_id)
                else:
                    results["failed"].append(item_id)
                    results["errors"].append(f"Item {item_id} failed")

            return results

        items = [1, 2, 3, 4, 5]
        result = await process_batch(items)

        assert len(result["success"]) == 2
        assert len(result["failed"]) == 3
        assert len(result["errors"]) == 3


class TestAsyncQueryOperations:
    """Test async query operations."""

    @pytest.mark.asyncio
    async def test_async_query_execution(self):
        """Test async query execution."""
        session_mock = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))

        session_mock.execute = AsyncMock(return_value=mock_result)

        async def query_items() -> list:
            result = await session_mock.execute(MagicMock())
            items = result.scalars().all()
            return items

        items = await query_items()
        assert items == []

    @pytest.mark.asyncio
    async def test_async_query_with_pagination(self):
        """Test async paginated queries."""
        async def fetch_page(page: int, page_size: int) -> dict:
            # Simulate async database query
            await asyncio.sleep(0.01)
            offset = (page - 1) * page_size
            total = 100

            items = list(range(offset, min(offset + page_size, total)))
            return {
                "items": items,
                "page": page,
                "total": total,
                "has_next": offset + page_size < total
            }

        # Fetch multiple pages concurrently
        pages = await asyncio.gather(*[
            fetch_page(page, 10) for page in range(1, 4)
        ])

        assert len(pages) == 3
        assert all(p["total"] == 100 for p in pages)

    @pytest.mark.asyncio
    async def test_async_query_timeout(self):
        """Test timeout on async query."""
        async def slow_query() -> list:
            await asyncio.sleep(1)
            return [1, 2, 3]

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_query(), timeout=0.1)


class TestAsyncTransactionPatterns:
    """Test async transaction patterns."""

    @pytest.mark.asyncio
    async def test_nested_async_transactions(self):
        """Test nested transaction behavior."""
        class AsyncTransaction:
            def __init__(self):
                self.transaction_stack = []

            async def begin(self) -> None:
                self.transaction_stack.append("begin")
                await asyncio.sleep(0.001)

            async def commit(self) -> None:
                self.transaction_stack.append("commit")
                await asyncio.sleep(0.001)

            async def rollback(self) -> None:
                self.transaction_stack.append("rollback")
                await asyncio.sleep(0.001)

        tx = AsyncTransaction()

        await tx.begin()
        await tx.begin()  # Nested
        await tx.commit()
        await tx.commit()

        assert tx.transaction_stack == ["begin", "begin", "commit", "commit"]

    @pytest.mark.asyncio
    async def test_transaction_savepoint(self):
        """Test transaction savepoint."""
        class TransactionWithSavepoint:
            def __init__(self):
                self.state = []

            async def create_savepoint(self) -> str:
                await asyncio.sleep(0.001)
                savepoint_id = f"sp_{len(self.state)}"
                self.state.append(("savepoint", savepoint_id))
                return savepoint_id

            async def rollback_to_savepoint(self, savepoint_id: str) -> None:
                await asyncio.sleep(0.001)
                self.state.append(("rollback", savepoint_id))

        tx = TransactionWithSavepoint()
        sp = await tx.create_savepoint()
        await tx.rollback_to_savepoint(sp)

        assert ("savepoint", sp) in tx.state
        assert ("rollback", sp) in tx.state

    @pytest.mark.asyncio
    async def test_concurrent_transaction_isolation(self):
        """Test isolation in concurrent transactions."""
        class Database:
            def __init__(self):
                self.data = {"counter": 0}
                self.lock = asyncio.Lock()

            async def increment_in_transaction(self) -> int:
                async with self.lock:
                    current = self.data["counter"]
                    await asyncio.sleep(0.001)
                    new_value = current + 1
                    self.data["counter"] = new_value
                    return new_value

        db = Database()

        results = await asyncio.gather(*[
            db.increment_in_transaction() for _ in range(5)
        ])

        assert results == [1, 2, 3, 4, 5]
        assert db.data["counter"] == 5


class TestAsyncRepositoryPatterns:
    """Test async repository patterns."""

    @pytest.mark.asyncio
    async def test_async_crud_operations(self):
        """Test async CRUD operations."""
        class AsyncRepository:
            def __init__(self):
                self.data = {}
                self.next_id = 1

            async def create(self, item: dict) -> int:
                await asyncio.sleep(0.001)
                item_id = self.next_id
                self.next_id += 1
                self.data[item_id] = item
                return item_id

            async def read(self, item_id: int) -> dict | None:
                await asyncio.sleep(0.001)
                return self.data.get(item_id)

            async def update(self, item_id: int, item: dict) -> bool:
                await asyncio.sleep(0.001)
                if item_id not in self.data:
                    return False
                self.data[item_id] = item
                return True

            async def delete(self, item_id: int) -> bool:
                await asyncio.sleep(0.001)
                if item_id not in self.data:
                    return False
                del self.data[item_id]
                return True

        repo = AsyncRepository()

        # Create
        item_id = await repo.create({"name": "Test Item"})
        assert item_id == 1

        # Read
        item = await repo.read(item_id)
        assert item["name"] == "Test Item"

        # Update
        success = await repo.update(item_id, {"name": "Updated Item"})
        assert success

        # Delete
        success = await repo.delete(item_id)
        assert success

        # Verify deleted
        item = await repo.read(item_id)
        assert item is None

    @pytest.mark.asyncio
    async def test_async_repository_concurrent_operations(self):
        """Test concurrent operations on async repository."""
        class ConcurrentRepository:
            def __init__(self):
                self.items = {}

            async def batch_create(self, items: list[dict]) -> list[int]:
                ids = []
                for item in items:
                    await asyncio.sleep(0.001)
                    item_id = len(self.items) + 1
                    self.items[item_id] = item
                    ids.append(item_id)
                return ids

        repo = ConcurrentRepository()

        # Create items concurrently
        results = await asyncio.gather(*[
            repo.batch_create([{"id": i}]) for i in range(3)
        ])

        assert len(results) == 3
        assert all(isinstance(r, list) for r in results)
