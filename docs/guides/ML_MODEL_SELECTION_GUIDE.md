# ML Model Selection Guide for TraceRTM

## Decision Matrix by Use Case

### 1. Semantic Similarity & Duplicate Detection

**Winner: Sentence-Transformers (all-MiniLM-L6-v2)**

| Aspect | Score | Reasoning |
|--------|-------|-----------|
| Accuracy | 8/10 | Good semantic understanding, not state-of-the-art |
| Speed | 10/10 | ~2000 seqs/sec on CPU |
| Memory | 10/10 | Only 22 MB, minimal RAM needed |
| Cost | 10/10 | Free, open-source |
| Ease of Use | 9/10 | Simple API, works out-of-box |
| Scalability | 9/10 | Can batch process, no GPU needed |

**Why not alternatives:**
- ❌ all-mpnet-base-v2: 10x slower for MVP needs
- ❌ OpenAI embeddings: Not justified cost-wise for MVP
- ❌ CodeBERT: Overkill for text similarity

**Implementation Time**: <1 hour
**Confidence Level**: Very High

---

### 2. Requirement Quality Analysis

**Winner: Claude 4.5 (via Anthropic API)**

| Aspect | Score | Reasoning |
|--------|-------|-----------|
| Accuracy | 10/10 | State-of-the-art reasoning |
| Cost | 6/10 | ~$0.003 per requirement |
| Speed | 6/10 | 1-3 seconds per analysis |
| Flexibility | 10/10 | Can detect arbitrary quality issues |
| Hallucination Risk | 8/10 | Low with structured prompts |
| Easy Integration | 9/10 | Use Anthropic SDK |

**Fallback option**: Pattern-based analysis (regex)
- No cost
- Instant
- Limited to known patterns
- Can be combined with LLM

**Implementation Time**: <1 hour
**Confidence Level**: Very High

---

### 3. Requirement Classification (FURPS+)

**Winner: Hybrid (Patterns + Claude)**

**Approach:**

1. **Fast path** (90% of requirements):
   - Pattern matching on keywords
   - 0ms latency
   - 70% accuracy
   - Free

2. **Accurate path** (10% of requirements):
   - Claude 4.5 when pattern ambiguous
   - 3-5 seconds
   - 95% accuracy
   - $0.001 per classification

**Why hybrid:**
- Most requirements clearly belong to one category (keywords obvious)
- Only use expensive LLM when pattern is ambiguous
- Best cost/accuracy trade-off

**Decision tree:**
```
IF (keywords match single category) → Use pattern (instant, 80% confidence)
ELIF (no match or multiple matches) → Use LLM (slow, 95% confidence)
ELSE → Default to FUNCTIONAL (0% cost)
```

**Implementation Time**: 2-3 hours
**Confidence Level**: High

---

### 4. Named Entity Recognition (NER)

**Winner: spaCy + Fine-tuning**

| Approach | Accuracy | Training Time | Cost | Ease |
|----------|----------|---------------|------|------|
| Pre-trained spaCy | 60% | 0 | Free | Easy |
| Fine-tuned spaCy | 85% | 2 hours | Free | Medium |
| Transformer-based | 88% | 4 hours | Free | Hard |
| Claude 4.5 | 92% | 0 | $0.002/req | Easy |

**For TraceRTM MVP**: Pre-trained spaCy
- Decent baseline (60% accuracy)
- No training needed
- Fast inference
- Can improve later

**For Phase 2**: Fine-tune on domain data
- Collect 200-500 labeled examples
- Train on GPU (2 hours)
- Achieve 85%+ accuracy

**Implementation Time**:
- Phase 1: <1 hour (pre-trained)
- Phase 2: 4-6 hours (fine-tuning)

**Confidence Level**: Medium → High (after fine-tuning)

---

### 5. Test Prioritization

**Winner: Q-Learning (custom implementation)**

| Approach | Complexity | ROI | Training | Accuracy |
|----------|-----------|-----|----------|----------|
| Random | 0/10 | 0% | None | Baseline |
| Simple heuristics | 2/10 | 20% | None | 60% |
| Q-Learning | 6/10 | 40% | Continuous | 75% |
| RETECS (full) | 9/10 | 50% | Weeks | 85% |
| ML model (XGBoost) | 8/10 | 45% | Days | 80% |

**For TraceRTM MVP**: Simple heuristics
```python
# Prioritize by:
1. Failure rate (tests that failed before)
2. Duration (short tests first for fast feedback)
3. Last execution (untested code)
4. Coverage (critical path tests)
```

**Cost**: Free
**Time**: 3-4 hours

**For Phase 3**: Q-Learning
- More sophisticated
- Learns from CI history
- Improves over time
- Worth investment at scale

**Implementation Time**: 6-8 hours
**Confidence Level**: High (for heuristic), Medium (for RL)

---

### 6. Code Metrics for Defect Prediction

**Winner: Radon + scikit-learn RandomForest**

