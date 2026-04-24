# Grafana Dashboards

This directory contains Grafana dashboard definitions for TraceRTM monitoring.

## Dashboard Files

### 1. application-metrics.json

**Purpose**: Monitor API performance, latency, error rates, and application behavior.

**Key Metrics**:
- API request rate and latency (p50, p95, p99)
- Error rates by endpoint (4xx, 5xx)
- Success rate and error budget
- Database query duration
- Cache hit rates
- WebSocket connections
- Temporal workflow metrics
- Goroutine/thread counts

**Refresh**: 10 seconds

**Use Cases**:
- Performance monitoring
- Error tracking
- API optimization
- Capacity planning

### 2. infrastructure-metrics.json

**Purpose**: Monitor system resources, databases, and infrastructure health.

**Key Metrics**:
- CPU and memory usage (system + processes)
- Disk I/O and network traffic
- PostgreSQL: connections, transactions, cache hit rate
- Redis: memory, operations, hit rate
- File descriptors
- Garbage collection (Go)

**Refresh**: 30 seconds

**Use Cases**:
- Resource monitoring
- Database tuning
- Capacity planning
- Infrastructure troubleshooting

### 3. business-metrics.json

**Purpose**: Track user activity, feature usage, and business KPIs.

**Key Metrics**:
- Active users and API requests
- Feature usage distribution
- Project and item creation rates
- Test execution and pass rates
- Traceability link creation
- Coverage percentage
- Integration activity
- User session duration

**Refresh**: 1 minute

**Use Cases**:
- User engagement tracking
- Feature adoption analysis
- Development activity monitoring
- Quality metrics

### 4. slo-dashboard.json

**Purpose**: Track Service Level Objectives (SLOs) and Service Level Indicators (SLIs).

**Key Metrics**:
- Availability SLO (99.9% target)
- Latency SLO (p95 < 500ms)
- Error budget tracking and burn rate
- Success rates by component
- SLO compliance summary

**Refresh**: 1 minute

**Use Cases**:
- Reliability engineering
- SLO compliance tracking
- Error budget management
- Incident detection

## Dashboard Structure

All dashboards follow this JSON structure:

```json
{
  "dashboard": {
    "id": null,
    "uid": "unique-dashboard-id",
    "title": "Dashboard Title",
    "tags": ["tag1", "tag2"],
    "timezone": "browser",
    "schemaVersion": 38,
    "version": 0,
    "refresh": "10s",
    "panels": [...],
    "templating": {...},
    "time": {...},
    "timepicker": {...}
  }
}
```

### Panel Types

- **graph**: Time-series line charts
- **stat**: Single-value statistics with thresholds
- **table**: Tabular data display
- **piechart**: Pie/donut charts for distributions
- **row**: Collapsible section headers

### Common PromQL Patterns

#### Rate Calculations

```promql
# Requests per second
rate(http_requests_total[5m])

# With filtering
rate(http_requests_total{job="go-backend",status_code="200"}[5m])
```

#### Percentiles

