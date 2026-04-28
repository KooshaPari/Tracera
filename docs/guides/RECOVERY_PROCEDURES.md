# Recovery Procedures

## Overview

This document provides detailed recovery procedures for all TraceRTM services when chaos events or failures occur. All procedures are designed to achieve recovery within **30 seconds** (SLA target).

---

## Quick Recovery Commands

### PostgreSQL

```bash
# Status check
pg_isready -h localhost -p 5432 -U tracertm

# Restart (macOS Homebrew)
brew services restart postgresql@17

# Restart (Linux systemd)
sudo systemctl restart postgresql

# Verify connection
psql -U tracertm -d tracertm -c "SELECT 1"

# Check active connections
psql -U tracertm -d tracertm -c "SELECT count(*) FROM pg_stat_activity"
```

**Expected Recovery Time:** 5-10 seconds

---

### Redis

```bash
# Status check
redis-cli ping

# Restart (macOS Homebrew)
brew services restart redis

# Restart (Linux systemd)
sudo systemctl restart redis

# Verify connection
redis-cli SET recovery_test "ok"
redis-cli GET recovery_test

# Check memory usage
redis-cli INFO memory | grep used_memory_human
```

**Expected Recovery Time:** 2-5 seconds

---

### NATS

```bash
# Status check
curl http://localhost:8222/healthz

# Restart (macOS Homebrew)
brew services restart nats-server

# Restart (Linux systemd)
sudo systemctl restart nats-server

# Verify connection
nats-top
```

**Expected Recovery Time:** 3-7 seconds

---

### Neo4j

```bash
# Status check
curl http://localhost:7474/

# Restart (macOS Homebrew)
neo4j restart

# Restart (Linux systemd)
sudo systemctl restart neo4j

# Verify via Cypher
cypher-shell -u neo4j -p password "RETURN 1"
```

**Expected Recovery Time:** 15-20 seconds

---

### Go Backend

```bash
# Status check
curl http://localhost:8080/health

# Restart via process-compose
process-compose project restart go-backend

# Restart via systemd (production)
sudo systemctl restart tracertm-go-backend

# Check logs
tail -f .process-compose/logs/go-backend.log

# Verify API
curl http://localhost:8080/api/v1/health
```

**Expected Recovery Time:** 10-15 seconds

---

### Python Backend

```bash
# Status check
curl http://localhost:8000/health

# Restart via process-compose
process-compose project restart python-backend

# Restart via systemd (production)
sudo systemctl restart tracertm-python-backend

# Check logs
tail -f .process-compose/logs/python-backend.log

# Verify API
curl http://localhost:8000/docs  # OpenAPI docs
```

**Expected Recovery Time:** 5-10 seconds

---

### Temporal

```bash
# Status check
temporal operator cluster health

# Restart (Docker)
docker restart temporal

# Restart (macOS Homebrew)
brew services restart temporal

# Verify connection
temporal workflow list
```

**Expected Recovery Time:** 20-25 seconds

---

### Frontend (Vite Dev Server)

```bash
# Status check
curl http://localhost:5173/

# Restart via process-compose
process-compose project restart frontend

# Restart manually
cd frontend && bun run dev

# Check logs
tail -f .process-compose/logs/frontend.log
```

**Expected Recovery Time:** 15-20 seconds

---

## Cascading Failure Recovery

### Scenario: Database + Redis Both Down

**Recovery Order:**
1. PostgreSQL (5-10s)
2. Redis (2-5s)
3. Backend services auto-reconnect (5-10s)

**Total Recovery Time:** ~20-25 seconds

**Commands:**
```bash
# Step 1: Restart PostgreSQL
brew services restart postgresql@17
sleep 5

# Step 2: Restart Redis
brew services restart redis
sleep 3

# Step 3: Verify backends reconnected
curl http://localhost:8080/health
curl http://localhost:8000/health

# Step 4: Check connection pools
psql -U tracertm -d tracertm -c "SELECT count(*) FROM pg_stat_activity"
redis-cli INFO clients
```

---

### Scenario: All Infrastructure Down

**Recovery Order:**
1. PostgreSQL
2. Redis
3. Neo4j
4. NATS
5. Temporal
6. Backend services
7. Frontend

**Total Recovery Time:** ~30 seconds (within SLA)

**Script:** `scripts/recovery-all-services.sh`

```bash
#!/usr/bin/env bash
echo "Starting full system recovery..."

echo "[1/7] Restarting PostgreSQL..."
brew services restart postgresql@17
sleep 5

echo "[2/7] Restarting Redis..."
brew services restart redis
sleep 3

echo "[3/7] Restarting Neo4j..."
neo4j restart
sleep 15

echo "[4/7] Restarting NATS..."
brew services restart nats-server
sleep 3

echo "[5/7] Restarting Temporal..."
brew services restart temporal
sleep 10

echo "[6/7] Restarting backends..."
process-compose project restart go-backend
process-compose project restart python-backend
sleep 10

echo "[7/7] Restarting frontend..."
process-compose project restart frontend

echo "Recovery complete. Verifying health..."
curl -f http://localhost:8080/health && echo "✓ Go backend OK"
curl -f http://localhost:8000/health && echo "✓ Python backend OK"
curl -f http://localhost:5173/ && echo "✓ Frontend OK"
```

---

## Automated Recovery (Production)

### Systemd Service Configuration

All production services should have systemd auto-restart:

