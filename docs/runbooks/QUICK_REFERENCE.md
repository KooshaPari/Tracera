# Incident Response Quick Reference

**Emergency Hotline**: [Add your on-call number]
**Status Page**: [Add your status page URL]
**Last Updated**: 2026-02-01

## Quick Access

```bash
# Interactive menu
./scripts/runbook-quick-access.sh

# Specific scenario
./scripts/runbook-quick-access.sh [database|latency|memory|disk|network|auth|cache]

# List all runbooks
./scripts/runbook-quick-access.sh list

# Run tests
./scripts/runbook-quick-access.sh test
```

## At-a-Glance Troubleshooting

### 1. Database Connection Failures ⚠️ CRITICAL
**Response Time**: < 5 minutes | [Full Runbook](./database-connection-failures.md)

```bash
# Quick check
docker-compose ps postgres
docker-compose exec backend python -c "from backend.core.database import engine; engine.connect()"

# Quick fix
docker-compose restart postgres
docker-compose restart backend
```

**Common causes**: Connection pool exhausted, database down, network partition

---

### 2. High Latency / Timeouts ⚠️ HIGH
**Response Time**: < 10 minutes | [Full Runbook](./high-latency-timeouts.md)

```bash
# Quick check
curl -w "@-" -o /dev/null -s http://localhost:8000/api/v1/items <<'EOF'
time_total: %{time_total}s
EOF

docker-compose exec postgres psql -U postgres -d trace -c "
SELECT pid, now() - query_start AS duration, LEFT(query, 50)
FROM pg_stat_activity WHERE state != 'idle' ORDER BY duration DESC LIMIT 5;"

# Quick fix - Kill slow query
# Get PID from above, then:
docker-compose exec postgres psql -U postgres -d trace -c "SELECT pg_terminate_backend([PID]);"
```

**Common causes**: Slow queries, missing indexes, resource contention, external API delays

---

### 3. Memory Exhaustion ⚠️ CRITICAL
**Response Time**: < 5 minutes | [Full Runbook](./memory-exhaustion.md)

```bash
# Quick check
docker stats --no-stream
free -h

# Quick fix - Restart to free memory
docker-compose restart backend

# Increase memory limit (docker-compose.yml)
# deploy.resources.limits.memory: 2G
docker-compose up -d backend
```

**Common causes**: Memory leaks, unbounded caching, large dataset processing, connection leaks

---

### 4. Disk Space Issues ⚠️ HIGH
**Response Time**: < 15 minutes | [Full Runbook](./disk-space-issues.md)

```bash
# Quick check
df -h
docker system df

# Emergency cleanup
docker system prune -af --volumes
find /var/log -name "*.log" -mtime +7 -delete
docker-compose exec postgres psql -U postgres -d trace -c "VACUUM FULL;"
```

**Common causes**: Log accumulation, Docker image sprawl, database bloat, temp files

---

### 5. Network Partitions ⚠️ CRITICAL
**Response Time**: < 5 minutes | [Full Runbook](./network-partitions.md)

```bash
# Quick check
docker-compose exec backend ping -c 3 postgres
docker-compose exec backend nslookup postgres
docker-compose exec backend nc -zv postgres 5432

# Quick fix - Recreate network
docker-compose down
docker network prune -f
docker-compose up -d
```

**Common causes**: Docker network issues, DNS failures, firewall rules, container isolation

---

### 6. Authentication Failures ⚠️ HIGH
**Response Time**: < 10 minutes | [Full Runbook](./authentication-failures.md)

```bash
# Quick check
curl -I http://localhost:8000/health
curl -I http://localhost:8000/api/v1/items  # Should return 401
docker-compose exec redis redis-cli KEYS "session:*"

# Quick fix - Clear sessions
docker-compose exec redis redis-cli FLUSHDB
docker-compose restart backend

# Verify OAuth config
docker-compose exec backend env | grep WORKOS
```

**Common causes**: OAuth misconfiguration, token expiration, session storage issues, CORS

---

### 7. Cache Invalidation Issues ⚠️ MEDIUM
**Response Time**: < 20 minutes | [Full Runbook](./cache-invalidation-issues.md)

```bash
# Quick check
docker-compose exec redis redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses"
docker-compose exec redis redis-cli DBSIZE
docker-compose exec redis redis-cli INFO memory | grep used_memory_human

# Quick fix - Clear cache
docker-compose exec redis redis-cli FLUSHDB

# Check eviction policy
docker-compose exec redis redis-cli CONFIG GET maxmemory-policy
# Set to: allkeys-lru
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

**Common causes**: Missing TTL, no invalidation on write, memory bloat, cache stampede

---

## Common Commands

### Service Management
```bash
# Restart service
docker-compose restart [service-name]

# View logs
docker-compose logs -f [service-name]

# Service status
docker-compose ps

# Restart all services
docker-compose restart
```

### Database
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d trace

# Check connections
docker-compose exec postgres psql -U postgres -d trace -c "
SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Vacuum database
docker-compose exec postgres psql -U postgres -d trace -c "VACUUM ANALYZE;"
```

### Cache
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Clear all cache
docker-compose exec redis redis-cli FLUSHDB

# View keys
docker-compose exec redis redis-cli KEYS "*"

# Delete pattern
docker-compose exec redis redis-cli --scan --pattern "cache:*" | xargs docker-compose exec redis redis-cli DEL
```

### Monitoring
```bash
# Prometheus queries
curl 'http://localhost:9090/api/v1/query?query=up'

# View traces
open http://localhost:16686

# Grafana dashboards
open http://localhost:3001
```

## Escalation Path

```
Incident Detected
       ↓
   Severity?
       ↓
    ┌──┴──┐
Critical  High    Medium
    ↓      ↓        ↓
  Page   Notify   Ticket
  On-Call  Lead
    ↓      ↓        ↓
15min?  1hr?    4hr?
    ↓      ↓        ↓
Escalate → Senior Engineer
           ↓
    Incident Commander
           ↓
    Blameless Postmortem
```

## Communication Template

```
[INCIDENT] [Severity] - [Brief Description]

Status: Investigating / Identified / Fixing / Monitoring / Resolved
Impact: [User impact description]
Started: [Timestamp]
Services Affected: [List]
Current Action: [What's being done]
ETA: [Expected resolution time]
Updates: Every [X] minutes

Root Cause: [Once identified]
Resolution: [Actions taken]
Prevention: [Follow-up tasks]
```

## Post-Incident Checklist

- [ ] Incident documented in log
- [ ] Root cause identified
- [ ] Fix verified in production
- [ ] Monitoring alerts reviewed/updated
- [ ] Runbook updated if needed
- [ ] Blameless postmortem scheduled (Critical/High)
- [ ] Prevention tasks created
- [ ] Team notified of resolution

## Contact Information

| Role | Name | Contact |
|------|------|---------|
| On-Call Engineer | [Name] | [Phone/Slack] |
| Team Lead | [Name] | [Phone/Slack] |
| Senior Engineer | [Name] | [Phone/Slack] |
| DevOps | [Name] | [Phone/Slack] |

## Resources

- **Runbooks**: `docs/runbooks/`
- **Monitoring**: http://localhost:3001 (Grafana)
- **Metrics**: http://localhost:9090 (Prometheus)
- **Traces**: http://localhost:16686 (Jaeger)
- **Deployment Guide**: `docs/guides/DEPLOYMENT_GUIDE.md`
- **Architecture**: `docs/01-getting-started/README.md`

---

**Keep this card accessible during incidents!**
Print or bookmark for quick reference during high-pressure situations.
