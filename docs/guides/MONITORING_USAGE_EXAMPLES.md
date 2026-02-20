# MCP Monitoring - Usage Examples

## Quick Start Examples

### Example 1: Enable All Monitoring (Default)

Monitoring is enabled by default. Just start the MCP server:

```bash
# Start MCP server with default monitoring
rtm-mcp
```

All monitoring features are active:
- ✓ OpenTelemetry tracing
- ✓ Prometheus metrics
- ✓ Performance monitoring
- ✓ Enhanced errors
- ✓ Structured logging

### Example 2: Start Metrics Server

```python
from tracertm.mcp import start_metrics_server

# Start metrics server on port 9090
server = start_metrics_server(host="0.0.0.0", port=9090)

# Metrics available at http://localhost:9090/metrics
# Health check at http://localhost:9090/health
```

### Example 3: Custom Log Level

```bash
# Set custom log level
export TRACERTM_MCP_LOG_LEVEL=DEBUG

# Start server
rtm-mcp
```

### Example 4: Disable Specific Features

```bash
# Disable telemetry but keep metrics
export TRACERTM_MCP_TELEMETRY_ENABLED=false
export TRACERTM_MCP_METRICS_ENABLED=true

rtm-mcp
```

## Using Enhanced Errors

### Example 5: Raising LLM-Friendly Errors

```python
from tracertm.mcp.error_handlers import (
    ProjectNotSelectedError,
    ItemNotFoundError,
    ValidationError,
)

# In your tool implementation
def my_tool(item_id: str):
    # Raise with automatic recovery hint
    if not item_id:
        raise ValidationError(
            field="item_id",
            value=item_id,
            reason="Cannot be empty"
        )

    # Check if item exists
    item = get_item(item_id)
    if not item:
        raise ItemNotFoundError(item_id)

    return item
```

**LLM sees**:
```json
{
  "error": "Item 'abc-123' not found.",
  "type": "ItemNotFoundError",
  "recovery_hint": "Use query_items() to search for items, or create_item() to create a new one.",
  "context": {
    "item_id": "abc-123"
  }
}
```

### Example 6: Custom Error with Recovery Hint

```python
from tracertm.mcp.error_handlers import LLMFriendlyError

class CustomError(LLMFriendlyError):
    def __init__(self, resource: str):
        super().__init__(
            message=f"Resource '{resource}' is temporarily unavailable.",
            recovery_hint="Wait a few moments and try again. If the problem persists, check system status.",
            context={"resource": resource}
        )

# Use it
raise CustomError("database")
```

## Structured Logging

### Example 7: Using Structured Logger

```python
from tracertm.mcp.logging_config import get_structured_logger

logger = get_structured_logger()

# Log tool execution
logger.log_tool_call(
    tool_name="create_project",
    arguments={"name": "MyProject", "description": "..."},
    duration=0.123,
    success=True
)

# Log performance
logger.log_performance(
    operation="database_query",
    duration=0.456,
    threshold=1.0  # Warns if > 1s
)

# Log error with context
try:
    risky_operation()
except Exception as e:
    logger.log_error(
        error=e,
        context={
            "operation": "risky_operation",
            "user_id": "user-123",
            "retry_count": 3
        }
    )

# Log auth event
logger.log_auth(
    action="permission_check",
    user_id="user-123",
    success=True
)

# Log rate limit event
logger.log_rate_limit(
    user_key="user-123",
    limit_type="per_minute",
    current_count=45,
    limit=60
)
```

### Example 8: Configure Logging

```python
from tracertm.mcp.logging_config import configure_structured_logging

# JSON logs to file and console
configure_structured_logging(
    log_level="INFO",
    json_output=True,
    log_file="/var/log/tracertm-mcp.log"
)

# Human-readable logs for development
configure_structured_logging(
    log_level="DEBUG",
    json_output=False  # Console renderer
)
```

## Metrics Collection

### Example 9: Track Custom Metrics

```python
from tracertm.mcp.metrics import (
    tool_duration_seconds,
    tool_calls_total,
    tool_errors_total,
)

# Manual metric tracking
def my_operation():
    import time
    start = time.time()

    try:
        # Do work
        result = perform_operation()

        # Record success
        elapsed = time.time() - start
        tool_duration_seconds.labels(
            tool_name="my_operation",
            status="success"
        ).observe(elapsed)

        tool_calls_total.labels(
            tool_name="my_operation",
            status="success"
        ).inc()

        return result

    except Exception as e:
        # Record failure
        elapsed = time.time() - start
        tool_duration_seconds.labels(
            tool_name="my_operation",
            status="error"
        ).observe(elapsed)

        tool_errors_total.labels(
            tool_name="my_operation",
            error_type=type(e).__name__
        ).inc()

        raise
```

