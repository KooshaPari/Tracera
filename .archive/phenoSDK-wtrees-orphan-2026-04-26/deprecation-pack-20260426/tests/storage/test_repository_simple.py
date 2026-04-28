"""
Simple tests for repository backends that don't require external dependencies.

These tests use the InMemoryBackend which has no dependencies.
For full SQLAlchemy tests, install sqlalchemy and aiosqlite:
    pip install 'sqlalchemy>=2.0.0' 'aiosqlite>=0.19.0'
"""


import pytest

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)
pytestmark = pytest.mark.asyncio

from pheno.storage.repository import (
    EntityNotFoundError,
    InMemoryBackend,
    create_repository,
)


# Fixtures
@pytest.fixture
def memory_backend():
    """Create an in-memory backend for testing."""
    backend = InMemoryBackend(entity_type="test")
    return backend


# Basic CRUD Tests
class TestInMemoryCRUD:
    """Test basic CRUD operations with in-memory backend."""

    @pytest.mark.asyncio
    async def test_create_and_read(self, memory_backend):
        """Test creating and reading an entity."""
        entity_id = "test-1"
        data = {"name": "Test Entity", "value": 42, "active": True}

        # Create
        await memory_backend.create(entity_id, data)

        # Read
        result = await memory_backend.read(entity_id)
        assert result is not None
        assert result["name"] == "Test Entity"
        assert result["value"] == 42
        assert result["active"] is True

    @pytest.mark.asyncio
    async def test_read_nonexistent(self, memory_backend):
        """Test reading a non-existent entity."""
        result = await memory_backend.read("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_entity(self, memory_backend):
        """Test updating an entity."""
        entity_id = "test-2"
        original_data = {"name": "Original", "value": 10}
        updated_data = {"name": "Updated", "value": 20}

        # Create
        await memory_backend.create(entity_id, original_data)

        # Update
        await memory_backend.update(entity_id, updated_data)

        # Read and verify
        result = await memory_backend.read(entity_id)
        assert result["name"] == "Updated"
        assert result["value"] == 20

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, memory_backend):
        """Test updating a non-existent entity raises error."""
        with pytest.raises(EntityNotFoundError):
            await memory_backend.update("nonexistent", {"name": "Test"})

    @pytest.mark.asyncio
    async def test_delete_entity(self, memory_backend):
        """Test deleting an entity."""
        entity_id = "test-3"
        data = {"name": "To Delete"}

        # Create
        await memory_backend.create(entity_id, data)
        assert await memory_backend.exists(entity_id)

        # Delete
        await memory_backend.delete(entity_id)

        # Verify deleted
        assert not await memory_backend.exists(entity_id)
        assert await memory_backend.read(entity_id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, memory_backend):
        """Test deleting a non-existent entity raises error."""
        with pytest.raises(EntityNotFoundError):
            await memory_backend.delete("nonexistent")

    @pytest.mark.asyncio
    async def test_exists(self, memory_backend):
        """Test checking entity existence."""
        entity_id = "test-4"

        # Should not exist initially
        assert not await memory_backend.exists(entity_id)

        # Create entity
        await memory_backend.create(entity_id, {"name": "Test"})

        # Should exist now
        assert await memory_backend.exists(entity_id)


# Query Tests
class TestInMemoryQuery:
    """Test query operations with in-memory backend."""

    @pytest.mark.asyncio
    async def test_query_all(self, memory_backend):
        """Test querying all entities."""
        # Create multiple entities
        for i in range(5):
            await memory_backend.create(f"entity-{i}", {"index": i, "name": f"Entity {i}"})

        # Query all
        results = await memory_backend.query()
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_with_limit(self, memory_backend):
        """Test query pagination with limit."""
        # Create multiple entities
        for i in range(10):
            await memory_backend.create(f"entity-{i}", {"index": i})

        # Query with limit
        results = await memory_backend.query(limit=5)
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_with_offset(self, memory_backend):
        """Test query pagination with offset."""
        # Create multiple entities
        for i in range(10):
            await memory_backend.create(f"entity-{i}", {"index": i})

        # Query with offset
        results = await memory_backend.query(limit=5, offset=5)
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_with_filters(self, memory_backend):
        """Test query with filters."""
        # Create entities with different statuses
        await memory_backend.create("user-1", {"name": "Alice", "status": "active"})
        await memory_backend.create("user-2", {"name": "Bob", "status": "inactive"})
        await memory_backend.create("user-3", {"name": "Charlie", "status": "active"})

        # Query active users
        results = await memory_backend.query(filters={"status": "active"})
        assert len(results) == 2

        # Verify correct users returned
        names = {r["name"] for r in results}
        assert names == {"Alice", "Charlie"}

    @pytest.mark.asyncio
    async def test_count(self, memory_backend):
        """Test counting entities."""
        # Create multiple entities
        for i in range(7):
            await memory_backend.create(f"entity-{i}", {"index": i})

        # Count all
        count = await memory_backend.count()
        assert count == 7

    @pytest.mark.asyncio
    async def test_count_with_filters(self, memory_backend):
        """Test counting with filters."""
        # Create entities
        await memory_backend.create("user-1", {"status": "active"})
        await memory_backend.create("user-2", {"status": "inactive"})
        await memory_backend.create("user-3", {"status": "active"})

        # Count active users
        count = await memory_backend.count(filters={"status": "active"})
        assert count == 2

    @pytest.mark.asyncio
    async def test_count_empty(self, memory_backend):
        """Test counting with no entities."""
        count = await memory_backend.count()
        assert count == 0


