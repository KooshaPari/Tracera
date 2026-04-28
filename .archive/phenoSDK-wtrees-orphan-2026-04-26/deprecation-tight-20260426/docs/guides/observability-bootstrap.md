# Observability Bootstrap: OpenTelemetry + structlog

Goal: Standardize traces/metrics/logs across kits and apps with minimal setup.

## Principles
- Use OpenTelemetry (OTEL) SDK for traces and metrics; exporters configurable per env.
- Use structlog for structured logs; bridge stdlib logging and OTEL correlation.
- Provide FastAPI/HTTPX/worker instrumentation helpers.

## Setup Steps (per service)
1) Configure structlog
   - JSON renderer in production; console in dev.
   - Include correlation_id, request_id, service, env.
2) Initialize OTEL
   - Resource: service.name, service.version, environment.
   - TracerProvider + MeterProvider with batch processors.
   - Exporters: OTLP gRPC/HTTP; console in dev.
3) Instrument
   - FastAPI: starlette asgi, requests/HTTPX, SQLAlchemy, redis, etc.
   - Background workers: instrument asyncio tasks; propagate context via headers.

## Example (pseudo-code)
```python
# logging.py
import structlog

def setup_logging(service: str, env: str = "dev"):
    structlog.configure(processors=[structlog.processors.add_log_level,
                                    structlog.processors.TimeStamper(),
                                    structlog.processors.JSONRenderer()])
```
```python
# otel.py
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing(service: str, version: str, environment: str):
    provider = TracerProvider(resource=Resource.create({
        "service.name": service,
        "service.version": version,
        "deployment.environment": environment,
    }))
    trace.set_tracer_provider(provider)
    # add exporter here
```

## FastAPI Integration
- Add OTEL ASGI middleware
- Add structlog request context (correlation id)

## HTTPX Integration
- Use OTEL HTTPX instrumentation
- Centralized retry/timeout policy via pydevkit wrappers

## Notes
- Keep exporters optional; disable in tests.
- Provide convenience helpers in observability-kit once stabilized.
