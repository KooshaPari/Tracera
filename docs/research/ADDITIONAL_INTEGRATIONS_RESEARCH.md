# Additional Integrations & Infrastructure Deep Dive

**Research Date:** 2025-11-20
**Focus:** Deep patterns for existing infrastructure components + gap analysis

---

## 1. TimescaleDB Advanced Patterns

### Continuous Aggregates (Real-Time Analytics)

```sql
-- Automatic hourly requirement metrics
CREATE MATERIALIZED VIEW requirement_metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 hour', created_at) AS hour,
  project_id,
  COUNT(*) AS total_requirements,
  COUNT(*) FILTER (WHERE status = 'approved') AS approved_count,
  AVG(complexity_score) AS avg_complexity
FROM requirements
GROUP BY hour, project_id;

-- Auto-refresh policy
SELECT add_continuous_aggregate_policy('requirement_metrics_hourly',
  start_offset => INTERVAL '3 hours',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');

-- Query is instant (pre-aggregated)
SELECT * FROM requirement_metrics_hourly
WHERE hour > now() - INTERVAL '7 days';
```

### Compression (90%+ Storage Reduction)

```sql
ALTER TABLE traces SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'requirement_id'
);

SELECT add_compression_policy('traces', INTERVAL '7 days');
```

### MCP Integration

```python
@tool()
async def get_requirement_velocity_trend(project_id: str, days: int = 30):
    """Get requirement creation velocity over time."""
    query = f"""
    SELECT hour, total_requirements
    FROM requirement_metrics_hourly
    WHERE project_id = '{project_id}'
      AND hour > now() - INTERVAL '{days} days'
    ORDER BY hour
    """
    return await db.query(query)
```

---

## 2. Weaviate Vector Search (Semantic Requirements)

### Hybrid Search Pattern

```python
# Combine vector similarity + keyword matching
async def semantic_requirement_search(query: str, project_id: str):
    return await weaviate.query.hybrid(
        query=query,
        alpha=0.75,  # 75% vector, 25% BM25 keyword
        where={
            "path": ["project_id"],
            "operator": "Equal",
            "valueString": project_id
        },
        limit=10
    )
```

### AI-Powered Impact Analysis

```python
@tool()
async def analyze_requirement_change_impact(req_id: str, new_description: str):
    """Use AI to predict impact of requirement change."""

    # Generate embedding for new description
    new_embedding = await openai.embed(new_description)

    # Find semantically similar requirements
    similar = await weaviate.near_vector(new_embedding, limit=20)

    # Check for dependency changes
    current_deps = await db.get_requirement_dependencies(req_id)
    potential_new_deps = [s for s in similar if s["id"] not in current_deps]

    return {
        "potentially_impacted": similar[:10],
        "new_dependencies_suggested": potential_new_deps,
        "risk_level": "high" if len(similar) > 15 else "medium"
    }
```

---

## 3. Temporal.io Workflow Patterns

### Long-Running Approval Workflow

```python
@workflow.defn
class RequirementApprovalWorkflow:
    @workflow.run
    async def run(self, req_id: str, approvers: list[str]):
        """Multi-day approval with reminders."""
        approvals = []

        # Send initial notifications
        await workflow.execute_activity(
            notify_approvers,
            args=[req_id, approvers],
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Wait for approvals (with timeout)
        try:
            async with workflow.timeout(timedelta(days=3)):
                while len(approvals) < len(approvers):
                    # Wait for approval signal
                    approval = await workflow.wait_condition(
                        lambda: self.has_new_approval()
                    )
                    approvals.append(approval)
        except asyncio.TimeoutError:
            # Escalate after 3 days
            await workflow.execute_activity(escalate_approval, args=[req_id])

        if len(approvals) >= len(approvers):
            await workflow.execute_activity(mark_approved, args=[req_id])
            return {"status": "approved", "approvals": approvals}

        return {"status": "timeout", "approvals": approvals}

    @workflow.signal
    async def approve(self, approver: str):
        self.approvals.append(approver)
```

---

## 4. Redis Rate Limiting (Production Pattern)

### Token Bucket Algorithm

```python
# High-performance rate limiting
async def check_rate_limit(
    redis: Redis,
    key: str,
    max_requests: int,
    window_seconds: int
) -> tuple[bool, int]:
    """
    Returns (allowed, remaining_requests)
    """
    now = time.time()

    # Sliding window with sorted set
    async with redis.pipeline(transaction=True) as pipe:
        # Remove old entries
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        # Count current
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiry
        pipe.expire(key, window_seconds)

        _, count, *_ = await pipe.execute()

        allowed = count < max_requests
        remaining = max(0, max_requests - count - 1)

        return allowed, remaining

# MCP middleware
@mcp.middleware
async def rate_limit_middleware(ctx, call_next):
    agent_id = ctx.agent_id
    allowed, remaining = await check_rate_limit(
        redis,
        f"rate_limit:agent:{agent_id}",
        max_requests=1000,
        window_seconds=3600  # 1000 requests/hour
    )

    if not allowed:
        raise ToolError("Rate limit exceeded")

    ctx.response_headers["X-RateLimit-Remaining"] = str(remaining)
    return await call_next(ctx)
```