### Example 10: Export Metrics

```python
from tracertm.mcp.metrics import MetricsExporter

# Get metrics in Prometheus format
metrics_text = MetricsExporter.export_metrics_text()
print(metrics_text)

# Or as bytes
metrics_bytes = MetricsExporter.export_metrics()

# Save to file
with open("metrics.txt", "w") as f:
    f.write(metrics_text)
```

## Performance Monitoring

### Example 11: Custom Performance Thresholds

```bash
# Set custom slow thresholds
export TRACERTM_MCP_SLOW_THRESHOLD=2.0      # 2 seconds
export TRACERTM_MCP_VERY_SLOW_THRESHOLD=10.0 # 10 seconds

rtm-mcp
```

### Example 12: Get Performance Statistics

```python
from tracertm.mcp.telemetry import PerformanceMonitoringMiddleware

# Access the middleware instance
perf_monitor = PerformanceMonitoringMiddleware(
    slow_threshold_seconds=5.0,
    very_slow_threshold_seconds=30.0
)

# After some operations...
stats = perf_monitor.get_statistics()

print(f"Total calls: {stats['total_calls']}")
print(f"Average duration: {stats['avg_duration_seconds']:.3f}s")
print(f"Slow calls: {stats['slow_calls']}")
print(f"Very slow calls: {stats['very_slow_calls']}")
```

## OpenTelemetry Tracing

### Example 13: Custom Span Attributes

```python
from tracertm.mcp.telemetry import get_tracer

tracer = get_tracer()

def my_function(user_id: str):
    with tracer.start_as_current_span("custom_operation") as span:
        # Add custom attributes
        span.set_attribute("user.id", user_id)
        span.set_attribute("custom.flag", True)
        span.set_attribute("custom.count", 42)

        # Add event
        span.add_event("processing_started", attributes={
            "item_count": 10
        })

        # Do work
        result = process_data()

        # Add another event
        span.add_event("processing_completed", attributes={
            "result_size": len(result)
        })

        return result
```

### Example 14: Nested Spans

```python
from tracertm.mcp.telemetry import get_tracer

tracer = get_tracer()

def parent_operation():
    with tracer.start_as_current_span("parent_op") as parent:
        parent.set_attribute("operation.type", "batch")

        # Child span 1
        with tracer.start_as_current_span("fetch_data") as child1:
            data = fetch_data()
            child1.set_attribute("data.size", len(data))

        # Child span 2
        with tracer.start_as_current_span("process_data") as child2:
            result = process(data)
            child2.set_attribute("result.count", len(result))

        return result
```

## Integration Examples

### Example 15: Docker Compose with Prometheus

```yaml
# docker-compose.yml
version: '3.8'

services:
  tracertm-mcp:
    build: .
    environment:
      - TRACERTM_MCP_METRICS_ENABLED=true
      - TRACERTM_MCP_TELEMETRY_ENABLED=true
      - TRACERTM_MCP_LOG_LEVEL=INFO
    ports:
      - "9090:9090"  # Metrics port
    networks:
      - monitoring

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9091:9090"
    networks:
      - monitoring
    depends_on:
      - tracertm-mcp

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'tracertm-mcp'
    static_configs:
      - targets: ['tracertm-mcp:9090']
```

### Example 16: Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracertm-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tracertm-mcp
  template:
    metadata:
      labels:
        app: tracertm-mcp
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: tracertm-mcp
        image: tracertm:latest
        env:
        - name: TRACERTM_MCP_METRICS_ENABLED
          value: "true"
        - name: TRACERTM_MCP_TELEMETRY_ENABLED
          value: "true"
        - name: TRACERTM_MCP_LOG_LEVEL
          value: "INFO"
        ports:
        - containerPort: 9090
          name: metrics
        livenessProbe:
          httpGet:
            path: /health
            port: 9090
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 9090
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: tracertm-mcp-metrics
  labels:
    app: tracertm-mcp
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

## Prometheus Queries

### Example 17: Common Queries

