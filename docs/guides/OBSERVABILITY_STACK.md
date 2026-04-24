> Historical note: this document preserves the pre-Phenotype observability stack. The active org path is the shared collector, Grafana Alloy, and Grafana Tempo. Treat Jaeger and Promtail references below as legacy context only.

# TraceRTM Observability Stack

Complete overview of the observability infrastructure including metrics (Prometheus), logs
(Loki), and traces through Grafana Alloy, the shared Phenotype collector, and Tempo.

## Overview

The TraceRTM observability stack provides three pillars of observability:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Observability Stack                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  METRICS (Prometheus)        LOGS (Loki)         TRACES (Tempo) │
│  ├─ Request count           ├─ Application logs  ├─ Request flow│
│  ├─ Response latency        ├─ Error logs        ├─ Latency     │
│  ├─ Error rate              ├─ Debug logs        ├─ Dependencies│
│  ├─ Service health          └─ Tracing context   └─ Errors      │
│  ├─ Resource usage                                              │
│  └─ Custom metrics          (Timestamps, IDs, stack traces)     │
│                                                                 │
│  Visualized in:             Collected by:        Visualized in: │
│  ├─ Grafana (3000)          ├─ Application       ├─ Tempo (3200)
│  ├─ Prometheus (9090)       ├─ Grafana Alloy     └─ Via trace IDs
│  └─ Exporters (9113, etc)   └─ Structured logging               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Metrics (Prometheus)

**Purpose:** Measure and aggregate quantitative data
- Request counts
- Latency (p50, p95, p99)
- Error rates
- Resource usage (CPU, memory)
- Custom application metrics

**Stack:**
```
Application          Prometheus      Grafana
    │                    │               │
    ├─ Metrics           │       Dashboard/Alerts
    │   (port 9090)      │
    ├─ Go:8080/metrics   │
    └─ Python:8000/      │
       metrics            │
```

**Services:**
- **Prometheus** (port 9090): Scrapes and stores metrics
- **Grafana** (port 3000): Visualizes metrics via dashboards
- **Exporters:**
  - Node Exporter (9100): Host metrics
  - Postgres Exporter (9187): Database metrics
  - Redis Exporter (9121): Cache metrics
  - Nginx Exporter (9113): Reverse proxy metrics

### Logs (Structured)

**Purpose:** Record detailed events and debugging information
- Application lifecycle events
- Request context (ID, user, duration)
- Error messages with stack traces
- Database queries
- External API calls

**Stack:**
```
Application          Structured Logs      Log Aggregation
    │                    │                     │
    ├─ Log lines         │                     │
    │  (JSON/plain)      │        Future: ELK/Loki
    ├─ Go: logrus/zap    │
    └─ Python: loguru    │
       structlog          │
```

**Current Implementation:**
- Go: `go.uber.org/zap` + `logrus`
- Python: `loguru` + `structlog`
- Docker: Logs to stdout (managed by docker-compose)
- Access: `docker logs <container>`

### Traces (Tempo)

**Purpose:** Track request flow across service boundaries
- End-to-end request journey
- Service dependencies
- Latency bottlenecks
- Error context across services
- Distributed correlation (trace ID)

**Stack:**
```
Application          OTLP             Alloy/Tempo         Grafana
    │                 │                  │                   │
    ├─ Spans          │           Collector/Storage      Visualization
    │  (OTLP/gRPC)    │                  │
    ├─ Go             │                  │
    └─ Python:8000    ├─ Port 4317      │
                      │ (gRPC)           │
                      └─ Port 4318 (HTTP)└─ Grafana trace search
```

**Services:**
- **Grafana Alloy**: OTLP ingress, normalization, and routing
- **Shared Phenotype Collector**: The org-level trace entrypoint used by both backends
- **Tempo** (port 3200): Trace storage and query backend
- **OTLP/gRPC** (port 4317): Trace protocol
- **OTLP/HTTP** (port 4318): Alternative protocol

## Configuration Summary

### Go Backend (`backend/`)

**Tracing:**
```go
// File: internal/tracing/tracer.go
tp, err := tracing.InitTracer(ctx, "127.0.0.1:4317", "development")
```

**Configuration:**
- Service: `tracertm-backend`
- Version: `1.0.0`
- Environment: From `TRACING_ENVIRONMENT` env var
- OTLP endpoint: From `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` (default: `127.0.0.1:4317`)
- Sampling: 100% (development)
- Processor: Batch (efficient for high throughput)

**Metrics:**
- Prometheus client on `/metrics` endpoint
- Custom metrics for request count, latency, etc.

**Logging:**
- Structured logs via `zap` and `logrus`
- Trace context included in logs

### Python Backend (`src/tracertm/`)

**Tracing:**
```python
# File: observability/tracing.py
tracer = init_tracing(
    service_name="tracertm-python-backend",
    otlp_endpoint="127.0.0.1:4317"
)
```

**Configuration:**
- Service: `tracertm-python-backend`
- Version: `1.0.0`
- Environment: From `TRACING_ENVIRONMENT` env var
- OTLP endpoint: From `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` (default: `127.0.0.1:4317`)
- **Must enable:** `TRACING_ENABLED=true`
- Sampling: 100% (development)
- Processor: Batch (efficient for high throughput)

**Instrumentation:**
```python
# Auto-instrument FastAPI, SQLAlchemy, Redis, HTTP
instrument_app(app)
instrument_all()

# Custom tracing via decorator
@trace_method(span_name="custom.op", attributes={"key": "value"})
async def my_function():
    pass
```

**Logging:**
- Structured logs via `loguru` and `structlog`
- Trace context included in logs

## Docker Compose Integration

All observability components are configured in the shared org stack:

