# TraceRTM Search - Quick Reference

## 🚀 Quick Start

### Activate Search in Your App (5 minutes)

**1. Update `backend/main.go`:**
```go
package main

import (
    // ... existing imports
    "github.com/kooshapari/tracertm-backend/internal/search"
)

func main() {
    // ... existing code (database init, etc.)

    // Initialize search components
    searchEngine := search.NewSearchEngine(pool)
    indexer := search.NewIndexer(pool, 4, 1000)  // 4 workers, 1000 queue size
    indexer.Start()
    defer indexer.Stop()

    // Initialize server with search components
    srv := server.NewServer(pool, cfg, searchEngine, indexer)

    // ... rest of main
}
```

**2. Update `backend/internal/server/server.go`:**
```go
type Server struct {
    echo              *echo.Echo
    pool              *pgxpool.Pool
    cfg               *config.Config
    // ... existing fields
    searchEngine      *search.SearchEngine
    indexer           *search.Indexer
}

func NewServer(pool *pgxpool.Pool, cfg *config.Config,
               searchEngine *search.SearchEngine, indexer *search.Indexer) *Server {
    // ... existing code

    s := &Server{
        // ... existing fields
        searchEngine: searchEngine,
        indexer:      indexer,
    }

    // ... rest of NewServer
}

func (s *Server) setupRoutes() {
    // ... existing routes

    // Search routes (UNCOMMENT THESE - lines 252-269)
    searchHandler := handlers.NewSearchHandler(s.searchEngine, s.indexer)
    api.POST("/search", searchHandler.Search)
    api.GET("/search", searchHandler.SearchGet)
    api.GET("/search/suggest", searchHandler.Suggest)
    api.POST("/search/index/:id", searchHandler.IndexItem)
    api.POST("/search/batch-index", searchHandler.BatchIndex)
    api.POST("/search/reindex", searchHandler.ReindexAll)
    api.GET("/search/stats", searchHandler.IndexStats)
    api.GET("/search/health", searchHandler.SearchHealth)
    api.DELETE("/search/index/:id", searchHandler.DeleteIndex)
}

func (s *Server) Shutdown(ctx context.Context) error {
    // Stop indexer before shutting down
    if s.indexer != nil {
        s.indexer.Stop()
    }
    // ... existing shutdown code
}
```

**3. Run migrations:**
```bash
# Extensions and schema are already in backend/schema.sql
# Just apply them:
psql $DATABASE_URL < backend/schema.sql
```

**4. Test it:**
```bash
# Start server
cd backend && go run main.go

# In another terminal:
curl http://localhost:8080/api/v1/search/health

# Create some items and search
curl -X POST http://localhost:8080/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "type": "fulltext", "limit": 10}'
```

---

## 📚 API Quick Reference

### Search
```bash
# POST search
curl -X POST /api/v1/search -d '{
  "query": "authentication",
  "type": "hybrid",
  "project_id": "uuid",
  "limit": 20
}'

# GET search
curl "/api/v1/search?q=auth&type=fulltext&limit=10"

# Suggestions
curl "/api/v1/search/suggest?prefix=user&limit=5"
```

### Indexing
```bash
# Index single item
curl -X POST /api/v1/search/index/{item-id}

# Batch index
curl -X POST /api/v1/search/batch-index -d '{
  "item_ids": ["id1", "id2", "id3"]
}'

# Full reindex
curl -X POST /api/v1/search/reindex

# Delete from index
curl -X DELETE /api/v1/search/index/{item-id}
```

### Monitoring
```bash
# Statistics
curl /api/v1/search/stats

# Health check
curl /api/v1/search/health
```

---

## 🖥️ CLI Quick Reference

### Search
```bash
# Basic search
trace search query "authentication"

# Vector search
trace search query "user login" --type vector

# Hybrid search with filters
trace search query "bug" \
  --type hybrid \
  --project abc-123 \
  --item-types feature,task \
  --status todo,in_progress \
  --limit 50

# JSON output
trace search query "api" --json
```

