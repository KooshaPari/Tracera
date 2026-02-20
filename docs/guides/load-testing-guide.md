# Load Testing Guide

Comprehensive guide for running load tests and validating TracerTM performance at scale.

## Overview

This guide covers the complete load testing infrastructure for TracerTM, including:

- **k6 Test Scenarios**: Smoke, load, stress, spike, and soak tests
- **WebSocket Load Testing**: High-concurrency connection testing
- **Database Stress Testing**: Connection pool and query performance
- **Performance Regression Detection**: Automated baseline comparison
- **CI/CD Integration**: Continuous performance validation

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Scenarios](#test-scenarios)
3. [Running Tests](#running-tests)
4. [Performance Budgets](#performance-budgets)
5. [Database Testing](#database-testing)
6. [WebSocket Testing](#websocket-testing)
7. [CI/CD Integration](#cicd-integration)
8. [Analyzing Results](#analyzing-results)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

```bash
# Install k6
brew install k6  # macOS
# OR
sudo apt install k6  # Ubuntu/Debian
# OR
choco install k6  # Windows

# Install PostgreSQL tools (for database testing)
brew install postgresql  # macOS

# Start TracerTM services
make dev
```

### Run Your First Load Test

```bash
# Run smoke test (quick validation)
k6 run tests/load/k6/scenarios/smoke.js

# Run with custom base URL
BASE_URL=http://localhost:4000 k6 run tests/load/k6/scenarios/smoke.js

# Run with detailed output
k6 run --out json=results.json tests/load/k6/scenarios/smoke.js
```

---

## Test Scenarios

### 1. Smoke Test

**Purpose**: Quick validation that system is functioning correctly

**Configuration**:
- **Users**: 1-5 concurrent
- **Duration**: 1 minute
- **Goal**: Verify basic functionality before larger tests

**When to Run**:
- Before every load test session
- After deployments
- During development

**Run**:
```bash
k6 run tests/load/k6/scenarios/smoke.js
```

**Expected Results**:
- ✅ Error rate < 1%
- ✅ P95 latency < 500ms
- ✅ All critical paths functional

---

### 2. Load Test

**Purpose**: Validate performance under expected production load

**Configuration**:
- **Users**: Ramp to 100 concurrent
- **Duration**: 18 minutes total
  - 2m warm-up (0 → 20 users)
  - 3m ramp-up (20 → 100 users)
  - 10m sustained (100 users)
  - 3m ramp-down (100 → 0 users)
- **Goal**: Ensure system meets performance SLAs under normal load

**When to Run**:
- Before releases
- Performance regression testing
- Capacity planning

**Run**:
```bash
k6 run tests/load/k6/scenarios/load.js
```

**Expected Results**:
- ✅ Error rate < 0.1%
- ✅ P95 latency < 500ms
- ✅ P99 latency < 1000ms
- ✅ Throughput > 500 req/s

---

### 3. Stress Test

**Purpose**: Find breaking points and validate graceful degradation

**Configuration**:
- **Users**: Ramp to 1000 concurrent over 10 minutes
- **Duration**: 25 minutes total
- **Goal**: Identify capacity limits and failure modes

**When to Run**:
- Capacity planning
- Infrastructure validation
- Pre-scaling decisions

**Run**:
```bash
k6 run tests/load/k6/scenarios/stress.js
```

**Expected Results**:
- ✅ Error rate < 5% (degraded but acceptable)
- ✅ P95 latency < 2000ms
- ✅ System remains stable (no crashes)
- ✅ Graceful degradation observed

**Analysis Points**:
- At what user count do errors begin?
- Which endpoints fail first?
- How does the system recover?
- Are there resource exhaustion issues?

---

### 4. Spike Test

**Purpose**: Validate behavior during sudden traffic spikes

**Configuration**:
- **Users**: 10 → 500 users in 10 seconds (sudden spike)
- **Duration**: 7.5 minutes total
- **Goal**: Test auto-scaling and rate limiting

**When to Run**:
- Before marketing campaigns
- After implementing rate limiting
- Testing auto-scaling configurations

**Run**:
```bash
k6 run tests/load/k6/scenarios/spike.js
```

**Expected Results**:
- ✅ Error rate < 10% during spike
- ✅ Rate limiting activates (429 responses)
- ✅ System recovers within 30 seconds
- ✅ No crashes or permanent degradation

**Key Metrics**:
- **Rate Limit Hits**: Should be > 0 (rate limiting working)
- **Spike Recovery Time**: Time to return to normal performance
- **Queued Requests**: Requests accepted but queued (202 responses)

---

### 5. Soak Test (Endurance Test)

**Purpose**: Detect memory leaks and long-term stability issues

**Configuration**:
- **Users**: 50 concurrent (sustained)
- **Duration**: 2 hours 10 minutes
- **Goal**: Validate stability over extended periods

**When to Run**:
- Before major releases
- After significant architectural changes
- Monthly stability validation

**Run**:
```bash
# Run soak test (long-running)
k6 run tests/load/k6/scenarios/soak.js

# Run overnight
nohup k6 run tests/load/k6/scenarios/soak.js > soak-test.log 2>&1 &
```

**Expected Results**:
- ✅ Error rate < 0.1% (consistent)
- ✅ No response time degradation over time
- ✅ No memory leaks (stable memory usage)
- ✅ No connection pool exhaustion

**What to Monitor**:
- Memory usage trends (should be flat)
- Response time trends (should be stable)
- Database connection count (should be stable)
- Error patterns (should be random, not trending)

---

## Performance Budgets

### Response Time Targets

| Percentile | Target | Max Acceptable | Critical Threshold |
|------------|--------|----------------|-------------------|
| P50 (Median) | < 200ms | < 300ms | < 500ms |
| P95 | < 500ms | < 800ms | < 1000ms |
| P99 | < 1000ms | < 1500ms | < 2000ms |

### Error Rate Targets

| Scenario | Target | Max Acceptable | Critical Threshold |
|----------|--------|----------------|-------------------|
| Normal Load | < 0.01% | < 0.1% | < 1% |
| Stress Test | < 1% | < 5% | < 10% |
| Spike Test | < 5% | < 10% | < 20% |

### Throughput Targets

| Scenario | Target | Minimum Acceptable |
|----------|--------|-------------------|
| Load Test | > 500 req/s | > 300 req/s |
| Stress Test | > 1000 req/s | > 500 req/s |

### Resource Utilization Targets

| Resource | Normal | High Load | Critical |
|----------|--------|-----------|----------|
| CPU | < 50% | < 70% | < 90% |
| Memory | < 60% | < 80% | < 95% |
| Database Connections | < 50% of pool | < 70% of pool | < 90% of pool |

---

## Database Testing

### Connection Pool Stress Test

Tests database performance under high connection count and query load.

**Setup**:
```bash
# Ensure PostgreSQL is running
pg_isready -h localhost -p 5432

# Check current connection limits
psql -U tracertm -d tracertm -c "SHOW max_connections;"
```

**Run with pgbench**:
```bash
# Initialize test data (if needed)
psql -U tracertm -d tracertm -f tests/load/database/setup-test-data.sql

# Run connection pool test
# 1000 concurrent connections, 100 threads, 10 minutes
pgbench -c 1000 -j 100 -T 600 \
  -f tests/load/database/connection-pool-test.sql \
  -U tracertm tracertm

# Monitor during test
watch -n 1 'psql -U tracertm -d tracertm -c "
  SELECT
    COUNT(*) as total_connections,
    COUNT(*) FILTER (WHERE state = '\''active'\'') as active,
    COUNT(*) FILTER (WHERE state = '\''idle'\'') as idle
  FROM pg_stat_activity
  WHERE datname = '\''tracertm'\'';"'
```

**Expected Results**:
- ✅ Handle 1000+ simultaneous connections
- ✅ No connection pool exhaustion errors
- ✅ Query performance remains consistent
- ✅ No deadlocks or lock contention

**Monitoring Queries**:
```sql
-- Check connection count
SELECT count(*) FROM pg_stat_activity WHERE datname = 'tracertm';

-- Check for slow queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle' AND now() - query_start > interval '1 second'
ORDER BY duration DESC;

-- Check for locks
SELECT locktype, relation::regclass, mode, COUNT(*)
FROM pg_locks
WHERE NOT granted
GROUP BY locktype, relation, mode;
```

---

## WebSocket Testing

### High-Concurrency WebSocket Test

Tests WebSocket performance with 5000+ concurrent connections.

**Run**:
```bash
# Run WebSocket load test
k6 run tests/load/websocket/ws-load-test.js

# Monitor WebSocket connections
watch -n 1 'ss -tan | grep :4000 | wc -l'
```

**Expected Results**:
- ✅ Support 5000+ concurrent connections
- ✅ Message latency < 200ms (P95)
- ✅ Broadcast latency < 500ms (P95)
- ✅ Connection drops < 100 over test duration
- ✅ Stable reconnection handling

**Key Metrics**:
- `ws_connection_time`: Time to establish WebSocket connection
- `ws_message_latency`: End-to-end message delivery time
- `ws_broadcast_latency`: Time from server send to client receipt
- `ws_active_connections`: Current connection count
- `ws_connection_drops`: Number of dropped connections

**Monitoring**:
```bash
# Monitor WebSocket connections
netstat -an | grep ESTABLISHED | grep :4000 | wc -l

# Monitor memory usage
ps aux | grep -E '(go-backend|python-backend)' | awk '{print $4}'

# Monitor CPU usage
top -p $(pgrep -f 'go-backend|python-backend')
```

---

## CI/CD Integration

### GitHub Actions Workflow

The performance regression testing workflow runs automatically on:
- Pull requests to main/master
- Pushes to main/master (establishes baseline)
- Weekly schedule (Monday 2 AM UTC)
- Manual trigger

**Trigger Manually**:
```bash
# Via GitHub CLI
gh workflow run performance-regression.yml

# With specific test type
gh workflow run performance-regression.yml -f test_type=load
```

**Workflow Steps**:
1. Setup test environment (PostgreSQL, Redis)
2. Build and start services
3. Run selected test scenario
4. Compare against baseline
5. Generate performance report
6. Comment on PR with results

**Baseline Management**:
- Baselines stored in `tests/load/.baseline/`
- Updated automatically on main branch merges
- Manual baseline update:
  ```bash
  # Run test and save as baseline
  k6 run --summary-export=smoke-baseline.json tests/load/k6/scenarios/smoke.js
  cp smoke-baseline.json tests/load/.baseline/
  git add tests/load/.baseline/smoke-baseline.json
  git commit -m "Update performance baseline"
  ```

---

## Analyzing Results

### Reading k6 Output

```
scenarios: (100.00%) 1 scenario, 100 max VUs, 20m30s max duration
✓ Projects loaded
✓ Dashboard loaded
✓ Item created

checks.........................: 100.00% ✓ 15420     ✗ 0
data_received..................: 45 MB   75 kB/s
data_sent......................: 12 MB   20 kB/s
http_req_duration..............: avg=234ms min=45ms med=198ms max=2.1s p(90)=389ms p(95)=456ms
http_req_failed................: 0.12%   ✓ 18       ✗ 14982
http_reqs......................: 15000   250/s
iteration_duration.............: avg=2.4s  min=1.2s med=2.3s max=5.1s p(90)=3.2s p(95)=3.8s
iterations.....................: 5000    83.33/s
vus............................: 100     min=0      max=100
```

**Key Metrics Explained**:
- `checks`: Test assertions (should be 100%)
- `http_req_duration.p95`: 95% of requests completed in this time
- `http_req_failed`: Percentage of failed requests
- `http_reqs`: Total requests and rate (req/s)
- `vus`: Virtual users (concurrent users)

### Interpreting Results

**Healthy System**:
```
http_req_duration.p95: < 500ms
http_req_failed: < 0.1%
checks: 100%
```

**Performance Issues**:
```
http_req_duration.p95: > 1000ms  ⚠️ Slow responses
http_req_failed: > 1%            ⚠️ High error rate
checks: < 95%                    ⚠️ Failing assertions
```

**Resource Exhaustion**:
```
http_req_duration: Increasing over time  ⚠️ Memory leak
http_req_failed: Sudden spikes          ⚠️ Resource limits
5xx errors: > 0                         ⚠️ Server errors
```

### Comparing with Baseline

```bash
# Compare current results with baseline
python tests/load/scripts/compare-performance.py \
  --baseline tests/load/.baseline/load-baseline.json \
  --current load-test-summary.json \
  --threshold 10
```

**Output**:
```
================================================================================
PERFORMANCE COMPARISON REPORT
================================================================================

Baseline: tests/load/.baseline/load-baseline.json
Current:  load-test-summary.json
Threshold: 10%

Findings:

  ✅ P95 Response Time improved by 12.34% (baseline: 456.00ms, current: 400.00ms)
  ⚠️  Error Rate increased by 8.50% (baseline: 0.0010, current: 0.0011)
  ✅ Request Rate improved by 5.20% (baseline: 245.00, current: 257.73)

================================================================================
✅ Performance check passed!
```

---

## Troubleshooting

### High Error Rates

**Symptoms**:
- `http_req_failed` > 1%
- Many 5xx errors
- Connection timeouts

**Diagnosis**:
```bash
# Check service health
curl http://localhost:4000/health

# Check logs
make dev-logs-follow SERVICE=go-backend

# Check resource usage
docker stats  # If using Docker
top           # Native processes
```

**Common Causes**:
- Database connection pool exhausted
- Memory limits reached
- Rate limiting activated
- Backend service crashed

**Solutions**:
- Increase connection pool size
- Add more resources (CPU/memory)
- Adjust rate limiting thresholds
- Fix backend bugs causing crashes

---

### Slow Response Times

**Symptoms**:
- `http_req_duration.p95` > 1000ms
- Increasing latency over time

**Diagnosis**:
```sql
-- Check for slow queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '500 milliseconds'
ORDER BY duration DESC;

-- Check for missing indexes
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

**Common Causes**:
- Missing database indexes
- N+1 query problems
- Inefficient algorithms
- Cache misses

**Solutions**:
- Add appropriate indexes
- Optimize database queries
- Implement query caching
- Use connection pooling

---

### Memory Leaks

**Symptoms** (during soak test):
- Response time degrading over time
- Memory usage increasing linearly
- Eventual OOM errors

**Diagnosis**:
```bash
# Monitor memory usage over time
watch -n 10 'ps aux | grep -E "(go-backend|python-backend)" | awk "{print \$4}"'

# Check for connection leaks
psql -U tracertm -d tracertm -c "
  SELECT count(*) FROM pg_stat_activity WHERE datname = 'tracertm';"

# Profile memory usage
# Go backend
go tool pprof http://localhost:8080/debug/pprof/heap

# Python backend
pip install memray
memray run --live src/main.py
```

**Common Causes**:
- Unclosed database connections
- Event listener leaks
- Large object caching without eviction
- WebSocket connection leaks

**Solutions**:
- Ensure proper connection cleanup
- Implement connection pooling with limits
- Add cache eviction policies
- Use context managers for resources

---

### Connection Pool Exhaustion

**Symptoms**:
- "connection pool exhausted" errors
- Long wait times for database connections
- 503 Service Unavailable errors

**Diagnosis**:
```sql
-- Check current connections
SELECT
  count(*) as total,
  count(*) FILTER (WHERE state = 'active') as active,
  count(*) FILTER (WHERE state = 'idle') as idle,
  count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity
WHERE datname = 'tracertm';

-- Check connection limits
SHOW max_connections;
```

**Solutions**:
```python
# Increase pool size (.env)
DATABASE_POOL_SIZE=100
DATABASE_MAX_OVERFLOW=50

# Or use PgBouncer for connection pooling
# Install and configure PgBouncer
sudo apt install pgbouncer
```

---

## Best Practices

### 1. Always Start with Smoke Test

Before running expensive load tests, verify system is healthy:

```bash
# Quick smoke test
k6 run tests/load/k6/scenarios/smoke.js

# If smoke test fails, fix issues before proceeding
```

### 2. Run Tests in Sequence

Don't run multiple load tests simultaneously:

```bash
# Good: Sequential testing
k6 run tests/load/k6/scenarios/smoke.js
k6 run tests/load/k6/scenarios/load.js

# Bad: Parallel testing (skews results)
k6 run tests/load/k6/scenarios/load.js &
k6 run tests/load/k6/scenarios/stress.js &
```

### 3. Monitor System Resources

Always monitor while testing:

```bash
# Terminal 1: Run test
k6 run tests/load/k6/scenarios/load.js

# Terminal 2: Monitor resources
watch -n 1 'ps aux | grep -E "(go-backend|python-backend|postgres|redis)"'

# Terminal 3: Monitor logs
make dev-logs-follow
```

### 4. Establish Baselines

Create performance baselines for comparison:

```bash
# Run test and save baseline
k6 run --summary-export=baseline.json tests/load/k6/scenarios/load.js

# Move to baseline directory
mv baseline.json tests/load/.baseline/load-baseline.json
```

### 5. Test Realistic Scenarios

Use realistic data and usage patterns:

```javascript
// Good: Realistic user behavior
sleep(Math.random() * 5 + 2); // 2-7 seconds think time

// Bad: Unrealistic hammering
sleep(0.1); // Unrealistic 100ms think time
```

---

## Performance Optimization Checklist

After identifying performance issues:

- [ ] **Database Optimization**
  - [ ] Add missing indexes
  - [ ] Optimize slow queries
  - [ ] Implement query caching
  - [ ] Use connection pooling

- [ ] **Application Optimization**
  - [ ] Reduce N+1 queries
  - [ ] Implement API response caching
  - [ ] Optimize serialization
  - [ ] Use async/await properly

- [ ] **Infrastructure Optimization**
  - [ ] Enable compression (gzip)
  - [ ] Configure CDN for static assets
  - [ ] Implement rate limiting
  - [ ] Add load balancing

- [ ] **Monitoring & Alerting**
  - [ ] Set up performance dashboards
  - [ ] Configure latency alerts
  - [ ] Monitor error rates
  - [ ] Track resource usage trends

---

## Additional Resources

- **k6 Documentation**: https://k6.io/docs/
- **PostgreSQL Performance**: https://www.postgresql.org/docs/current/performance-tips.html
- **WebSocket Scalability**: https://www.nginx.com/blog/websocket-nginx/
- **Performance Testing Best Practices**: https://k6.io/docs/testing-guides/

---

## Summary

This guide provides comprehensive load testing coverage for TracerTM:

- ✅ **5 Test Scenarios**: Smoke, load, stress, spike, and soak tests
- ✅ **Database Testing**: Connection pool stress testing with pgbench
- ✅ **WebSocket Testing**: 5000+ concurrent connection validation
- ✅ **CI/CD Integration**: Automated regression detection
- ✅ **Performance Budgets**: Clear targets for all metrics
- ✅ **Troubleshooting**: Common issues and solutions

**Next Steps**:
1. Run smoke test to validate setup
2. Establish baseline with load test
3. Schedule regular soak tests
4. Monitor performance trends over time
