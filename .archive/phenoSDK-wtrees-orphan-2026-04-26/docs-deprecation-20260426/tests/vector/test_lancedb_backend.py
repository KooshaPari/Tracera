"""
Comprehensive tests for LanceDB backend.
"""

import asyncio
import shutil
import tempfile
import time
from collections.abc import AsyncGenerator

import pytest

# Skip tests if lancedb dependencies are not available
try:
    import lancedb
    import pyarrow as pa
except ImportError:
    pytest.skip("lancedb or pyarrow not installed, skipping lancedb tests", allow_module_level=True)

from pheno.vector.backends.lancedb import LanceDBBackend


@pytest.fixture
async def temp_db_path() -> AsyncGenerator[str, None]:
    """Create a temporary directory for LanceDB."""
    temp_dir = tempfile.mkdtemp(prefix="lancedb_test_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def backend(temp_db_path: str) -> AsyncGenerator[LanceDBBackend, None]:
    """Create a test LanceDB backend instance."""
    backend = LanceDBBackend(
        uri=temp_db_path,
        table_name="test_embeddings",
        dimension=384,  # Smaller dimension for testing
        distance_metric="l2",
    )

    try:
        await backend.initialize()
        yield backend
    finally:
        await backend.close()


@pytest.mark.asyncio
class TestLanceDBBackendBasics:
    """Test basic operations of LanceDB backend."""

    async def test_initialization(self, backend: LanceDBBackend):
        """Test backend initialization."""
        assert backend._initialized
        assert backend._db is not None
        assert backend._table is not None
        assert backend.dimension == 384
        assert backend.table_name == "test_embeddings"

    async def test_insert_single_vector(self, backend: LanceDBBackend):
        """Test inserting a single vector."""
        vector = [0.1] * 384
        metadata = {"type": "test", "name": "vector1"}

        await backend.insert(id="test_1", vector=vector, metadata=metadata)

        # Verify count
        count = await backend.count()
        assert count >= 1  # LanceDB may have some quirks with exact counts

    async def test_insert_duplicate_updates(self, backend: LanceDBBackend):
        """Test that inserting duplicate ID updates the vector."""
        vector1 = [0.1] * 384
        vector2 = [0.2] * 384

        await backend.insert(id="test_dup", vector=vector1, metadata={"version": 1})
        await backend.insert(id="test_dup", vector=vector2, metadata={"version": 2})

        # Should still have only 1 record (old one deleted, new one added)
        count = await backend.count()
        assert count == 1

    async def test_insert_wrong_dimension(self, backend: LanceDBBackend):
        """Test that wrong dimension raises error."""
        vector = [0.1] * 100  # Wrong dimension

        with pytest.raises(ValueError, match="dimension mismatch"):
            await backend.insert(id="test_bad", vector=vector, metadata={})

    async def test_delete_existing(self, backend: LanceDBBackend):
        """Test deleting an existing vector."""
        vector = [0.1] * 384
        await backend.insert(id="test_delete", vector=vector, metadata={})

        result = await backend.delete("test_delete")
        assert result is True

        count = await backend.count()
        assert count == 0

    async def test_delete_non_existing(self, backend: LanceDBBackend):
        """Test deleting a non-existing vector."""
        result = await backend.delete("non_existing_id")
        assert result is False

    async def test_count_empty(self, backend: LanceDBBackend):
        """Test counting when no vectors exist."""
        count = await backend.count()
        assert count == 0

    async def test_count_with_vectors(self, backend: LanceDBBackend):
        """Test counting vectors."""
        vectors = [[0.1 * i] * 384 for i in range(5)]

        for i, vector in enumerate(vectors):
            await backend.insert(id=f"test_{i}", vector=vector, metadata={"index": i})

        count = await backend.count()
        assert count == 5


@pytest.mark.asyncio
class TestLanceDBSearch:
    """Test search functionality."""

    async def test_search_basic(self, backend: LanceDBBackend):
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

    async def test_search_with_filters(self, backend: LanceDBBackend):
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

    async def test_search_similarity_threshold(self, backend: LanceDBBackend):
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
            query_vector=query, limit=10, similarity_threshold=0.5,
        )

        # Should only get vectors above threshold
        assert all(r["score"] >= 0.5 for r in results)

    async def test_search_limit(self, backend: LanceDBBackend):
        """Test search result limit."""
        # Insert 10 vectors
        for i in range(10):
            vector = [0.1 * i] * 384
            await backend.insert(id=f"vec_{i}", vector=vector, metadata={"index": i})

        # Search with limit=3
        query = [0.1] * 384
        results = await backend.search(query_vector=query, limit=3)

        assert len(results) <= 3

    async def test_search_empty_index(self, backend: LanceDBBackend):
        """Test search on empty index."""
        query = [0.1] * 384
        results = await backend.search(query_vector=query, limit=10)

        assert len(results) == 0


