#!/usr/bin/env python3
"""Cold Cache Usage Examples.

Demonstrates persistent disk-based caching for expensive computations that survive
process restarts.
"""

import asyncio
import random

from pheno.caching import DiskCache, EmbeddingCache, TestDataCache


# Example 1: Basic Disk Cache Usage
def example_basic_disk_cache():
    """
    Basic persistent disk cache usage.
    """
    print("\n=== Example 1: Basic Disk Cache ===\n")

    # Create cache (survives restarts)
    cache = DiskCache(namespace="demo", cache_dir="~/.cache/pheno", ttl=3600)  # 1 hour

    key = "user_123"

    # Check cache
    print("1. Checking cache...")
    cached = cache.get(key)
    if cached is None:
        print("   Cache miss - computing result...")
        result = {"id": 123, "name": "John Doe", "computed": "expensive_value"}
        cache.set(key, result)
        print(f"   Cached: {result}")
    else:
        print(f"   Cache hit! {cached}")

    # Retrieve again (instant!)
    print("\n2. Retrieving again (from disk):")
    result = cache.get(key)
    print(f"   Result: {result}")

    # Get statistics
    stats = cache.get_stats()
    print(f"\n3. Cache Statistics:")
    print(f"   Namespace: {stats['namespace']}")
    print(f"   Entries: {stats['entries']}")
    print(f"   Size: {stats['size_mb']} MB")
    print(f"   Location: {stats['cache_dir']}")


# Example 2: Embedding Cache
def example_embedding_cache():
    """
    Demonstrate embedding cache for ML vectors.
    """
    print("\n=== Example 2: Embedding Cache ===\n")

    # Create embedding cache
    cache = EmbeddingCache(ttl=86400)  # 24 hour TTL

    entity_id = "document_456"

    # Simulate expensive embedding generation
    print("1. Checking for cached embedding...")
    cached = cache.get_embedding(entity_id)

    if cached is None:
        print("   Cache miss - generating embedding (expensive!)...")
        # Simulate embedding generation
        embedding = [random.random() for _ in range(768)]
        cache.set_embedding(
            entity_id=entity_id,
            embedding=embedding,
            model="text-embedding-3-small",
            dimensions=768,
            entity_type="document",
        )
        print(f"   Generated and cached 768-dimensional embedding")
    else:
        print(f"   Cache hit! Retrieved embedding:")
        print(f"   Model: {cached['model']}")
        print(f"   Dimensions: {cached['dimensions']}")
        print(f"   Entity type: {cached.get('entity_type', 'unknown')}")

    # Retrieve again (instant, survives restarts!)
    print("\n2. Retrieving cached embedding:")
    result = cache.get_embedding(entity_id)
    print(f"   Found: {result is not None}")
    print(f"   Dimensions: {len(result['embedding'])}")

    stats = cache.get_stats()
    print(f"\n3. Cache Statistics:")
    print(f"   Entries: {stats['entries']}")
    print(f"   Size: {stats['size_mb']} MB")


# Example 3: Test Data Cache
def example_test_data_cache():
    """
    Demonstrate test data and UUID caching.
    """
    print("\n=== Example 3: Test Data Cache ===\n")

    # Create test data cache (never expires)
    cache = TestDataCache()

    # Cache test UUIDs
    print("1. Caching test UUIDs:")
    test_users = {
        "test_user_admin": "550e8400-e29b-41d4-a716-446655440000",
        "test_user_member": "550e8400-e29b-41d4-a716-446655440001",
        "test_org": "550e8400-e29b-41d4-a716-446655440002",
    }

    for key, uuid in test_users.items():
        cache.set_uuid(key, uuid)
        print(f"   Cached {key}: {uuid}")

    # Retrieve in tests (consistent across runs!)
    print("\n2. Retrieving test UUIDs:")
    admin_id = cache.get_uuid("test_user_admin")
    member_id = cache.get_uuid("test_user_member")
    org_id = cache.get_uuid("test_org")

    print(f"   Admin: {admin_id}")
    print(f"   Member: {member_id}")
    print(f"   Org: {org_id}")

    print("\n   These UUIDs persist across test runs!")


# Example 4: Multi-Process Embedding Cache
async def example_multi_process_cache():
    """
    Demonstrate cache persistence across process restarts.
    """
    print("\n=== Example 4: Multi-Process Cache ===\n")

    cache = EmbeddingCache()

    entities = [f"doc_{i}" for i in range(5)]

    print("1. Caching embeddings for 5 documents:")
    for entity_id in entities:
        # Check if already cached
        cached = cache.get_embedding(entity_id)
        if cached is None:
            # Generate new embedding
            embedding = [random.random() for _ in range(768)]
            cache.set_embedding(
                entity_id, embedding, model="text-embedding-3-small", dimensions=768
            )
            print(f"   Generated embedding for {entity_id}")
        else:
            print(f"   Found cached embedding for {entity_id}")

    stats = cache.get_stats()
    print(f"\n2. Cache Statistics:")
    print(f"   Total entries: {stats['entries']}")
    print(f"   Total size: {stats['size_mb']} MB")

    print("\n   NOTE: These embeddings will persist even if you restart!")
    print("   Run this script again to see cache hits for all documents.")


