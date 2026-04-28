# Pheno Caching System - Complete Usage Guide

Comprehensive multi-layer caching infrastructure extracted from atoms project.

## Quick Start

```bash
# Install pheno-sdk
pip install pheno-sdk

# Run examples
python examples/caching/hot_cache_example.py
python examples/caching/cold_cache_example.py
python examples/caching/dry_run_example.py
```

## Overview

The Pheno caching system provides three complementary caching strategies:

### 1. Hot Cache (In-Memory TTL-Based)
- **Use Case**: Frequently accessed data with acceptable staleness
- **Performance**: 10x improvement for repeated queries
- **TTL**: 30 seconds default
- **Persistence**: Process lifetime only

### 2. Cold Cache (Persistent Disk-Based)
- **Use Case**: Expensive computations (embeddings, ML outputs)
- **Performance**: Eliminates recomputation across restarts
- **TTL**: Hours to days (configurable)
- **Persistence**: Survives process restarts

### 3. Dry-Run System (Non-Destructive Operations)
- **Use Case**: Safe testing, previews, staging operations
- **Performance**: Negligible overhead (~0.001ms)
- **Mode**: Global or instance-level
- **Persistence**: N/A (behavioral flag)

## Installation

```bash
pip install pheno-sdk
```

Or install from source:
```bash
cd pheno-sdk
pip install -e .
```

## Hot Cache Examples

### Basic Usage

```python
from pheno.caching import QueryCache

# Create cache with 30 second TTL
cache = QueryCache(ttl=30, max_size=1000)

# Generate cache key
key = cache.generate_key("select", {"table": "users", "id": 123})

# Check cache
result = cache.get(key)
if result is None:
    # Cache miss - query database
    result = await db.query(...)
    cache.set(key, result, metadata={"table": "users"})

# Statistics
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

### Database Adapter Integration

```python
from pheno.caching import CachedQueryMixin

class DatabaseAdapter(CachedQueryMixin):
    def __init__(self):
        self._init_cache(ttl=30, max_size=1000)

    async def select(self, table: str, filters: dict):
        key = self._query_cache.generate_key("select", {
            "table": table, "filters": filters
        })

        # Check cache
        cached = self._query_cache.get(key)
        if cached is not None:
            return cached

        # Query database
        result = await self._execute_query(table, filters)

        # Cache result
        self._query_cache.set(key, result, {"table": table})
        return result

    async def insert(self, table: str, data: dict):
        result = await self._execute_insert(table, data)
        # Invalidate cache on write
        self._query_cache.invalidate_by_table(table)
        return result
```

### Performance Characteristics

- Cache Hit: ~0.001ms (in-memory lookup)
- Cache Miss: Query time + ~0.01ms (overhead)
- Speedup: **10x for repeated queries**
- Memory: ~1KB per entry

## Cold Cache Examples

### Embedding Cache

```python
from pheno.caching import EmbeddingCache

# Create cache (survives restarts)
cache = EmbeddingCache(ttl=86400)  # 24 hour TTL

# Cache embedding
cache.set_embedding(
    entity_id="doc_123",
    embedding=[0.1, 0.2, ...],  # 768-dim vector
    model="text-embedding-3-small",
    dimensions=768,
    entity_type="document"
)

# Retrieve cached embedding (instant!)
result = cache.get_embedding("doc_123")
if result is None:
    embedding = await generate_embedding(text)  # Expensive!
    cache.set_embedding("doc_123", embedding, model, dims)
```

### Test Data Cache

```python
from pheno.caching import TestDataCache

# Create cache (never expires)
cache = TestDataCache()

# Cache test UUIDs
cache.set_uuid("test_user", "550e8400-e29b-41d4-a716-446655440000")
cache.set_uuid("test_org", "550e8400-e29b-41d4-a716-446655440001")

# Retrieve in tests (consistent across runs!)
user_id = cache.get_uuid("test_user")
if user_id is None:
    user_id = create_test_user()
    cache.set_uuid("test_user", user_id)
```

### Performance Characteristics

- Cache Hit: ~1-5ms (disk read + JSON parse)
- Cache Miss: Computation time + ~2-10ms (write + sync)
- Speedup: **Eliminates expensive recomputation**
- Disk: Configurable max_size_mb (default 1GB)

## Dry-Run Examples

### Function Decorator

```python
from pheno.caching import set_dry_run, dry_run_aware

# Enable dry-run mode
set_dry_run(True)

# Decorate functions
@dry_run_aware(operation_name="delete_user", return_value={"deleted": False})
async def delete_user(user_id: str):
    # In dry-run mode, this logs but doesn't execute
    await db.delete("users", {"id": user_id})
    return {"deleted": True}

# Safe preview
result = await delete_user("123")  # Logs: [DRY RUN] Would execute...
```

### Class with Dry-Run Support

```python
from pheno.caching import DryRunMixin, dry_run_method

class UserService(DryRunMixin):
    def __init__(self, dry_run: bool = False):
        self._init_dry_run(dry_run)

    @dry_run_method(return_value={"created": False, "id": "dry-run-id"})
    async def create_user(self, name: str, email: str):
        # Skipped if dry_run=True
        result = await db.insert("users", {"name": name, "email": email})
        return result

# Use in CLI
service = UserService(dry_run=args.dry_run)
await service.create_user("John", "john@example.com")
```

### Context Manager

```python
from pheno.caching import DryRunContext

