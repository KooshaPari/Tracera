# TraceRTM Monitoring Guide

This guide explains how to use the Grafana dashboards and monitoring system for TraceRTM.

## Overview

TraceRTM uses a comprehensive monitoring stack:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Exporters**: Specialized metric collectors for PostgreSQL, Redis, and system resources
- **Custom Metrics**: Application-specific metrics from Go and Python backends

## Quick Start

### Starting the Monitoring Stack

The monitoring stack is integrated into the process-compose setup:

```bash
# Start all services including monitoring
make dev

# Or start with TUI
make dev-tui
```

### Accessing Dashboards

- **Grafana UI**: http://localhost:3000
  - Username: `admin`
  - Password: `admin` (change in production)
- **Prometheus UI**: http://localhost:9090

### Available Dashboards

1. **Application Metrics** - API performance and behavior
2. **Infrastructure Metrics** - System resources and databases
3. **Business Metrics** - User activity and feature usage
4. **SLO Dashboard** - Service Level Objectives and reliability

## Dashboard Details

### 1. Application Metrics Dashboard

**Purpose**: Monitor API performance, latency, error rates, and throughput.

**Key Panels**:

- **API Request Rate**: Requests per second by endpoint and method
  - Shows traffic patterns across Go and Python backends
  - Useful for identifying popular endpoints

- **API Latency (p50, p95, p99)**: Response time percentiles
  - p50: Median response time
  - p95: 95th percentile (5% of requests slower)
  - p99: 99th percentile (1% of requests slower)
  - Target: p95 < 500ms

- **Error Rate by Endpoint**: 4xx and 5xx errors per second
  - Alerts when error rate exceeds threshold
  - Broken down by endpoint for debugging

- **Success Rate**: Percentage of successful requests
  - Green: >99%, Yellow: 95-99%, Red: <95%

- **Database Query Duration**: Average query execution time
  - Identifies slow database operations
  - Broken down by operation type

- **Cache Hit Rate**: Redis cache effectiveness
  - Target: >80% hit rate
  - Low hit rate indicates cache tuning needed

- **Active Goroutines/Threads**: Concurrency metrics
  - High values may indicate goroutine leaks

- **WebSocket Connections**: Real-time connection metrics
  - Active connections, messages sent/received

- **Temporal Workflow Metrics**: Workflow execution stats
  - Started, completed, failed workflows
  - Active workflow count

- **Top 10 Slowest Endpoints**: Table of endpoints needing optimization

**Alert Rules**:
- High Error Rate: Triggers when 5xx errors exceed 10/sec

### 2. Infrastructure Metrics Dashboard

**Purpose**: Monitor system resources, databases, and infrastructure health.

**Key Panels**:

- **CPU Usage**: System and process CPU utilization
  - Alert threshold: 80%
  - Shows Go backend, Python backend, and system CPU

- **Memory Usage**: RAM consumption
  - System memory percentage
  - Process resident memory (Go, Python)
  - Go heap allocation

- **Disk I/O**: Read/write throughput
  - Identifies disk bottlenecks
  - Per-device breakdown

- **Network Traffic**: Receive/transmit bandwidth
  - Monitors network utilization

- **PostgreSQL Connections**: Database connection pool
  - Active connections vs max connections
  - High usage indicates need for connection pool tuning

- **PostgreSQL Transaction Rate**: Commits and rollbacks
  - High rollback rate indicates application issues

- **PostgreSQL Cache Hit Rate**: Buffer cache effectiveness
  - Target: >95%
  - Low hit rate indicates need for more shared_buffers

- **Redis Memory Usage**: Cache memory consumption
  - Used memory vs max memory
  - Prevents out-of-memory errors

- **Redis Operations**: Command throughput
  - Commands/sec, hits/sec, misses/sec

- **Redis Hit Rate**: Cache effectiveness
  - Target: >80%

- **File Descriptors**: Open file descriptor count
  - Prevents file descriptor exhaustion

- **Garbage Collection (Go)**: GC performance
  - GC duration and frequency
  - High values indicate memory pressure

**Alert Rules**:
- High CPU Usage: Triggers when CPU exceeds 80% for 5 minutes

### 3. Business Metrics Dashboard

**Purpose**: Track user activity, feature usage, and business KPIs.

**Key Panels**:

- **Active Users (Last 24h)**: Unique user count
  - Green: >50 users, Yellow: 10-50, Red: <10

- **Total API Requests (Last 24h)**: Request volume
  - Overall system usage metric

- **Feature Usage Distribution**: Pie chart of feature usage
  - Identifies most-used features
  - Guides development priorities

- **Project Creation Rate**: Projects created per hour
  - Measures user onboarding and activity

- **Item Creation Rate**: Items created by type
  - Requirements, test cases, defects per hour
  - Indicates development activity

- **Test Execution Rate**: Test runs per hour
  - Passed, failed, skipped tests
  - Quality assurance activity metric

- **Test Pass Rate (Last 24h)**: Test success percentage
  - Green: >95%, Yellow: 80-95%, Red: <80%

- **Traceability Link Creation**: Links created per hour
  - Measures traceability coverage growth

