"""
LanceDB backend for vector search - local vector database.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

try:
    import lancedb
    from lancedb.db import LanceDBConnection
    from lancedb.table import Table
except ImportError:
    lancedb = None
    LanceDBConnection = None
    Table = None

from .base import IndexBackend

logger = logging.getLogger(__name__)


class LanceDBBackend(IndexBackend):
    """
    LanceDB vector search backend for local development and testing.

    LanceDB is a fast, embedded vector database that's ideal for:
    - Local development and testing
    - Edge deployments
    - Applications requiring no external infrastructure

    Supports multiple distance metrics and provides fast similarity search
    with minimal configuration.

    Example:
        ```python
        backend = LanceDBBackend(
            uri="/path/to/lancedb",
            table_name="embeddings",
            dimension=768,
            distance_metric="l2"
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
        uri: str,
        table_name: str = "embeddings",
        dimension: int = 768,
        distance_metric: str = "l2",
    ):
        """
        Initialize LanceDB backend.

        Args:
            uri: Path to the LanceDB database (e.g., "/path/to/lancedb" or "~/lancedb")
            table_name: Name of the table to store vectors
            dimension: Dimension of the vectors (default 768 for text-embedding-004)
            distance_metric: Distance metric to use ("l2", "cosine", "dot")
        """
        if lancedb is None:
            raise ImportError(
                "LanceDB is not installed. Install it with: pip install lancedb",
            )

        self.uri = str(Path(uri).expanduser().resolve())
        self.table_name = table_name
        self.dimension = dimension
        self.distance_metric = distance_metric
        self._db: LanceDBConnection | None = None
        self._table: Table | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize the backend: connect to database and create/open table.
        """
        if self._initialized:
            return

        try:
            # LanceDB operations are synchronous, so we run them in executor
            def _init_db():
                # Connect to LanceDB
                db = lancedb.connect(self.uri)

                # Check if table exists
                existing_tables = db.table_names()

                if self.table_name in existing_tables:
                    # Open existing table
                    table = db.open_table(self.table_name)
                else:
                    # Create new table with schema
                    # Initial empty data to create table
                    import pyarrow as pa

                    schema = pa.schema([
                        pa.field("id", pa.string()),
                        pa.field("vector", pa.list_(pa.float32(), self.dimension)),
                        pa.field("metadata", pa.string()),  # JSON string
                    ])

                    table = db.create_table(
                        self.table_name,
                        schema=schema,
                        mode="overwrite",
                    )

                return db, table

            loop = asyncio.get_event_loop()
            self._db, self._table = await loop.run_in_executor(None, _init_db)

            logger.info(
                f"LanceDB backend initialized: uri={self.uri}, "
                f"table={self.table_name}, dimension={self.dimension}, "
                f"metric={self.distance_metric}",
            )

            self._initialized = True

        except Exception as e:
            logger.exception(f"Failed to initialize LanceDB backend: {e}")
            raise

    def _serialize_metadata(self, metadata: dict[str, Any]) -> str:
        """Serialize metadata to JSON string."""
        import json
        return json.dumps(metadata)

    def _deserialize_metadata(self, metadata_str: str) -> dict[str, Any]:
        """Deserialize metadata from JSON string."""
        import json
        try:
            return json.loads(metadata_str)
        except (json.JSONDecodeError, TypeError):
            return {}

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
        if not self._initialized or not self._table:
            await self.initialize()

        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}",
            )

        try:
            def _insert():
                import pyarrow as pa

                # Delete existing record if it exists
                try:
                    self._table.delete(f"id = '{id}'")
                except Exception:
                    pass  # Record doesn't exist, that's fine

                # Insert new record
                data = pa.table({
                    "id": [id],
                    "vector": [vector],
                    "metadata": [self._serialize_metadata(metadata)],
                })

                self._table.add(data)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _insert)

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
        Search for similar vectors using LanceDB.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            filters: Optional metadata filters

        Returns:
            List of results with id, score, and metadata
        """
        if not self._initialized or not self._table:
            await self.initialize()

        if len(query_vector) != self.dimension:
            raise ValueError(
                f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}",
            )

        try:
            def _search():
                # Perform vector search
                query = self._table.search(query_vector)

                # Set distance metric
                if self.distance_metric == "cosine":
                    query = query.metric("cosine")
                elif self.distance_metric == "dot":
                    query = query.metric("dot")
                else:  # l2 is default
                    query = query.metric("l2")

                # Execute search
                results = query.limit(limit * 2).to_list()  # Get more for filtering

                # Convert results and apply filters
                filtered_results = []
                for result in results:
                    # Calculate similarity score from distance
                    distance = result.get("_distance", 0.0)

                    if self.distance_metric == "l2":
                        # For L2: score = 1 / (1 + distance)
                        score = 1.0 / (1.0 + distance)
                    elif self.distance_metric == "cosine":
                        # For cosine: distance is already 0-2, convert to 0-1 similarity
                        score = 1.0 - (distance / 2.0)
                    else:  # dot product
                        # For dot product: higher is better, normalize
                        score = 1.0 / (1.0 + abs(distance))

                    # Apply similarity threshold
                    if score < similarity_threshold:
                        continue

                    # Parse metadata
                    metadata = self._deserialize_metadata(result.get("metadata", "{}"))

                    # Apply metadata filters
                    if filters:
                        match = all(
                            str(metadata.get(key)) == str(value)
                            for key, value in filters.items()
                        )
                        if not match:
                            continue

                    filtered_results.append({
                        "id": result["id"],
                        "score": float(score),
                        "metadata": metadata,
                        "distance": float(distance),
                    })

                    if len(filtered_results) >= limit:
                        break

                return filtered_results

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _search)

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
        if not self._initialized or not self._table:
            await self.initialize()

        try:
            def _delete():
                try:
                    # Check if record exists first
                    results = self._table.search().where(f"id = '{id}'").limit(1).to_list()
                    if not results:
                        return False

                    # Delete the record
                    self._table.delete(f"id = '{id}'")
                    return True
                except Exception:
                    return False

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _delete)

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
        if not self._initialized or not self._table:
            await self.initialize()

        try:
            def _count():
                # Get all records (LanceDB doesn't have a direct count method)
                results = self._table.search().limit(100000).to_list()

                if not filters:
                    return len(results)

                # Apply filters
                count = 0
                for result in results:
                    metadata = self._deserialize_metadata(result.get("metadata", "{}"))
                    match = all(
                        str(metadata.get(key)) == str(value)
                        for key, value in filters.items()
                    )
                    if match:
                        count += 1

                return count

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _count)

        except Exception as e:
            logger.exception(f"Failed to count vectors: {e}")
            raise

    async def close(self) -> None:
        """Close the database connection."""
        # LanceDB doesn't require explicit closing
        self._db = None
        self._table = None
        self._initialized = False
        logger.info("LanceDB backend closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
