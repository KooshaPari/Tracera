# Traceability Matrix Service

## Overview

The Traceability Matrix Service provides high-performance traceability matrix generation and analysis for requirements, tests, and implementation items. It uses optimized PostgreSQL batch queries and Redis caching to deliver sub-500ms response times for projects with 1000+ items.

## Architecture

### Components

- **MatrixService**: Core service handling traceability operations
- **TraceabilityHandler**: HTTP API endpoints
- **PostgreSQL**: Primary data store with optimized batch queries
- **Redis Cache**: 10-minute TTL for computed results

### Data Model

```
Items (Requirements, Features, Tests)
  ↓
Links (TRACES_TO, VALIDATES, IMPLEMENTS, TESTS)
  ↓
Traceability Matrix (Generated view with coverage metrics)
```

## API Endpoints

### 1. Generate Matrix

**Endpoint**: `GET /api/v1/traceability/matrix/:project_id`

Generates a complete traceability matrix for a project.

**Response**:
```json
{
  "project_id": "proj-123",
  "generated_at": "2024-01-15T10:30:00Z",
  "requirements": [
    {
      "item_id": "req-1",
      "title": "User Authentication",
      "type": "requirement",
      "status": "active",
      "trace_count": 3,
      "metadata": {}
    }
  ],
  "test_cases": [
    {
      "item_id": "test-1",
      "title": "Auth Test Suite",
      "type": "test_suite",
      "status": "active",
      "trace_count": 2,
      "metadata": {}
    }
  ],
  "links": [
    {
      "source_id": "req-1",
      "target_id": "test-1",
      "link_type": "TRACES_TO",
      "bidirectional": false
    }
  ],
  "coverage": {
    "total_requirements": 100,
    "traced_requirements": 85,
    "coverage_percent": 85.0,
    "untraced_items": ["req-2", "req-5"]
  }
}
```

**Performance**:
- <200ms for projects with <500 items
- <500ms for projects with <1000 items
- Uses batch queries to minimize database roundtrips

### 2. Get Coverage Report

**Endpoint**: `GET /api/v1/traceability/coverage/:project_id`

Provides detailed coverage analysis with recommendations.

**Response**:
```json
{
  "project_id": "proj-123",
  "overall": {
    "total_requirements": 100,
    "traced_requirements": 85,
    "coverage_percent": 85.0,
    "untraced_items": []
  },
  "by_type": {
    "requirement": {
      "total_requirements": 60,
      "traced_requirements": 55,
      "coverage_percent": 91.67
    },
    "feature": {
      "total_requirements": 30,
      "traced_requirements": 25,
      "coverage_percent": 83.33
    },
    "epic": {
      "total_requirements": 10,
      "traced_requirements": 5,
      "coverage_percent": 50.0
    }
  },
  "recommendations": [
    "Epic coverage is critically low (50.0%). Focus on this area.",
    "5 items have no traceability links. Start with the oldest items."
  ]
}
```

### 3. Get Gap Analysis

**Endpoint**: `GET /api/v1/traceability/gaps/:project_id`

Identifies missing traceability links.

**Response**:
```json
{
  "project_id": "proj-123",
  "missing_forward": [
    {
      "item_id": "req-10",
      "title": "Password Reset",
      "type": "requirement",
      "expected_links": []
    }
  ],
  "missing_backward": [
    {
      "item_id": "test-20",
      "title": "Isolated Test",
      "type": "test_case",
      "expected_links": []
    }
  ],
  "orphaned": ["req-15", "feat-8"],
  "recommendations": [
    "5 requirements lack test coverage. Create test cases for validation.",
    "3 tests are not linked to requirements. Ensure all tests validate specific requirements."
  ]
}
```

### 4. Get Item Traceability

**Endpoint**: `GET /api/v1/traceability/items/:item_id`

Gets traceability information for a specific item.

**Response**:
```json
{
  "item_id": "req-1",
  "upstream_links": [
    {
      "source_id": "epic-1",
      "target_id": "req-1",
      "link_type": "IMPLEMENTS",
      "bidirectional": false
    }
  ],
  "downstream_links": [
    {
      "source_id": "req-1",
      "target_id": "test-1",
      "link_type": "TRACES_TO",
      "bidirectional": false
    },
    {
      "source_id": "req-1",
      "target_id": "test-2",
      "link_type": "VALIDATES",
      "bidirectional": false
    }
  ],
  "coverage_status": "full"
}
```

