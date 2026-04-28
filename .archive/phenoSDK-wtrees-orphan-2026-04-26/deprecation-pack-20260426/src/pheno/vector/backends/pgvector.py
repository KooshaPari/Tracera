"""
PgVector backend for vector search using PostgreSQL with pgvector extension.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from asyncpg.pool import Pool

try:
    import asyncpg
except ImportError:
    asyncpg = None

from .base import IndexBackend

logger = logging.getLogger(__name__)


class PgVectorBackend(IndexBackend):
    """
    PostgreSQL vector search backend using pgvector extension.

    Provides high-performance vector similarity search using L2 distance.
    Supports connection pooling for optimal performance (>1000 vectors/second).

    Example:
        ```python
        backend = PgVectorBackend(
            dsn="postgresql://user:pass@localhost/db",
            table_name="embeddings",
            dimension=768
        )
        await backend.initialize()

        # Index a vector
        await backend.insert(
            id="doc_1",
            vector=[0.1, 0.2, ...],
            metadata={"type": "document", "title": "Example"}
        )

        # Search similar vectors
        results = await backend.search(
            query_vector=[0.1, 0.2, ...],
            limit=10,
            similarity_threshold=0.7
        )
        ```
    """

    def __init__(
        self,
        dsn: str,
        table_name: str = "embeddings",
        dimension: int = 768,
        pool_min_size: int = 2,
        pool_max_size: int = 10,
        distance_metric: str = "l2",
    ):
        """
        Initialize PgVector backend.

        Args:
            dsn: PostgreSQL connection string (e.g., "postgresql://user:pass@localhost/db")
            table_name: Name of the table to store vectors
            dimension: Dimension of the vectors (default 768 for text-embedding-004)
            pool_min_size: Minimum number of connections in pool
            pool_max_size: Maximum number of connections in pool
            distance_metric: Distance metric to use ("l2", "cosine", "inner_product")
        """
        if asyncpg is None:
            raise ImportError(
                "asyncpg is required for PgVectorBackend. "
                "Install it with: pip install asyncpg pgvector",
            )

        self.dsn = dsn
        self.table_name = table_name
        self.dimension = dimension
        self.pool_min_size = pool_min_size
        self.pool_max_size = pool_max_size
        self.distance_metric = distance_metric
        self._pool: Pool | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize the backend: create connection pool, enable extension, create table and index.
        """
        if self._initialized:
            return

        try:
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                self.dsn,
                min_size=self.pool_min_size,
                max_size=self.pool_max_size,
                command_timeout=60,
            )

            if not self._pool:
                raise RuntimeError("Failed to create connection pool")

            async with self._pool.acquire() as conn:
                # Enable pgvector extension
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

                # Create table if not exists
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id TEXT PRIMARY KEY,
                        embedding vector({self.dimension}),
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Create vector index using HNSW for fast approximate search
                # Using L2 distance as default for compatibility
                index_name = f"{self.table_name}_embedding_idx"
                operator = self._get_distance_operator()

                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON {self.table_name}
                    USING hnsw (embedding {operator})
                    WITH (m = 16, ef_construction = 64)
                """)

                # Create metadata GIN index for filtering
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.table_name}_metadata_idx
                    ON {self.table_name}
                    USING GIN (metadata)
                """)

                logger.info(
                    f"PgVector backend initialized: table={self.table_name}, "
                    f"dimension={self.dimension}, metric={self.distance_metric}",
                )

            self._initialized = True

        except Exception as e:
            logger.exception(f"Failed to initialize PgVector backend: {e}")
            if self._pool:
                await self._pool.close()
                self._pool = None
            raise

    def _get_distance_operator(self) -> str:
        """Get the appropriate distance operator for pgvector."""
        operators = {
            "l2": "vector_l2_ops",
            "cosine": "vector_cosine_ops",
            "inner_product": "vector_ip_ops",
        }
        return operators.get(self.distance_metric, "vector_l2_ops")

    def _get_distance_function(self) -> str:
        """Get the appropriate distance function for queries."""
        functions = {
            "l2": "<->",
            "cosine": "<=>",
            "inner_product": "<#>",
        }
        return functions.get(self.distance_metric, "<->")

    async def insert(
        self, id: str, vector: list[float], metadata: dict[str, Any],
    ) -> None:
        """
        Insert or update a vector in the index.

        Args:
            id: Unique identifier for the vector
            vector: Embedding vector
            metadata: Associated metadata (must be JSON-serializable)
        """
        if not self._initialized or not self._pool:
            await self.initialize()

        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}",
            )

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    f"""
                    INSERT INTO {self.table_name} (id, embedding, metadata, updated_at)
                    VALUES ($1, $2, $3, NOW())
                    ON CONFLICT (id)
                    DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    """,
                    id,
                    vector,
                    metadata,
                )

        except Exception as e:
            logger.exception(f"Failed to insert vector {id}: {e}")
            raise

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        similarity_threshold: float = 0.7,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors using pgvector.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            filters: Optional metadata filters (JSONB queries)

        Returns:
            List of results with id, score, and metadata
        """
        if not self._initialized or not self._pool:
            await self.initialize()

        if len(query_vector) != self.dimension:
            raise ValueError(
                f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}",
            )

        try:
            async with self._pool.acquire() as conn:
                # Build the query
                distance_fn = self._get_distance_function()

                # Convert distance to similarity score (1 - normalized_distance)
                # For L2: score = 1 / (1 + distance)
                # For cosine: score = 1 - distance (already normalized)
                if self.distance_metric == "l2":
                    score_expr = f"1.0 / (1.0 + (embedding {distance_fn} $1))"
                elif self.distance_metric == "cosine":
                    score_expr = f"1.0 - (embedding {distance_fn} $1)"
                else:  # inner_product
                    score_expr = f"1.0 / (1.0 + ABS(embedding {distance_fn} $1))"

                # Build WHERE clause for filters
                where_clauses = []
                params = [query_vector]
                param_index = 2

                if filters:
                    for key, value in filters.items():
                        where_clauses.append(f"metadata->>{key!r} = ${param_index}")
                        params.append(str(value))
                        param_index += 1

                # Add similarity threshold filter
                where_clauses.append(f"{score_expr} >= ${param_index}")
                params.append(similarity_threshold)

                where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"

                query = f"""
                    SELECT
                        id,
                        {score_expr} as score,
                        metadata,
                        embedding {distance_fn} $1 as distance
                    FROM {self.table_name}
                    WHERE {where_clause}
                    ORDER BY embedding {distance_fn} $1
                    LIMIT {limit}
                """

                rows = await conn.fetch(query, *params)

                results = []
                for row in rows:
                    results.append({
                        "id": row["id"],
                        "score": float(row["score"]),
                        "metadata": dict(row["metadata"]),
                        "distance": float(row["distance"]),
                    })

                return results

        except Exception as e:
            logger.exception(f"Search failed: {e}")
            raise

    async def delete(self, id: str) -> bool:
        """
        Delete a vector from the index.

        Args:
            id: Vector identifier

        Returns:
            True if deleted, False if not found
        """
        if not self._initialized or not self._pool:
            await self.initialize()

        try:
            async with self._pool.acquire() as conn:
                result = await conn.execute(
                    f"DELETE FROM {self.table_name} WHERE id = $1",
                    id,
                )
                # Result format is "DELETE N" where N is number of rows
                return result.split()[-1] != "0"

        except Exception as e:
            logger.exception(f"Failed to delete vector {id}: {e}")
            raise

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """
        Count vectors in the index.

        Args:
            filters: Optional metadata filters

        Returns:
            Number of vectors matching filters
        """
        if not self._initialized or not self._pool:
            await self.initialize()

        try:
            async with self._pool.acquire() as conn:
                if not filters:
                    result = await conn.fetchval(
                        f"SELECT COUNT(*) FROM {self.table_name}",
                    )
                else:
                    where_clauses = []
                    params = []
                    for i, (key, value) in enumerate(filters.items(), 1):
                        where_clauses.append(f"metadata->>{key!r} = ${i}")
                        params.append(str(value))

                    where_clause = " AND ".join(where_clauses)
                    query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"
                    result = await conn.fetchval(query, *params)

                return int(result) if result else 0

        except Exception as e:
            logger.exception(f"Failed to count vectors: {e}")
            raise

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._initialized = False
            logger.info("PgVector backend connection pool closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
