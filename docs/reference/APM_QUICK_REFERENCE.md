# APM Quick Reference

Quick reference for Application Performance Monitoring in TraceRTM.

## Configuration

### Environment Variables

```bash
# Enable/disable tracing
TRACING_ENABLED=true

# Shared Phenotype OTLP endpoint
PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=127.0.0.1:4317
OTLP_ENDPOINT=127.0.0.1:4317

# Environment name
TRACING_ENVIRONMENT=development
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | http://localhost:3000 | Dashboards, traces, metrics, logs |
| Tempo | http://localhost:3200 | Trace backend |
| Prometheus | http://localhost:9090 | Raw metrics data |

## Go Backend

### HTTP Tracing

Automatic via middleware (already configured).

### Database Tracing

```go
import "github.com/kooshapari/tracertm-backend/internal/tracing"

ctx, dbSpan := tracing.StartDBSpan(ctx, tracing.dbOperationSelect, "items")
defer dbSpan.End()

dbSpan.SetQuery("SELECT * FROM items WHERE id = $1")
// Execute query
dbSpan.SetRowsAffected(rowCount)
```

### Custom Spans

```go
import "go.opentelemetry.io/otel"

tracer := otel.Tracer("tracertm-backend")
ctx, span := tracer.Start(ctx, "operation-name")
defer span.End()

span.SetAttributes(attribute.String("key", "value"))
```

## Python Backend

### HTTP Tracing

Automatic via FastAPI instrumentation (already configured).

### Database Tracing

Automatic via SQLAlchemy instrumentation (already configured).

### Custom Tracing

```python
# Decorator
from tracertm.observability import trace_method

@trace_method(span_name="my_operation")
async def my_function(data: dict) -> Result:
    return result

# Manual
from tracertm.observability import get_tracer

tracer = get_tracer()
with tracer.start_as_current_span("operation") as span:
    span.set_attribute("key", "value")
    # Do work
```

## Common Patterns

### Error Recording

```go
// Go
if err != nil {
    span.RecordError(err)
    span.SetStatus(codes.Error, err.Error())
}
```

```python
# Python
try:
    result = await operation()
except Exception as e:
    span.record_exception(e)
    raise
```

### Span Attributes

```go
// Go
span.SetAttributes(
    attribute.String("user.id", userID),
    attribute.Int("count", count),
    attribute.Bool("success", true),
)
```

```python
# Python
span.set_attribute("user.id", user_id)
span.set_attribute("count", count)
span.set_attribute("success", True)
```

## Useful Prometheus Queries

### Response Time Percentiles

```promql
# p95 response time
histogram_quantile(0.95,
  sum(rate(http_server_duration_milliseconds_bucket[5m])) by (le)
)
```

### Error Rate

```promql
# Error percentage
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
* 100
```

### Request Throughput

```promql
# Requests per second
sum(rate(http_requests_total[5m]))
```

### Database Performance

```promql
# Slow queries (>100ms)
histogram_quantile(0.95,
  sum(rate(db_query_duration_milliseconds_bucket[5m])) by (le)
) > 100
```

## Trace Search Tips

### Find Slow Requests

1. Select service: `tracertm-backend` or `tracertm-python-backend`
2. Set min duration: `500ms`
3. Open the trace view in Grafana and inspect the matching spans

### Search by Tag

Add tags in search:
- `http.method=POST`
- `http.status_code=500`
- `user.id=abc123`

### Service Dependency Graph

Click "System Architecture" tab to view service dependencies.

## Dashboard Shortcuts

### APM Performance Dashboard

- **Response times**: p50, p95, p99 for both backends
- **Request rates**: Requests/sec by endpoint
- **Success rates**: Percentage of successful requests
- **Database ops**: Query performance metrics
- **Cache metrics**: Hit rates, latency

### Distributed Tracing Dashboard

- **Trace collection**: Spans collected per service
- **Span duration**: Latency percentiles
- **Error rate**: Failed traces
- **Top endpoints**: Most-called APIs
- **External calls**: Third-party API performance

## Troubleshooting Commands

```bash
# Check the shared collector path
curl -fsS http://localhost:12345/-/ready
curl -fsS http://localhost:3000/api/health

# View backend logs with tracing info
tail -f .process-compose/logs/go-backend.log | grep -i tracing
tail -f .process-compose/logs/python-backend.log | grep -i tracing

# Restart Alloy
process-compose process restart alloy

# Check trace export rate (Prometheus)
curl -s http://localhost:9090/api/v1/query?query=rate(otelcol_receiver_accepted_spans[1m])
```

## Performance Impact

| Component | Overhead |
|-----------|----------|
| HTTP request tracing | ~0.5-2ms |
| Database query tracing | ~0.1ms |
| Custom span | ~0.05ms |

## Best Practices

✅ **Do**:
- Use meaningful span names
- Add relevant attributes
- Record errors
- Sanitize sensitive data
- Use batch processing

❌ **Don't**:
- Log passwords or tokens
- Create too many spans (>100 per request)
- Use blocking exporters
- Include PII in span names
- Trace every small function

## Common Issues

| Issue | Solution |
|-------|----------|
| No traces in Grafana | Check `TRACING_ENABLED=true` and Alloy is running |
| High latency | Reduce sampling rate or increase batch timeout |
| Missing DB traces | Ensure instrumentation is called on engine |
| Broken trace chains | Check context propagation across boundaries |

## Links

- [Full APM Integration Guide](../guides/APM_INTEGRATION_GUIDE.md)
- [Grafana Dashboards](./GRAFANA_DASHBOARDS.md)
- [OpenTelemetry Docs](https://opentelemetry.io/docs/)
