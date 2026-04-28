import types

import numpy as np
import pytest

from pheno.vector.stores import faiss_store, qdrant_store
from pheno.vector.stores.base import Document


@pytest.mark.asyncio
async def test_faiss_vector_store(monkeypatch):
    class FakeFaissIndex:
        def __init__(self, dimension):
            self.dim = dimension
            self.vectors: list[list[float]] = []
            self.ids: list[int] = []

        def add_with_ids(self, data, ids):
            self.vectors.extend(data.tolist())
            self.ids.extend(ids.tolist())

        def search(self, query, k):
            query_vec = np.array(query[0])
            distances = []
            indices = []
            for idx, vec in zip(self.ids, self.vectors, strict=False):
                dist = float(np.linalg.norm(np.array(vec) - query_vec))
                distances.append(dist)
                indices.append(idx)
            return np.array([distances]), np.array([indices])

        def remove_ids(self, selector):  # pragma: no cover - not used in test
            pass

        @property
        def ntotal(self):
            return len(self.ids)

    fake_module = types.SimpleNamespace(
        IndexFlatL2=lambda dim: FakeFaissIndex(dim),
        IndexIDMap=lambda index: index,
        IDSelectorRange=lambda start, end: None,
    )

    monkeypatch.setattr(faiss_store, "faiss", fake_module, raising=False)

    store = faiss_store.FaissVectorStore(dimension=3, normalize=False)
    doc1 = Document(id="1", text="hello", vector=[1.0, 0.0, 0.0])
    doc2 = Document(id="2", text="world", vector=[0.0, 1.0, 0.0])

    await store.add_documents([doc1, doc2])

    results = await store.search([1.0, 0.2, 0.0], k=2)
    assert results
    assert results[0].document.id == "1"


@pytest.mark.asyncio
async def test_qdrant_vector_store(monkeypatch):
    class DummyResponseItem:
        def __init__(self, idx, score):
            self.id = idx
            self.score = score
            self.payload = {"text": f"doc-{idx}"}

    class DummyClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.collections = types.SimpleNamespace(collections=[])

        def get_collections(self):
            return types.SimpleNamespace(collections=[])

        def recreate_collection(self, collection_name, vectors_config):
            return None

        def upsert(self, collection_name, points):
            self._payload = points

        def search(self, collection_name, query_vector, limit, query_filter=None):
            return [DummyResponseItem("a", 0.9), DummyResponseItem("b", 0.5)]

        def delete(self, collection_name, points_selector):  # pragma: no cover - not used
            return None

    monkeypatch.setattr(qdrant_store, "QdrantClient", DummyClient, raising=False)
    monkeypatch.setattr(
        qdrant_store, "VectorParams", lambda size, distance: (size, distance), raising=False,
    )
    monkeypatch.setattr(
        qdrant_store, "Distance", types.SimpleNamespace(COSINE="cosine"), raising=False,
    )

    store = qdrant_store.QdrantVectorStore(collection="test", dimension=3)
    await store.add_document(Document(id="x", text="sample", vector=[0, 0, 1]))

    results = await store.search([0, 0, 1], k=2)
    assert len(results) == 2
    assert results[0].score >= results[1].score
