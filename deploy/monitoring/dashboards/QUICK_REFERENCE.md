# Grafana Dashboards Quick Reference

## Access

- **Grafana**: http://localhost:3000
- **Username**: `admin`
- **Password**: `admin`

## Available Dashboards

### 1. Application Metrics
**UID**: `application-metrics`
**URL**: http://localhost:3000/d/application-metrics

**Purpose**: Monitor API performance and application behavior

**Key Panels**:
- API Request Rate → Identify traffic patterns
- API Latency (p95) → Must be <500ms (SLO target)
- Error Rate → Should be minimal
- Success Rate → Target >99%
- Cache Hit Rate → Target >80%

**When to Use**:
- Investigating slow API responses
- Tracking error spikes
- Optimizing endpoint performance
- Monitoring cache effectiveness

**Alerts**: High Error Rate (>10 errors/sec)

---

### 2. Infrastructure Metrics
**UID**: `infrastructure-metrics`
**URL**: http://localhost:3000/d/infrastructure-metrics

**Purpose**: Monitor system resources and database health

**Key Panels**:
- CPU Usage → Alert at >80%
- Memory Usage → Watch for leaks
- PostgreSQL Connections → Monitor pool usage
- Redis Hit Rate → Target >80%
- Disk I/O → Identify bottlenecks

**When to Use**:
- Investigating performance issues
- Capacity planning
- Database tuning
- Resource optimization

**Alerts**: High CPU Usage (>80%)

---

### 3. Business Metrics
**UID**: `business-metrics`
**URL**: http://localhost:3000/d/business-metrics

**Purpose**: Track user activity and feature adoption

**Key Panels**:
- Active Users (24h) → Engagement metric
- Feature Usage → Most popular features
- Test Pass Rate → Quality indicator (target >95%)
- Coverage Percentage → Target >80%
- Integration Activity → Sync health

**When to Use**:
- Product analytics
- Feature adoption tracking
- Quality metrics reporting
- User engagement analysis

**Filters**: Project selector (template variable)

---

### 4. SLO Dashboard
**UID**: `slo-dashboard`
**URL**: http://localhost:3000/d/slo-dashboard

**Purpose**: Service Level Objectives and reliability tracking

**Key Panels**:
- Availability SLO → 99.9% target (30 days)
- Latency SLO → p95 <500ms target
- Error Budget Remaining → >50% is healthy
- Error Budget Burn Rate → <1x is normal

**When to Use**:
- Daily reliability checks
- Incident response
- SLO compliance reporting
- Error budget management

**Alerts**: High Error Budget Burn (>10x normal)

---

## Common Tasks

### Check Overall Health
1. Open **SLO Dashboard**
2. Check Availability SLO (should be green, ≥99.9%)
3. Check Error Budget Remaining (should be >20%)
4. Look for red indicators

### Investigate Performance Issue
1. Open **Application Metrics**
2. Check API Latency panel for spikes
3. Review Error Rate by Endpoint
4. Check Database Query Duration
5. Open **Infrastructure Metrics**
6. Check CPU and Memory usage
7. Review database connection pool

### Monitor User Activity
1. Open **Business Metrics**
2. Review Active Users (24h)
3. Check Feature Usage Distribution
4. Monitor Test Pass Rate
5. Review Integration Activity

### Troubleshoot Errors
1. Open **Application Metrics**
2. Check Error Rate by Endpoint (identify endpoint)
3. Review Success Rate (severity)
4. Open **Infrastructure Metrics**
5. Check database and Redis health
6. Review application logs for details

---

## Dashboard Controls

### Time Range Selector
- **Presets**: Last 5m, 15m, 1h, 6h, 24h, 7d, 30d
- **Custom**: Click "Time range" to set custom range
- **Refresh**: Auto-refresh intervals (5s to 1h)

### Panel Actions
- **Zoom**: Click and drag on graph
- **View**: Click panel title → View
- **Edit**: Click panel title → Edit (requires permissions)
- **Share**: Click panel title → Share → Link or Snapshot

### Variables
- **Project Filter** (Business Metrics): Select specific project(s)
- **SLO Window** (SLO Dashboard): Change time window (1h, 6h, 24h, 7d, 30d)

---

## Alert Status

### Current Alerts
- High Error Rate (Application Metrics)
- High CPU Usage (Infrastructure Metrics)
- High Error Budget Burn (SLO Dashboard)

### Configuring Notifications
1. Navigate to **Alerting** → **Contact Points**
2. Add notification channel (Email, Slack, etc.)
3. Configure notification policies
4. Test notifications

---

## PromQL Quick Reference

### Common Queries

**Request Rate**:
```promql
rate(http_requests_total[5m])
```

**Success Rate**:
```promql
sum(rate(http_requests_total{status_code!~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

**p95 Latency**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Cache Hit Rate**:
```promql
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

### Filters

**By Job**:
```promql
http_requests_total{job="go-backend"}
```

**By Status Code**:
```promql
http_requests_total{status_code=~"5.."}  # 5xx errors
http_requests_total{status_code!~"5.."} # non-5xx
```

**Aggregation**:
```promql
sum by (endpoint) (rate(http_requests_total[5m]))
```

---

## Troubleshooting

### No Data in Panels
1. Check Prometheus is running: http://localhost:9090/targets
2. Verify metric names: http://localhost:9090/api/v1/label/__name__/values
3. Test query in Prometheus UI
4. Check datasource config: **Configuration** → **Data Sources**

### Dashboard Not Loading
1. Check Grafana logs: `.grafana/logs/grafana.log`
2. Verify provisioning: `monitoring/grafana/provisioning/dashboards/default.yaml`
3. Restart Grafana: `process-compose process restart grafana`

### Slow Loading
1. Reduce time range (use last 6h instead of 30d)
2. Reduce refresh rate
3. Check Prometheus performance: http://localhost:9090/tsdb-status

---

## Keyboard Shortcuts

- `d` + `s` - Save dashboard
- `d` + `h` - Dashboard home
- `d` + `k` - Kiosk mode
- `t` + `z` - Zoom out time range
- `t` + `←` - Move time range back
- `t` + `→` - Move time range forward
- `Ctrl` + `s` - Save snapshot
- `?` - Show all keyboard shortcuts

---

## Best Practices

1. **Start with SLO Dashboard** for overall health
2. **Set time range appropriately** (don't always use 30d)
3. **Use template variables** for filtering
4. **Add annotations** for deployments and incidents
5. **Create snapshots** when sharing issues
6. **Set up notifications** for critical alerts
7. **Review dashboards regularly** (daily/weekly)
8. **Update thresholds** as system evolves

---

## Resources

- Full Documentation: `docs/guides/MONITORING.md`
- Dashboard Details: `monitoring/dashboards/README.md`
- Prometheus UI: http://localhost:9090
- Process Status: `process-compose process list`

---

**Last Updated**: 2026-02-01