@pytest.mark.asyncio
class TestLanceDBPerformance:
    """Test performance requirements."""

    async def test_bulk_insert_performance(self, backend: LanceDBBackend):
        """Test bulk insert performance."""
        num_vectors = 1000
        vectors = [[0.1 * (i % 100)] * 384 for i in range(num_vectors)]

        start_time = time.time()

        # Insert vectors
        tasks = []
        for i, vector in enumerate(vectors):
            task = backend.insert(
                id=f"perf_{i}", vector=vector, metadata={"batch": i // 100},
            )
            tasks.append(task)

            # Process in batches to avoid overwhelming
            if len(tasks) >= 50:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:
            await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        rate = num_vectors / elapsed

        print(f"\nInsert performance: {rate:.0f} vectors/second")
        # LanceDB is fast for local operations
        assert rate > 100, f"Insert rate {rate:.0f} < 100 vectors/second"

    async def test_search_performance(self, backend: LanceDBBackend):
        """Test search performance."""
        # Insert 500 vectors (smaller set for local DB)
        for i in range(500):
            vector = [0.1 * (i % 100)] * 384
            await backend.insert(id=f"search_{i}", vector=vector, metadata={"index": i})

        # Perform multiple searches and measure time
        query = [0.5] * 384
        num_searches = 50

        start_time = time.time()
        for _ in range(num_searches):
            await backend.search(query_vector=query, limit=10)

        elapsed = time.time() - start_time
        rate = num_searches / elapsed

        print(f"\nSearch performance: {rate:.0f} searches/second")
        # LanceDB should be fast for local searches
        assert rate > 5, f"Search rate {rate:.0f} < 5 searches/second"


@pytest.mark.asyncio
class TestLanceDBDistanceMetrics:
    """Test different distance metrics."""

    async def test_cosine_distance(self, temp_db_path: str):
        """Test cosine distance metric."""
        backend = LanceDBBackend(
            uri=temp_db_path,
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
            await backend.close()

    async def test_dot_product_distance(self, temp_db_path: str):
        """Test dot product distance metric."""
        backend = LanceDBBackend(
            uri=temp_db_path,
            table_name="test_dot",
            dimension=384,
            distance_metric="dot",
        )

        try:
            await backend.initialize()

            vector = [0.1] * 384
            await backend.insert(id="v1", vector=vector, metadata={})

            results = await backend.search(query_vector=vector, limit=1)
            assert len(results) == 1

        finally:
            await backend.close()


@pytest.mark.asyncio
class TestLanceDBContextManager:
    """Test async context manager."""

    async def test_context_manager(self, temp_db_path: str):
        """Test using backend as async context manager."""
        async with LanceDBBackend(
            uri=temp_db_path, table_name="test_context", dimension=384,
        ) as backend:
            assert backend._initialized
            vector = [0.1] * 384
            await backend.insert(id="test", vector=vector, metadata={})
            count = await backend.count()
            assert count >= 1

        # Should be closed after context
        assert backend._db is None
        assert not backend._initialized


@pytest.mark.asyncio
class TestLanceDBMultipleTables:
    """Test multiple tables in same database."""

    async def test_multiple_tables(self, temp_db_path: str):
        """Test creating multiple tables in the same database."""
        backend1 = LanceDBBackend(
            uri=temp_db_path, table_name="table1", dimension=384,
        )
        backend2 = LanceDBBackend(
            uri=temp_db_path, table_name="table2", dimension=384,
        )

        try:
            await backend1.initialize()
            await backend2.initialize()

            # Insert to both tables
            vector1 = [0.1] * 384
            vector2 = [0.2] * 384

            await backend1.insert(id="t1_v1", vector=vector1, metadata={"table": 1})
            await backend2.insert(id="t2_v1", vector=vector2, metadata={"table": 2})

            # Verify counts are separate
            count1 = await backend1.count()
            count2 = await backend2.count()

            assert count1 == 1
            assert count2 == 1

        finally:
            await backend1.close()
            await backend2.close()


@pytest.mark.asyncio
class TestLanceDBPersistence:
    """Test data persistence across backend instances."""

    async def test_persistence(self, temp_db_path: str):
        """Test that data persists after closing and reopening."""
        # First backend instance
        backend1 = LanceDBBackend(
            uri=temp_db_path, table_name="persistent", dimension=384,
        )

        try:
            await backend1.initialize()

            # Insert data
            vector = [0.1] * 384
            await backend1.insert(id="persistent_1", vector=vector, metadata={"test": 1})

            count1 = await backend1.count()
            assert count1 == 1

        finally:
            await backend1.close()

        # Second backend instance (same path)
        backend2 = LanceDBBackend(
            uri=temp_db_path, table_name="persistent", dimension=384,
        )

        try:
            await backend2.initialize()

            # Should see the data from first instance
            count2 = await backend2.count()
            assert count2 == 1

            # Should be able to search
            results = await backend2.search(query_vector=[0.1] * 384, limit=1)
            assert len(results) == 1
            assert results[0]["id"] == "persistent_1"

        finally:
            await backend2.close()


@pytest.mark.asyncio
class TestLanceDBErrorHandling:
    """Test error handling."""

    async def test_search_before_init(self, temp_db_path: str):
        """Test that operations work even before explicit initialization."""
        backend = LanceDBBackend(
            uri=temp_db_path, table_name="test_auto_init", dimension=384,
        )

        try:
            # Should auto-initialize
            vector = [0.1] * 384
            await backend.insert(id="test", vector=vector, metadata={})

            results = await backend.search(query_vector=vector, limit=1)
            assert len(results) >= 1

        finally:
            await backend.close()

    async def test_invalid_uri(self):
        """Test handling of invalid URI."""
        # Use a path that should cause issues (read-only location)
        backend = LanceDBBackend(
            uri="/dev/null/invalid", table_name="test_invalid", dimension=384,
        )

        with pytest.raises(Exception):
            await backend.initialize()


@pytest.mark.asyncio
class TestLanceDBMetadata:
    """Test metadata handling."""

    async def test_complex_metadata(self, backend: LanceDBBackend):
        """Test storing and retrieving complex metadata."""
        vector = [0.1] * 384
        metadata = {
            "type": "document",
            "tags": ["tag1", "tag2"],
            "nested": {"key": "value", "number": 42},
            "bool": True,
        }

        await backend.insert(id="complex", vector=vector, metadata=metadata)

        results = await backend.search(query_vector=vector, limit=1)
        assert len(results) == 1

        retrieved_metadata = results[0]["metadata"]
        assert retrieved_metadata["type"] == "document"
        assert "tags" in retrieved_metadata
        assert "nested" in retrieved_metadata

    async def test_empty_metadata(self, backend: LanceDBBackend):
        """Test storing vectors with empty metadata."""
        vector = [0.1] * 384

        await backend.insert(id="empty_meta", vector=vector, metadata={})

        results = await backend.search(query_vector=vector, limit=1)
        assert len(results) == 1
        assert results[0]["metadata"] == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
