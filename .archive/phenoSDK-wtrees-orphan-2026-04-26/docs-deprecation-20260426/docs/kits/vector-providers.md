# Vector Providers Matrix

Status: Stubs added for provider adapters; implementations to follow.

| Backend | Module | Sync/Async | License | Notes |
|---|---|---|---|---|
| FAISS | vector_kit/stores/faiss.py | Async wrapper (planned) | MIT | CPU/GPU builds; local/offline |
| Qdrant | vector_kit/stores/qdrant.py | Async client (planned) | Apache-2.0 | Remote server; filters/payload |
| Chroma | vector_kit/stores/chroma.py | Async wrapper (planned) | Apache-2.0 | Local/remote; persistent collections |

Migration path: maintain InMemoryVectorStore for tests; add provider-specific extras.
