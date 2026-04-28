# Automated Rollback Procedures

## Overview

TraceRTM includes a comprehensive automated rollback system designed to detect and recover from deployment issues in under 2 minutes. The system monitors health metrics continuously and can trigger automatic rollbacks when critical thresholds are exceeded.

## Architecture

### Components

1. **Rollback Orchestrator** (`scripts/rollback/rollback.sh`)
   - Main coordinator for all rollback operations
   - Manages component-specific rollback scripts
   - Tracks rollback state and timing
   - Provides unified interface for manual and automatic rollbacks

2. **Component Rollback Scripts**
   - `rollback-frontend.sh` - Frontend deployment rollback
   - `rollback-backend.sh` - Go and Python backend rollback
   - `rollback-database.sh` - Database schema and data rollback

3. **Health Monitor Daemon** (`health-monitor.sh`)
   - Continuous health monitoring
   - Automatic rollback triggering
   - Cooldown period management
   - Notification integration

4. **Prometheus Alert Rules** (`monitoring/alerts.yml`)
   - Automated rollback triggers
   - Health metric thresholds
   - Cascading failure detection

## Rollback Triggers

### Automatic Triggers

The system automatically triggers rollbacks when:

1. **Error Rate** > 5% for 2 minutes
2. **Latency** > 2x baseline for 2 minutes
3. **Critical Service** down for 1 minute
4. **Database** unavailable for 1 minute
5. **Multiple Critical Alerts** (>3) firing simultaneously

### Manual Triggers

You can manually trigger rollbacks:

```bash
# Rollback all components
./scripts/rollback/rollback.sh rollback all

# Rollback specific component
./scripts/rollback/rollback.sh rollback frontend
./scripts/rollback/rollback.sh rollback backend
./scripts/rollback/rollback.sh rollback database
```

## Usage

### Before Deployment

Create deployment snapshots before any deployment:

```bash
# Create snapshots for all components
VERSION="v1.2.3"

./scripts/rollback/rollback.sh snapshot frontend $VERSION
./scripts/rollback/rollback.sh snapshot backend $VERSION
./scripts/rollback/rollback.sh snapshot database $VERSION
```

### Health Monitoring

Start the health monitor daemon:

```bash
# Start monitoring
./scripts/rollback/health-monitor.sh start

# Check status
./scripts/rollback/health-monitor.sh status

# Stop monitoring
./scripts/rollback/health-monitor.sh stop

# Run one-time health check
./scripts/rollback/health-monitor.sh check
```

### Manual Rollback

Trigger rollback manually:

```bash
# Check if rollback is needed
./scripts/rollback/rollback.sh check

# Perform rollback
./scripts/rollback/rollback.sh rollback all

# Check rollback status
./scripts/rollback/rollback.sh status
```

### Automatic Rollback

Enable automatic rollback mode:

```bash
# Run in automatic mode
./scripts/rollback/rollback.sh auto

# Or use the health monitor daemon
./scripts/rollback/health-monitor.sh start
```

## Rollback Process

### Frontend Rollback

1. Stop frontend service
2. Backup current deployment
3. Extract stable version from snapshot
4. Restart frontend service
5. Verify health (wait up to 60 seconds)

**Target Time:** <30 seconds

### Backend Rollback

1. Stop Go backend
2. Stop Python backend
3. Restore binary/code from snapshot
4. Reinstall Python dependencies if needed
5. Restart both backends
6. Verify health endpoints

**Target Time:** <60 seconds

### Database Rollback

1. Create pre-rollback backup
2. Attempt migration-based rollback (faster)
3. If migration fails, restore from snapshot
4. Terminate active connections
5. Drop and recreate database
6. Restore from backup
7. Verify critical tables exist

**Target Time:** <45 seconds

### Total Rollback Time

**Target:** <2 minutes from detection to completion

**Typical Timeline:**
- Detection: 0-30s (depending on alert evaluation interval)
- Decision: <5s
- Frontend rollback: 20-30s
- Backend rollback: 40-60s
- Database rollback: 30-45s
- Verification: 10-20s

**Total:** 100-190 seconds

## Health Checks

### Service Health

- **Go Backend**: `http://localhost:8080/health`
- **Python Backend**: `http://localhost:8000/health`
- **PostgreSQL**: `pg_isready -h localhost -p 5432`
- **Redis**: `redis-cli -h localhost ping`
- **NATS**: `http://localhost:8222/healthz`

### Metrics Monitoring

- **Error Rate**: `rate(http_requests_total{status=~"5.."}[5m])`
- **Latency P95**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Memory Usage**: System memory percentage
- **Disk Usage**: Filesystem capacity

## Deployment Integration

### Pre-Deployment Checklist

1. Create snapshots of current stable version
2. Verify snapshots are created successfully
3. Ensure health monitor is running
4. Check current system health
5. Note baseline metrics (error rate, latency)

### Post-Deployment Monitoring

1. Monitor error rates for 5 minutes
2. Monitor latency compared to baseline
3. Check service health endpoints
4. Verify critical functionality
5. Watch for Prometheus alerts

### Rollback Decision Matrix

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Error Rate | >5% for 2min | Auto rollback |
| Latency | >2x baseline for 2min | Auto rollback |
| Service Down | >1 minute | Auto rollback |
| Database Down | >1 minute | Auto rollback |
| Multiple Critical Alerts | >3 alerts | Auto rollback |
| Manual Override | Any time | Manual rollback |

