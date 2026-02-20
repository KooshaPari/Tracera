# Rate Limiting Implementation Guide

## Overview

TraceRTM implements a **multi-layer rate limiting strategy** to protect against abuse while maintaining excellent user experience:

1. **Gateway Layer (Caddy)**: Coarse-grained DDoS protection
2. **Application Layer (Go Backend)**: Fine-grained per-endpoint controls

## Architecture

### Gateway Layer (Caddy)

The Caddy gateway provides the first line of defense:

```caddyfile
# Gateway-wide rate limit: 100 requests per minute per IP
rate_limit {
    zone dynamic {
        key {remote_host}
        events 100
        window 1m
    }
}
```

**Purpose**: Block obvious volumetric attacks before they reach the backend.

### Application Layer (Go Backend)

The backend implements sophisticated token bucket rate limiting with:

- **Per-endpoint limits**: Different limits for different API routes
- **Flexible key extraction**: Rate limit by IP, user ID, or custom logic
- **Redis support**: Distributed rate limiting across multiple instances
- **In-memory fallback**: Works without Redis for single-instance deployments
- **Rate limit headers**: Standard `X-RateLimit-*` headers for client guidance

## Configuration

### Default Endpoint Limits

The standard rate limiter (`CreateStandardRateLimiter`) configures:

| Endpoint Pattern | Requests/Min | Burst | Key | Purpose |
|-----------------|--------------|-------|-----|---------|
| `/api/v1/auth/*` | 5 | 2 | IP only | Prevent brute force attacks |
| `/api/v1/*` | 100 | 10 | User/IP | General API protection |
| `/static/*` | 1000 | 50 | User/IP | Allow fast asset loading |
| `/assets/*` | 1000 | 50 | User/IP | Allow fast asset loading |
| Health checks | Unlimited | N/A | N/A | Always available for monitoring |

### Environment Variables

Configure rate limits via environment variables:

```bash
# Auth endpoints (default: 5)
RATE_LIMIT_AUTH_RPM=5

# API endpoints (default: 100)
RATE_LIMIT_API_RPM=100

# Static assets (default: 1000)
RATE_LIMIT_STATIC_RPM=1000
```

### Custom Configuration

Create a custom rate limiter with specific rules:

```go
import "github.com/kooshapari/tracertm-backend/internal/middleware"

limiter := middleware.NewEnhancedRateLimiter(middleware.EnhancedRateLimitConfig{
    RedisClient:              redisClient, // Optional, uses in-memory if nil
    DefaultRequestsPerMinute: 100,
    DefaultBurstSize:         10,
    AddHeaders:               true,
    EndpointLimits: []middleware.EndpointLimit{
        {
            Pattern:           "/api/v1/sensitive/*",
            RequestsPerMinute: 10,
            BurstSize:         2,
            KeyExtractor: func(c *echo.Context) string {
                // Always use IP for sensitive endpoints
                return fmt.Sprintf("ip:%s:sensitive", (*c).RealIP())
            },
        },
    },
})

// Use in Echo middleware chain
e.Use(limiter.Middleware())
```

## Integration

The rate limiter is automatically integrated in `server.go`:

```go
// Enhanced rate limiting with per-endpoint controls
rateLimiter := custommw.CreateStandardRateLimiter(s.redisClient)
s.echo.Use(rateLimiter.Middleware())
```

## Response Headers

When rate limiting is active, the following headers are added:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

When rate limited, clients receive:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45
Content-Type: application/json

{
  "message": "Rate limit exceeded. Please try again later."
}
```

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
cd backend
go test -v ./internal/middleware -run TestEnhancedRateLimiter
```

Tests cover:
- ✓ In-memory rate limiting
- ✓ Redis-based rate limiting
- ✓ Per-endpoint limits
- ✓ Custom key extraction
- ✓ Rate limit headers
- ✓ Skipper function
- ✓ Cleanup routine

### Integration Tests

Use the provided script to test against a running server:

```bash
cd backend
./scripts/test-rate-limit.sh
```

This script:
1. Verifies health checks are never rate limited
2. Confirms API endpoints enforce limits
3. Checks rate limit headers are present

### Manual Testing with curl

Test rate limiting manually:

```bash
# Health endpoint - should never be rate limited
for i in {1..20}; do curl http://localhost:8080/health; done

# API endpoint - should be rate limited after ~10 requests
for i in {1..15}; do
    curl -i http://localhost:8080/api/v1/projects 2>&1 | grep -E "HTTP|X-RateLimit"
done

# Auth endpoint - should be rate limited after 2 requests
for i in {1..5}; do
    curl -i http://localhost:8080/api/v1/auth/login 2>&1 | grep -E "HTTP|X-RateLimit"
done
```

## Performance

