# Production Hardening Guide

## Overview

This guide covers production-grade error handling and resilience patterns implemented in TraceRTM to ensure 99.9% uptime and zero unhandled errors in production.

## Table of Contents

1. [Circuit Breakers](#circuit-breakers)
2. [Retry Policies](#retry-policies)
3. [Graceful Degradation](#graceful-degradation)
4. [Health Checks](#health-checks)
5. [Automated Rollback](#automated-rollback)
6. [Monitoring and Alerting](#monitoring-and-alerting)
7. [Best Practices](#best-practices)

---

## Circuit Breakers

Circuit breakers prevent cascading failures by stopping requests to failing services and allowing them time to recover.

### Backend Implementation

```go
import (
    "github.com/kooshapari/tracertm-backend/internal/resilience"
)

// Execute with circuit breaker protection
result, err := resilience.Execute("github-api", func() (interface{}, error) {
    return githubClient.GetUser(ctx, username)
})
```

### Circuit Breaker States

- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Service is failing, requests fail immediately
- **HALF_OPEN**: Testing recovery, limited requests allowed

### Configuration

```go
config := resilience.CircuitBreakerConfig{
    MaxRequests:   1,                    // Test requests in half-open
    Interval:      10 * time.Second,     // Failure counting window
    Timeout:       30 * time.Second,     // Open state duration
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        // Trip after 5 failures in 10 seconds OR >50% failure rate
        failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
        return counts.ConsecutiveFailures >= 5 ||
               (counts.TotalFailures >= 5 && failureRatio >= 0.5)
    },
}

manager := resilience.NewCircuitBreakerManagerWithConfig(config)
```

### Frontend Implementation

```typescript
import { globalRegistry } from '@/lib/resilience/CircuitBreaker';

// Execute with circuit breaker
const result = await globalRegistry.execute('github-api', async () => {
  return fetch('/api/github/user');
});
```

### Service Names

Use consistent service names across your application:

- `github-api` - GitHub API calls
- `linear-api` - Linear API calls
- `openai-api` - OpenAI API calls
- `anthropic-api` - Anthropic API calls
- `python-backend` - Python backend service
- `temporal` - Temporal workflow service
- `redis` - Redis cache
- `neo4j` - Neo4j graph database
- `s3` - S3 storage

---

## Retry Policies

Retry policies handle transient failures with exponential backoff and jitter.

### Backend Implementation

```go
import (
    "github.com/kooshapari/tracertm-backend/internal/resilience"
)

// Use default retry policy
policy := resilience.DefaultRetryPolicy()

err := resilience.RetryWithPolicy(ctx, policy, func() error {
    return externalService.Call()
})

// Use with result
result, err := resilience.RetryWithPolicyAndResult(ctx, policy, func() (Response, error) {
    return externalService.CallWithResult()
})
```

### Retry Policy Types

**Default Policy** (General use):
- Max retries: 3
- Initial delay: 1s
- Max delay: 16s
- Multiplier: 2.0
- Jitter: ±20%

**Aggressive Policy** (Critical operations):
- Max retries: 5
- Initial delay: 500ms
- Max delay: 32s

**Conservative Policy** (Less critical):
- Max retries: 2
- Initial delay: 2s
- Max delay: 10s

### Retry Sequence

```
Attempt 1: Immediate
Attempt 2: ~1s delay (0.8s - 1.2s with jitter)
Attempt 3: ~2s delay (1.6s - 2.4s with jitter)
Attempt 4: ~4s delay (3.2s - 4.8s with jitter)
```

### Frontend Implementation

```typescript
import { RetryPolicies } from '@/lib/resilience/RetryPolicy';

// Use predefined policy
const result = await RetryPolicies.default.execute(async () => {
  return fetch('/api/data');
});

// Custom policy
const policy = new RetryPolicy({
  maxRetries: 5,
  initialDelay: 500,
  maxDelay: 30000,
});

const result = await policy.fetch('/api/critical-operation');
```

### Idempotency Keys

Always use idempotency keys for retryable operations:

```go
// Backend
key := resilience.IdempotencyKey(requestID, attempt)
req.Header.Set("Idempotency-Key", key)

// Frontend
import { generateIdempotencyKey, withIdempotencyKey } from '@/lib/resilience/RetryPolicy';

const key = generateIdempotencyKey('request-123', attempt);
const options = withIdempotencyKey({ method: 'POST' }, key);
```

---

## Graceful Degradation

Graceful degradation ensures the system continues to function with reduced capabilities when dependencies fail.

### Feature Flags

Enable/disable non-critical features:

```go
if featureFlags.IsEnabled("ai-suggestions") {
    suggestions, err := aiService.GetSuggestions(ctx)
    if err != nil {
        log.Warn("AI suggestions unavailable, continuing without them")
        // Continue with degraded functionality
    }
}
```

### Fallback Modes

**Cached Data Fallback**:
```go
// Try live data first
data, err := liveService.GetData(ctx)
if err != nil {
    // Fallback to cache
    data, err = cache.Get(ctx, cacheKey)
    if err == nil {
        c.Response().Header().Set("X-Data-Source", "cache")
        return data
    }
}
```

**Reduced Functionality**:
```typescript
// Try full feature
try {
  const aiAnalysis = await aiService.analyze(data);
  return { ...data, aiAnalysis };
} catch (error) {
  console.warn('AI analysis unavailable, returning basic data');
  return { ...data, aiAnalysis: null };
}
```

### User Messaging

Always inform users about degraded service:

```go
c.Response().Header().Set("X-Service-Status", "degraded")
c.Response().Header().Set("X-Degradation-Reason", "AI service temporarily unavailable")
```

---

## Health Checks

Comprehensive health checks ensure system reliability.

### Health Check Endpoints

```
GET /health      - Comprehensive health check
GET /ready       - Readiness probe (Kubernetes)
GET /live        - Liveness probe (Kubernetes)
```

### Backend Implementation

```go
import (
    "github.com/kooshapari/tracertm-backend/internal/health"
)

// Create health checker
checker := health.NewHealthChecker(
    db,
    redisClient,
    pythonBackendURL,
    temporalURL,
    version,
)

// Health check handler
func HealthHandler(c echo.Context) error {
    report := checker.Check(c.Request().Context())

    statusCode := http.StatusOK
    if report.Status == health.HealthStatusUnhealthy {
        statusCode = http.StatusServiceUnavailable
    }

    return c.JSON(statusCode, report)
}
```

### Health Report Structure

```json
{
  "status": "healthy",
  "version": "v1.0.0",
  "timestamp": "2026-02-01T12:00:00Z",
  "components": {
    "database": {
      "name": "database",
      "status": "healthy",
      "message": "connection ok",
      "latency_ms": 5
    },
    "redis": {
      "name": "redis",
      "status": "healthy",
      "message": "connection ok",
      "latency_ms": 2
    },
    "python-backend": {
      "name": "python-backend",
      "status": "healthy",
      "message": "connection ok",
      "latency_ms": 15
    }
  },
  "metrics": {
    "disk_total_gb": 100,
    "disk_free_gb": 50,
    "disk_used_percent": 50.0,
    "memory_total_gb": 16,
    "memory_available_gb": 8,
    "memory_used_percent": 50.0
  }
}
```

### Component Health Statuses

- **healthy**: Component is functioning normally
- **degraded**: Component is functioning but with issues (high latency, etc.)
- **unhealthy**: Component is not functioning

### Thresholds

**Disk Space**:
- Warning: >80% used
- Critical: >90% used

**Memory**:
- Warning: >75% used
- Critical: >85% used

**Latency**:
- Database: >1000ms = degraded
- Redis: >500ms = degraded
- Python Backend: >2000ms = degraded

---

## Automated Rollback

Automated rollback ensures rapid recovery from failed deployments.

### Trigger Conditions

Rollback triggers automatically when:

1. **Error Rate Spike**: >5% error rate for 5 minutes
2. **Health Check Failures**: 3 consecutive health check failures
3. **Performance Degradation**: P95 latency >3x baseline

### Manual Rollback

```bash
# Trigger manual rollback via GitHub Actions
gh workflow run deployment-rollback.yml \
  -f environment=production \
  -f version=v1.2.3 \
  -f reason="Critical bug in authentication"
```

### Rollback Process

1. **Validation**: Verify target version exists
2. **Pre-rollback Health Check**: Document current state
3. **Backend Rollback**: Rollback container deployment
4. **Stabilization**: Wait 30 seconds
5. **Health Check**: Verify rollback success
6. **Frontend Rollback**: Rollback frontend deployment
7. **Smoke Tests**: Run critical path tests
8. **Monitoring**: Monitor error rates for 30 minutes

### Rollback Timeline

- Detection: <1 minute
- Decision: <2 minutes
- Execution: <5 minutes
- **Total Recovery Time: <8 minutes**

### Post-Rollback

1. Create incident report
2. Notify team via Slack/PagerDuty
3. Schedule post-mortem
4. Fix original issue
5. Create hotfix deployment

---

## Monitoring and Alerting

### Metrics to Monitor

**Error Rates**:
- Overall error rate
- Error rate per endpoint
- Error rate per service

**Latency**:
- P50, P95, P99 latency
- Per-endpoint latency
- Database query latency

**Circuit Breaker States**:
- Number of open circuits
- Circuit state transitions
- Failure counts

**Retry Attempts**:
- Retry success rate
- Average retries per request
- Retry budget exhaustion

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error Rate | >1% | >5% |
| P95 Latency | >2s | >5s |
| Open Circuits | >1 | >3 |
| Disk Usage | >80% | >90% |
| Memory Usage | >75% | >85% |

### Integration Points

**Sentry**: Error tracking and alerting
- Configure DSN in environment
- Automatic error capture
- Release tracking

**Prometheus**: Metrics collection
- Circuit breaker states
- Retry attempts
- Health check results

**Grafana**: Dashboards and visualization
- Real-time system health
- Historical trends
- SLO tracking

---

## Best Practices

### 1. Use Circuit Breakers for All External Services

```go
// ✅ Good
result, err := resilience.Execute("github-api", func() (interface{}, error) {
    return githubClient.GetUser(ctx, username)
})

// ❌ Bad
result, err := githubClient.GetUser(ctx, username)
```

### 2. Always Use Context for Timeouts

```go
// ✅ Good
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

// ❌ Bad
ctx := context.Background() // No timeout
```

### 3. Implement Idempotency for Retries

```go
// ✅ Good
key := resilience.IdempotencyKey(requestID, attempt)
req.Header.Set("Idempotency-Key", key)

// ❌ Bad
// No idempotency key = duplicate operations on retry
```

### 4. Log Circuit Breaker State Changes

```go
config.OnStateChange = func(name string, from, to gobreaker.State) {
    log.Printf("Circuit [%s]: %s -> %s", name, from, to)
    // Send alert to Slack/PagerDuty
}
```

### 5. Set Appropriate Retry Policies

```go
// Critical operations
policy := resilience.AggressiveRetryPolicy()

// User-facing operations
policy := resilience.DefaultRetryPolicy()

// Background jobs
policy := resilience.ConservativeRetryPolicy()
```

### 6. Monitor Error Budgets

```go
// Track error budget
errorBudget := middleware.NewErrorBudgetMiddleware(
    1*time.Hour,  // Window
    0.01,         // 1% error budget
)
```

### 7. Implement Health Checks Correctly

```go
// ✅ Good - Check actual dependencies
func (hc *HealthChecker) CheckDatabase(ctx context.Context) ComponentHealth {
    err := hc.db.PingContext(ctx)
    // Return status based on actual check
}

// ❌ Bad - Always return healthy
func BadHealthCheck() { return "healthy" }
```

### 8. Test Failure Scenarios

```go
// Test circuit breaker trips
for i := 0; i < 5; i++ {
    manager.Execute("test-service", func() (interface{}, error) {
        return nil, errors.New("failure")
    })
}
assert.Equal(t, gobreaker.StateOpen, manager.GetState("test-service"))
```

### 9. Set Realistic SLOs

- **Availability**: 99.9% (8.76 hours downtime/year)
- **Error Rate**: <1%
- **P95 Latency**: <2 seconds
- **Recovery Time**: <30 seconds

### 10. Document Runbooks

Create runbooks for common scenarios:
- Circuit breaker open
- High error rate
- Failed deployment
- Database connection issues
- Cache unavailable

---

## Success Criteria

✅ **99.9% Uptime**
- Measured over rolling 30-day window
- Excludes planned maintenance

✅ **Zero Unhandled Errors**
- All errors caught and logged
- User-friendly error messages
- Automatic retry or fallback

✅ **<30 Second Recovery Time**
- From failure detection to recovery
- Circuit breakers transition to half-open
- Service returns to normal operation

✅ **<5% Error Rate During Incidents**
- Even during partial outages
- Graceful degradation maintains core functionality

---

## Troubleshooting

### Circuit Breaker Stuck Open

**Symptoms**: Requests fail immediately with circuit breaker error

**Diagnosis**:
```go
state := manager.GetState("service-name")
counts := manager.GetCounts("service-name")
log.Printf("State: %s, Failures: %d", state, counts.TotalFailures)
```

**Resolution**:
1. Check service health
2. Fix underlying issue
3. Wait for automatic recovery (30s)
4. Or manually reset: `manager.GetOrCreateBreaker("service-name").Reset()`

### Retry Storm

**Symptoms**: High request volume, performance degradation

**Diagnosis**:
- Check retry budget exhaustion
- Monitor retry attempt metrics

**Resolution**:
1. Enable retry budgets
2. Reduce max retries
3. Increase backoff delays
4. Add jitter to prevent thundering herd

### Health Check Failures

**Symptoms**: /health endpoint returns 503

**Diagnosis**:
```bash
curl -v http://localhost:8080/health | jq
```

**Resolution**:
1. Check component statuses in response
2. Verify database connectivity
3. Check Redis connectivity
4. Verify external service availability

---

## Additional Resources

- [Circuit Breaker Pattern (Martin Fowler)](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Retry Pattern (Microsoft)](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Health Check Pattern](https://microservices.io/patterns/observability/health-check-api.html)
- [Site Reliability Engineering Book](https://sre.google/sre-book/table-of-contents/)

---

## Support

For issues or questions:
- Create an issue on GitHub
- Contact the SRE team
- Check #engineering-support on Slack
