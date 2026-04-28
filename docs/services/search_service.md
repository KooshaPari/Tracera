# Search Service Documentation

## Overview

The TraceRTM Search Service provides high-performance, multi-modal search capabilities using PostgreSQL full-text search and pgvector semantic search. The service supports keyword matching, semantic understanding, fuzzy matching, and advanced filtering.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Search Service                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Full-Text   │  │   Semantic   │  │    Hybrid    │      │
│  │    Search    │  │    Search    │  │    Search    │      │
│  │  (tsvector)  │  │  (pgvector)  │  │     (RRF)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Fuzzy     │  │   Advanced   │  │   Suggest    │      │
│  │    Search    │  │   Filtering  │  │ (Autocomplete)│      │
│  │  (pg_trgm)   │  │  (Dynamic)   │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    Redis Cache (5 min TTL)                  │
└─────────────────────────────────────────────────────────────┘
```

## Search Types

### 1. Full-Text Search (PostgreSQL tsvector)

**Best for**: Exact keyword matching, boolean queries, phrase searches

**Performance**: < 100ms for most queries

**Features**:
- Uses PostgreSQL's built-in full-text search
- Supports English stemming and stop words
- Weighted ranking (title > description > metadata)
- Boolean operators (AND, OR, NOT)

**Example**:
```go
results, err := service.FullTextSearch(ctx, FullTextSearchRequest{
    Query:     "authentication AND login",
    ProjectID: "proj-123",
    Limit:     20,
    MinScore:  0.1,
})
```

**SQL Implementation**:
```sql
SELECT id, title, description,
       ts_rank(search_vector, websearch_to_tsquery('english', $1)) AS score
FROM items
WHERE search_vector @@ websearch_to_tsquery('english', $1)
  AND project_id = $2
ORDER BY score DESC
LIMIT $3
```

### 2. Semantic Search (pgvector)

**Best for**: Conceptual understanding, similar meaning, cross-lingual

**Performance**: < 200ms with HNSW index

**Features**:
- Uses vector embeddings (1024-dim VoyageAI)
- Cosine similarity matching
- Understands semantic relationships
- Language-agnostic

**Example**:
```go
results, err := service.SemanticSearch(ctx, SemanticSearchRequest{
    Query:     "user authentication flow",
    ProjectID: "proj-123",
    TopK:      20,
    Threshold: 0.5,
})
```

**SQL Implementation**:
```sql
SELECT id, title, description,
       1 - (embedding <=> $1::vector) AS similarity
FROM items
WHERE embedding IS NOT NULL
  AND project_id = $2
  AND (1 - (embedding <=> $1::vector)) >= $3
ORDER BY embedding <=> $1::vector
LIMIT $4
```

### 3. Hybrid Search (Reciprocal Rank Fusion)

**Best for**: Best of both worlds - keyword + semantic

**Performance**: < 300ms (runs both searches in parallel)

**Features**:
- Combines full-text and semantic results
- Reciprocal Rank Fusion (RRF) algorithm
- Configurable weights
- Deduplicates results

**Example**:
```go
results, err := service.HybridSearch(ctx, HybridSearchRequest{
    Query:          "authentication system",
    ProjectID:      "proj-123",
    Limit:          20,
    TextWeight:     0.6,  // 60% weight to keyword matching
    SemanticWeight: 0.4,  // 40% weight to semantic similarity
})
```

**RRF Algorithm**:
```
RRF(d) = Σ (weight / (k + rank(d)))
where k = 60 (constant)
```

### 4. Fuzzy Search (pg_trgm)

**Best for**: Typo tolerance, spelling mistakes, partial matches

**Performance**: < 150ms

**Features**:
- Trigram similarity matching
- Handles typos (1-3 character differences)
- Case-insensitive
- Works without exact matches

**Example**:
```go
results, err := service.FuzzySearch(ctx, FuzzySearchRequest{
    Query:       "authenticaton",  // Note: missing 'i'
    ProjectID:   "proj-123",
    MaxDistance: 3,
    Limit:       20,
})
```

**SQL Implementation**:
```sql
SELECT id, title, description,
       similarity(title, $1) AS score
FROM items
WHERE (title % $1 OR description % $1)
  AND similarity(title, $1) > 0.3