# Example 5: Cache Cleanup and Maintenance
def example_cache_maintenance():
    """
    Demonstrate cache cleanup operations.
    """
    print("\n=== Example 5: Cache Maintenance ===\n")

    # Create cache with short TTL for demo
    cache = DiskCache(namespace="maintenance_demo", ttl=1)

    # Add some entries
    print("1. Adding 3 cache entries:")
    for i in range(3):
        cache.set(f"key_{i}", {"value": i})
    print(f"   Cache size: {cache.get_stats()['entries']}")

    # Wait for expiration
    print("\n2. Waiting for TTL expiration...")
    import time

    time.sleep(2)

    # Cleanup expired entries
    print("\n3. Cleaning up expired entries:")
    removed = cache.cleanup_expired()
    print(f"   Removed {removed} expired entries")
    print(f"   Cache size: {cache.get_stats()['entries']}")

    # Clear entire cache
    print("\n4. Clearing entire cache:")
    cache.clear()
    print(f"   Cache size: {cache.get_stats()['entries']}")


# Example 6: Multi-Namespace Strategy
def example_multi_namespace():
    """
    Demonstrate using multiple cache namespaces.
    """
    print("\n=== Example 6: Multi-Namespace Strategy ===\n")

    # Create separate caches for different purposes
    embedding_cache = EmbeddingCache()
    test_cache = TestDataCache()
    config_cache = DiskCache(namespace="config", ttl=None)

    print("1. Creating multiple cache namespaces:")
    print(f"   Embeddings: {embedding_cache.namespace}")
    print(f"   Test data: {test_cache.namespace}")
    print(f"   Config: {config_cache.namespace}")

    # Cache different types of data
    embedding_cache.set_embedding("doc_1", [0.1] * 768, "text-embedding-3-small", 768)
    test_cache.set_uuid("test_user", "550e8400-e29b-41d4-a716-446655440000")
    config_cache.set("app_version", "1.0.0")

    print("\n2. Each namespace is isolated:")
    print(f"   Embeddings: {embedding_cache.get_stats()['entries']} entries")
    print(f"   Test data: {test_cache.get_stats()['entries']} entries")
    print(f"   Config: {config_cache.get_stats()['entries']} entries")

    print("\n   Clearing one namespace doesn't affect others!")


# Example 7: Real-World Embedding Pipeline
async def example_embedding_pipeline():
    """
    Demonstrate real-world embedding cache usage.
    """
    print("\n=== Example 7: Real-World Embedding Pipeline ===\n")

    cache = EmbeddingCache(ttl=86400)  # 24 hour TTL

    async def get_embedding(entity_id: str, text: str) -> list[float]:
        """
        Get embedding with caching.
        """
        # Check cache first
        cached = cache.get_embedding(entity_id)
        if cached is not None:
            return cached["embedding"]

        # Generate embedding (expensive!)
        print(f"   Generating embedding for {entity_id}...")
        await asyncio.sleep(0.1)  # Simulate API call
        embedding = [random.random() for _ in range(768)]

        # Cache for future use
        cache.set_embedding(entity_id, embedding, model="text-embedding-3-small", dimensions=768)

        return embedding

    # Process multiple documents
    documents = [
        ("doc_1", "Sample text 1"),
        ("doc_2", "Sample text 2"),
        ("doc_3", "Sample text 3"),
        ("doc_1", "Sample text 1"),  # Duplicate - will hit cache
    ]

    print("1. Processing documents with caching:")
    for doc_id, text in documents:
        embedding = await get_embedding(doc_id, text)
        print(f"   {doc_id}: {len(embedding)} dimensions")

    stats = cache.get_stats()
    print(f"\n2. Cache Statistics:")
    print(f"   Entries: {stats['entries']}")
    print(f"   Size: {stats['size_mb']} MB")
    print("\n   Notice: doc_1 was only generated once (cached for second use)!")


# Main execution
async def main():
    """
    Run all examples.
    """
    print("=" * 70)
    print("COLD CACHE EXAMPLES - Persistent Disk-Based Caching")
    print("=" * 70)

    example_basic_disk_cache()
    example_embedding_cache()
    example_test_data_cache()
    await example_multi_process_cache()
    example_cache_maintenance()
    example_multi_namespace()
    await example_embedding_pipeline()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nNOTE: All cached data persists at ~/.cache/pheno/")
    print("Run this script again to see cache hits!")


if __name__ == "__main__":
    asyncio.run(main())
