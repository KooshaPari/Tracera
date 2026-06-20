> Historical note: this document preserves the pre-Phenotype observability stack. The active org path is the shared collector, Grafana Alloy, and Grafana Tempo. Treat Jaeger and Promtail references below as legacy context only.

# Performance Monitoring Guide

> **Complete real-time monitoring system for TraceRTM covering frontend, backend, infrastructure, and business metrics**

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Dashboards](#dashboards)
- [Frontend Monitoring](#frontend-monitoring)
- [Backend Monitoring](#backend-monitoring)
- [Infrastructure Monitoring](#infrastructure-monitoring)
- [Business Metrics](#business-metrics)
- [SLO Alerting](#slo-alerting)
- [Setup & Configuration](#setup--configuration)
- [Testing & Verification](#testing--verification)
- [Troubleshooting](#troubleshooting)

---

## Overview

TraceRTM's performance monitoring system provides comprehensive observability across all layers of the application stack:

- **Detection Time**: <5 minutes for performance regressions
- **False Positive Rate**: <1% on alert triggers
- **Alert Delivery**: 100% critical alert delivery guarantee
- **Dashboard Refresh**: Auto-refresh every 5 minutes
- **Data Retention**: 15 days (Prometheus default)

### Key Features

1. **Real-time Web Vitals tracking** (LCP, FID, CLS, TTFB, INP)
2. **API performance monitoring** (latency percentiles, error rates, throughput)
3. **Infrastructure health monitoring** (CPU, memory, disk, network)
4. **Business metrics tracking** (users, features, journeys)
5. **SLO-based alerting** (latency, errors, availability)
6. **Anomaly detection** (spikes, drops, variance)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Browser)                      │
├─────────────────────────────────────────────────────────────┤
│  Web Vitals Collector                                       │
│  ├─ Core Web Vitals (LCP, FID, CLS, TTFB, INP)            │
│  ├─ Bundle Size Tracking                                    │
│  ├─ Component Render Times                                  │
│  └─ JavaScript Error Tracking                               │
│                          │                                   │
│                          ▼                                   │
│              POST /api/v1/metrics/web-vitals                │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Backend (Go + Python)                     │
├─────────────────────────────────────────────────────────────┤
│  Service Metrics                                             │
│  ├─ Request duration histograms                             │
│  ├─ Error rate counters                                     │
│  ├─ Throughput gauges                                       │
│  └─ Active request tracking                                 │
│                                                              │
│  Business Metrics                                            │
│  ├─ User session tracking                                   │
│  ├─ Feature adoption rates                                  │
│  ├─ Journey completion tracking                             │
│  └─ Content creation metrics                                │
│                          │                                   │
│                          ▼                                   │
│            /metrics (Prometheus scrape endpoint)            │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Prometheus (Scraper)                        │
├─────────────────────────────────────────────────────────────┤
│  Scrape Targets (15s interval):                             │
│  ├─ Go Backend         :8080/metrics                        │
│  ├─ Python Backend     :8000/metrics                        │
│  ├─ PostgreSQL Export :9187/metrics                        │
│  ├─ Redis Exporter    :9121/metrics                        │
│  ├─ Node Exporter     :9100/metrics                        │
│  └─ Caddy            :2019/metrics                        │
│                                                              │
│  Rule Files:                                                 │
│  └─ monitoring/alerting/slo-alerts.yml                      │
│                          │                                   │
│                          ▼                                   │
│                    Alertmanager                              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    ┌──────────┴─────────┐
                    ▼                    ▼
         ┌───────────────┐    ┌──────────────────┐
         │    Grafana    │    │   Alertmanager   │
         │  Dashboards   │    │    (Routing)     │
         └───────────────┘    └──────┬───────────┘
              :3000                  │
                               ┌─────┴──────┬──────────┐
                               ▼            ▼          ▼
                           Slack      PagerDuty    Email
```

---

## Dashboards

### Dashboard List

1. **[Frontend Performance](#frontend-performance-dashboard)** (`frontend-performance.json`)
   - Core Web Vitals (LCP, FID, CLS, TTFB, INP)
   - Bundle size tracking
   - Component render times
   - JavaScript error rates

2. **[Backend Performance](#backend-performance-dashboard)** (`backend-performance.json`)
   - Request latency percentiles (P50, P95, P99, P99.9)
   - Error rates by endpoint and status
   - Throughput (requests/second)
   - Database query performance
   - External API latency

3. **[Infrastructure Health](#infrastructure-health-dashboard)** (`infrastructure-health.json`)
   - CPU usage by service
   - Memory usage with leak detection
   - Disk I/O and space
   - Network bandwidth
   - Service health status
   - Database connection pools

4. **[Business Metrics](#business-metrics-dashboard)** (`business-metrics-enhanced.json`)
   - Active users (realtime, daily, weekly, monthly)
   - API usage by endpoint
   - Feature adoption rates
   - User journey completion rates
   - Content creation metrics
   - Integration activity

### Accessing Dashboards

```bash
# Start monitoring stack
make dev-tui

# Open Grafana
make grafana-dashboard
# or: open http://localhost:3000

# Login credentials (default)
Username: admin
Password: admin
```

Navigate to:
- **Dashboards → Browse → TraceRTM**
- Or use dashboard links (cross-linked in UI)

---

## Frontend Monitoring

### Web Vitals Tracking

Located at: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/lib/monitoring/webVitals.ts`

#### Core Web Vitals

| Metric | Description | Good | Needs Improvement | Poor |
|--------|-------------|------|------------------|------|
| **LCP** | Largest Contentful Paint | <2.5s | 2.5s - 4s | >4s |
| **FID** | First Input Delay | <100ms | 100ms - 300ms | >300ms |
| **CLS** | Cumulative Layout Shift | <0.1 | 0.1 - 0.25 | >0.25 |
| **TTFB** | Time to First Byte | <800ms | 800ms - 1.8s | >1.8s |
| **INP** | Interaction to Next Paint | <200ms | 200ms - 500ms | >500ms |

#### Usage

```typescript
// Initialize in app root
import { initWebVitals } from '@/lib/monitoring/webVitals';

// In your main app component
useEffect(() => {
  if (typeof window !== 'undefined') {
    initWebVitals();
  }
}, []);
```

#### React Profiler Integration

```typescript
import { Profiler } from 'react';
import { createProfilerOnRender } from '@/lib/monitoring/webVitals';

function MyComponent() {
  return (
    <Profiler id="MyComponent" onRender={createProfilerOnRender('MyComponent')}>
      {/* component content */}
    </Profiler>
  );
}
```

#### Manual Event Reporting

```typescript
import { webVitalsCollector } from '@/lib/monitoring/webVitals';

// Report custom component render
webVitalsCollector.reportComponentRender({
  componentName: 'DataTable',
  renderTime: 45.5,
  phase: 'update',
  timestamp: Date.now(),
});
```

### Bundle Size Tracking

Automatically tracked on page load. Measures:
- Total bundle size
- JavaScript bundle size
- CSS bundle size
- Image assets size

### Error Tracking

Automatically captures:
- Uncaught JavaScript errors
- Unhandled promise rejections
- Component-level errors (via Error Boundaries)

---

## Backend Monitoring

### Service Metrics (Go)

Located at: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/metrics/service_metrics.go`

#### Initialization

```go
import "your-module/backend/internal/metrics"

func main() {
    // Initialize metrics
    metrics.Metrics = metrics.NewServiceMetrics("tracertm")

    // Start your server
    // ...
}
```

#### Recording Metrics

```go
// Record request
start := time.Now()
defer func() {
    duration := time.Since(start).Seconds()

    metrics.Metrics.RequestsTotal.WithLabelValues(
        "items",      // service
        "GET",        // method
        "200",        // status
    ).Inc()

    metrics.Metrics.RequestDuration.WithLabelValues(
        "items",      // service
        "GET",        // method
    ).Observe(duration)
}()
```

### Business Metrics (Go)

Located at: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/metrics/business_metrics.go`

#### Initialization

```go
import "your-module/backend/internal/metrics"

func init() {
    metrics.InitBusinessMetrics("tracertm")
}
```

#### Recording Business Events

```go
// Record user session
metrics.RecordUserSession("user-123", 30*time.Minute)

// Record feature usage
metrics.RecordFeatureUsage("graph-view", "expand-node", "user-123")

// Record journey step
metrics.RecordJourneyStep("onboarding", "create-first-project", "user-123")

// Record search query
metrics.RecordSearchQuery("semantic", 15) // 15 results

// Record web vitals from frontend
metrics.RecordWebVitals("dashboard", "LCP", "good", 2.1)
```

### API Endpoints

Backend exposes metrics at:

- **Go Backend**: `http://localhost:8080/metrics`
- **Python Backend**: `http://localhost:8000/metrics`

Test with:
```bash
curl http://localhost:8080/metrics | grep tracertm
```

---

## Infrastructure Monitoring

### Exporters

| Exporter | Port | Metrics |
|----------|------|---------|
| **postgres_exporter** | 9187 | Connection pool, query stats, locks |
| **redis_exporter** | 9121 | Memory, connections, commands |
| **node_exporter** | 9100 | CPU, memory, disk, network |

### Health Checks

All services expose health checks:

```bash
# Infrastructure
curl http://localhost:5432  # PostgreSQL (connection test)
redis-cli ping              # Redis
curl http://localhost:7474  # Neo4j
curl http://localhost:8222/healthz  # NATS

# Backends
curl http://localhost:8080/health   # Go
curl http://localhost:8000/health   # Python

# Gateway
curl http://localhost:4000/health   # Caddy

# Monitoring
curl http://localhost:9090/-/ready  # Prometheus
curl http://localhost:3000/api/health  # Grafana
```

### Process Status

Check native process status:

```bash
# Via Process Compose
make dev-status

# Via TUI
make dev-tui  # Press 'h' for help

# Check individual service
make dev-logs-follow SERVICE=postgres
```

---

## Business Metrics

### User Tracking

**Active Users**:
- **Real-time**: Users active in last 5 minutes
- **Daily**: Unique users in last 24 hours
- **Weekly**: Unique users in last 7 days
- **Monthly**: Unique users in last 30 days

**Session Tracking**:
```go
// Start session
sessionStart := time.Now()

// ... user activity ...

// End session
sessionDuration := time.Since(sessionStart)
metrics.RecordUserSession(userID, sessionDuration)
```

### Feature Adoption

**Tracking Feature Usage**:
```go
metrics.RecordFeatureUsage(
    "graph-filtering",  // feature name
    "apply-filter",     // action
    userID,             // user ID
)
```

**Calculating Adoption Rate** (in dashboard):
```promql
sum(count_over_time(tracertm_features_usage_total{feature="graph-filtering"}[7d]))
/
tracertm_users_unique_weekly
```

### User Journeys

**Defining Journeys**:
1. Journey Start
2. Multiple Steps
3. Journey Completion or Dropoff

**Tracking Journey**:
```go
// Journey starts
metrics.BusinessMetricsInstance.JourneyStarts.WithLabelValues(
    "project-creation",
    userID,
).Inc()

// Each step
metrics.RecordJourneyStep("project-creation", "name-entered", userID)
metrics.RecordJourneyStep("project-creation", "settings-configured", userID)

// Completion
metrics.BusinessMetricsInstance.JourneyCompletions.WithLabelValues(
    "project-creation",
    userID,
).Inc()

// Track duration
journeyDuration := time.Since(journeyStart)
metrics.BusinessMetricsInstance.JourneyDuration.WithLabelValues(
    "project-creation",
).Observe(journeyDuration.Seconds())
```

### Content Creation Tracking

```go
// Items
metrics.BusinessMetricsInstance.ItemsCreated.WithLabelValues(
    "requirement",  // item type
    userID,
).Inc()

// Links
metrics.BusinessMetricsInstance.LinksCreated.WithLabelValues(
    "satisfies",    // link type
    userID,
).Inc()

// Projects
metrics.BusinessMetricsInstance.ProjectsCreated.WithLabelValues(
    userID,
).Inc()
```

---

## SLO Alerting

### Service Level Objectives

Located at: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/monitoring/alerting/slo-alerts.yml`

| SLO | Target | Warning Threshold | Critical Threshold |
|-----|--------|------------------|-------------------|
| **Latency (P95)** | <500ms | >500ms | >1s |
| **Error Rate** | <1% | >1% | >5% |
| **Availability** | >99.9% | Service flapping | Service down |

### Alert Configuration

Prometheus loads alerts from:
```yaml
# monitoring/prometheus.yml
rule_files:
  - 'alerting/slo-alerts.yml'
```

### Alert Routing

Configure in `monitoring/alertmanager.yml`:

```yaml
route:
  group_by: ['alertname', 'job']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        alert_channel: pagerduty
      receiver: 'pagerduty'
      continue: true
    - match:
        alert_channel: slack
      receiver: 'slack'
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://localhost:8080/api/v1/alerts'

  - name: 'slack'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
```

### Environment Variables

Add to `.env`:
```bash
# Alerting Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_SERVICE_KEY=your-pagerduty-integration-key

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@yourdomain.com
SMTP_PASSWORD=your-smtp-password
ALERT_EMAIL_FROM=alerts@yourdomain.com
ALERT_EMAIL_TO=oncall@yourdomain.com
```

### Testing Alerts

Trigger test alert:
```bash
# Simulate high latency (in development)
# Add artificial delay to an endpoint

# Force alert
curl -X POST http://localhost:9090/-/reload

# Check alert status
curl http://localhost:9090/api/v1/alerts | jq .
```

View alerts in Grafana:
1. Navigate to **Alerting → Alert Rules**
2. Check alert status and history
3. View firing alerts

---

## Setup & Configuration

### 1. Install Dependencies

```bash
# Install native monitoring stack
make install-native

# Verify installation
make verify-install

# Check services
brew services list | grep -E "(prometheus|grafana)"
```

### 2. Start Monitoring Stack

```bash
# Start all services (including monitoring)
make dev-tui

# Or start in background
make dev

# Check status
make dev-status
```

### 3. Configure Dashboards

Dashboards are auto-provisioned from:
```
monitoring/
├── dashboards/
│   ├── frontend-performance.json
│   ├── backend-performance.json
│   ├── infrastructure-health.json
│   └── business-metrics-enhanced.json
└── grafana/provisioning/
    └── dashboards/
        └── dashboards.yml
```

### 4. Verify Metrics Collection

```bash
# Check Prometheus targets
open http://localhost:9090/targets

# Should see all targets "UP":
# - go-backend
# - python-backend
# - postgresql
# - redis
# - node
# - caddy
```

### 5. Access Grafana

```bash
# Open Grafana
make grafana-dashboard

# Login: admin / admin
# Navigate to Dashboards → Browse → TraceRTM
```

---

## Testing & Verification

### 1. Frontend Metrics Test

```bash
# Open frontend
open http://localhost:4000

# Check browser console for Web Vitals
# Should see metrics being collected and sent

# Verify metrics endpoint received data
curl -s http://localhost:8080/metrics | grep webvitals
```

### 2. Backend Metrics Test

```bash
# Generate some requests
for i in {1..100}; do
  curl -s http://localhost:4000/api/v1/health > /dev/null
done

# Check metrics
curl -s http://localhost:8080/metrics | grep request_duration

# Should see histogram buckets populated
```

### 3. Dashboard Refresh Test

1. Open Grafana dashboard
2. Note current values
3. Generate activity (browse pages, create items)
4. Wait 15-30 seconds (scrape interval)
5. Refresh dashboard (or wait for auto-refresh)
6. Verify metrics updated

### 4. Alert Test

Trigger a test alert:

```bash
# 1. Create artificial high latency
# Edit a backend endpoint to add sleep(2 seconds)

# 2. Generate requests
for i in {1..50}; do
  curl -s http://localhost:4000/api/v1/items > /dev/null
  sleep 0.1
done

# 3. Check Prometheus alerts
open http://localhost:9090/alerts

# 4. Wait ~2 minutes (alert "for" duration)
# 5. Alert should fire and appear in Grafana
```

### 5. Dashboard Load Time Test

```bash
# Measure dashboard load time
time curl -s http://localhost:3000/d/frontend-performance > /dev/null

# Should complete in <2 seconds
```

---

## Troubleshooting

### Issue: No Metrics in Grafana

**Symptoms**: Dashboards show "No data"

**Diagnosis**:
```bash
# 1. Check if Prometheus is scraping
open http://localhost:9090/targets

# 2. Check if metrics endpoint is responding
curl http://localhost:8080/metrics

# 3. Check Prometheus logs
make dev-logs-follow SERVICE=prometheus
```

**Solutions**:
- Restart Prometheus: `make dev-restart SERVICE=prometheus`
- Verify scrape configs in `monitoring/prometheus.yml`
- Check firewall/network connectivity

---

### Issue: Web Vitals Not Recording

**Symptoms**: Frontend dashboard shows no Web Vitals data

**Diagnosis**:
```bash
# 1. Check browser console for errors
# Open DevTools → Console

# 2. Check metrics endpoint
curl http://localhost:8080/api/v1/metrics/web-vitals

# 3. Check if web-vitals library loaded
# In browser console:
console.log(window.webVitalsCollector)
```

**Solutions**:
- Ensure `web-vitals` package installed: `bun add web-vitals`
- Verify `initWebVitals()` called in app initialization
- Check CORS settings if frontend on different port
- Clear browser cache and reload

---

### Issue: Alerts Not Firing

**Symptoms**: Expected alerts not appearing

**Diagnosis**:
```bash
# 1. Check alert rules loaded
curl http://localhost:9090/api/v1/rules | jq .

# 2. Check if conditions met
# Query Prometheus with alert expression

# 3. Check Alertmanager status
curl http://localhost:9093/api/v1/status | jq .
```

**Solutions**:
- Verify alert file syntax: `promtool check rules monitoring/alerting/slo-alerts.yml`
- Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`
- Check alert "for" duration (may need to wait)
- Verify Alertmanager routing configuration

---

### Issue: High Cardinality / Prometheus Performance

**Symptoms**: Prometheus slow, high memory usage

**Diagnosis**:
```bash
# Check Prometheus metrics
curl http://localhost:9090/metrics | grep prometheus_tsdb_symbol_table_size_bytes

# Check number of active series
curl http://localhost:9090/api/v1/status/tsdb | jq .data.seriesCountByMetricName
```

**Solutions**:
- Review metric labels (reduce cardinality)
- Don't use unique IDs as label values
- Use recording rules for expensive queries
- Adjust retention period
- Increase Prometheus resources

---

### Issue: Dashboard Performance Slow

**Symptoms**: Grafana dashboards take >5 seconds to load

**Diagnosis**:
```bash
# 1. Check Grafana logs
make dev-logs-follow SERVICE=grafana

# 2. Check query performance in Prometheus
# Use "Explain" in Grafana query editor

# 3. Check Grafana database
ls -lh .grafana/grafana.db
```

**Solutions**:
- Optimize Prometheus queries (use recording rules)
- Reduce dashboard time range
- Limit number of panels per dashboard
- Use dashboard variables for filtering
- Enable query caching in Grafana

---

### Issue: Missing Business Metrics

**Symptoms**: Business metrics dashboard empty

**Diagnosis**:
```bash
# 1. Check if business metrics initialized
curl http://localhost:8080/metrics | grep tracertm_users

# 2. Check application logs
make dev-logs-follow SERVICE=go-backend | grep metrics
```

**Solutions**:
- Verify `metrics.InitBusinessMetrics()` called in main.go
- Check that business events are being recorded
- Verify Prometheus scraping backend `/metrics` endpoint
- Generate some user activity to populate metrics

---

## Performance Targets

### Detection Time

| Event | Target | Method |
|-------|--------|--------|
| Performance regression | <5 min | SLO alerts |
| Service down | <30 sec | Health check probes |
| Error rate spike | <2 min | SLO alerts |
| Anomaly detection | <5 min | Stddev alerts |

### False Positive Rate

- **Target**: <1%
- **Method**: Appropriate `for` durations and thresholds
- **Verification**: Alert history analysis

### Alert Delivery

- **Target**: 100% for critical alerts
- **Channels**:
  - PagerDuty (critical)
  - Slack (warning)
  - Email (info)
- **Verification**: Test alerts weekly

### Dashboard Performance

- **Load time**: <2 seconds
- **Query time**: <1 second per panel
- **Auto-refresh**: Every 5 minutes
- **Data retention**: 15 days

---

## Best Practices

### 1. Metric Naming

Follow Prometheus conventions:
```
<namespace>_<subsystem>_<name>_<unit>

Examples:
- tracertm_request_duration_seconds
- tracertm_users_active_total
- tracertm_cache_hits_total
```

### 2. Label Cardinality

Keep label cardinality low (<100 values):

**Good**:
```go
.WithLabelValues("items", "GET", "200")  // service, method, status
```

**Bad**:
```go
.WithLabelValues(itemID)  // Unique per item (high cardinality!)
```

### 3. Histogram Buckets

Choose appropriate buckets for your use case:

```go
// For API latency (milliseconds to seconds)
Buckets: []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10}

// For session duration (minutes to hours)
Buckets: []float64{60, 300, 600, 1800, 3600, 7200, 14400}
```

### 4. Dashboard Design

- **One metric per panel** (clear focus)
- **Consistent colors** (green=good, yellow=warning, red=critical)
- **Cross-dashboard links** (easy navigation)
- **Time range selectors** (flexibility)
- **Alert annotations** (context)

### 5. Alert Tuning

- Start conservative (high thresholds)
- Monitor false positive rate
- Adjust `for` duration to reduce noise
- Use multi-window multi-burn-rate for SLOs
- Document runbooks for all alerts

---

## Resources

### Documentation

- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/
- **Web Vitals**: https://web.dev/vitals/
- **SLO Alerting**: https://sre.google/workbook/alerting-on-slos/

### Tools

- **Grafana Cloud**: https://grafana.com/products/cloud/ (for production)
- **PagerDuty**: https://www.pagerduty.com/
- **Slack Webhooks**: https://api.slack.com/messaging/webhooks

### Internal

- **Runbooks**: https://docs.tracertm.com/runbooks/ (TODO: create)
- **On-call Schedule**: https://docs.tracertm.com/oncall/ (TODO: create)
- **Incident Response**: https://docs.tracertm.com/incidents/ (TODO: create)

---

## Success Criteria

✅ **Detection Time**: <5 minutes for performance regressions
✅ **False Positive Rate**: <1% on alert triggers
✅ **Alert Delivery**: 100% critical alert delivery
✅ **Dashboard Load**: <2 seconds
✅ **Data Retention**: 15 days of metrics
✅ **Coverage**: Frontend, backend, infrastructure, business metrics

---

## Next Steps

1. **Production Deployment**
   - Deploy to Grafana Cloud or self-hosted
   - Configure PagerDuty integration
   - Set up on-call rotation

2. **Advanced Monitoring**
   - Distributed tracing (Jaeger/Tempo)
   - Log aggregation (Loki)
   - Synthetic monitoring (uptime checks)

3. **Optimization**
   - Review and optimize expensive queries
   - Implement recording rules
   - Tune alert thresholds based on data

4. **Documentation**
   - Create runbooks for all alerts
   - Document incident response procedures
   - Train team on monitoring tools

---

**Last Updated**: 2026-02-01
**Version**: 1.0
**Maintainer**: TraceRTM Dev Team
