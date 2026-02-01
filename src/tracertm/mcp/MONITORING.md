# MCP Monitoring and Telemetry Guide

## Overview

The TraceRTM MCP server includes comprehensive monitoring and telemetry capabilities:

- **OpenTelemetry Tracing**: Distributed tracing for all tool calls
- **Prometheus Metrics**: Production-ready metrics for monitoring
- **Structured Logging**: JSON-formatted logs for aggregation
- **Enhanced Errors**: LLM-friendly error messages with recovery hints
- **Performance Monitoring**: Automatic detection of slow operations

## Quick Start

### Enable All Monitoring Features

```bash
# Enable all monitoring features (default: enabled)
export TRACERTM_MCP_TELEMETRY_ENABLED=true
export TRACERTM_MCP_METRICS_ENABLED=true
export TRACERTM_MCP_PERF_MONITORING=true
export TRACERTM_MCP_ENHANCED_ERRORS=true
export TRACERTM_MCP_STRUCTURED_LOGGING=true
```

### Start Metrics Server

```python
from tracertm.mcp.metrics_endpoint import start_metrics_server

# Start metrics server on port 9090
server = start_metrics_server(host="0.0.0.0", port=9090)
```

Access metrics at: `http://localhost:9090/metrics`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TRACERTM_MCP_TELEMETRY_ENABLED` | `true` | Enable OpenTelemetry tracing |
| `TRACERTM_MCP_METRICS_ENABLED` | `true` | Enable Prometheus metrics |
| `TRACERTM_MCP_PERF_MONITORING` | `true` | Enable performance monitoring |
| `TRACERTM_MCP_ENHANCED_ERRORS` | `true` | Enable LLM-friendly errors |
| `TRACERTM_MCP_STRUCTURED_LOGGING` | `true` | Enable structured JSON logging |
| `TRACERTM_MCP_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TRACERTM_MCP_JSON_LOGS` | `true` | Output logs in JSON format |
| `TRACERTM_MCP_LOG_FILE` | None | Optional log file path |
| `TRACERTM_MCP_TRACK_PAYLOAD_SIZE` | `true` | Track request/response sizes |
| `TRACERTM_MCP_SLOW_THRESHOLD` | `5.0` | Threshold for slow call warning (seconds) |
| `TRACERTM_MCP_VERY_SLOW_THRESHOLD` | `30.0` | Threshold for very slow call alert (seconds) |
| `TRACERTM_MCP_INCLUDE_STACK_TRACES` | `false` | Include stack traces in errors |

## Metrics

### Available Metrics

#### Tool Execution Duration
```
mcp_tool_duration_seconds{tool_name="create_project", status="success"}
```
Histogram of tool execution times in seconds.

**Labels:**
- `tool_name`: Name of the MCP tool
- `status`: `success` or `error`

**Buckets:** 5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s, 30s, 60s

#### Tool Call Counter
```
mcp_tool_calls_total{tool_name="create_project", status="success"}
```
Total number of tool calls.

**Labels:**
- `tool_name`: Name of the MCP tool
- `status`: `success` or `error`

#### Tool Errors by Type
```
mcp_tool_errors_total{tool_name="create_project", error_type="ValidationError"}
```
Total number of errors grouped by error type.

**Labels:**
- `tool_name`: Name of the MCP tool
- `error_type`: Exception class name

#### Payload Size
```
mcp_tool_payload_size_bytes{tool_name="query_items"}
```
Histogram of request payload sizes in bytes.

**Labels:**
- `tool_name`: Name of the MCP tool

**Buckets:** 100B, 500B, 1KB, 5KB, 10KB, 50KB, 100KB, 500KB, 1MB

#### Active Tool Calls
```
mcp_active_tool_calls{tool_name="detect_cycles"}
```
Current number of in-flight tool calls.

**Labels:**
- `tool_name`: Name of the MCP tool

#### Rate Limit Violations
```
mcp_rate_limit_hits_total{user_key="user123", limit_type="per_minute"}
```
Total number of rate limit violations.

**Labels:**
- `user_key`: User identifier
- `limit_type`: `per_minute` or `per_hour`

#### Auth Failures
```
mcp_auth_failures_total{failure_type="expired_token"}
```
Total number of authentication failures.

**Labels:**
- `failure_type`: Type of failure (expired_token, missing_scope, etc.)

### Querying Metrics with Prometheus

#### Average Tool Duration
```promql
rate(mcp_tool_duration_seconds_sum[5m]) / rate(mcp_tool_duration_seconds_count[5m])
```

#### Error Rate by Tool
```promql
sum(rate(mcp_tool_calls_total{status="error"}[5m])) by (tool_name)
```

#### P95 Tool Latency
```promql
histogram_quantile(0.95, rate(mcp_tool_duration_seconds_bucket[5m]))
```

#### Top 5 Slowest Tools
```promql
topk(5, avg(rate(mcp_tool_duration_seconds_sum[5m])) by (tool_name) / avg(rate(mcp_tool_duration_seconds_count[5m])) by (tool_name))
```

#### Tool Success Rate
```promql
sum(rate(mcp_tool_calls_total{status="success"}[5m])) by (tool_name) / sum(rate(mcp_tool_calls_total[5m])) by (tool_name) * 100
```

## OpenTelemetry Tracing

### Span Attributes

Every tool call creates a span with the following attributes:

- `mcp.tool.name`: Tool name
- `mcp.tool.start_time`: Start timestamp
- `mcp.tool.arg_count`: Number of arguments
- `mcp.tool.payload_size_bytes`: Request payload size
- `mcp.tool.duration_seconds`: Execution duration
- `mcp.tool.success`: Boolean success flag
- `mcp.tool.error.type`: Error type if failed
- `mcp.tool.error.message`: Error message if failed
- `mcp.auth.subject`: User ID (if authenticated)
- `mcp.auth.client_id`: Client ID (if authenticated)

### Viewing Traces

Traces are exported to console by default. To export to a tracing backend:

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure OTLP exporter for Jaeger/Tempo
exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
provider.add_span_processor(BatchSpanProcessor(exporter))
```