- **Total Projects**: Current project count

- **Coverage Percentage**: Average test coverage
  - Green: >80%, Yellow: 60-80%, Red: <60%

- **Integration Activity**: Sync activity by integration
  - Jira, GitHub, Figma syncs per hour

- **User Session Duration**: Session length percentiles
  - p50, p95, p99 session duration
  - User engagement metric

- **Top 10 Most Active Projects**: Table of high-activity projects

**Template Variables**:
- `project`: Filter metrics by specific project(s)

### 4. SLO Dashboard

**Purpose**: Track Service Level Objectives (SLOs) and Service Level Indicators (SLIs) for reliability engineering.

**Key Concepts**:

- **SLO (Service Level Objective)**: Target reliability goal (e.g., 99.9% availability)
- **SLI (Service Level Indicator)**: Measured metric (e.g., actual availability)
- **Error Budget**: Allowed downtime before SLO breach (0.1% for 99.9% SLO)

**Key Panels**:

- **Availability SLO (99.9%)**: 30-day availability
  - Calculation: (non-5xx requests / total requests) × 100
  - Green: ≥99.9%, Yellow: ≥99%, Red: <99%

- **Latency SLO (95th %ile < 500ms)**: 30-day p95 latency
  - Green: <500ms, Yellow: 500-1000ms, Red: >1000ms

- **Error Budget Remaining (30d)**: Available error budget
  - 100% = no errors, 0% = SLO breach
  - Green: >50%, Yellow: 20-50%, Red: <20%

- **Success Rate (Last Hour)**: Short-term availability
  - Real-time health indicator

- **Request Success Rate (Rolling 7d)**: 7-day availability trend
  - Shows SLO target line (99.9%)

- **Latency Percentiles (Rolling 7d)**: 7-day latency trend
  - p50, p95, p99 with 500ms SLO target

- **Error Budget Burn Rate**: Rate of error budget consumption
  - 1h, 6h, 24h burn rates
  - >10x normal burn rate triggers alert
  - 1.0 = normal burn (will exhaust budget in 30 days)
  - 10.0 = 10x burn (will exhaust in 3 days)

- **Database Query SLI**: Database reliability
  - Success rate and p95 latency

- **API Endpoint Availability by Path**: Per-endpoint availability
  - Identifies problematic endpoints

- **WebSocket Connection Uptime**: WebSocket reliability
  - Connection stability percentage

- **Temporal Workflow Success Rate**: Workflow reliability
  - Target: 99% success rate

- **SLO Compliance Summary (Last 30 Days)**: Table of SLO status

**Alert Rules**:
- High Error Budget Burn: Triggers when 1h burn rate exceeds 10x normal

**Template Variables**:
- `slo_window`: Time window for SLO calculation (1h, 6h, 24h, 7d, 30d)

## Metrics Reference

### Application Metrics

#### HTTP Metrics (Go Backend)

```promql
# Request rate
rate(http_requests_total{job="go-backend"}[5m])

# Latency percentiles
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status_code=~"5.."}[5m])

# Success rate
rate(http_requests_total{status_code!~"5.."}[5m]) / rate(http_requests_total[5m])
```

#### Database Metrics

```promql
# Query duration
rate(db_query_duration_seconds_sum[5m]) / rate(db_query_duration_seconds_count[5m])

# Connection pool
pg_stat_database_numbackends{datname="tracertm"}
```

#### Cache Metrics

```promql
# Hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))

# Redis hit rate
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
```

#### WebSocket Metrics

```promql
# Active connections
websocket_connections_active

# Message rate
rate(websocket_messages_sent_total[5m])
```

#### Temporal Metrics

```promql
# Workflow rate
rate(temporal_workflow_started_total[5m])

# Active workflows
temporal_workflow_active
```

### Infrastructure Metrics

#### CPU

```promql
# System CPU
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Process CPU
rate(process_cpu_seconds_total[5m]) * 100
```

#### Memory

```promql
# System memory
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# Process memory
process_resident_memory_bytes

# Go heap
go_memstats_heap_alloc_bytes
```

#### Disk

```promql
# I/O rate
rate(node_disk_read_bytes_total[5m])
rate(node_disk_written_bytes_total[5m])
```

#### Network

```promql
# Traffic
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

### Business Metrics

#### Users

```promql
# Active users
count(count by (user_id) (increase(http_requests_total[24h])))
```

#### Features

```promql
# Feature usage
rate(feature_usage_total[5m])
```

#### Items

```promql
# Creation rate
rate(items_created_total[5m])

# By type
rate(items_created_total{type="requirement"}[5m])
```

#### Tests

```promql
# Execution rate
rate(test_executions_total[5m])