---

## 5. Multi-Layer Caching

### L1 (In-Memory) + L2 (Redis) + L3 (Database)

```python
from cachetools import TTLCache

class MultiLayerCache:
    def __init__(self):
        self.l1 = TTLCache(maxsize=1000, ttl=60)  # 1 min
        self.l2_ttl = 300  # 5 min in Redis

    async def get(self, key: str):
        # L1: In-memory (fastest)
        if key in self.l1:
            return self.l1[key]

        # L2: Redis
        value = await redis.get(key)
        if value:
            deserialized = json.loads(value)
            self.l1[key] = deserialized  # Populate L1
            return deserialized

        # L3: Database (slowest)
        db_value = await db.get(key)
        if db_value:
            # Populate L2 and L1
            await redis.setex(key, self.l2_ttl, json.dumps(db_value))
            self.l1[key] = db_value

        return db_value

# MCP tool with caching
@tool()
async def get_requirement(req_id: str):
    """Get requirement with multi-layer caching."""
    cache_key = f"requirement:{req_id}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Cache miss: load from database
    req = await db.requirements.get(req_id)
    await cache.set(cache_key, req)

    return req
```

---

## 6. Gap Analysis & Enhancement Areas

### Currently Missing (High Priority)

| Capability | Solution | Effort | Impact |
|------------|----------|--------|--------|
| **Semantic search** | Weaviate integration | Medium | High |
| **Rate limiting** | Redis token bucket | Low | High |
| **API gateway** | Kong/Traefik + auth | High | High |
| **Real-time analytics** | TimescaleDB aggregates | Low | Medium |
| **Workflow versioning** | Temporal patterns | Medium | Medium |
| **Multi-tenant isolation** | PostgreSQL RLS | High | High |
| **Distributed caching** | Redis cluster | Medium | Medium |
| **GraphQL API** | Strawberry/Ariadne | High | Medium |

### Quick Wins (Low Effort, High Impact)

1. **Redis rate limiting** (1-2 days)
2. **TimescaleDB continuous aggregates** (2-3 days)
3. **Multi-layer caching** (3-4 days)
4. **Webhook aggregation service** (1 week)

### Strategic Investments (High Effort, High Impact)

1. **Weaviate semantic search** (2-3 weeks)
2. **Multi-tenant architecture** (3-4 weeks)
3. **API gateway with auth** (2-3 weeks)
4. **GraphQL federation** (4-6 weeks)

---

## 7. Infrastructure Component Deep Dives

### Unleash (Feature Flags)

```python
# Progressive rollout for new trace features
unleash = UnleashClient(url="http://unleash:4242/api")

@tool()
async def get_trace_format(user_id: str):
    if unleash.is_enabled("new-trace-format-v2", {"userId": user_id}):
        return generate_trace_v2()
    return generate_trace_v1()

# Gradual rollout: 0% → 10% → 50% → 100% over 2 weeks
```

### Elasticsearch (Full-Text Search)

```python
# Faceted search for requirements
async def search_requirements(query: str, filters: dict):
    return await es.search(
        index="requirements",
        body={
            "query": {
                "bool": {
                    "must": [{"match": {"description": query}}],
                    "filter": [
                        {"term": {"project_id": filters["project_id"]}},
                        {"terms": {"status": filters.get("statuses", [])}}
                    ]
                }
            },
            "aggs": {
                "by_priority": {"terms": {"field": "priority"}},
                "by_status": {"terms": {"field": "status.keyword"}}
            }
        }
    )
```

### S3/MinIO (Document Versioning)

```python
# Enable versioning
s3.put_bucket_versioning(
    Bucket="requirements-docs",
    VersioningConfiguration={"Status": "Enabled"}
)

# List all versions of a requirement document
versions = s3.list_object_versions(
    Bucket="requirements-docs",
    Prefix=f"req-{req_id}/spec.md"
)
```

---

## Conclusion

**Complete infrastructure integration strategy** covering:
- TimescaleDB for time-series analytics
- Weaviate for semantic search
- Temporal for workflow orchestration
- Unleash for feature flags
- Elasticsearch for full-text search
- Redis for rate limiting and caching
- S3/MinIO for document storage

**All integrated via:**
- FastMCP composition for unified agent interface
- Backend services for data orchestration
- Our frontend for all user interactions
- No reliance on external application UIs

**Priority implementations:**
1. Redis rate limiting (immediate)
2. Multi-layer caching (week 1)
3. TimescaleDB aggregates (week 2)
4. Weaviate semantic search (month 2)
