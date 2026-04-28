"""
Basic test to verify the repository backend implementation works.

This is a standalone verification test.
"""

import asyncio

from pheno.storage.repository import (
    EntityNotFoundError,
    InMemoryBackend,
    create_repository,
)


async def test_in_memory_basic_crud():
    """Test basic CRUD operations with in-memory backend."""
    backend = InMemoryBackend(entity_type="test")

    # Create
    await backend.create("user-1", {"name": "Alice", "age": 30})

    # Read
    user = await backend.read("user-1")
    assert user is not None
    assert user["name"] == "Alice"
    assert user["age"] == 30

    # Update
    await backend.update("user-1", {"name": "Alice", "age": 31})
    user = await backend.read("user-1")
    assert user["age"] == 31

    # Count
    count = await backend.count()
    assert count == 1

    # Exists
    assert await backend.exists("user-1")
    assert not await backend.exists("user-2")

    # Delete
    await backend.delete("user-1")
    assert not await backend.exists("user-1")

    await backend.close()
    print("✓ Basic CRUD operations passed")


async def test_in_memory_query():
    """Test query operations with in-memory backend."""
    backend = InMemoryBackend(entity_type="test")

    # Create test data
    for i in range(10):
        await backend.create(f"user-{i}", {"name": f"User {i}", "active": i % 2 == 0})

    # Query all
    results = await backend.query(limit=20)
    assert len(results) == 10

    # Query with filter
    active_users = await backend.query(filters={"active": True})
    assert len(active_users) == 5

    # Query with limit and offset
    page = await backend.query(limit=3, offset=2)
    assert len(page) == 3

    # Count
    total = await backend.count()
    assert total == 10

    active_count = await backend.count(filters={"active": True})
    assert active_count == 5

    await backend.close()
    print("✓ Query operations passed")


async def test_in_memory_transactions():
    """Test transaction support."""
    backend = InMemoryBackend(entity_type="test")

    # Successful transaction
    async with backend.transaction():
        await backend.create("tx-1", {"name": "Transaction 1"})
        await backend.create("tx-2", {"name": "Transaction 2"})

    assert await backend.exists("tx-1")
    assert await backend.exists("tx-2")

    # Rollback transaction
    try:
        async with backend.transaction():
            await backend.create("tx-3", {"name": "Transaction 3"})
            raise ValueError("Test error")
    except ValueError:
        pass

    # Entity should not exist due to rollback
    assert not await backend.exists("tx-3")

    await backend.close()
    print("✓ Transaction support passed")


async def test_error_handling():
    """Test error handling."""
    backend = InMemoryBackend(entity_type="test")

    # Update non-existent
    try:
        await backend.update("nonexistent", {"name": "Test"})
        assert False, "Should have raised EntityNotFoundError"
    except EntityNotFoundError:
        pass

    # Delete non-existent
    try:
        await backend.delete("nonexistent")
        assert False, "Should have raised EntityNotFoundError"
    except EntityNotFoundError:
        pass

    await backend.close()
    print("✓ Error handling passed")


async def test_factory():
    """Test repository factory."""
    repo = create_repository("memory", entity_type="test")
    assert isinstance(repo, InMemoryBackend)

    await repo.create("test-1", {"name": "Test"})
    result = await repo.read("test-1")
    assert result["name"] == "Test"

    await repo.close()
    print("✓ Repository factory passed")


async def run_all_tests():
    """Run all tests."""
    print("\nRunning repository backend tests...\n")

    await test_in_memory_basic_crud()
    await test_in_memory_query()
    await test_in_memory_transactions()
    await test_error_handling()
    await test_factory()

    print("\n✅ All tests passed!\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
