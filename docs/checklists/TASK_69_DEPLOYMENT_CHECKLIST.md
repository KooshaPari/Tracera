# Task #69: Prometheus Alerting Rules - Deployment Checklist

## Pre-Deployment Verification

- [x] All configuration files created
  - [x] `/monitoring/alerts.yml` - 29 alert rules (425 lines)
  - [x] `/monitoring/alertmanager.yml` - routing configuration
  - [x] `/monitoring/prometheus.yml` - updated with alert integration
  - [x] `/monitoring/docker-compose.yml` - complete monitoring stack
  - [x] `/monitoring/.env.example` - environment template

- [x] Documentation complete
  - [x] `/docs/guides/PROMETHEUS_ALERTING_SETUP.md` - comprehensive guide
  - [x] `/docs/reference/PROMETHEUS_ALERTING_QUICK_REF.md` - quick reference
  - [x] `/docs/reports/TASK_69_PROMETHEUS_ALERTING_COMPLETION.md` - completion report
  - [x] `/docs/checklists/TASK_69_DEPLOYMENT_CHECKLIST.md` - this checklist

- [x] Configuration validation
  - [x] YAML syntax verified
  - [x] PromQL expressions reviewed
  - [x] Alert rules organized logically
  - [x] All thresholds appropriate for MTTR < 5 minutes

## Deployment Steps

### Step 1: Prepare Environment

- [ ] Navigate to monitoring directory
  ```bash
  cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/monitoring
  ```

- [ ] Create .env file from template
  ```bash
  cp .env.example .env
  ```

- [ ] Edit .env with your credentials
  ```bash
  # Required
  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

  # Optional but recommended
  SMTP_USERNAME=alerts@example.com
  SMTP_PASSWORD=your-password
  PAGERDUTY_SERVICE_KEY=your-key

  # Database (if monitoring database)
  DB_USER=postgres
  DB_PASSWORD=postgres
  DB_HOST=localhost
  DB_NAME=tracertm
  ```

### Step 2: Start Monitoring Stack

- [ ] Start all services
  ```bash
  docker-compose up -d
  ```

- [ ] Verify all services are running
  ```bash
  docker-compose ps
  ```
  Expected: All services showing "Up"

- [ ] Check Prometheus is healthy
  ```bash
  curl http://localhost:9090/-/healthy
  ```
  Expected: HTTP 200

- [ ] Check Alertmanager is healthy
  ```bash
  curl http://localhost:9093/-/healthy
  ```
  Expected: HTTP 200

### Step 3: Verify Prometheus

- [ ] Access Prometheus UI
  ```
  http://localhost:9090
  ```

- [ ] Check all targets are scraped
  - [ ] Go to Status → Targets
  - [ ] All job targets should show "UP"
  - [ ] Expected jobs: prometheus, node, postgres, redis, go-backend, python-backend

- [ ] Verify alert rules loaded
  - [ ] Go to Alerts tab
  - [ ] Should see 29 alert rules listed
  - [ ] Rules organized into 8 groups

- [ ] Check metrics are flowing
  ```bash
  curl 'http://localhost:9090/api/v1/query?query=up' | jq
  ```
  Expected: Multiple targets with value 1

### Step 4: Verify Alertmanager

- [ ] Access Alertmanager UI
  ```
  http://localhost:9093
  ```

- [ ] Check status
  - [ ] Click "Status" tab
  - [ ] Configuration should load without errors

- [ ] Verify routing configuration
  - [ ] Should see receiver configuration
  - [ ] Routes properly defined
  - [ ] Inhibition rules configured

- [ ] Check alert groups (if any alerts firing)
  ```bash
  curl http://localhost:9093/api/v1/alerts/groups | jq
  ```

### Step 5: Test Alert Delivery

#### Test Slack Integration

- [ ] Trigger test notification
  ```bash
  curl -X POST $SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d '{"text":"Test from Prometheus Alerting Setup"}'
  ```
  Expected: Message appears in configured Slack channel

