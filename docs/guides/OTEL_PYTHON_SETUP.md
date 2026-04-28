# OpenTelemetry Python Backend Setup Guide

## Overview

This guide covers setting up and verifying OpenTelemetry (OTEL) instrumentation for the TraceRTM Python backend. The setup provides distributed tracing, performance monitoring, and observability across the entire application stack.

**Current Status:** ✅ Fully implemented and verified

## What is OpenTelemetry?

OpenTelemetry is an open-source observability framework that standardizes the collection, processing, and exporting of telemetry data (traces, metrics, logs). It provides:

- **Distributed Tracing**: Track requests across service boundaries
- **Automatic Instrumentation**: Zero-code instrumentation for common frameworks
- **Standardized Context Propagation**: W3C Trace Context for cross-service correlation
- **OTLP Export**: Protocol for sending telemetry to collector backends (Tempo, etc.)

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│ Python Backend (TraceRTM)                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ FastAPI Application                                 │   │
│  │  - HTTP Request/Response spans                      │   │
│  │  - Status codes, latency, headers                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ OpenTelemetry Instrumentation                       │   │
│  │  - FastAPI automatic spans                          │   │
│  │  - SQLAlchemy query tracing                         │   │
│  │  - HTTP client (HTTPX) spans                        │   │
│  │  - Custom spans (@trace_method decorator)           │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Tracer Provider                                      │   │
│  │  - Resource metadata (service name, version, env)   │   │
│  │  - Batch span processor                             │   │
│  │  - W3C Trace Context propagator                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ OTLP Exporter (gRPC)                                │   │
│  │  - Exports to 127.0.0.1:4317 (configurable)        │   │
│  │  - Batch processing for efficiency                  │   │
│  │  - Automatic retry and backoff                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Grafana Alloy / Shared Collector│
        │ Tempo / Loki / Prometheus      │
        │ OTLP gRPC on 127.0.0.1:4317    │
        └───────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.12+
- pip or poetry for package management

### Step 1: Install Observability Dependencies

The observability dependencies are defined in the `[project.optional-dependencies.observability]` section of `pyproject.toml`.

**Install using pip:**
```bash
pip install 'tracertm[observability]'
```

**Or individually:**
```bash
pip install \
  'opentelemetry-api>=1.39.1' \
  'opentelemetry-sdk>=1.39.1' \
  'opentelemetry-exporter-otlp-proto-grpc>=1.39.1' \
  'opentelemetry-instrumentation-fastapi>=0.60b1' \
  'opentelemetry-instrumentation-sqlalchemy>=0.60b1' \
  'opentelemetry-instrumentation-httpx>=0.59b0' \
  'opentelemetry-instrumentation-requests>=0.46b0' \
  'opentelemetry-instrumentation-redis>=0.59b0' \
  'prometheus-client>=0.24.1'
```

**Verify installation:**
```bash
python -c "from opentelemetry import trace; from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter; print('✅ OpenTelemetry installed')"
```

### Step 2: Verify Installation

Run the verification script to ensure all components are properly installed:

```bash
python -m tracertm.observability.verify_traces
```

Expected output:
```
================================================================================
OpenTelemetry Instrumentation Verification
================================================================================

Verifying instrumentation packages...
✅ FastAPI instrumentation available
✅ SQLAlchemy instrumentation available
✅ HTTPX instrumentation available
...

Verifying tracing setup...
✅ Tracing initialized successfully
✅ Tracer instance available
✅ Test spans created successfully
✅ Spans flushed successfully

================================================================================
VERIFICATION SUMMARY
================================================================================

✅ All verification checks passed!
Traces are being generated and exported to OTLP endpoint.
```

## Configuration

### Environment Variables

