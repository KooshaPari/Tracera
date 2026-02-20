# Jaeger Distributed Tracing Setup Guide

This guide explains how to configure and use Jaeger for distributed tracing in TraceRTM's Go and Python backends.

## Overview

Jaeger is an open-source distributed tracing system that helps track requests as they flow across multiple services. TraceRTM uses Jaeger for:

- **End-to-end request tracing** across Go and Python backends
- **Performance monitoring** via latency visualization
- **Dependency analysis** between services
- **Error tracking** and debugging
- **Service health monitoring**

## Architecture

```
Go Backend (port 8080)          Python Backend (port 8000)
     |                               |
     | OTLP gRPC (4317)            | OTLP gRPC (4317)
     v                              v
  +-------- Jaeger Collector --------+
  |      (Docker: jaeger:4317)      |
  |                                  |
  +-------- Jaeger Storage -----------+
  |    (In-memory or persistent)     |
  |                                  |
  +--- Jaeger Query/UI (port 16686) -+
            |
         Browser: http://localhost:16686
```

## Docker Compose Configuration

Jaeger is automatically configured in `docker-compose.yml`:

```yaml
jaeger:
  image: jaegertracing/all-in-one:latest
  container_name: tracertm-jaeger
  ports:
    - "4317:4317"    # OTLP gRPC (trace input)
    - "4318:4318"    # OTLP HTTP
    - "16686:16686"  # Jaeger UI
    - "6831:6831/udp"      # Agent Zipkin thrift
    - "6832:6832/udp"      # Agent compact thrift
    - "14268:14268"  # Agent HTTP
  environment:
    COLLECTOR_OTLP_ENABLED: "true"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:16686"]
    interval: 10s
    timeout: 5s
    retries: 5
  networks:
    - tracertm
```

## Backend Configuration

### Go Backend

The Go backend sends traces via OTLP/gRPC to Jaeger. Configuration is in `/backend/internal/tracing/tracer.go`:

**Key features:**
- Service name: `tracertm-backend`
- OTLP endpoint: `127.0.0.1:4317` (development) or via `JAEGER_ENDPOINT` env var
- Batch span processor for efficient batching
- W3C Trace Context propagation
- Always sample (100% sampling in development)

**Initialization:**
```go
tp, err := tracing.InitTracer(ctx, "localhost:4317", "development")
```

**Environment variables:**
- `JAEGER_ENDPOINT`: OTLP gRPC endpoint (default: `127.0.0.1:4317`)
- `JAEGER_ENVIRONMENT`: Deployment environment (default: `development`)

**Docker environment:**
```yaml
go-backend:
  environment:
    - JAEGER_ENDPOINT=jaeger:4317
    - JAEGER_ENVIRONMENT=docker
  depends_on:
    jaeger:
      condition: service_started
```

### Python Backend

The Python backend sends traces via OTLP/gRPC to Jaeger. Configuration is in `/src/tracertm/observability/tracing.py`:

**Key features:**
- Service name: `tracertm-python-backend`
- OTLP endpoint: `127.0.0.1:4317` (development) or via `OTLP_ENDPOINT`/`JAEGER_ENDPOINT` env vars
- Batch span processor with configurable buffer sizes
- W3C Trace Context propagation
- Always sample (100% sampling in development)

**Initialization:**
```python
from tracertm.observability.tracing import init_tracing

tracer = init_tracing(
    service_name="tracertm-python-backend",
    service_version="1.0.0",
    environment="docker",
    otlp_endpoint="jaeger:4317"
)
```

**Environment variables (fallback chain):**
1. `OTLP_ENDPOINT` - Explicit OTLP endpoint override
2. `JAEGER_ENDPOINT` - Jaeger-specific endpoint
3. Default: `127.0.0.1:4317`

**Docker environment:**
```yaml
python-backend:
  environment:
    - OTLP_ENDPOINT=jaeger:4317
    - JAEGER_ENDPOINT=jaeger:4317
    - TRACING_ENVIRONMENT=docker
  depends_on:
    jaeger:
      condition: service_started
```

## Starting the Stack

### Using Docker Compose

Start all services including Jaeger:

```bash
docker compose up
```

Jaeger will start and be ready at `http://localhost:16686`.

