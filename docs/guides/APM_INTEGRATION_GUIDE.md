# Application Performance Monitoring (APM) Integration Guide

This guide explains how to use the integrated APM solution in TraceRTM, powered by OpenTelemetry, Jaeger, and Grafana.

## Overview

TraceRTM includes a comprehensive APM solution that provides:

- **Distributed Tracing**: Track requests across Go and Python backends, databases, and external APIs
- **Performance Metrics**: Monitor response times, throughput, and error rates
- **Database Instrumentation**: Trace SQL queries and optimize database performance
- **Custom Instrumentation**: Add tracing to your own code

## Architecture

```
┌──────────────┐     ┌──────────────┐
│ Go Backend   │────▶│              │
│ (Echo/HTTP)  │     │              │
└──────────────┘     │              │
                     │   Jaeger     │──────▶ Grafana Dashboards
┌──────────────┐     │   (OTLP)     │
│ Python       │────▶│              │
│ Backend      │     │              │
│ (FastAPI)    │     │              │
└──────────────┘     └──────────────┘
       │                     ▲
       │                     │
       ▼                     │
┌──────────────┐            │
│ PostgreSQL   │────────────┘
│ Redis        │
│ Neo4j        │
└──────────────┘
```

## Quick Start

### 1. Enable Tracing

Add to your `.env` file:

```bash
# Enable distributed tracing
TRACING_ENABLED=true

# Jaeger endpoint (default: localhost:4317)
JAEGER_ENDPOINT=localhost:4317
OTLP_ENDPOINT=localhost:4317

# Environment name
TRACING_ENVIRONMENT=development
```

### 2. Start Services

```bash
# Start the full stack with monitoring
make dev

# Or with TUI
make dev-tui
```

