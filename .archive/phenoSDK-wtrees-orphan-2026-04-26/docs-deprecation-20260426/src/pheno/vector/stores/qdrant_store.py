"""
Qdrant vector store wrapper.
"""

from __future__ import annotations

import logging

from pheno.vector.stores.base import Document, SearchResult, VectorStore

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from qdrant_client import QdrantClient  # type: ignore
    from qdrant_client.models import Distance, VectorParams  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    QdrantClient = None
    Distance = None
    VectorParams = None


class QdrantVectorStore(VectorStore):
    """
    Simple wrapper around Qdrant collections.
    """

    def __init__(
        self,
        collection: str,
        dimension: int,
        *,
        url: str | None = None,
        api_key: str | None = None,
        prefer_grpc: bool = False,
    ) -> None:
        if QdrantClient is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError(
                "qdrant-client not installed. Install with `pip install qdrant-client`.",
            )

        self.collection = collection
        self.dimension = dimension
        self._client = QdrantClient(url=url, api_key=api_key, prefer_grpc=prefer_grpc)
        self._ensure_collection()

    async def add_document(self, document: Document):
        await self.add_documents([document])

    async def add_documents(self, documents: list[Document]):
        if not documents:
            return
        payloads = [doc.metadata or {} for doc in documents]
        vectors = [doc.vector for doc in documents]
        ids = [doc.id for doc in documents]
        self._client.upsert(  # type: ignore[func-returns-value]
            collection_name=self.collection,
            points={"ids": ids, "vectors": vectors, "payloads": payloads},
        )

    async def search(
        self,
        query_vector: list[float],
        k: int = 10,
        filter_dict: dict | None = None,
    ) -> list[SearchResult]:
        filter_proto = filter_dict if filter_dict else None
        response = self._client.search(  # type: ignore[assignment]
            collection_name=self.collection,
            query_vector=query_vector,
            limit=k,
            query_filter=filter_proto,
        )
        results: list[SearchResult] = []
        for item in response:
            doc = Document(
                id=str(item.id),
                text=item.payload.get("text", ""),
                vector=query_vector,
                metadata=item.payload,
            )
            results.append(SearchResult(document=doc, score=float(item.score)))
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    async def delete(self, document_id: str):
        self._client.delete(  # type: ignore[func-returns-value]
            collection_name=self.collection,
            points_selector={"ids": [document_id]},
        )

    def _ensure_collection(self) -> None:
        collections = self._client.get_collections()  # type: ignore[assignment]
        names = {collection.name for collection in collections.collections}
        if self.collection not in names:
            self._client.recreate_collection(  # type: ignore[func-returns-value]
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )
