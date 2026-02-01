# Prometheus Alerting Rules Setup

## Overview

This document describes the Prometheus alerting rules configured for TraceRTM with a Mean Time To Recovery (MTTR) target of **less than 5 minutes** for critical issues.

## Architecture

```
Application Metrics
      ↓
  Prometheus (scrapes every 15s)
      ↓
  Alert Rules (evaluated every 30s)
      ↓
  Alertmanager (routes & notifies)
      ↓
  Notification Channels:
  ├── Slack (warnings & info)
  ├── Email (critical alerts)
  └── PagerDuty (on-call management)
```

## Quick Start

### 1. Start Monitoring Stack

```bash
cd monitoring/
docker-compose up -d
```

This starts:
- **Prometheus** (port 9090) - metrics scraping & alert evaluation
- **Alertmanager** (port 9093) - alert routing & notifications
- **Node Exporter** (port 9100) - system metrics
- **PostgreSQL Exporter** (port 9187) - database metrics
- **Redis Exporter** (port 9121) - cache metrics

### 2. Configure Notification Channels

#### Slack Integration

1. Create a Slack App: https://api.slack.com/apps
2. Create an Incoming Webhook
3. Set environment variable:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
docker-compose up -d
```

#### Email Integration

Set SMTP credentials:

```bash
export SMTP_USERNAME="alerts@example.com"
export SMTP_PASSWORD="your-password"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
docker-compose up -d
```

#### PagerDuty Integration

1. Create a service in PagerDuty
2. Add an integration key
3. Set environment variable:

```bash
export PAGERDUTY_SERVICE_KEY="your-service-key"
docker-compose up -d
```

### 3. Verify Setup

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Alertmanager status
curl http://localhost:9093/api/v1/status

# View active alerts
curl http://localhost:9090/api/v1/alerts
```

## Alert Categories & SLOs

### 1. API & Service Health (MTTR: <5 minutes)

| Alert | Threshold | Duration | Severity | SLO |
|-------|-----------|----------|----------|-----|
| HighAPILatency | P95 > 1s | 2m | warning | latency |
| CriticalAPILatency | P95 > 5s | 1m | critical | latency |
| HighErrorRate | >5% errors | 2m | warning | availability |
| CriticalErrorRate | >20% errors | 1m | critical | availability |
| ServiceDown | Service unreachable | 1m | critical | availability |

**MTTR Actions:**
- Auto-scale services if CPU/memory high
- Check recent deployments
- Review error logs for patterns
- Contact on-call engineer via PagerDuty

### 2. Database Alerts (MTTR: <5 minutes)

| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| DatabaseConnectionPoolExhausted | >80% connections | 2m | warning |
| DatabaseConnectionPoolCritical | >95% connections | 1m | critical |
| HighDatabaseLatency | P95 > 1s | 3m | warning |
| DatabaseSlowQueries | Avg >500ms | 5m | warning |
| DatabaseHighLoad | Rollback rate >0.1/sec | 2m | warning |

**MTTR Actions:**
- Review active queries: `SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10`
- Check connection usage: `SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname`
- Consider connection pooling (PgBouncer)
- Scale read replicas if read-heavy

### 3. Resource Alerts (MTTR: <5 minutes)

| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| HighMemoryUsage | >1GB | 5m | warning |
| CriticalMemoryUsage | >2GB | 2m | critical |
| HighCPUUsage | >80% | 5m | warning |
| CriticalCPUUsage | >95% | 2m | critical |
| DiskSpaceLow | <10% free | 5m | warning |

**MTTR Actions:**
- Check for memory leaks: `docker stats`
- Review process logs for GC issues
- Auto-scale horizontally
- Clean up old data/logs

### 4. Cache Alerts

| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| LowCacheHitRatio | <50% | 10m | info |
| CacheUnavailable | Redis down | 1m | critical |

**MTTR Actions:**
- Restart Redis if down
- Review cache eviction policies
- Check for cache stampedes

### 5. Workflow & Agent Alerts

| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| NoActiveAgents | Active agents = 0 | 1m | critical |
| LowAgentCount | Active agents < 2 | 3m | warning |
| HighTaskErrorRate | >20% task failures | 5m | warning |
| AgentHeartbeatFailure | No heartbeats | 2m | critical |

**MTTR Actions:**
- Check agent connectivity
- Review agent logs for errors
- Restart failing agents
- Check message queue health

## Alert Rule Structure

Each alert rule has:

```yaml
- alert: AlertName              # Unique identifier
  expr: promql_expression       # Threshold query
  for: duration                 # How long condition must be true
  labels:                       # Metadata for routing
    severity: critical|warning  # Alert severity
    team: backend|infra|dba     # Responsible team
    slo: availability|latency   # Associated SLO
  annotations:                  # Alert details
    summary: "Brief description"
    description: "{{ variable }} details"
    runbook_url: "Link to runbook"
    mttr_target: "X minutes"    # Target recovery time
```

## Alert Routing

Alertmanager routes alerts based on labels:

### Critical Alerts
- **Channel:** Slack #critical-alerts + Email + PagerDuty
- **Wait Time:** 0s (immediate)
- **Repeat Interval:** 1 hour

### Warning Alerts
- **Channel:** Slack #warnings
- **Wait Time:** 30s (batch)
- **Repeat Interval:** 4 hours

### Info Alerts
- **Channel:** Slack #info
- **Wait Time:** 5 minutes
- **Repeat Interval:** 24 hours

## PromQL Expressions Explained

### Latency (P95)
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```
- Calculates 95th percentile of request duration
- `[5m]` = 5-minute time window
- Result: latency in seconds

### Error Rate
```promql
rate(http_requests_total{status=~"5.."}[5m]) > 0.05
```
- `rate()` = requests per second
- `status=~"5.."` = HTTP 500-599 errors
- `> 0.05` = greater than 5% error rate

### Connection Pool Usage
```promql
pg_stat_database_numbackends / pg_settings_max_connections > 0.8
```
- Divides active connections by max connections
- `> 0.8` = more than 80% used

### CPU Usage
```promql
rate(process_cpu_seconds_total[5m]) > 0.8
```
- CPU time rate over 5 minutes
- `> 0.8` = 80% of 1 core for a single-threaded process

## Monitoring the Monitoring

### Check Alert Evaluation

```bash
# View all rules and their status
curl http://localhost:9090/api/v1/rules | jq

# Check specific alert
curl 'http://localhost:9090/api/v1/query?query=ALERTS{alertname="ServiceDown"}' | jq
```

### Verify Alert Delivery

```bash
# View firing alerts in Alertmanager
curl http://localhost:9093/api/v1/alerts | jq

# Check alert history
curl http://localhost:9093/api/v1/alerts/groups | jq
```

### Prometheus Health

```bash
# TSDB status
curl http://localhost:9090/api/v1/query?query=prometheus_tsdb_symbol_table_size_bytes | jq

# Scrape metrics
curl http://localhost:9090/api/v1/query?query=prometheus_sd_discovered_targets | jq
```

## Runbook Examples

### High Error Rate Runbook

**Alert:** HighErrorRate
**Duration:** 5 minutes at >5% error rate

**Steps:**
1. Check recent deployments: `git log --oneline -5`
2. Review error logs: `docker logs <service> --tail 100`
3. Check database connectivity
4. Check external dependencies (APIs, services)
5. Scale service if under load: `docker-compose up -d --scale backend=3`
6. If unresolved, trigger incident: Create PagerDuty incident

**Prevention:**
- Implement better error tracking
- Increase test coverage
- Add pre-deployment smoke tests

### ServiceDown Runbook

**Alert:** ServiceDown
**Duration:** 1 minute

**Steps:**
1. Check service status: `curl http://service:port/health`
2. Check logs: `docker logs <service> --tail 50`
3. Check resource usage: `docker stats`
4. Restart service: `docker-compose restart <service>`
5. Verify recovery: `curl http://service:port/health`
6. If still down, check infrastructure (disk space, network)

### High Database Latency Runbook