### Local Development (Native Services)

If running backends locally without Docker:

**1. Start Jaeger (Docker only):**
```bash
docker run --rm \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

**2. Set environment variables for local backends:**

For Go:
```bash
export JAEGER_ENDPOINT=localhost:4317
export JAEGER_ENVIRONMENT=development
```

For Python:
```bash
export OTLP_ENDPOINT=localhost:4317
export TRACING_ENVIRONMENT=development
```

**3. Start backends with hot reload:**
```bash
# Go backend
cd backend && air

# Python backend (separate terminal)
python -m uvicorn tracertm.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Accessing the Jaeger UI

**URL:** `http://localhost:16686`

### UI Features

1. **Service Selection (left sidebar)**
   - `tracertm-backend` (Go)
   - `tracertm-python-backend` (Python)

2. **Trace Filtering**
   - Operation: Select specific endpoints
   - Tags: Filter by attributes (http.status_code, db.system, etc.)
   - Time range: View traces in specific time window

3. **Trace Details**
   - Timeline view: See span duration and nesting
   - Service map: View inter-service dependencies
   - Logs and tags: Inspect span attributes

### Typical Workflows

**Find a slow request:**
1. Select service from dropdown
2. Set min duration filter (e.g., "500ms")
3. Click "Find Traces"
4. Click trace to view details

**Debug cross-service call:**
1. Click on a trace
2. Look for spans in both Go and Python service
3. Check for errors in span logs
4. Inspect attributes for request context

**Monitor service dependencies:**
1. Click "Service Dependencies" in left menu
2. See visual graph of service connections
3. Hover over edges to see request counts

## Trace Context Propagation

Traces automatically propagate across service boundaries via W3C Trace Context headers:

```
traceparent: 00-<trace-id>-<span-id>-<trace-flags>
tracestate: <vendor-specific-data>
```

**Flow example:**
```
Client HTTP Request
    ↓ [includes traceparent header]
Go Backend (span created with trace-id)
    ↓ [propagates trace-id to Python]
Python Backend (span created with same trace-id)
    ↓ [propagates trace-id back to Go]
Go Backend (another span with same trace-id)
    ↓ [all spans collected and sent to Jaeger]
Jaeger UI (shows unified trace timeline)
```

## Span Types

### Go Backend Spans

Common spans created automatically:
- `http.server` - HTTP request handling
- `db.query` - Database queries (PostgreSQL)
- `messaging.publish` - NATS publish
- `messaging.receive` - NATS subscribe
- `http.client` - Calls to Python backend

### Python Backend Spans

Common spans created automatically:
- `http.server` - HTTP request handling (FastAPI)
- `http.client` - HTTP outbound calls
- `db.query` - Database queries (SQLAlchemy)
- `redis.command` - Redis operations
- `messaging.publish` - NATS publish

### Custom Spans

Add custom tracing to your code:

**Go:**
```go
ctx, span := tracer.Start(ctx, "operation-name")
defer span.End()

// Add attributes
span.SetAttributes(
    attribute.String("request.id", id),
    attribute.Int("item.count", count),
)

// Record exception
if err != nil {
    span.RecordError(err)
    span.SetStatus(codes.Error, err.Error())
}
```

**Python:**
```python
from tracertm.observability.tracing import get_tracer, trace_method

@trace_method(span_name="custom.operation", attributes={"key": "value"})
async def my_operation(arg1, arg2):
    # Your code here
    return result
```

## Performance Tuning

### Sampling Strategy

For production, use sampler based on request count:

**Go (configure in code):**
```go
// Sample 10% of requests
sampler := sdktrace.TraceIDRatioBased(0.1)
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sampler),
    // ...
)
```

**Python (configure in code):**
```python
# Implement custom sampler
from opentelemetry.sdk.trace import TraceIdRatioBased

sampler = TraceIdRatioBased(0.1)  # 10% sampling
provider = TracerProvider(sampler=sampler)
```

### Batch Processor Settings

**Go defaults:**
- Max export batch: 512 spans
- Max queue size: 2048 spans
- Batch timeout: 5 seconds

**Python defaults:**
- Max export batch: 512 spans
- Max queue size: 2048 spans
- Schedule delay: 5000ms

