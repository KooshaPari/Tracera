# Operations Runbook

Comprehensive guide for day-to-day operations and incident response for TracerTM production environments.

## Table of Contents

- [Service Monitoring](#service-monitoring)
- [Common Operational Tasks](#common-operational-tasks)
- [Incident Response](#incident-response)
- [Scaling Procedures](#scaling-procedures)
- [Performance Tuning](#performance-tuning)
- [Log Management](#log-management)
- [Database Maintenance](#database-maintenance)
- [On-Call Procedures](#on-call-procedures)

---

## Service Monitoring

### Daily Health Checks

Run the automated health check script:

```bash
/opt/tracertm/scripts/health-check.sh tracertm.example.com
```

Expected output:
```
TracerTM Health Check
=====================
Docker: ✓
All services running: ✓ (9/9)
Gateway health: ✓
Go backend: ✓
Python backend: ✓
SSL: ✓
Database: ✓
Redis: ✓
NATS: ✓
```

### Key Metrics to Monitor

#### Application Metrics

| Metric | Normal Range | Warning | Critical | Action |
|--------|--------------|---------|----------|---------|
| **API Response Time** | < 200ms | > 500ms | > 1000ms | Check backend logs, database queries |
| **Error Rate** | < 0.1% | > 1% | > 5% | Review error logs, check dependencies |
| **Request Rate** | Baseline ±20% | Spike > 50% | Spike > 100% | Check for DDoS, review caching |
| **Active Connections** | < 1000 | > 2000 | > 5000 | Check connection pooling |

#### Infrastructure Metrics

| Metric | Normal Range | Warning | Critical | Action |
|--------|--------------|---------|----------|---------|
| **CPU Usage** | < 60% | > 75% | > 90% | Scale horizontally, optimize code |
| **Memory Usage** | < 70% | > 85% | > 95% | Investigate memory leaks, scale up |
| **Disk Usage** | < 70% | > 85% | > 95% | Clean logs, expand storage |
| **Network I/O** | < 70% capacity | > 85% | > 95% | Check for anomalies, upgrade network |

#### Database Metrics

| Metric | Normal Range | Warning | Critical | Action |
|--------|--------------|---------|----------|---------|
| **Connection Pool** | < 50% | > 75% | > 90% | Increase pool size, check queries |
| **Query Time** | < 100ms avg | > 500ms | > 1000ms | Optimize queries, add indexes |
| **Cache Hit Rate** | > 90% | < 80% | < 60% | Review caching strategy |
| **Replication Lag** | < 1s | > 5s | > 30s | Check replication health |

### Monitoring Tools Access

```bash
# Prometheus
https://tracertm.example.com:9090

# Grafana
https://tracertm.example.com:3000
User: admin
Pass: [see .env]

# NATS Monitoring
http://localhost:8222/varz

# PostgreSQL Stats
docker compose exec postgres psql -U tracertm -c \
  "SELECT * FROM pg_stat_activity WHERE state != 'idle';"
```

---

## Common Operational Tasks

### Service Management

#### Restart a Service

```bash
# Restart specific service
docker compose restart go-backend

# Restart all services
docker compose restart

# Restart with rebuild
docker compose up -d --build go-backend
```

#### View Service Logs

```bash
# Tail logs (follow mode)
docker compose logs -f go-backend

# Last 100 lines
docker compose logs --tail=100 go-backend

# All services
docker compose logs --tail=50 --follow

# Filter by time
docker compose logs --since 2024-01-01T00:00:00

# Save logs to file
docker compose logs --no-color > logs-$(date +%Y%m%d).txt
```

#### Check Service Status

```bash
# Docker Compose status
docker compose ps

# Detailed container info
docker inspect tracertm-go-backend

# Resource usage
docker stats --no-stream

# Network connectivity
docker compose exec go-backend ping python-backend
```

### Configuration Updates

#### Update Environment Variables

```bash
# Edit environment file
sudo nano /etc/tracertm/.env

# Restart affected services
docker compose up -d --force-recreate go-backend python-backend

# Verify changes
docker compose exec go-backend env | grep NEW_VARIABLE
```

#### Update Application Code

```bash
# Navigate to deployment directory
cd /opt/tracertm

# Backup current version
git tag backup-$(date +%Y%m%d-%H%M%S)

# Pull updates
git fetch --tags
git pull origin main

# Or checkout specific version
git checkout v1.1.0

# Rebuild and restart
docker compose build --no-cache
docker compose up -d

# Verify deployment
curl -f http://localhost/health
```

#### Rolling Update (Zero Downtime)

```bash
# Scale up
docker compose up -d --scale go-backend=2

# Wait for new instance to be healthy
sleep 30
curl -f http://localhost/health/go

# Remove old instance
docker compose up -d --scale go-backend=1
```

### User Management

#### Create Admin User

```bash
# Using Python backend CLI
docker compose exec python-backend python -m app.cli create-user \
  --email admin@example.com \
  --role admin

# Or via API
curl -X POST http://localhost/api/v1/auth/users \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "role": "admin",
    "name": "Admin User"
  }'
```

#### Reset User Password

```bash
# Generate password reset token
docker compose exec python-backend python -m app.cli reset-password \
  --email user@example.com

# Or use WorkOS dashboard
# https://dashboard.workos.com/
```

### Certificate Renewal

#### Let's Encrypt Certificates

```bash
# Check certificate expiration
sudo certbot certificates

# Manual renewal
sudo certbot renew

# Force renewal (for testing)
sudo certbot renew --force-renewal

# Reload Nginx after renewal
docker compose exec nginx nginx -s reload
```

#### Verify SSL Configuration

```bash
# Test SSL setup
openssl s_client -connect tracertm.example.com:443 -servername tracertm.example.com

# Check certificate details
echo | openssl s_client -connect tracertm.example.com:443 2>/dev/null | openssl x509 -noout -dates

# SSL Labs test
# https://www.ssllabs.com/ssltest/analyze.html?d=tracertm.example.com
```

---

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| **P0 - Critical** | Complete outage | Immediate | Site down, database unavailable |
| **P1 - High** | Major degradation | < 15 min | API errors > 10%, slow responses |
| **P2 - Medium** | Partial degradation | < 1 hour | Single service down, elevated errors |
| **P3 - Low** | Minor issues | < 4 hours | Cosmetic bugs, logging issues |

### Incident Response Workflow

#### 1. Acknowledge and Assess

```bash
# Check service status
docker compose ps

# Check recent logs
docker compose logs --tail=100 --follow

# Check system resources
docker stats --no-stream
df -h
free -m

# Check error rates in Grafana
# https://tracertm.example.com:3000
```

#### 2. Communicate

- Update status page
- Notify stakeholders via Slack/email
- Create incident ticket

#### 3. Mitigate

**Service Down:**
```bash
# Check if service crashed
docker compose ps | grep -E "Exit|Restarting"

# View crash logs
docker compose logs --tail=200 go-backend

# Restart service
docker compose restart go-backend

# If restart fails, check health
docker compose exec go-backend /app/tracertm-backend health
```

**High Error Rate:**
```bash
# Check error logs
docker compose logs go-backend | grep ERROR

# Check database connectivity
docker compose exec postgres pg_isready -U tracertm

# Check Redis
docker compose exec redis redis-cli ping

# Restart problematic service
docker compose restart go-backend
```

**Performance Degradation:**
```bash
# Check slow queries
docker compose exec postgres psql -U tracertm -c \
  "SELECT pid, query, query_start, state FROM pg_stat_activity
   WHERE state != 'idle' AND query_start < NOW() - INTERVAL '5 seconds';"

# Kill slow query
docker compose exec postgres psql -U tracertm -c \
  "SELECT pg_terminate_backend(PID);"

# Clear cache if needed
docker compose exec redis redis-cli FLUSHDB
```

#### 4. Restore Service

```bash
# If all else fails, rollback to previous version
cd /opt/tracertm
git checkout backup-YYYYMMDD-HHMMSS
docker compose build --no-cache
docker compose up -d

# Verify restoration
curl -f http://localhost/health
```

#### 5. Post-Incident Review

- Document root cause
- Update runbook
- Implement preventive measures
- Schedule post-mortem meeting

### Common Incident Scenarios

#### Scenario 1: Database Connection Pool Exhausted

**Symptoms:**
- Error logs: "connection pool exhausted"
- 503 errors from API
- High database connection count

**Resolution:**
```bash
# Check active connections
docker compose exec postgres psql -U tracertm -c \
  "SELECT COUNT(*) FROM pg_stat_activity WHERE state != 'idle';"

# Kill idle connections
docker compose exec postgres psql -U tracertm -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity
   WHERE state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes';"

# Increase pool size in .env
# DB_MAX_CONNECTIONS=150 (from 100)

# Restart backends
docker compose restart go-backend python-backend
```

#### Scenario 2: Out of Memory (OOM)

**Symptoms:**
- Service crashes without error logs
- `docker compose ps` shows "Exit 137"
- System logs show OOM killer

**Resolution:**
```bash
# Check system memory
free -m

# Check Docker container memory
docker stats --no-stream

# Restart crashed service
docker compose up -d go-backend

# Increase memory limits in docker-compose.yml
# resources:
#   limits:
#     memory: 4G  (from 2G)

# Apply changes
docker compose up -d --force-recreate
```

#### Scenario 3: Disk Full

**Symptoms:**
- Write errors in logs
- Services unable to start
- `df -h` shows 100% usage

**Resolution:**
```bash
# Check disk usage
df -h
du -sh /var/lib/docker/*

# Clean Docker resources
docker system prune -a --volumes -f

# Clean old logs
find /var/log -type f -name "*.log" -mtime +30 -delete

# Rotate logs
docker compose exec nginx logrotate -f /etc/logrotate.conf

# If still critical, expand disk or add volume
```

#### Scenario 4: SSL Certificate Expired

**Symptoms:**
- Browser shows security warning
- API calls fail with SSL errors
- Certificate expiration warnings

**Resolution:**
```bash
# Check certificate
sudo certbot certificates

# Renew immediately
sudo certbot renew --force-renewal

# Reload web server
docker compose exec nginx nginx -s reload

# Verify fix
curl -vI https://tracertm.example.com 2>&1 | grep "expire"
```

---

## Scaling Procedures

### Horizontal Scaling

#### Scale Up Services

```bash
# Scale Go backend to 3 instances
docker compose up -d --scale go-backend=3

# Verify scaling
docker compose ps | grep go-backend

# Check load distribution (nginx logs)
docker compose logs nginx | grep "go-backend"
```

#### Scale Down Services

```bash
# Scale back to 1 instance
docker compose up -d --scale go-backend=1

# Or stop specific instances
docker stop tracertm-go-backend-2
docker stop tracertm-go-backend-3
```

### Vertical Scaling

#### Increase Resource Limits

Edit `docker-compose.yml`:

```yaml
go-backend:
  deploy:
    resources:
      limits:
        cpus: '4'        # was 2
        memory: 4G       # was 2G
      reservations:
        cpus: '2'        # was 1
        memory: 2G       # was 1G
```

Apply changes:

```bash
docker compose up -d --force-recreate go-backend
```

### Database Scaling

#### Read Replicas

Add read replica to `docker-compose.yml`:

```yaml
postgres-replica:
  image: postgres:15-alpine
  environment:
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  command: |
    postgres -c wal_level=replica
             -c hot_standby=on
             -c max_wal_senders=10
             -c max_replication_slots=10
  volumes:
    - postgres_replica_data:/var/lib/postgresql/data
```

Configure streaming replication:

```bash
# On primary
docker compose exec postgres psql -U tracertm -c \
  "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replica_pass';"

# On replica
docker compose exec postgres-replica pg_basebackup \
  -h postgres -D /var/lib/postgresql/data -U replicator -P
```

Update application to use read replica for queries:

```env
DB_READ_URL=postgresql://tracertm:password@postgres-replica:5432/tracertm
```

---

## Performance Tuning

### Application Performance

#### Enable Response Compression

Already configured in Nginx (`nginx/nginx.conf`):

```nginx
gzip on;
gzip_comp_level 6;
gzip_types text/plain application/json;
```

#### Cache Configuration

```bash
# Adjust Redis cache TTL
# In .env:
CACHE_TTL=3600  # 1 hour

# Warm up cache on startup
docker compose exec python-backend python -m app.cli warm-cache
```

#### Connection Pooling

```env
# Go backend (in .env)
DB_MAX_OPEN_CONNS=100
DB_MAX_IDLE_CONNS=10
DB_CONN_MAX_LIFETIME=300

# Python backend
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

### Database Performance

#### Analyze Slow Queries

```bash
# Enable slow query logging
docker compose exec postgres psql -U tracertm -c \
  "ALTER SYSTEM SET log_min_duration_statement = 1000;"  # 1 second

# Reload config
docker compose exec postgres psql -U tracertm -c "SELECT pg_reload_conf();"

# View slow queries
docker compose exec postgres tail -f /var/lib/postgresql/data/log/postgresql-*.log | grep "duration:"
```

#### Create Indexes

```bash
# Identify missing indexes
docker compose exec postgres psql -U tracertm -c \
  "SELECT schemaname, tablename, attname, n_distinct, correlation
   FROM pg_stats
   WHERE schemaname = 'public' AND n_distinct > 100
   ORDER BY n_distinct DESC;"

# Create index
docker compose exec postgres psql -U tracertm -c \
  "CREATE INDEX CONCURRENTLY idx_items_created_at ON items(created_at);"
```

#### Vacuum and Analyze

```bash
# Manual vacuum
docker compose exec postgres psql -U tracertm -c "VACUUM ANALYZE;"

# Schedule automatic vacuum (already enabled by default)
docker compose exec postgres psql -U tracertm -c \
  "ALTER SYSTEM SET autovacuum = on;"
```

### Redis Performance

#### Monitor Redis Performance

```bash
# Redis stats
docker compose exec redis redis-cli INFO stats

# Monitor commands in real-time
docker compose exec redis redis-cli MONITOR

# Check memory usage
docker compose exec redis redis-cli INFO memory
```

#### Optimize Redis Memory

```bash
# Set maxmemory policy
docker compose exec redis redis-cli CONFIG SET maxmemory 2gb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Persist changes
docker compose exec redis redis-cli CONFIG REWRITE
```

---

## Log Management

### Log Locations

| Service | Container Path | Host Path (if mounted) |
|---------|----------------|------------------------|
| **Nginx** | `/var/log/nginx/` | `./logs/nginx/` |
| **Go Backend** | stdout/stderr | `docker compose logs` |
| **Python Backend** | stdout/stderr | `docker compose logs` |
| **PostgreSQL** | `/var/lib/postgresql/data/log/` | Volume |
| **Caddy** | `/tmp/caddy-*.log` | `./logs/caddy/` |

### Log Aggregation

#### Centralized Logging with Loki (Optional)

Add to `docker-compose.yml`:

```yaml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  volumes:
    - ./loki-config.yml:/etc/loki/local-config.yaml
    - loki_data:/loki

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/log:/var/log
    - ./promtail-config.yml:/etc/promtail/config.yml
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
  command: -config.file=/etc/promtail/config.yml
```

### Log Rotation

Create `/etc/logrotate.d/tracertm`:

```
/opt/tracertm/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root docker
    sharedscripts
    postrotate
        docker compose exec nginx nginx -s reopen
    endscript
}
```

Test rotation:

```bash
sudo logrotate -f /etc/logrotate.d/tracertm
```

### Log Analysis

#### Search Logs

```bash
# Search all logs for error
docker compose logs | grep -i error

# Search specific service for pattern
docker compose logs go-backend | grep "status: 500"

# Count errors by type
docker compose logs go-backend | grep ERROR | cut -d':' -f3 | sort | uniq -c

# Extract stack traces
docker compose logs python-backend | grep -A 10 "Traceback"
```

#### Export Logs

```bash
# Export last hour of logs
docker compose logs --since 1h > logs-$(date +%Y%m%d-%H%M%S).txt

# Export specific service
docker compose logs --no-color go-backend > go-backend-logs.txt

# Export to JSON (for analysis tools)
docker compose logs --json > logs.json
```

---

## Database Maintenance

### Routine Maintenance

#### Daily Tasks

```bash
# Vacuum analyze (automatic, but can run manually)
docker compose exec postgres psql -U tracertm -c "VACUUM ANALYZE;"

# Check database size
docker compose exec postgres psql -U tracertm -c \
  "SELECT pg_size_pretty(pg_database_size('tracertm'));"

# Check for bloat
docker compose exec postgres psql -U tracertm -c \
  "SELECT schemaname, tablename,
          pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
   LIMIT 10;"
```

#### Weekly Tasks

```bash
# Reindex tables
docker compose exec postgres psql -U tracertm -c "REINDEX DATABASE tracertm;"

# Update statistics
docker compose exec postgres psql -U tracertm -c "ANALYZE;"

# Check for unused indexes
docker compose exec postgres psql -U tracertm -f /opt/scripts/find-unused-indexes.sql
```

#### Monthly Tasks

```bash
# Full vacuum (requires downtime)
docker compose exec postgres psql -U tracertm -c "VACUUM FULL;"

# Backup verification
/opt/tracertm/scripts/verify-backup.sh
```

### Database Optimization

#### Find and Kill Long-Running Queries

```bash
# Find queries running > 5 minutes
docker compose exec postgres psql -U tracertm -c \
  "SELECT pid, usename, query_start, state, query
   FROM pg_stat_activity
   WHERE state != 'idle' AND query_start < NOW() - INTERVAL '5 minutes';"

# Kill specific query
docker compose exec postgres psql -U tracertm -c \
  "SELECT pg_terminate_backend(12345);"  # Replace with actual PID
```

#### Connection Monitoring

```bash
# Current connections
docker compose exec postgres psql -U tracertm -c \
  "SELECT COUNT(*), state FROM pg_stat_activity GROUP BY state;"

# Connections by application
docker compose exec postgres psql -U tracertm -c \
  "SELECT application_name, COUNT(*)
   FROM pg_stat_activity
   GROUP BY application_name;"
```

---

## On-Call Procedures

### On-Call Checklist

When going on-call:

- [ ] Verify access to monitoring dashboards
- [ ] Test incident notification channels
- [ ] Review recent incidents and changes
- [ ] Ensure access to production servers
- [ ] Have this runbook accessible
- [ ] Know escalation contacts

### Escalation Path

1. **Level 1** - On-call engineer (you)
2. **Level 2** - Senior engineer / Team lead
3. **Level 3** - Engineering manager
4. **Level 4** - CTO / VP Engineering

### Emergency Contacts

Keep an emergency contact list:

```
On-Call Rotation:
- Week 1: Engineer A - phone: xxx-xxx-xxxx
- Week 2: Engineer B - phone: xxx-xxx-xxxx

Escalation:
- Senior Engineer: phone: xxx-xxx-xxxx
- Manager: phone: xxx-xxx-xxxx

Vendors:
- AWS Support: xxx-xxx-xxxx (Case #: XXXXX)
- Database Admin: vendor@example.com
```

### Incident Documentation Template

```markdown
## Incident Report: [YYYY-MM-DD] [Brief Description]

**Severity:** P0/P1/P2/P3
**Start Time:** YYYY-MM-DD HH:MM UTC
**End Time:** YYYY-MM-DD HH:MM UTC
**Duration:** X hours Y minutes

### Impact
- Services affected: [list]
- Users affected: [estimated number/percentage]
- Revenue impact: [if applicable]

### Timeline
- HH:MM - Alert received
- HH:MM - Incident acknowledged
- HH:MM - Root cause identified
- HH:MM - Mitigation applied
- HH:MM - Service restored
- HH:MM - Incident closed

### Root Cause
[Detailed explanation]

### Resolution
[Steps taken to resolve]

### Prevention
- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

### Lessons Learned
[What went well, what could be improved]
```

---

## Appendix: Quick Reference Commands

### Service Commands

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart go-backend

# View logs
docker compose logs -f go-backend

# Check status
docker compose ps

# Update and restart
git pull && docker compose build && docker compose up -d
```

### Health Checks

```bash
# All health endpoints
curl http://localhost/health
curl http://localhost/health/go
curl http://localhost/health/python

# Database
docker compose exec postgres pg_isready -U tracertm

# Redis
docker compose exec redis redis-cli ping

# NATS
curl http://localhost:8222/healthz
```

### Emergency Procedures

```bash
# Rollback deployment
cd /opt/tracertm && git checkout backup-LATEST && docker compose up -d --build

# Emergency restart
docker compose down && docker compose up -d

# Force recreate all containers
docker compose up -d --force-recreate

# Restore database from backup
cat /backup/tracertm_LATEST.dump.gz | gunzip | docker compose exec -T postgres pg_restore -U tracertm -d tracertm -c
```

---

For additional information, see:

- [Production Deployment Guide](/docs/guides/PRODUCTION_DEPLOYMENT.md)
- [Troubleshooting Guide](/docs/guides/TROUBLESHOOTING.md)
- [Environment Configuration Guide](/docs/guides/ENVIRONMENT_CONFIGURATION.md)
