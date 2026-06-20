# Rollback Quick Reference

## Emergency Rollback (Production)

```bash
# Immediate rollback of all components
cd /opt/tracertm
./scripts/rollback/rollback.sh rollback all

# Check status
./scripts/rollback/rollback.sh status
```

## Common Commands

### Health Monitoring

```bash
# Start health monitor
./scripts/rollback/health-monitor.sh start

# Stop health monitor
./scripts/rollback/health-monitor.sh stop

# Check health monitor status
./scripts/rollback/health-monitor.sh status

# Run one-time health check
./scripts/rollback/health-monitor.sh check
```

### Rollback Operations

```bash
# Check if rollback is needed
./scripts/rollback/rollback.sh check

# Rollback all components
./scripts/rollback/rollback.sh rollback all

# Rollback specific component
./scripts/rollback/rollback.sh rollback frontend
./scripts/rollback/rollback.sh rollback backend
./scripts/rollback/rollback.sh rollback database

# Auto mode (check and rollback if needed)
./scripts/rollback/rollback.sh auto
```

### Snapshot Management

```bash
# Create deployment snapshot
./scripts/rollback/rollback.sh snapshot <component> <version>

# Examples
./scripts/rollback/rollback.sh snapshot frontend v1.2.3
./scripts/rollback/rollback.sh snapshot backend v1.2.3
./scripts/rollback/rollback.sh snapshot database v1.2.3
```

### Status & Logs

```bash
# View rollback status
./scripts/rollback/rollback.sh status

# View rollback logs
tail -f .rollback-logs/rollback.log

# View health monitor logs
tail -f .rollback-logs/health-monitor.log
```

## Automatic Rollback Triggers

| Trigger | Threshold | Duration |
|---------|-----------|----------|
| Error Rate | >5% | 2 minutes |
| Latency | >2x baseline | 2 minutes |
| Service Down | Any | 1 minute |
| Database Down | Any | 1 minute |
| Multiple Alerts | >3 critical | 1 minute |

## Target Timings

| Operation | Target Time |
|-----------|-------------|
| Detection | <30 seconds |
| Frontend Rollback | <30 seconds |
| Backend Rollback | <60 seconds |
| Database Rollback | <45 seconds |
| **Total Rollback** | **<2 minutes** |

## Health Check Endpoints

```bash
# Go Backend
curl http://localhost:8080/health

# Python Backend
curl http://localhost:8000/health

# PostgreSQL
pg_isready -h localhost -p 5432 -U tracertm

# Redis
redis-cli -h localhost -p 6379 ping

# NATS
curl http://localhost:8222/healthz
```

## Prometheus Queries

```promql
# Error rate (5-minute window)
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Service up/down
up{job=~"go-backend|python-backend"}

# Rollback in progress
tracertm_rollback_in_progress

# Rollback duration
tracertm_rollback_duration_seconds
```

## File Locations

```
scripts/rollback/
├── rollback.sh                 # Main orchestrator
├── rollback-frontend.sh        # Frontend rollback
├── rollback-backend.sh         # Backend rollback
├── rollback-database.sh        # Database rollback
├── health-monitor.sh           # Health monitoring daemon
└── test-rollback-staging.sh    # Test suite

.deployments/
├── snapshots/
│   ├── frontend/              # Frontend snapshots
│   ├── backend/               # Backend snapshots
│   └── database/              # Database snapshots
├── backups/                   # Pre-rollback backups
├── frontend-stable-version.txt
├── backend-stable-version.txt
└── database-stable-version.txt

.rollback-logs/
├── rollback.log               # Rollback operations log
├── health-monitor.log         # Health monitor log
├── rollback-state.json        # Current rollback state
└── last-rollback-time         # Cooldown tracking

monitoring/
└── alerts.yml                 # Prometheus alerts (includes rollback triggers)
```

## Environment Variables