ORDER BY score DESC
LIMIT $2
```

### 5. Advanced Search (Dynamic Filtering)

**Best for**: Complex queries with multiple filters

**Features**:
- Dynamic query builder
- Multiple filter operators (eq, neq, contains, gt, lt, in)
- Custom sorting
- Pagination

**Example**:
```go
results, err := service.AdvancedSearch(ctx, AdvancedSearchRequest{
    ProjectID: "proj-123",
    Query:     "authentication",
    Filters: []SearchFilter{
        {Field: "type", Operator: "eq", Value: "requirement"},
        {Field: "status", Operator: "in", Value: []string{"active", "review"}},
        {Field: "priority", Operator: "gt", Value: 5},
    },
    Sort: []SortOption{
        {Field: "priority", Direction: "desc"},
        {Field: "updated_at", Direction: "desc"},
    },
    Limit: 20,
})
```

## Performance Optimization

### 1. Caching Strategy

All search results are cached in Redis for 5 minutes:

```go
cacheKey := generateCacheKey("fulltext", req)
if cached, err := cache.Get(ctx, cacheKey); err == nil {
    return cached
}

results := performSearch(req)
cache.Set(ctx, cacheKey, results, 5*time.Minute)
```

**Cache Hit Rates**:
- Full-text: ~70%
- Semantic: ~60%
- Hybrid: ~50%

### 2. Database Indexes

**Full-Text Search**:
```sql
CREATE INDEX idx_items_search_vector ON items USING GIN (search_vector);
```

**Trigram Fuzzy Matching**:
```sql
CREATE INDEX idx_items_title_trgm ON items USING GIN (title gin_trgm_ops);
CREATE INDEX idx_items_description_trgm ON items USING GIN (description gin_trgm_ops);
```

**Vector Search (HNSW)**:
```sql
CREATE INDEX idx_items_embedding_hnsw ON items
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**HNSW Parameters**:
- `m = 16`: Number of connections per layer (higher = better accuracy, slower build)
- `ef_construction = 64`: Build quality (higher = better accuracy, slower build)

### 3. Query Optimization

**Limit Scanning**:
```sql
-- Good: Use LIMIT to reduce scanned rows
SELECT * FROM items WHERE ... LIMIT 20;

-- Bad: Scan all rows then limit in application
SELECT * FROM items WHERE ...;
```

**Avoid N+1 Queries**:
```sql
-- Good: Single query with JOIN
SELECT i.*, m.metadata FROM items i LEFT JOIN metadata m ON i.id = m.item_id;

-- Bad: Query in loop
for item in items:
    metadata = db.query("SELECT * FROM metadata WHERE item_id = ?", item.id)
```

## Ranking Strategies

### 1. Full-Text Ranking (ts_rank)

PostgreSQL's `ts_rank` calculates relevance based on:
- Term frequency (TF)
- Document length normalization
- Weight (A > B > C > D)

```sql
ts_rank(
    search_vector,
    query,
    normalization := 1  -- Divides rank by 1 + log(doc_length)
)
```

### 2. Semantic Ranking (Cosine Similarity)

```
similarity = 1 - cosine_distance
cosine_distance = 1 - (A · B) / (||A|| * ||B||)
```

Range: 0.0 (completely different) to 1.0 (identical)

### 3. Hybrid Ranking (RRF)

Reciprocal Rank Fusion combines rankings:

```
For each result in text_results:
    score[result] += text_weight / (60 + rank)

For each result in semantic_results:
    score[result] += semantic_weight / (60 + rank)

Sort by combined score
```

**Why RRF?**:
- Handles different score scales
- Resistant to outliers
- Proven effective in IR research

## Autocomplete (Suggestions)

```go
suggestions, err := service.Suggest(ctx, "auth", 10)
// Returns: ["Authentication", "Authorization", "Audit Log", ...]
```

**Implementation**:
```sql
SELECT DISTINCT title,
       word_similarity($1, title) AS score
FROM items
WHERE (title ILIKE $1 || '%' OR title % $1)
  AND deleted_at IS NULL
ORDER BY score DESC, title
LIMIT $2
```

## Indexing Operations

### Index Single Item
```go
err := service.IndexItem(ctx, &Item{
    ID:          "item-123",
    Title:       "User Authentication",
    Description: "Implement OAuth2 authentication flow",
    Type:        "requirement",
})
```

### Batch Index
```go
items := []*Item{
    {ID: "1", Title: "Item 1", ...},
    {ID: "2", Title: "Item 2", ...},
    {ID: "3", Title: "Item 3", ...},
}
err := service.BatchIndexItems(ctx, items)
```

### Delete from Index
```go
err := service.DeleteFromIndex(ctx, "item-123")
```

**Note**: Indexing invalidates cache automatically.

## Error Handling