```ini
[Unit]
Description=TraceRTM Go Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=tracertm
WorkingDirectory=/opt/tracertm/backend
ExecStart=/opt/tracertm/backend/tracertm-backend
Restart=on-failure
RestartSec=5s
StartLimitInterval=60s
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```

**Key Settings:**
- `Restart=on-failure`: Auto-restart on crash
- `RestartSec=5s`: Wait 5s before restart
- `StartLimitBurst=3`: Max 3 restarts in 60s

---

### Kubernetes Liveness Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Recovery Behavior:**
- Liveness failure → Pod restart (recovery ~20s)
- Readiness failure → Remove from load balancer (no restart)

---

## Connection Pool Recovery

### PostgreSQL Connection Pool

```go
// Go backend connection pool settings
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(10)
db.SetConnMaxLifetime(5 * time.Minute)
db.SetConnMaxIdleTime(1 * time.Minute)
```

**Recovery Behavior:**
- Broken connections are detected on next use
- Pool automatically creates new connections
- Recovery time: ~2-5 seconds

---

### Redis Connection Pool

```python
# Python backend Redis pool
redis_pool = redis.ConnectionPool(
    host="localhost",
    port=6379,
    max_connections=50,
    socket_connect_timeout=5,
    socket_keepalive=True,
    health_check_interval=30,
)
```

**Recovery Behavior:**
- Health checks detect connection failures
- Pool recreates connections automatically
- Recovery time: ~1-3 seconds

---

## Circuit Breaker Recovery

Backend services implement circuit breakers for downstream dependencies:

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
async def call_external_service():
    # Circuit opens after 5 failures
    # Attempts recovery after 30 seconds
    pass
```

**States:**
- **Closed:** Normal operation
- **Open:** All requests fail immediately (no backend calls)
- **Half-Open:** Test requests to check recovery

**Recovery Time:** 30 seconds (configurable)

---

## Monitoring Recovery

### Prometheus Queries

```promql
# Track service uptime
up{job="tracertm-backend"}

# Monitor recovery time
increase(service_recovery_duration_seconds[5m])

# Connection pool saturation
pg_stat_database_numbackends / pg_settings_max_connections

# Request success rate
rate(http_requests_total{status="200"}[1m])
```

### Grafana Alerts

```yaml
- alert: ServiceRecoveryExceeded
  expr: service_recovery_duration_seconds > 30
  for: 1m
  annotations:
    summary: "Service recovery exceeded 30s SLA"

- alert: HighConnectionPoolUtilization
  expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.9
  for: 2m
  annotations:
    summary: "Connection pool near exhaustion"
```

---

## Post-Recovery Verification

After any recovery, verify system health:

```bash
# 1. Check all service health endpoints
curl -f http://localhost:8080/health  # Go backend
curl -f http://localhost:8000/health  # Python backend
curl -f http://localhost:5173/        # Frontend

# 2. Verify database connectivity
psql -U tracertm -d tracertm -c "SELECT NOW()"

# 3. Verify cache
redis-cli PING

# 4. Check message queue
curl http://localhost:8222/healthz

# 5. Run smoke tests
pytest tests/integration/test_health_checks.py -v

# 6. Monitor logs for errors
tail -f .process-compose/logs/*.log | grep -i error
```

---

## Runbook: Database Connection Failure

### Symptoms
- API returns 500 errors
- Logs show "connection refused" or "max connections"
- Health checks fail

### Diagnosis
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check active connections
psql -U tracertm -d tracertm -c "
  SELECT count(*), state
  FROM pg_stat_activity
  GROUP BY state
"

# Check for long-running queries
psql -U tracertm -d tracertm -c "
  SELECT pid, now() - query_start AS duration, query
  FROM pg_stat_activity
  WHERE state = 'active'
  ORDER BY duration DESC
"
```

### Resolution
1. **If PostgreSQL is down:**
   ```bash
   brew services restart postgresql@17
   ```

2. **If connection pool exhausted:**
   ```bash
   # Kill idle connections
   psql -U tracertm -d tracertm -c "
     SELECT pg_terminate_backend(pid)
     FROM pg_stat_activity
     WHERE state = 'idle' AND query_start < NOW() - INTERVAL '5 minutes'
   "
   ```

3. **If long-running query blocking:**
   ```bash
   # Cancel blocking query (find PID from diagnosis query)
   psql -U tracertm -d tracertm -c "SELECT pg_cancel_backend(<PID>)"
   ```

**Expected Recovery:** 5-10 seconds

---

## Runbook: Redis Connection Failure

### Symptoms
- Cache miss rate spikes to 100%
- Logs show Redis connection errors
- Session management fails

### Diagnosis
```bash
# Check if Redis is running
redis-cli ping

# Check memory usage
redis-cli INFO memory

# Check for blocked clients
redis-cli CLIENT LIST
```

### Resolution
1. **If Redis is down:**
   ```bash
   brew services restart redis
   ```

2. **If memory exhausted:**
   ```bash
   # Check eviction policy
   redis-cli CONFIG GET maxmemory-policy

   # Flush expired keys
   redis-cli --scan --pattern "*" | xargs redis-cli DEL
   ```

**Expected Recovery:** 2-5 seconds

---

## Contact Information

**On-Call Engineer:** See PagerDuty rotation
**Slack Channel:** #tracertm-ops
**Escalation:** See `docs/escalation-policy.md`

---

**Last Updated:** 2026-02-01
**Review Cycle:** Monthly