# Temporary dry-run
with DryRunContext(enabled=True):
    # All operations in this block are dry-run
    await delete_user("user_123")
    await send_email("test@example.com", "Subject", "Body")

# Outside context, dry-run mode is restored
```

## Multi-Layer Caching Strategy

Combine hot and cold caches for optimal performance:

```python
from pheno.caching import QueryCache, EmbeddingCache

# Hot cache for frequent queries (30s TTL)
query_cache = QueryCache(ttl=30)

# Cold cache for embeddings (24h TTL)
embedding_cache = EmbeddingCache(ttl=86400)

async def get_embedding(entity_id: str):
    # Layer 1: Hot cache (instant)
    key = query_cache.generate_key("embedding", {"id": entity_id})
    result = query_cache.get(key)
    if result is not None:
        return result

    # Layer 2: Cold cache (fast)
    result = embedding_cache.get_embedding(entity_id)
    if result is not None:
        # Promote to hot cache
        query_cache.set(key, result)
        return result

    # Layer 3: Generate (expensive)
    embedding = await generate_embedding(entity_id)

    # Cache in both layers
    embedding_cache.set_embedding(entity_id, embedding, "model", 768)
    query_cache.set(key, embedding)
    return embedding
```

## Best Practices

### Hot Cache

1. **TTL Selection**
   - Read-heavy: 60 seconds
   - Moderate: 30 seconds (default)
   - Write-heavy: 10-15 seconds

2. **Size Limits**
   - Small datasets: 1000 entries
   - Medium datasets: 5000 entries
   - Large datasets: 10000 entries

3. **Invalidation**
   - Always invalidate on writes
   - Use table-based invalidation for simplicity
   - Use pattern-based for complex queries

### Cold Cache

1. **TTL Selection**
   - Embeddings: 24 hours
   - Test data: Never expire
   - Build artifacts: 7 days

2. **Cleanup**
   - Run periodic cleanup_expired()
   - Schedule during low-traffic periods
   - Monitor disk usage

3. **Namespace Strategy**
   - Separate namespaces for different data types
   - Use descriptive names (embeddings, test_data, config)
   - Isolate environments (dev, staging, prod)

### Dry-Run System

1. **Always Test**
   - Test with dry_run=True first
   - Verify logs show expected operations
   - Confirm return values are correct

2. **CLI Integration**
   - Provide --dry-run flag
   - Show clear dry-run status
   - Prompt before actual execution

3. **Destructive Operations**
   - Always use dry-run for DELETE/UPDATE
   - Log all operations
   - Implement confirmation prompts

## Performance Metrics

### Hot Cache
- **Hit latency**: 0.001ms
- **Miss latency**: 0.01ms
- **Speedup**: 10x for repeated queries
- **Memory overhead**: ~1KB per entry

### Cold Cache
- **Hit latency**: 1-5ms
- **Miss latency**: 2-10ms
- **Speedup**: Eliminates recomputation
- **Disk overhead**: ~2KB per entry + data size

### Dry-Run
- **Overhead**: 0.001ms
- **Memory**: Negligible
- **CPU**: < 0.1%

## Monitoring

### Hot Cache Statistics

```python
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Size: {stats['size']}/{stats['max_size']}")
print(f"Evictions: {stats['evictions']}")
print(f"Invalidations: {stats['invalidations']}")
```

### Cold Cache Statistics

```python
stats = cache.get_stats()
print(f"Entries: {stats['entries']}")
print(f"Size: {stats['size_mb']} MB")
print(f"Location: {stats['cache_dir']}")
```

### Dry-Run State

```python
from pheno.caching import is_dry_run

if is_dry_run():
    print("Running in dry-run mode")
```

## Integration Tests

Run the examples to verify installation:

```bash
# Hot cache examples
python examples/caching/hot_cache_example.py

# Cold cache examples
python examples/caching/cold_cache_example.py

# Dry-run examples
python examples/caching/dry_run_example.py
```

Expected output:
- All examples should run without errors
- Hot cache should show 10x speedup
- Cold cache should persist across runs
- Dry-run should log operations without executing

## Troubleshooting

### Hot Cache Issues

**Problem**: Low hit rate
- Check TTL is appropriate for workload
- Verify cache key generation is consistent
- Ensure invalidation isn't too aggressive

**Problem**: High memory usage
- Reduce max_size
- Lower TTL to expire entries faster
- Implement more aggressive cleanup

### Cold Cache Issues

**Problem**: Cache directory not found
- Check permissions on ~/.cache/pheno/
- Verify cache_dir path is correct
- Create directory manually if needed

**Problem**: High disk usage
- Run cleanup_expired()
- Reduce max_size_mb
- Lower TTL for non-critical data

### Dry-Run Issues

**Problem**: Operations executing in dry-run mode
- Verify set_dry_run(True) is called
- Check decorator is applied correctly
- Ensure is_dry_run() returns True

**Problem**: Decorators not working
- Verify function signature matches
- Check async/sync wrapper is correct
- Ensure imports are correct

## API Reference

See inline documentation for detailed API reference:

```python
# Hot Cache API
help(QueryCache)
help(CachedQueryMixin)

# Cold Cache API
help(DiskCache)
help(EmbeddingCache)
help(TestDataCache)

# Dry-Run API
help(dry_run_aware)
help(DryRunMixin)
```

## Contributing

Found a bug or have a feature request? Open an issue on GitHub.

## License

Part of the Pheno SDK.
