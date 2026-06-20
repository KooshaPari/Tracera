---
name: Performance Regression
about: Report performance degradation detected in load tests
title: '[PERF] Performance regression in [component/endpoint]'
labels: performance, regression
assignees: ''
---

## Performance Regression Details

**Test Type**: <!-- smoke/load/stress/spike/soak -->
**Detected In**: <!-- PR number, commit hash, or workflow run -->
**Environment**: <!-- development/staging/production -->

## Metrics

### Response Time Degradation
- **Baseline P95**: <!-- e.g., 450ms -->
- **Current P95**: <!-- e.g., 650ms -->
- **Change**: <!-- e.g., +44% -->

### Error Rate
- **Baseline**: <!-- e.g., 0.05% -->
- **Current**: <!-- e.g., 0.15% -->
- **Change**: <!-- e.g., +200% -->

### Throughput
- **Baseline**: <!-- e.g., 520 req/s -->
- **Current**: <!-- e.g., 380 req/s -->
- **Change**: <!-- e.g., -27% -->

## Affected Endpoints/Components

<!-- List endpoints or components showing degradation -->

- [ ] `/api/v1/projects`
- [ ] `/api/v1/items`
- [ ] `/api/v1/search`
- [ ] `/api/v1/graphs`
- [ ] WebSocket connections
- [ ] Database queries
- [ ] Other: ___

## Test Results

**k6 Summary**:
```
<!-- Paste k6 summary output -->
```

**Comparison Report**:
```
<!-- Paste output from compare-performance.py -->
```

## System State During Test

### Resource Utilization
- **CPU**: <!-- e.g., 85% peak -->
- **Memory**: <!-- e.g., 4.2GB / 8GB -->
- **Database Connections**: <!-- e.g., 450 / 500 -->

### Error Logs
<!-- Any relevant error messages from logs -->
```
<!-- Paste errors here -->
```

## Suspected Cause

<!-- What changes might have caused this regression? -->

- [ ] Recent code changes in PR #___
- [ ] Database schema changes
- [ ] Configuration changes
- [ ] Infrastructure changes
- [ ] Dependency updates
- [ ] Unknown

## Reproduction Steps

1. Start services: `make dev`
2. Run test: `make load-test-___`
3. Compare with baseline: `make load-test-compare`

## Performance Report

<!-- Attach or link to generated performance report -->

**Report Link**: <!-- e.g., GitHub Actions artifact URL -->

## Additional Context

<!-- Any other relevant information -->

## Checklist

- [ ] Performance regression confirmed with multiple test runs
- [ ] Baseline comparison performed
- [ ] System logs reviewed
- [ ] Resource utilization checked
- [ ] Related PRs/commits identified
- [ ] Performance report attached/linked
