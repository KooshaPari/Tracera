# Rate Limiting Quick Reference

Fast reference for TraceRTM rate limiting configuration and operations.

## Quick Start

```bash
# Start with Redis
make dev

# Verify Redis
redis-cli ping  # Should return PONG

# Test rate limiting
./scripts/shell/test-rate-limiting.sh

# Monitor keys
redis-cli --scan --pattern "ratelimit:*"
```

## Rate Limit Tiers

| Endpoint | Req/Min | Burst | Use Case |
|----------|---------|-------|----------|
| `/api/v1/auth/*` | 5 | 2 | Login, logout |
| `/api/v1/*` | 100 | 10 | API operations |
| `/static/*` | 1000 | 50 | Static files |
| `/assets/*` | 1000 | 50 | Uploads |

## Environment Variables

```bash
# Required
REDIS_URL=redis://localhost:6379

# Optional
RATE_LIMIT_AUTH_RPM=5          # Auth limit
RATE_LIMIT_API_RPM=100         # API limit
RATE_LIMIT_STATIC_RPM=1000     # Static limit
RATE_LIMITER_TTL_SECONDS=300   # TTL (5 min)
```

## Testing

### Manual Test

```bash
# Test rate limiting
for i in {1..10}; do
  curl -i http://localhost:8080/api/v1/items | grep X-RateLimit
done
```

### Automated Test

```bash
./scripts/shell/test-rate-limiting.sh
```

### Load Test

```bash
ab -n 1000 -c 100 http://localhost:8080/api/v1/items
```

## Monitoring

### Redis Commands

```bash
# Check keys
redis-cli DBSIZE
redis-cli --scan --pattern "ratelimit:*" | wc -l

# Memory usage
redis-cli INFO memory | grep used_memory_human

# Evictions
redis-cli INFO stats | grep evicted

# Slow queries
redis-cli SLOWLOG GET 10
```

### Metrics (Prometheus)

```promql
# Rate limit checks/sec
rate(redis_commands_processed_total{cmd="eval"}[1m])

# Memory usage
redis_memory_used_bytes

# Eviction rate
rate(redis_evicted_keys_total[5m])
```

### Grafana

- URL: http://localhost:3000
- Dashboard: Redis Overview (ID 11835)

## Configuration Files

| File | Purpose |
|------|---------|
| `redis.conf` | Redis production config |
| `backend/.env` | Rate limit settings |
| `docker-compose.yml` | Docker Redis setup |
| `process-compose.yaml` | Native Redis setup |

## Common Operations

### Start Redis

```bash
# Docker
docker-compose up -d redis

# Native
make dev
```

### Stop Redis

```bash
# Docker
docker-compose down redis

# Native
make stop
```

### Reset Rate Limits

```bash
# Delete all rate limit keys
redis-cli --scan --pattern "ratelimit:*" | xargs redis-cli DEL

# Or flush entire DB (CAUTION: deletes ALL Redis data)
redis-cli FLUSHDB
```

### Check Rate Limit for IP

```bash
# List keys for specific IP
redis-cli --scan --pattern "ratelimit:*:192.168.1.1:*"

# Get current token count
redis-cli GET "ratelimit:ip:192.168.1.1:api:tokens"
```

## Troubleshooting

### Rate limits not working

```bash
# 1. Check Redis
redis-cli ping

# 2. Check backend logs
tail -f backend/logs/app.log | grep -i redis

# 3. Verify config
grep REDIS backend/.env
```

### High memory usage

```bash
# 1. Check memory
redis-cli INFO memory | grep used_memory

# 2. Set limit
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy volatile-lru

# 3. Reduce TTL
# Edit backend/.env:
RATE_LIMITER_TTL_SECONDS=300
```

### Slow performance

```bash
# 1. Check latency
redis-cli --latency

# 2. Check slow log
redis-cli SLOWLOG GET 10

# 3. Optimize
redis-cli CONFIG SET hz 10
redis-cli CONFIG SET lazyfree-lazy-expire yes
```

## Headers Reference

**Request:**
- `X-Forwarded-For: <ip>` - Override client IP (for testing)
- `Authorization: Bearer <token>` - User authentication

**Response (Success):**
- `X-RateLimit-Limit: <number>` - Total requests allowed
- `X-RateLimit-Remaining: <number>` - Remaining requests
- `X-RateLimit-Reset: <timestamp>` - Reset time (Unix epoch)

**Response (Rate Limited):**
- `HTTP/1.1 429 Too Many Requests`
- `Retry-After: <seconds>` - Seconds until retry

## Security

### Production Checklist

```bash
# Set password
redis-cli CONFIG SET requirepass "YOUR_STRONG_PASSWORD"

# Bind to private network
# Edit redis.conf:
bind 127.0.0.1

# Disable dangerous commands
# Edit redis.conf:
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

## Algorithms

### Token Bucket

- **Use case:** Primary rate limiting
- **Pros:** Burst support, simple
- **Cons:** Less precise over time

### Sliding Window

- **Use case:** Precise time-based limiting
- **Pros:** Accurate, fair
- **Cons:** More memory, complex

## Performance

| Mode | Throughput | Latency (P95) |
|------|------------|---------------|
| In-memory | 50k ops/s | <2ms |
| Redis (local) | 10k ops/s | <10ms |
| Redis (network) | 5k ops/s | <20ms |

## Memory Usage

| Active Users | Memory |
|--------------|--------|
| 1,000 | ~1MB |
| 10,000 | ~10MB |
| 100,000 | ~100MB |
| 1,000,000 | ~1GB |

## Resources

- **Full Guide:** [docs/guides/rate-limiting-deployment.md](../guides/rate-limiting-deployment.md)
- **Completion Report:** [docs/reports/rate-limiting-redis-deployment-complete.md](../reports/rate-limiting-redis-deployment-complete.md)
- **Test Script:** [scripts/shell/test-rate-limiting.sh](../../scripts/shell/test-rate-limiting.sh)
- **Redis Config:** [redis.conf](../../config/redis.conf)

## Support

For detailed information, see the [full deployment guide](../guides/rate-limiting-deployment.md).

---

**Version:** 1.0
**Last Updated:** 2026-02-01
