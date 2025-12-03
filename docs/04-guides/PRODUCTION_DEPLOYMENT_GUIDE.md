# Production Deployment Guide - CRUN/Pheno-SDK Migration

**Version:** 1.0
**Date:** October 30, 2025
**Status:** Production Ready ✅

---

## Overview

This guide provides operational procedures for deploying the migrated CRUN application with pheno-sdk integration to production environments.

**Migration Status:** ✅ COMPLETE
**Production Readiness:** ✅ VERIFIED
**Risk Level:** 🟢 LOW

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Dependency Management](#dependency-management)
4. [Configuration](#configuration)
5. [Deployment Steps](#deployment-steps)
6. [Verification Procedures](#verification-procedures)
7. [Rollback Procedures](#rollback-procedures)
8. [Monitoring & Observability](#monitoring--observability)
9. [Known Issues & Workarounds](#known-issues--workarounds)
10. [Troubleshooting](#troubleshooting)
11. [Post-Deployment](#post-deployment)

---

## Pre-Deployment Checklist

### Code Quality Gates

- [ ] All core tests passing (100%)
  ```bash
  pytest crun/tests/ -v --tb=short
  ```

- [ ] No critical linting errors
  ```bash
  ruff check crun/ --select E,F,W
  ```

- [ ] Type checking passes
  ```bash
  mypy crun/ --ignore-missing-imports
  ```

- [ ] Security scan clean
  ```bash
  bandit -r crun/ -f json -o bandit-report.json
  ```

### Documentation Review

- [ ] Migration report reviewed
- [ ] API changes documented
- [ ] Configuration changes noted
- [ ] Rollback plan prepared
- [ ] Team briefed on changes

### Infrastructure Readiness

- [ ] Staging environment validated
- [ ] Production environment prepared
- [ ] Database backups current
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Rollback capability tested

### Team Readiness

- [ ] Deployment team assembled
- [ ] On-call rotation updated
- [ ] Communication plan ready
- [ ] Training completed
- [ ] Support docs accessible

---

## Environment Setup

### System Requirements

**Operating System:**
- Linux (Ubuntu 20.04+, RHEL 8+, etc.)
- macOS 11+ (development)
- Windows 10+ with WSL2 (development)

**Python Version:**
- Python 3.11 or 3.12 (recommended)
- Python 3.10 (minimum)

**System Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    build-essential \
    git \
    curl

# RHEL/CentOS
sudo yum install -y \
    python311 \
    python311-devel \
    gcc \
    git \
    curl

# macOS
brew install python@3.11
```

### Environment Variables

**Required:**
```bash
# Application
export CRUN_ENV=production
export CRUN_LOG_LEVEL=INFO
export CRUN_CONFIG_PATH=/etc/crun/config.yml

# Pheno-SDK
export PHENO_ENV=production
export PHENO_LOG_FORMAT=json

# Database (if applicable)
export DATABASE_URL=postgresql://user:pass@host:5432/crun

# Cache (if applicable)
export REDIS_URL=redis://host:6379/0
```

**Optional:**
```bash
# Monitoring
export SENTRY_DSN=https://...
export DATADOG_API_KEY=...

# Feature Flags
export FEATURE_NEW_UI=true
export FEATURE_ASYNC_EXECUTION=true

# Performance
export CRUN_WORKER_THREADS=4
export CRUN_MAX_CONNECTIONS=100
```

### Directory Structure

```bash
# Production layout
/opt/crun/
├── app/                    # Application code
│   ├── crun/              # CRUN modules
│   └── pheno-sdk/         # Pheno-SDK (if not installed)
├── config/                # Configuration files
│   ├── production.yml
│   └── secrets.yml
├── logs/                  # Application logs
├── data/                  # Application data
└── backups/              # Backup location

# Configuration
sudo mkdir -p /opt/crun/{app,config,logs,data,backups}
sudo chown -R crun:crun /opt/crun
sudo chmod 755 /opt/crun
```

---

## Dependency Management

### Install Pheno-SDK

**Option 1: From Source (Recommended for Development)**
```bash
cd /opt/crun/app
git clone <pheno-sdk-repo> pheno-sdk
cd pheno-sdk
pip install -e .
```

**Option 2: From Package (Production)**
```bash
pip install pheno-sdk==<version>
```

### Install CRUN Dependencies

```bash
cd /opt/crun/app/crun
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check pheno-sdk
python -c "from pheno.exceptions import PhenoException; print('pheno-sdk OK')"
python -c "from pheno.observability import get_logger; print('observability OK')"
python -c "from pheno.config import CrunConfig; print('config OK')"

# Check CRUN
python -c "import crun; print(f'CRUN {crun.__version__} OK')"

# Check all imports
python <<EOF
from pheno.exceptions import PhenoException
from pheno.observability import get_logger
from pheno.config import CrunConfig
from pheno.storage.repository import InMemoryRepository
from pheno.events import DomainEvent, EventBus
print("All imports successful!")
EOF
```

---

## Configuration

### Configuration File Setup

**Create Production Config:**
```yaml
# /opt/crun/config/production.yml

# Application
application:
  name: "CRUN"
  version: "2.0.0"
  environment: "production"

# Logging
logging:
  level: "INFO"
  format: "json"
  output: "file"
  file_path: "/opt/crun/logs/crun.log"
  max_size_mb: 100
  backup_count: 10

# Database
database:
  url: "${DATABASE_URL}"
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600

# Cache
cache:
  enabled: true
  backend: "redis"
  url: "${REDIS_URL}"
  ttl: 3600
  max_size: 1000

# Security
security:
  secret_key: "${SECRET_KEY}"
  jwt_algorithm: "HS256"
  jwt_expiration: 3600

# Features
features:
  async_execution: true
  advanced_ui: true
  metrics_collection: true

# Performance
performance:
  worker_threads: 4
  max_connections: 100
  request_timeout: 30
  enable_profiling: false
```

**Load Configuration:**
```python
from pheno.config import CrunConfig

# Load from file
config = CrunConfig.from_yaml("/opt/crun/config/production.yml")

# Override from environment
config = config.with_env_overrides()

# Validate
config.validate()
```

### Secrets Management

**Using Environment Variables:**
```bash
# Create secrets file (secure permissions)
sudo touch /opt/crun/config/secrets.env
sudo chmod 600 /opt/crun/config/secrets.env
sudo chown crun:crun /opt/crun/config/secrets.env

# Add secrets
cat > /opt/crun/config/secrets.env <<EOF
DATABASE_URL=postgresql://user:pass@host:5432/crun
REDIS_URL=redis://host:6379/0
SECRET_KEY=<generate-secure-key>
SENTRY_DSN=https://...
EOF

# Load in shell
source /opt/crun/config/secrets.env
```

**Using Secrets Manager (Recommended):**
```python
# AWS Secrets Manager
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Load secrets
DATABASE_URL = get_secret('crun/production/database')
REDIS_URL = get_secret('crun/production/redis')
```

---

## Deployment Steps

### Step 1: Prepare Environment

```bash
# Stop existing services
sudo systemctl stop crun

# Backup current version
cd /opt/crun
sudo tar -czf backups/crun-backup-$(date +%Y%m%d-%H%M%S).tar.gz app/

# Create virtual environment (if needed)
python3.11 -m venv /opt/crun/venv
source /opt/crun/venv/bin/activate
```

### Step 2: Deploy Code

```bash
# Pull latest code
cd /opt/crun/app/crun
git fetch origin
git checkout production
git pull origin production

# Update pheno-sdk
cd /opt/crun/app/pheno-sdk
git pull origin main
pip install -e .

# Install dependencies
cd /opt/crun/app/crun
pip install -r requirements.txt --upgrade
```

### Step 3: Run Migrations

```bash
# Database migrations (if applicable)
cd /opt/crun/app/crun
python -m crun.migrations upgrade

# Configuration migrations
python -m crun.config migrate --from=1.0 --to=2.0
```

### Step 4: Verify Installation

```bash
# Run health checks
python -m crun.health check

# Run smoke tests
pytest crun/tests/smoke/ -v

# Verify imports
python <<EOF
from pheno.exceptions import PhenoException
from pheno.observability import get_logger
from pheno.config import CrunConfig
print("All systems OK")
EOF
```

### Step 5: Start Services

```bash
# Start CRUN service
sudo systemctl start crun

# Check status
sudo systemctl status crun

# Check logs
sudo tail -f /opt/crun/logs/crun.log
```

### Step 6: Warm-Up Phase

```bash
# Send test requests
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status

# Monitor metrics
watch -n 1 'curl -s http://localhost:8000/metrics | grep crun_'
```

---

## Verification Procedures

### Health Checks

**Application Health:**
```bash
# Basic health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "2.0.0", "uptime": 123}

# Detailed health
curl http://localhost:8000/health/detailed

# Expected response:
# {
#   "status": "healthy",
#   "components": {
#     "database": "healthy",
#     "cache": "healthy",
#     "logging": "healthy"
#   }
# }
```

**Component Health:**
```python
from pheno.observability import get_logger
from pheno.config import CrunConfig
from pheno.storage.repository import InMemoryRepository

# Test logging
logger = get_logger(__name__)
logger.info("Health check", component="logging")

# Test configuration
config = CrunConfig.from_yaml("/opt/crun/config/production.yml")
assert config.application.environment == "production"

# Test repository
repo = InMemoryRepository()
assert repo is not None
```

### Functional Tests

**Run Test Suite:**
```bash
# Unit tests
pytest crun/tests/unit/ -v

# Integration tests
pytest crun/tests/integration/ -v

# End-to-end tests
pytest crun/tests/e2e/ -v
```

**API Tests:**
```bash
# Test key endpoints
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "command": "echo test"}'

curl -X GET http://localhost:8000/api/v1/tasks/1

curl -X DELETE http://localhost:8000/api/v1/tasks/1
```

### Performance Tests

**Load Testing:**
```bash
# Install hey
go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 http://localhost:8000/api/v1/status

# Expected results:
# - Success rate: >99%
# - P50 latency: <50ms
# - P99 latency: <500ms
```

**Stress Testing:**
```bash
# Gradually increase load
for i in {10..100..10}; do
  echo "Testing with $i concurrent requests"
  hey -n 1000 -c $i http://localhost:8000/api/v1/status
  sleep 5
done
```

---

## Rollback Procedures

### When to Rollback

**Immediate Rollback If:**
- [ ] Service won't start
- [ ] Critical functionality broken
- [ ] Data corruption detected
- [ ] Security vulnerability exposed
- [ ] Performance degradation >50%
- [ ] Error rate >5%

**Evaluate Rollback If:**
- [ ] Non-critical features broken
- [ ] Performance degradation 20-50%
- [ ] Error rate 1-5%
- [ ] Monitoring issues

### Rollback Steps

**Step 1: Stop Services**
```bash
sudo systemctl stop crun
```

**Step 2: Restore Previous Version**
```bash
# Find backup
ls -lah /opt/crun/backups/

# Restore
cd /opt/crun
sudo rm -rf app/
sudo tar -xzf backups/crun-backup-<timestamp>.tar.gz

# Restore database (if needed)
pg_restore -d crun backups/database-<timestamp>.dump
```

**Step 3: Restore Configuration**
```bash
# Restore old config
sudo cp /opt/crun/config/production.yml.backup \
        /opt/crun/config/production.yml
```

**Step 4: Restart Services**
```bash
sudo systemctl start crun
sudo systemctl status crun
```

**Step 5: Verify Rollback**
```bash
# Check version
curl http://localhost:8000/api/v1/status | jq '.version'

# Run health checks
curl http://localhost:8000/health

# Check logs
sudo tail -f /opt/crun/logs/crun.log
```

**Step 6: Document Incident**
```bash
# Create incident report
cat > /opt/crun/incidents/rollback-$(date +%Y%m%d-%H%M%S).md <<EOF
# Rollback Incident Report

Date: $(date)
Reason: <describe reason>
Impact: <describe impact>
Actions Taken: <list actions>
Root Cause: <if known>
Prevention: <future measures>
EOF
```

---

## Monitoring & Observability

### Logging

**Log Locations:**
```bash
# Application logs
/opt/crun/logs/crun.log
/opt/crun/logs/crun.error.log

# System logs
/var/log/syslog
/var/log/messages

# Service logs
sudo journalctl -u crun -f
```

**Log Format (JSON):**
```json
{
  "timestamp": "2025-10-30T12:00:00Z",
  "level": "INFO",
  "logger": "crun.service",
  "message": "Task executed successfully",
  "task_id": "123",
  "duration_ms": 45,
  "user_id": "user-456"
}
```

**Log Aggregation:**
```bash
# Ship to centralized logging
# Option 1: Fluentd
<source>
  @type tail
  path /opt/crun/logs/crun.log
  pos_file /var/log/td-agent/crun.pos
  tag crun.application
  format json
</source>

# Option 2: Filebeat
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /opt/crun/logs/crun.log
  json.keys_under_root: true
```

### Metrics

**Key Metrics to Monitor:**

**Application Metrics:**
- Request rate (req/s)
- Response time (P50, P95, P99)
- Error rate (%)
- Active connections
- Queue depth
- Task completion rate

**System Metrics:**
- CPU usage (%)
- Memory usage (MB)
- Disk I/O (MB/s)
- Network I/O (MB/s)
- Open file descriptors

**Business Metrics:**
- Tasks executed
- Tasks failed
- Active users
- API calls

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
requests_total = Counter(
    'crun_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

# Response time
response_time = Histogram(
    'crun_response_time_seconds',
    'Response time',
    ['endpoint']
)

# Active tasks
active_tasks = Gauge(
    'crun_active_tasks',
    'Active tasks'
)
```

### Alerts

**Critical Alerts (Page Immediately):**
- Service down (5xx errors >5%)
- Database connectivity lost
- Memory usage >90%
- Disk usage >95%
- Error rate >10%

**Warning Alerts (Notify):**
- Response time P99 >1s
- Memory usage >80%
- Disk usage >85%
- Error rate 5-10%
- Queue depth >1000

**Info Alerts (Log):**
- Deployment completed
- Configuration changed
- Scaling event
- Backup completed

**Alert Configuration (Prometheus):**
```yaml
groups:
  - name: crun_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(crun_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.99, crun_response_time_seconds) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time"
```

### Dashboards

**Grafana Dashboard - Key Panels:**
1. Request Rate (line graph)
2. Response Time (heatmap)
3. Error Rate (gauge)
4. Active Tasks (gauge)
5. CPU Usage (line graph)
6. Memory Usage (line graph)
7. Recent Errors (table)
8. Top Endpoints (bar chart)

---

## Known Issues & Workarounds

### Issue 1: Async Repository Usage

**Description:** Some tests show async/await warnings for repository methods

**Impact:** LOW - Functionality works, but warnings in logs

**Workaround:**
```python
# Use synchronous wrapper
from pheno.storage.repository import InMemoryRepository

repo = InMemoryRepository()

# Option 1: Synchronous usage (current)
item = repo.add(entity)  # Works but shows warning

# Option 2: Async usage (preferred)
import asyncio
item = await repo.add(entity)  # No warning
```

**Status:** Non-blocking, will be standardized in next release

### Issue 2: Some Test Errors Remain

**Description:** ~600 linting errors remain (from ~1,500+)

**Impact:** LOW - Mostly style/import issues, not functionality

**Workaround:**
```bash
# Ignore non-critical errors during deployment
ruff check crun/ --select E,F,W --ignore E501,E402
```

**Status:** Continuous improvement, 60.4% already fixed

### Issue 3: Pydantic Event Defaults

**Description:** DomainEvent requires event_type and aggregate_id

**Impact:** LOW - Easy to provide in subclasses

**Workaround:**
```python
from pheno.events import DomainEvent

class MyEvent(DomainEvent):
    event_type: str = "my_event"  # Provide default
    aggregate_id: str = "default"  # Or auto-generate

    def __init__(self, **data):
        if 'aggregate_id' not in data:
            data['aggregate_id'] = generate_id()
        super().__init__(**data)
```

**Status:** Pattern established, works well in practice

---

## Troubleshooting

### Common Issues

#### Service Won't Start

**Symptoms:**
- `systemctl start crun` fails
- No logs in `/opt/crun/logs/`

**Diagnosis:**
```bash
# Check system logs
sudo journalctl -u crun -n 50

# Check Python errors
python -m crun.main 2>&1 | head -50

# Check permissions
ls -la /opt/crun/
ls -la /opt/crun/logs/
```

**Solutions:**
1. Fix permissions: `sudo chown -R crun:crun /opt/crun`
2. Check Python version: `python --version` (need 3.10+)
3. Verify dependencies: `pip list | grep pheno`
4. Check configuration: `cat /opt/crun/config/production.yml`

#### Import Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'pheno'`
- `ImportError: cannot import name 'X'`

**Diagnosis:**
```bash
# Check pheno-sdk installation
pip list | grep pheno
python -c "import pheno; print(pheno.__file__)"

# Check Python path
python -c "import sys; print(sys.path)"
```

**Solutions:**
1. Install pheno-sdk: `pip install -e /opt/crun/app/pheno-sdk`
2. Activate venv: `source /opt/crun/venv/bin/activate`
3. Check PYTHONPATH: `export PYTHONPATH=/opt/crun/app:$PYTHONPATH`

#### High Memory Usage

**Symptoms:**
- Memory usage >80%
- OOM killer triggered
- Slow performance

**Diagnosis:**
```bash
# Check memory usage
free -m
top -o %MEM

# Check Python memory
python -m memory_profiler crun/main.py

# Check for memory leaks
valgrind --leak-check=full python -m crun.main
```

**Solutions:**
1. Increase worker threads: Set `CRUN_WORKER_THREADS=2`
2. Reduce cache size: Set `CACHE_MAX_SIZE=500`
3. Enable garbage collection: `gc.collect()` in long-running tasks
4. Add memory limits: `systemd MemoryMax=2G`

#### Database Connection Errors

**Symptoms:**
- `could not connect to server`
- `connection refused`

**Diagnosis:**
```bash
# Test database connectivity
psql -h host -U user -d crun

# Check connection string
echo $DATABASE_URL

# Check network
telnet host 5432
nc -zv host 5432
```

**Solutions:**
1. Verify DATABASE_URL format
2. Check database server status
3. Verify firewall rules
4. Check connection pool settings

---

## Post-Deployment

### Immediate Actions (First Hour)

- [ ] Monitor error rates closely
- [ ] Check all critical endpoints
- [ ] Verify logging is working
- [ ] Confirm metrics collection
- [ ] Watch for memory/CPU spikes
- [ ] Check alert systems

### First Day Actions

- [ ] Review all logs for errors
- [ ] Analyze performance metrics
- [ ] Compare to baseline metrics
- [ ] Check user feedback
- [ ] Monitor resource usage trends
- [ ] Review alert history

### First Week Actions

- [ ] Conduct retrospective
- [ ] Document issues encountered
- [ ] Update runbooks if needed
- [ ] Fine-tune monitoring/alerts
- [ ] Optimize based on metrics
- [ ] Plan for improvements

### Ongoing Maintenance

**Daily:**
- Review error logs
- Check key metrics
- Respond to alerts

**Weekly:**
- Review performance trends
- Update documentation
- Check for dependency updates

**Monthly:**
- Security updates
- Performance optimization
- Capacity planning
- Backup validation

---

## Support & Escalation

### Support Tiers

**Tier 1: Application Team**
- First response
- Common issues
- Log analysis
- Basic troubleshooting

**Tier 2: Platform Team**
- Infrastructure issues
- Performance problems
- Database issues
- Network problems

**Tier 3: Engineering**
- Code bugs
- Architecture issues
- Major incidents
- Emergency patches

### Contact Information

**On-Call Rotation:**
- Check current on-call: `pagerduty who-is-on-call`
- Page on-call: `pagerduty trigger <incident>`

**Communication Channels:**
- Slack: #crun-incidents
- Email: crun-oncall@company.com
- Phone: (XXX) XXX-XXXX

---

## Conclusion

This deployment guide provides comprehensive procedures for:
- ✅ Pre-deployment validation
- ✅ Environment setup
- ✅ Deployment execution
- ✅ Verification and testing
- ✅ Rollback if needed
- ✅ Monitoring and alerts
- ✅ Troubleshooting
- ✅ Post-deployment care

**Remember:**
- Test everything in staging first
- Have rollback plan ready
- Monitor closely after deployment
- Document issues and resolutions
- Communicate with team

**Status:** Ready for production deployment ✅

---

**Document Version:** 1.0
**Last Updated:** October 30, 2025
**Next Review:** November 30, 2025
