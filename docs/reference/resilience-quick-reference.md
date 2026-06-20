# Resilience Patterns - Quick Reference

## Circuit Breakers

### Backend

```go
// Execute with circuit breaker
result, err := resilience.Execute("github-api", func() (interface{}, error) {
    return githubClient.GetUser(ctx, username)
})

// With context
result, err := resilience.ExecuteWithContext(ctx, "github-api", func() (interface{}, error) {
    return githubClient.GetUser(ctx, username)
})

// Check state
state := resilience.GetGlobalManager().GetState("github-api")
isHealthy := resilience.GetGlobalManager().IsHealthy()
```

### Frontend

```typescript
import { globalRegistry } from '@/lib/resilience/CircuitBreaker';

// Execute with circuit breaker
const result = await globalRegistry.execute('github-api', async () => {
  return fetch('/api/github/user');
});

// Check state
const state = globalRegistry.getBreaker('github-api').getState();
const isHealthy = globalRegistry.isHealthy();
```

### Service Names

- `github-api` - GitHub API
- `linear-api` - Linear API
- `openai-api` - OpenAI API
- `anthropic-api` - Anthropic API
- `python-backend` - Python service
- `temporal` - Temporal workflows
- `redis` - Redis cache
- `neo4j` - Neo4j database
- `s3` - S3 storage

---

## Retry Policies

### Backend

```go
// Default retry policy
policy := resilience.DefaultRetryPolicy()
err := resilience.RetryWithPolicy(ctx, policy, func() error {
    return externalService.Call()
})

// With result
result, err := resilience.RetryWithPolicyAndResult(ctx, policy, func() (Response, error) {
    return externalService.CallWithResult()
})

// HTTP retry
resp, err := resilience.HTTPRetry(ctx, policy, client, req)

// Idempotency key
key := resilience.IdempotencyKey(requestID, attempt)
req.Header.Set("Idempotency-Key", key)
```

### Frontend

```typescript
import { RetryPolicies, RetryPolicy } from '@/lib/resilience/RetryPolicy';

// Use predefined policy
const result = await RetryPolicies.default.execute(async () => {
  return fetch('/api/data');
});

// Fetch with retry
const response = await RetryPolicies.default.fetch('/api/data');

// Custom policy
const policy = new RetryPolicy({
  maxRetries: 5,
  initialDelay: 500,
  maxDelay: 30000,
});
const result = await policy.execute(async () => { /* ... */ });

// Idempotency key
import { generateIdempotencyKey, withIdempotencyKey } from '@/lib/resilience/RetryPolicy';
const key = generateIdempotencyKey('request-123', attempt);
const options = withIdempotencyKey({ method: 'POST' }, key);
```

### Policy Types

| Policy | Max Retries | Initial Delay | Max Delay | Use Case |
|--------|-------------|---------------|-----------|----------|
| Default | 3 | 1s | 16s | General |
| Aggressive | 5 | 500ms | 32s | Critical |
| Conservative | 2 | 2s | 10s | Less critical |
| Quick | 2 | 500ms | 2s | Fast-failing |

---

## Health Checks

### Endpoints

```bash
# Comprehensive health
curl http://localhost:8080/health

# Kubernetes probes
curl http://localhost:8080/ready   # Readiness
curl http://localhost:8080/live    # Liveness
curl http://localhost:8080/startup # Startup

# Circuit breaker states
curl http://localhost:8080/circuit-breakers
```

### Health Status

- `healthy` - Component functioning normally
- `degraded` - Functioning but with issues
- `unhealthy` - Not functioning

### Thresholds

| Component | Degraded | Unhealthy |
|-----------|----------|-----------|
| Database | >1000ms | Connection failed |
| Redis | >500ms | Connection failed |
| Python Backend | >2000ms | HTTP 500+ |
| Disk | >80% | >90% |
| Memory | >75% | >85% |

---

## Middleware

### Backend

```go
// Resilience middleware
e.Use(middleware.ResilienceMiddleware(middleware.DefaultResilienceConfig()))

// Timeout middleware
e.Use(middleware.TimeoutMiddleware(30 * time.Second))

// Concurrency limiter
e.Use(middleware.ConcurrencyLimiter(1000))

// Error budget
errorBudget := middleware.NewErrorBudgetMiddleware(1*time.Hour, 0.01)
e.Use(errorBudget.Middleware())
```

---

## Monitoring

### Metrics

```
circuit_breaker_state{service="github-api"}
circuit_breaker_failures{service="github-api"}
retry_attempts_total
retry_success_rate
health_check_latency{component="database"}
error_rate
p95_latency
```

### Alerts

| Alert | Threshold | Severity |
|-------|-----------|----------|
| High Error Rate | >1% | Warning |
| Critical Error Rate | >5% | Critical |
| High Latency | P95 >2s | Warning |
| Critical Latency | P95 >5s | Critical |
| Circuit Open | >1 | Warning |
| Multiple Circuits Open | >3 | Critical |

---

## Rollback

### Manual Rollback

```bash
gh workflow run deployment-rollback.yml \
  -f environment=production \
  -f version=v1.2.3 \
  -f reason="Critical bug"
```

### Timeline

1. Detection: <1 min
2. Decision: <2 min
3. Execution: <5 min
4. **Total: <8 min**

---

## Best Practices

1. ✅ Use circuit breakers for all external services
2. ✅ Always use context with timeouts
3. ✅ Implement idempotency for retries
4. ✅ Log circuit breaker state changes
5. ✅ Set appropriate retry policies
6. ✅ Monitor error budgets
7. ✅ Implement health checks correctly
8. ✅ Test failure scenarios
9. ✅ Set realistic SLOs
10. ✅ Document runbooks

---

## Troubleshooting

### Circuit Breaker Stuck Open

```go
// Check state
state := manager.GetState("service-name")
counts := manager.GetCounts("service-name")

// Manual reset (emergency only)
manager.GetOrCreateBreaker("service-name").Reset()
```

### Retry Storm

- Enable retry budgets
- Reduce max retries
- Increase backoff delays

### Health Check Failures

```bash
curl -v http://localhost:8080/health | jq
```

---

## Quick Links

- [Full Guide](../guides/production-hardening-guide.md)
- [Implementation Summary](../reports/task-95-production-hardening-summary.md)
- [Circuit Breaker Source](../../backend/internal/resilience/circuit_breaker.go)
- [Retry Policy Source](../../backend/internal/resilience/retry.go)
- [Health Checks Source](../../backend/internal/health/checks.go)
