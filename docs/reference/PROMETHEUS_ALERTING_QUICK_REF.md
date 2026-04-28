# Prometheus Alerting - Quick Reference

## Quick Start

```bash
# Start monitoring stack
cd monitoring/
cp .env.example .env
# Edit .env with your Slack/Email/PagerDuty credentials
docker-compose up -d

# Verify all services are running
docker-compose ps
```

## UI Access

| Service | URL | Purpose |
|---------|-----|---------|
| Prometheus | http://localhost:9090 | Metrics & alerts dashboard |
| Alertmanager | http://localhost:9093 | Alert routing & notifications |

## Common Tasks

### View Active Alerts

```bash
# In browser
open http://localhost:9090/alerts

# Via API
curl http://localhost:9090/api/v1/alerts | jq '.data[] | {alertname, state, severity}'
```

### View Alert Groups

```bash
curl http://localhost:9093/api/v1/alerts/groups | jq
```

### Check Specific Alert Status

```bash
curl 'http://localhost:9090/api/v1/query?query=ALERTS{alertname="ServiceDown"}' | jq
```

### View Prometheus Targets

```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job, instance, health}'
```

### Test Alert Rules

```bash
# Check syntax
promtool check rules /path/to/alerts.yml

# Validate configuration
promtool check config /path/to/prometheus.yml
```

### Manually Fire an Alert (Testing)

```bash
# Query that matches the alert condition
curl 'http://localhost:9090/api/v1/query?query=up{job="prometheus"}==0' | jq

# If it returns data, the alert would fire
# Wait for the "for:" duration, then it fires
```

### Silence an Alert

In Alertmanager UI:
1. Navigate to http://localhost:9093/#/silences
2. Click "New Silence"
3. Select matcher (alertname, job, etc.)
4. Set duration
5. Click "Create"

Or via API:
```bash
curl -X POST http://localhost:9093/api/v1/silences \
  -H 'Content-Type: application/json' \
  -d '{
    "matchers": [{"name": "alertname", "value": "ServiceDown"}],
    "startsAt": "2024-02-01T00:00:00Z",
    "endsAt": "2024-02-02T00:00:00Z",
    "comment": "Maintenance window"
  }'
```

## Alert Severity Levels

| Severity | Response Time | Channel | Example |
|----------|---------------|---------|---------|
| critical | 0-5 min | Slack + Email + PagerDuty | ServiceDown, NoActiveAgents |
| warning | 5-30 min | Slack #warnings | HighErrorRate, HighLatency |
| info | 30+ min | Slack #info | LowCacheHitRatio, SystemIdle |

## PromQL Snippets

### Current Error Rate (%)
```promql
100 * sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### Current P95 Latency
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Database Connections
```promql
pg_stat_database_numbackends
```

### Cache Hit Ratio
```promql
sum(rate(tracertm_cache_hits_total[5m])) / (sum(rate(tracertm_cache_hits_total[5m])) + sum(rate(tracertm_cache_misses_total[5m])))
```

### Active Agents
```promql
tracertm_active_agents
```

## Docker Commands

```bash
# View logs
docker-compose logs -f prometheus
docker-compose logs -f alertmanager

# Restart service
docker-compose restart prometheus
docker-compose restart alertmanager

# Rebuild and restart
docker-compose up -d --force-recreate

# Stop monitoring
docker-compose down

# Check stats
docker stats prometheus alertmanager
```

## Troubleshooting

### "No targets found"

```bash
# Check if services are running
docker-compose ps

# Check Prometheus config syntax
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml

# View startup logs
docker logs prometheus
```

### "Alert not firing"

```bash
# Verify metric exists
curl 'http://localhost:9090/api/v1/query?query=up{job="your-job"}' | jq

# Check alert rule evaluation
curl http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name=="api_alerts") | .rules[] | {alert, state, evaluationTime}'

# Wait for "for:" duration to complete
```

### "Alerts not being delivered"

```bash
# Check Alertmanager status
curl http://localhost:9093/api/v1/status | jq

# Test webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from Prometheus"}'

# View Alertmanager logs
docker logs alertmanager
```

### "High memory usage in Prometheus"

```bash
# Check TSDB statistics
curl http://localhost:9090/api/v1/tsdb | jq

# Reduce retention period in prometheus.yml
# Change: --storage.tsdb.retention.time=15d to shorter duration

# Restart Prometheus
docker-compose restart prometheus
```

## Alert Configuration Reference

### Add New Alert Rule

Edit `/monitoring/alerts.yml`:

```yaml
- alert: MyNewAlert
  expr: metric > threshold           # PromQL expression
  for: 5m                            # Duration before firing
  labels:
    severity: warning                # critical | warning | info
    team: backend                     # Team responsible
    slo: availability                 # Associated SLO
  annotations:
    summary: "Brief description"
    description: "{{ $value }}"       # Include variable details
    runbook_url: "Link to wiki"
    mttr_target: "5m"
```

Reload rules:
```bash
curl -X POST http://localhost:9090/-/reload
# Or restart Prometheus
docker-compose restart prometheus
```

### Add New Notification Channel

Edit `/monitoring/alertmanager.yml`:

```yaml
receivers:
  - name: 'my-channel'
    slack_configs:
      - channel: '#my-alerts'
        api_url: '${SLACK_WEBHOOK_URL}'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_KEY}'
    email_configs:
      - to: 'team@example.com'
```

Update route:
```yaml
routes:
  - match:
      team: my-team
    receiver: 'my-channel'
```

Restart Alertmanager:
```bash
docker-compose restart alertmanager
```

## Performance Tuning

### Reduce TSDB Disk Usage

```bash
# In prometheus.yml, modify command section:
--storage.tsdb.retention.time=7d    # Reduce from 15d
--storage.tsdb.max-block-duration=2h # Smaller blocks
```

### Reduce Alert Evaluation Load

```yaml
global:
  evaluation_interval: 60s  # Increase from 15s
```

**Trade-off:** Longer latency to detect issues (slower MTTR)

### Optimize Scrape Interval

```yaml
scrape_configs:
  - job_name: 'my-job'
    scrape_interval: 30s    # Increase if OK for your use case
```

## Metrics Glossary

| Metric | Meaning | Alert Threshold |
|--------|---------|-----------------|
| `http_request_duration_seconds_bucket` | Request latency histogram | P95 > 1s |
| `http_requests_total` | Total HTTP requests | N/A (for rate) |
| `pg_stat_database_numbackends` | Active DB connections | > 0.8 * max |
| `process_resident_memory_bytes` | Process memory usage | > 1GB |
| `process_cpu_seconds_total` | Process CPU time | rate > 0.8 |
| `up` | Target health (1=up, 0=down) | == 0 |

## Links

- [Prometheus Docs](https://prometheus.io/docs/)
- [Alertmanager Docs](https://prometheus.io/docs/alerting/latest/)
- [PromQL Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Alert Best Practices](https://prometheus.io/docs/practices/alerting/)

## Support

For detailed information, see:
- `/docs/guides/PROMETHEUS_ALERTING_SETUP.md` - Full setup guide
- `/monitoring/alerts.yml` - All alert rules
- `/monitoring/alertmanager.yml` - Routing configuration
- `/monitoring/prometheus.yml` - Prometheus configuration
