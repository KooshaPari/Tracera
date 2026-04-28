"""
Comprehensive tests for PgVector backend.
"""

import asyncio
import os
import time
from collections.abc import AsyncGenerator

import pytest

# Skip tests if pgvector dependencies are not available
pytest.importorskip("asyncpg")
pytest.importorskip("pgvector")

from pheno.vector.backends.pgvector import PgVectorBackend

# Test DSN - use environment variable or skip if not available
TEST_DSN = os.environ.get("PGVECTOR_TEST_DSN")
if not TEST_DSN:
    pytest.skip("PGVECTOR_TEST_DSN not set, skipping pgvector tests", allow_module_level=True)


@pytest.fixture
async def backend() -> AsyncGenerator[PgVectorBackend, None]:
    """Create a test pgvector backend instance."""
    backend = PgVectorBackend(
        dsn=TEST_DSN,
        table_name="test_embeddings",
        dimension=384,  # Smaller dimension for testing
        pool_min_size=1,
        pool_max_size=5,
        distance_metric="l2",
    )

    try:
        await backend.initialize()
        yield backend
    finally:
        # Cleanup: drop test table
        if backend._pool:
            async with backend._pool.acquire() as conn:
                await conn.execute("DROP TABLE IF EXISTS test_embeddings CASCADE")
        await backend.close()


@pytest.mark.asyncio
class TestPgVectorBackendBasics:
    """Test basic operations of PgVector backend."""

    async def test_initialization(self, backend: PgVectorBackend):
        """Test backend initialization."""
        assert backend._initialized
        assert backend._pool is not None
        assert backend.dimension == 384
        assert backend.table_name == "test_embeddings"

    async def test_insert_single_vector(self, backend: PgVectorBackend):
        """Test inserting a single vector."""
        vector = [0.1] * 384
        metadata = {"type": "test", "name": "vector1"}

        await backend.insert(id="test_1", vector=vector, metadata=metadata)

        # Verify count
        count = await backend.count()
        assert count == 1

    async def test_insert_duplicate_updates(self, backend: PgVectorBackend):
        """Test that inserting duplicate ID updates the vector."""
        vector1 = [0.1] * 384
        vector2 = [0.2] * 384

        await backend.insert(id="test_dup", vector=vector1, metadata={"version": 1})
        await backend.insert(id="test_dup", vector=vector2, metadata={"version": 2})

        # Should still have only 1 record
        count = await backend.count()
        assert count == 1

    async def test_insert_wrong_dimension(self, backend: PgVectorBackend):
        """Test that wrong dimension raises error."""
        vector = [0.1] * 100  # Wrong dimension

        with pytest.raises(ValueError, match="dimension mismatch"):
            await backend.insert(id="test_bad", vector=vector, metadata={})

    async def test_delete_existing(self, backend: PgVectorBackend):
        """Test deleting an existing vector."""
        vector = [0.1] * 384
        await backend.insert(id="test_delete", vector=vector, metadata={})

        result = await backend.delete("test_delete")
        assert result is True

        count = await backend.count()
        assert count == 0

    async def test_delete_non_existing(self, backend: PgVectorBackend):
        """Test deleting a non-existing vector."""
        result = await backend.delete("non_existing_id")
        assert result is False

    async def test_count_empty(self, backend: PgVectorBackend):
        """Test counting when no vectors exist."""
        count = await backend.count()
        assert count == 0

    async def test_count_with_vectors(self, backend: PgVectorBackend):
        """Test counting vectors."""
        vectors = [[0.1 * i] * 384 for i in range(5)]

        for i, vector in enumerate(vectors):
            await backend.insert(id=f"test_{i}", vector=vector, metadata={"index": i})

        count = await backend.count()
        assert count == 5


@pytest.mark.asyncio
class TestPgVectorSearch:
    """Test search functionality."""

    async def test_search_basic(self, backend: PgVectorBackend):
        """Test basic similarity search."""
        # Insert some vectors
        vectors = [
            ([0.1] * 384, {"type": "a", "value": 1}),
            ([0.2] * 384, {"type": "a", "value": 2}),
            ([0.9] * 384, {"type": "b", "value": 3}),
        ]

        for i, (vector, metadata) in enumerate(vectors):
            await backend.insert(id=f"vec_{i}", vector=vector, metadata=metadata)

        # Search with a query similar to first vector
        query = [0.15] * 384
        results = await backend.search(query_vector=query, limit=2)

        assert len(results) <= 2
        assert all("id" in r for r in results)
        assert all("score" in r for r in results)
        assert all("metadata" in r for r in results)

        # Results should be ordered by similarity
        if len(results) > 1:
            assert results[0]["score"] >= results[1]["score"]

    async def test_search_with_filters(self, backend: PgVectorBackend):
        """Test search with metadata filters."""
        # Insert vectors with different metadata
        for i in range(5):
            vector = [0.1 * i] * 384
            metadata = {"type": "a" if i < 3 else "b", "index": i}
            await backend.insert(id=f"vec_{i}", vector=vector, metadata=metadata)

        # Search with filter for type "a"
        query = [0.1] * 384
        results = await backend.search(
            query_vector=query, limit=10, filters={"type": "a"},
        )

        assert len(results) <= 3
        assert all(r["metadata"]["type"] == "a" for r in results)

    async def test_search_similarity_threshold(self, backend: PgVectorBackend):
        """Test search with similarity threshold."""
        # Insert vectors
        vectors = [
            [0.1] * 384,
            [0.5] * 384,
            [0.9] * 384,
        ]

        for i, vector in enumerate(vectors):
            await backend.insert(id=f"vec_{i}", vector=vector, metadata={"index": i})

        # Search with high similarity threshold
        query = [0.1] * 384
        results = await backend.search(
            query_vector=query, limit=10, similarity_threshold=0.9,
        )

        # Should only get very similar vectors
        assert all(r["score"] >= 0.9 for r in results)

    async def test_search_limit(self, backend: PgVectorBackend):
        """Test search result limit."""
        # Insert 10 vectors
        for i in range(10):
            vector = [0.1 * i] * 384
            await backend.insert(id=f"vec_{i}", vector=vector, metadata={"index": i})

        # Search with limit=3
        query = [0.1] * 384
        results = await backend.search(query_vector=query, limit=3)

        assert len(results) <= 3

    async def test_search_empty_index(self, backend: PgVectorBackend):
        """Test search on empty index."""
        query = [0.1] * 384
        results = await backend.search(query_vector=query, limit=10)

        assert len(results) == 0