**Coverage Status**:
- `none`: No traceability links
- `partial`: 1 link (either upstream or downstream)
- `full`: 2+ links (both upstream and downstream)

### 5. Validate Completeness

**Endpoint**: `GET /api/v1/traceability/validate/:project_id`

Validates traceability completeness and generates a compliance report.

**Response**:
```json
{
  "project_id": "proj-123",
  "is_complete": false,
  "score": 78.5,
  "issues": [
    {
      "severity": "error",
      "item_id": "req-10",
      "message": "Requirement 'Password Reset' has no traceability to tests",
      "suggestion": "Create test cases that validate this requirement"
    },
    {
      "severity": "warning",
      "item_id": "feat-5",
      "message": "feature 'Advanced Search' is orphaned (no links)",
      "suggestion": "Link this item to related requirements, tests, or other items"
    }
  ],
  "passed": 85,
  "failed": 15
}
```

**Score Calculation**:
```
score = (passed / total_items) × 100
```

### 6. Get Change Impact

**Endpoint**: `GET /api/v1/traceability/impact/:item_id`

Analyzes the impact of changes to an item.

**Response**:
```json
{
  "item_id": "req-1",
  "direct_impact": ["feat-1", "test-1", "test-2"],
  "indirect_impact": ["test-3", "doc-1"],
  "tests_to_run": ["test-1", "test-2", "test-3"],
  "docs_to_update": ["doc-1"]
}
```

**Impact Levels**:
- **Direct Impact**: Items directly linked to the changed item
- **Indirect Impact**: Items linked to directly impacted items (2 levels deep)
- **Tests to Run**: All test cases in direct and indirect impact
- **Docs to Update**: Documentation items that reference the changed item

## SQL Optimization

### Batch Query Pattern

All major operations use PostgreSQL batch queries to minimize roundtrips:

```go
batch := &pgx.Batch{}

// Queue multiple queries
batch.Queue(query1, args1...)
batch.Queue(query2, args2...)
batch.Queue(query3, args3...)

// Execute in single roundtrip
br := pool.SendBatch(ctx, batch)
defer br.Close()

// Process results
rows1, _ := br.Query()
rows2, _ := br.Query()
rows3, _ := br.Query()
```

**Benefits**:
- Reduces network latency
- Improves throughput
- Enables parallel query execution in PostgreSQL

### Optimized Queries

#### Coverage Metrics Query

```sql
WITH traced AS (
    SELECT DISTINCT i.id
    FROM items i
    JOIN links l ON i.id = l.source_id OR i.id = l.target_id
    WHERE i.project_id = $1
      AND i.type IN ('requirement', 'feature', 'epic')
      AND i.deleted_at IS NULL
)
SELECT
    COUNT(DISTINCT i.id) AS total,
    COUNT(DISTINCT t.id) AS traced,
    ROUND(COALESCE(COUNT(DISTINCT t.id)::numeric / NULLIF(COUNT(DISTINCT i.id), 0) * 100, 0), 2) AS percent
FROM items i
LEFT JOIN traced t ON i.id = t.id
WHERE i.project_id = $1
  AND i.type IN ('requirement', 'feature', 'epic')
  AND i.deleted_at IS NULL
```

**Performance**:
- Uses CTE for efficient link tracking
- Single table scan with index on (project_id, type)
- Handles division by zero gracefully

#### Gap Detection Query

```sql
-- Requirements without tests
SELECT i.id, i.title, i.type
FROM items i
WHERE i.project_id = $1
  AND i.type IN ('requirement', 'feature', 'epic')
  AND i.deleted_at IS NULL
  AND NOT EXISTS (
      SELECT 1 FROM links l
      WHERE l.source_id = i.id
        AND l.link_type IN ('TRACES_TO', 'VALIDATES', 'TESTS')
  )
```

**Performance**:
- Uses NOT EXISTS for efficient anti-join
- Index on (source_id, link_type) for fast lookups
- Filters early with WHERE clause

## Caching Strategy

### Cache Keys

```
traceability:matrix:{project_id}      → Full matrix
traceability:coverage:{project_id}    → Coverage report
traceability:gaps:{project_id}        → Gap analysis
traceability:item:{item_id}           → Item traceability
traceability:validation:{project_id}  → Validation report
traceability:impact:{item_id}         → Change impact
```

### TTL Configuration

- **Matrix/Coverage/Gaps/Validation**: 10 minutes
- **Item Traceability/Impact**: 5 minutes

### Cache Invalidation

Invalidate on:
- Link creation/deletion
- Item status changes
- Project structure updates