### Suggestions
```bash
# Get autocomplete
trace search suggest "auth"
trace search suggest "user" --project abc-123 --limit 10
```

### Indexing
```bash
# Index single item
trace search index <item-id>

# Batch index
trace search batch-index <id1> <id2> <id3>

# Full reindex
trace search reindex --yes

# Delete from index
trace search delete-index <item-id>
```

### Monitoring
```bash
# View stats
trace search stats

# Health check
trace search health
```

---

## 🔍 Search Type Comparison

| Feature | fulltext | vector | hybrid |
|---------|----------|--------|--------|
| **Speed** | ⚡⚡⚡ Fast (1-10ms) | ⚡⚡ Medium (10-50ms) | ⚡ Slower (20-100ms) |
| **Accuracy** | Good for exact matches | Best for semantic | Best overall |
| **Setup** | ✅ Ready | ⚠️ Needs embeddings | ⚠️ Needs embeddings |
| **Cost** | Free | API costs | API costs |
| **Use Case** | Keywords | Concepts | General purpose |

**Examples:**
- **fulltext:** "authentication" finds "User Authentication System"
- **vector:** "login flow" finds "User Authentication System" (semantic match)
- **hybrid:** Best of both worlds

---

## 🛠️ Common Tasks

### Add Embedding Service (Local - Free)

**1. Create Python service:**
```python
# embedding_service.py
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify

app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

@app.route('/embed', methods=['POST'])
def embed():
    text = request.json['text']
    embedding = model.encode(text).tolist()
    return jsonify({'embedding': embedding})

if __name__ == '__main__':
    app.run(port=5001)
```

**2. Update Go code:**
```go
// backend/internal/search/indexer.go
func (idx *Indexer) generateEmbedding(text string) (string, error) {
    reqBody, _ := json.Marshal(map[string]string{"text": text})

    resp, err := http.Post("http://localhost:5001/embed",
        "application/json", bytes.NewBuffer(reqBody))
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    var result struct {
        Embedding []float64 `json:"embedding"`
    }
    json.NewDecoder(resp.Body).Decode(&result)

    embeddingJSON, _ := json.Marshal(result.Embedding)
    return string(embeddingJSON), nil
}
```

**3. Start services:**
```bash
# Terminal 1: Embedding service
pip install sentence-transformers flask
python embedding_service.py

# Terminal 2: TraceRTM backend
cd backend && go run main.go
```

### Add Redis Caching

**1. Update search.go:**
```go
type SearchEngine struct {
    pool  *pgxpool.Pool
    cache *cache.RedisCache
}

func (s *SearchEngine) Search(ctx context.Context, req *SearchRequest) (*SearchResponse, error) {
    // Generate cache key
    cacheKey := fmt.Sprintf("search:%s:%s:%s", req.Type, req.ProjectID, req.Query)

    // Check cache
    if s.cache != nil {
        if cached, err := s.cache.Get(ctx, cacheKey); err == nil {
            var response SearchResponse
            json.Unmarshal([]byte(cached), &response)
            return &response, nil
        }
    }

    // Execute search (existing code)
    response := /* ... */

    // Cache result
    if s.cache != nil {
        data, _ := json.Marshal(response)
        s.cache.Set(ctx, cacheKey, string(data), 5*time.Minute)
    }

    return response, nil
}
```

**2. Invalidate on updates:**
```go
// In item handler
func (h *ItemHandler) UpdateItem(c echo.Context) error {
    // ... update item

    // Clear search cache
    pattern := fmt.Sprintf("search:*:%s:*", item.ProjectID)
    h.cache.Delete(c.Request().Context(), pattern)

    return c.JSON(200, item)
}
```

### Optimize Performance

**Database:**
```sql
-- Rebuild indexes
REINDEX INDEX idx_items_search_vector;
REINDEX INDEX idx_items_embedding;

-- Update statistics
ANALYZE items;

-- Tune PostgreSQL
SET work_mem = '256MB';
SET max_parallel_workers_per_gather = 4;
```