@pytest.mark.asyncio
class TestPgVectorPerformance:
    """Test performance requirements."""

    async def test_bulk_insert_performance(self, backend: PgVectorBackend):
        """Test that we can insert >1000 vectors/second."""
        num_vectors = 1000
        vectors = [[0.1 * (i % 100)] * 384 for i in range(num_vectors)]

        start_time = time.time()

        # Insert vectors in batches (async)
        tasks = []
        for i, vector in enumerate(vectors):
            task = backend.insert(
                id=f"perf_{i}", vector=vector, metadata={"batch": i // 100},
            )
            tasks.append(task)

            # Process in batches of 100 to avoid overwhelming
            if len(tasks) >= 100:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:
            await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        rate = num_vectors / elapsed

        print(f"\nInsert performance: {rate:.0f} vectors/second")
        assert rate > 1000, f"Insert rate {rate:.0f} < 1000 vectors/second"

    async def test_search_performance(self, backend: PgVectorBackend):
        """Test search performance with indexed data."""
        # Insert 1000 vectors
        for i in range(1000):
            vector = [0.1 * (i % 100)] * 384
            await backend.insert(id=f"search_{i}", vector=vector, metadata={"index": i})

        # Perform multiple searches and measure time
        query = [0.5] * 384
        num_searches = 100

        start_time = time.time()
        for _ in range(num_searches):
            await backend.search(query_vector=query, limit=10)

        elapsed = time.time() - start_time
        rate = num_searches / elapsed

        print(f"\nSearch performance: {rate:.0f} searches/second")
        # Should be able to do many searches per second with HNSW index
        assert rate > 10, f"Search rate {rate:.0f} < 10 searches/second"


@pytest.mark.asyncio
class TestPgVectorDistanceMetrics:
    """Test different distance metrics."""

    async def test_cosine_distance(self):
        """Test cosine distance metric."""
        backend = PgVectorBackend(
            dsn=TEST_DSN,
            table_name="test_cosine",
            dimension=384,
            distance_metric="cosine",
        )

        try:
            await backend.initialize()

            # Insert vectors
            vector1 = [1.0] + [0.0] * 383
            vector2 = [0.0] + [1.0] + [0.0] * 382

            await backend.insert(id="v1", vector=vector1, metadata={"name": "x-axis"})
            await backend.insert(id="v2", vector=vector2, metadata={"name": "y-axis"})

            # Search
            results = await backend.search(query_vector=vector1, limit=2)
            assert len(results) == 2

        finally:
            if backend._pool:
                async with backend._pool.acquire() as conn:
                    await conn.execute("DROP TABLE IF EXISTS test_cosine CASCADE")
            await backend.close()

    async def test_inner_product_distance(self):
        """Test inner product distance metric."""
        backend = PgVectorBackend(
            dsn=TEST_DSN,
            table_name="test_ip",
            dimension=384,
            distance_metric="inner_product",
        )

        try:
            await backend.initialize()

            vector = [0.1] * 384
            await backend.insert(id="v1", vector=vector, metadata={})

            results = await backend.search(query_vector=vector, limit=1)
            assert len(results) == 1

        finally:
            if backend._pool:
                async with backend._pool.acquire() as conn:
                    await conn.execute("DROP TABLE IF EXISTS test_ip CASCADE")
            await backend.close()


@pytest.mark.asyncio
class TestPgVectorContextManager:
    """Test async context manager."""

    async def test_context_manager(self):
        """Test using backend as async context manager."""
        async with PgVectorBackend(
            dsn=TEST_DSN, table_name="test_context", dimension=384,
        ) as backend:
            assert backend._initialized
            vector = [0.1] * 384
            await backend.insert(id="test", vector=vector, metadata={})
            count = await backend.count()
            assert count == 1

        # Should be closed after context
        assert backend._pool is None
        assert not backend._initialized


@pytest.mark.asyncio
class TestPgVectorErrorHandling:
    """Test error handling."""

    async def test_search_before_init(self):
        """Test that operations work even before explicit initialization."""
        backend = PgVectorBackend(
            dsn=TEST_DSN, table_name="test_auto_init", dimension=384,
        )

        try:
            # Should auto-initialize
            vector = [0.1] * 384
            await backend.insert(id="test", vector=vector, metadata={})

            results = await backend.search(query_vector=vector, limit=1)
            assert len(results) == 1

        finally:
            if backend._pool:
                async with backend._pool.acquire() as conn:
                    await conn.execute("DROP TABLE IF EXISTS test_auto_init CASCADE")
            await backend.close()

    async def test_invalid_dsn(self):
        """Test handling of invalid DSN."""
        backend = PgVectorBackend(
            dsn="postgresql://invalid:invalid@localhost:9999/invalid",
            table_name="test_invalid",
            dimension=384,
        )

        with pytest.raises(Exception):
            await backend.initialize()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
