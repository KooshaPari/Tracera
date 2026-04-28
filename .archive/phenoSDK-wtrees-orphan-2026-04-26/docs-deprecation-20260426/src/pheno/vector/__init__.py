"""
pheno.vector - Embeddings and vector search

Provides vector storage, embeddings, and semantic search capabilities.

Migrated from vector-kit into pheno namespace.

Features:
- In-memory vector store for development/testing
- Base interfaces for implementing providers
- Semantic search with configurable embeddings
- Document chunking and indexing

Usage:
    from pheno.vector import VectorStore, SemanticSearch, InMemoryVectorStore
    from pheno.vector import similarity_search

    # Quick similarity search
    results = await similarity_search(
        query="What is machine learning?",
        documents=["ML is...", "AI is...", "DL is..."],
        k=2
    )

    # Advanced usage
    store = InMemoryVectorStore()
    search = SemanticSearch(vector_store=store)
    await search.index_documents(documents)
    results = await search.search("query", k=5)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .embeddings.base import EmbeddingProvider, InMemoryEmbeddings
from .search.semantic import SemanticSearch
from .stores.base import Document, InMemoryVectorStore, SearchResult, VectorStore

if TYPE_CHECKING:
    from collections.abc import Sequence


def create_vector_store(backend: str = "memory", **kwargs) -> VectorStore:
    """Create a vector store by backend name.

    Currently supported: memory (default) - in-memory store for development/testing.
    Additional providers can be implemented following the base VectorStore interface.
    """
    name = (backend or "memory").strip().lower()
    if name in {"memory", "inmemory", "in-memory"}:
        return InMemoryVectorStore(**kwargs)

    # For unsupported backends, fall back to memory store
    return InMemoryVectorStore(**kwargs)


async def similarity_search(
    query: str,
    documents: Sequence[str],
    *,
    k: int = 10,
    provider: EmbeddingProvider | None = None,
    store: VectorStore | None = None,
    backend: str = "memory",
) -> list[SearchResult]:
    """One-shot similarity search over an in-memory (or provided) store.

    - Builds (or uses) a vector store
    - Indexes the given documents
    - Returns top-k similar results for the query
    """
    embedder = provider or InMemoryEmbeddings()
    vstore = store or create_vector_store(backend)
    search = SemanticSearch(embedding_provider=embedder, vector_store=vstore)
    await search.index_documents(list(documents))
    return await search.search(query, k=k)


__version__ = "0.1.0"

__all__ = [
    # Base types
    "Document",
    # Core interfaces
    "EmbeddingProvider",
    # Vector store implementations
    "InMemoryVectorStore",  # Testing/development
    "SearchResult",
    "SemanticSearch",
    "VectorStore",
    # Convenience API
    "create_vector_store",
    "similarity_search",
]