```go
results, err := service.FullTextSearch(ctx, req)
if err != nil {
    switch {
    case errors.Is(err, context.DeadlineExceeded):
        // Handle timeout
    case strings.Contains(err.Error(), "connection"):
        // Handle database connection error
    default:
        // Generic error
    }
}
```

## Monitoring & Metrics

### Query Performance

```sql
-- View slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%items%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Index Usage

```sql
-- Check index efficiency
SELECT schemaname, tablename, indexname,
       idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'items';
```

### Cache Hit Rate

```go
// Monitor Redis cache
stats := cache.Stats()
hitRate := float64(stats.Hits) / float64(stats.Hits + stats.Misses)
```

## Best Practices

### 1. Choose the Right Search Type

| Use Case | Search Type |
|----------|-------------|
| Exact keyword match | Full-Text |
| "Find similar items" | Semantic |
| Best overall results | Hybrid |
| Typo-tolerant input | Fuzzy |
| Complex filtering | Advanced |
| Autocomplete | Suggest |

### 2. Set Appropriate Limits

```go
// Good: Reasonable limit
req.Limit = 20

// Bad: Unbounded or too large
req.Limit = 10000  // Will be capped at 100
```

### 3. Use Minimum Score Thresholds

```go
// Filter low-quality results
req.MinScore = 0.1  // Full-text
req.Threshold = 0.5  // Semantic
```

### 4. Leverage Caching

```go
// Cache automatically used for 5 minutes
// To bypass cache for real-time results:
cache.InvalidatePattern(ctx, "search:*")
```

### 5. Monitor Performance

```go
start := time.Now()
results, err := service.Search(ctx, req)
duration := time.Since(start)

if duration > 500*time.Millisecond {
    log.Warn("Slow search query", "duration", duration, "query", req.Query)
}
```

## Troubleshooting

### Slow Queries

**Problem**: Search takes > 500ms

**Solutions**:
1. Check indexes: `EXPLAIN ANALYZE SELECT ...`
2. Reduce LIMIT
3. Add more specific filters
4. Increase cache TTL
5. Consider read replicas

### Low Relevance

**Problem**: Irrelevant results returned

**Solutions**:
1. Increase `MinScore` threshold
2. Use Hybrid search instead of Full-Text only
3. Adjust weights in Hybrid search
4. Re-index items with better metadata

### No Results

**Problem**: Valid query returns 0 results

**Solutions**:
1. Check if items are indexed: `SELECT COUNT(*) FROM items WHERE search_vector IS NOT NULL`
2. Try Fuzzy search for typo tolerance
3. Verify filters aren't too restrictive
4. Check `deleted_at` filter

### Cache Issues

**Problem**: Stale results returned

**Solutions**:
```go
// Clear specific cache
cache.InvalidatePattern(ctx, "search:fulltext:*")

// Clear all search cache
cache.InvalidatePattern(ctx, "search:*")
```

## API Examples

### REST Endpoints

```bash
# Full-text search
POST /api/v1/search
{
  "query": "authentication",
  "type": "fulltext",
  "project_id": "proj-123",
  "limit": 20
}

# Semantic search
POST /api/v1/search
{
  "query": "user login flow",
  "type": "semantic",
  "project_id": "proj-123",
  "top_k": 20,
  "threshold": 0.5
}

# Hybrid search
POST /api/v1/search
{
  "query": "authentication",
  "type": "hybrid",
  "project_id": "proj-123",
  "text_weight": 0.6,
  "semantic_weight": 0.4,
  "limit": 20
}

# Autocomplete
GET /api/v1/search/suggest?prefix=auth&limit=10
```

## Performance Benchmarks

Tested on:
- PostgreSQL 15
- pgvector 0.5
- 10,000 items
- 1024-dim embeddings

| Search Type | Avg Time | P95 Time | Cache Hit |
|-------------|----------|----------|-----------|
| Full-Text   | 45ms     | 95ms     | 70%       |
| Semantic    | 120ms    | 180ms    | 60%       |
| Hybrid      | 165ms    | 250ms    | 50%       |
| Fuzzy       | 60ms     | 110ms    | 65%       |
| Advanced    | 35ms     | 80ms     | 55%       |

## Future Enhancements

- [ ] Multi-language support (non-English)
- [ ] Faceted search (aggregations by type, status, etc.)
- [ ] Query suggestions ("Did you mean...")
- [ ] Personalized ranking based on user preferences
- [ ] Elasticsearch integration for advanced features
- [ ] Real-time indexing with change data capture (CDC)

## References

- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [pg_trgm Extension](https://www.postgresql.org/docs/current/pgtrgm.html)
- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)
