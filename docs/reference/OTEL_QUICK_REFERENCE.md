# OpenTelemetry Python Quick Reference

## Quick Start

```bash
# 1. Install
pip install 'tracertm[observability]'

# 2. Verify
python -m tracertm.observability.verify_traces

# 3. Start the local stack
GRAFANA_ALLOY_BIN="$HOME/.local/bin/grafana-alloy" make dev

# 4. Enable in .env
echo "TRACING_ENABLED=true" >> .env
echo "PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=127.0.0.1:4317" >> .env

# 5. Run app
python -m uvicorn src.tracertm.api.main:app --reload

# 6. Make request and view traces
curl http://localhost:8000/health
# Open Grafana: http://localhost:3000
```

## Environment Variables

```bash
TRACING_ENABLED=true                          # Enable/disable tracing
PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=127.0.0.1:4317  # Shared collector endpoint
TRACING_ENVIRONMENT=development               # Environment name
SERVICE_NAME=tracertm-python-backend          # Service identifier
SERVICE_VERSION=1.0.0                         # Service version
```

## Custom Spans

### Using Decorator

```python
from tracertm.observability import trace_method

@trace_method(
    span_name="process.data",
    attributes={"data.type": "json"}
)
async def process_data(data: dict) -> dict:
    return result
```

### Using Context Manager

```python
from tracertm.observability import get_tracer
from opentelemetry.trace import Status, StatusCode

tracer = get_tracer()

with tracer.start_as_current_span("operation.name") as span:
    span.set_attribute("key", "value")
    try:
        result = do_work()
        span.set_status(Status(StatusCode.OK))
    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR))
        raise
```

## Common Attributes

```python
# HTTP
span.set_attribute("http.method", "GET")
span.set_attribute("http.url", "https://api.example.com")
span.set_attribute("http.status_code", 200)

# Database
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.operation", "SELECT")
span.set_attribute("db.rows_affected", 42)

# Custom
span.set_attribute("user.id", user_id)
span.set_attribute("request.id", request_id)
span.set_attribute("operation.duration_ms", duration)
```

## Backends

### Shared Phenotype Collector

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoObservability/deployments/org-observability-stack
./scripts/verify-native-setup.sh
./scripts/dev-up.sh
```

### Grafana Tempo (Production)

```yaml
# docker-compose.yml
services:
  tempo:
    image: grafana/tempo:latest
    ports:
      - "4317:4317"
      - "3200:3200"

  python-backend:
    environment:
      TRACING_ENABLED: "true"
      PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT: "tempo:4317"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OTLP not reachable | Check endpoint: `nc -zv 127.0.0.1 4317` |
| Import error | Install: `pip install 'tracertm[observability]'` |
| No traces visible | Verify: `TRACING_ENABLED=true` and backend running |
| High memory | Reduce batch processor queue size |
| Version conflicts | Upgrade: `pip install --upgrade opentelemetry-sdk` |

## Integration Points

### Automatic Instrumentation

- ✅ FastAPI HTTP requests/responses
- ✅ SQLAlchemy database queries
- ✅ HTTPX client requests
- ✅ W3C Trace Context propagation

### Manual Instrumentation

- Custom business logic via `@trace_method`
- Explicit spans with context managers
- Custom attributes for filtering/debugging

## Performance

- **Overhead**: ~10% for HTTP requests, ~2% for database
- **Batching**: Spans batched and exported asynchronously
- **Sampling**: Use `TraceIdRatioBased` sampler in production

## Code Locations

| Component | File |
|-----------|------|
| Core tracing | `src/tracertm/observability/tracing.py` |
| Instrumentation | `src/tracertm/observability/instrumentation.py` |
| Verification | `src/tracertm/observability/verify_traces.py` |
| FastAPI setup | `src/tracertm/api/main.py` (lines 778-804) |
| Dependencies | `pyproject.toml` (lines 147-159) |

## Useful Commands

```bash
# Verify installation
python -m tracertm.observability.verify_traces

# Check OTLP endpoint reachable
nc -zv 127.0.0.1 4317

# View FastAPI docs with tracing info
curl http://localhost:8000/docs

# Export traces (if backend supports)
curl http://localhost:3200/ready

# Check application traces logs
grep -i "tracing" .process-compose/logs/python-backend.log
```

## Related Files

- **Main docs**: [OTEL_PYTHON_SETUP.md](../guides/OTEL_PYTHON_SETUP.md)
- **OpenTelemetry**: https://opentelemetry.io/docs/
- **Tempo**: https://grafana.com/docs/tempo/latest/
