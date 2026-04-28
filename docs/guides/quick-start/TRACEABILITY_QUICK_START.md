# Traceability Matrix Service - Quick Start Guide

## Overview

The Traceability Matrix Service provides fast, cached traceability analysis for requirements, tests, and implementation items.

## Quick Start

### 1. Generate Matrix (30 seconds)

```bash
curl -X GET \
  "http://localhost:8080/api/v1/traceability/matrix/YOUR_PROJECT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Returns**: Complete traceability matrix with requirements, tests, links, and coverage metrics.

### 2. Check Coverage (15 seconds)

```bash
curl -X GET \
  "http://localhost:8080/api/v1/traceability/coverage/YOUR_PROJECT_ID"
```

**Returns**: Coverage report by item type with recommendations.

### 3. Find Gaps (20 seconds)

```bash
curl -X GET \
  "http://localhost:8080/api/v1/traceability/gaps/YOUR_PROJECT_ID"
```

**Returns**: Missing links (requirements without tests, tests without requirements, orphaned items).

## Common Use Cases

### Before Release: Validate Completeness

```bash
curl -X GET \
  "http://localhost:8080/api/v1/traceability/validate/YOUR_PROJECT_ID"
```

**Check**:
- `is_complete`: `true` if all requirements are traced
- `score`: Completeness score (0-100)
- `issues`: List of validation failures

### Before Merge: Assess Change Impact

```bash
curl -X GET \
  "http://localhost:8080/api/v1/traceability/impact/ITEM_ID"
```

**Check**:
- `tests_to_run`: Which tests need to run
- `direct_impact`: Immediately affected items
- `indirect_impact`: Cascading effects

### During Review: Item Traceability

```bash
curl -X GET \
  "http://localhost:8080/api/v1/traceability/items/ITEM_ID"
```

**Check**:
- `upstream_links`: What links TO this item
- `downstream_links`: What this item links TO
- `coverage_status`: "full", "partial", or "none"

## API Endpoints Summary

| Endpoint | Purpose | Cache TTL |
|----------|---------|-----------|
| `GET /matrix/:project_id` | Full matrix | 10 min |
| `GET /coverage/:project_id` | Coverage report | 10 min |
| `GET /gaps/:project_id` | Gap analysis | 10 min |
| `GET /validate/:project_id` | Validation report | 10 min |
| `GET /items/:item_id` | Item traceability | 5 min |
| `GET /impact/:item_id` | Change impact | 5 min |

## Response Examples

### Matrix Response (Simplified)

```json
{
  "project_id": "proj-123",
  "coverage": {
    "total_requirements": 100,
    "traced_requirements": 85,
    "coverage_percent": 85.0,
    "untraced_items": ["req-1", "req-5"]
  }
}
```

### Coverage Response

```json
{
  "overall": {
    "coverage_percent": 85.0
  },
  "by_type": {
    "requirement": {"coverage_percent": 90.0},
    "feature": {"coverage_percent": 80.0}
  },
  "recommendations": [
    "Coverage is below target (80%). Continue adding traceability links."
  ]
}
```

### Gap Analysis Response

```json
{
  "missing_forward": [
    {
      "item_id": "req-10",
      "title": "Password Reset",
      "type": "requirement"
    }
  ],
  "recommendations": [
    "5 requirements lack test coverage. Create test cases for validation."
  ]
}
```

### Validation Response

```json
{
  "is_complete": false,
  "score": 78.5,
  "issues": [
    {
      "severity": "error",
      "item_id": "req-10",
      "message": "Requirement 'Password Reset' has no traceability to tests"
    }
  ]
}
```

## Performance

| Project Size | Matrix Gen | Coverage | Gap Analysis |
|--------------|------------|----------|--------------|
| 100 items    | ~30ms      | ~20ms    | ~25ms        |
| 500 items    | ~150ms     | ~80ms    | ~120ms       |
| 1000 items   | ~400ms     | ~200ms   | ~300ms       |

**Note**: First request generates and caches. Subsequent requests return instantly from cache.

## Best Practices

### 1. Check Coverage Regularly

Run coverage checks in CI/CD:
```bash
COVERAGE=$(curl -s "http://localhost:8080/api/v1/traceability/coverage/$PROJECT_ID" | jq '.overall.coverage_percent')

if (( $(echo "$COVERAGE < 80" | bc -l) )); then
  echo "Coverage below 80%: $COVERAGE%"
  exit 1