## Structured Logging

### Log Format

When structured logging is enabled, all logs are output in JSON format:

```json
{
  "timestamp": 1706745600.123,
  "timestamp_iso": "2025-01-30T12:00:00",
  "level": "INFO",
  "logger": "tracertm.mcp",
  "event": "tool_call_succeeded",
  "tool": "create_project",
  "arg_count": 2,
  "duration_seconds": 0.042,
  "success": true
}
```

### Log Events

#### Tool Call Success
```json
{
  "event": "tool_call_succeeded",
  "tool": "query_items",
  "arg_count": 3,
  "duration_seconds": 0.156,
  "success": true
}
```

#### Tool Call Failure
```json
{
  "event": "tool_call_failed",
  "tool": "create_link",
  "arg_count": 2,
  "duration_seconds": 0.023,
  "success": false,
  "error": "Item not found"
}
```

#### Slow Operation Warning
```json
{
  "event": "slow_operation",
  "operation": "detect_cycles",
  "duration_seconds": 7.823,
  "slow": true
}
```

#### Rate Limit Warning
```json
{
  "event": "rate_limit_warning",
  "user_key": "user123",
  "limit_type": "per_minute",
  "current_count": 48,
  "limit": 60,
  "exceeded": false
}
```

### Structured Logger API

```python
from tracertm.mcp.logging_config import get_structured_logger

logger = get_structured_logger()

# Log tool call
logger.log_tool_call(
    tool_name="create_project",
    arguments={"name": "MyProject"},
    duration=0.042,
    success=True
)

# Log performance
logger.log_performance(
    operation="database_query",
    duration=0.156,
    threshold=1.0
)

# Log error
logger.log_error(
    error=exception,
    context={"tool": "create_link", "item_id": "123"}
)

# Log auth event
logger.log_auth(
    action="permission_check",
    user_id="user123",
    success=True
)
```

## Enhanced Error Messages

### LLM-Friendly Errors

All errors include:
- **Clear message**: Human-readable error description
- **Recovery hint**: Suggested action to resolve the error
- **Context**: Relevant data (sanitized)

#### Example Error Response

```python
{
  "error": "No project is currently selected.",
  "type": "ProjectNotSelectedError",
  "recovery_hint": "Use create_project() to create a new project, or select_project(project_id='...') to select an existing one. Use list_projects() to see available projects.",
  "context": {}
}
```

### Common Errors

#### ProjectNotSelectedError
**When:** No project is selected
**Recovery:** Use `create_project()` or `select_project()`

#### ItemNotFoundError
**When:** Item doesn't exist
**Recovery:** Use `query_items()` to search or `create_item()` to create