This starts:
- Jaeger (UI: http://localhost:16686)
- Prometheus (http://localhost:9090)
- Grafana (http://localhost:3001)

### 3. Access APM Dashboards

1. **Grafana**: http://localhost:3001
   - Username: `admin`
   - Password: `admin` (change on first login)

2. **Pre-configured Dashboards**:
   - **APM Performance**: Response times, throughput, cache metrics
   - **Distributed Tracing**: Trace analysis, error rates, top endpoints
   - **Infrastructure**: Database, Redis, system metrics

3. **Jaeger UI**: http://localhost:16686
   - Search traces by service, operation, tags
   - View detailed trace timelines
   - Analyze service dependencies

## Go Backend Instrumentation

### Automatic HTTP Tracing

HTTP requests are automatically traced via middleware:

```go
// Already configured in server.go
if infra.TracerProvider != nil {
    s.echo.Use(tracing.Middleware())
}
```

### Database Query Tracing

Use the database tracing helpers:

```go
import "github.com/kooshapari/tracertm-backend/internal/tracing"

func (r *Repository) GetItem(ctx context.Context, id string) (*Item, error) {
    // Start a database span
    ctx, dbSpan := tracing.StartDBSpan(ctx, tracing.dbOperationSelect, "items")
    defer dbSpan.End()

    query := "SELECT * FROM items WHERE id = $1"
    dbSpan.SetQuery(query)

    var item Item
    err := r.db.QueryRow(ctx, query, id).Scan(&item)
    if err != nil {
        dbSpan.RecordError(err)
        return nil, err
    }

    dbSpan.SetRowsAffected(1)
    return &item, nil
}
```

### Custom Span Creation

Add custom spans to trace specific operations:

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
)

func processData(ctx context.Context, data []byte) error {
    tracer := otel.Tracer("tracertm-backend")

    ctx, span := tracer.Start(ctx, "processData")
    defer span.End()

    span.SetAttributes(
        attribute.Int("data.size", len(data)),
        attribute.String("data.format", "json"),
    )

    // Your processing logic
    result, err := doProcessing(data)
    if err != nil {
        span.RecordError(err)
        return err
    }

    span.SetAttributes(attribute.String("result.id", result.ID))
    return nil
}
```

## Python Backend Instrumentation

### Automatic FastAPI Tracing

FastAPI requests are automatically traced:

```python
# Already configured in main.py
from tracertm.observability import init_tracing, instrument_app

if tracing_enabled:
    init_tracing(
        service_name="tracertm-python-backend",
        environment=os.getenv("TRACING_ENVIRONMENT", "development"),
    )
    instrument_app(app)
```

### Database Query Tracing

Database queries are automatically traced via SQLAlchemy instrumentation:

```python
# Already configured in main.py
from tracertm.observability import instrument_database

# Instrument the database engine
instrument_database(engine)
```

### Custom Span Creation

Add custom tracing to your code:

```python
from tracertm.observability import trace_method

# Decorator-based tracing
@trace_method(
    span_name="process_requirements",
    attributes={"module": "requirements"}
)
async def process_requirements(requirements: list[Requirement]) -> Result:
    # Your processing logic
    return result

# Manual span creation
from tracertm.observability import get_tracer

async def complex_operation(data: dict) -> None:
    tracer = get_tracer()

    with tracer.start_as_current_span(
        "complex_operation",
        attributes={
            "operation.type": "analysis",
            "data.size": len(data)
        }
    ) as span:
        try:
            result = await process(data)
            span.set_attribute("result.count", len(result))
        except Exception as e:
            span.record_exception(e)
            raise
```

### HTTP Client Tracing

External API calls are automatically traced:

```python
# Already configured via instrument_all()
import httpx

async def call_external_api(url: str) -> dict:
    # Automatically traced
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## Best Practices

### 1. Span Naming

Use clear, hierarchical span names:

```
✅ Good:
- "db.query.items.select"
- "http.request.POST /api/items"
- "cache.get.user_profile"

❌ Bad:
- "query"
- "request"
- "operation"
```

### 2. Attributes

Add meaningful attributes to spans:

```go
span.SetAttributes(
    attribute.String("user.id", userID),
    attribute.String("project.id", projectID),
    attribute.Int("items.count", len(items)),
    attribute.String("operation.type", "batch_import"),
)
```

### 3. Error Handling

Always record errors:

```go
if err != nil {
    span.RecordError(err)
    span.SetStatus(codes.Error, err.Error())
    return err
}
```

### 4. Sensitive Data

Never log sensitive data in spans:

```go
// ❌ Don't do this
span.SetAttributes(
    attribute.String("user.password", password),
    attribute.String("api.key", apiKey),
)

// ✅ Do this
span.SetAttributes(
    attribute.String("user.id", userID),
    attribute.Bool("auth.success", true),
)
```

## Performance Impact

OpenTelemetry adds minimal overhead:

- **Go Backend**: ~0.5ms per traced request
- **Python Backend**: ~1-2ms per traced request
- **Database Queries**: ~0.1ms per query

Tracing uses:
- Sampling (configurable)
- Batch span processing (5-second intervals)
- Async export to Jaeger

## Troubleshooting

### Traces Not Appearing

1. **Check Jaeger is running**:
   ```bash
   curl http://localhost:16686
   ```

2. **Verify tracing is enabled**:
   ```bash
   echo $TRACING_ENABLED
   # Should output: true
   ```

3. **Check backend logs**:
   ```bash
   # Go backend
   tail -f .process-compose/logs/go-backend.log | grep -i tracing

   # Python backend
   tail -f .process-compose/logs/python-backend.log | grep -i tracing
   ```

### High Latency

If tracing adds too much latency:

1. **Reduce sampling**:
   ```go
   // In backend/internal/tracing/tracer.go
   sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1)) // Sample 10%
   ```

2. **Increase batch timeout**:
   ```go
   sdktrace.WithBatchTimeout(10*time.Second)
   ```

### Missing Database Traces

Ensure database instrumentation is enabled:

```python
# Python
from tracertm.observability import instrument_database
instrument_database(engine)
```

```go
// Go - use tracing helpers
ctx, dbSpan := tracing.StartDBSpan(ctx, operation, table)
defer dbSpan.End()
```

## Dashboard Queries

### Custom Prometheus Queries

**Average Response Time by Endpoint**:
```promql
histogram_quantile(0.95,
  sum(rate(http_server_duration_milliseconds_bucket[5m])) by (le, route)
)
```

**Error Rate**:
```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

**Database Query Performance**:
```promql
histogram_quantile(0.99,
  sum(rate(db_query_duration_milliseconds_bucket[5m])) by (le, operation)
)
```

## Advanced Topics

### Trace Context Propagation

Traces automatically propagate across:
- HTTP requests (W3C Trace Context headers)
- gRPC calls
- Message queues (NATS)

### Custom Exporters

Add additional exporters (e.g., Tempo, Zipkin):

```go
// In backend/internal/tracing/tracer.go
import "go.opentelemetry.io/otel/exporters/zipkin"

zipkinExporter, _ := zipkin.New("http://localhost:9411/api/v2/spans")
tp := sdktrace.NewTracerProvider(
    sdktrace.WithBatcher(otlpExporter),
    sdktrace.WithBatcher(zipkinExporter), // Multiple exporters
)
```

### Sampling Strategies

Configure different sampling for different environments:

```go
var sampler sdktrace.Sampler
switch environment {
case "production":
    sampler = sdktrace.TraceIDRatioBased(0.1) // 10%
case "staging":
    sampler = sdktrace.TraceIDRatioBased(0.5) // 50%
default:
    sampler = sdktrace.AlwaysSample() // 100%
}
```

## Related Documentation

- [Grafana Dashboards Guide](./GRAFANA_DASHBOARDS.md)
- [Monitoring Overview](../reports/MONITORING_OVERVIEW.md)
- [OpenTelemetry Best Practices](https://opentelemetry.io/docs/best-practices/)

## Support

For issues or questions:
- Check Jaeger UI: http://localhost:16686
- View Grafana dashboards: http://localhost:3001
- Review backend logs in `.process-compose/logs/`
