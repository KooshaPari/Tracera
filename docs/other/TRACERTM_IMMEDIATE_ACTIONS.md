# TraceRTM: Immediate Actions (This Week)

## 🎯 Focus: AI Integration - Week 1

### Action 1: Enable pgvector (30 min)
```sql
-- In backend/migrations/
CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE items ADD COLUMN embedding vector(1536);
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### Action 2: Add Embedding Generation (1 hr)
```python
# cli/tracertm/ai/embeddings.py
from openai import OpenAI

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()
    
    def embed_requirement(self, text: str) -> list:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
```

### Action 3: Add Semantic Search Endpoint (1.5 hrs)
```go
// backend/internal/handlers/search.go
func (h *Handler) SemanticSearch(c echo.Context) error {
    query := c.QueryParam("q")
    embedding := h.embeddingService.Embed(query)
    
    results, err := h.db.Query(`
        SELECT id, title, content, 1 - (embedding <=> $1) as similarity
        FROM items
        WHERE 1 - (embedding <=> $1) > 0.7
        ORDER BY embedding <=> $1
        LIMIT 10
    `, embedding)
    
    return c.JSON(200, results)
}
```

### Action 4: Setup Hybrid RAG (2 hrs)
```python
# cli/tracertm/ai/rag.py
from langchain.chains import RetrievalQA
from langchain.llms import ChatAnthropic

class HybridRAG:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet")
        self.retriever = SemanticRetriever()
    
    def analyze_requirement(self, requirement: str) -> dict:
        # 1. Retrieve similar requirements
        similar = self.retriever.search(requirement)
        
        # 2. Use fine-tuned model for analysis
        analysis = self.llm.predict(
            f"Analyze this requirement: {requirement}\n"
            f"Similar requirements: {similar}"
        )
        
        return {"analysis": analysis, "similar": similar}
```

### Action 5: Add Prompt Caching (30 min)
```python
# Use Claude API prompt caching
response = client.messages.create(
    model="claude-3-5-sonnet",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are a requirements engineer"
        },
        {
            "type": "text",
            "text": LARGE_CONTEXT,
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": "Analyze this requirement..."}]
)
```

## 📋 Checklist

- [ ] Enable pgvector extension
- [ ] Add embedding column to items
- [ ] Create vector index
- [ ] Implement embedding service
- [ ] Add semantic search endpoint
- [ ] Setup Hybrid RAG
- [ ] Add prompt caching
- [ ] Test end-to-end
- [ ] Update documentation

## 🔗 Related Files

- Backend: `backend/internal/handlers/search.go`
- CLI: `cli/tracertm/ai/`
- Database: `backend/migrations/`
- Tests: `tests/backend/test_semantic_search.py`

## ⏱️ Timeline

- **Monday:** pgvector setup + embedding service
- **Tuesday:** Semantic search endpoint
- **Wednesday:** Hybrid RAG implementation
- **Thursday:** Prompt caching + testing
- **Friday:** Documentation + review

## 🎯 Success Criteria

- ✅ Semantic search returns relevant results
- ✅ RAG improves requirement analysis accuracy
- ✅ Prompt caching reduces API costs by 90%
- ✅ All tests pass
- ✅ Documentation updated

---

**Effort:** 5 hours
**Impact:** Very High
**Start:** Today

