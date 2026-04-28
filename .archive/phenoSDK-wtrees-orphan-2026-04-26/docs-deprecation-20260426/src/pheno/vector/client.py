"""
Vector-Kit unified client interface.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from pheno.vector.providers.factory import get_embedding_service
from pheno.vector.search.enhanced import EnhancedVectorSearchService

if TYPE_CHECKING:
    from pheno.vector.search.types import SearchResponse

logger = logging.getLogger(__name__)


class VectorClient:
    """Unified client for vector search with progressive embedding.

    Provides a simple interface to:
    - Generate embeddings across multiple providers (Vertex AI, OpenAI, local)
    - Search across multiple backends (pgvector, Supabase, FAISS, LanceDB)
    - Progressive embedding (on-demand generation for missing records)
    - Hybrid search (semantic + keyword)

    Example:
        ```python
        from vector_kit import VectorClient

        client = VectorClient(
            provider="vertex",
            backend_dsn="postgres://...",
        )

        # Progressive semantic search
        results = await client.search.semantic(
            query="machine learning frameworks",
            limit=20,
            ensure_embeddings=True,  # Generate missing embeddings
        )
        ```
    """

    def __init__(
        self,
        provider: str | None = None,
        backend_dsn: str | None = None,
        supabase_client=None,
        backend_type: str | None = None,
        backend_uri: str | None = None,
        **provider_kwargs,
    ):
        """Initialize Vector Client.

        Args:
            provider: Embedding provider ("vertex", "openai", "local", or None for auto-detect)
            backend_dsn: Database connection string for pgvector backend
            supabase_client: Supabase client instance (alternative to backend_dsn)
            backend_type: Type of backend ("pgvector", "lancedb", "supabase")
            backend_uri: URI for backend (LanceDB path, etc.)
            **provider_kwargs: Additional provider-specific configuration
        """
        self.provider = provider
        self.backend_dsn = backend_dsn
        self.supabase_client = supabase_client
        self.backend_type = backend_type
        self.backend_uri = backend_uri
        self.provider_kwargs = provider_kwargs

        # Initialize embedding service
        if provider:
            self.embedding_service = get_embedding_service(
                provider_type=provider, **provider_kwargs,
            )
        else:
            self.embedding_service = get_embedding_service()  # Auto-detect

        # Initialize search service based on backend type
        if supabase_client:
            self.search = EnhancedVectorSearchService(
                supabase_client=supabase_client, embedding_service=self.embedding_service,
            )
        elif backend_type == "pgvector" and backend_dsn:
            # Note: EnhancedVectorSearchService is Supabase-specific
            # For pgvector/lancedb, use the backend directly
            raise NotImplementedError(
                "Direct pgvector backend integration with EnhancedVectorSearchService coming soon. "
                "Use IndexBackend.pgvector() for direct backend access.",
            )
        elif backend_type == "lancedb" and backend_uri:
            raise NotImplementedError(
                "Direct lancedb backend integration with EnhancedVectorSearchService coming soon. "
                "Use IndexBackend.lancedb() for direct backend access.",
            )
        else:
            raise ValueError(
                "Must provide either supabase_client, or backend_type with backend_dsn/backend_uri. "
                "For direct backend access, use IndexBackend.pgvector() or IndexBackend.lancedb().",
            )

    async def semantic_search(
        self,
        query: str,
        similarity_threshold: float = 0.7,
        limit: int = 10,
        entity_types: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        ensure_embeddings: bool = True,
    ) -> SearchResponse:
        """Perform semantic search with automatic embedding generation.

        Args:
            query: Search query text
            similarity_threshold: Minimum similarity score (0-1)
            limit: Maximum results to return
            entity_types: Specific entity types to search
            filters: Additional filters to apply
            ensure_embeddings: If True, generate embeddings for missing records

        Returns:
            SearchResponse with ranked results
        """
        return await self.search.semantic_search(
            query=query,
            similarity_threshold=similarity_threshold,
            limit=limit,
            entity_types=entity_types,
            filters=filters,
            ensure_embeddings=ensure_embeddings,
        )

    async def hybrid_search(
        self,
        query: str,
        similarity_threshold: float = 0.7,
        limit: int = 10,
        keyword_weight: float = 0.3,
        entity_types: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        ensure_embeddings: bool = True,
    ) -> SearchResponse:
        """Perform hybrid search (semantic + keyword).

        Args:
            query: Search query text
            similarity_threshold: Minimum similarity score (0-1)
            limit: Maximum results to return
            keyword_weight: Weight for keyword results (0-1, default 0.3)
            entity_types: Specific entity types to search
            filters: Additional filters to apply
            ensure_embeddings: If True, generate embeddings for missing records

        Returns:
            SearchResponse with ranked results
        """
        return await self.search.hybrid_search(
            query=query,
            similarity_threshold=similarity_threshold,
            limit=limit,
            keyword_weight=keyword_weight,
            entity_types=entity_types,
            filters=filters,
            ensure_embeddings=ensure_embeddings,
        )

    async def keyword_search(
        self,
        query: str,
        limit: int = 10,
        entity_types: list[str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> SearchResponse:
        """Perform keyword-only search (no embeddings needed).

        Args:
            query: Search query text
            limit: Maximum results to return
            entity_types: Specific entity types to search
            filters: Additional filters to apply

        Returns:
            SearchResponse with ranked results
        """
        return await self.search.keyword_search(
            query=query, limit=limit, entity_types=entity_types, filters=filters,
        )

    async def similarity_search_by_content(
        self,
        content: str,
        entity_type: str,
        similarity_threshold: float = 0.8,
        limit: int = 5,
        exclude_id: str | None = None,
        ensure_embeddings: bool = True,
    ) -> SearchResponse:
        """Find similar content by comparing embeddings.

        Args:
            content: Content to find similar matches for
            entity_type: Entity type to search within
            similarity_threshold: Minimum similarity score (0-1)
            limit: Maximum results to return
            exclude_id: Optional ID to exclude from results
            ensure_embeddings: If True, generate missing embeddings

        Returns:
            SearchResponse with similar content
        """
        return await self.search.similarity_search_by_content(
            content=content,
            entity_type=entity_type,
            similarity_threshold=similarity_threshold,
            limit=limit,
            exclude_id=exclude_id,
            ensure_embeddings=ensure_embeddings,
        )

    async def comprehensive_search(
        self,
        query: str,
        similarity_threshold: float = 0.7,
        limit: int = 20,
        entity_types: list[str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, SearchResponse]:
        """Perform comprehensive search using all methods.

        Returns:
            Dict with results from each search method:
            {
                "semantic": SearchResponse,
                "keyword": SearchResponse,
                "hybrid": SearchResponse
            }
        """
        return await self.search.comprehensive_search(
            query=query,
            similarity_threshold=similarity_threshold,
            limit=limit,
            entity_types=entity_types,
            filters=filters,
        )


class EmbeddingProvider:
    """
    Factory for creating embedding providers.
    """

    @staticmethod
    def vertex(project: str, location: str = "us-central1", **kwargs):
        """
        Create Vertex AI embedding provider.
        """
        from pheno.vector.providers.vertex import VertexEmbeddingService

        return VertexEmbeddingService(project=project, location=location, **kwargs)

    @staticmethod
    def openai(api_key: str | None = None, **kwargs):
        """
        Create OpenAI embedding provider.
        """
        # Implementation coming soon
        raise NotImplementedError("OpenAI provider coming soon")

    @staticmethod
    def local(model_name: str = "all-MiniLM-L6-v2", **kwargs):
        """
        Create local embedding provider using sentence-transformers.
        """
        from pheno.vector.providers.sentence_transformers import (
            SentenceTransformersEmbeddingProvider,
        )

        return SentenceTransformersEmbeddingProvider(model_name=model_name, **kwargs)


class IndexBackend:
    """
    Factory for creating index backends.
    """

    @staticmethod
    def pgvector(dsn: str, **kwargs):
        """
        Create pgvector backend.

        Args:
            dsn: PostgreSQL connection string (e.g., "postgresql://user:pass@localhost/db")
            **kwargs: Additional configuration (table_name, dimension, pool_min_size, pool_max_size, distance_metric)
        """
        from pheno.vector.backends.pgvector import PgVectorBackend

        return PgVectorBackend(dsn=dsn, **kwargs)

    @staticmethod
    def supabase(client, **kwargs):
        """
        Create Supabase backend.
        """
        return {"supabase_client": client, **kwargs}

    @staticmethod
    def faiss(_index_path: str | None = None, **kwargs):
        """
        Create FAISS backend.
        """
        # Implementation coming soon
        raise NotImplementedError("FAISS backend coming soon")

    @staticmethod
    def lancedb(uri: str, **kwargs):
        """
        Create LanceDB backend.

        Args:
            uri: Path to LanceDB database (e.g., "/path/to/lancedb" or "~/lancedb")
            **kwargs: Additional configuration (table_name, dimension, distance_metric)
        """
        from pheno.vector.backends.lancedb import LanceDBBackend

        return LanceDBBackend(uri=uri, **kwargs)
