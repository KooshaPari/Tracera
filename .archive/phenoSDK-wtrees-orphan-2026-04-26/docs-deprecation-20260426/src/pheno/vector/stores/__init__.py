"""Vector store adapters for multiple providers.

Implemented:
- base: VectorStore interface, Document, SearchResult, InMemoryVectorStore

Provider-specific vector stores should be implemented as needed.
See: vector-kit/docs/VECTOR_STORE_MATRIX.md for implementation guidance.
"""

from .base import Document, InMemoryVectorStore, SearchResult, VectorStore
from .faiss_store import FaissVectorStore
from .qdrant_store import QdrantVectorStore

__all__ = [
    "Document",
    "FaissVectorStore",
    # Stores
    "InMemoryVectorStore",  # For testing/development
    "QdrantVectorStore",
    "SearchResult",
    # Base types
    "VectorStore",
]
