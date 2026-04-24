# Load Testing Suite

Comprehensive load testing infrastructure for TracerTM performance validation.

## Quick Start

```bash
# Install k6
brew install k6  # macOS
# OR
sudo apt install k6  # Ubuntu/Debian

# Start TracerTM services
make dev

# Run smoke test (quick validation)
make load-test-smoke

# Run full load test
make load-test-load
```

## Test Scenarios

| Test | Users | Duration | Purpose |
|------|-------|----------|---------|
| **Smoke** | 1-5 | 1 min | Quick sanity check |
| **Load** | 100 | 18 min | Normal production load |
| **Stress** | 1000 | 25 min | Find breaking points |
| **Spike** | 10→500 | 7.5 min | Sudden traffic spikes |
| **Soak** | 50 | 2h 10m | Long-term stability |

## Directory Structure

```
tests/load/
├── k6/
│   ├── scenarios/           # Test scenarios
│   │   ├── smoke.js         # Quick validation
│   │   ├── load.js          # Normal load
│   │   ├── stress.js        # High load
│   │   ├── spike.js         # Traffic spikes
│   │   └── soak.js          # Endurance test
│   └── helpers/             # Shared utilities
│       ├── auth.js          # Authentication helpers
│       └── data-generators.js # Test data generation
├── websocket/
│   └── ws-load-test.js      # WebSocket load testing
├── database/
│   └── connection-pool-test.sql # Database stress testing
├── scripts/
│   ├── compare-performance.py   # Baseline comparison
│   └── generate-report.py       # HTML report generation
└── .baseline/               # Performance baselines
```

## Running Tests

### Smoke Test (1 minute)

Quick validation before larger tests:

```bash
# Using make
make load-test-smoke

# Using k6 directly
k6 run tests/load/k6/scenarios/smoke.js

# With custom URL
BASE_URL=http://localhost:4000 k6 run tests/load/k6/scenarios/smoke.js
```

### Load Test (18 minutes)

Standard performance validation:

```bash
make load-test-load
```

### Stress Test (25 minutes)

Find breaking points:

```bash
make load-test-stress
```

### Spike Test (7.5 minutes)

Test sudden traffic spikes:

```bash
make load-test-spike
```

### Soak Test (2+ hours)

Long-term stability:

```bash
# Run in background
nohup make load-test-soak > soak-test.log 2>&1 &

# Monitor progress
tail -f soak-test.log
```

### WebSocket Load Test

Test WebSocket performance:

```bash
make load-test-websocket
```

### Database Stress Test

Test database connection pool:

```bash
# Ensure PostgreSQL is running
pg_isready -h localhost -p 5432

# Run pgbench test
pgbench -c 1000 -j 100 -T 600 \
  -f tests/load/database/connection-pool-test.sql \
  -U tracertm tracertm
```

## Performance Budgets

### Response Time Targets

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| P95 Latency | < 500ms | < 1000ms |
| P99 Latency | < 1000ms | < 2000ms |
| Average | < 300ms | < 600ms |

### Error Rate Targets

| Scenario | Target | Max Acceptable |
|----------|--------|----------------|
| Normal Load | < 0.01% | < 0.1% |
| Stress Test | < 1% | < 5% |
| Spike Test | < 5% | < 10% |

### Throughput Targets

| Scenario | Minimum | Target |
|----------|---------|--------|
| Load Test | 300 req/s | 500 req/s |
| Stress Test | 500 req/s | 1000 req/s |

## Analyzing Results

### Understanding k6 Output

```
checks.........................: 100.00% ✓ 15420     ✗ 0
http_req_duration..............: avg=234ms p(95)=456ms
http_req_failed................: 0.12%   ✓ 18       ✗ 14982
http_reqs......................: 15000   250/s
```

**Key Metrics**:
- `checks`: Test assertions (should be 100%)
- `http_req_duration.p95`: 95th percentile response time
- `http_req_failed`: Error rate
- `http_reqs`: Total requests and rate

### Comparing with Baseline

```bash
# Compare current results with baseline
python tests/load/scripts/compare-performance.py \
  --baseline tests/load/.baseline/load-baseline.json \
  --current load-test-summary.json \
  --threshold 10
```

### Generating HTML Report

```bash
# Generate performance report
python tests/load/scripts/generate-report.py \
  --results-dir results \
  --output performance-report.html

# Open report
open performance-report.html  # macOS
xdg-open performance-report.html  # Linux
```

## CI/CD Integration

Tests run automatically on:
- Pull requests to main/master
- Pushes to main (establishes baseline)
- Weekly schedule (Monday 2 AM UTC)

Manual trigger:

```bash
# Via GitHub CLI
gh workflow run performance-regression.yml

# With specific test type
gh workflow run performance-regression.yml -f test_type=load
```

## Troubleshooting

### High Error Rates

```bash
# Check service health
curl http://localhost:4000/health

# Check logs
make dev-logs-follow

# Check resource usage
top
htop
```

### Slow Response Times

```sql
-- Check for slow queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '500 milliseconds'
ORDER BY duration DESC;
```

### Memory Leaks

```bash
# Monitor memory usage
watch -n 10 'ps aux | grep -E "(go-backend|python-backend)" | awk "{print \$4}"'

# Check for connection leaks
psql -U tracertm -d tracertm -c "
  SELECT count(*) FROM pg_stat_activity WHERE datname = 'tracertm';"
```

## Best Practices

1. **Always start with smoke test** before running expensive tests
2. **Run tests sequentially**, not in parallel
3. **Monitor system resources** during tests
4. **Establish baselines** for comparison
5. **Test realistic scenarios** with appropriate think times

## Environment Variables

```bash
# Base URL for tests
export BASE_URL=http://localhost:4000

# Test environment
export TEST_ENV=development

# Test users (JSON array)
export TEST_USERS='[
  {"email": "test1@example.com", "password": "Test123!"},
  {"email": "test2@example.com", "password": "Test123!"}
]'
```

## Additional Resources

- **Full Guide**: [Load Testing Guide](../../docs/guides/load-testing-guide.md)
- **k6 Documentation**: https://k6.io/docs/
- **Performance Budgets**: See full guide for detailed targets
- **Troubleshooting**: See full guide for common issues

## Success Criteria

✅ **All tests pass with**:
- Support 1000+ concurrent users (stress test)
- Maintain <500ms P95 latency under normal load
- Zero crashes or OOM errors during stress tests
- <0.1% error rate under normal load
- No performance degradation during soak test
- 5000+ concurrent WebSocket connections
- 1000+ database connections without exhaustion

---

For detailed information, see the [Load Testing Guide](../../docs/guides/load-testing-guide.md).