#### DatabaseError
**When:** Database operation fails
**Recovery:** Check database connection with `rtm config show`

#### ValidationError
**When:** Invalid input data
**Recovery:** Check tool documentation for valid values

#### AuthorizationError
**When:** Insufficient permissions
**Recovery:** Request access or use token with appropriate scopes

#### RateLimitError
**When:** Too many requests
**Recovery:** Wait before making more requests (includes wait time)

## Grafana Dashboard

### Sample Dashboard Configuration

```json
{
  "dashboard": {
    "title": "TraceRTM MCP Monitoring",
    "panels": [
      {
        "title": "Tool Call Rate",
        "targets": [
          {
            "expr": "sum(rate(mcp_tool_calls_total[5m])) by (tool_name)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "sum(rate(mcp_tool_calls_total{status=\"error\"}[5m]))"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(mcp_tool_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Active Calls",
        "targets": [
          {
            "expr": "sum(mcp_active_tool_calls)"
          }
        ]
      }
    ]
  }
}
```

### Alert Rules

#### High Error Rate
```yaml
alert: HighErrorRate
expr: sum(rate(mcp_tool_calls_total{status="error"}[5m])) > 0.1
annotations:
  summary: "High error rate detected"
  description: "Error rate is {{ $value }} errors/sec"
```

#### Slow Tool Execution
```yaml
alert: SlowToolExecution
expr: histogram_quantile(0.95, rate(mcp_tool_duration_seconds_bucket[5m])) > 30
annotations:
  summary: "Tools executing slowly"
  description: "P95 latency is {{ $value }}s"
```

#### Rate Limit Violations
```yaml
alert: RateLimitViolations
expr: rate(mcp_rate_limit_hits_total[5m]) > 1
annotations:
  summary: "Rate limits being hit"
  description: "{{ $value }} rate limit violations/sec"
```

## Performance Baselines

### Expected Performance

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| create_project | 50ms | 150ms | 300ms |
| list_projects | 20ms | 50ms | 100ms |
| create_item | 30ms | 100ms | 200ms |
| query_items | 100ms | 500ms | 1s |
| create_link | 25ms | 75ms | 150ms |
| detect_cycles | 200ms | 2s | 5s |
| get_trace_matrix | 500ms | 5s | 10s |

### Thresholds

- **Warning threshold**: 5 seconds
- **Alert threshold**: 30 seconds
- **Timeout**: 60 seconds (configurable per tool)

## Integration Examples

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tracertm-mcp-metrics
spec:
  ports:
  - port: 9090
    targetPort: 9090
    name: metrics
  selector:
    app: tracertm-mcp
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tracertm-mcp
spec:
  selector:
    matchLabels:
      app: tracertm-mcp
  endpoints:
  - port: metrics
    interval: 15s
```

### Docker Compose

```yaml
services:
  tracertm-mcp:
    image: tracertm:latest
    environment:
      - TRACERTM_MCP_METRICS_ENABLED=true
      - TRACERTM_MCP_TELEMETRY_ENABLED=true
    ports:
      - "9090:9090"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9091:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

## Troubleshooting

### Metrics Not Appearing

1. Check metrics server is running:
```bash
curl http://localhost:9090/health
```

2. Verify environment variable:
```bash
echo $TRACERTM_MCP_METRICS_ENABLED
```

3. Check logs for errors:
```bash
tail -f tracertm-mcp.log | grep METRICS
```

### High Memory Usage

If tracking payload sizes, disable for large payloads:
```bash
export TRACERTM_MCP_TRACK_PAYLOAD_SIZE=false
```

### Trace Not Showing

Verify telemetry is enabled and exporter is configured:
```bash
echo $TRACERTM_MCP_TELEMETRY_ENABLED
```

## Best Practices

1. **Enable All Monitoring**: Use all features in production
2. **Set Appropriate Thresholds**: Tune slow thresholds based on your workload
3. **Monitor Error Rates**: Set up alerts for error spikes
4. **Track P95/P99 Latency**: Focus on tail latencies
5. **Review Structured Logs**: Use log aggregation tools
6. **Set Up Dashboards**: Create Grafana dashboards for visibility
7. **Configure Alerts**: Set up alerts for critical metrics
8. **Regular Review**: Review metrics weekly to identify trends

## See Also

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Structured Logging with structlog](https://www.structlog.org/)
