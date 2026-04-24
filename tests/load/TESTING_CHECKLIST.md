# Load Testing Checklist

Pre-flight checklist for running load tests on TracerTM.

## Pre-Test Setup

### 1. Environment Preparation

- [ ] All services running (`make dev`)
- [ ] Database migrations applied (`./scripts/run_python_migrations.sh`)
- [ ] No existing load on system
- [ ] k6 installed (`k6 version`)
- [ ] PostgreSQL accessible (`pg_isready -h localhost -p 5432`)

### 2. System Health Check

- [ ] Health endpoint responding: `curl http://localhost:4000/health`
- [ ] Database connections available
- [ ] Redis cache working
- [ ] No recent errors in logs

### 3. Resource Availability

- [ ] Sufficient disk space (> 10GB free)
- [ ] Network connectivity stable
- [ ] System not under other load
- [ ] Monitoring accessible (Grafana, Prometheus)

## Test Execution

### Smoke Test (1 minute)

- [ ] Run: `make load-test-smoke`
- [ ] All checks passing (100%)
- [ ] Error rate < 1%
- [ ] P95 latency < 500ms
- [ ] Review results before proceeding

### Load Test (18 minutes)

- [ ] Smoke test passed
- [ ] Run: `make load-test-load`
- [ ] Save results: `k6 run --summary-export=load-summary.json tests/load/k6/scenarios/load.js`
- [ ] Error rate < 0.1%
- [ ] P95 latency < 500ms
- [ ] Throughput > 500 req/s

### Stress Test (25 minutes)

- [ ] Load test passed
- [ ] Monitor system resources during test
- [ ] Run: `make load-test-stress`
- [ ] Note breaking points
- [ ] Error rate < 5%
- [ ] System remains stable

### Spike Test (7.5 minutes)

- [ ] Run: `make load-test-spike`
- [ ] Rate limiting activates
- [ ] System recovers after spike
- [ ] No crashes or permanent degradation

### Soak Test (2+ hours)

- [ ] Run in background: `nohup make load-test-soak > soak-test.log 2>&1 &`
- [ ] Monitor periodically: `tail -f soak-test.log`
- [ ] Check for memory leaks
- [ ] No performance degradation over time
- [ ] No connection leaks

### WebSocket Test (23 minutes)

- [ ] Run: `make load-test-websocket`
- [ ] 5000+ connections established
- [ ] Message latency < 200ms (P95)
- [ ] Connection stability maintained

### Database Test (10 minutes)

- [ ] PostgreSQL running
- [ ] Run: `make load-test-database`
- [ ] 1000+ connections handled
- [ ] No connection pool exhaustion
- [ ] Query performance acceptable

## Post-Test Analysis

### Result Collection

- [ ] k6 results saved (`*.json` files)
- [ ] Logs collected
- [ ] System metrics captured
- [ ] Screenshots of monitoring dashboards

### Performance Analysis

- [ ] Compare with baseline: `make load-test-compare`
- [ ] Generate report: `make load-test-report`
- [ ] Review all metrics
- [ ] Identify any regressions

### Metric Review

Response Time:
- [ ] P50 < 200ms
- [ ] P95 < 500ms
- [ ] P99 < 1000ms

Error Rate:
- [ ] Normal load < 0.1%
- [ ] Stress test < 5%
- [ ] Spike test < 10%

Throughput:
- [ ] Load test > 500 req/s
- [ ] Stress test > 1000 req/s

Resource Utilization:
- [ ] CPU < 70%
- [ ] Memory < 80%
- [ ] DB connections < 70% pool

### Issue Identification

- [ ] Any performance regressions?
- [ ] Any new errors?
- [ ] Any resource exhaustion?
- [ ] Any memory leaks?

## Baseline Management

### Establish New Baseline

- [ ] Tests passing consistently
- [ ] No known issues
- [ ] System in stable state
- [ ] Copy results to baseline directory:
  ```bash
  cp load-test-summary.json tests/load/.baseline/load-baseline.json
  git add tests/load/.baseline/
  git commit -m "Update performance baseline"
  ```

## Reporting

### Success Case

- [ ] All tests passed
- [ ] No regressions detected
- [ ] Performance within budgets
- [ ] Document results

### Regression Case

- [ ] Create performance regression issue
- [ ] Attach test results
- [ ] Identify suspected cause
- [ ] Tag relevant team members

## Cleanup

- [ ] Stop long-running tests
- [ ] Archive test results
- [ ] Clean temporary files
- [ ] Document findings
- [ ] Update baselines if needed

## Next Steps

- [ ] Schedule regular testing (weekly/monthly)
- [ ] Monitor trends over time
- [ ] Optimize identified bottlenecks
- [ ] Update performance budgets as needed

---

**Last Updated**: 2026-02-01
**Maintained By**: Performance Team
