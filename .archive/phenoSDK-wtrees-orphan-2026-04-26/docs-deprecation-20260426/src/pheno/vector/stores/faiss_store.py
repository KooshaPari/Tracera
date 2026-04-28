"""
FAISS vector store implementation.
"""

from __future__ import annotations

import logging

from pheno.vector.stores.base import Document, SearchResult, VectorStore

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    faiss = None


class FaissVectorStore(VectorStore):
    """
    Vector store backed by FAISS (IndexFlatL2).
    """

    def __init__(self, dimension: int, *, normalize: bool = True) -> None:
        if faiss is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError(
                "faiss is not installed. Install with `pip install faiss-cpu` to enable FaissVectorStore.",
            )

        self._dimension = dimension
        self._normalize = normalize
        self._index = faiss.IndexIDMap(faiss.IndexFlatL2(dimension))
        self._documents: dict[int, Document] = {}

    async def add_document(self, document: Document):
        await self.add_documents([document])

    async def add_documents(self, documents: list[Document]):
        if not documents:
            return

        vectors = []
        ids = []
        for doc in documents:
            vec = self._ensure_vector(doc.vector)
            vectors.append(vec)
            ids.append(int(hash(doc.id) & 0xFFFFFFFF))
        import numpy as np  # type: ignore

        data = np.vstack(vectors).astype("float32")
        id_array = np.array(ids, dtype="int64")
        self._index.add_with_ids(data, id_array)
        for id_value, doc in zip(id_array, documents, strict=False):
            self._documents[int(id_value)] = doc

    async def search(
        self, query_vector: list[float], k: int = 10, filter_dict: dict | None = None,
    ) -> list[SearchResult]:
        if self._index.ntotal == 0:
            return []
        import numpy as np  # type: ignore

        vec = self._ensure_vector(query_vector)
        query = np.array([vec], dtype="float32")
        distances, indices = self._index.search(query, k)
        results: list[SearchResult] = []
        for dist, idx in zip(distances[0], indices[0], strict=False):
            if idx == -1:
                continue
            doc = self._documents.get(int(idx))
            if not doc:
                continue
            similarity = 1.0 / (1.0 + float(dist))
            results.append(SearchResult(document=doc, score=similarity))
        results.sort(key=lambda item: item.score, reverse=True)
        return results

    async def delete(self, document_id: str):
        target_hash = int(hash(document_id) & 0xFFFFFFFF)
        if target_hash in self._documents:
            self._index.remove_ids(faiss.IDSelectorRange(target_hash, target_hash + 1))
            self._documents.pop(target_hash, None)

    def _ensure_vector(self, vector: list[float]) -> list[float]:
        if self._normalize:
            import numpy as np  # type: ignore

            arr = np.array(vector, dtype="float32")
            norm = np.linalg.norm(arr)
            if norm != 0:
                arr = arr / norm
            return arr.tolist()
        return vector
