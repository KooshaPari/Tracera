# Automated Rollback Scripts

This directory contains the automated rollback system for TraceRTM.

## Quick Start

### Emergency Rollback

```bash
# Rollback everything immediately
./rollback.sh rollback all
```

### Before Every Deployment

```bash
# Create snapshots of current stable version
VERSION="v1.2.3"
./rollback.sh snapshot frontend $VERSION
./rollback.sh snapshot backend $VERSION
./rollback.sh snapshot database $VERSION
```

### Start Health Monitoring

```bash
# Start the health monitor daemon
./health-monitor.sh start

# Check status
./health-monitor.sh status
```

## Files

- **rollback.sh** - Main orchestrator for rollback operations
- **rollback-frontend.sh** - Frontend-specific rollback logic
- **rollback-backend.sh** - Backend (Go + Python) rollback logic
- **rollback-database.sh** - Database rollback logic
- **health-monitor.sh** - Health monitoring daemon
- **test-rollback-staging.sh** - Test suite for staging validation
- **rollback-health-monitor.service** - Systemd service configuration

## Documentation

- [Complete Procedures](../../docs/guides/ROLLBACK_PROCEDURES.md)
- [Quick Reference](../../docs/reference/ROLLBACK_QUICK_REFERENCE.md)
- [Completion Report](../../docs/reports/TASK_110_AUTOMATED_ROLLBACK_COMPLETION.md)

## Rollback Triggers

The system automatically triggers rollbacks when:

1. **Error Rate** >5% for 2 minutes
2. **Latency** >2x baseline for 2 minutes
3. **Critical Service** down for 1 minute
4. **Database** unavailable for 1 minute
5. **Multiple Critical Alerts** (>3) firing

## Target Performance

- **Total Rollback Time:** <2 minutes
- **Detection Time:** <30 seconds
- **Frontend Rollback:** <30 seconds
- **Backend Rollback:** <60 seconds
- **Database Rollback:** <45 seconds

## Testing

Run the test suite in staging:

```bash
# Run all tests
./test-rollback-staging.sh all

# Run specific tests
./test-rollback-staging.sh timing
./test-rollback-staging.sh health
./test-rollback-staging.sh monitor
```

## Production Deployment

Install as systemd service:

```bash
sudo cp rollback-health-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rollback-health-monitor
sudo systemctl start rollback-health-monitor
```

## Support

For questions or issues, see the [troubleshooting guide](../../docs/guides/ROLLBACK_PROCEDURES.md#troubleshooting).
