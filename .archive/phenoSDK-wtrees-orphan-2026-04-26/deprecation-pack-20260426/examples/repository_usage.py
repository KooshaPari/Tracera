"""
Example usage of the pheno-SDK repository system.

This demonstrates how to use the repository backends for data storage.
"""

import asyncio
import tempfile
from pathlib import Path

from pheno.storage.repository import (
    EntityNotFoundError,
    SQLAlchemyBackend,
    create_repository,
)


async def example_basic_usage():
    """Basic CRUD operations example."""
    print("\n=== Basic CRUD Operations ===\n")

    # Create an in-memory repository
    repo = create_repository("memory", entity_type="users")

    # Create entities
    await repo.create("user-1", {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "age": 30,
        "active": True,
    })

    await repo.create("user-2", {
        "name": "Bob Jones",
        "email": "bob@example.com",
        "age": 25,
        "active": True,
    })

    # Read entity
    user = await repo.read("user-1")
    print(f"User 1: {user}")

    # Update entity
    await repo.update("user-1", {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "age": 31,
        "active": True,
    })

    # Check existence
    exists = await repo.exists("user-1")
    print(f"User 1 exists: {exists}")

    # Delete entity
    await repo.delete("user-2")
    print("User 2 deleted")

    # Count entities
    count = await repo.count()
    print(f"Total users: {count}")

    await repo.close()


async def example_query_operations():
    """Query and filtering example."""
    print("\n=== Query Operations ===\n")

    repo = create_repository("memory", entity_type="products")

    # Create test data
    products = [
        {"name": "Laptop", "price": 1200, "category": "electronics", "in_stock": True},
        {"name": "Mouse", "price": 25, "category": "electronics", "in_stock": True},
        {"name": "Desk", "price": 300, "category": "furniture", "in_stock": False},
        {"name": "Chair", "price": 150, "category": "furniture", "in_stock": True},
        {"name": "Monitor", "price": 400, "category": "electronics", "in_stock": True},
    ]

    for i, product in enumerate(products):
        await repo.create(f"product-{i}", product)

    # Query all products
    all_products = await repo.query(limit=10)
    print(f"Total products: {len(all_products)}")

    # Query with filters
    electronics = await repo.query(filters={"category": "electronics"})
    print(f"Electronics products: {len(electronics)}")

    # Query with pagination
    page1 = await repo.query(limit=2, offset=0)
    page2 = await repo.query(limit=2, offset=2)
    print(f"Page 1: {len(page1)} products, Page 2: {len(page2)} products")

    # Count with filters
    in_stock = await repo.count(filters={"in_stock": True})
    print(f"In-stock products: {in_stock}")

    await repo.close()


async def example_transactions():
    """Transaction support example."""
    print("\n=== Transactions ===\n")

    repo = create_repository("memory", entity_type="orders")

    # Successful transaction
    print("Creating orders in transaction...")
    async with repo.transaction():
        await repo.create("order-1", {"amount": 100, "status": "pending"})
        await repo.create("order-2", {"amount": 200, "status": "pending"})

    count = await repo.count()
    print(f"Orders created: {count}")

    # Failed transaction (rollback)
    print("Attempting transaction with error...")
    try:
        async with repo.transaction():
            await repo.create("order-3", {"amount": 300, "status": "pending"})
            raise ValueError("Payment failed")
    except ValueError:
        pass

    count = await repo.count()
    print(f"Orders after failed transaction: {count} (order-3 was rolled back)")

    await repo.close()


async def example_sqlite_backend():
    """SQLite backend example."""
    print("\n=== SQLite Backend ===\n")

    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "example.db"

        # Create SQLAlchemy backend with SQLite
        repo = SQLAlchemyBackend(
            database_url=f"sqlite+aiosqlite:///{db_path}",
            entity_type="customers",
            echo=False,  # Set to True to see SQL queries
        )

        # Create some data
        print("Creating customers in SQLite...")
        for i in range(5):
            await repo.create(f"customer-{i}", {
                "name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "tier": "gold" if i % 2 == 0 else "silver",
            })

        # Query data
        all_customers = await repo.query(limit=10)
        print(f"Total customers: {len(all_customers)}")

        gold_customers = await repo.query(filters={"tier": "gold"})
        print(f"Gold tier customers: {len(gold_customers)}")

        # Update a customer
        await repo.update("customer-0", {
            "name": "VIP Customer",
            "email": "vip@example.com",
            "tier": "platinum",
        })

        # Transaction example
        async with repo.transaction():
            await repo.create("customer-5", {
                "name": "Batch Customer 1",
                "email": "batch1@example.com",
                "tier": "silver",
            })
            await repo.create("customer-6", {
                "name": "Batch Customer 2",
                "email": "batch2@example.com",
                "tier": "silver",
            })

        final_count = await repo.count()
        print(f"Final customer count: {final_count}")

        await repo.close()


async def example_error_handling():
    """Error handling example."""
    print("\n=== Error Handling ===\n")

    repo = create_repository("memory", entity_type="items")

    # Try to update non-existent entity
    try:
        await repo.update("nonexistent", {"data": "value"})
    except EntityNotFoundError:
        print("✓ EntityNotFoundError caught for update")

    # Try to delete non-existent entity
    try:
        await repo.delete("nonexistent")
    except EntityNotFoundError:
        print("✓ EntityNotFoundError caught for delete")

    # Read non-existent entity returns None (no exception)
    result = await repo.read("nonexistent")
    print(f"✓ Read nonexistent returns: {result}")

    await repo.close()


async def example_advanced_usage():
    """Advanced usage patterns."""
    print("\n=== Advanced Usage ===\n")

    repo = create_repository("memory", entity_type="documents")

    # Store complex nested data
    await repo.create("doc-1", {
        "title": "Meeting Notes",
        "content": "Discussion about Q4 plans",
        "metadata": {
            "author": "Alice",
            "department": "Engineering",
            "tags": ["planning", "q4", "strategy"],
        },
        "attachments": [
            {"name": "slides.pdf", "size": 1024000},
            {"name": "spreadsheet.xlsx", "size": 512000},
        ],
    })

    # Retrieve and display
    doc = await repo.read("doc-1")
    print(f"Document title: {doc['title']}")
    print(f"Author: {doc['metadata']['author']}")
    print(f"Tags: {', '.join(doc['metadata']['tags'])}")
    print(f"Attachments: {len(doc['attachments'])}")

    # Store binary data (base64 encoded)
    import base64
    binary_data = b"Hello, World!"
    await repo.create("binary-1", {
        "filename": "hello.txt",
        "content": base64.b64encode(binary_data).decode("utf-8"),
    })

    # Retrieve binary data
    stored = await repo.read("binary-1")
    decoded = base64.b64decode(stored["content"])
    print(f"Decoded binary: {decoded.decode('utf-8')}")

    await repo.close()


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  Repository Backend Usage Examples")
    print("=" * 60)

    await example_basic_usage()
    await example_query_operations()
    await example_transactions()
    await example_error_handling()
    await example_advanced_usage()

    # SQLite example (requires SQLAlchemy + aiosqlite)
    try:
        await example_sqlite_backend()
    except ImportError as e:
        print("\n=== SQLite Backend ===\n")
        print("SQLite backend requires SQLAlchemy and aiosqlite:")
        print("  pip install 'sqlalchemy>=2.0.0' 'aiosqlite>=0.19.0'")
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("  All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