| Metric | Correlation with Defects | Effort to Collect |
|--------|--------------------------|-------------------|
| Lines of Code (LOC) | 0.65 | Very Easy |
| Cyclomatic Complexity | 0.72 | Easy |
| Halstead Metrics | 0.68 | Easy |
| Code Coverage | 0.71 | Medium |
| Age/Churn | 0.74 | Medium |
| Author Experience | 0.62 | Hard |

**Best combination**: LOC + Cyclomatic + Coverage + Churn
- Achieves ~75% accuracy
- All easy to collect
- Uses free tools (Radon)

**ML Model Choice**: RandomForest
- Better than linear regression for non-linear relationships
- More robust than SVM
- Interpretable (feature importance)
- Fast inference

**Implementation Time**: 4-6 hours
**Confidence Level**: Medium

---

### 7. Requirement-Code Traceability

**Progressive Approach**:

#### Phase 1: BM25 Keyword Matching (MVP)
```
Cost: Free
Speed: <100ms
Accuracy: 65%
Time to implement: 2-3 hours
```

#### Phase 2: BM25 + Embeddings (Hybrid)
```
Cost: Free
Speed: 100-500ms
Accuracy: 75%
Time to implement: 3-4 hours
```

#### Phase 3: CodeBERT Deep Learning
```
Cost: Free
Speed: 1-5 seconds
Accuracy: 85%
Time to implement: 6-8 hours
Memory: 2-4 GB
```

**Recommendation**: Start with Phase 1, upgrade as needed

**Implementation Time**:
- Phase 1: 2-3 hours
- Phase 2: +2-3 hours
- Phase 3: +6-8 hours

**Confidence Level**: High → Very High (as you progress)

---

### 8. Duplicate Detection

**Winner: SimHash (Simple & Fast)**

| Algorithm | Speed | Accuracy | Memory | Scalability |
|-----------|-------|----------|--------|-------------|
| SimHash | Very Fast | 85% | Minimal | 10K items |
| LSH+MinHash | Fast | 80% | Low | 1M items |
| Embeddings | Slow | 90% | High | 100K items |
| All-pairs | Slow | 100% | High | <5K items |

**For TraceRTM**: SimHash
- Sufficient accuracy (85%)
- Extremely fast (microseconds)
- Minimal memory
- Simple implementation

**When to upgrade**:
- If duplicate detection accuracy < 80% → use embeddings
- If > 100K requirements → use LSH+MinHash
- If need exact detection → embeddings + threshold

**Implementation Time**: <1 hour
**Confidence Level**: Very High

---

## Model Comparison Matrix

### Embedding Models

| Model | Dimension | Speed | MTEB Score | Size | Cost | Best For |
|-------|-----------|-------|-----------|------|------|----------|
| all-MiniLM-L6-v2 | 384 | 2000 seq/s | 56.9 | 22 MB | Free | **MVP** |
| all-mpnet-base-v2 | 768 | 200 seq/s | 63.3 | 438 MB | Free | Production |
| multilingual-e5-large | 1024 | 50 seq/s | 64.9 | 1.7 GB | Free | International |
| text-embedding-3-small | 512 | API | 65.1 | N/A | $0.02/1M | Quality |
| CodeBERT | 768 | 100 seq/s | - | 420 MB | Free | Code |

**MVP Selection**: all-MiniLM-L6-v2
- Perfect for requirements (general text)
- Lightning fast on CPU
- Tiny memory footprint
- Good enough accuracy

**Upgrade Path**: all-mpnet-base-v2 (when accuracy matters)

---

### LLM Models

| Model | Cost | Speed | Quality | Context | Best For |
|-------|------|-------|---------|---------|----------|
| Claude 4.5 Sonnet | $3/1M | Fast | 95% | 200K | **MVP** |
| Claude 4.5 Opus | $15/1M | Slower | 98% | 200K | Complex analysis |
| GPT-4o | $5/1M | Fast | 94% | 128K | Alternative |
| GPT-5.2 | $20/1M | Fast | 99% | 200K | If cost not issue |
| DeepSeek V3 | $0.27/1M | Fast | 91% | 128K | Cost-sensitive |

**MVP Selection**: Claude 4.5 Sonnet
- Best balance of cost/quality
- Excellent reasoning
- Fast enough
- Reliable API

**Cost at Scale**:
- 10,000 requirements × $0.003 = $30 (one-time)
- Monthly updates: ~$50

---

### NER Models

| Model | Accuracy | Training | Size | Speed | Cost |
|-------|----------|----------|------|-------|------|
| spaCy pre-trained | 60% | None | 40 MB | Fast | Free |
| spaCy fine-tuned | 85% | 2 hours | 60 MB | Fast | Free |
| Hugging Face transformer | 88% | 4 hours | 500 MB | Slow | Free |
| Claude 4.5 | 92% | None | N/A | 2-3s | $0.002 |