# Pass rate
rate(test_executions_total{status="passed"}[5m]) / rate(test_executions_total[5m])
```

## Alert Configuration

Grafana dashboards include built-in alerts. Configure notification channels:

1. Navigate to **Alerting** > **Contact Points** in Grafana
2. Add notification channel (Email, Slack, PagerDuty, etc.)
3. Configure notification policies
4. Test notifications

### Recommended Alerts

- **High Error Rate**: >10 errors/sec for 5 minutes
- **High CPU Usage**: >80% for 5 minutes
- **High Error Budget Burn**: >10x normal burn rate
- **Low Availability**: <99% for 15 minutes
- **High Latency**: p95 >1000ms for 10 minutes

## Best Practices

### Dashboard Usage

1. **Start with SLO Dashboard**: Get overall health status
2. **Drill down with Application Metrics**: Investigate specific issues
3. **Check Infrastructure Metrics**: Rule out resource constraints
4. **Review Business Metrics**: Understand user impact

### Performance Monitoring

1. **Set baseline metrics**: Record normal operating values
2. **Monitor trends**: Look for gradual degradation
3. **Compare periods**: Use time range selector
4. **Use annotations**: Mark deployments and incidents

### Troubleshooting

1. **High latency**:
   - Check Database Query Duration panel
   - Review cache hit rates
   - Check CPU and memory usage
   - Look at slowest endpoints table

2. **High error rate**:
   - Check Error Rate by Endpoint
   - Review application logs
   - Check database connection pool
   - Verify external integrations

3. **Low availability**:
   - Check SLO Dashboard for error budget
   - Review error budget burn rate
   - Identify failing endpoints
   - Check infrastructure health

4. **Resource exhaustion**:
   - Monitor CPU, memory, disk I/O
   - Check file descriptors
   - Review garbage collection metrics
   - Check database connections

## Customization

### Adding Custom Metrics

1. **Instrument code** with Prometheus client libraries
2. **Expose /metrics endpoint** in your service
3. **Add scrape config** to `monitoring/prometheus.yml`
4. **Create dashboard panel** using PromQL query

### Creating Custom Dashboards

1. **UI Method**:
   - Click **+ Create** > **Dashboard** in Grafana
   - Add panels with queries
   - Save dashboard
   - Export JSON to `monitoring/dashboards/`

2. **JSON Method**:
   - Copy existing dashboard JSON
   - Modify panels and queries
   - Save to `monitoring/dashboards/`
   - Restart Grafana or wait for provisioning

### Dashboard Variables

Add template variables for filtering:

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

## Production Deployment

### Configuration Changes

1. **Update grafana.ini**:
   ```ini
   [server]
   root_url = https://grafana.yourdomain.com/

   [security]
   admin_password = <strong-password>

   [auth]
   disable_login_form = false

   [auth.anonymous]
   enabled = false
   ```

2. **Configure persistent storage**:
   - Use PostgreSQL instead of SQLite
   - Mount persistent volumes for data

3. **Enable HTTPS**:
   - Configure TLS certificates
   - Update Caddy reverse proxy

### Prometheus Configuration

1. **Configure retention**:
   ```bash
   prometheus --storage.tsdb.retention.time=30d
   ```

2. **Enable remote write** for long-term storage (optional):
   ```yaml
   remote_write:
     - url: "https://prometheus-remote-storage.example.com/api/v1/write"
   ```

### High Availability

1. **Run multiple Prometheus instances**
2. **Configure Grafana HA**:
   - Use external database
   - Load balance with multiple replicas
3. **Use Prometheus federation** for centralized monitoring

## Maintenance

### Regular Tasks

- **Weekly**: Review SLO compliance
- **Monthly**: Audit dashboard usage and cleanup unused panels
- **Quarterly**: Review alert thresholds and adjust
- **As needed**: Update dashboards for new features

### Backup

```bash
# Backup Grafana database
cp .grafana/grafana.db .grafana/grafana.db.backup

# Backup dashboards
tar -czf dashboards-backup.tar.gz monitoring/dashboards/

# Backup Prometheus data
tar -czf prometheus-backup.tar.gz .prometheus/
```

### Upgrades

1. **Backup** existing configuration and data
2. **Review** release notes for breaking changes
3. **Test** in non-production environment
4. **Upgrade** Grafana and Prometheus
5. **Verify** dashboards and alerts work

## Troubleshooting

### Dashboard Not Loading

- Check Grafana logs: `.grafana/logs/grafana.log`
- Verify Prometheus datasource: **Configuration** > **Data Sources**
- Test Prometheus connectivity: `curl http://localhost:9090/-/ready`

### Missing Metrics

- Check exporter status in process-compose
- Verify scrape targets: http://localhost:9090/targets
- Check metric names: http://localhost:9090/api/v1/label/__name__/values

### Slow Queries

- Reduce time range
- Increase scrape interval in `prometheus.yml`
- Optimize PromQL queries (avoid high cardinality)
- Enable query caching in Grafana

## Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Grafana Best Practices**: https://grafana.com/docs/grafana/latest/best-practices/
- **SLO Engineering**: https://sre.google/workbook/implementing-slos/

## Support

For monitoring issues:

1. Check logs in `.grafana/logs/` and `.process-compose/logs/`
2. Verify all exporters are running: `process-compose process list`
3. Review Prometheus targets: http://localhost:9090/targets
4. Consult this documentation
5. Review Grafana community forums

---

**Last Updated**: 2026-02-01
**Version**: 1.0.0
