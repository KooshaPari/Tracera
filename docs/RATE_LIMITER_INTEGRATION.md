# Rate Limiter Integration Guide

## Quick Start

The rate limiter cleanup is automatically enabled when using `RateLimitMiddleware`. No additional setup is required.

```go
import "github.com/kooshapari/tracertm-backend/internal/middleware"

// In your Echo application setup
e.Use(middleware.RateLimitMiddleware(middleware.RateLimitConfig{
    RequestsPerSecond: 100,
    BurstSize:        50,
}))
```

## Full Integration Example

### Application Startup

```go
package main

import (
    "github.com/labstack/echo/v4"
    "github.com/kooshapari/tracertm-backend/internal/middleware"
)

func main() {
    e := echo.New()

    // Initialize rate limit config
    rateLimitConfig := middleware.RateLimitConfig{
        RequestsPerSecond: 100,
        BurstSize:        50,
        // TTL and CleanupInterval will use environment variables or defaults
    }

    // Apply middleware
    e.Use(middleware.RateLimitMiddleware(rateLimitConfig))

    // ... register routes ...

    // Start server with graceful shutdown
    if err := startServerWithGracefulShutdown(e, &rateLimitConfig); err != nil {
        e.Logger.Fatal(err)
    }
}

func startServerWithGracefulShutdown(e *echo.Echo, config *middleware.RateLimitConfig) error {
    // Setup graceful shutdown
    go func() {
        if err := e.Start(":8080"); err != nil {
            e.Logger.Error(err)
        }
    }()

    // Wait for interrupt signal
    sigint := make(chan os.Signal, 1)
    signal.Notify(sigint, os.Interrupt, syscall.SIGTERM)
    <-sigint

    // Gracefully shutdown rate limiter
    middleware.StopRateLimitCleanup(config)

    // Shutdown server
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    return e.Shutdown(ctx)
}
```

### Environment Configuration

Create a `.env` file or set environment variables:

```bash
# Rate limiting configuration
RATE_LIMITER_TTL_SECONDS=300                        # 5 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=60            # 1 minute
```

### Docker Integration

Update your Dockerfile:

```dockerfile
FROM golang:1.21-alpine

WORKDIR /app
COPY . .

# Build application
RUN go build -o app ./cmd/main.go

# Set rate limiter environment variables
ENV RATE_LIMITER_TTL_SECONDS=300
ENV RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=60

EXPOSE 8080
CMD ["./app"]
```

### Kubernetes Deployment

Add to your Kubernetes manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api-server
        image: your-registry/api-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: RATE_LIMITER_TTL_SECONDS
          value: "300"
        - name: RATE_LIMITER_CLEANUP_INTERVAL_SECONDS
          value: "60"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
```

## Configuration Strategies

### Development Environment

For development, use lenient settings:

```bash
# Long TTL, infrequent cleanup
RATE_LIMITER_TTL_SECONDS=1800              # 30 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=600  # 10 minutes
```

### Production Environment

For production with medium traffic:

```bash
# Balanced settings
RATE_LIMITER_TTL_SECONDS=300               # 5 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=60   # 1 minute
```

### High-Traffic Environment

For high-traffic production:

```bash
# Aggressive cleanup
RATE_LIMITER_TTL_SECONDS=120               # 2 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=30   # 30 seconds
```

## Monitoring Setup

### Metrics Collection

The cleanup goroutine logs its activities. Set up log aggregation:

```go
import (
    "log/slog"
    "os"
)

func init() {
    // Use structured logging for better monitoring
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
    slog.SetDefault(logger)
}
```

Expected log output:
```json
{
  "level": "INFO",
  "msg": "Rate limiter cleanup: removed 15 stale limiters, 42 active limiters remaining",
  "time": "2024-01-15T10:30:45Z"
}
```

### Prometheus Metrics (Optional)

For production monitoring, consider exporting metrics:

```go
package main

import (
    "github.com/prometheus/client_golang/prometheus"
)

var (
    staleLimitersRemoved = prometheus.NewCounter(prometheus.CounterOpts{
        Name: "rate_limiter_stale_removed_total",
        Help: "Total number of stale limiters removed",
    })
    activeLimiters = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "rate_limiter_active_count",
        Help: "Current count of active rate limiters",
    })
    cleanupDuration = prometheus.NewHistogram(prometheus.HistogramOpts{
        Name: "rate_limiter_cleanup_duration_seconds",
        Help: "Duration of rate limiter cleanup operations",
    })
)

