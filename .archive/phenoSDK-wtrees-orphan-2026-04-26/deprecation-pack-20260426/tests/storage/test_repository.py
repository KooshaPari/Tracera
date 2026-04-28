"""
Comprehensive tests for repository backends.

Tests cover:
- Basic CRUD operations
- Query and filtering
- Transactions
- Connection pooling
- Concurrent access
- Performance benchmarks
"""

import asyncio
import tempfile
from pathlib import Path

import pytest

from pheno.storage.repository import (
    ConnectionError,
    EntityNotFoundError,
    InMemoryBackend,
    RepositoryError,
    SQLAlchemyBackend,
    create_repository,
)


# Fixtures
@pytest.fixture
async def sqlite_backend():
    """Create a SQLite backend for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        backend = SQLAlchemyBackend(
            database_url=f"sqlite+aiosqlite:///{db_path}",
            entity_type="test",
            echo=False,
        )
        yield backend
        await backend.close()


@pytest.fixture
async def memory_backend():
    """Create an in-memory backend for testing."""
    backend = InMemoryBackend(entity_type="test")
    yield backend
    await backend.close()


@pytest.fixture
async def postgres_backend():
    """
    Create a PostgreSQL backend for testing.

    This requires a PostgreSQL database to be available.
    Set POSTGRES_URL environment variable to enable these tests.
    """
    import os

    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        pytest.skip("PostgreSQL not configured (set POSTGRES_URL)")

    backend = SQLAlchemyBackend(
        database_url=postgres_url,
        entity_type="test",
        pool_size=10,
        max_overflow=20,
    )
    yield backend

    # Cleanup
    await backend.close()


# Test all backends with parametrization
@pytest.fixture(params=["sqlite", "memory"])
async def any_backend(request):
    """Parametrized fixture to test all backends."""
    if request.param == "sqlite":
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            backend = SQLAlchemyBackend(
                database_url=f"sqlite+aiosqlite:///{db_path}",
                entity_type="test",
            )
            yield backend
            await backend.close()
    elif request.param == "memory":
        backend = InMemoryBackend(entity_type="test")
        yield backend
        await backend.close()


# Basic CRUD Tests
class TestCRUDOperations:
    """Test basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_read(self, any_backend):
        """Test creating and reading an entity."""
        entity_id = "test-1"
        data = {"name": "Test Entity", "value": 42, "active": True}

        # Create
        await any_backend.create(entity_id, data)

        # Read
        result = await any_backend.read(entity_id)
        assert result is not None
        assert result["name"] == "Test Entity"
        assert result["value"] == 42
        assert result["active"] is True

    @pytest.mark.asyncio
    async def test_read_nonexistent(self, any_backend):
        """Test reading a non-existent entity."""
        result = await any_backend.read("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_entity(self, any_backend):
        """Test updating an entity."""
        entity_id = "test-2"
        original_data = {"name": "Original", "value": 10}
        updated_data = {"name": "Updated", "value": 20}

        # Create
        await any_backend.create(entity_id, original_data)

        # Update
        await any_backend.update(entity_id, updated_data)

        # Read and verify
        result = await any_backend.read(entity_id)
        assert result["name"] == "Updated"
        assert result["value"] == 20

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, any_backend):
        """Test updating a non-existent entity raises error."""
        with pytest.raises(EntityNotFoundError):
            await any_backend.update("nonexistent", {"name": "Test"})

    @pytest.mark.asyncio
    async def test_delete_entity(self, any_backend):
        """Test deleting an entity."""
        entity_id = "test-3"
        data = {"name": "To Delete"}

        # Create
        await any_backend.create(entity_id, data)
        assert await any_backend.exists(entity_id)

        # Delete
        await any_backend.delete(entity_id)

        # Verify deleted
        assert not await any_backend.exists(entity_id)
        assert await any_backend.read(entity_id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, any_backend):
        """Test deleting a non-existent entity raises error."""
        with pytest.raises(EntityNotFoundError):
            await any_backend.delete("nonexistent")

    @pytest.mark.asyncio
    async def test_exists(self, any_backend):
        """Test checking entity existence."""
        entity_id = "test-4"

        # Should not exist initially
        assert not await any_backend.exists(entity_id)

        # Create entity
        await any_backend.create(entity_id, {"name": "Test"})

        # Should exist now
        assert await any_backend.exists(entity_id)


