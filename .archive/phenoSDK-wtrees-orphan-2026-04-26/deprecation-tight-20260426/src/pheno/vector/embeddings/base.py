"""
Base embedding provider interface.
"""

import random
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Base embedding provider.

    Example:
        provider = OpenAIEmbeddings(api_key="...")

        vectors = await provider.embed_documents([
            "Hello world",
            "Python programming"
        ])
    """

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """
        Embed single text.
        """

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents.
        """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Get embedding dimension.
        """


class InMemoryEmbeddings(EmbeddingProvider):
    """Simple in-memory embeddings for testing.

    Generates random vectors for demonstration.
    """

    def __init__(self, dim: int = 384):
        self._dim = dim
        self._cache = {}

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate random embedding for text.
        """
        if text not in self._cache:
            self._cache[text] = [random.random() for _ in range(self._dim)]
        return self._cache[text]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents.
        """
        return [await self.embed_text(text) for text in texts]

    @property
    def dimension(self) -> int:
        """
        Get embedding dimension.
        """
        return self._dim
