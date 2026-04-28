# Vector Search Backends

This directory contains vector search backend implementations for the pheno-SDK.

## Available Backends

### 1. PgVector Backend (PostgreSQL)

Production-ready backend using PostgreSQL with pgvector extension.

**Best for**: Production deployments, large-scale vector search

**Dependencies**:
```bash
pip install asyncpg pgvector
```

**Usage**:
```python
from pheno.vector.backends import PgVectorBackend

backend = PgVectorBackend(
    dsn="postgresql://user:pass@localhost/db",
    table_name="embeddings",
    dimension=768,
    pool_min_size=2,
    pool_max_size=10,
    distance_metric="l2"  # or "cosine", "inner_product"
)

await backend.initialize()
```

**Features**:
- Connection pooling for high performance
- HNSW index for fast approximate nearest neighbor search
- Multiple distance metrics (L2, cosine, inner product)
- GIN index for efficient metadata filtering
- Automatic table and index creation
- >1000 vectors/second insert rate

### 2. LanceDB Backend (Local)

Embedded vector database for local development and edge deployments.

**Best for**: Local development, testing, edge deployments

**Dependencies**:
```bash
pip install lancedb pyarrow
```

**Usage**:
```python
from pheno.vector.backends import LanceDBBackend

backend = LanceDBBackend(
    uri="/path/to/lancedb",
    table_name="embeddings",
    dimension=768,
    distance_metric="l2"  # or "cosine", "dot"
)

await backend.initialize()
```

**Features**:
- No server required - fully embedded
- File-based persistence
- Multiple distance metrics
- Fast local search
- Multi-table support
- Data persists across restarts

### 3. Supabase Backend (Legacy)

Existing backend using Supabase for vector search.

**Best for**: Managed cloud deployments with Supabase

**Usage**:
```python
from pheno.vector.client import IndexBackend

backend_config = IndexBackend.supabase(
    client=supabase_client
)
```

## Common Interface

All backends implement the `IndexBackend` abstract base class:

```python
class IndexBackend(ABC):
    async def insert(id: str, vector: list[float], metadata: dict) -> None
    async def search(query_vector: list[float], limit: int, ...) -> list[dict]
    async def delete(id: str) -> bool
    async def count(filters: dict | None = None) -> int
```

## Factory Pattern

Use the factory pattern for easy backend creation:

```python
from pheno.vector.client import IndexBackend

# PgVector
backend = IndexBackend.pgvector(
    dsn="postgresql://...",
    dimension=768
)

# LanceDB
backend = IndexBackend.lancedb(
    uri="/path/to/db",
    dimension=768
)

# Supabase
backend = IndexBackend.supabase(
    client=supabase_client
)
```

## Distance Metrics

All backends support multiple distance metrics:

- **L2 (Euclidean)**: General-purpose similarity
- **Cosine**: Angle-based similarity (normalized)
- **Dot Product**: Optimized for dot product similarity

## Performance Comparison

| Backend | Insert Rate | Search Rate | Scalability | Setup |
|---------|-------------|-------------|-------------|-------|
| PgVector | >1000/s | >10/s | Millions | Medium |
| LanceDB | >100/s | >5/s | Thousands | Easy |
| Supabase | High | High | Millions | Easy |

## Testing

Run backend tests:

```bash
# Quick validation (no dependencies required)
python test_backends_simple.py

# Full test suite (requires dependencies)
pytest tests/vector/test_pgvector_backend.py -v
pytest tests/vector/test_lancedb_backend.py -v
```

## Coming Soon

- **FAISS Backend**: In-memory high-performance search
- **OpenAI Backend**: OpenAI-hosted vector search
- **Qdrant Backend**: Distributed vector search

## Migration Guide

Switching backends is easy thanks to the consistent interface:

```python
# Before (Supabase)
backend = IndexBackend.supabase(client=supabase_client)

# After (PgVector)
backend = IndexBackend.pgvector(dsn="postgresql://...")

# Or (LanceDB)
backend = IndexBackend.lancedb(uri="/path/to/db")

# Rest of code stays the same
await backend.initialize()
await backend.insert(id="...", vector=[...], metadata={})
results = await backend.search(query_vector=[...], limit=10)
```

## Error Handling

All backends provide clear error messages:

```python
try:
    backend = PgVectorBackend(dsn="invalid://...")
    await backend.initialize()
except ImportError as e:
    # Missing dependencies
    print(f"Install dependencies: {e}")
except Exception as e:
    # Connection or configuration errors
    print(f"Backend error: {e}")
```

## Best Practices

1. **Use connection pooling** for PgVector in production
2. **Use async context managers** for automatic cleanup
3. **Choose appropriate distance metrics** for your use case
4. **Index metadata fields** for efficient filtering
5. **Batch operations** for better performance
6. **Monitor performance** and tune settings

## Support

For issues or questions:
- Check the test files for usage examples
- See PHASE_3_TASK_3.1_COMPLETION_REPORT.md for details
- Refer to individual backend docstrings