The tracing setup is controlled by the following environment variables:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `TRACING_ENABLED` | Enable/disable distributed tracing | `false` | `true` |
| `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` | Shared collector endpoint | `127.0.0.1:4317` | `otel-collector:4317` |
| `OTLP_ENDPOINT` | Legacy collector endpoint fallback | `127.0.0.1:4317` | `otel-collector:4317` |
| `TRACING_ENVIRONMENT` | Deployment environment | `development` | `production`, `staging` |
| `SERVICE_NAME` | Service name for tracing | `tracertm-python-backend` | Custom name |
| `SERVICE_VERSION` | Service version | `1.0.0` | `0.2.0` |

> Primary setup uses `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT`; `OTLP_ENDPOINT` remains only for
> older environment files that have not been normalized yet.

### Configuration in Development

Create a `.env` file in the project root:

```bash
# .env
TRACING_ENABLED=true
PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=127.0.0.1:4317
TRACING_ENVIRONMENT=development
SERVICE_NAME=tracertm-python-backend
SERVICE_VERSION=0.2.0
```

### Configuration in Production

Set environment variables in your deployment environment:

**Docker:**
```dockerfile
ENV TRACING_ENABLED=true
ENV PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=otel-collector:4317
ENV TRACING_ENVIRONMENT=production
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tracertm-config
data:
  TRACING_ENABLED: "true"
  PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT: "otel-collector:4317"
  TRACING_ENVIRONMENT: "production"
```

**Docker Compose:**
```yaml
services:
  python-backend:
    environment:
      TRACING_ENABLED: "true"
      PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT: "otel-collector:4317"
      TRACING_ENVIRONMENT: "development"
```

## Backend Setup

### Shared Phenotype Collector

The shared Phenotype collector is the recommended distributed tracing path for local development
and org-level deployments.

**Start the shared stack:**
```bash
make dev
```

**Access Grafana:**
- URL: `http://localhost:3000`

### Grafana Tempo

Grafana Tempo is recommended for scalable trace storage and querying.

**Start Tempo with Docker Compose:**

Create `docker-compose.yml`:
```yaml
version: '3'
services:
  tempo:
    image: grafana/tempo:latest
    ports:
      - "4317:4317"      # OTLP gRPC receiver
      - "4318:4318"      # OTLP HTTP receiver
      - "3200:3200"      # Tempo API

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
```

**Access Grafana:**
- URL: `http://localhost:3000`

## How It Works

### Initialization Flow

When the Python backend starts with `TRACING_ENABLED=true`:

```python
# src/tracertm/api/main.py
if tracing_enabled:
    from tracertm.observability import init_tracing, instrument_all, instrument_app

    # 1. Initialize tracer provider with OTLP exporter
    init_tracing(
        service_name="tracertm-python-backend",
        service_version="1.0.0",
        environment=os.getenv("TRACING_ENVIRONMENT", "development"),
        otlp_endpoint=os.getenv("PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT", "127.0.0.1:4317"),
    )

    # 2. Instrument FastAPI for automatic HTTP spans
    instrument_app(app)

    # 3. Instrument HTTP clients and Redis
    instrument_all()
```

### Automatic Instrumentation

**FastAPI Requests:**
Each HTTP request creates a root span with:
- Request method and path
- Status code
- Request duration
- Request/response headers (sanitized)

Example trace:
```
GET /api/v1/projects
├── GET projects
├── SELECT * FROM projects
└── Response: 200 OK (15ms)
```

**SQLAlchemy Queries:**
Database queries are automatically traced with:
- SQL statement (sanitized)
- Query parameters
- Query duration
- Connection pool statistics

**HTTP Clients:**
Outbound HTTP requests via HTTPX are traced with:
- Request method and URL
- Status code
- Request/response headers
- Total duration

### Custom Spans

Use the `@trace_method` decorator for custom tracing:

```python
from tracertm.observability import trace_method

@trace_method(
    span_name="custom.operation",
    attributes={"operation.type": "analysis"}
)
async def analyze_data(data: dict) -> dict:
    # Your code here
    return result
```

## Usage Examples

### Example 1: Enable Tracing for Development

```bash
# Set environment variable
export TRACING_ENABLED=true
export PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=127.0.0.1:4317

# Start the shared org stack in another terminal
make dev

# Run the backend
python -m uvicorn src.tracertm.api.main:app --reload

# Make a request
curl http://localhost:8000/health

# View traces in Grafana
# http://localhost:3000
```

