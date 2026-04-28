# Dependency Migration Guide

Step-by-step guide to migrate to enhanced dependencies.

## Phase 1: Core Performance (Week 1)

### 1. Replace requests with httpx

**Before**:
```python
import requests

response = requests.get("https://api.example.com")
data = response.json()
```

**After**:
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com")
    data = response.json()
```

### 2. Add msgspec for JSON

**Before**:
```python
import json

data = json.dumps(obj)
obj = json.loads(data)
```

**After**:
```python
import msgspec

encoder = msgspec.json.Encoder()
decoder = msgspec.json.Decoder()

data = encoder.encode(obj)
obj = decoder.decode(data)
```

### 3. Add anyio for async

**Before**:
```python
import asyncio

async def main():
    await asyncio.gather(task1(), task2())
```

**After**:
```python
import anyio

async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(task1)
        tg.start_soon(task2)
```

## Phase 2: Observability (Week 2)

### 1. Add structlog

**Before**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("User login", extra={"user_id": 123})
```

**After**:
```python
import structlog

logger = structlog.get_logger()
logger.info("user_login", user_id=123)
```

### 2. Add OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("operation"):
    # Do work
    pass
```

### 3. Add Prometheus

```python
from prometheus_client import Counter, Histogram

request_count = Counter("requests_total", "Total requests")
request_duration = Histogram("request_duration_seconds", "Request duration")

@request_duration.time()
def handle_request():
    request_count.inc()
    # Handle request
```

## Phase 3: Security (Week 3)

### 1. Add bcrypt for passwords

**Before**:
```python
import hashlib

hashed = hashlib.sha256(password.encode()).hexdigest()
```

**After**:
```python
import bcrypt

hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
if bcrypt.checkpw(password.encode(), hashed):
    # Password matches
    pass
```

### 2. Add cryptography

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

encrypted = cipher.encrypt(b"secret data")
decrypted = cipher.decrypt(encrypted)
```

### 3. Add Authlib

```python
from authlib.integrations.httpx_client import AsyncOAuth2Client

client = AsyncOAuth2Client(client_id="...", client_secret="...")
token = await client.fetch_token("https://...")
```

### 4. Add PyCasbin

```python
import casbin

enforcer = casbin.Enforcer("model.conf", "policy.csv")

if enforcer.enforce("alice", "data1", "read"):
    # Access allowed
    pass
```

## Phase 4: Advanced (Week 4)

### 1. Add Polars for data

**Before**:
```python
import pandas as pd

df = pd.read_csv("data.csv")
result = df[df["age"] > 30][["name", "age"]]
```

**After**:
```python
import polars as pl

df = pl.read_csv("data.csv")
result = df.filter(pl.col("age") > 30).select(["name", "age"])
```

### 2. Add Ray for distributed

```python
import ray

@ray.remote
def expensive_task(x):
    return x ** 2

ray.init()
futures = [expensive_task.remote(i) for i in range(10)]
results = ray.get(futures)
```

### 3. Add DuckDB for SQL

```python
import duckdb

result = duckdb.query("""
    SELECT name, age FROM data
    WHERE age > 30
""").to_df()
```

## Installation Steps

### Step 1: Update pyproject.toml
```bash
# Already done - new dependencies added
```

### Step 2: Install dependencies
```bash
# Install all enhanced dependencies
uv sync --all

# Or install specific groups
uv sync --group observability
uv sync --group security
uv sync --group distributed
uv sync --group data
```

### Step 3: Update imports
- Replace `requests` with `httpx`
- Replace `json` with `msgspec`
- Replace `asyncio` with `anyio`
- Replace `logging` with `structlog`

### Step 4: Update code
- Convert sync code to async where possible
- Add structured logging
- Add observability instrumentation
- Add security measures

### Step 5: Test
```bash
# Run tests
uv run poe test

# Run quality checks
uv run poe all

# Benchmark performance
uv run poe test-benchmark
```

## Rollback Plan

If issues occur:

```bash
# Revert pyproject.toml
git checkout pyproject.toml

# Reinstall original dependencies
uv sync

# Revert code changes
git checkout src/
```

## Performance Verification

### Before Migration
```bash
uv run poe test-benchmark
# Record baseline metrics
```

### After Migration
```bash
uv run poe test-benchmark
# Compare with baseline
# Expected improvements:
# - JSON: 50x faster
# - HTTP: 2-5x faster
# - Data: 10-100x faster
```

## Troubleshooting

### httpx issues
- Ensure async context
- Use `AsyncClient` for async code
- Use `Client` for sync code

### msgspec issues
- Ensure Pydantic models are compatible
- Use `msgspec.json.Encoder()` for encoding
- Use `msgspec.json.Decoder()` for decoding

### anyio issues
- Use `anyio.create_task_group()` for concurrency
- Use `anyio.from_thread.run()` for sync context
- Use `anyio.to_thread.run_sync()` for blocking calls

### structlog issues
- Configure before first use
- Use `structlog.get_logger()` to get logger
- Use keyword arguments for context

## Timeline

- **Week 1**: Core performance (httpx, msgspec, anyio)
- **Week 2**: Observability (structlog, OpenTelemetry, Prometheus)
- **Week 3**: Security (cryptography, bcrypt, Authlib, PyCasbin)
- **Week 4**: Advanced (Ray, Polars, DuckDB)

## Success Criteria

✅ All tests pass  
✅ Performance improved  
✅ No breaking changes  
✅ Documentation updated  
✅ Team trained  

## Next Steps

1. Review this guide
2. Start Phase 1 migration
3. Run tests after each phase
4. Benchmark improvements
5. Document learnings

