# Load Testing Integration Guide

This guide covers the k6 load testing framework integrated into the TraceRTM CI/CD pipeline.

## Overview

Load testing is automatically executed on:
- All pull requests to `main` or `develop` branches
- Weekly scheduled runs (Monday 2 AM UTC)

The tests validate performance thresholds and detect regressions against a baseline.

## Quick Start

### Running Load Tests Locally

```bash
# Install k6
brew install k6  # macOS
# or apt-get install k6  # Linux

# Run with default settings
cd backend/tests/performance
k6 run load_test.js

# Run against specific API
k6 run --env API_URL=http://localhost:3030 load_test.js

# Quick smoke test (30 seconds, 1 user)
k6 run --vus 1 --duration 30s load_test.js

# Stress test (ramp up to 500 users)
k6 run --stage 2m:0,5m:500,2m:0 load_test.js
```

### Validating Against Thresholds

```bash
# Generate results file
k6 run load_test.js --out json=results.json

# Validate thresholds
node check-thresholds.js results.json

# Compare against baseline
node check-thresholds.js results.json .github/performance-baseline.json
```

## Performance Thresholds

The CI/CD pipeline enforces these thresholds:

| Metric | Threshold | Notes |
|--------|-----------|-------|
| P95 Latency | < 500ms | 95th percentile response time |
| P99 Latency | < 1000ms | 99th percentile response time |
| Error Rate | < 1% | Percentage of failed requests |
| RPS | > 100 | Requests per second (warning only in CI) |
| Regression | < 10% | Performance degradation vs baseline |

## Load Test Stages

The test uses a realistic ramp-up pattern:

```
Stage 1: 0→10 VUs over 1m   (Ramp up to 10 users)
Stage 2: 10 VUs for 3m      (Steady state at 10 users)
Stage 3: 10→50 VUs over 1m  (Ramp up to 50 users)
Stage 4: 50 VUs for 3m      (Steady state at 50 users)
Stage 5: 50→100 VUs over 1m (Spike to 100 users)
Stage 6: 100 VUs for 2m     (Sustained load)
Stage 7: 100→0 VUs over 1m  (Ramp down)

Total Duration: ~13 minutes
```

## CI/CD Pipeline

### GitHub Actions Workflow

The workflow (`.github/workflows/load-test.yml`) executes:

1. **Setup**
   - Checkout code
   - Install k6
   - Start backend service

2. **Run Tests**
   - Execute k6 load test
   - Generate JSON and CSV results
   - Capture output log

3. **Validate**
   - Check threshold violations
   - Compare against baseline
   - Detect performance regressions

4. **Report**
   - Post PR comments with results
   - Upload artifacts (30-day retention)
   - Update performance baseline

### Viewing Results

#### In Pull Requests
- Look for the "Load Testing Results" comment on your PR
- Shows key metrics and threshold status

#### In GitHub Actions
- Navigate to Actions → "Load Testing" workflow
- Download "k6-load-tests/results-*" artifact
- Contains: `results.json`, `results.csv`, `output.log`

## Performance Regression Detection

The system automatically compares results against a baseline:

```
Baseline Storage: .github/performance-baseline.json
Update Trigger:   Main branch successful runs
Regression Threshold: 10% degradation
```

## Troubleshooting

### High Latency in Load Tests

1. Check database slow query logs
2. Review connection pool exhaustion
3. Look for N+1 query patterns
4. Profile CPU/memory usage

### High Error Rate

1. Backend service not running
2. Authentication failures
3. Rate limiting triggered
4. Resource exhaustion

### Connection Refused

Verify backend is running:
```bash
curl http://localhost:3030/health
```

## Best Practices

1. Run load tests locally before major changes
2. Compare against baseline to detect regressions
3. Investigate any >10% regression
4. Monitor database performance after migrations

## Configuration Files

- `.github/workflows/load-test.yml` - Main CI/CD workflow
- `backend/tests/performance/load_test.js` - Load test script
- `backend/tests/performance/check-thresholds.js` - Validation tool
- `.github/performance-baseline.json` - Performance baseline (auto-managed)

## References

- [k6 Documentation](https://k6.io/docs/)
- [k6 Thresholds](https://k6.io/docs/using-k6/thresholds/)
- [GitHub Actions](https://docs.github.com/en/actions)
