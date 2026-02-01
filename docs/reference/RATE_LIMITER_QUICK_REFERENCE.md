# Rate Limiter - Quick Reference

## TL;DR

The rate limiter now has automatic cleanup to prevent memory leaks. No action required unless you want to customize settings.

## Basic Usage

```go
import "github.com/kooshapari/tracertm-backend/internal/middleware"

// In your Echo setup
e.Use(middleware.RateLimitMiddleware(middleware.RateLimitConfig{
    RequestsPerSecond: 100,
    BurstSize:        50,
}))

// Optional: Graceful shutdown
defer middleware.StopRateLimitCleanup(&config)
```

## Environment Variables

```bash
# Cleanup configuration (all optional)
RATE_LIMITER_TTL_SECONDS=300              # How long to keep unused limiters (default: 5 min)
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=60  # How often to cleanup (default: 1 min)
```

## Expected Logs

```
Rate limiter cleanup: removed 15 stale limiters, 42 active limiters remaining
```

This is normal. It shows:
- **removed**: Stale limiters cleaned up
- **active**: Current limit entries in use

## Verify It's Working

```bash
# Check logs for cleanup messages
tail -f /var/log/app.log | grep "Rate limiter cleanup"

# Monitor memory (should be stable)
watch -n 5 'ps aux | grep api-server | grep -v grep'
```

## Configuration Examples

### Development (Conservative)
```bash
RATE_LIMITER_TTL_SECONDS=1800              # 30 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=600  # 10 minutes
```

### Production (Balanced)
```bash
RATE_LIMITER_TTL_SECONDS=300               # 5 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=60   # 1 minute
```

### High Traffic (Aggressive)
```bash
RATE_LIMITER_TTL_SECONDS=120               # 2 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=30   # 30 seconds
```

## Troubleshooting

### Problem: High Memory Usage
**Solution**: Reduce TTL
```bash
RATE_LIMITER_TTL_SECONDS=120
```

### Problem: Legitimate Users Getting Rate Limited
**Solution**: Increase limit in config
```go
RequestsPerSecond: 200,  // Was 100
BurstSize:        100,   // Was 50
```

### Problem: Too Many Cleanup Logs
**Solution**: Increase cleanup interval
```bash
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=300
```

## Files Changed

- ✓ `backend/internal/middleware/middleware.go` - Core fix
- ✓ `backend/internal/middleware/middleware_test.go` - Tests added
- ✓ Documentation files created

## Success Indicators

- [ ] Application runs without increasing memory
- [ ] Cleanup log messages appear every 1 minute (or as configured)
- [ ] No rate limit false positives
- [ ] Clean shutdown without goroutine warnings

## Further Reading

- Full documentation: `docs/RATE_LIMITER_FIX.md`
- Integration guide: `docs/RATE_LIMITER_INTEGRATION.md`
- Before/After analysis: `docs/RATE_LIMITER_BEFORE_AFTER.md`
- Implementation details: `.trace/RATE_LIMITER_IMPLEMENTATION.md`