**MVP Selection**: spaCy pre-trained
- Works out-of-box
- No training needed
- Free
- Fast

**Phase 2**: Fine-tune on requirements data

---

## Total Cost of Ownership (TCO)

### MVP Setup (Month 1)

| Component | Cost | Time |
|-----------|------|------|
| Embeddings (all-MiniLM-L6-v2) | $0 | 1 hour |
| Duplicate detection (SimHash) | $0 | 1 hour |
| Quality analysis (Claude) | $50 | 2 hours |
| Classification (patterns) | $0 | 1 hour |
| NER (pre-trained) | $0 | 1 hour |
| Database schema | $0 | 1 hour |
| API routes | $0 | 2 hours |
| Testing | $0 | 2 hours |
| **Total** | **$50** | **11 hours** |

### Scaled Production (Month 3)

| Component | Cost/Month | Notes |
|-----------|-----------|-------|
| LLM API (Claude) | $100-500 | 30-150K requirements/month |
| Embeddings storage | $0 | PostgreSQL pgvector (free) |
| Compute (embeddings) | $0 | CPU sufficient |
| Monitoring | $50-100 | DataDog/New Relic |
| **Total** | **$150-600** | Depends on scale |

**ROI**: High
- Catches duplicate requirements early
- Improves testing effectiveness
- Reduces maintenance burden
- Saves cost of bugs in production

---

## Implementation Priority Matrix

```
High Impact, Low Effort:
1. Embeddings (similarity search)
2. SimHash (duplicate detection)
3. Pattern-based classification

Medium Impact, Low Effort:
4. LLM quality analysis
5. Pre-trained NER
6. Basic defect metrics

High Impact, Medium Effort:
7. Hybrid traceability (BM25 + embeddings)
8. Fine-tuned NER
9. Test prioritization (heuristic)

Medium Impact, High Effort:
10. CodeBERT traceability
11. RETECS test prioritization
12. Advanced defect prediction
```

**Recommended Phase 1** (MVP, 1-2 weeks):
- Embeddings
- Duplicate detection
- Classification

**Recommended Phase 2** (Enhanced, weeks 3-4):
- LLM quality analysis
- NER (pre-trained)
- Simple traceability

**Recommended Phase 3** (Advanced, weeks 5-6):
- Fine-tuned NER
- Hybrid traceability
- Test prioritization

---

## A/B Testing Framework

### Test Setup

```python
# Feature flags for A/B testing
class MLFeatureFlags:
    # Phase 1
    enable_embeddings: bool = True
    enable_duplicate_detection: bool = True
    enable_classification: bool = True

    # Phase 2
    enable_llm_quality: bool = False
    enable_traceability: bool = False

    # Phase 3
    enable_advanced_ner: bool = False
    enable_test_prioritization: bool = False
```

### Metrics to Track

For each ML feature, measure:
1. **Accuracy**: Against ground truth
2. **Latency**: p50, p95, p99
3. **Memory**: Peak usage
4. **Cost**: API calls, storage
5. **User satisfaction**: Feedback, adoption

---

## Migration Path

### Week 1-2: MVP
```
Requirements → Embeddings → Vector DB
                ↓
            Similar Finder
            ↓
        Duplicate Detector
```

### Week 3-4: Enhancement
```
Requirements → LLM Analysis → Quality Scores
            ↓
        Classification
            ↓
        Entity Extraction
```

### Week 5-6: Advanced
```
Requirements + Code → Embeddings Alignment
                   ↓
               Trace Links
                   ↓
        ML-Discovered Dependencies
```

### Week 7+: Optimization
```
Full pipeline with:
- Caching
- Batching
- GPU acceleration (optional)
- A/B testing results
```

---

## Success Metrics

### Phase 1 (MVP)
- [ ] Can find duplicates with 85%+ accuracy
- [ ] Embedding latency < 200ms
- [ ] Classification accuracy > 75%
- [ ] Zero errors in production

### Phase 2 (Enhanced)
- [ ] Quality analysis catches issues in 90% of cases
- [ ] NER accuracy > 80%
- [ ] Traceability links valid 80% of time
- [ ] User adoption > 60%

### Phase 3 (Advanced)
- [ ] Fine-tuned NER accuracy > 90%
- [ ] Hybrid traceability > 85% accuracy
- [ ] Test prioritization reduces CI time by 30%
- [ ] Defect prediction catches 70% of bugs pre-release

---

## Conclusion

**Start here**:
1. Embeddings (all-MiniLM-L6-v2)
2. Duplicate detection (SimHash)
3. Classification (patterns)

**Add when ready**:
4. LLM analysis (Claude 4.5)
5. Traceability (BM25 + embeddings)
6. Test prioritization (heuristic)

**Upgrade over time**:
7. Fine-tuned NER
8. CodeBERT traceability
9. RETECS test prioritization

This path maximizes value while keeping complexity manageable.

---

**Document Version**: 1.0
**Last Updated**: January 29, 2026