**Application:**
```go
// Increase pool size
pool.Config().MaxConns = 20
pool.Config().MinConns = 5

// Add query timeout
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
```

---

## 🐛 Troubleshooting

### No search results

```bash
# Check if items are indexed
curl /api/v1/search/stats

# Check extensions
curl /api/v1/search/health

# Manually trigger indexing
curl -X POST /api/v1/search/reindex

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM items WHERE search_vector IS NOT NULL;"
```

### Slow searches

```sql
-- Check index usage
EXPLAIN ANALYZE
SELECT * FROM items
WHERE search_vector @@ plainto_tsquery('english', 'authentication');

-- Rebuild indexes if needed
REINDEX INDEX idx_items_search_vector;
ANALYZE items;
```

### Vector search not working

```bash
# Check pgvector extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Check embeddings
psql $DATABASE_URL -c "SELECT COUNT(*) FROM items WHERE embedding IS NOT NULL;"

# Check embedding service
curl -X POST http://localhost:5001/embed -d '{"text": "test"}'
```

### Indexer issues

```bash
# Check stats
curl /api/v1/search/stats

# Check logs
# Look for "Indexer stats:" messages

# Restart indexer
# Restart the backend server
```

---

## 📊 Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Search latency | <100ms | Check response `duration` field |
| Indexing rate | >100 items/sec | `curl /api/v1/search/stats` |
| Cache hit rate | >70% | Redis INFO stats |
| Error rate | <1% | Monitor `failed_jobs` in stats |
| Queue size | <100 | Monitor `queue_size` in stats |

---

## 🔐 Security Checklist

- [ ] Add authentication to search endpoints
- [ ] Implement project-based access control
- [ ] Add rate limiting (already available in middleware)
- [ ] Sanitize search queries (prevent SQL injection)
- [ ] Audit log search queries (for compliance)
- [ ] Validate project_id in requests
- [ ] Add CORS restrictions

---

## 📈 Monitoring

### Key Metrics

```bash
# Indexer health
watch -n 5 'curl -s http://localhost:8080/api/v1/search/stats | jq'

# Search latency
curl -w "@curl-format.txt" http://localhost:8080/api/v1/search?q=test

# Database queries
psql $DATABASE_URL -c "SELECT * FROM pg_stat_statements WHERE query LIKE '%search_vector%';"
```

### Alerts

```yaml
# Prometheus alerts
groups:
  - name: search
    rules:
      - alert: HighSearchLatency
        expr: search_duration_seconds{quantile="0.95"} > 0.5

      - alert: IndexerQueueFull
        expr: search_indexer_queue_size > 900

      - alert: HighIndexerErrorRate
        expr: rate(search_indexer_failed_jobs[5m]) > 0.1
```

---

## 🚀 Next Steps

### Week 1: Get It Working
- [ ] Activate routes (30 min)
- [ ] Fix test errors (1 hour)
- [ ] Add local embeddings (4 hours)
- [ ] Run integration tests (1 hour)

### Week 2: Make It Fast
- [ ] Implement Redis caching (3 hours)
- [ ] Load testing (2 hours)
- [ ] Performance tuning (2 hours)

### Week 3: Make It Better
- [ ] Add analytics (4 hours)
- [ ] Implement BM25 ranking (8 hours)
- [ ] Add boolean operators (4 hours)

---

## 📖 Further Reading

- **Documentation:** `backend/internal/search/README.md`
- **API Reference:** `/api/v1/search` endpoints
- **Tests:** `backend/internal/search/search_test.go`
- **PostgreSQL FTS:** https://www.postgresql.org/docs/current/textsearch.html
- **pgvector:** https://github.com/pgvector/pgvector
- **sentence-transformers:** https://www.sbert.net/

---

**Need Help?**
- Check the detailed docs: `SEARCH_IMPLEMENTATION_SUMMARY.md`
- Technical deep dive: `SEARCH_TECHNICAL_REPORT.md`
- Backend README: `backend/internal/search/README.md`