#### Test Email Integration (if configured)

- [ ] Verify SMTP credentials in .env
- [ ] Watch for test email delivery
  - Send via API or trigger an alert

#### Test PagerDuty Integration (if configured)

- [ ] Verify service key in .env
- [ ] Create test incident in PagerDuty dashboard
- [ ] Verify can be resolved

### Step 6: Verify Alert Rules

#### Quick Verification

- [ ] Query for alert rules
  ```bash
  curl http://localhost:9090/api/v1/rules | jq '.data.groups[] | .name'
  ```
  Expected 8 groups:
  - api_alerts
  - database_alerts
  - resource_alerts
  - cache_alerts
  - messaging_alerts
  - infrastructure_alerts
  - workflow_alerts
  - slo_alerts

#### Verify Critical Alerts

- [ ] Check critical alert count
  ```bash
  curl http://localhost:9090/api/v1/rules | jq '[.data.groups[].rules[] | select(.labels.severity=="critical")] | length'
  ```
  Expected: 8 critical alerts

#### Verify MTTR Targets

- [ ] All critical alerts should have mttr_target
  ```bash
  curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.labels.severity=="critical") | .annotations.mttr_target'
  ```

### Step 7: Load Testing (Optional)

#### Simulate High Latency

- [ ] Verify HighAPILatency alert threshold
  - [ ] Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
  - [ ] Should be collecting values

#### Simulate Error Rate

- [ ] Verify HighErrorRate alert threshold
  - [ ] Query: `rate(http_requests_total{status=~"5.."}[5m])`
  - [ ] Should be collecting values

#### Simulate Resource Pressure

- [ ] Monitor resource metrics
  - [ ] CPU: `rate(process_cpu_seconds_total[5m])`
  - [ ] Memory: `process_resident_memory_bytes`
  - [ ] All metrics should be available

### Step 8: Documentation Verification

- [ ] Read setup guide
  - [ ] Path: `/docs/guides/PROMETHEUS_ALERTING_SETUP.md`
  - [ ] Contains quick start
  - [ ] Contains alert categories
  - [ ] Contains runbook examples

- [ ] Review quick reference
  - [ ] Path: `/docs/reference/PROMETHEUS_ALERTING_QUICK_REF.md`
  - [ ] Common commands documented
  - [ ] Troubleshooting guide available
  - [ ] PromQL snippets provided

- [ ] Check completion report
  - [ ] Path: `/docs/reports/TASK_69_PROMETHEUS_ALERTING_COMPLETION.md`
  - [ ] Contains implementation details
  - [ ] Files summary with locations
  - [ ] Next steps documented

## Post-Deployment Configuration

### Configure Runbooks

- [ ] Update runbook URLs in alerts.yml
  - [ ] Replace `https://wiki.example.com/runbooks/` with actual wiki URL
  - [ ] Ensure each alert has valid runbook link

  ```bash
  sed -i 's|https://wiki.example.com/runbooks/|https://your-wiki.com/runbooks/|g' /monitoring/alerts.yml
  docker-compose restart prometheus
  ```

### Configure On-Call

- [ ] Set up PagerDuty service
  - [ ] Create service in PagerDuty
  - [ ] Add Events integration
  - [ ] Copy service key to .env

- [ ] Configure escalation policy
  - [ ] Set up on-call rotation
  - [ ] Assign team members

- [ ] Test on-call notification
  - [ ] Trigger a critical alert
  - [ ] Verify on-call engineer is notified

### Configure Team Ownership

- [ ] Verify team labels in alerts
  ```bash
  curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | .labels.team' | sort -u
  ```
  Should see: backend, infra, dba

- [ ] Create Slack channels for each team
  - [ ] #critical-alerts (for critical issues)
  - [ ] #warnings (for warnings)
  - [ ] #info (for info alerts)

- [ ] Update Alertmanager receivers with team channels
  ```yaml
  - name: 'backend-team'
    slack_configs:
      - channel: '#backend-alerts'
  ```

## Operational Verification

