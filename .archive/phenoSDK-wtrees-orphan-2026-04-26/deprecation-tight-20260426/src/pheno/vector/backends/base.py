"""
Base index backend class.
"""

from abc import ABC, abstractmethod
from typing import Any


class IndexBackend(ABC):
    """
    Abstract base class for vector index backends.
    """

    @abstractmethod
    async def insert(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """Insert a vector into the index.

        Args:
            id: Unique identifier
            vector: Embedding vector
            metadata: Associated metadata
        """

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        similarity_threshold: float = 0.7,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            filters: Optional metadata filters

        Returns:
            List of results with id, score, and metadata
        """

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a vector from the index.

        Args:
            id: Vector identifier

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count vectors in the index.

        Args:
            filters: Optional metadata filters

        Returns:
            Number of vectors matching filters
        """