func init() {
    prometheus.MustRegister(staleLimitersRemoved, activeLimiters, cleanupDuration)
}
```

### Health Check Endpoint

Add health check that includes rate limiter status:

```go
func healthCheck(c echo.Context) error {
    return c.JSON(http.StatusOK, map[string]interface{}{
        "status": "ok",
        "rate_limiter": map[string]interface{}{
            "enabled": true,
            "requests_per_second": 100,
            "burst_size": 50,
        },
    })
}

e.GET("/health", healthCheck)
```

## Testing Integration

### Unit Tests

Run middleware tests:

```bash
cd backend
go test ./internal/middleware -v
```

### Integration Tests

Test with your actual handlers:

```go
func TestRateLimiterWithRealHandler(t *testing.T) {
    e := echo.New()
    config := middleware.RateLimitConfig{
        RequestsPerSecond: 10,
        BurstSize:        5,
    }
    defer middleware.StopRateLimitCleanup(&config)

    e.Use(middleware.RateLimitMiddleware(config))
    e.GET("/api/data", func(c echo.Context) error {
        return c.JSON(http.StatusOK, map[string]string{"data": "value"})
    })

    // Make test requests
    // Verify rate limiting behavior
}
```

### Load Testing

Use load testing tools to verify cleanup under stress:

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://localhost:8080/api/endpoint

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8080/api/endpoint
```

Monitor memory usage during load test:
```bash
watch -n 1 'ps aux | grep api-server | grep -v grep'
```

## Troubleshooting Guide

### Issue: Memory Still Growing

**Symptoms**: Memory usage increases over time despite cleanup

**Solutions**:
1. Check cleanup is running: Look for cleanup log messages
2. Reduce TTL: `RATE_LIMITER_TTL_SECONDS=120`
3. Increase cleanup frequency: `RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=30`

### Issue: Rate Limiting Too Aggressive

**Symptoms**: Legitimate users getting 429 errors

**Solutions**:
1. Increase requests per second: Adjust `RequestsPerSecond` in config
2. Increase burst size: Adjust `BurstSize` in config
3. Increase TTL: `RATE_LIMITER_TTL_SECONDS=600`

### Issue: Cleanup Logs Too Verbose

**Symptoms**: Too many cleanup messages in logs

**Solutions**:
1. Increase cleanup interval: `RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=300`
2. Filter logs at application level
3. Use log sampling for high-traffic scenarios

### Issue: Goroutine Leak on Shutdown

**Symptoms**: Goroutine count increases after shutdown

**Solutions**:
1. Ensure `StopRateLimitCleanup()` is called during graceful shutdown
2. Verify cleanup channel is properly closed
3. Add timeout for cleanup goroutine termination

## Performance Tuning

### Recommended Settings by Load

| Scenario | RPS | Burst | TTL | Cleanup Interval |
|---|---|---|---|---|
| Development | 100 | 50 | 1800s | 600s |
| Light API | 100 | 50 | 600s | 300s |
| Medium API | 1000 | 100 | 300s | 60s |
| Heavy API | 10000 | 500 | 120s | 30s |
| Cache Server | 50000 | 2000 | 60s | 15s |

### Memory Impact

Estimated memory usage per limiter entry:
- ~200 bytes per limiter
- With 1000 active limiters: ~200KB
- With 10000 active limiters: ~2MB
- With 100000 active limiters: ~20MB (rare in practice)

## Best Practices

1. **Always Shutdown Gracefully**
   ```go
   defer middleware.StopRateLimitCleanup(&config)
   ```

2. **Monitor Cleanup Logs**
   - Set up log aggregation
   - Alert on abnormal removal rates

3. **Test TTL Settings**
   - Run load tests with typical client patterns
   - Adjust TTL based on session duration

4. **Use Environment Variables**
   - Never hardcode rate limiter settings
   - Allow runtime configuration changes

5. **Log Cleanup Operations**
   - Review cleanup statistics regularly
   - Identify optimal settings for your workload

## Migration from Old Implementation

If upgrading from the previous version:

1. **No Breaking Changes**: Existing code continues to work
2. **Optional Enhancement**: Add graceful shutdown:
   ```go
   middleware.StopRateLimitCleanup(&config)
   ```
3. **Optional Configuration**: Set environment variables for tuning

## Support and Issues

For issues with the rate limiter:
1. Check cleanup logs: `Rate limiter cleanup: removed X stale limiters`
2. Verify environment variables are set correctly
3. Monitor memory usage during peak load
4. Review goroutine count for leaks

## References

- [Go time/rate package](https://pkg.go.dev/golang.org/x/time/rate)
- [Echo Framework](https://echo.labstack.com/)
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