## Testing

Run rollback tests in staging:

```bash
# Run all tests
./scripts/rollback/test-rollback-staging.sh all

# Run specific tests
./scripts/rollback/test-rollback-staging.sh snapshot
./scripts/rollback/test-rollback-staging.sh health
./scripts/rollback/test-rollback-staging.sh timing
./scripts/rollback/test-rollback-staging.sh monitor

# Allow actual rollbacks in staging
ALLOW_ACTUAL_ROLLBACK=true ./scripts/rollback/test-rollback-staging.sh timing
```

## Monitoring & Alerts

### Prometheus Alerts

Rollback-specific alerts in `monitoring/alerts.yml`:

- `RollbackTrigger_ErrorRate` - Error rate threshold exceeded
- `RollbackTrigger_Latency` - Latency threshold exceeded
- `RollbackTrigger_ServiceDown` - Critical service failure
- `RollbackTrigger_DatabaseFailure` - Database unavailable
- `RollbackTrigger_CascadingFailures` - Multiple critical alerts
- `RollbackInProgress` - Rollback is running
- `RollbackFailed` - Rollback failed (critical)
- `RollbackTooSlow` - Rollback exceeding 2-minute target

### Grafana Dashboards

Monitor rollback metrics:

- Rollback frequency (per day/week)
- Rollback duration trends
- Rollback success rate
- Trigger reasons distribution
- Component rollback breakdown

## State Files

### Rollback State

Location: `.rollback-logs/rollback-state.json`

```json
{
    "rollback_start": "2024-02-01T12:34:56Z",
    "trigger_reason": "error_rate_threshold_exceeded",
    "status": "completed",
    "duration_seconds": 85,
    "components": {
        "frontend": "success",
        "backend": "success",
        "database": "success"
    }
}
```

### Deployment Snapshots

Location: `.deployments/snapshots/{component}/{version}`

- Frontend: `{version}.tar.gz`
- Backend: `go-{version}` (binary), `python-{version}.tar.gz`
- Database: `{version}.sql[.gz]`

### Stable Version Markers

Location: `.deployments/{component}-stable-version.txt`

Contains the version identifier for the last known stable deployment.

## Troubleshooting

### Rollback Failed

1. Check rollback logs: `.rollback-logs/rollback.log`
2. Check component-specific logs
3. Verify snapshot files exist
4. Check disk space
5. Verify service permissions

### Rollback Too Slow

1. Check disk I/O performance
2. Verify network latency
3. Optimize snapshot sizes
4. Consider incremental rollbacks
5. Review database backup size

### Health Monitor Not Starting

1. Check if already running: `health-monitor.sh status`
2. Verify Prometheus is accessible
3. Check log file: `.rollback-logs/health-monitor.log`
4. Ensure jq is installed
5. Verify file permissions

### False Positive Triggers

1. Adjust threshold values in `health-monitor.sh`
2. Increase evaluation periods in Prometheus alerts
3. Add cooldown period between rollbacks
4. Review baseline calculation methods

## Best Practices

### Snapshot Management

- Create snapshots before every deployment
- Keep at least 3 stable versions
- Compress large snapshots
- Test snapshot restoration regularly
- Clean up old snapshots (>30 days)

### Monitoring Configuration

- Set appropriate thresholds for your traffic patterns
- Monitor rollback frequency
- Review false positive/negative rates
- Adjust cooldown periods based on deployment frequency

### Testing

- Test rollback procedures weekly in staging
- Measure and track rollback times
- Verify all components can be rolled back independently
- Practice manual rollback procedures

### Documentation

- Document version-specific rollback considerations
- Maintain runbooks for common rollback scenarios
- Update contact information for on-call escalation
- Keep rollback procedures up-to-date

## Production Deployment

### Systemd Service (Linux)

Install the health monitor as a systemd service:

```bash
# Copy service file
sudo cp scripts/rollback/rollback-health-monitor.service \
    /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable rollback-health-monitor
sudo systemctl start rollback-health-monitor

# Check status
sudo systemctl status rollback-health-monitor

# View logs
sudo journalctl -u rollback-health-monitor -f
```

### Process Compose Integration

Add to `process-compose.yaml`:

```yaml
health-monitor:
  command: "bash scripts/rollback/health-monitor.sh start"
  working_dir: "."
  availability:
    restart: always
  environment:
    - "CHECK_INTERVAL=30"
```

## Security Considerations

- Limit access to rollback scripts (production)
- Audit rollback operations
- Encrypt snapshot backups
- Secure database credentials
- Implement approval workflows for manual rollbacks

## Metrics & SLOs

### Rollback SLOs

- **Rollback Time**: <2 minutes (P95)
- **Rollback Success Rate**: >99%
- **Detection Time**: <1 minute
- **False Positive Rate**: <5%

### Key Metrics

- `tracertm_rollback_duration_seconds` - Time to complete rollback
- `tracertm_rollback_total` - Total rollbacks (by reason, status)
- `tracertm_rollback_in_progress` - Active rollback indicator
- `tracertm_rollback_success_rate` - Success rate over time

## Support

For issues or questions:

1. Check logs in `.rollback-logs/`
2. Review Prometheus alerts
3. Consult runbooks in wiki
4. Escalate to on-call team
5. Create incident report

## References

- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Monitoring Setup](../../monitoring/README.md)
- [Prometheus Alerts](../../monitoring/alerts.yml)
- [Health Check API](../api/health-checks.md)
