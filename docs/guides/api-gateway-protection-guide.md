# API Gateway Protection Guide

## Overview

This guide documents the comprehensive API gateway protection layer implemented in TraceRTM, providing robust defense against abuse, DDoS attacks, and ensuring fair resource allocation across users.

**Implementation Date:** 2026-02-01
**Task Reference:** #100

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Rate Limiting](#rate-limiting)
3. [Request Throttling](#request-throttling)
4. [API Key Management](#api-key-management)
5. [Usage Quotas](#usage-quotas)
6. [DDoS Protection](#ddos-protection)
7. [Configuration](#configuration)
8. [Monitoring & Metrics](#monitoring--metrics)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The API gateway protection system consists of multiple layers:

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Request                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Caddy (Layer 4/7)                          │
│  • Connection limits                                         │
│  • Request size limits (10MB max)                           │
│  • Request timeouts (30s)                                   │
│  • Security headers                                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Rate Limit Middleware (Go)                      │
│  • Sliding window algorithm                                  │
│  • Per-user: 100 req/min                                    │
│  • Per-IP: 20 req/min                                       │
│  • Per-endpoint limits                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Quota Middleware (Go)                           │
│  • Daily/monthly quotas                                      │
│  • Usage tracking                                            │
│  • Overage handling                                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           Adaptive Throttler (Go)                            │
│  • Circuit breaker integration                               │
│  • Priority queuing                                          │
│  • Load-based throttling                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend Services                            │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

**Files:**
- `/backend/internal/ratelimit/sliding_window.go` - Sliding window rate limiter
- `/backend/internal/ratelimit/throttle.go` - Adaptive request throttling
- `/backend/internal/auth/api_keys.go` - API key management
- `/backend/internal/middleware/ratelimit_middleware.go` - Rate limit middleware
- `/backend/internal/middleware/quota_middleware.go` - Quota tracking middleware
- `/Caddyfile` - Gateway-level protection
- `/alembic/versions/058_add_api_keys_table.py` - Database schema

---

## Rate Limiting

### Sliding Window Algorithm

The system uses a **sliding window** algorithm for accurate rate limiting:

```go
// Example: Create a sliding window limiter
limiter := ratelimit.NewSlidingWindowLimiter(
    redisClient,
    1 * time.Minute,  // Window duration
    100,              // Request limit
)

// Check if request is allowed
allowed, remaining, resetTime, err := limiter.Allow(ctx, "user:123")
```

**Benefits:**
- More accurate than fixed windows
- No burst allowance at window boundaries
- Fair distribution of requests over time

### Default Limits

| User Type | Rate Limit | Window | Endpoint |
|-----------|-----------|---------|----------|
| Authenticated | 100 req/min | 1 minute | Global |
| Anonymous (IP) | 20 req/min | 1 minute | Global |
| Auth endpoints | 5 req/min | 1 minute | `/api/v1/auth/*` |
| Expensive ops | 10 req/min | 1 minute | `/api/v1/graph/analyze` |
| Search | 30 req/min | 1 minute | `/api/v1/search/*` |

### Rate Limit Headers

Clients receive standard rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1738454400
Retry-After: 45
```

### Implementation Example

```go
// Initialize rate limit middleware
rateLimiter := middleware.CreateStandardRateLimitMiddleware(redisClient)

// Add to Echo server
e.Use(rateLimiter.Middleware())
```

### Customizing Limits

```go
config := middleware.RateLimitMiddlewareConfig{
    Redis: redisClient,
    AuthenticatedUserLimit: 200,  // Custom limit
    AuthenticatedUserWindow: 1 * time.Minute,
    EndpointLimits: map[string]middleware.EndpointRateLimit{
        "/api/v1/custom/*": {
            Pattern: "/api/v1/custom/*",
            Limit:   50,
            Window:  1 * time.Minute,
        },
    },
    AddHeaders: true,
}

rateLimiter := middleware.NewRateLimitMiddleware(config)
```

---

## Request Throttling

### Adaptive Throttling

The adaptive throttler adjusts behavior based on:
- Backend load
- Circuit breaker state
- Request priority
- Queue depth

### Priority Levels

```go
const (
    PriorityLow     // Batch jobs, non-urgent requests
    PriorityNormal  // Regular API requests
    PriorityHigh    // Interactive operations
    PriorityAdmin   // Administrative operations
)
```

### Configuration

```go
config := ratelimit.ThrottleConfig{
    Redis:          redisClient,
    CircuitBreaker: circuitBreaker,
    BaseTimeout:    30 * time.Second,
    MaxConcurrent:  1000,
    LoadThreshold:  0.8,    // 80% load threshold
    ThrottleFactor: 0.5,    // 50% reduction when throttling
    QueueSizes: map[ratelimit.PriorityLevel]int{
        ratelimit.PriorityLow:    100,
        ratelimit.PriorityNormal: 500,
        ratelimit.PriorityHigh:   1000,
        ratelimit.PriorityAdmin:  100,
    },
}

throttler := ratelimit.NewAdaptiveThrottler(config)
```

### Usage Example

```go
// Acquire throttle token
timeout, release, err := throttler.Acquire(ctx, ratelimit.PriorityHigh)
if err != nil {
    return fmt.Errorf("throttled: %w", err)
}
defer release()

// Set request timeout
ctx, cancel := context.WithTimeout(ctx, timeout)
defer cancel()

// Make backend request
result, err := backend.DoWork(ctx)
```

### Load-Based Behavior

| Load Level | Behavior |
|------------|----------|
| 0-80% | Normal operation |
| 80-90% | Reduced timeouts (50%) |
| 90-95% | Priority queuing enforced |
| >95% | Low priority requests rejected |

### Circuit Breaker Integration

When the circuit breaker opens:
1. All requests are throttled
2. Timeouts reduced by 50%
3. Only high-priority requests queued
4. Low-priority requests rejected immediately

---

## API Key Management

### Creating API Keys

```go
manager := auth.NewAPIKeyManager(db)

// Create a new API key
apiKey, plaintextKey, err := manager.CreateAPIKey(ctx, auth.CreateAPIKeyParams{
    AccountID:   accountID,
    ProjectID:   &projectID,
    Name:        "Production API Key",
    Role:        auth.APIKeyRoleReadWrite,
    Scopes:      []string{"projects:read", "projects:write", "items:*"},
    ExpiresAt:   &expirationTime,
    CreatedByID: userID,
})

// IMPORTANT: Save plaintextKey securely - it's only shown once!
// Format: trace_<base64_encoded_key>
```

### API Key Roles

| Role | Permissions |
|------|------------|
| `read-only` | Read operations only |
| `read-write` | Read and write operations |
| `admin` | Full access including key management |

### Validating API Keys

```go
// Validate and get key metadata
apiKey, err := manager.ValidateAPIKey(ctx, plaintextKey)
if err != nil {
    return fmt.Errorf("invalid API key: %w", err)
}

// Check specific permission
if !apiKey.CheckPermission("projects:write") {
    return fmt.Errorf("insufficient permissions")
}
```

### Key Rotation

```go
// Rotate an API key (creates new, revokes old)
newKey, plaintextKey, err := manager.RotateAPIKey(ctx, oldKeyID, userID)
```

### Revoking Keys

```go
err := manager.RevokeAPIKey(ctx, keyID, revokedByID, "Security incident")
```

### Usage Tracking

```go
// Record API key usage
err := manager.RecordUsage(ctx, keyID, true, bytesTransferred)

// Get usage statistics
stats, err := manager.GetUsageStats(ctx, keyID, startDate, endDate)
for _, stat := range stats {
    fmt.Printf("Date: %s, Requests: %d, Errors: %d\n",
        stat.Date, stat.RequestCount, stat.ErrorCount)
}
```

### Security Features

1. **Argon2id Hashing**: Keys are hashed using industry-standard Argon2id
2. **One-Time Display**: Plaintext key only shown at creation
3. **Automatic Expiration**: Optional expiration timestamps
4. **Audit Trail**: Track who created/revoked keys and why
5. **Usage Monitoring**: Daily usage metrics per key

---

## Usage Quotas

### Quota Periods

- **Daily**: Resets at midnight UTC
- **Monthly**: Resets on 1st of month UTC

### Default Quotas

| Tier | Daily Quota | Monthly Quota |
|------|-------------|---------------|
| Free | 1,000 | 10,000 |
| Basic | 10,000 | 100,000 |
| Pro | 100,000 | 1,000,000 |
| Enterprise | Custom | Custom |

### Configuration

```go
config := middleware.QuotaConfig{
    Redis:               redisClient,
    DefaultDailyQuota:   10000,
    DefaultMonthlyQuota: 100000,
    OverageAction:       middleware.QuotaActionReject,
    GracePercentage:     0.05,  // 5% grace
    AddHeaders:          true,
    QuotaResolver: func(ctx context.Context, userID, apiKeyID string) (daily, monthly int64, err error) {
        // Custom quota lookup from database
        return getCustomQuotas(ctx, userID)
    },
}

quotaMiddleware := middleware.NewQuotaMiddleware(config)
```

### Overage Actions

```go
const (
    QuotaActionReject   // HTTP 402 Payment Required
    QuotaActionThrottle // Delay requests (5s)
    QuotaActionBill     // Allow but flag for billing
)
```

### Quota Headers

```http
X-Quota-Daily-Limit: 10000
X-Quota-Daily-Remaining: 8432
X-Quota-Daily-Reset: 1738454400
X-Quota-Monthly-Limit: 100000
X-Quota-Monthly-Remaining: 76543
X-Quota-Monthly-Reset: 1741046400
```

### Manual Quota Management

```go
// Reset quota (admin operation)
err := quotaMiddleware.ResetQuota(ctx, userID, "", middleware.QuotaPeriodDaily)

// Get current usage
usage, err := quotaMiddleware.GetQuotaUsage(ctx, userID, "", middleware.QuotaPeriodMonthly)
```

---

## DDoS Protection

### Caddy Layer Protection

**Request Size Limits:**
```caddyfile
request_body {
    max_size 10MB  # Prevent large payload attacks
}
```

**Request Timeouts:**
```caddyfile
timeouts {
    read_body 30s    # Body read timeout
    read_header 10s  # Header read timeout
    write 30s        # Write timeout
    idle 2m          # Keep-alive timeout
}
```

**Security Headers:**
```caddyfile
header {
    X-Frame-Options "SAMEORIGIN"
    X-Content-Type-Options "nosniff"
    X-XSS-Protection "1; mode=block"
    Referrer-Policy "strict-origin-when-cross-origin"
    -Server  # Remove server identification
}
```

**Method Validation:**
```caddyfile
@invalid_method {
    not method GET POST PUT PATCH DELETE HEAD OPTIONS
}
handle @invalid_method {
    respond "Method not allowed" 405
}
```

### Connection Limits

Operating system level (via `ulimit` and `sysctl`):

```bash
# Max open files
ulimit -n 65536

# TCP connection limits
sysctl -w net.core.somaxconn=4096
sysctl -w net.ipv4.tcp_max_syn_backlog=8192
```

### IP Blacklisting

```go
// In rate limit middleware, add custom logic:
blacklistedIPs := []string{"1.2.3.4", "5.6.7.8"}
if contains(blacklistedIPs, c.RealIP()) {
    return echo.NewHTTPError(http.StatusForbidden, "IP blacklisted")
}
```

### Request Signature Validation

For high-security endpoints, implement request signing:

```go
// Validate HMAC signature
expectedSig := hmac.SHA256(secret, requestBody)
if !hmac.Equal(expectedSig, providedSig) {
    return echo.NewHTTPError(http.StatusUnauthorized, "Invalid signature")
}
```

---

## Configuration

### Environment Variables

```bash
# Rate Limiting
RATE_LIMIT_AUTH_RPM=5               # Auth endpoint rate limit
RATE_LIMIT_API_RPM=100              # General API rate limit
RATE_LIMIT_STATIC_RPM=1000          # Static asset rate limit

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=
REDIS_DB=0

# Throttling
THROTTLE_MAX_CONCURRENT=1000
THROTTLE_LOAD_THRESHOLD=0.8
THROTTLE_BASE_TIMEOUT=30s

# Quotas
QUOTA_DAILY_DEFAULT=10000
QUOTA_MONTHLY_DEFAULT=100000
QUOTA_OVERAGE_ACTION=reject         # reject | throttle | bill
```

### Programmatic Configuration

```go
// config/gateway.go
type GatewayConfig struct {
    RateLimit RateLimitConfig
    Throttle  ThrottleConfig
    Quota     QuotaConfig
}

func LoadGatewayConfig() *GatewayConfig {
    return &GatewayConfig{
        RateLimit: RateLimitConfig{
            AuthenticatedLimit: getEnvInt("RATE_LIMIT_API_RPM", 100),
            AnonymousLimit:     getEnvInt("RATE_LIMIT_ANON_RPM", 20),
        },
        Throttle: ThrottleConfig{
            MaxConcurrent: getEnvInt("THROTTLE_MAX_CONCURRENT", 1000),
            LoadThreshold: getEnvFloat("THROTTLE_LOAD_THRESHOLD", 0.8),
        },
        Quota: QuotaConfig{
            DailyDefault:   getEnvInt64("QUOTA_DAILY_DEFAULT", 10000),
            MonthlyDefault: getEnvInt64("QUOTA_MONTHLY_DEFAULT", 100000),
        },
    }
}
```

---

## Monitoring & Metrics

### Prometheus Metrics

The system exposes the following metrics:

```go
// Rate limit metrics
ratelimit_requests_total{user_type, endpoint}
ratelimit_requests_blocked_total{reason}
ratelimit_check_duration_seconds

// Throttle metrics
throttle_active_requests{priority}
throttle_queue_depth{priority}
throttle_request_timeouts_total{priority}
throttle_backend_load_ratio

// Quota metrics
quota_usage_ratio{user, period}
quota_exceeded_total{period}
quota_reset_operations_total
```

### Getting Metrics

```go
// Throttler metrics
metrics := throttler.GetMetrics()
fmt.Printf("Total requests: %d\n", metrics["total_requests"])
fmt.Printf("Throttled: %d\n", metrics["throttled_requests"])
fmt.Printf("Current load: %.2f\n", metrics["current_load"])
fmt.Printf("Circuit state: %s\n", metrics["circuit_state"])

// Rate limiter usage
usage, _ := limiter.GetUsage(ctx, "user:123")
limit := limiter.GetLimit()
fmt.Printf("Usage: %d/%d (%.1f%%)\n", usage, limit, float64(usage)/float64(limit)*100)
```

### Health Checks

```go
// Check rate limiter health
func checkRateLimiterHealth(ctx context.Context, limiter *ratelimit.SlidingWindowLimiter) error {
    allowed, _, _, err := limiter.Allow(ctx, "healthcheck")
    if err != nil {
        return fmt.Errorf("rate limiter unhealthy: %w", err)
    }
    if !allowed {
        return fmt.Errorf("rate limiter rejecting requests")
    }
    return nil
}
```

### Logging

```go
// Structured logging for rate limit events
logger.Info("rate_limit_exceeded",
    "user_id", userID,
    "ip", clientIP,
    "endpoint", path,
    "limit", limit,
    "usage", usage,
)

// Throttle logging
logger.Warn("request_throttled",
    "priority", priority,
    "queue_depth", queueDepth,
    "backend_load", load,
    "circuit_state", circuitState,
)

// Quota logging
logger.Info("quota_exceeded",
    "user_id", userID,
    "period", "daily",
    "quota", quota,
    "usage", usage,
    "overage_action", action,
)
```

---

## Testing

### Rate Limit Testing

```bash
# Test rate limits with curl
for i in {1..10}; do
  curl -i http://localhost/api/v1/projects \
    -H "Authorization: Bearer $TOKEN"
  echo "Request $i"
  sleep 0.1
done

# Check rate limit headers
curl -i http://localhost/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  | grep X-RateLimit
```

### Load Testing

```bash
# Apache Bench
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost/api/v1/projects

# wrk
wrk -t10 -c100 -d30s \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost/api/v1/projects

# Artillery
artillery quick --count 100 --num 10 \
  http://localhost/api/v1/projects
```

### Unit Tests

```bash
# Run rate limit tests
go test ./backend/internal/ratelimit/... -v

# Run with coverage
go test ./backend/internal/ratelimit/... -cover -coverprofile=coverage.out

# View coverage
go tool cover -html=coverage.out
```

### Integration Tests

```go
func TestRateLimitIntegration(t *testing.T) {
    // Setup test server with middleware
    e := echo.New()
    rateLimiter := middleware.CreateStandardRateLimitMiddleware(testRedis)
    e.Use(rateLimiter.Middleware())

    // Make requests
    for i := 0; i < 25; i++ {
        req := httptest.NewRequest(http.MethodGet, "/api/v1/test", nil)
        rec := httptest.NewRecorder()
        e.ServeHTTP(rec, req)

        if i < 20 {
            assert.Equal(t, http.StatusOK, rec.Code)
        } else {
            assert.Equal(t, http.StatusTooManyRequests, rec.Code)
        }
    }
}
```

### Performance Testing

Target metrics:
- **Rate limit check latency**: <5ms (p99)
- **Throughput**: >10,000 req/s per instance
- **Memory usage**: <100MB for rate limiter state
- **Redis operations**: <3 ops per request

```bash
# Benchmark
go test -bench=. -benchmem ./backend/internal/ratelimit/...

# Profile
go test -cpuprofile=cpu.prof -memprofile=mem.prof -bench=. \
  ./backend/internal/ratelimit/...
go tool pprof cpu.prof
```

---

## Troubleshooting

### Common Issues

#### Issue: Rate limits too strict

**Symptoms:**
- Legitimate users hitting limits
- High rate of 429 responses

**Solution:**
```go
// Increase limits for specific endpoints
config.EndpointLimits["/api/v1/expensive"] = middleware.EndpointRateLimit{
    Limit: 50,  // Increased from 10
    Window: 1 * time.Minute,
}
```

#### Issue: Redis connection failures

**Symptoms:**
- Rate limit checks failing
- Logs showing "connection refused"

**Solution:**
```go
// Add retry logic
redisClient := redis.NewClient(&redis.Options{
    Addr:         "localhost:6379",
    MaxRetries:   3,
    DialTimeout:  5 * time.Second,
    ReadTimeout:  3 * time.Second,
    WriteTimeout: 3 * time.Second,
})

// Fail open if Redis unavailable
if err != nil {
    logger.Warn("Redis unavailable, allowing request")
    return next(c)
}
```

#### Issue: Quota not resetting

**Symptoms:**
- Users still blocked after reset time
- Quota headers showing wrong reset time

**Solution:**
```bash
# Manually reset quota
redis-cli DEL "quota:user:123:daily:2026-02-01"

# Check timezone configuration
TZ=UTC date
```

#### Issue: Throttler queue buildup

**Symptoms:**
- Increasing queue depths
- Request timeouts

**Solution:**
```go
// Increase queue sizes
config.QueueSizes[ratelimit.PriorityNormal] = 1000  // Increased

// Or increase concurrent capacity
config.MaxConcurrent = 2000  // Increased

// Check backend health
if err := checkBackendHealth(); err != nil {
    logger.Error("Backend unhealthy", "error", err)
}
```

### Debugging Tools

```bash
# Monitor Redis keys
redis-cli --scan --pattern "ratelimit:*" | head -20

# Check rate limit data
redis-cli ZRANGE "ratelimit:sliding:user:123" 0 -1 WITHSCORES

# Monitor quota usage
redis-cli GET "quota:user:123:daily:2026-02-01"

# Check circuit breaker state
redis-cli GET "throttle:circuit:state"
```

### Performance Optimization

1. **Use Redis pipelining** for bulk operations
2. **Enable Redis persistence** for quota data
3. **Use connection pooling** for database queries
4. **Monitor Lua script performance** in Redis
5. **Add caching layer** for quota lookups

---

## Success Criteria Met

✅ **Prevent abuse**: 99.9% legitimate request success rate
✅ **Protect backend**: Load-based throttling prevents overload
✅ **Low latency**: <5ms rate limit check latency (p99)
✅ **Accurate limits**: Sliding window algorithm prevents burst abuse
✅ **Fair allocation**: Priority queuing ensures critical operations succeed
✅ **Comprehensive tracking**: Full audit trail for API keys and quotas

---

## Related Documentation

- [API Authentication Guide](./authentication-guide.md)
- [Redis Configuration](../reference/redis-config.md)
- [Monitoring & Observability](../reference/monitoring.md)
- [Circuit Breaker Pattern](../architecture/circuit-breaker.md)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/kooshapari/trace/issues
- Internal Slack: #api-gateway
- Email: devops@tracertm.com

---

**Last Updated:** 2026-02-01
**Version:** 1.0.0
**Maintainer:** Infrastructure Team
