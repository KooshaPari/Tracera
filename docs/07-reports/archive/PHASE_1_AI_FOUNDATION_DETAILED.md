# Phase 1: AI Foundation - Detailed Implementation (Weeks 1-2, 80 hours)

## Overview

Complete AI infrastructure setup: embeddings, vector search, RAG, and function calling.

## Week 1: Embeddings & Vector Search (40 hours)

### Day 1-2: Setup & Configuration (16 hours)

**Tasks:**
1. Get VoyageAI API key (free tier: 200M tokens/month)
2. Add environment variables:
   ```
   VOYAGE_API_KEY=your_key
   VOYAGE_MODEL=voyage-3.5
   VOYAGE_DIMENSIONS=1024
   RERANK_ENABLED=true
   RERANK_MODEL=rerank-2.5
   INDEXER_ENABLED=true
   INDEXER_WORKERS=3
   INDEXER_BATCH_SIZE=128
   INDEXER_POLL_INTERVAL=30s
   ```
3. Verify pgvector extension in PostgreSQL
4. Verify embedding column exists in items table
5. Verify IVFFlat index created

**Code Changes:**
- Update `backend/internal/config/config.go` with embedding config
- Update `backend/internal/infrastructure/infrastructure.go` to initialize embeddings
- Update `backend/main.go` to start indexer

### Day 3-4: Indexing (16 hours)

**Tasks:**
1. Call `POST /api/v1/search/reindex` to start indexing
2. Monitor progress with `GET /api/v1/search/stats`
3. Verify all items have embeddings
4. Test with sample queries
5. Optimize batch size if needed

**Expected Results:**
- All items indexed with embeddings
- Response time <100ms
- Reranking working

### Day 5: Testing & Validation (8 hours)

**Tasks:**
1. Test full-text search
2. Test vector search
3. Test hybrid search
4. Test fuzzy search
5. Test phonetic search
6. Verify response times
7. Write integration tests

## Week 2: RAG & Function Calling (40 hours)

### Day 1-2: RAG Service (16 hours)

**Tasks:**
1. Create `backend/internal/rag/rag.go`:
   - AnalyzeRequirement() method
   - BuildContext() from Neo4j
   - GenerateAnalysis() with Claude
   - Add prompt caching

2. Create `backend/internal/handlers/rag_handler.go`:
   - POST /api/v1/rag/analyze
   - POST /api/v1/rag/suggest-links
   - POST /api/v1/rag/generate-tests
   - GET /api/v1/rag/status

3. Implement prompt caching:
   - Cache requirement templates
   - Cache analysis patterns
   - Cache relationship rules

### Day 3-4: Function Calling (16 hours)

**Tasks:**
1. Create `backend/internal/agents/tools.go`:
   - Define requirement tools
   - Define search tools
   - Define link tools
   - Define analysis tools

2. Implement tool handlers:
   - Search requirements
   - Link requirements
   - Analyze requirement
   - Generate suggestions

3. Integrate with Claude API:
   - Function calling
   - Tool use
   - Result processing

### Day 5: Testing & Integration (8 hours)

**Tasks:**
1. Write unit tests for RAG service
2. Write integration tests for handlers
3. Test function calling
4. Test error handling
5. Test performance
6. Document API endpoints

## Implementation Details

### Embeddings Configuration

```go
type EmbeddingConfig struct {
    Provider    string // "voyage"
    APIKey      string
    Model       string // "voyage-3.5"
    Dimensions  int    // 1024
    RerankerEnabled bool
    RerankerModel string // "rerank-2.5"
}
```

### RAG Service Interface

```go
type RAGService interface {
    AnalyzeRequirement(ctx context.Context, itemID string) (*Analysis, error)
    SuggestLinks(ctx context.Context, itemID string) ([]*Link, error)
    GenerateTests(ctx context.Context, itemID string) ([]*Test, error)
}
```

### Function Calling Tools

```go
type Tool struct {
    Name        string
    Description string
    Parameters  map[string]interface{}
    Handler     func(context.Context, map[string]interface{}) (interface{}, error)
}
```

## Success Criteria

✅ Semantic search working (<100ms)
✅ RAG analysis working (<2s)
✅ Function calling working
✅ All tests passing
✅ Costs tracked
✅ Documentation complete

## Expected Results

- **Search Performance:** 500ms → 50ms (10x faster)
- **AI Accuracy:** 70% → 90% (+20%)
- **Cost:** $10k/mo → $5k/mo (50% savings)
- **Scalability:** 1k req/s → 10k req/s (10x)

## Troubleshooting

**Issue:** Embeddings not generating
- Check VoyageAI API key
- Check rate limits
- Check batch size

**Issue:** Search slow
- Check IVFFlat index
- Check batch size
- Check reranking

**Issue:** RAG not working
- Check Claude API key
- Check context building
- Check prompt caching

## Next Phase

After Phase 1 complete:
- Move to Phase 2: Event Sourcing & CQRS
- Implement audit trail
- Separate read/write models