fi
```

### 2. Validate Before Release

Add to release checklist:
```bash
VALIDATION=$(curl -s "http://localhost:8080/api/v1/traceability/validate/$PROJECT_ID")
IS_COMPLETE=$(echo $VALIDATION | jq -r '.is_complete')

if [ "$IS_COMPLETE" != "true" ]; then
  echo "Traceability incomplete. Cannot release."
  echo $VALIDATION | jq '.issues'
  exit 1
fi
```

### 3. Assess Impact on Changes

Before merging PRs:
```bash
IMPACT=$(curl -s "http://localhost:8080/api/v1/traceability/impact/$ITEM_ID")
TESTS=$(echo $IMPACT | jq -r '.tests_to_run[]')

echo "Tests to run:"
echo "$TESTS"
```

### 4. Monitor Gaps

Track gap trends:
```bash
GAPS=$(curl -s "http://localhost:8080/api/v1/traceability/gaps/$PROJECT_ID")
FORWARD=$(echo $GAPS | jq '.missing_forward | length')
BACKWARD=$(echo $GAPS | jq '.missing_backward | length')

echo "Forward gaps (reqs without tests): $FORWARD"
echo "Backward gaps (tests without reqs): $BACKWARD"
```

## Link Types

The service recognizes these link types:

- **TRACES_TO**: Requirement → Test (forward traceability)
- **VALIDATES**: Test → Requirement (backward traceability)
- **IMPLEMENTS**: Feature → Code/Component
- **TESTS**: Test → Feature/Component

## Troubleshooting

### Matrix Generation Slow (>1s)

1. Check project size: `SELECT COUNT(*) FROM items WHERE project_id = 'proj-123'`
2. Check cache: Items should be cached for 10 minutes
3. Review indexes: Ensure `(project_id, type, deleted_at)` index exists

### Cache Not Working

1. Verify Redis connection: `redis-cli ping`
2. Check cache keys: `redis-cli KEYS "traceability:*"`
3. Review TTL: `redis-cli TTL "traceability:matrix:proj-123"`

### Missing Links

1. Verify link types: Service only recognizes TRACES_TO, VALIDATES, IMPLEMENTS, TESTS
2. Check soft deletes: Deleted items/links are excluded
3. Review project context: Links must be within same project

### Low Coverage

1. Run gap analysis to find untraced items
2. Create missing links: `POST /api/v1/links`
3. Re-run coverage check (cache invalidates automatically)

## Integration Examples

### Frontend (TypeScript)

```typescript
// Get coverage
const coverage = await fetch(`/api/v1/traceability/coverage/${projectId}`)
  .then(r => r.json());

console.log(`Coverage: ${coverage.overall.coverage_percent}%`);

// Validate before release
const validation = await fetch(`/api/v1/traceability/validate/${projectId}`)
  .then(r => r.json());

if (!validation.is_complete) {
  alert(`Traceability incomplete (${validation.score.toFixed(1)}%)`);
}
```

### Python CLI

```python
import requests

def get_coverage(project_id: str, base_url: str) -> dict:
    response = requests.get(f"{base_url}/api/v1/traceability/coverage/{project_id}")
    response.raise_for_status()
    return response.json()

coverage = get_coverage("proj-123", "http://localhost:8080")
print(f"Coverage: {coverage['overall']['coverage_percent']}%")
```

### Go Client

```go
type CoverageReport struct {
    Overall struct {
        CoveragePercent float64 `json:"coverage_percent"`
    } `json:"overall"`
}

func GetCoverage(projectID string) (*CoverageReport, error) {
    resp, err := http.Get(fmt.Sprintf("http://localhost:8080/api/v1/traceability/coverage/%s", projectID))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var report CoverageReport
    if err := json.NewDecoder(resp.Body).Decode(&report); err != nil {
        return nil, err
    }

    return &report, nil
}
```

## Next Steps

1. **Read Full Documentation**: [Traceability Matrix Service](docs/services/traceability_matrix_service.md)
2. **Explore API**: Try all 6 endpoints with your project
3. **Integrate CI/CD**: Add coverage/validation checks to pipeline
4. **Monitor Trends**: Track coverage and gaps over time
5. **Optimize Performance**: Add recommended database indexes

## Support

- **API Issues**: Check logs in `backend/logs/`
- **Performance**: Review [Performance Tuning Guide](docs/guides/performance_tuning.md)
- **Questions**: See [Full Documentation](docs/services/traceability_matrix_service.md)