```yaml
services:
  # Tracing
  alloy:
    image: grafana/alloy:latest
    ports:
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    depends_on:
      - tempo

  tempo:
    image: grafana/tempo:latest
    ports:
      - "3200:3200"    # Tempo query API

  # Metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  # Exporters
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    ports:
      - "9187:9187"

  redis-exporter:
    image: oliver006/redis_exporter:latest
    ports:
      - "9121:9121"

  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    ports:
      - "9113:9113"
```

## Access Points

| Component | URL | Purpose |
|-----------|-----|---------|
| Grafana | http://localhost:3000 | View traces and dashboards |
| Prometheus | http://localhost:9090 | Query metrics |
| Tempo | http://localhost:3200 | Trace backend |

## Example Workflows

### Workflow 1: Find Slow Request

1. **Metrics first** (Prometheus/Grafana):
   - Check latency p95, p99
   - Identify which endpoint is slow

2. **Drill down to trace** (Grafana/Tempo):
   - Find that endpoint's traces
   - Sort by duration
   - View slowest trace

3. **Analyze trace**:
   - Which span is taking time?
   - Is it database, HTTP, or compute?
   - Check span attributes for context

### Workflow 2: Debug Error

1. **Logs first**:
   - `docker logs tracertm-go-backend | grep ERROR`
   - Find error message and trace ID

2. **View trace in Grafana**:
   - Search by trace ID
   - Find span with error
   - View error attributes and logs

3. **Check metrics**:
   - Did error rate spike?
   - Which service is erroring?
   - Is it a pattern or one-off?

### Workflow 3: Monitor Performance

1. **Set up Grafana dashboard**:
   - Add panels for p50, p95, p99 latencies
   - Add panel for error rate
   - Add panel for request count

2. **Configure alerts**:
   - Alert if latency p95 > 500ms
   - Alert if error rate > 1%
   - Alert if service is down

3. **On alert**:
   - Check Grafana dashboard
   - Drill into Prometheus for details
   - Use Grafana trace search to inspect Tempo-backed traces

## Best Practices

### Logging
- ✅ Use structured logging (JSON format)
- ✅ Include trace ID in every log line
- ✅ Use appropriate log levels (INFO, WARN, ERROR)
- ❌ Don't log sensitive data (passwords, tokens)
- ❌ Don't log in hot paths without sampling

### Tracing
- ✅ Include business context in span attributes
- ✅ Use semantic span names
- ✅ Add error details to spans
- ✅ Sample appropriately for your load
- ❌ Don't create spans for every tiny operation
- ❌ Don't use unbounded attribute values

### Metrics
- ✅ Use consistent naming conventions
- ✅ Emit custom business metrics
- ✅ Set up alerting for critical metrics
- ❌ Don't emit high-cardinality metrics
- ❌ Don't scrape too frequently (30s default is good)

## Performance Considerations

### Logging Impact
- **Low:** Structured logging is efficient
- Typical overhead: <1% CPU

### Tracing Impact
- **Medium:** Collecting traces adds overhead
- With 100% sampling: 2-5% CPU overhead
- With 10% sampling: <1% CPU overhead
- Memory: ~10-50MB for trace storage

### Metrics Impact
- **Low:** Prometheus scraping is lightweight
- Typical overhead: <1% CPU
- Memory: ~50-100MB for timeseries storage

## Capacity Planning

For development/testing (current):
- Trace storage: 1-10GB (in-memory, cleared on restart)
- Metrics storage: ~1GB (7 days retention)
- Log volume: ~100MB per service per day

For production, plan for:
- Trace storage: 10-100GB (persistent)
- Metrics storage: 100GB+ (1 year retention)
- Log aggregation: 100GB+ per day (all services)

## Future Enhancements

**Planned improvements:**
1. Elasticsearch backend for persistent trace storage
2. Loki for log aggregation and long-term retention
3. Alert Manager for intelligent alerting
4. Custom dashboards for business metrics
5. OpenTelemetry collector for centralized configuration
6. Service topology auto-discovery

**Out of scope for MVP:**
- Distributed tracing to external services
- Custom instrumentation for business logic
- Anomaly detection and auto-scaling
- Cross-region trace aggregation

## Troubleshooting

### "No traces appear in Grafana"
1. Check `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` is correct
2. Verify backends can reach the shared collector endpoint
3. Check backend logs for tracing errors: `docker logs <backend> | grep -i trac`
4. Generate a test request: `curl http://localhost:8080/api/v1/health`

### "Prometheus has no metrics"
1. Check `/metrics` endpoints are accessible
2. Verify `prometheus.yml` scrape config is correct
3. Check service health: `curl http://localhost:8080/metrics`

### "Grafana can't connect to Prometheus"
1. Check Prometheus is healthy: `curl http://localhost:9090`
2. Add Prometheus datasource: http://prometheus:9090
3. Verify docker network connectivity

## Related Documentation

- **Setup Guides:**
  - [OpenTelemetry Go Setup](./OTEL_GO_SETUP.md)
  - [OpenTelemetry Python Setup](./OTEL_PYTHON_SETUP.md)

- **Quick References:**
  - [Distributed Tracing Quick Reference](../reference/TRACING_QUICK_REFERENCE.md)

- **Configuration:**
  - Go tracing: `backend/internal/tracing/tracer.go`
  - Python tracing: `src/tracertm/observability/tracing.py`
  - Docker: `docker-compose.yml`
  - Prometheus: `monitoring/prometheus.yml`

## Summary

The TraceRTM observability stack provides:
- **Metrics** via Prometheus for quantitative measurement
- **Logs** via structured logging for detailed context
- **Traces** via Grafana Alloy and Tempo for distributed request tracking

Together, these provide complete visibility into application behavior and performance.