Adjust in code if needed for your throughput.

### Storage

All-in-One deployment uses **in-memory storage** by default. For persistent storage:

```bash
docker run \
  -p 4317:4317 \
  -p 16686:16686 \
  -e MEMORY_MAX_TRACES=10000 \
  jaegertracing/all-in-one:latest
```

For production, use Elasticsearch backend (see Jaeger docs).

## Troubleshooting

### Traces Not Appearing in UI

1. **Check Jaeger is running:**
   ```bash
   curl http://localhost:16686
   ```

2. **Verify endpoint configuration:**
   - Go: `echo $JAEGER_ENDPOINT`
   - Python: `echo $OTLP_ENDPOINT`

3. **Check logs for export errors:**
   ```bash
   # Docker
   docker logs tracertm-jaeger
   docker logs tracertm-go-backend
   docker logs tracertm-python-backend
   ```

4. **Verify network connectivity:**
   ```bash
   # From backend container
   docker exec tracertm-go-backend nc -zv jaeger 4317
   ```

### High Memory Usage

Jaeger in-memory storage has limits:
- Default: ~1GB
- Increase with `MEMORY_MAX_TRACES` env var
- Consider: Reduce sampling rate, use persistent storage

### Missing Spans

**Reasons:**
- Sampling disabled or misconfigured (check sampler)
- Service not initialized correctly (check logs)
- Trace context not propagating (check headers)
- Batch timeout too long (default 5s is good)

**Debug:**
```bash
# Enable debug logging in Go backend
OTEL_SDK_DISABLED_SPANS=false

# Enable debug logging in Python
OTEL_LOG_LEVEL=debug
```

## Advanced Topics

### Integrating with Metrics and Logs

Jaeger works alongside Prometheus and logs:

- **Prometheus:** Provides metrics (request count, latency)
- **Jaeger:** Provides distributed traces (request flow)
- **Logs:** Provides detailed context

Combined, they give complete observability:
```
Metrics (Prometheus) ──→ Indicates high latency
Logs ──────────────────→ Shows application events
Traces (Jaeger) ────────→ Shows exact flow and timing
```

### Custom Exporters

Instead of Jaeger, you can export to other OTLP backends:

- **Tempo** (Grafana) - OTLP native, integrates with Loki/Prometheus
- **Zipkin** - Legacy but still common
- **CloudTrace** (GCP) - Cloud-native
- **AWS X-Ray** - AWS-native

Just change the exporter endpoint and credentials.

## References

- [Jaeger Official Docs](https://www.jaegertracing.io/)
- [OpenTelemetry Go SDK](https://pkg.go.dev/go.opentelemetry.io/otel)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
- [OTLP Protocol Specification](https://opentelemetry.io/docs/specs/otel/protocol/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)

## Quick Reference

| Task | Command |
|------|---------|
| Start full stack | `docker compose up` |
| View Jaeger UI | `http://localhost:16686` |
| View Go backend traces | Jaeger UI → Service: `tracertm-backend` |
| View Python traces | Jaeger UI → Service: `tracertm-python-backend` |
| Stop all services | `docker compose down` |
| View Jaeger logs | `docker logs tracertm-jaeger` |
| Inspect trace from CLI | Use Jaeger API: `curl http://localhost:16686/api/traces?service=tracertm-backend` |

## Environment Variables Summary

### Go Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `JAEGER_ENDPOINT` | `127.0.0.1:4317` | OTLP gRPC endpoint |
| `JAEGER_ENVIRONMENT` | `development` | Deployment environment (for tags) |

### Python Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `OTLP_ENDPOINT` | (none) | OTLP endpoint (overrides JAEGER_ENDPOINT) |
| `JAEGER_ENDPOINT` | `127.0.0.1:4317` | Fallback OTLP endpoint |
| `TRACING_ENVIRONMENT` | `development` | Deployment environment (for tags) |

### Jaeger All-in-One

| Variable | Default | Description |
|----------|---------|-------------|
| `COLLECTOR_OTLP_ENABLED` | `true` | Enable OTLP collector |
| `MEMORY_MAX_TRACES` | ~1000 | Max traces in memory |
| `COLLECTOR_ZIPKIN_HOST_PORT` | `:9411` | Zipkin collector port |
