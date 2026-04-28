# Getting Started with Pheno-SDK

Build your first Pheno-SDK service in less than fifteen minutes. This guide walks through installation, configuration, and a minimal FastAPI project that uses configuration, database access, and observability.

## Overview

Pheno-SDK provides a modular toolkit for building production-grade Python systems. This guide will help you create a complete service with:

- **Configuration Management**: Environment-aware settings
- **Database Access**: Supabase integration with type safety
- **Observability**: Structured logging, metrics, and tracing
- **API Layer**: FastAPI with dependency injection

## Prerequisites

- **Python 3.10+**: Required for all Pheno-SDK features
- **Package Manager**: `pip` or `pipx` for installation
- **Optional Services**:
  - Supabase (database) - [Get started here](https://supabase.com)
  - Prometheus (metrics) - [Installation guide](https://prometheus.io/docs/prometheus/latest/installation/)

## 1. Install pheno-sdk

```
pip install "pheno-sdk[web-service]"
# or: pheno-sdk[full]
```

Optional extras for local development and testing:

```
pip install "pheno-sdk[dev]"
```

## 2. Scaffold the Project

```bash
mkdir pheno-sample && cd pheno-sample
python -m venv .venv
source .venv/bin/activate
pip install "pheno-sdk[web-service]"
```

Create `app/config.py` with your configuration schema:

```python
from pheno.config import AppConfig  # prefer pheno.config; config_kit remains as a shim
from pydantic import Field

class Settings(AppConfig):
    environment: str = Field(default="local")
    supabase_url: str
    supabase_key: str
```

## 3. Wire Dependencies

```python
# app/container.py
from adapter_kit import Container
from pheno.config import collect_env
from db_kit import Database
from observability import StructuredLogger, MetricsCollector, DistributedTracer
from .config import Settings

container = Container()

settings = Settings.load(env_prefix="APP_")
container.register_instance(Settings, settings)

container.register_instance(Database, Database.supabase(
    url=settings.supabase_url,
    anon_key=settings.supabase_key,
))

container.register_instance(StructuredLogger, StructuredLogger("sample", environment=settings.environment))
container.register_instance(MetricsCollector, MetricsCollector())
container.register_instance(DistributedTracer, DistributedTracer("sample"))
```

## 4. Expose an API

```python
# app/main.py
from fastapi import Depends, FastAPI
from adapter_kit import inject
from db_kit import Database
from observability import StructuredLogger

app = FastAPI()

def get_db() -> Database:
    return inject(Database)

def get_logger() -> StructuredLogger:
    return inject(StructuredLogger)

@app.get("/users")
async def list_users(db: Database = Depends(get_db), logger: StructuredLogger = Depends(get_logger)):
    logger.info("list_users", event="fetch")
    return await db.query("users", filters={"active": True})
```

Add middleware in `app/__init__.py` or `main.py`:

```python
from observability.fastapi import add_observability
from adapter_kit import inject

add_observability(app,
    logger_provider=lambda: inject(StructuredLogger),
    metrics_provider=lambda: inject(MetricsCollector),
    tracer_provider=lambda: inject(DistributedTracer)
)
```

Run the service:

```
uvicorn app.main:app --reload
```

## 5. Add Streaming Feedback (Optional)

Install stream-kit and send events to the UI:

```
pip install stream-kit
```

```python
from stream_kit import StreamingManager

manager = StreamingManager()

@app.post("/broadcast")
async def broadcast(payload: dict):
    await manager.broadcast("updates", payload)
    return {"status": "sent"}
```

## 6. Observe

Expose Prometheus metrics and structured logs:

```python
from pheno.observability import add_prometheus_endpoint

add_prometheus_endpoint(app, path="/metrics")  # simple FastAPI/Starlette helper
```

### Protecting /metrics in production
```python
import os

from observability_kit.metrics.collector import MetricsCollector
from observability_kit.exporters import make_protected_metrics_app_from_collector

metrics = MetricsCollector()
app.mount(
    "/metrics",
    make_protected_metrics_app_from_collector(
        metrics,
        bearer_token=os.environ["METRICS_BEARER_TOKEN"],
    ),
)
# Basic auth alternative:
# app.mount("/metrics", make_protected_metrics_app_from_collector(metrics, basic_auth=("user","pass")))
```


## 7. Test Locally

```
pytest
```

Use the in-memory adapters shipped by each kit for fast tests. See [Testing & Quality](../concepts/testing-quality.md).

## Next Steps
- Explore kit manuals for the capabilities you need.
- Integrate workflow-kit or orchestrator-kit for background processing.
- Configure deploy-kit to ship your service to Vercel or your cloud of choice.

For more advanced blueprints, see the examples embedded in each kit and the `integration-tests/` directory.