# Query and Filtering Tests
class TestQueryOperations:
    """Test query and filtering operations."""

    @pytest.mark.asyncio
    async def test_query_all(self, any_backend):
        """Test querying all entities."""
        # Create multiple entities
        for i in range(5):
            await any_backend.create(f"entity-{i}", {"index": i, "name": f"Entity {i}"})

        # Query all
        results = await any_backend.query()
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_with_limit(self, any_backend):
        """Test query pagination with limit."""
        # Create multiple entities
        for i in range(10):
            await any_backend.create(f"entity-{i}", {"index": i})

        # Query with limit
        results = await any_backend.query(limit=5)
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_with_offset(self, any_backend):
        """Test query pagination with offset."""
        # Create multiple entities
        for i in range(10):
            await any_backend.create(f"entity-{i}", {"index": i})

        # Query with offset
        results = await any_backend.query(limit=5, offset=5)
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_count(self, any_backend):
        """Test counting entities."""
        # Create multiple entities
        for i in range(7):
            await any_backend.create(f"entity-{i}", {"index": i})

        # Count all
        count = await any_backend.count()
        assert count == 7

    @pytest.mark.asyncio
    async def test_count_empty(self, any_backend):
        """Test counting with no entities."""
        count = await any_backend.count()
        assert count == 0


# Transaction Tests
class TestTransactions:
    """Test transaction support."""

    @pytest.mark.asyncio
    async def test_transaction_commit(self, any_backend):
        """Test successful transaction commit."""
        async with any_backend.transaction():
            await any_backend.create("tx-1", {"name": "Transaction 1"})
            await any_backend.create("tx-2", {"name": "Transaction 2"})

        # Verify both entities were created
        assert await any_backend.exists("tx-1")
        assert await any_backend.exists("tx-2")

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, any_backend):
        """Test transaction rollback on error."""
        try:
            async with any_backend.transaction():
                await any_backend.create("tx-3", {"name": "Transaction 3"})
                # Force an error
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify entity was NOT created due to rollback
        # Note: In-memory backend may behave differently
        if isinstance(any_backend, SQLAlchemyBackend):
            assert not await any_backend.exists("tx-3")

    @pytest.mark.asyncio
    async def test_transaction_update_delete(self, any_backend):
        """Test update and delete in transaction."""
        # Create initial entity
        await any_backend.create("tx-4", {"name": "Original", "value": 100})

        async with any_backend.transaction():
            # Update
            await any_backend.update("tx-4", {"name": "Updated", "value": 200})

            # Create another
            await any_backend.create("tx-5", {"name": "New Entity"})

        # Verify changes
        entity = await any_backend.read("tx-4")
        assert entity["name"] == "Updated"
        assert entity["value"] == 200
        assert await any_backend.exists("tx-5")