### Week 1 Monitoring

- [ ] Monitor alert accuracy
  - [ ] Log all alert firing/resolving
  - [ ] Identify false positives
  - [ ] Note thresholds that need adjustment

- [ ] Track MTTR
  - [ ] Time from alert to notification
  - [ ] Time from notification to response
  - [ ] Time from response to resolution

- [ ] Review alert volume
  - [ ] Expected: 2-5 alerts per day (normal operation)
  - [ ] If too many: adjust thresholds
  - [ ] If none: verify metrics are flowing

### Week 2 Tuning

- [ ] Adjust thresholds based on week 1 data
  - [ ] Update alerts.yml
  - [ ] Restart prometheus: `docker-compose restart prometheus`

- [ ] Create team runbooks
  - [ ] Document each alert's remediation
  - [ ] Update runbook URLs
  - [ ] Train teams

- [ ] Set up dashboards
  - [ ] Create Grafana dashboard with alert metrics
  - [ ] Link from Alertmanager

### Month 1 Review

- [ ] Analyze MTTR metrics
  - [ ] Are we meeting < 5 minutes?
  - [ ] What's blocking faster response?
  - [ ] Adjust as needed

- [ ] Review alert effectiveness
  - [ ] Ratio of actionable vs noise
  - [ ] Adjust severity levels if needed
  - [ ] Update inhibition rules

- [ ] Plan improvements
  - [ ] Add more alerts if gaps found
  - [ ] Improve runbooks
  - [ ] Train team

## Troubleshooting Checklist

### If services won't start

- [ ] Check Docker is running
  ```bash
  docker ps
  ```

- [ ] Check port conflicts (9090, 9093)
  ```bash
  lsof -i :9090
  lsof -i :9093
  ```

- [ ] View logs
  ```bash
  docker-compose logs prometheus
  docker-compose logs alertmanager
  ```

### If targets are down

- [ ] Check target services are running
  - [ ] Backend: `curl http://localhost:8080/metrics`
  - [ ] Database: `curl http://localhost:9187/metrics`
  - [ ] Redis: `curl http://localhost:9121/metrics`

- [ ] Check network connectivity
  ```bash
  docker exec prometheus curl http://node_exporter:9100/metrics
  ```

- [ ] Check Prometheus scrape config
  ```bash
  curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health=="down")'
  ```

### If alerts not firing

- [ ] Verify metrics exist
  ```bash
  curl 'http://localhost:9090/api/v1/query?query=http_request_duration_seconds_bucket' | jq
  ```

- [ ] Check alert rule evaluation
  ```bash
  curl http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name=="api_alerts") | .rules[] | {alert, state}'
  ```

- [ ] Verify "for:" duration has passed
  - [ ] Rules need to be true for the "for:" duration
  - [ ] Check how long the condition has been true

### If alerts not delivering

- [ ] Check Alertmanager status
  ```bash
  curl http://localhost:9093/api/v1/status | jq
  ```

- [ ] Test webhook directly
  ```bash
  curl -X POST $SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d '{"text":"Test"}'
  ```

- [ ] Check Alertmanager logs
  ```bash
  docker logs alertmanager --tail 50
  ```

## Sign-Off

- [ ] Pre-deployment checks completed
- [ ] Deployment completed successfully
- [ ] All services verified operational
- [ ] Alert delivery tested
- [ ] Documentation reviewed
- [ ] Team trained
- [ ] On-call integration verified
- [ ] Runbooks created and linked
- [ ] MTTR targets confirmed < 5 minutes

**Deployment Date:** _______________
**Deployed By:** _______________
**Verified By:** _______________
**Notes:** _______________

---

## Support

For issues or questions, refer to:
- Setup Guide: `/docs/guides/PROMETHEUS_ALERTING_SETUP.md`
- Quick Reference: `/docs/reference/PROMETHEUS_ALERTING_QUICK_REF.md`
- Completion Report: `/docs/reports/TASK_69_PROMETHEUS_ALERTING_COMPLETION.md`