The rate limiter is highly optimized:

### In-Memory Mode
- **Throughput**: >100K requests/second (see benchmarks)
- **Memory**: ~1KB per unique client (cleaned up after 10 minutes)
- **Latency**: <100μs overhead per request

### Redis Mode
- **Throughput**: ~10K requests/second (network bound)
- **Memory**: Minimal (state in Redis)
- **Latency**: ~1ms overhead per request
- **Scalability**: Shared state across multiple backend instances

### Benchmarks

Run performance benchmarks:

```bash
cd backend
go test -bench=BenchmarkRateLimiter ./internal/middleware
```

## Best Practices

### 1. Choose the Right Key

- **Auth endpoints**: Always use IP address to prevent credential stuffing
- **API endpoints**: Use user ID when authenticated, IP otherwise
- **Public endpoints**: Use IP address

### 2. Set Appropriate Limits

- **Write operations**: Lower limits (10-50 req/min)
- **Read operations**: Higher limits (100-500 req/min)
- **List/search**: Moderate limits (50-100 req/min)

### 3. Use Redis in Production

For multi-instance deployments:

```go
rateLimiter := middleware.CreateStandardRateLimiter(redisClient)
```

This ensures consistent rate limiting across all backend instances.

### 4. Monitor Rate Limit Events

Log rate limit events for analysis:

```go
// In middleware, after rate limit check
if !allowed {
    log.Printf("Rate limit exceeded: client=%s endpoint=%s", clientKey, c.Path())
}
```

### 5. Provide Clear Error Messages

Customize error messages per endpoint:

```go
config := middleware.EnhancedRateLimitConfig{
    ErrorMessage: "Too many login attempts. Please try again in 1 minute.",
}
```

## Troubleshooting

### Rate Limiter Not Working

1. **Check if middleware is registered**:
   ```bash
   grep -r "rateLimiter.Middleware" backend/internal/server/
   ```

2. **Verify Redis connection** (if using Redis):
   ```bash
   redis-cli ping
   ```

3. **Check environment variables**:
   ```bash
   env | grep RATE_LIMIT
   ```

### Too Aggressive Limiting

1. **Increase limits** via environment variables
2. **Check if using correct key** (IP vs User ID)
3. **Verify burst size** is appropriate for use case

### Headers Not Appearing

Ensure `AddHeaders: true` in config:

```go
config := middleware.EnhancedRateLimitConfig{
    AddHeaders: true,
}
```

## Security Considerations

### DDoS Protection

The multi-layer approach provides defense in depth:

1. **Caddy** blocks simple volumetric attacks
2. **Go backend** enforces business logic limits
3. **Redis** (optional) enables distributed limiting

### Brute Force Prevention

Auth endpoints have strict limits:

```go
{
    Pattern:           "/api/v1/auth/*",
    RequestsPerMinute: 5,
    BurstSize:         2,
    KeyExtractor: func(c *echo.Context) string {
        // Always use IP, never user ID
        return fmt.Sprintf("ip:%s:auth", (*c).RealIP())
    },
}
```

### Bypass Protection

Health checks bypass rate limiting via skipper:

```go
Skipper: middleware.HealthCheckSkipper,
```

This ensures monitoring systems can always check service health.

## Advanced Features

### Custom Key Extraction

Implement custom logic for rate limit keys:

```go
KeyExtractor: func(c *echo.Context) string {
    // Rate limit by API key instead of IP
    apiKey := (*c).Request().Header.Get("X-API-Key")
    if apiKey != "" {
        return fmt.Sprintf("apikey:%s", apiKey)
    }
    // Fallback to IP
    return fmt.Sprintf("ip:%s", (*c).RealIP())
}
```

### Dynamic Limits

Adjust limits based on user tier:

```go
KeyExtractor: func(c *echo.Context) string {
    userID := (*c).Get("user_id")
    tier := getUserTier(userID) // premium, standard, free
    return fmt.Sprintf("user:%v:tier:%s", userID, tier)
}
```

Then create separate `EndpointLimit` entries for each tier.

### Cleanup Configuration

The cleanup routine runs every 5 minutes by default. Stale limiters (>10 minutes idle) are removed.

To stop the cleanup routine (e.g., during shutdown):

```go
limiter.Stop()
```

## References

- Implementation: `backend/internal/middleware/rate_limiter.go`
- Tests: `backend/internal/middleware/rate_limiter_test.go`
- Integration: `backend/internal/server/server.go`
- Caddy config: `Caddyfile`
- Test script: `backend/scripts/test-rate-limit.sh`

## Related Documentation

- [Security Overview](../security-overview.md)
- [API Documentation](../api-documentation.md)
- [Production Deployment Guide](./DEPLOYMENT_GUIDE.md)
