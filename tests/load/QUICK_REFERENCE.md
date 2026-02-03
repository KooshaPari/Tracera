# Load Testing Quick Reference

Quick reference for running load tests on TracerTM.

## Prerequisites

```bash
# Install k6
brew install k6  # macOS
sudo apt install k6  # Ubuntu

# Start services
make dev
```

## Running Tests

| Command | Test Type | Duration | Users |
|---------|-----------|----------|-------|
| `make load-test-smoke` | Smoke Test | 1 min | 1-5 |
| `make load-test-load` | Load Test | 18 min | 100 |
| `make load-test-stress` | Stress Test | 25 min | 1000 |
| `make load-test-spike` | Spike Test | 7.5 min | 10→500 |
| `make load-test-soak` | Soak Test | 2h 10m | 50 |
| `make load-test-websocket` | WebSocket | 23 min | 5000 |
| `make load-test-database` | Database | 10 min | 1000 conn |

## Performance Targets

### Response Time
- **P95**: < 500ms
- **P99**: < 1000ms
- **Average**: < 300ms

### Error Rate
- **Normal Load**: < 0.1%
- **Stress Test**: < 5%
- **Spike Test**: < 10%

### Throughput
- **Load Test**: > 500 req/s
- **Stress Test**: > 1000 req/s

## Common Commands

```bash
# Quick smoke test
make load-test-smoke

# Full load test
make load-test-load

# Run with custom URL
BASE_URL=http://localhost:4000 k6 run tests/load/k6/scenarios/smoke.js

# Save results
k6 run --out json=results.json --summary-export=summary.json tests/load/k6/scenarios/load.js

# Compare with baseline
make load-test-compare

# Generate HTML report
make load-test-report
```

## Monitoring During Tests

```bash
# Terminal 1: Run test
make load-test-load

# Terminal 2: Monitor resources
watch -n 1 'ps aux | grep -E "(go-backend|python-backend)"'

# Terminal 3: Monitor logs
make dev-logs-follow
```

## Reading Results

```
http_req_duration.p95: 456ms  ✅ Good (< 500ms)
http_req_failed: 0.12%        ✅ Good (< 0.1%)
http_reqs: 250/s              ✅ Good (> 200/s)
checks: 100%                  ✅ Perfect
```

## Troubleshooting

### High Errors
```bash
curl http://localhost:4000/health
make dev-logs-follow
```

### Slow Responses
```sql
-- Check slow queries
SELECT pid, query, now() - query_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

### Memory Issues
```bash
watch -n 10 'ps aux | grep python | awk "{print \$4}"'
```

## Environment Variables

```bash
export BASE_URL=http://localhost:4000
export TEST_ENV=development
export TEST_USERS='[{"email":"test@example.com","password":"Test123!"}]'
```

## Files

- **Scenarios**: `tests/load/k6/scenarios/*.js`
- **Helpers**: `tests/load/k6/helpers/*.js`
- **Database**: `tests/load/database/*.sql`
- **WebSocket**: `tests/load/websocket/*.js`
- **Scripts**: `tests/load/scripts/*.py`
- **Baselines**: `tests/load/.baseline/*.json`

## Next Steps

1. Run smoke test: `make load-test-smoke`
2. Establish baseline: `make load-test-load`
3. Schedule soak test: `make load-test-soak`
4. Monitor trends over time

See [Load Testing Guide](../../docs/guides/load-testing-guide.md) for full documentation.
