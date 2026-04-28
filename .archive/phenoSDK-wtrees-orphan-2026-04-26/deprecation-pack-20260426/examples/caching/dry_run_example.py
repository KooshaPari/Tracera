#!/usr/bin/env python3
"""Dry-Run System Usage Examples.

Demonstrates non-destructive operation mode for safe testing and previews.
"""

import asyncio
import logging

from pheno.caching import (
    DryRunContext,
    DryRunMixin,
    dry_run_aware,
    dry_run_method,
    dry_run_skip,
    is_dry_run,
    set_dry_run,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# Example 1: Basic Dry-Run Decorator
@dry_run_aware(operation_name="delete_user", return_value={"deleted": False})
async def delete_user(user_id: str):
    """
    Delete a user (dry-run aware).
    """
    print(f"   Deleting user {user_id} from database...")
    await asyncio.sleep(0.1)
    return {"deleted": True, "user_id": user_id}


async def example_basic_decorator():
    """
    Demonstrate basic dry-run decorator.
    """
    print("\n=== Example 1: Basic Dry-Run Decorator ===\n")

    # Normal execution
    print("1. Normal execution:")
    set_dry_run(False)
    result = await delete_user("user_123")
    print(f"   Result: {result}")

    # Dry-run execution
    print("\n2. Dry-run execution:")
    set_dry_run(True, logger)
    result = await delete_user("user_456")
    print(f"   Result: {result}")
    print("   (Operation was logged but not executed)")


# Example 2: Skip Decorator
@dry_run_skip(operation_name="send_email")
async def send_email(to: str, subject: str, body: str):
    """
    Send an email (skipped in dry-run).
    """
    print(f"   Sending email to {to}...")
    print(f"   Subject: {subject}")
    await asyncio.sleep(0.1)
    return {"sent": True}


async def example_skip_decorator():
    """
    Demonstrate skip decorator.
    """
    print("\n=== Example 2: Skip Decorator ===\n")

    # Normal execution
    print("1. Normal execution:")
    set_dry_run(False)
    result = await send_email("user@example.com", "Welcome", "Hello!")
    print(f"   Result: {result}")

    # Dry-run execution (skipped)
    print("\n2. Dry-run execution (skipped):")
    set_dry_run(True, logger)
    result = await send_email("user@example.com", "Welcome", "Hello!")
    print(f"   Result: {result}")


# Example 3: Context Manager
async def example_context_manager():
    """
    Demonstrate dry-run context manager.
    """
    print("\n=== Example 3: Dry-Run Context Manager ===\n")

    # Normal execution
    print("1. Outside dry-run context:")
    set_dry_run(False)
    await delete_user("user_001")

    # Temporary dry-run
    print("\n2. Inside dry-run context:")
    with DryRunContext(enabled=True, logger=logger):
        await delete_user("user_002")
        await send_email("test@example.com", "Test", "Body")

    # Back to normal
    print("\n3. After dry-run context:")
    await delete_user("user_003")


# Example 4: Class with Dry-Run Support
class UserService(DryRunMixin):
    """
    User service with dry-run support.
    """

    def __init__(self, dry_run: bool = False):
        self._init_dry_run(dry_run, logger)

    @dry_run_method(return_value={"created": False, "id": "dry-run-id"})
    async def create_user(self, name: str, email: str):
        """
        Create a new user.
        """
        print(f"   Creating user: {name} ({email})")
        await asyncio.sleep(0.1)
        return {"created": True, "id": "user_123", "name": name}

    @dry_run_method(return_value={"updated": False})
    async def update_user(self, user_id: str, data: dict):
        """
        Update user data.
        """
        print(f"   Updating user {user_id}: {data}")
        await asyncio.sleep(0.1)
        return {"updated": True, "user_id": user_id}

    async def get_user(self, user_id: str):
        """
        Get user (not affected by dry-run).
        """
        print(f"   Fetching user {user_id}")
        return {"id": user_id, "name": "John Doe"}


async def example_class_with_dry_run():
    """
    Demonstrate class with dry-run support.
    """
    print("\n=== Example 4: Class with Dry-Run Support ===\n")

    # Normal mode
    print("1. Normal mode:")
    service = UserService(dry_run=False)
    result = await service.create_user("John", "john@example.com")
    print(f"   Result: {result}")

    # Dry-run mode
    print("\n2. Dry-run mode:")
    service = UserService(dry_run=True)
    result = await service.create_user("Jane", "jane@example.com")
    print(f"   Result: {result}")

    # Read operations work normally
    print("\n3. Read operations (always execute):")
    result = await service.get_user("user_123")
    print(f"   Result: {result}")


# Example 5: Database Migration Preview
class DatabaseMigration(DryRunMixin):
    """
    Database migration with dry-run support.
    """

    def __init__(self, dry_run: bool = False):
        self._init_dry_run(dry_run, logger)
        self.operations = []

    @dry_run_method()
    async def create_table(self, table_name: str, schema: dict):
        """
        Create a table.
        """
        print(f"   CREATE TABLE {table_name}")
        self.operations.append(f"CREATE TABLE {table_name}")
        await asyncio.sleep(0.05)

    @dry_run_method()
    async def add_column(self, table: str, column: str, type: str):
        """
        Add a column.
        """
        print(f"   ALTER TABLE {table} ADD COLUMN {column} {type}")
        self.operations.append(f"ALTER TABLE {table} ADD COLUMN {column}")
        await asyncio.sleep(0.05)

    @dry_run_method()
    async def create_index(self, table: str, columns: list[str]):
        """
        Create an index.
        """
        cols = ", ".join(columns)
        print(f"   CREATE INDEX ON {table}({cols})")
        self.operations.append(f"CREATE INDEX ON {table}")
        await asyncio.sleep(0.05)

    async def run_migration(self):
        """
        Run full migration.
        """
        print("\n   Running migration:")
        await self.create_table("users", {"id": "uuid", "name": "text"})
        await self.add_column("users", "email", "text")
        await self.create_index("users", ["email"])
        print(f"\n   Total operations: {len(self.operations)}")


async def example_migration_preview():
    """
    Demonstrate migration preview with dry-run.
    """
    print("\n=== Example 5: Database Migration Preview ===\n")

    # Dry-run preview
    print("1. Migration preview (dry-run):")
    migration = DatabaseMigration(dry_run=True)
    await migration.run_migration()
    print("   (No actual changes made)")

    # Actual migration
    print("\n2. Actual migration:")
    response = input("   Apply migration? (y/n): ")
    if response.lower() == "y":
        migration = DatabaseMigration(dry_run=False)
        await migration.run_migration()
        print("   Migration applied!")
    else:
        print("   Migration cancelled")


# Example 6: Batch Operations with Dry-Run
class BatchProcessor(DryRunMixin):
    """
    Batch processor with dry-run support.
    """

    def __init__(self, dry_run: bool = False):
        self._init_dry_run(dry_run, logger)
        self.processed = 0
        self.skipped = 0

    @dry_run_method(return_value={"processed": False})
    async def process_item(self, item: dict):
        """
        Process a single item.
        """
        await asyncio.sleep(0.01)
        return {"processed": True, "item_id": item["id"]}

    async def batch_process(self, items: list[dict]):
        """
        Process items in batch.
        """
        print(f"\n   Processing {len(items)} items:")
        for item in items:
            result = await self.process_item(item)
            if result["processed"]:
                self.processed += 1
            else:
                self.skipped += 1

        print(f"\n   Processed: {self.processed}")
        print(f"   Skipped: {self.skipped}")


async def example_batch_operations():
    """
    Demonstrate batch operations with dry-run.
    """
    print("\n=== Example 6: Batch Operations with Dry-Run ===\n")

    items = [{"id": i, "data": f"item_{i}"} for i in range(10)]

    # Dry-run preview
    print("1. Batch preview (dry-run):")
    processor = BatchProcessor(dry_run=True)
    await processor.batch_process(items)

    # Actual processing
    print("\n2. Actual processing:")
    processor = BatchProcessor(dry_run=False)
    await processor.batch_process(items[:3])  # Process only first 3


# Example 7: CLI with Dry-Run Flag
async def example_cli_pattern():
    """
    Demonstrate CLI pattern with --dry-run flag.
    """
    print("\n=== Example 7: CLI with Dry-Run Flag ===\n")

    # Simulate CLI arguments
    import argparse

    # Parse arguments
    parser = argparse.ArgumentParser(description="Backfill embeddings")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--limit", type=int, default=100, help="Number to process")

    # For demo, simulate --dry-run flag
    class Args:
        dry_run = True
        limit = 5

    args = Args()

    print(f"Arguments: dry_run={args.dry_run}, limit={args.limit}")

    # Initialize service with dry-run flag
    service = UserService(dry_run=args.dry_run)

    # Process operations
    print("\nProcessing:")
    for i in range(args.limit):
        await service.create_user(f"user_{i}", f"user{i}@example.com")

    if args.dry_run:
        print("\n✓ Dry-run complete - no changes made")
        print("  Run without --dry-run to apply changes")


# Main execution
async def main():
    """
    Run all examples.
    """
    print("=" * 70)
    print("DRY-RUN SYSTEM EXAMPLES - Non-Destructive Operation Mode")
    print("=" * 70)

    await example_basic_decorator()
    await example_skip_decorator()
    await example_context_manager()
    await example_class_with_dry_run()
    await example_migration_preview()
    await example_batch_operations()
    await example_cli_pattern()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