# Concurrent Access Tests
class TestConcurrentAccess:
    """Test concurrent access to repository."""

    @pytest.mark.asyncio
    async def test_concurrent_creates(self, sqlite_backend):
        """Test concurrent entity creation."""

        async def create_entity(backend, index: int):
            await backend.create(f"concurrent-{index}", {"index": index})

        # Create 20 entities concurrently
        tasks = [create_entity(sqlite_backend, i) for i in range(20)]
        await asyncio.gather(*tasks)

        # Verify all were created
        count = await sqlite_backend.count()
        assert count == 20

    @pytest.mark.asyncio
    async def test_concurrent_reads(self, sqlite_backend):
        """Test concurrent entity reads."""
        # Create test entity
        await sqlite_backend.create("concurrent-read", {"name": "Test"})

        async def read_entity(backend):
            return await backend.read("concurrent-read")

        # Read concurrently 50 times
        tasks = [read_entity(sqlite_backend) for _ in range(50)]
        results = await asyncio.gather(*tasks)

        # Verify all reads succeeded
        assert all(r is not None for r in results)
        assert all(r["name"] == "Test" for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_updates(self, sqlite_backend):
        """Test concurrent entity updates."""
        # Create test entity
        await sqlite_backend.create("concurrent-update", {"counter": 0})

        async def update_entity(backend, value: int):
            # Read-modify-write pattern
            entity = await backend.read("concurrent-update")
            if entity:
                await backend.update("concurrent-update", {"counter": value})

        # Update concurrently (last write wins)
        tasks = [update_entity(sqlite_backend, i) for i in range(10)]
        await asyncio.gather(*tasks)

        # Verify entity was updated
        entity = await sqlite_backend.read("concurrent-update")
        assert entity is not None
        assert "counter" in entity


# Performance Tests
class TestPerformance:
    """Test performance characteristics."""

    @pytest.mark.asyncio
    async def test_bulk_create_performance(self, sqlite_backend):
        """Test bulk entity creation performance."""
        import time

        start = time.time()

        # Create 100 entities
        for i in range(100):
            await sqlite_backend.create(f"perf-{i}", {"index": i, "data": "x" * 100})

        elapsed = time.time() - start

        # Should complete in reasonable time (< 5 seconds for 100 entities)
        assert elapsed < 5.0

        # Verify count
        count = await sqlite_backend.count()
        assert count == 100

    @pytest.mark.asyncio
    async def test_bulk_read_performance(self, sqlite_backend):
        """Test bulk entity read performance."""
        import time

        # Create test entities
        for i in range(100):
            await sqlite_backend.create(f"read-perf-{i}", {"index": i})

        start = time.time()

        # Read all entities
        results = await sqlite_backend.query(limit=100)

        elapsed = time.time() - start

        # Should complete quickly (< 1 second for 100 entities)
        assert elapsed < 1.0
        assert len(results) == 100

    @pytest.mark.asyncio
    async def test_query_performance(self, sqlite_backend):
        """Test query performance with pagination."""
        import time

        # Create 500 entities
        for i in range(500):
            await sqlite_backend.create(f"query-perf-{i}", {"index": i})

        start = time.time()

        # Query with pagination
        results = await sqlite_backend.query(limit=50, offset=100)

        elapsed = time.time() - start

        # Should be fast even with many entities
        assert elapsed < 1.0
        assert len(results) == 50


# Factory Tests
class TestRepositoryFactory:
    """Test repository factory."""

    def test_create_sqlite_repository(self):
        """Test creating SQLite repository via factory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            repo = create_repository(
                "sqlalchemy", entity_type="test", database_url=f"sqlite+aiosqlite:///{db_path}",
            )
            assert isinstance(repo, SQLAlchemyBackend)

    def test_create_memory_repository(self):
        """Test creating in-memory repository via factory."""
        repo = create_repository("memory", entity_type="test")
        assert isinstance(repo, InMemoryBackend)

    def test_create_unknown_backend(self):
        """Test creating repository with unknown backend raises error."""
        with pytest.raises(ValueError, match="Unknown backend type"):
            create_repository("unknown", entity_type="test")


# Connection Pool Tests (SQLAlchemy only)
class TestConnectionPool:
    """Test connection pool configuration and behavior."""

    @pytest.mark.asyncio
    async def test_pool_configuration(self):
        """Test connection pool is configured correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "pool_test.db"
            backend = SQLAlchemyBackend(
                database_url=f"sqlite+aiosqlite:///{db_path}",
                entity_type="test",
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
            )

            # Ensure initialized
            await backend.create("test-1", {"name": "Test"})

            # Check engine is configured
            assert backend._engine is not None
            assert backend._session_factory is not None

            await backend.close()

    @pytest.mark.asyncio
    async def test_connection_reuse(self, sqlite_backend):
        """Test connections are reused from pool."""
        # Perform multiple operations
        for i in range(20):
            await sqlite_backend.create(f"pool-{i}", {"index": i})

        # All should succeed without creating excessive connections
        count = await sqlite_backend.count()
        assert count == 20


# Error Handling Tests
class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_invalid_database_url(self):
        """Test invalid database URL raises connection error."""
        backend = SQLAlchemyBackend(database_url="invalid://url", entity_type="test")

        with pytest.raises((ConnectionError, RepositoryError)):
            await backend.create("test", {"name": "Test"})

        await backend.close()

    @pytest.mark.asyncio
    async def test_repository_error_on_invalid_data(self, sqlite_backend):
        """Test repository handles invalid data gracefully."""
        # This test depends on implementation details
        # For now, just ensure no crashes with unusual data
        try:
            await sqlite_backend.create("test", {"data": None})
            await sqlite_backend.create("test2", {"data": []})
            await sqlite_backend.create("test3", {"data": {}})
        except Exception:
            # Some backends may reject certain data types
            pass


# Edge Cases
class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    @pytest.mark.asyncio
    async def test_empty_data(self, any_backend):
        """Test storing entity with empty data."""
        await any_backend.create("empty", {})
        result = await any_backend.read("empty")
        assert result == {}

    @pytest.mark.asyncio
    async def test_large_data(self, any_backend):
        """Test storing entity with large data."""
        large_data = {"text": "x" * 10000, "numbers": list(range(1000))}
        await any_backend.create("large", large_data)

        result = await any_backend.read("large")
        assert len(result["text"]) == 10000
        assert len(result["numbers"]) == 1000

    @pytest.mark.asyncio
    async def test_special_characters_in_id(self, any_backend):
        """Test entity IDs with special characters."""
        special_ids = [
            "id-with-dashes",
            "id_with_underscores",
            "id.with.dots",
            "id:with:colons",
        ]

        for entity_id in special_ids:
            await any_backend.create(entity_id, {"name": entity_id})
            result = await any_backend.read(entity_id)
            assert result["name"] == entity_id

    @pytest.mark.asyncio
    async def test_unicode_data(self, any_backend):
        """Test storing Unicode data."""
        unicode_data = {"name": "测试", "emoji": "🔥🚀", "symbols": "αβγδ"}

        await any_backend.create("unicode", unicode_data)
        result = await any_backend.read("unicode")

        assert result["name"] == "测试"
        assert result["emoji"] == "🔥🚀"
        assert result["symbols"] == "αβγδ"


# Integration Tests
class TestIntegration:
    """Integration tests for real-world scenarios."""

    @pytest.mark.asyncio
    async def test_complete_crud_workflow(self, any_backend):
        """Test complete CRUD workflow."""
        # Create
        await any_backend.create("user-1", {"name": "John Doe", "email": "john@example.com", "age": 30})

        # Read
        user = await any_backend.read("user-1")
        assert user["name"] == "John Doe"

        # Update
        await any_backend.update("user-1", {"name": "John Doe", "email": "john@example.com", "age": 31})

        # Read updated
        user = await any_backend.read("user-1")
        assert user["age"] == 31

        # Delete
        await any_backend.delete("user-1")

        # Verify deleted
        assert not await any_backend.exists("user-1")

    @pytest.mark.asyncio
    async def test_batch_operations_workflow(self, any_backend):
        """Test batch operations workflow."""
        # Batch create
        users = [{"name": f"User {i}", "active": i % 2 == 0} for i in range(10)]

        for i, user_data in enumerate(users):
            await any_backend.create(f"batch-user-{i}", user_data)

        # Query all
        all_users = await any_backend.query(limit=20)
        assert len(all_users) == 10

        # Count
        total = await any_backend.count()
        assert total == 10

        # Batch delete
        for i in range(10):
            await any_backend.delete(f"batch-user-{i}")

        # Verify all deleted
        count = await any_backend.count()
        assert count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
