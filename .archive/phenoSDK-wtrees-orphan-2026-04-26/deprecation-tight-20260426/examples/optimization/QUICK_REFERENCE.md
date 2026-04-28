# Performance Optimization Quick Reference

One-page reference for pheno-sdk optimization utilities.

## Import

```python
from pheno.optimization import (
    # HTTP Pooling
    get_shared_session, SessionPool,
    # Compression
    add_gzip_compression, optimize_response_middleware,
    # Rate Limiting
    RateLimiter, rate_limit,
    # Database Pooling
    get_supabase, configure_supabase_pooling,
    # Utilities
    optimize_fastapi_app, get_optimization_status,
)
```

## One-Line Optimization

```python
from pheno.optimization import optimize_fastapi_app

optimize_fastapi_app(app, requests_per_minute=100)
```

**Applies:** Compression, rate limiting, HTTP pooling

## HTTP Connection Pooling (4x OAuth, 10x queries)

```python
# Get shared session
session = await get_shared_session()
async with session.get("https://api.example.com") as resp:
    data = await resp.json()

# Configure (optional)
pool = await SessionPool.get_instance()
await pool.configure(total=200, per_host=50, dns_cache_ttl=600)
```

## Response Compression (60-90% reduction)

```python
# Simple
app = add_gzip_compression(app, minimum_size=500)

# Full optimization
app = optimize_response_middleware(
    app,
    enable_compression=True,
    enable_headers=True,
    minimum_size=500,
    compresslevel=5,
)
```

## Rate Limiting

```python
# Decorator (per-endpoint)
@app.post("/api/endpoint")
@rate_limit(requests_per_minute=100)
async def endpoint(request: Request):
    return {"status": "ok"}

# Middleware (global)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    burst_multiplier=2.0,
)

# Per-user
def get_user_key(req: Request) -> str:
    return f"user:{req.state.user_id}"

@rate_limit(requests_per_minute=100, key_func=get_user_key)
async def user_action(request: Request):
    return {"status": "ok"}
```

## Database Pooling (6x queries)

```python
# Direct usage
client = get_supabase()
result = client.table("users").select("*").execute()

# With user token (RLS)
client = get_supabase(access_token=user_token)

# FastAPI dependency
get_db = create_supabase_dependency(use_cache=True)

@app.get("/users")
async def list_users(db=Depends(get_db)):
    return db.table("users").select("*").execute()

# Configure
configure_supabase_pooling(
    pool_mode="transaction",
    max_connections=200,
    client_cache_ttl=600,
)
```

## Complete Example

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from pheno.optimization import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await SessionPool.get_instance()
    await pool.configure(total=200, per_host=50)
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)
get_db = create_supabase_dependency()

@app.get("/")
async def root():
    return {"message": "Optimized API"}

@app.get("/users")
async def list_users(db=Depends(get_db)):
    return db.table("users").select("*").execute()

@app.get("/external")
async def call_external():
    session = await get_shared_session()
    async with session.get("https://api.example.com") as resp:
        return await resp.json()

@app.post("/limited")
@rate_limit(requests_per_minute=10)
async def rate_limited(request: Request):
    return {"status": "ok"}

optimize_fastapi_app(app, requests_per_minute=100)
```

## Health Check

```python
@app.get("/health/optimizations")
async def health():
    return get_optimization_status()
```

**Response:**
```json
{
  "http_pooling": {"status": "active", "performance_impact": "4x OAuth, 10x queries"},
  "db_pooling": {"status": "active", "performance_impact": "6x DB queries"},
  "overall_impact": {"http_speedup": "4-10x", "db_speedup": "6x", "bandwidth_reduction": "70-80%"}
}
```

## Configuration

### HTTP Pooling
```python
total=200              # Max connections
per_host=50           # Per-host limit
dns_cache_ttl=600     # DNS cache (seconds)
```

### Compression
```python
minimum_size=500      # Min size to compress
compresslevel=5       # Level 1-9 (5=balanced)
```

### Rate Limiting
```python
requests_per_minute=60    # Sustained rate
burst_multiplier=2.0      # Burst allowance
```

### Database Pooling
```python
pool_mode="transaction"   # transaction|session|statement
max_connections=200       # Max pooled connections
client_cache_ttl=600      # Cache TTL (seconds)
```

## Environment Variables

```bash
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-key"
```

## Performance Metrics

| Optimization | Improvement |
|-------------|-------------|
| HTTP Pooling | 4-10x faster |
| DB Pooling | 6x faster |
| Compression | 60-90% reduction |
| Throughput | 1000+ req/s |

## Troubleshooting

### HTTP Pooling
```python
pool = await SessionPool.get_instance()
print(pool.get_stats())
```

### DB Pooling
```python
from pheno.optimization import cache_stats, optimize_query_pooling
print(cache_stats())
print(optimize_query_pooling())
```

### Compression
```bash
curl -H "Accept-Encoding: gzip" -I http://localhost:8000/endpoint
# Check: Content-Encoding: gzip
```

### Rate Limiting
```python
limiter = RateLimiter()
print(f"Remaining: {limiter.get_remaining('key')}")
```

## Benchmarking

```bash
# HTTP pooling
python examples/optimization/benchmark_http_pooling.py

# DB pooling
python examples/optimization/benchmark_db_pooling.py

# Load test
locust -f locustfile.py --host=http://localhost:8000
```

## Documentation

- **Full Guide:** `pheno-sdk/src/pheno/optimization/README.md`
- **Benchmarks:** `examples/optimization/BENCHMARKING.md`
- **Performance:** `examples/optimization/PERFORMANCE_REPORT.md`
- **Example:** `examples/optimization/fastapi_complete_example.py`

## Run Example

```bash
cd pheno-sdk
uvicorn examples.optimization.fastapi_complete_example:app --reload
```

**Endpoints:**
- `GET /` - Overview
- `GET /health/optimizations` - Status
- `GET /users` - DB pooling example
- `GET /external/get` - HTTP pooling example
- `GET /api/limited` - Rate limiting example
- `GET /large-response` - Compression example

---

**Full documentation:** See `pheno-sdk/src/pheno/optimization/README.md`