```go
cache.InvalidatePattern(ctx, fmt.Sprintf("traceability:*:%s", projectID))
```

## Performance Benchmarks

### Target Metrics

| Project Size | Matrix Generation | Coverage Report | Gap Analysis |
|--------------|------------------|-----------------|--------------|
| 100 items    | <50ms            | <30ms           | <40ms        |
| 500 items    | <200ms           | <100ms          | <150ms       |
| 1000 items   | <500ms           | <250ms          | <350ms       |
| 5000 items   | <2s              | <1s             | <1.5s        |

### Optimization Techniques

1. **Batch Queries**: Reduce database roundtrips from 5+ to 1
2. **Indexed Lookups**: Fast access via (project_id, type, deleted_at)
3. **Caching**: 10-minute TTL reduces database load
4. **Partial Loading**: Stream results instead of loading all into memory
5. **Concurrent Processing**: Process independent queries in parallel

## Usage Examples

### Generate Matrix

```bash
curl -X GET \
  'https://api.tracertm.com/api/v1/traceability/matrix/proj-123' \
  -H 'Authorization: Bearer {token}'
```

### Get Coverage with Filtering

```bash
curl -X GET \
  'https://api.tracertm.com/api/v1/traceability/coverage/proj-123' \
  -H 'Authorization: Bearer {token}'
```

### Validate Before Release

```bash
curl -X GET \
  'https://api.tracertm.com/api/v1/traceability/validate/proj-123' \
  -H 'Authorization: Bearer {token}'
```

### Assess Change Impact

```bash
curl -X GET \
  'https://api.tracertm.com/api/v1/traceability/impact/req-123' \
  -H 'Authorization: Bearer {token}'
```

## Integration

### Event Publishing

On traceability operations, publish events for real-time updates:

```go
publisher.Publish(ctx, nats.Event{
    Type:      "traceability.matrix.generated",
    ProjectID: projectID,
    Timestamp: time.Now(),
    Data: map[string]interface{}{
        "coverage_percent": matrix.Coverage.CoveragePercent,
        "total_items": len(matrix.Requirements) + len(matrix.TestCases),
    },
})
```

### Frontend Integration

```typescript
// Fetch traceability matrix
const matrix = await fetch(`/api/v1/traceability/matrix/${projectId}`)
  .then(r => r.json());

// Display coverage metrics
console.log(`Coverage: ${matrix.coverage.coverage_percent}%`);

// Show gaps
const gaps = await fetch(`/api/v1/traceability/gaps/${projectId}`)
  .then(r => r.json());

console.log(`Missing forward links: ${gaps.missing_forward.length}`);
```

### CLI Integration

```bash
# Generate matrix report
tracertm trace matrix --project proj-123

# Validate completeness
tracertm trace validate --project proj-123

# Assess impact
tracertm trace impact --item req-123
```

## Error Handling

### Common Errors

| Error | Status | Description | Solution |
|-------|--------|-------------|----------|
| Project not found | 404 | Invalid project_id | Verify project exists |
| Item not found | 404 | Invalid item_id | Verify item exists |
| Database timeout | 500 | Query took >30s | Reduce project size or optimize |
| Cache failure | 500 | Redis unavailable | Check Redis connection |

### Retry Strategy

For transient errors:
1. Retry with exponential backoff
2. Max 3 retries
3. Fall back to uncached query

## Monitoring

### Key Metrics

- **Matrix Generation Time**: P50, P95, P99
- **Cache Hit Rate**: Target >80%
- **Database Query Time**: Per query type
- **Error Rate**: By error type

### Alerts

- Matrix generation >1s for projects <1000 items
- Cache hit rate <60%
- Error rate >5%

## Future Enhancements

1. **Real-time Updates**: Stream matrix updates via WebSocket
2. **Custom Views**: User-defined matrix filters and groupings
3. **Export Formats**: PDF, Excel, CSV matrix exports
4. **AI Suggestions**: ML-powered link recommendations
5. **Compliance Reports**: ISO 26262, DO-178C, FDA compliance
6. **Diff Views**: Compare matrices across versions
7. **Bulk Operations**: Batch link creation/deletion
8. **Advanced Analytics**: Trend analysis, coverage history

## References

- [Traceability Matrix Types Guide](../guides/traceability_matrix_types.md)
- [Link Types Documentation](../concepts/link_types.md)
- [Performance Tuning Guide](../guides/performance_tuning.md)
- [API Reference](../api/traceability.md)
