# Enhanced Dependencies Guide

Comprehensive guide to new and improved dependencies added to TraceRTM.

## New Core Dependencies

### HTTP & Networking
**httpx** (0.28.1+)
- Modern async-first HTTP client
- Replaces requests
- 2-5x faster
- Full async/await support

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com")
```

**aiohttp** (3.8.0+)
- Async HTTP client/server
- WebSocket support
- Connection pooling

### Serialization
**msgspec** (0.18.0+)
- 50x faster JSON serialization
- Type-safe encoding/decoding
- Supports Pydantic models

```python
import msgspec

encoder = msgspec.json.Encoder()
decoder = msgspec.json.Decoder(type=MyModel)
```

**msgpack** (1.0.5+)
- Compact binary format
- Faster than JSON
- Language-agnostic

### Async/Concurrency
**anyio** (4.0.0+)
- Abstraction layer for asyncio/trio
- Better error handling
- Structured concurrency

```python
import anyio

async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(task1)
        tg.start_soon(task2)
```

### Logging & Observability
**structlog** (24.1.0+)
- Enterprise-grade structured logging
- JSON output
- Context propagation

```python
import structlog

log = structlog.get_logger()
log.info("event", user_id=123, action="login")
```

**OpenTelemetry** (1.24.0+)
- Distributed tracing
- Metrics collection
- Standardized observability

**Prometheus** (0.20.0+)
- Metrics collection
- Time-series database
- Alerting

### Security & Cryptography
**cryptography** (41.0.0+)
- Encryption/decryption
- Digital signatures
- Key management

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(b"secret")
```

**bcrypt** (4.1.0+)
- Password hashing
- Secure by default
- Adaptive cost

```python
import bcrypt

hashed = bcrypt.hashpw(password, bcrypt.gensalt())
bcrypt.checkpw(password, hashed)
```

**PyJWT** (2.10.0+)
- JWT encoding/decoding
- Token management
- Signature verification

**Authlib** (1.3.0+)
- OAuth/OIDC support
- JWT handling
- Multi-protocol support

**PyCasbin** (1.35.0+)
- RBAC/ABAC authorization
- Policy management
- Access control

## Optional Dependency Groups

### Observability
```bash
uv sync --group observability
```
- OpenTelemetry
- Prometheus
- structlog

### Security
```bash
uv sync --group security
```
- cryptography
- bcrypt
- PyJWT
- Authlib
- PyCasbin

### Distributed Computing
```bash
uv sync --group distributed
```
- Ray (distributed Python)
- Dask (parallel computing)

### Data Processing
```bash
uv sync --group data
```
- Polars (10-100x faster than Pandas)
- DuckDB (SQL on data)
- Ibis (data abstraction)

### All Enhanced
```bash
uv sync --all
```
- All optional groups
- All development tools

## Usage Examples

### Async HTTP with httpx
```python
import httpx

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()
```

### Fast JSON with msgspec
```python
import msgspec
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

encoder = msgspec.json.Encoder()
user = User(id=1, name="Alice")
json_bytes = encoder.encode(user)
```

### Structured Logging
```python
import structlog

log = structlog.get_logger()
log.info("user_login", user_id=123, ip="192.168.1.1")
```

### Distributed Computing with Ray
```python
import ray

@ray.remote
def expensive_task(x):
    return x ** 2

ray.init()
futures = [expensive_task.remote(i) for i in range(10)]
results = ray.get(futures)
```

### Data Processing with Polars
```python
import polars as pl

df = pl.read_csv("data.csv")
result = df.filter(pl.col("age") > 30).select(["name", "age"])
```

## Performance Improvements

| Tool | Improvement | Use Case |
|------|-------------|----------|
| msgspec | 50x faster | JSON serialization |
| httpx | 2-5x faster | HTTP requests |
| Polars | 10-100x faster | Data processing |
| Ray | Linear scaling | Distributed computing |
| bcrypt | Secure | Password hashing |

## Migration Guide

### Phase 1: Core (Week 1)
- Replace requests with httpx
- Add msgspec for JSON
- Add anyio for async

### Phase 2: Observability (Week 2)
- Add structlog
- Add OpenTelemetry
- Add Prometheus

### Phase 3: Security (Week 3)
- Add cryptography
- Add bcrypt
- Add Authlib

### Phase 4: Advanced (Week 4)
- Add Ray for distributed
- Add Polars for data
- Add DuckDB for SQL

## Installation

### Install all enhanced dependencies
```bash
uv sync --all
```

### Install specific groups
```bash
uv sync --group observability
uv sync --group security
uv sync --group distributed
uv sync --group data
```

## Best Practices

1. **Use httpx** instead of requests
2. **Use msgspec** for JSON serialization
3. **Use anyio** for async abstractions
4. **Use structlog** for structured logging
5. **Use bcrypt** for password hashing
6. **Use Polars** for data processing
7. **Use Ray** for distributed computing
8. **Use OpenTelemetry** for observability

## References

- httpx: https://www.python-httpx.org/
- msgspec: https://jcristharif.com/msgspec/
- anyio: https://anyio.readthedocs.io/
- structlog: https://www.structlog.org/
- OpenTelemetry: https://opentelemetry.io/
- Polars: https://www.pola.rs/
- Ray: https://www.ray.io/
- Authlib: https://authlib.org/
- PyCasbin: https://casbin.org/

