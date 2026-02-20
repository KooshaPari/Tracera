# Troubleshooting Guide

Comprehensive troubleshooting guide for common issues in TracerTM deployment and operations.

## Table of Contents

- [Service Won't Start](#service-wont-start)
- [Connection Issues](#connection-issues)
- [Performance Problems](#performance-problems)
- [Authentication Issues](#authentication-issues)
- [Database Issues](#database-issues)
- [Cache and Message Broker](#cache-and-message-broker)
- [API Errors](#api-errors)
- [Frontend Issues](#frontend-issues)
- [Log Analysis Techniques](#log-analysis-techniques)
- [Debug Mode Activation](#debug-mode-activation)
- [Network and Connectivity](#network-and-connectivity)
- [Docker and Container Issues](#docker-and-container-issues)

---

## Service Won't Start

### Symptom: Docker Compose Fails to Start

**Check Docker status:**
```bash
# Verify Docker is running
docker info

# Check Docker Compose version
docker compose version

# View service status
docker compose ps
```

**Common Causes:**

#### 1. Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8080: bind: address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml or .env
PORT=8081
```

#### 2. Missing Environment Variables

**Error:**
```
Error: environment variable DATABASE_URL is required
```

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Verify variable is set
grep DATABASE_URL .env

# Load environment
source .env

# Restart services
docker compose down
docker compose up -d
```

#### 3. Volume Permission Issues

**Error:**
```
Permission denied: '/var/lib/postgresql/data'
```

**Solution:**
```bash
# Check volume permissions
docker volume inspect tracertm_postgres_data

# Remove and recreate volume
docker compose down -v
docker compose up -d

# Or fix permissions
docker run --rm -v tracertm_postgres_data:/data alpine chown -R 999:999 /data
```

#### 4. Image Build Failures

**Error:**
```
failed to solve: failed to fetch anonymous: Get "https://registry...": dial tcp: lookup ...
```

**Solution:**
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker compose build --no-cache

# Check DNS resolution
docker run --rm alpine nslookup registry-1.docker.io

# Configure Docker DNS (if needed)
# Edit /etc/docker/daemon.json:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
# Restart Docker
sudo systemctl restart docker
```

### Symptom: Service Starts but Immediately Exits

**Check exit code:**
```bash
docker compose ps
# Look for "Exit 1", "Exit 137" (OOM), "Exit 139" (segfault)

# View last logs
docker compose logs --tail=100 go-backend
```

**Common Causes:**

#### 1. Configuration Error

**Solution:**
```bash
# Validate configuration
./scripts/validate-config.sh

# Check specific service logs
docker compose logs go-backend | grep -i error

# Test configuration in isolation
docker run --rm --env-file .env tracertm-go-backend /app/tracertm-backend --validate
```

#### 2. Dependency Not Ready

**Solution:**
```bash
# Check dependencies
docker compose exec postgres pg_isready -U tracertm
docker compose exec redis redis-cli ping

# Increase healthcheck intervals in docker-compose.yml
healthcheck:
  interval: 10s  # from 30s
  timeout: 5s
  retries: 5
  start_period: 60s  # from 40s
```

#### 3. Memory Limits

**Exit code 137 = OOM killed**

**Solution:**
```bash
# Check system memory
free -m

# Increase container memory limit
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G  # increase from 2G

# Check for memory leaks
docker stats --no-stream
```

---

## Connection Issues

### Cannot Connect to Database

**Symptoms:**
- `connection refused`
- `could not connect to server`
- `authentication failed`

**Diagnostic Steps:**

```bash
# 1. Check PostgreSQL is running
docker compose ps postgres

# 2. Check PostgreSQL logs
docker compose logs postgres

# 3. Test connection from host
psql -h localhost -U tracertm -d tracertm

# 4. Test from container
docker compose exec go-backend psql -h postgres -U tracertm -d tracertm

# 5. Check network
docker compose exec go-backend ping postgres
```

**Solutions:**

#### Invalid Credentials
```bash
# Reset database password
docker compose exec postgres psql -U tracertm -c \
  "ALTER USER tracertm WITH PASSWORD 'new_password';"

# Update .env
DATABASE_URL=postgresql+asyncpg://tracertm:new_password@postgres:5432/tracertm

# Restart services
docker compose restart go-backend python-backend
```

#### Network Issues
```bash
# Check Docker network
docker network inspect tracertm_tracertm

# Recreate network
docker compose down
docker network prune
docker compose up -d
```

#### Max Connections Reached
```bash
# Check connection count
docker compose exec postgres psql -U tracertm -c \
  "SELECT COUNT(*) FROM pg_stat_activity;"

# Kill idle connections
docker compose exec postgres psql -U tracertm -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity
   WHERE state = 'idle' AND state_change < NOW() - INTERVAL '10 minutes';"

# Increase max_connections
docker compose exec postgres psql -U tracertm -c \
  "ALTER SYSTEM SET max_connections = 200;"

# Restart PostgreSQL
docker compose restart postgres
```

### Cannot Connect to Redis

**Symptoms:**
- `connection timeout`
- `NOAUTH Authentication required`

**Solutions:**

```bash
# 1. Check Redis is running
docker compose ps redis

# 2. Test connection
docker compose exec redis redis-cli ping

# 3. Test with password
docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" ping

# 4. Check Redis config
docker compose exec redis redis-cli CONFIG GET requirepass

# 5. Update .env with correct password
REDIS_URL=redis://:correct_password@redis:6379

# 6. Restart services
docker compose restart go-backend python-backend
```

### Cannot Connect to NATS

**Symptoms:**
- `nats: no servers available for connection`
- `nats: timeout`

**Solutions:**

```bash
# 1. Check NATS is running
docker compose ps nats

# 2. Check NATS health
curl http://localhost:8222/healthz

# 3. Check NATS varz (monitoring endpoint)
curl http://localhost:8222/varz | jq

# 4. Test connection from service
docker compose exec go-backend nc -zv nats 4222

# 5. Check for JetStream
curl http://localhost:8222/jsz | jq

# 6. Restart NATS if needed
docker compose restart nats
```

---

## Performance Problems

### Slow API Response Times

**Diagnostic Steps:**

```bash
# 1. Check system resources
docker stats --no-stream

# 2. Check database query performance
docker compose exec postgres psql -U tracertm -c \
  "SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 10;"

# 3. Check for slow queries
docker compose logs python-backend | grep "slow query"

# 4. Check Redis cache hit rate
docker compose exec redis redis-cli INFO stats | grep keyspace

# 5. Profile API endpoints
# Use tools like Apache Bench
ab -n 100 -c 10 http://localhost/api/v1/projects
```

**Solutions:**

#### High CPU Usage
```bash
# 1. Check which service is consuming CPU
docker stats --no-stream

# 2. Increase CPU limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '4'  # increase from 2

# 3. Scale horizontally
docker compose up -d --scale go-backend=3
```

#### High Memory Usage
```bash
# 1. Check memory usage
docker stats --format "table {{.Name}}\t{{.MemUsage}}"

# 2. Check for memory leaks
# Monitor memory over time
watch -n 5 'docker stats --no-stream --format "{{.Name}}: {{.MemPerc}}"'

# 3. Restart leaking service
docker compose restart go-backend

# 4. Increase memory limit
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

#### Slow Database Queries
```bash
# 1. Enable slow query logging
docker compose exec postgres psql -U tracertm -c \
  "ALTER SYSTEM SET log_min_duration_statement = 1000;"  # 1 second

# 2. Reload config
docker compose exec postgres psql -U tracertm -c "SELECT pg_reload_conf();"

# 3. Analyze slow queries
docker compose logs postgres | grep "duration:" | sort -rn

# 4. Create missing indexes
# Example:
docker compose exec postgres psql -U tracertm -c \
  "CREATE INDEX CONCURRENTLY idx_items_project_id ON items(project_id);"

# 5. Run VACUUM ANALYZE
docker compose exec postgres psql -U tracertm -c "VACUUM ANALYZE;"
```

#### Poor Cache Performance
```bash
# 1. Check cache hit rate
docker compose exec redis redis-cli INFO stats

# 2. Monitor cache keys
docker compose exec redis redis-cli MONITOR

# 3. Adjust TTL
# In .env:
CACHE_TTL=7200  # increase from 3600

# 4. Increase Redis memory
# In docker-compose.yml for redis:
command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

# 5. Restart Redis
docker compose restart redis
```

---

## Authentication Issues

### WorkOS Authentication Fails

**Symptoms:**
- Redirect loop
- "Invalid state" error
- "Invalid code" error

**Diagnostic Steps:**

```bash
# 1. Verify WorkOS configuration
echo "Client ID: ${WORKOS_CLIENT_ID}"
echo "Redirect URI: ${WORKOS_REDIRECT_URI}"

# 2. Check WorkOS dashboard
# https://dashboard.workos.com/
# Verify redirect URIs match exactly

# 3. Check backend logs
docker compose logs go-backend | grep -i "workos\|auth"
docker compose logs python-backend | grep -i "workos\|auth"

# 4. Test WorkOS API directly
curl -H "Authorization: Bearer ${WORKOS_API_KEY}" \
  https://api.workos.com/organizations
```

**Solutions:**

#### Redirect URI Mismatch
```bash
# 1. Check configured URIs
echo $WORKOS_REDIRECT_URI

# 2. Update to match WorkOS dashboard
# Development:
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback

# Production:
WORKOS_REDIRECT_URI=https://tracertm.example.com/auth/callback

# 3. Restart services
docker compose restart go-backend python-backend
```

#### Invalid API Key
```bash
# 1. Verify API key is correct
# Check WorkOS dashboard: https://dashboard.workos.com/api-keys

# 2. Update .env
WORKOS_API_KEY=sk_live_NEW_KEY

# 3. Restart services
docker compose restart go-backend python-backend
```

#### Cookie/Session Issues
```bash
# 1. Clear browser cookies
# 2. Check session configuration
echo "SESSION_SECURE: ${SESSION_SECURE}"
echo "SESSION_SAMESITE: ${SESSION_SAMESITE}"

# 3. For local development, disable secure flag
SESSION_SECURE=false

# 4. For production, ensure HTTPS
SESSION_SECURE=true
SESSION_SAMESITE=strict
```

### JWT Token Issues

**Symptoms:**
- "Token expired"
- "Invalid token"
- "Signature verification failed"

**Solutions:**

```bash
# 1. Verify JWT secret is same across services
docker compose exec go-backend env | grep JWT_SECRET
docker compose exec python-backend env | grep JWT_SECRET

# 2. Check token expiry
# In .env:
JWT_EXPIRY=24h

# 3. Decode JWT to inspect (without verification)
# Use https://jwt.io or:
echo "TOKEN" | cut -d'.' -f2 | base64 -d | jq

# 4. Test token generation
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

---

## Database Issues

### Database Locked

**Symptom:**
```
database is locked
could not obtain lock
```

**Solution:**
```bash
# 1. Check for long-running queries
docker compose exec postgres psql -U tracertm -c \
  "SELECT pid, usename, state, query_start, query
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY query_start;"

# 2. Check for locks
docker compose exec postgres psql -U tracertm -c \
  "SELECT * FROM pg_locks WHERE NOT granted;"

# 3. Kill blocking queries
docker compose exec postgres psql -U tracertm -c \
  "SELECT pg_terminate_backend(PID);"

# 4. If persistent, restart PostgreSQL
docker compose restart postgres
```

### 500 relation "…" does not exist (UndefinedTableError)

**Symptom:**
Python backend returns 500 with:
```
asyncpg.exceptions.UndefinedTableError: relation "test_cases" does not exist
```
(or `links`, `graphs`, `test_runs`, etc.)

**Cause:** The Python backend uses Alembic migrations; the database has not had them applied.

**Solution:**
```bash
# From repo root, with DATABASE_URL (or TRACERTM_DATABASE_URL) set (e.g. in .env)
./scripts/run_python_migrations.sh

# Or manually:
uv run alembic upgrade head
```
Verify: `uv run alembic current` should show the latest revision.

### Migrations Failed

**Symptom:**
```
migration version XXX already applied
migration failed: duplicate key value
```

**Solution:**
```bash
# 1. Check migration status
docker compose exec python-backend alembic current

# 2. View migration history
docker compose exec python-backend alembic history

# 3. Rollback one version
docker compose exec python-backend alembic downgrade -1

# 4. Re-apply
docker compose exec python-backend alembic upgrade head

# 5. If completely broken, reset migrations
docker compose exec postgres psql -U tracertm -c \
  "DROP TABLE IF EXISTS alembic_version;"

docker compose exec python-backend alembic upgrade head
```

### Database Full

**Symptom:**
```
ERROR: could not extend file: No space left on device
```

**Solution:**
```bash
# 1. Check disk space
df -h

# 2. Check database size
docker compose exec postgres psql -U tracertm -c \
  "SELECT pg_size_pretty(pg_database_size('tracertm'));"

# 3. Check table sizes
docker compose exec postgres psql -U tracertm -c \
  "SELECT schemaname, tablename,
          pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
   LIMIT 10;"

# 4. Clean up old data
# Example: Delete old records
docker compose exec postgres psql -U tracertm -c \
  "DELETE FROM events WHERE created_at < NOW() - INTERVAL '90 days';"

# 5. Vacuum to reclaim space
docker compose exec postgres psql -U tracertm -c "VACUUM FULL;"

# 6. Expand disk if needed
# Cloud provider specific
```

---

## Cache and Message Broker

### Redis Out of Memory

**Symptom:**
```
OOM command not allowed when used memory > 'maxmemory'
```

**Solution:**
```bash
# 1. Check memory usage
docker compose exec redis redis-cli INFO memory

# 2. Increase maxmemory
docker compose exec redis redis-cli CONFIG SET maxmemory 2gb

# 3. Set eviction policy
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 4. Flush cache if needed (caution!)
docker compose exec redis redis-cli FLUSHDB

# 5. Make permanent in docker-compose.yml
# redis:
#   command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

# 6. Restart Redis
docker compose restart redis
```

### NATS Connection Issues

**Symptom:**
```
nats: no servers available for connection
```

**Solution:**
```bash
# 1. Check NATS status
docker compose ps nats
docker compose logs nats

# 2. Check NATS health
curl http://localhost:8222/healthz

# 3. Check JetStream status
curl http://localhost:8222/jsz | jq '.config.max_memory'

# 4. Test connection
docker compose exec go-backend sh -c \
  'echo "test" | nats pub test.subject -s nats://nats:4222'

# 5. Restart NATS
docker compose restart nats

# 6. Recreate streams if corrupted
docker compose exec go-backend sh -c \
  'nats stream rm tracertm -f && nats stream add tracertm'
```

---

## API Errors

### 500 Internal Server Error

**Diagnostic:**
```bash
# 1. Check backend logs
docker compose logs --tail=100 go-backend
docker compose logs --tail=100 python-backend

# 2. Enable debug mode
# In .env:
GIN_MODE=debug
LOG_LEVEL=DEBUG

# 3. Restart services
docker compose restart go-backend python-backend

# 4. Reproduce error and check logs
curl -v http://localhost/api/v1/projects
docker compose logs --follow go-backend
```

### 503 Service Unavailable

**Diagnostic:**
```bash
# 1. Check health endpoints
curl http://localhost/health
curl http://localhost/health/go
curl http://localhost/health/python

# 2. Check service status
docker compose ps

# 3. Check backend connectivity
docker compose exec nginx ping go-backend
docker compose exec nginx ping python-backend

# 4. Restart unhealthy services
docker compose restart go-backend python-backend
```

### 429 Too Many Requests

**Diagnostic:**
```bash
# 1. Check rate limiting configuration
echo "RATE_LIMIT_ENABLED: ${RATE_LIMIT_ENABLED}"
echo "RATE_LIMIT_REQUESTS: ${RATE_LIMIT_REQUESTS}"

# 2. Check Nginx rate limiting
docker compose exec nginx cat /etc/nginx/nginx.conf | grep limit_req

# 3. Check Redis for rate limit keys
docker compose exec redis redis-cli --scan --pattern 'ratelimit:*'
```

**Solution:**
```bash
# 1. Increase rate limits
# In .env:
RATE_LIMIT_REQUESTS=500  # from 100
RATE_LIMIT_WINDOW=60

# 2. Or disable temporarily
RATE_LIMIT_ENABLED=false

# 3. Restart services
docker compose restart go-backend nginx
```

---

## Frontend Issues

### Cannot Connect to Backend

**Diagnostic:**
```bash
# 1. Check API base URL
echo $VITE_API_BASE_URL

# 2. Test API from browser console
fetch('http://localhost:4000/health')
  .then(r => r.text())
  .then(console.log)

# 3. Check CORS headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -I http://localhost/api/v1/projects
```

**Solution:**
```bash
# 1. Update VITE_API_BASE_URL
# In frontend/.env.local:
VITE_API_BASE_URL=http://localhost:4000

# 2. Add origin to CORS allowed list
# In backend .env:
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# 3. Restart frontend and backend
cd frontend && bun run dev
docker compose restart go-backend
```

### WebSocket Connection Failed

**Diagnostic:**
```bash
# 1. Check WebSocket URL
echo $VITE_WS_URL

# 2. Test WebSocket endpoint
wscat -c ws://localhost:4000/api/v1/ws

# 3. Check WebSocket logs
docker compose logs go-backend | grep -i websocket
```

**Solution:**
```bash
# 1. Verify WebSocket enabled
# In .env:
ENABLE_WEBSOCKET=true

# 2. Check Nginx WebSocket configuration
# nginx/nginx.conf should have:
# location /ws {
#   proxy_http_version 1.1;
#   proxy_set_header Upgrade $http_upgrade;
#   proxy_set_header Connection "Upgrade";
# }

# 3. Restart services
docker compose restart nginx go-backend
```

---

## Log Analysis Techniques

### Filtering Logs

```bash
# By severity
docker compose logs | grep -i error
docker compose logs | grep -i warn

# By time range
docker compose logs --since 2024-01-01T00:00:00
docker compose logs --until 2024-01-01T23:59:59

# By service
docker compose logs go-backend python-backend

# Exclude noise
docker compose logs | grep -v "health check"

# Count errors by type
docker compose logs | grep ERROR | cut -d':' -f3 | sort | uniq -c | sort -rn
```

### Structured Log Analysis

```bash
# Parse JSON logs
docker compose logs --json go-backend | jq '.log | fromjson'

# Filter by field
docker compose logs --json | jq 'select(.log | contains("error"))'

# Extract specific fields
docker compose logs --json python-backend | \
  jq -r '.log | fromjson | "\(.timestamp) \(.level) \(.message)"'
```

### Performance Analysis

```bash
# Response time analysis
docker compose logs nginx | \
  grep -oP 'request_time=\K[0-9.]+' | \
  awk '{sum+=$1; count++} END {print "Avg:", sum/count, "Max:", max}'

# Slow query detection
docker compose logs postgres | \
  grep "duration:" | \
  awk -F'duration: ' '{print $2}' | \
  sort -rn | head -10
```

---

## Debug Mode Activation

### Enable Debug Logging

#### Go Backend
```bash
# In .env
GIN_MODE=debug

# Restart
docker compose restart go-backend

# View debug logs
docker compose logs -f go-backend
```

#### Python Backend
```bash
# In .env
LOG_LEVEL=DEBUG

# Restart
docker compose restart python-backend

# View debug logs
docker compose logs -f python-backend
```

### Interactive Debugging

#### Attach to Running Container
```bash
# Execute shell in container
docker compose exec go-backend sh

# View environment
env | grep -E 'DATABASE|REDIS|NATS'

# Test connectivity
ping postgres
curl http://python-backend:8000/health

# Check processes
ps aux

# Exit
exit
```

#### Run Commands in Container
```bash
# Test database connection
docker compose exec go-backend psql -h postgres -U tracertm -d tracertm

# Check Go version
docker compose exec go-backend go version

# Check Python version
docker compose exec python-backend python --version
```

### Prometheus Metrics

```bash
# Go backend metrics
curl http://localhost:8080/metrics

# Python backend metrics
curl http://localhost:4000/metrics

# Filter specific metrics
curl http://localhost:8080/metrics | grep http_requests_total
```

---

## Network and Connectivity

### DNS Resolution Issues

```bash
# Test DNS from container
docker compose exec go-backend nslookup postgres
docker compose exec go-backend nslookup google.com

# Check /etc/hosts
docker compose exec go-backend cat /etc/hosts

# Check /etc/resolv.conf
docker compose exec go-backend cat /etc/resolv.conf
```

### Port Conflicts

```bash
# Find what's using a port
lsof -i :8080
netstat -tulpn | grep :8080

# Check Docker port mappings
docker compose ps
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

### Network Inspection

```bash
# List Docker networks
docker network ls

# Inspect tracertm network
docker network inspect tracertm_tracertm

# Check container IPs
docker compose exec go-backend hostname -i

# Test connectivity between containers
docker compose exec go-backend ping python-backend
docker compose exec go-backend telnet postgres 5432
```

---

## Docker and Container Issues

### Container Keeps Restarting

```bash
# Check restart reason
docker compose ps
docker inspect tracertm-go-backend | jq '.[0].State'

# View crash logs
docker compose logs --tail=200 go-backend

# Check exit code
docker compose ps | grep go-backend
# Exit 0 = clean exit
# Exit 1 = error
# Exit 137 = killed (OOM)
# Exit 139 = segfault
```

### Disk Space Issues

```bash
# Check disk usage
df -h
docker system df

# Clean Docker resources
docker system prune -a --volumes -f

# Remove specific items
docker image prune -a
docker volume prune
docker network prune

# Remove old containers
docker ps -a -f status=exited -q | xargs docker rm
```

### Volume Corruption

```bash
# Backup volume
docker run --rm \
  -v tracertm_postgres_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/postgres-$(date +%Y%m%d).tar.gz /data

# Remove corrupted volume
docker compose down -v
docker volume rm tracertm_postgres_data

# Restore from backup
docker volume create tracertm_postgres_data
docker run --rm \
  -v tracertm_postgres_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/postgres-YYYYMMDD.tar.gz -C /

# Restart services
docker compose up -d
```

---

## Emergency Procedures

### Complete Service Reset

```bash
# 1. Backup data first!
./scripts/backup-postgres.sh

# 2. Stop all services
docker compose down

# 3. Remove all containers, networks, volumes
docker compose down -v
docker system prune -a -f

# 4. Rebuild from scratch
docker compose build --no-cache
docker compose up -d

# 5. Restore data
cat /backup/tracertm_LATEST.dump.gz | gunzip | \
  docker compose exec -T postgres pg_restore -U tracertm -d tracertm -c
```

### Rollback to Previous Version

```bash
# 1. Stop services
docker compose down

# 2. Checkout previous version
git checkout backup-YYYYMMDD-HHMMSS

# 3. Rebuild and start
docker compose build
docker compose up -d

# 4. Verify
curl http://localhost/health
```

---

## Getting Help

If the issue persists after trying these troubleshooting steps:

1. **Gather diagnostic information:**
   ```bash
   # System info
   uname -a
   docker version
   docker compose version

   # Service status
   docker compose ps

   # Recent logs
   docker compose logs --tail=200 > logs-$(date +%Y%m%d).txt

   # Configuration (sanitized)
   cat .env | sed 's/=.*/=***/' > config-sanitized.txt
   ```

2. **Check existing issues:**
   - GitHub Issues: [github.com/your-org/tracertm/issues](https://github.com/your-org/tracertm/issues)
   - Documentation: [docs/INDEX.md](/docs/INDEX.md)

3. **File a new issue** with:
   - Detailed description of the problem
   - Steps to reproduce
   - Diagnostic logs
   - Environment details

---

For additional information, see:

- [Production Deployment Guide](/docs/guides/PRODUCTION_DEPLOYMENT.md)
- [Operations Runbook](/docs/guides/OPERATIONS_RUNBOOK.md)
- [Environment Configuration Guide](/docs/guides/ENVIRONMENT_CONFIGURATION.md)