### Example 2: Production Deployment with Tempo

```bash
# In docker-compose.yml for production
services:
  tempo:
    image: grafana/tempo:latest
    environment:
      LOG_LEVEL: info

  python-backend:
    environment:
      TRACING_ENABLED: "true"
      PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT: "tempo:4317"
      TRACING_ENVIRONMENT: "production"
```

### Example 3: Custom Application Tracing

```python
from tracertm.observability import get_tracer, trace_method

# Get tracer
tracer = get_tracer()

# Create span manually
with tracer.start_as_current_span("process.data") as span:
    span.set_attribute("data.size", len(data))
    span.set_attribute("operation.id", operation_id)

    try:
        result = process_expensive_operation(data)
        span.set_status(trace.Status(trace.StatusCode.OK))
    except Exception as e:
        span.record_exception(e)
        span.set_status(trace.Status(trace.StatusCode.ERROR))
        raise

# Or use decorator
@trace_method(span_name="import.project", attributes={"import.source": "github"})
async def import_github_project(org: str, repo: str) -> Project:
    # Implementation
    pass
```

## Span Attributes

Spans automatically include the following attributes:

### HTTP Request Spans
- `http.method` - HTTP method (GET, POST, etc.)
- `http.url` - Request URL
- `http.status_code` - Response status code
- `http.request.header.*` - Request headers (sanitized)
- `http.response.header.*` - Response headers (sanitized)
- `http.client_ip` - Client IP address
- `http.scheme` - http or https

### Database Query Spans
- `db.system` - Database type (postgresql, mysql, etc.)
- `db.statement` - SQL statement (sanitized)
- `db.operation` - SQL operation (SELECT, INSERT, UPDATE, DELETE)
- `db.rows_affected` - Number of rows affected
- `pool.name` - Connection pool name
- `pool.open_connections` - Open connections

### HTTP Client Spans
- `http.method` - HTTP method
- `http.url` - Target URL
- `http.status_code` - Response status code
- `http.client` - Client library (httpx, requests)
- `peer.service` - Target service name

### Custom Spans
- `span.kind` - INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER
- `function.name` - Function name
- `function.module` - Python module
- Custom attributes from decorator

## Troubleshooting

### Traces Not Appearing

**Issue:** Spans are created but not exported to OTLP backend.

**Solutions:**
1. Verify OTLP endpoint is reachable:
   ```bash
   nc -zv 127.0.0.1 4317
   ```

2. Check environment variables:
   ```bash
   echo $TRACING_ENABLED
   echo $PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT
   ```

3. Verify the shared collector stack is running:
   ```bash
   docker ps | grep -E 'alloy|tempo|grafana'
   ```

4. Check application logs for errors:
   ```bash
   grep -i "tracing\|otlp\|exporter" application.log
   ```

### OTLP Exporter Not Available

**Error:** `APM instrumentation not available: No module named 'opentelemetry.exporter'`

**Solution:** Install observability dependencies:
```bash
pip install 'tracertm[observability]'
```

### Version Conflicts

**Error:** `ImportError: cannot import name 'LogData' from 'opentelemetry.sdk._logs'`

**Solution:** Upgrade all OpenTelemetry packages to compatible versions:
```bash
pip install --upgrade opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
```

### High Memory Usage

**Issue:** Span processor consumes too much memory.

**Solution:** Adjust batch processor settings in `src/tracertm/observability/tracing.py`:

```python
provider.add_span_processor(
    BatchSpanProcessor(
        otlp_exporter,
        max_queue_size=1024,      # Reduce from 2048
        max_export_batch_size=256, # Reduce from 512
        schedule_delay_millis=10000, # Increase from 5000
    )
)
```

### Spans Not Flushing

**Issue:** Spans remain in buffer when application shuts down.

**Solution:** Ensure graceful shutdown flushes spans:

