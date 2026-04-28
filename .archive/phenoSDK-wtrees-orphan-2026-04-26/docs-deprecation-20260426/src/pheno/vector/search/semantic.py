"""
Semantic search combining embeddings and vector stores.
"""

from pheno.vector.embeddings.base import EmbeddingProvider
from pheno.vector.stores.base import Document, SearchResult, VectorStore


class SemanticSearch:
    """Semantic search engine.

    Combines embedding provider and vector store for semantic search.

    Example:
        search = SemanticSearch(
            embedding_provider=OpenAIEmbeddings(),
            vector_store=FAISSVectorStore()
        )

        # Index documents
        await search.index_documents([
            "Python is a programming language",
            "JavaScript is used for web development"
        ])

        # Search
        results = await search.search("programming languages", k=5)
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ):
        self.embedder = embedding_provider
        self.store = vector_store

    async def index_document(
        self,
        text: str,
        doc_id: str | None = None,
        metadata: dict | None = None,
    ):
        """Index single document.

        Args:
            text: Document text
            doc_id: Optional document ID
            metadata: Optional metadata
        """
        vector = await self.embedder.embed_text(text)

        document = Document(
            id=doc_id or str(hash(text)),
            text=text,
            vector=vector,
            metadata=metadata,
        )

        await self.store.add_document(document)

    async def index_documents(
        self,
        texts: list[str],
        metadata_list: list[dict] | None = None,
    ):
        """Index multiple documents.

        Args:
            texts: List of document texts
            metadata_list: Optional list of metadata dicts
        """
        vectors = await self.embedder.embed_documents(texts)

        documents = []
        for i, (text, vector) in enumerate(zip(texts, vectors, strict=False)):
            metadata = metadata_list[i] if metadata_list else None
            documents.append(
                Document(
                    id=str(hash(text)),
                    text=text,
                    vector=vector,
                    metadata=metadata,
                ),
            )

        await self.store.add_documents(documents)

    async def search(
        self,
        query: str,
        k: int = 10,
        filter_dict: dict | None = None,
    ) -> list[SearchResult]:
        """Search for semantically similar documents.

        Args:
            query: Search query
            k: Number of results
            filter_dict: Optional metadata filter

        Returns:
            List of search results
        """
        query_vector = await self.embedder.embed_text(query)

        return await self.store.search(
            query_vector=query_vector,
            k=k,
            filter_dict=filter_dict,
        )
