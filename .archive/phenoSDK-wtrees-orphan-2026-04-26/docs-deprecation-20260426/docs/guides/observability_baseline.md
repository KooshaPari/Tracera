# Observability Baseline: OpenTelemetry + Prometheus client

Status: Draft

This guide shows how to initialize tracing/metrics with standard libraries using
small bootstrap helpers.

## Requirements

These are required dependencies of observability-kit and are installed with it:
- opentelemetry-sdk, opentelemetry-exporter-otlp, opentelemetry-instrumentation-fastapi
- prometheus-client

## Initialize OpenTelemetry

Example (without auto-export, console exporter fallback):

```python
from observability_kit.bootstrap import init_otel
init_otel(service_name="demo-api", environment="dev")
```

With OTLP HTTP exporter:

```python
init_otel(service_name="demo-api", environment="dev", otlp_endpoint="http://otel:4318/v1/traces")
```

FastAPI instrumentation (if you want auto-span for routes):

```python
from fastapi import FastAPI
from observability_kit.bootstrap import init_otel
app = FastAPI()
init_otel(service_name="demo-api", environment="dev", fastapi_app=app)
```

## Prometheus /metrics endpoint

```python
from observability_kit.bootstrap import add_prometheus_endpoint
add_prometheus_endpoint(app, path="/metrics")
```

## httpx tracing hooks (optional)

```python
from pydevkit.http import create_client, build_httpx_otel_hooks
hooks = build_httpx_otel_hooks()
client = create_client(event_hooks=hooks)
```

Async client:

```python
from pydevkit.http import create_async_client, build_async_httpx_otel_hooks
hooks = build_async_httpx_otel_hooks()
async with create_async_client(event_hooks=hooks) as client:
    ...
```

Notes:
- The bootstrap helpers initialize tracing/metrics; configure exporter/path as needed.