# Transaction Tests
class TestInMemoryTransactions:
    """Test transaction support with in-memory backend."""

    @pytest.mark.asyncio
    async def test_transaction_commit(self, memory_backend):
        """Test successful transaction commit."""
        async with memory_backend.transaction():
            await memory_backend.create("tx-1", {"name": "Transaction 1"})
            await memory_backend.create("tx-2", {"name": "Transaction 2"})

        # Verify both entities were created
        assert await memory_backend.exists("tx-1")
        assert await memory_backend.exists("tx-2")

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, memory_backend):
        """Test transaction rollback on error."""
        try:
            async with memory_backend.transaction():
                await memory_backend.create("tx-3", {"name": "Transaction 3"})
                # Force an error
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify entity was NOT created due to rollback
        assert not await memory_backend.exists("tx-3")

    @pytest.mark.asyncio
    async def test_transaction_update_delete(self, memory_backend):
        """Test update and delete in transaction."""
        # Create initial entity
        await memory_backend.create("tx-4", {"name": "Original", "value": 100})

        async with memory_backend.transaction():
            # Update
            await memory_backend.update("tx-4", {"name": "Updated", "value": 200})

            # Create another
            await memory_backend.create("tx-5", {"name": "New Entity"})

        # Verify changes
        entity = await memory_backend.read("tx-4")
        assert entity["name"] == "Updated"
        assert entity["value"] == 200
        assert await memory_backend.exists("tx-5")


# Factory Tests
class TestRepositoryFactory:
    """Test repository factory."""

    def test_create_memory_repository(self):
        """Test creating in-memory repository via factory."""
        repo = create_repository("memory", entity_type="test")
        assert isinstance(repo, InMemoryBackend)

    def test_create_unknown_backend(self):
        """Test creating repository with unknown backend raises error."""
        with pytest.raises(ValueError, match="Unknown backend type"):
            create_repository("unknown", entity_type="test")


# Edge Cases
class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    @pytest.mark.asyncio
    async def test_empty_data(self, memory_backend):
        """Test storing entity with empty data."""
        await memory_backend.create("empty", {})
        result = await memory_backend.read("empty")
        assert result == {}

    @pytest.mark.asyncio
    async def test_large_data(self, memory_backend):
        """Test storing entity with large data."""
        large_data = {"text": "x" * 10000, "numbers": list(range(1000))}
        await memory_backend.create("large", large_data)

        result = await memory_backend.read("large")
        assert len(result["text"]) == 10000
        assert len(result["numbers"]) == 1000

    @pytest.mark.asyncio
    async def test_special_characters_in_id(self, memory_backend):
        """Test entity IDs with special characters."""
        special_ids = [
            "id-with-dashes",
            "id_with_underscores",
            "id.with.dots",
            "id:with:colons",
        ]

        for entity_id in special_ids:
            await memory_backend.create(entity_id, {"name": entity_id})
            result = await memory_backend.read(entity_id)
            assert result["name"] == entity_id

    @pytest.mark.asyncio
    async def test_unicode_data(self, memory_backend):
        """Test storing Unicode data."""
        unicode_data = {"name": "测试", "emoji": "🔥🚀", "symbols": "αβγδ"}

        await memory_backend.create("unicode", unicode_data)
        result = await memory_backend.read("unicode")

        assert result["name"] == "测试"
        assert result["emoji"] == "🔥🚀"
        assert result["symbols"] == "αβγδ"


# Integration Tests
class TestIntegration:
    """Integration tests for real-world scenarios."""

    @pytest.mark.asyncio
    async def test_complete_crud_workflow(self, memory_backend):
        """Test complete CRUD workflow."""
        # Create
        await memory_backend.create(
            "user-1", {"name": "John Doe", "email": "john@example.com", "age": 30},
        )

        # Read
        user = await memory_backend.read("user-1")
        assert user["name"] == "John Doe"

        # Update
        await memory_backend.update(
            "user-1", {"name": "John Doe", "email": "john@example.com", "age": 31},
        )

        # Read updated
        user = await memory_backend.read("user-1")
        assert user["age"] == 31

        # Delete
        await memory_backend.delete("user-1")

        # Verify deleted
        assert not await memory_backend.exists("user-1")

    @pytest.mark.asyncio
    async def test_batch_operations_workflow(self, memory_backend):
        """Test batch operations workflow."""
        # Batch create
        users = [{"name": f"User {i}", "active": i % 2 == 0} for i in range(10)]

        for i, user_data in enumerate(users):
            await memory_backend.create(f"batch-user-{i}", user_data)

        # Query all
        all_users = await memory_backend.query(limit=20)
        assert len(all_users) == 10

        # Count
        total = await memory_backend.count()
        assert total == 10

        # Batch delete
        for i in range(10):
            await memory_backend.delete(f"batch-user-{i}")

        # Verify all deleted
        count = await memory_backend.count()
        assert count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
