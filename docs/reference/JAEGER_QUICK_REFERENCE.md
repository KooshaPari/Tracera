# Jaeger Distributed Tracing Quick Reference

## URLs and Ports

| Service | URL/Port | Purpose |
|---------|----------|---------|
| Jaeger UI | http://localhost:16686 | View and analyze traces |
| OTLP gRPC | localhost:4317 | Trace collector (production protocol) |
| OTLP HTTP | localhost:4318 | HTTP trace collector (alternative) |
| Jaeger Agent Thrift | localhost:6831 (UDP) | Legacy agent protocol |
| Jaeger HTTP API | http://localhost:14268 | REST API for queries |

## Starting/Stopping

```bash
# Start full stack with Jaeger
docker compose up

# Stop everything
docker compose down

# View Jaeger logs
docker logs tracertm-jaeger

# View Go backend logs (includes tracing init)
docker logs tracertm-go-backend | grep -i tracing

# View Python backend logs (includes tracing init)
docker logs tracertm-python-backend | grep -i tracing
```

## Environment Variables

### Go Backend (`JAEGER_*`)
```bash
JAEGER_ENDPOINT=localhost:4317          # OTLP gRPC endpoint
JAEGER_ENVIRONMENT=development          # Environment tag for spans
TRACING_ENABLED=true                    # Enable/disable tracing (default: true)
```

### Python Backend (`OTLP_*`, `TRACING_*`)
```bash
OTLP_ENDPOINT=localhost:4317            # Explicit OTLP endpoint
JAEGER_ENDPOINT=localhost:4317          # Fallback OTLP endpoint
TRACING_ENABLED=true                    # MUST be "true" to enable
TRACING_ENVIRONMENT=development         # Environment tag for spans
```

## Common Tasks

### View All Traces for a Service
1. Open http://localhost:16686
2. Select service from dropdown:
   - `tracertm-backend` (Go)
   - `tracertm-python-backend` (Python)
3. Click "Find Traces"

### Find Slow Requests
1. Service: Select the service
2. Min Duration: Enter "500ms" (or desired threshold)
3. Click "Find Traces"
4. Sort by duration (default: newest first)

### Debug Failed Request
1. Find the trace with an error (red icon)
2. Click on the trace
3. Look for spans with error tag
4. Click error span to see error details in "Logs" section

### View Cross-Service Call
1. Make request that calls another service
2. Find trace in Jaeger
3. Expand timeline - should see:
   - HTTP request span in calling service
   - HTTP client span with call details
   - HTTP server span in called service
   - All with same trace ID

### Check Service Dependencies
1. Click "Service Dependencies" in left menu
2. See visual graph of which services call which
3. Hover over arrows for request count

### Monitor Performance
1. Click on service name in UI
2. Go to "Service Performance" tab
3. View P50, P95, P99 latencies
4. View request count and error rate

## Trace Context Propagation

Traces automatically propagate via W3C Trace Context headers:

```
traceparent: 00-<trace-id>-<span-id>-<trace-flags>
```

**Example:**
```
traceparent: 00-a0eebc999c0cff169f13f3f5c54e6d05-1001d129581e8cd6-01
```

Format:
- `00` = version
- `a0eebc999c0cff169f13f3f5c54e6d05` = 128-bit trace ID
- `1001d129581e8cd6` = 64-bit span ID
- `01` = sampled (trace this request)

## Span Types

### HTTP Spans
- **Type:** `http.server` or `http.client`
- **Attributes:** `http.method`, `http.status_code`, `http.route`, `http.url`
- **Created by:** Automatic instrumentation

### Database Spans
- **Type:** `db.query`
- **Attributes:** `db.system` (postgres/redis), `db.statement`, `db.rows_affected`
- **Created by:** SQLAlchemy (Python), pgx (Go)

### Message Queue Spans
- **Type:** `messaging.publish` or `messaging.receive`
- **Attributes:** `messaging.system` (nats), `messaging.destination`
- **Created by:** NATS client instrumentation

### Custom Spans

**Go:**
```go
tracer := otel.Tracer("my-app")
ctx, span := tracer.Start(ctx, "operation-name")
defer span.End()
span.SetAttributes(attribute.String("key", "value"))
```