```promql
# 95th percentile latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

#### Success Rate

```promql
# Percentage of successful requests
sum(rate(http_requests_total{status_code!~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

#### Aggregations

```promql
# Sum by label
sum by (endpoint) (rate(http_requests_total[5m]))

# Average by label
avg by (instance) (rate(cpu_usage[5m]))
```

## Provisioning

Dashboards are automatically loaded by Grafana via provisioning:

```yaml
# monitoring/grafana/provisioning/dashboards/default.yaml
apiVersion: 1
providers:
  - name: 'TraceRTM Dashboards'
    folder: ''
    type: file
    options:
      path: monitoring/dashboards
```

## Customization

### Editing Dashboards

#### Via Grafana UI

1. Open dashboard in Grafana
2. Click **Dashboard settings** (gear icon)
3. Make changes
4. Click **Save dashboard**
5. Export JSON: **Dashboard settings** > **JSON Model**
6. Copy JSON to dashboard file

#### Via JSON Files

1. Edit dashboard JSON file directly
2. Update panel queries, titles, thresholds
3. Restart Grafana or wait for provisioning refresh (10s)

### Adding Panels

```json
{
  "id": 100,
  "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
  "type": "graph",
  "title": "New Panel",
  "targets": [
    {
      "expr": "your_promql_query",
      "legendFormat": "{{label}}",
      "refId": "A"
    }
  ],
  "yaxes": [
    {"format": "short", "label": "Y-Axis"}
  ]
}
```

### Adding Alerts

```json
{
  "alert": {
    "name": "Alert Name",
    "conditions": [
      {
        "evaluator": {"params": [threshold], "type": "gt"},
        "query": {"params": ["A", "5m", "now"]},
        "reducer": {"params": [], "type": "avg"},
        "type": "query"
      }
    ],
    "frequency": "1m",
    "handler": 1
  }
}
```

### Template Variables

Add filters to dashboards:

```json
{
  "templating": {
    "list": [
      {
        "name": "environment",
        "type": "query",
        "query": "label_values(http_requests_total, environment)",
        "datasource": "Prometheus",
        "refresh": 1,
        "multi": true,
        "includeAll": true
      }
    ]
  }
}
```

Use in queries: `http_requests_total{environment=~"$environment"}`

## Testing

### Validate JSON

```bash
# Check JSON syntax
jq empty monitoring/dashboards/application-metrics.json

# Pretty print
jq . monitoring/dashboards/application-metrics.json
```

### Import to Grafana

1. **Via UI**:
   - **+ Create** > **Import**
   - Paste JSON or upload file
   - Select datasource: Prometheus
   - Click **Import**

2. **Via API**:
   ```bash
   curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
     -H "Content-Type: application/json" \
     -d @monitoring/dashboards/application-metrics.json
   ```

## Best Practices

### Dashboard Design

- **Keep panels focused**: One metric per panel
- **Use consistent colors**: Green for good, yellow for warning, red for critical
- **Add descriptions**: Help text for complex metrics
- **Set appropriate refresh rates**: Balance freshness vs load
- **Use template variables**: Enable filtering
- **Group related panels**: Use rows for organization

### PromQL Queries

- **Use rate() for counters**: `rate(http_requests_total[5m])`
- **Use irate() for volatile metrics**: `irate(cpu_usage[1m])`
- **Avoid high cardinality**: Don't group by user_id
- **Use recording rules**: Pre-calculate expensive queries
- **Set appropriate ranges**: Match dashboard refresh rate

### Performance

- **Limit time range**: Default to last 6-24 hours
- **Use smaller intervals**: Reduce scrape frequency for less critical metrics
- **Enable query caching**: Configure in Grafana settings
- **Use recording rules**: Pre-aggregate complex queries in Prometheus

## Troubleshooting

### Dashboard Not Loading

- Check JSON syntax: `jq empty dashboard.json`
- Verify provisioning config: `monitoring/grafana/provisioning/dashboards/default.yaml`
- Check Grafana logs: `.grafana/logs/grafana.log`
- Restart Grafana: `process-compose process restart grafana`

### No Data in Panels

- Verify Prometheus datasource is configured
- Check metric names: http://localhost:9090/api/v1/label/__name__/values
- Test query in Prometheus UI: http://localhost:9090/graph
- Verify scrape targets: http://localhost:9090/targets

### Slow Loading

- Reduce time range
- Simplify PromQL queries
- Check Prometheus performance
- Enable query caching
- Reduce panel refresh rates

## Development Workflow

### Creating New Dashboard

1. **Design in Grafana UI**:
   - Create dashboard with panels
   - Configure queries and thresholds
   - Test with real data

2. **Export JSON**:
   - **Dashboard settings** > **JSON Model**
   - Copy entire JSON

3. **Save to File**:
   ```bash
   # Create new dashboard file
   cat > monitoring/dashboards/my-dashboard.json
   # Paste JSON
   # Ctrl+D to save
   ```

4. **Format JSON**:
   ```bash
   jq . monitoring/dashboards/my-dashboard.json > temp.json
   mv temp.json monitoring/dashboards/my-dashboard.json
   ```

5. **Test Provisioning**:
   - Wait 10 seconds or restart Grafana
   - Verify dashboard appears in Grafana

### Updating Existing Dashboard

1. **Edit in Grafana or JSON file**
2. **Test changes**
3. **Export JSON** if edited in UI
4. **Commit changes** to version control

## Version Control

All dashboards are version controlled:

```bash
# Check changes
git diff monitoring/dashboards/

# Commit updates
git add monitoring/dashboards/
git commit -m "Update application metrics dashboard"
```

## References

- [Grafana Dashboard Documentation](https://grafana.com/docs/grafana/latest/dashboards/)
- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)

---

**Last Updated**: 2026-02-01
**Version**: 1.0.0