```promql
# Average request duration
rate(mcp_tool_duration_seconds_sum[5m]) / rate(mcp_tool_duration_seconds_count[5m])

# Error rate (percentage)
sum(rate(mcp_tool_calls_total{status="error"}[5m])) /
sum(rate(mcp_tool_calls_total[5m])) * 100

# P50, P95, P99 latency
histogram_quantile(0.50, rate(mcp_tool_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(mcp_tool_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(mcp_tool_duration_seconds_bucket[5m]))

# Top 5 slowest tools
topk(5, avg(rate(mcp_tool_duration_seconds_sum[5m])) by (tool_name) /
        avg(rate(mcp_tool_duration_seconds_count[5m])) by (tool_name))

# Top 5 most called tools
topk(5, sum(rate(mcp_tool_calls_total[5m])) by (tool_name))

# Success rate by tool
sum(rate(mcp_tool_calls_total{status="success"}[5m])) by (tool_name) /
sum(rate(mcp_tool_calls_total[5m])) by (tool_name) * 100

# Active calls
sum(mcp_active_tool_calls)

# Rate limit violations per user
sum(rate(mcp_rate_limit_hits_total[5m])) by (user_key)
```

## Grafana Alerts

### Example 18: Alert Configurations

```yaml
# alerts.yml
groups:
- name: tracertm_mcp
  interval: 30s
  rules:
  # High error rate
  - alert: HighErrorRate
    expr: sum(rate(mcp_tool_calls_total{status="error"}[5m])) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate in MCP server"
      description: "Error rate is {{ $value }} errors/sec"

  # Slow execution
  - alert: SlowToolExecution
    expr: histogram_quantile(0.95, rate(mcp_tool_duration_seconds_bucket[5m])) > 30
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Tools executing slowly"
      description: "P95 latency is {{ $value }}s"

  # Very slow execution
  - alert: VerySlowToolExecution
    expr: histogram_quantile(0.95, rate(mcp_tool_duration_seconds_bucket[5m])) > 60
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Tools executing very slowly"
      description: "P95 latency is {{ $value }}s"

  # Rate limit violations
  - alert: RateLimitViolations
    expr: rate(mcp_rate_limit_hits_total[5m]) > 1
    for: 5m
    labels:
      severity: info
    annotations:
      summary: "Rate limits being hit"
      description: "{{ $value }} rate limit violations/sec"

  # Auth failures
  - alert: AuthFailures
    expr: rate(mcp_auth_failures_total[5m]) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Authentication failures detected"
      description: "{{ $value }} auth failures/sec"

  # Service down
  - alert: MCPServerDown
    expr: up{job="tracertm-mcp"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "MCP server is down"
      description: "Instance {{ $labels.instance }} is down"
```

## Complete Example

### Example 19: Full Monitoring Setup

```python
#!/usr/bin/env python3
"""Complete monitoring setup example."""

import os
from tracertm.mcp import (
    start_metrics_server,
    configure_structured_logging,
    get_structured_logger,
)

def setup_monitoring():
    """Configure and start all monitoring components."""

    # 1. Configure environment
    os.environ["TRACERTM_MCP_TELEMETRY_ENABLED"] = "true"
    os.environ["TRACERTM_MCP_METRICS_ENABLED"] = "true"
    os.environ["TRACERTM_MCP_PERF_MONITORING"] = "true"
    os.environ["TRACERTM_MCP_ENHANCED_ERRORS"] = "true"
    os.environ["TRACERTM_MCP_LOG_LEVEL"] = "INFO"

    # 2. Configure structured logging
    configure_structured_logging(
        log_level="INFO",
        json_output=True,
        log_file="/var/log/tracertm-mcp.log"
    )

    # 3. Start metrics server
    metrics_server = start_metrics_server(
        host="0.0.0.0",
        port=9090
    )

    # 4. Get logger
    logger = get_structured_logger()
    logger.log_tool_call(
        tool_name="setup_monitoring",
        arguments={},
        duration=0.001,
        success=True
    )

    print("✓ Monitoring configured and started")
    print(f"✓ Metrics available at http://localhost:9090/metrics")
    print(f"✓ Health check at http://localhost:9090/health")
    print(f"✓ Logs writing to /var/log/tracertm-mcp.log")

    return metrics_server

if __name__ == "__main__":
    server = setup_monitoring()

    # Keep running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
```

## See Also

- **Comprehensive Guide**: `MONITORING.md`
- **Quick Reference**: `PHASE_4_QUICK_REFERENCE.md`
- **Implementation Details**: `PHASE_4_IMPLEMENTATION_SUMMARY.md`
- **Completion Summary**: `../../MCP_PHASE_4_COMPLETE.md`
