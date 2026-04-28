#!/usr/bin/env python3
"""Hot Cache Usage Examples.

Demonstrates in-memory TTL-based caching for high-performance query optimization.
"""

import asyncio
import time

from pheno.caching import CachedQueryMixin, QueryCache


# Example 1: Basic Query Cache Usage
def example_basic_usage():
    """
    Basic hot cache usage for query optimization.
    """
    print("\n=== Example 1: Basic Query Cache ===\n")

    # Create cache with 30 second TTL
    cache = QueryCache(ttl=30, max_size=1000)

    # Generate cache key
    key = cache.generate_key("select", {"table": "users", "id": 123})

    # First query - cache miss
    print("1. First query (cache miss):")
    result = cache.get(key)
    if result is None:
        print("   Cache miss - querying database...")
        result = {"id": 123, "name": "John Doe", "email": "john@example.com"}
        cache.set(key, result, metadata={"table": "users"})
        print(f"   Result: {result}")

    # Second query - cache hit (10x faster!)
    print("\n2. Second query (cache hit):")
    result = cache.get(key)
    if result is not None:
        print(f"   Cache hit! Result: {result}")

    # Get statistics
    stats = cache.get_stats()
    print(f"\n3. Cache Statistics:")
    print(f"   Hit rate: {stats['hit_rate']:.2%}")
    print(f"   Hits: {stats['hits']}, Misses: {stats['misses']}")
    print(f"   Size: {stats['size']}/{stats['max_size']}")


# Example 2: Automatic Write Invalidation
def example_write_invalidation():
    """
    Demonstrate automatic cache invalidation on writes.
    """
    print("\n=== Example 2: Write Invalidation ===\n")

    cache = QueryCache(ttl=30)

    # Cache some user data
    user_key = cache.generate_key("select", {"table": "users", "id": 123})
    cache.set(user_key, {"id": 123, "name": "John"}, metadata={"table": "users"})

    # Cache another user
    user2_key = cache.generate_key("select", {"table": "users", "id": 456})
    cache.set(user2_key, {"id": 456, "name": "Jane"}, metadata={"table": "users"})

    print("1. Cached 2 users")
    print(f"   Cache size: {cache.get_stats()['size']}")

    # Simulate write to users table
    print("\n2. Writing to users table...")
    cache.invalidate_by_table("users")

    print("\n3. After invalidation:")
    print(f"   Cache size: {cache.get_stats()['size']}")
    print("   All users table cache entries cleared!")


# Example 3: Database Adapter Integration
class MockDatabaseAdapter(CachedQueryMixin):
    """
    Mock database adapter with hot cache integration.
    """

    def __init__(self):
        self._init_cache(ttl=30, max_size=1000)
        self._query_count = 0

    async def select(self, table: str, filters: dict):
        """
        Select with automatic caching.
        """
        # Generate cache key
        key = self._query_cache.generate_key("select", {"table": table, "filters": filters})

        # Check cache
        cached = self._query_cache.get(key)
        if cached is not None:
            print(f"   [CACHE HIT] {table} query")
            return cached

        # Simulate database query
        print(f"   [CACHE MISS] Querying {table}...")
        await asyncio.sleep(0.1)  # Simulate network latency
        self._query_count += 1

        result = {"table": table, "filters": filters, "query_num": self._query_count}

        # Cache result
        self._query_cache.set(key, result, metadata={"table": table})
        return result

    async def insert(self, table: str, data: dict):
        """
        Insert with automatic cache invalidation.
        """
        # Simulate database insert
        print(f"   Inserting into {table}...")
        await asyncio.sleep(0.05)

        # Invalidate cache for this table
        self._query_cache.invalidate_by_table(table)
        print(f"   Cache invalidated for {table}")


async def example_database_integration():
    """
    Demonstrate database adapter with hot cache.
    """
    print("\n=== Example 3: Database Adapter Integration ===\n")

    db = MockDatabaseAdapter()

    # First query - cache miss
    print("1. First query:")
    start = time.time()
    result1 = await db.select("users", {"id": 123})
    elapsed1 = time.time() - start
    print(f"   Result: {result1['query_num']}")
    print(f"   Time: {elapsed1*1000:.1f}ms")

    # Second query - cache hit (10x faster!)
    print("\n2. Second query (same parameters):")
    start = time.time()
    result2 = await db.select("users", {"id": 123})
    elapsed2 = time.time() - start
    print(f"   Result: {result2['query_num']}")
    print(f"   Time: {elapsed2*1000:.1f}ms")
    print(f"   Speedup: {elapsed1/elapsed2:.1f}x faster!")

    # Insert - invalidates cache
    print("\n3. Insert operation:")
    await db.insert("users", {"id": 789, "name": "New User"})

    # Query after insert - cache miss
    print("\n4. Query after insert (cache invalidated):")
    start = time.time()
    result3 = await db.select("users", {"id": 123})
    elapsed3 = time.time() - start
    print(f"   Result: {result3['query_num']}")
    print(f"   Time: {elapsed3*1000:.1f}ms")


# Example 4: TTL Expiration
async def example_ttl_expiration():
    """
    Demonstrate TTL-based expiration.
    """
    print("\n=== Example 4: TTL Expiration ===\n")

    # Create cache with very short TTL for demo
    cache = QueryCache(ttl=2)  # 2 second TTL

    key = cache.generate_key("select", {"table": "users", "id": 123})

    # Cache a value
    print("1. Caching value with 2 second TTL...")
    cache.set(key, {"name": "John"})
    print(f"   Cached: {cache.get(key)}")

    # Retrieve immediately - cache hit
    print("\n2. Retrieving immediately:")
    result = cache.get(key)
    print(f"   Result: {result} (cache hit)")

    # Wait for expiration
    print("\n3. Waiting 3 seconds for TTL expiration...")
    await asyncio.sleep(3)

    # Retrieve after expiration - cache miss
    print("\n4. Retrieving after TTL:")
    result = cache.get(key)
    print(f"   Result: {result} (expired)")


# Example 5: Multi-Table Caching Strategy
async def example_multi_table_strategy():
    """
    Demonstrate caching strategy for multiple tables.
    """
    print("\n=== Example 5: Multi-Table Caching Strategy ===\n")

    db = MockDatabaseAdapter()

    # Query different tables
    print("1. Caching queries from multiple tables:")
    await db.select("users", {"id": 123})
    await db.select("projects", {"org_id": 456})
    await db.select("documents", {"project_id": 789})

    stats = db._query_cache.get_stats()
    print(f"\n   Cache size: {stats['size']} entries")

    # Write to one table
    print("\n2. Writing to projects table:")
    await db.insert("projects", {"id": 999, "name": "New Project"})

    # Only projects cache is invalidated
    print("\n3. Querying after write:")
    await db.select("users", {"id": 123})  # Cache hit
    await db.select("projects", {"org_id": 456})  # Cache miss (invalidated)

    stats = db._query_cache.get_stats()
    print(f"\n   Final statistics:")
    print(f"   Hit rate: {stats['hit_rate']:.2%}")
    print(f"   Cache size: {stats['size']} entries")


# Main execution
async def main():
    """
    Run all examples.
    """
    print("=" * 70)
    print("HOT CACHE EXAMPLES - In-Memory TTL-Based Caching")
    print("=" * 70)

    example_basic_usage()
    example_write_invalidation()
    await example_database_integration()
    await example_ttl_expiration()
    await example_multi_table_strategy()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
