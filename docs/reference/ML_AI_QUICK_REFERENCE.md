# ML/AI for Requirements & Testing - Quick Reference Guide

## At a Glance

### Best Models by Use Case

| Use Case | Model | Library | Speed | Accuracy | Cost |
|----------|-------|---------|-------|----------|------|
| Requirement Quality | Claude 4.5 | anthropic | Slow | 90% | $$ |
| Embeddings/Similarity | all-MiniLM-L6-v2 | sentence-transformers | Fast | 80% | Free |
| Duplicate Detection | SimHash | simhash | Very Fast | 85% | Free |
| Entity Extraction | spaCy (fine-tuned) | spacy | Fast | 88% | Free |
| Requirement Classification | Claude 4.5 | anthropic | Slow | 92% | $ |
| Test Prioritization | Q-Learning | custom | Fast | 75% | Free |
| Code Traceability | BM25 + Embeddings | hybrid | Fast | 75% | Free |
| High-Accuracy Traceability | CodeBERT | transformers | Slow | 85% | Free |

### Install Command

```bash
# Core ML/AI dependencies
pip install sentence-transformers scikit-learn spacy radon pgvector

# Optional: Advanced features
pip install transformers torch datasketch rank-bm25

# TraceRTM: Update pyproject.toml with [ml] extras
bun install  # After updating pyproject.toml
pip install -e ".[ml]"  # Dev installation
```

---

## Quick Implementation Templates

### 1. Embeddings (5 minutes)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Your requirement text")

# Find similar
query_emb = model.encode("Find similar to this")
similarity = model.similarity(query_emb, embedding)[0][0]
```

### 2. LLM Quality Analysis (10 minutes)

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key="sk-ant-...")

message = await client.messages.create(
    model="claude-opus-4-20250102",
    max_tokens=500,
    messages=[{
        "role": "user",
        "content": f"Analyze this requirement: {requirement_text}"
    }]
)

print(message.content[0].text)
```

### 3. Duplicate Detection (5 minutes)

```python
from simhash import SimHash

hash1 = SimHash("User should create items")
hash2 = SimHash("User must create items")
distance = hash1.distance(hash2)  # 0-64

if distance <= 5:  # Very similar
    print("Potential duplicate")
```

### 4. Entity Extraction (15 minutes)

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("User should create new items")

for ent in doc.ents:
    print(f"{ent.text}: {ent.label_}")
```

### 5. Defect Risk (10 minutes)

```python
from radon.complexity import cc_visit

code = open("file.py").read()
complexity = cc_visit(code)

if complexity > 15:
    print("High complexity - defect risk!")
```

---

## Integration with TraceRTM

### Add to Services

```python
# src/tracertm/services/ml_requirement_analyzer.py

class MLRequirementAnalyzer:
    """All-in-one requirement analysis."""

    async def analyze(self, requirement_text: str) -> dict:
        """Run all ML analyses."""
        return {
            "quality": await self.quality_check(requirement_text),
            "duplicates": await self.find_duplicates(requirement_text),
            "category": await self.classify(requirement_text),
            "entities": await self.extract_entities(requirement_text),
            "risks": await self.predict_risks(requirement_text),
        }
```

### Add to API

```python
# src/tracertm/api/routers/ml_analysis.py

@router.post("/projects/{project_id}/requirements/{req_id}/analyze")
async def analyze_requirement(
    project_id: str,
    req_id: str,
    session: AsyncSession
) -> dict:
    """Comprehensive ML analysis of requirement."""
    analyzer = MLRequirementAnalyzer()
    item = await get_item(session, req_id)
    return await analyzer.analyze(f"{item.title} {item.description}")
```

### Update Frontend

```typescript
// frontend/apps/web/src/hooks/useMLAnalysis.ts

