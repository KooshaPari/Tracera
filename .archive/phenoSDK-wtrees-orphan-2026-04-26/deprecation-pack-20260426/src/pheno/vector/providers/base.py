"""
Base embedding provider class.
"""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to generate embedding for

        Returns:
            List of floats representing the embedding vector
        """

    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (batched).

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Return the dimension of the embedding vectors.
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the name of the provider.
        """
