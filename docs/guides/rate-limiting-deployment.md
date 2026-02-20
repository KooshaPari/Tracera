# Rate Limiting Deployment Guide

Complete guide for deploying and configuring Redis-backed rate limiting in production.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Redis Setup](#redis-setup)
- [Configuration](#configuration)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

## Overview

TraceRTM implements a dual-strategy rate limiting system:

1. **Token Bucket Algorithm** - Primary rate limiter with burst support
2. **Sliding Window Algorithm** - Precise time-based rate limiting

Both algorithms support:
- **In-memory mode** - For development and single-instance deployments
- **Redis mode** - For production and distributed deployments

### Features

- ✅ Per-endpoint rate limits (auth, API, static assets)
- ✅ Per-user and per-IP rate limiting
- ✅ Custom key extraction for flexible identification
- ✅ Standard rate limit headers (X-RateLimit-*)
- ✅ Automatic cleanup of stale limiters
- ✅ Health check endpoint exemption
- ✅ Comprehensive test coverage

## Architecture

```
┌─────────────────┐
│   HTTP Request  │
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│ Rate Limit Middleware│
│  - Pattern matching  │
│  - Key extraction    │
│  - Header injection  │
└────────┬───────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌──────────┐
│In-Mem │ │  Redis   │
│Limiter│ │  Limiter │
│Token  │ │  Token   │
│Bucket │ │  Bucket  │
└───────┘ └──────────┘
                │
                ▼
         ┌──────────────┐
         │ Redis Server │
         │  - Key/Value  │
         │  - Lua Script │
         │  - TTL Mgmt   │
         └──────────────┘
```

### Rate Limiting Flow

1. **Request arrives** → Rate limit middleware intercepts
2. **Endpoint matching** → Determine applicable rate limit
3. **Key extraction** → Identify client (user ID or IP)
4. **Limit check** → Token bucket algorithm via Redis/in-memory
5. **Response** → Allow with headers OR 429 Too Many Requests

## Prerequisites

### Required Software

- **Redis 6.0+** (7.0+ recommended)
  - Required for Lua scripting support
  - Optional for development (falls back to in-memory)
- **Docker** (if using docker-compose)
- **process-compose** (if using native orchestration)

### Environment Variables

All rate limiting configuration is via environment variables:

```bash
# Redis Connection
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Rate Limit Configuration
RATE_LIMIT_AUTH_RPM=5          # Auth endpoints (strict)
RATE_LIMIT_API_RPM=100         # API endpoints (moderate)
RATE_LIMIT_STATIC_RPM=1000     # Static assets (loose)

# Rate Limiter Cleanup
RATE_LIMITER_TTL_SECONDS=300           # 5 minutes
RATE_LIMITER_CLEANUP_INTERVAL_SECONDS=60  # 1 minute
```

## Redis Setup

### Option 1: Docker Compose (Recommended for Production)

The `docker-compose.yml` already includes Redis configuration:

```yaml
redis:
  image: redis:7-alpine
  container_name: tracertm-redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
    - ./config/redis.conf:/usr/local/etc/redis/redis.conf:ro  # Mount config
  command: redis-server /usr/local/etc/redis/redis.conf
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
  restart: unless-stopped
```

**Start Redis:**

```bash
docker-compose up -d redis
```

**Verify Redis is running:**

```bash
docker-compose ps redis
docker-compose logs redis
redis-cli ping  # Should return PONG
```

### Option 2: Process Compose (Native Orchestration)

The `process-compose.yaml` includes Redis:

```yaml
redis:
  command: "bash scripts/shell/redis-if-not-running.sh"
  readiness_probe:
    exec:
      command: "redis-cli -h localhost -p 6379 ping"
    initial_delay_seconds: 1
    period_seconds: 3
```

**Start Redis:**

```bash
make dev  # or make dev-tui
```

**Verify Redis is running:**

```bash
redis-cli ping  # Should return PONG
```

### Option 3: Local Redis Installation

**macOS (Homebrew):**

```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Verify installation:**

```bash
redis-cli ping  # Should return PONG
redis-cli info server | grep version  # Check version
```

## Configuration

### 1. Redis Production Configuration

The project includes a production-ready Redis configuration at `config/redis.conf`:

**Key settings for rate limiting:**

```conf
# Memory limit (adjust based on scale)
maxmemory 512mb

# Eviction policy (remove oldest rate limit data first)
maxmemory-policy volatile-lru

# Persistence (RDB snapshots)
save 900 1      # 15 min if 1 key changed
save 300 10     # 5 min if 10 keys changed
save 60 10000   # 1 min if 10k keys changed

# Performance
lazyfree-lazy-expire yes  # Async expiration (important for TTLs)
hz 10                     # Background task frequency
```

**Apply configuration:**

```bash
# Docker
docker-compose down redis
# Edit docker-compose.yml to mount redis.conf (see above)
docker-compose up -d redis

# Native
redis-server /path/to/redis.conf

# Or use existing Redis with config
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy volatile-lru
redis-cli CONFIG REWRITE  # Persist changes
```

### 2. Backend Configuration

The Go backend automatically detects Redis and uses it for rate limiting.

**Configuration file:** `backend/.env`

```bash
# Copy from example
cp backend/.env.example backend/.env

# Edit backend/.env
REDIS_URL=redis://localhost:6379

# Rate limits (adjust per environment)
RATE_LIMIT_AUTH_RPM=5          # Login attempts
RATE_LIMIT_API_RPM=100         # API requests
RATE_LIMIT_STATIC_RPM=1000     # Static files
```

**Rate limit tiers:**

| Endpoint Pattern | Requests/Min | Burst | Use Case |
|------------------|--------------|-------|----------|
| `/api/v1/auth/*` | 5 | 2 | Authentication endpoints |
| `/api/v1/*` | 100 | 10 | General API endpoints |
| `/static/*`, `/assets/*` | 1000 | 50 | Static assets |
| `*` (default) | 100 | 10 | Catch-all |

**Custom endpoint limits:**

Edit `backend/internal/middleware/rate_limiter.go`:

```go
EndpointLimits: []EndpointLimit{
    {
        Pattern:           "/api/v1/admin/*",
        RequestsPerMinute: 1000,  // Higher limit for admins
        BurstSize:         50,
        KeyExtractor: func(c *echo.Context) string {
            // Admin endpoints use user ID only
            if userID := (*c).Get("user_id"); userID != nil {
                return fmt.Sprintf("user:%v:admin", userID)
            }
            return fmt.Sprintf("ip:%s:admin", (*c).RealIP())
        },
    },
}
```

### 3. Environment-Specific Configuration

**Development:**

```bash
# backend/.env.development
REDIS_URL=redis://localhost:6379
RATE_LIMIT_AUTH_RPM=100    # Relaxed for testing
RATE_LIMIT_API_RPM=1000
```

**Staging:**

```bash
# backend/.env.staging
REDIS_URL=redis://redis-staging:6379
RATE_LIMIT_AUTH_RPM=10     # Moderate limits
RATE_LIMIT_API_RPM=200
```

**Production:**

```bash
# backend/.env.production
REDIS_URL=redis://redis-prod:6379
RATE_LIMIT_AUTH_RPM=5      # Strict limits
RATE_LIMIT_API_RPM=100
RATE_LIMIT_STATIC_RPM=1000
```

## Testing

### 1. Unit Tests

**Run rate limiter tests:**

```bash
cd backend
go test -v ./internal/middleware -run TestEnhancedRateLimiter
go test -v ./internal/ratelimit -run TestSlidingWindow
```

**Expected output:**

```
✓ TestEnhancedRateLimiter_InMemory
✓ TestEnhancedRateLimiter_Redis
✓ TestEnhancedRateLimiter_EndpointSpecific
✓ TestSlidingWindowLimiter_BasicLimit
✓ TestSlidingWindowLimiter_ConcurrentRequests
PASS
```

### 2. Integration Tests

**Test with Redis backend:**

```bash
# Start Redis
docker-compose up -d redis

# Run tests
cd backend
REDIS_URL=redis://localhost:6379 go test -v ./tests/security -run TestRateLimit
```

### 3. Manual Testing

**Test rate limiting with curl:**

```bash
# Test auth endpoint (5 requests/min, burst 2)
for i in {1..10}; do
  echo "Request $i:"
  curl -i http://localhost:8080/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test"}' 2>&1 | grep -E "HTTP|X-RateLimit|Retry-After"
  echo ""
done
```

**Expected output:**

```
Request 1:
HTTP/1.1 200 OK
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4

Request 2:
HTTP/1.1 200 OK
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3

Request 3:
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
Retry-After: 58
```

**Test rate limit headers:**

```bash
curl -i http://localhost:8080/api/v1/items | grep X-RateLimit
```

**Monitor Redis keys:**

```bash
# Watch rate limit keys
redis-cli --scan --pattern "ratelimit:*" | head -10

# Monitor key expiration
redis-cli MONITOR | grep ratelimit
```

### 4. Load Testing

**Test rate limiting under load:**

```bash
# Install Apache Bench
brew install httpd  # macOS
sudo apt install apache2-utils  # Linux

# Test with 100 concurrent requests
ab -n 1000 -c 100 http://localhost:8080/api/v1/items

# Analyze results
# - Should see 429 responses when limit exceeded
# - Should see X-RateLimit headers in responses
```

**Load test script:**

```bash
#!/bin/bash
# test-rate-limits.sh

API_URL="http://localhost:8080"
TOTAL_REQUESTS=1000
CONCURRENCY=50

echo "Testing rate limiting..."
ab -n $TOTAL_REQUESTS -c $CONCURRENCY \
   -H "Authorization: Bearer test-token" \
   "$API_URL/api/v1/items" \
   > ab-results.txt

# Count 429 responses
RATE_LIMITED=$(grep "429" ab-results.txt | wc -l)
echo "Rate limited requests: $RATE_LIMITED"

# Check Redis memory
redis-cli INFO memory | grep used_memory_human
redis-cli DBSIZE
```

## Monitoring

### 1. Prometheus Metrics

Redis metrics are automatically exported via `redis-exporter` (port 9113).

**Key metrics to monitor:**

```yaml
# Rate limiting metrics
- redis_commands_processed_total{cmd="eval"}  # Lua script executions
- redis_keyspace_hits_total                   # Cache hit rate
- redis_keyspace_misses_total                 # Cache miss rate
- redis_memory_used_bytes                     # Memory usage
- redis_evicted_keys_total                    # Evicted rate limit data

# Performance metrics
- redis_connected_clients                     # Active connections
- redis_commands_duration_seconds{cmd="eval"} # Lua script latency
```

**Prometheus queries:**

```promql
# Rate limit checks per second
rate(redis_commands_processed_total{cmd="eval"}[1m])

# Memory usage percentage
(redis_memory_used_bytes / redis_memory_max_bytes) * 100

# Eviction rate (should be low)
rate(redis_evicted_keys_total[5m])
```

### 2. Grafana Dashboards

**Create rate limiting dashboard:**

```bash
# Access Grafana
open http://localhost:3000  # Default credentials: admin/admin

# Import Redis dashboard
# Dashboard ID: 11835 (Redis Overview)
```

**Custom panels:**

1. **Rate Limit Operations** - `redis_commands_processed_total{cmd="eval"}`
2. **Memory Usage** - `redis_memory_used_bytes`
3. **Connection Pool** - `redis_connected_clients`
4. **Key Expiration Rate** - `rate(redis_expired_keys_total[5m])`

### 3. Application Logging

**Enable rate limit logging:**

```go
// backend/internal/middleware/rate_limiter.go
if !allowed {
    c.Logger().Warnf("Rate limit exceeded for %s on %s", clientKey, c.Request().URL.Path)
    // ... return 429
}
```

**Log analysis:**

```bash
# Count rate limited requests
grep "Rate limit exceeded" backend/logs/*.log | wc -l

# Top rate limited IPs
grep "Rate limit exceeded" backend/logs/*.log | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -10

# Rate limit patterns by endpoint
grep "Rate limit exceeded" backend/logs/*.log | \
  awk '{print $(NF-1)}' | sort | uniq -c
```

### 4. Redis Monitoring Commands

**Check rate limiting status:**

```bash
# Key count by pattern
redis-cli --scan --pattern "ratelimit:*" | wc -l

# Memory usage
redis-cli INFO memory | grep used_memory_human

# Eviction statistics
redis-cli INFO stats | grep evicted

# Slow log (should be empty)
redis-cli SLOWLOG GET 10

# Latency monitoring
redis-cli --latency

# Client connections
redis-cli CLIENT LIST | wc -l
```

## Troubleshooting

### Issue: Rate limits not working

**Symptoms:**
- All requests allowed regardless of limit
- No 429 responses

**Diagnosis:**

```bash
# Check if Redis is connected
redis-cli ping

# Check backend logs
tail -f backend/logs/app.log | grep -i redis

# Verify environment variables
cd backend && grep REDIS .env
```

**Solutions:**

1. **Redis not running:**
   ```bash
   docker-compose up -d redis
   # or
   redis-server
   ```

2. **Wrong REDIS_URL:**
   ```bash
   # Test connection
   redis-cli -u redis://localhost:6379 ping

   # Update backend/.env
   REDIS_URL=redis://localhost:6379
   ```

3. **Redis connection refused:**
   ```bash
   # Check Redis is listening
   netstat -an | grep 6379

   # Check firewall
   telnet localhost 6379
   ```

### Issue: High memory usage

**Symptoms:**
- Redis memory growing unbounded
- Evictions occurring frequently

**Diagnosis:**

```bash
# Check memory stats
redis-cli INFO memory

# Key count and size
redis-cli --bigkeys

# Eviction statistics
redis-cli INFO stats | grep evicted
```

**Solutions:**

1. **Set memory limit:**
   ```bash
   redis-cli CONFIG SET maxmemory 512mb
   redis-cli CONFIG SET maxmemory-policy volatile-lru
   redis-cli CONFIG REWRITE
   ```

2. **Reduce TTL:**
   ```bash
   # Edit backend/.env
   RATE_LIMITER_TTL_SECONDS=300  # 5 minutes (down from 1 hour)
   ```

3. **Monitor key expiration:**
   ```bash
   redis-cli INFO stats | grep expired_keys
   ```

### Issue: Slow response times

**Symptoms:**
- High latency on rate-limited endpoints
- Slow Redis queries

**Diagnosis:**

```bash
# Check Redis latency
redis-cli --latency

# Slow log
redis-cli SLOWLOG GET 10

# Monitor commands
redis-cli MONITOR | grep EVAL
```

**Solutions:**

1. **Optimize Lua scripts:**
   - Scripts are already optimized with atomic operations
   - Check `backend/internal/middleware/rate_limiter.go`

2. **Increase Redis performance:**
   ```bash
   redis-cli CONFIG SET hz 10  # Increase background task frequency
   redis-cli CONFIG SET lazyfree-lazy-expire yes
   ```

3. **Connection pooling:**
   - Go Redis client uses connection pooling by default
   - Verify with: `redis-cli CLIENT LIST | wc -l`

### Issue: Inconsistent rate limits

**Symptoms:**
- Rate limits differ between requests
- Distributed deployment inconsistencies

**Diagnosis:**

```bash
# Check if multiple Redis instances
ps aux | grep redis-server

# Verify Redis URL consistency
grep REDIS_URL backend/.env
```

**Solutions:**

1. **Single Redis instance:**
   - Ensure all backends use same `REDIS_URL`
   - Set up Redis replication for HA

2. **Clock synchronization:**
   ```bash
   # Ensure NTP is running
   sudo systemctl status systemd-timesyncd  # Linux
   sudo systemctl status chronyd            # RHEL/CentOS
   ```

3. **Redis Cluster:**
   - For truly distributed deployments
   - See: https://redis.io/topics/cluster-tutorial

## Production Checklist

### Pre-Deployment

- [ ] **Redis Configuration**
  - [ ] Production config reviewed (`config/redis.conf`)
  - [ ] Memory limit set appropriately
  - [ ] Persistence configured (RDB/AOF)
  - [ ] Password authentication enabled (`requirepass`)
  - [ ] Dangerous commands disabled/renamed

- [ ] **Network Security**
  - [ ] Redis bound to private network only
  - [ ] Firewall rules configured
  - [ ] TLS/SSL enabled (if needed)
  - [ ] No public Redis exposure

- [ ] **Rate Limit Configuration**
  - [ ] Environment variables set (`backend/.env.production`)
  - [ ] Endpoint limits reviewed and adjusted
  - [ ] TTL and cleanup intervals configured
  - [ ] Load tested with expected traffic

- [ ] **Monitoring**
  - [ ] Prometheus scraping Redis exporter
  - [ ] Grafana dashboards created
  - [ ] Alerts configured (memory, evictions, latency)
  - [ ] Log aggregation set up

- [ ] **Testing**
  - [ ] Unit tests passing
  - [ ] Integration tests with Redis backend
  - [ ] Load testing completed
  - [ ] Failure scenarios tested (Redis down, high load)

### Post-Deployment

- [ ] **Verify Operation**
  - [ ] Rate limiting working (test with curl)
  - [ ] Headers present in responses
  - [ ] 429 responses for exceeded limits
  - [ ] Metrics visible in Prometheus/Grafana

- [ ] **Monitor for Issues**
  - [ ] Redis memory stable
  - [ ] No excessive evictions
  - [ ] Latency acceptable (<10ms for EVAL)
  - [ ] No errors in application logs

- [ ] **Documentation**
  - [ ] Runbook updated with Redis endpoints
  - [ ] On-call procedures documented
  - [ ] Rate limit policies communicated to users

### High Availability Setup

For production HA, consider:

1. **Redis Replication:**
   ```yaml
   # docker-compose.yml
   redis-master:
     image: redis:7-alpine
     command: redis-server /etc/redis/redis.conf

   redis-replica:
     image: redis:7-alpine
     command: redis-server /etc/redis/redis.conf --replicaof redis-master 6379
   ```

2. **Redis Sentinel:**
   - Automatic failover
   - Configuration in `redis-sentinel.conf`

3. **Redis Cluster:**
   - Distributed deployment
   - Sharding across multiple nodes

## Rate Limit Configuration Reference

### Default Limits

| Endpoint | RPM | Burst | Key Type | Use Case |
|----------|-----|-------|----------|----------|
| `/api/v1/auth/*` | 5 | 2 | IP only | Login, logout, password reset |
| `/api/v1/*` | 100 | 10 | User/IP | General API operations |
| `/static/*` | 1000 | 50 | IP | CSS, JS, images |
| `/assets/*` | 1000 | 50 | IP | Uploaded files |
| Default | 100 | 10 | User/IP | Catch-all |

### Scaling Guidelines

**Low traffic (<100 req/s):**
- Single Redis instance sufficient
- 256MB memory
- RDB persistence only

**Medium traffic (100-1000 req/s):**
- Redis with replication
- 512MB-1GB memory
- RDB + AOF persistence

**High traffic (>1000 req/s):**
- Redis Cluster
- 2GB+ memory per node
- Monitor eviction rate closely

**Enterprise scale (>10k req/s):**
- Redis Cluster with multiple shards
- Dedicated Redis instances
- Consider KeyDB (Redis alternative)

## Additional Resources

- **Redis Documentation:** https://redis.io/documentation
- **Rate Limiting Patterns:** https://redis.io/docs/reference/patterns/rate-limiting/
- **Token Bucket Algorithm:** https://en.wikipedia.org/wiki/Token_bucket
- **Sliding Window Algorithm:** https://blog.cloudflare.com/counting-things-a-lot-of-different-things/

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review Redis and application logs
3. Consult team documentation
4. Contact DevOps team

---

**Document Version:** 1.0
**Last Updated:** 2026-02-01
**Maintained By:** TraceRTM Team