export function useMLAnalysis(requirementId: string) {
  return useQuery({
    queryKey: ['ml-analysis', requirementId],
    queryFn: () => api.post(
      `/projects/${projectId}/requirements/${requirementId}/analyze`
    ),
  });
}
```

---

## Performance Expectations

### Latency (p95)

| Operation | Time | Notes |
|-----------|------|-------|
| Single embedding | 50-200ms | Depends on model size |
| LLM analysis | 1-3s | API call + reasoning |
| Duplicate detection (100 items) | 10-50ms | Very fast |
| NER extraction | 100-500ms | Per requirement |
| Classification | 500ms-2s | LLM-based |
| Code metrics | 10-100ms | Per file |

### Memory Usage

| Model | Size | RAM | GPU |
|-------|------|-----|-----|
| all-MiniLM-L6-v2 | 22 MB | ~200 MB | Not needed |
| all-mpnet-base-v2 | 438 MB | ~1 GB | 4 GB (optional) |
| CodeBERT | 420 MB | ~2 GB | 8 GB recommended |
| spaCy en_core | 40 MB | ~300 MB | Not needed |

---

## Cost Analysis

### LLM Costs (Claude API)

- **Quality analysis**: ~0.3¢ per requirement (input tokens)
- **Classification**: ~0.1¢ per requirement
- **Entity extraction**: ~0.2¢ per requirement

**Example**: 1,000 requirements
- Quality analysis: $3
- Classification: $1
- Total: $4 (one-time initial analysis)

### Infrastructure Costs

- **Embeddings storage**: pgvector (free, included with PostgreSQL)
- **Models**: All free (open source)
- **Compute**: Minimal (CPU sufficient for most tasks)

---

## Testing Checklist

- [ ] Unit tests for embedding generation
- [ ] Integration tests with database
- [ ] Performance benchmarks
- [ ] Accuracy validation on test data
- [ ] End-to-end pipeline testing
- [ ] Error handling tests
- [ ] Concurrency tests (async)

---

## Troubleshooting

### Slow Embeddings
- **Problem**: Embedding generation taking >500ms
- **Solution**: Use smaller model (all-MiniLM-L6-v2) or batch requests

### Low Similarity Scores
- **Problem**: Semantically similar items getting low scores
- **Solution**: Use all-mpnet-base-v2 (better quality) or LLM analysis

### Duplicate Detection False Positives
- **Problem**: Unrelated items flagged as duplicates
- **Solution**: Increase SimHash threshold (5 → 10)

### Memory Issues
- **Problem**: Out of memory loading models
- **Solution**: Load models on-demand, cache in singleton

### LLM API Errors
- **Problem**: Rate limiting or API failures
- **Solution**: Add retry logic, fallback to pattern-based analysis

---

## Recommended Implementation Order

### Week 1: MVP
1. Add embeddings service (all-MiniLM-L6-v2)
2. Duplicate detection (SimHash)
3. Store embeddings in pgvector

### Week 2: Enhancement
1. LLM quality analysis (Claude)
2. Basic classification (patterns)
3. Simple NER (spaCy pre-trained)

### Week 3: Advanced
1. Fine-tuned NER (domain-specific)
2. Traceability linking (BM25 + embeddings)
3. Defect prediction (code metrics)

### Week 4: Production
1. Model caching and optimization
2. Performance monitoring
3. API documentation
4. User-facing UI

---

## Common Pitfalls to Avoid

1. **Not caching models** → Load models once, reuse
2. **Using wrong dimension embeddings** → Check model specs
3. **Synchronous embedding operations** → Always use async
4. **Not handling LLM timeouts** → Add retry logic
5. **Storing full embeddings in logs** → Only store IDs
6. **No validation of model outputs** → Always validate

---

## Next Steps

1. Read full research document: `ML_AI_RESEARCH_REQUIREMENTS_TESTING.md`
2. Choose starting use case (likely embeddings + duplicates)
3. Create service stubs in codebase
4. Build tests first (TDD)
5. Integrate with existing services
6. Add API endpoints
7. Create frontend components
8. Monitor and iterate

---

## Resources

- **Sentence Transformers**: https://www.sbert.net/
- **spaCy Training**: https://spacy.io/usage/training
- **Radon Docs**: https://radon.readthedocs.io/
- **Claude API**: https://docs.anthropic.com/
- **scikit-learn**: https://scikit-learn.org/

---

**Quick Start**: Begin with embeddings for MVP, add LLM analysis next phase, scale with specialized models.