```bash
# Health monitor check interval (seconds)
export CHECK_INTERVAL=30

# Rollback reason (set by monitor)
export ROLLBACK_REASON="error_rate_threshold_exceeded"

# Database connection
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=tracertm
export DB_PASSWORD=tracertm_password
export DB_NAME=tracertm

# Allow actual rollbacks in staging tests
export ALLOW_ACTUAL_ROLLBACK=true
```

## Troubleshooting

### Rollback Failed

```bash
# Check logs
cat .rollback-logs/rollback.log | tail -100

# Check rollback state
cat .rollback-logs/rollback-state.json | jq

# Verify snapshots exist
ls -lah .deployments/snapshots/*/

# Check disk space
df -h

# Manual component restart
process-compose restart frontend
process-compose restart go-backend
process-compose restart python-backend
```

### Health Monitor Not Working

```bash
# Check if running
ps aux | grep health-monitor

# Check logs
tail -100 .rollback-logs/health-monitor.log

# Check Prometheus connectivity
curl http://localhost:9090/-/healthy

# Restart monitor
./scripts/rollback/health-monitor.sh stop
./scripts/rollback/health-monitor.sh start
```

### Snapshot Issues

```bash
# List snapshots
find .deployments/snapshots -type f -ls

# Verify snapshot integrity
tar -tzf .deployments/snapshots/frontend/v1.2.3.tar.gz

# Manually create snapshot
./scripts/rollback/rollback.sh snapshot frontend $(date +%Y%m%d%H%M%S)

# Clean old snapshots (>30 days)
find .deployments/snapshots -type f -mtime +30 -delete
```

## Testing in Staging

```bash
# Run all tests
./scripts/rollback/test-rollback-staging.sh all

# Run specific test
./scripts/rollback/test-rollback-staging.sh timing

# Enable actual rollbacks in staging
export ENVIRONMENT=staging
export ALLOW_ACTUAL_ROLLBACK=true
./scripts/rollback/test-rollback-staging.sh all
```

## Production Checklist

Before deploying to production:

- [ ] Create snapshots of current version
- [ ] Verify health monitor is running
- [ ] Check baseline metrics (error rate, latency)
- [ ] Test rollback in staging
- [ ] Review Prometheus alerts
- [ ] Ensure on-call team is ready
- [ ] Document deployment-specific considerations

After deploying to production:

- [ ] Monitor error rates for 5 minutes
- [ ] Monitor latency vs baseline
- [ ] Verify critical functionality
- [ ] Watch Prometheus alerts
- [ ] Review rollback readiness
- [ ] Update stable version markers

## Emergency Contacts

```bash
# View active alerts
curl http://localhost:9090/api/v1/alerts | jq

# Check system status
./scripts/rollback/rollback.sh check

# Emergency rollback
./scripts/rollback/rollback.sh rollback all
```

## Systemd Service (Production)

```bash
# Install service
sudo cp scripts/rollback/rollback-health-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload

# Manage service
sudo systemctl start rollback-health-monitor
sudo systemctl stop rollback-health-monitor
sudo systemctl restart rollback-health-monitor
sudo systemctl status rollback-health-monitor

# View logs
sudo journalctl -u rollback-health-monitor -f
```

## Metrics to Monitor

```promql
# Rollback metrics
tracertm_rollback_total{reason="error_rate"}
tracertm_rollback_total{status="success"}
tracertm_rollback_duration_seconds

# Health metrics
up{job="go-backend"}
rate(http_requests_total{status=~"5.."}[5m])
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Quick Diagnostics

```bash
# Check all services
curl -sf http://localhost:8080/health && echo "Go backend: OK"
curl -sf http://localhost:8000/health && echo "Python backend: OK"
pg_isready -h localhost -p 5432 && echo "PostgreSQL: OK"
redis-cli ping && echo "Redis: OK"

# Check error rate
curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])" | jq

# Check latency
curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))" | jq
```