```python
import signal

def shutdown_handler(signum, frame):
    logger.info("Shutting down...")
    tracer_provider = trace.get_tracer_provider()
    tracer_provider.force_flush(timeout_millis=5000)
    # Shutdown application

signal.signal(signal.SIGTERM, shutdown_handler)
```

## Performance Impact

### Overhead

Typical performance overhead with instrumentation enabled:

| Operation | Baseline | With Tracing | Overhead |
|-----------|----------|--------------|----------|
| HTTP request | 10ms | 11ms | ~10% |
| Database query | 50ms | 51ms | ~2% |
| Cache operation | 5ms | 5.5ms | ~10% |

The overhead scales sub-linearly because span export happens asynchronously via batch processing.

### Optimization Tips

1. **Selective Instrumentation**: Only instrument critical operations:
   ```python
   if os.getenv("TRACING_ENABLED") == "true":
       instrument_app(app)
       instrument_database(engine)
   ```

2. **Batch Export Settings**: Tune for your workload:
   ```python
   BatchSpanProcessor(
       exporter,
       max_queue_size=2048,        # Larger queue = less memory pressure
       max_export_batch_size=512,  # Larger batches = fewer exports
       schedule_delay_millis=5000, # Longer delay = fewer exports
   )
   ```

3. **Sampling**: Export only a percentage of traces in production:
   ```python
   from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

   sampler = TraceIdRatioBased(0.1)  # Sample 10% of traces
   provider = TracerProvider(resource=resource, sampler=sampler)
   ```

## Integration with Go Backend

The Python backend automatically integrates with the Go backend via W3C Trace Context propagation. When a request originates from the Go backend:

1. Go backend creates a root span and propagates trace context via HTTP headers
2. Python backend receives the trace context (W3C `traceparent` header)
3. Python creates child spans under the same trace ID
4. Both services export to the same OTLP backend
5. Traces are automatically correlated in Grafana/Tempo UI

**Example distributed trace (Go → Python):**

```
Trace ID: a4fb4a1d1a96d312516023370d5f7f8f

├── Span: GET /api/v1/projects (Go backend)
│   └── Span: list_projects (Python backend)
│       ├── Span: SELECT * FROM projects
│       └── Response: 200 OK
```

## Reference

### Code Files

- **Core Tracing**: `/src/tracertm/observability/tracing.py`
  - Tracer initialization
  - OTLP exporter configuration
  - Batch span processor setup
  - W3C Trace Context propagation

- **Instrumentation**: `/src/tracertm/observability/instrumentation.py`
  - FastAPI automatic instrumentation
  - SQLAlchemy query tracing
  - HTTP client instrumentation
  - Redis instrumentation

- **Verification**: `/src/tracertm/observability/verify_traces.py`
  - Test trace generation
  - Package availability checks
  - End-to-end verification

### Related Documentation

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [OTLP Exporter Documentation](https://opentelemetry.io/docs/reference/specification/otlp/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Grafana Tempo Documentation](https://grafana.com/docs/tempo/latest/)

### Configuration Files

- **Main Application**: `src/tracertm/api/main.py` (lines 778-804)
- **Pyproject**: `pyproject.toml` (lines 147-159, observability dependencies)

## Next Steps

### Recommended Setup Path

1. ✅ **Install dependencies** - `pip install 'tracertm[observability]'`
2. ✅ **Verify installation** - Run `python -m tracertm.observability.verify_traces`
3. **Start backend** - `make dev`
4. **Enable tracing** - Set `TRACING_ENABLED=true`
5. **View traces** - Open `http://localhost:3000`

### Advanced Topics

- [Custom metrics with Prometheus](./prometheus-metrics.md)
- [Log correlation with trace IDs](./log-correlation.md)
- [Performance profiling with OpenTelemetry](./performance-profiling.md)
- [Multi-service trace correlation](./distributed-tracing.md)

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review application logs: `tail -f .process-compose/logs/python-backend.log`
3. Test with verification script: `python -m tracertm.observability.verify_traces`
4. Consult [OpenTelemetry documentation](https://opentelemetry.io/docs/)