**Alert:** HighDatabaseLatency
**Duration:** 5 minutes at P95 > 1s

**Steps:**
1. Check slow queries:
   ```sql
   SELECT query, calls, mean_exec_time, max_exec_time
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC LIMIT 10;
   ```

2. Check connection count:
   ```sql
   SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
   ```

3. Check index usage:
   ```sql
   SELECT schemaname, tablename, indexname, idx_scan
   FROM pg_stat_user_indexes ORDER BY idx_scan DESC;
   ```

4. Consider:
   - Adding missing indexes
   - Optimizing problematic queries
   - Increasing connection pool size
   - Scaling to read replicas

## Integration with CI/CD

### Pre-deployment Alert Checks

```bash
#!/bin/bash
# Check if critical alerts are firing
FIRING=$(curl -s http://localhost:9093/api/v1/alerts | jq '.data | length')

if [ "$FIRING" -gt 0 ]; then
  echo "BLOCKED: Critical alerts are firing"
  echo "Current alerts:"
  curl -s http://localhost:9093/api/v1/alerts | jq '.data[] | {alertname, severity}'
  exit 1
fi

echo "All clear - proceeding with deployment"
```

### Post-deployment Verification

```bash
#!/bin/bash
# Wait for services to stabilize
sleep 30

# Check error rate
ERROR_RATE=$(curl -s 'http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])' | \
  jq '.data.result[0].value[1] | tonumber')

if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
  echo "ERROR: Post-deployment error rate too high: $ERROR_RATE"
  exit 1
fi

echo "Deployment verified - error rate: $ERROR_RATE"
```

## Troubleshooting

### Alerts not firing?

1. Check Prometheus is scraping targets:
   ```bash
   curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
   ```

2. Verify alert rules syntax:
   ```bash
   promtool check rules /etc/prometheus/alerts.yml
   ```

3. Check rule evaluation:
   ```bash
   curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | {alert, state, evaluationTime}'
   ```

### Alerts not delivering?

1. Check Alertmanager configuration:
   ```bash
   curl http://localhost:9093/api/v1/status | jq
   ```

2. Test webhook:
   ```bash
   curl -X POST $SLACK_WEBHOOK_URL \
     -H 'Content-Type: application/json' \
     -d '{"text":"Test alert from Prometheus"}'
   ```

3. Check Alertmanager logs:
   ```bash
   docker logs alertmanager
   ```

### Too many alerts?

1. Increase `for:` duration to reduce noise
2. Adjust thresholds based on actual SLOs
3. Use inhibition rules to suppress related alerts
4. Consider severity levels

## Best Practices

1. **Clear Alert Names:** Use `What + How Bad` (e.g., `HighErrorRate`)
2. **Actionable Descriptions:** Include relevant variables and context
3. **Runbook URLs:** Every alert should have a runbook
4. **MTTR Targets:** Define expected recovery time for each alert
5. **Team Labels:** Route to correct team/on-call
6. **SLO Alignment:** Link alerts to SLOs
7. **Threshold Testing:** Validate thresholds in staging first
8. **Inhibition Rules:** Suppress cascading alerts
9. **Silence Dead Alerts:** Disable alerts during planned maintenance
10. **Regular Reviews:** Monthly alert effectiveness review

## Files Created

- `/monitoring/alerts.yml` - Comprehensive alert rules (MTTR <5m)
- `/monitoring/alertmanager.yml` - Alert routing configuration
- `/monitoring/prometheus.yml` - Updated with alert rules and Alertmanager
- `/monitoring/docker-compose.yml` - Complete monitoring stack

## Next Steps

1. Configure Slack/Email/PagerDuty webhooks
2. Deploy monitoring stack: `docker-compose up -d`
3. Review alert thresholds for your environment
4. Create runbooks for each alert
5. Set up on-call rotation in PagerDuty
6. Test alert delivery with manual triggers
7. Monitor alert volume and false positives
8. Iterate on thresholds based on actual performance

## References

- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [SLO Best Practices](https://landing.google.com/sre/sre-book/chapters/service-level-objectives/)