**Python:**
```python
@trace_method(span_name="operation-name", attributes={"key": "value"})
async def my_operation():
    pass
```

## API Endpoints

### Get Services
```bash
curl http://localhost:16686/api/services | jq
```

### Get Traces for Service
```bash
curl "http://localhost:16686/api/traces?service=tracertm-backend&limit=10" | jq
```

### Get Specific Trace
```bash
TRACE_ID="..."  # From service dropdown
curl "http://localhost:16686/api/traces/$TRACE_ID" | jq
```

### Get Operations for Service
```bash
curl "http://localhost:16686/api/services/tracertm-backend/operations" | jq
```

## Sampling Strategies

Current setup: **Always sample** (100% in development)

For production, adjust sampler:

**Go:**
```go
sampler := sdktrace.TraceIDRatioBased(0.1)  // 10% sampling
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sampler),
)
```

**Python:**
```python
from opentelemetry.sdk.trace import TraceIdRatioBased
sampler = TraceIdRatioBased(0.1)  # 10% sampling
provider = TracerProvider(sampler=sampler)
```

## Troubleshooting Commands

```bash
# Check Jaeger is running
docker ps | grep jaeger

# Check Jaeger is healthy
docker exec tracertm-jaeger curl -s http://localhost:16686 > /dev/null && echo "✅ Jaeger OK"

# Check backends can reach Jaeger
docker exec tracertm-go-backend nc -zv jaeger 4317
docker exec tracertm-python-backend nc -zv jaeger 4317

# Generate test trace
curl http://localhost:8080/api/v1/health
curl http://localhost:8000/health

# Check for tracing errors
docker logs tracertm-go-backend 2>&1 | grep -i "error.*trac"
docker logs tracertm-python-backend 2>&1 | grep -i "error.*trac"

# View recent traces via API
curl "http://localhost:16686/api/traces?service=tracertm-backend&limit=5" | jq '.data[0] | {traceID, spans: (.spans | length)}'
```

## Docker Compose Changes

**Added to docker-compose.yml:**

```yaml
jaeger:
  image: jaegertracing/all-in-one:latest
  container_name: tracertm-jaeger
  ports:
    - "4317:4317"    # OTLP gRPC
    - "4318:4318"    # OTLP HTTP
    - "16686:16686"  # UI
  environment:
    COLLECTOR_OTLP_ENABLED: "true"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:16686"]
  networks:
    - tracertm
```

**Updated go-backend service:**
```yaml
environment:
  - JAEGER_ENDPOINT=jaeger:4317
  - JAEGER_ENVIRONMENT=docker
depends_on:
  jaeger:
    condition: service_started
```

**Updated python-backend service:**
```yaml
environment:
  - TRACING_ENABLED=true
  - OTLP_ENDPOINT=jaeger:4317
  - JAEGER_ENDPOINT=jaeger:4317
  - TRACING_ENVIRONMENT=docker
depends_on:
  jaeger:
    condition: service_started
```

## Performance Tuning

### Batch Processor Settings

Default configuration balances throughput and latency:

**Go:**
- Max batch size: 512 spans
- Max queue size: 2048 spans
- Batch timeout: 5 seconds
- OTLP timeout: 5 seconds

**Python:**
- Max batch size: 512 spans
- Max queue size: 2048 spans
- Schedule delay: 5000ms (5 seconds)

### Memory Usage

**In-memory storage limits:**
- Default: ~1000 traces
- Max traces: 10,000
- Max memory: ~500MB-1GB depending on trace size

To increase:
```bash
docker run -e MEMORY_MAX_TRACES=50000 jaegertracing/all-in-one:latest
```

## Reference Documents

- **Full Setup Guide:** `/docs/guides/JAEGER_SETUP.md`
- **Verification Guide:** `/docs/guides/JAEGER_VERIFICATION.md`
- **Configuration Code:**
  - Go: `/backend/internal/tracing/tracer.go`
  - Python: `/src/tracertm/observability/tracing.py`
  - Docker: `/docker-compose.yml`

## External References

- [Jaeger Official Docs](https://www.jaegertracing.io/)
- [OpenTelemetry Go Docs](https://opentelemetry.io/docs/instrumentation/go/)
- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/instrumentation/python/)
- [OTLP Protocol Spec](https://opentelemetry.io/docs/specs/otel/protocol/)
