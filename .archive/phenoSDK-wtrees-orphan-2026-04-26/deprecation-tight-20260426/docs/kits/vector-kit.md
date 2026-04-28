# Vector Kit

## At a Glance
- **Purpose:** Manage embeddings, vector stores, and semantic search pipelines.
- **Best For:** Retrieval-augmented generation (RAG), semantic search, document intelligence.
- **Key Building Blocks:** Embedding providers, vector stores, `SemanticSearch`, chunking strategies, evaluation utilities.

## Core Capabilities
- Pluggable embedding providers (OpenAI, Cohere, local transformers, in-memory for tests).
- Vector store abstractions with implementations for FAISS, ChromaDB, Supabase pgvector, and in-memory.
- Semantic search pipeline that handles indexing, retrieval, and scoring.
- Text chunking, metadata enrichment, and pipeline orchestration.
- Telemetry hooks for tracking embedding usage and search latency.

## Getting Started

### Installation
```
pip install vector-kit
# Extras
pip install "vector-kit[openai]" "vector-kit[faiss]" "vector-kit[chroma]"
```

### Minimal Example
```python
from vector_kit import SemanticSearch
from vector_kit.embeddings.base import InMemoryEmbeddings
from vector_kit.stores.base import InMemoryVectorStore

search = SemanticSearch(
    embedding_provider=InMemoryEmbeddings(),
    vector_store=InMemoryVectorStore()
)

await search.index_documents([
    "FastAPI integrates well with Pheno-SDK",
    "Observability-kit provides structured logging",
])

results = await search.search("structured logging", k=1)
print(results[0].document.text)
```

## How It Works
- Embedding providers live in `vector_kit.embeddings` (OpenAI, Cohere, HuggingFace, local models).
- Vector stores implement a simple interface (`add`, `search`, `delete`, `flush`).
- `SemanticSearch` orchestrates embedding, chunking, metadata, and store operations.
- Pipelines (`vector_kit.pipelines`) allow composing ingestion and retrieval workflows.
- Telemetry module hooks into observability-kit for metrics (`embedding_requests_total`, `search_latency_seconds`).

## Usage Recipes
- Combine with storage-kit to ingest documents from cloud storage before indexing.
- Use workflow-kit to schedule periodic reindexing and cleanup tasks.
- Integrate with db-kit for metadata persistence and versioning.
- Evaluate retrieval quality using `vector_kit.evaluation` helpers.

## Interoperability
- Config-kit loads provider credentials and index configuration.
- Observability-kit records embedding usage and search metrics.
- Stream-kit can broadcast search results to real-time clients.
- Works with mcp-sdk-kit for LLM agent retrieval workflows.

## Operations & Observability
- Cache embeddings to avoid duplicate API calls; configure TTL via providers.
- Monitor vector store size and TTL to manage cost/performance.
- Use telemetry hooks to alert on high error rates or latency spikes.

## Testing & QA
- In-memory embedding provider and vector store keep tests fast.
- Snapshot retrieval results to detect regressions in scoring.
- Mock external APIs (OpenAI, Cohere) in contract tests.

## Troubleshooting
- **Low recall:** adjust chunking strategy or store parameters (e.g., FAISS index type).
- **High cost:** reuse embeddings, limit contexts, and compress metadata.
- **Provider rate limits:** enable exponential backoff or queue ingestion via workflow-kit.

## Primary API Surface
- `SemanticSearch(embedding_provider, vector_store, *, chunker=None)`
- `SemanticSearch.index_documents(documents, metadata=None)`
- `SemanticSearch.search(query, k=5)`
- `vector_kit.embeddings.openai.OpenAIEmbeddings`
- `vector_kit.stores.faiss.FAISSVectorStore`, `vector_kit.stores.chroma.ChromaVectorStore`
- `vector_kit.chunking.text.TextChunker`
- `vector_kit.evaluation.evaluate_retrieval()`

## Additional Resources
- Examples: `vector-kit/examples/`
- Tests: `vector-kit/tests/`
- Related guides: [Patterns](../concepts/patterns.md), [Operations](../guides/operations.md)
