"""
Base vector store interface.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from math import sqrt


@dataclass
class Document:
    """
    Document with embedding.
    """

    id: str
    text: str
    vector: list[float]
    metadata: dict | None = None


@dataclass
class SearchResult:
    """
    Search result.
    """

    document: Document
    score: float


class VectorStore(ABC):
    """Base vector store interface.

    Example:
        store = FAISSVectorStore(dimension=384)

        await store.add_documents([
            Document(id="1", text="Hello", vector=vec1),
            Document(id="2", text="World", vector=vec2)
        ])

        results = await store.search(query_vector, k=5)
    """

    @abstractmethod
    async def add_document(self, document: Document):
        """
        Add single document.
        """

    @abstractmethod
    async def add_documents(self, documents: list[Document]):
        """
        Add multiple documents.
        """

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        k: int = 10,
        filter_dict: dict | None = None,
    ) -> list[SearchResult]:
        """
        Search for similar vectors.
        """

    @abstractmethod
    async def delete(self, document_id: str):
        """
        Delete document by ID.
        """


class InMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store.
    """

    def __init__(self):
        self._documents: list[Document] = []

    async def add_document(self, document: Document):
        """
        Add document.
        """
        self._documents.append(document)

    async def add_documents(self, documents: list[Document]):
        """
        Add multiple documents.
        """
        self._documents.extend(documents)

    async def search(
        self,
        query_vector: list[float],
        k: int = 10,
        filter_dict: dict | None = None,
    ) -> list[SearchResult]:
        """
        Search using cosine similarity.
        """
        results: list[SearchResult] = []
        for doc in self._documents:
            score = _cosine_similarity(query_vector, doc.vector)
            results.append(SearchResult(document=doc, score=float(score)))

        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:k]

    async def delete(self, document_id: str):
        """
        Delete document.
        """
        self._documents = [d for d in self._documents if d.id != document_id]


def _cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    vec_a = list(a)
    vec_b = list(b)
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(x * y for x, y in zip(vec_a, vec_b, strict=False))
    norm_a = sqrt(sum(x * x for x in vec_a))
    norm_b = sqrt(sum(y * y for y in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
