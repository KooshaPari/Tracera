# Performance Optimization Benchmarking Guide

This guide provides comprehensive benchmarking instructions to measure and validate the performance improvements from the optimization utilities.

## Performance Claims

| Optimization | Claimed Improvement | Benchmark Method |
|-------------|-------------------|-----------------|
| HTTP Connection Pooling | 4x OAuth, 10x queries | Concurrent request benchmark |
| Response Compression | 60-90% size reduction | Response size comparison |
| Rate Limiting | API protection | Load testing |
| Database Pooling | 6x DB queries | Database query benchmark |

## Setup

### 1. Install Dependencies

```bash
pip install aiohttp supabase fastapi uvicorn pytest pytest-asyncio locust httpx
```

### 2. Environment Variables

```bash
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

### 3. Start Example Application

```bash
cd pheno-sdk/examples/optimization
uvicorn fastapi_complete_example:app --reload
```

## Benchmark 1: HTTP Connection Pooling

### Goal
Measure speedup from connection pooling vs creating new connections each time.

### Benchmark Script

Create `benchmark_http_pooling.py`:

```python
"""Benchmark HTTP connection pooling performance."""

import asyncio
import time
import aiohttp
from statistics import mean, stdev

from pheno.optimization import get_shared_session, SessionPool


async def benchmark_without_pooling(num_requests: int = 100):
    """Benchmark without connection pooling (new session each request)."""
    times = []

    for _ in range(num_requests):
        start = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://httpbin.org/get") as resp:
                await resp.text()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return times


async def benchmark_with_pooling(num_requests: int = 100):
    """Benchmark with connection pooling (reuses session)."""
    session = await get_shared_session()
    times = []

    for _ in range(num_requests):
        start = time.perf_counter()
        async with session.get("https://httpbin.org/get") as resp:
            await resp.text()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return times


async def benchmark_concurrent(num_concurrent: int = 50):
    """Benchmark concurrent requests with pooling."""
    session = await get_shared_session()

    async def make_request():
        start = time.perf_counter()
        async with session.get("https://httpbin.org/get") as resp:
            await resp.text()
        return time.perf_counter() - start

    start_total = time.perf_counter()
    times = await asyncio.gather(*[make_request() for _ in range(num_concurrent)])
    total_time = time.perf_counter() - start_total

    return times, total_time


async def main():
    print("=" * 60)
    print("HTTP CONNECTION POOLING BENCHMARK")
    print("=" * 60)

    # Benchmark without pooling
    print("\n1. Without connection pooling (100 requests)...")
    times_without = await benchmark_without_pooling(100)
    avg_without = mean(times_without)
    std_without = stdev(times_without)
    print(f"   Average: {avg_without:.3f}s")
    print(f"   Std Dev: {std_without:.3f}s")
    print(f"   Total: {sum(times_without):.2f}s")

    # Benchmark with pooling
    print("\n2. With connection pooling (100 requests)...")
    times_with = await benchmark_with_pooling(100)
    avg_with = mean(times_with)
    std_with = stdev(times_with)
    print(f"   Average: {avg_with:.3f}s")
    print(f"   Std Dev: {std_with:.3f}s")
    print(f"   Total: {sum(times_with):.2f}s")

    # Calculate speedup
    speedup = avg_without / avg_with
    print(f"\n📊 SPEEDUP: {speedup:.1f}x faster with connection pooling")

    # Concurrent benchmark
    print("\n3. Concurrent requests (50 simultaneous)...")
    times_concurrent, total_concurrent = await benchmark_concurrent(50)
    avg_concurrent = mean(times_concurrent)
    print(f"   Individual avg: {avg_concurrent:.3f}s")
    print(f"   Total time: {total_concurrent:.2f}s")
    print(f"   Throughput: {50/total_concurrent:.1f} req/s")

    # Cleanup
    pool = await SessionPool.get_instance()
    await pool.close()

    print("\n" + "=" * 60)
    print("✅ Benchmark complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

### Run Benchmark

```bash
python benchmark_http_pooling.py
```

### Expected Results

- **Sequential speedup:** 3-5x faster with pooling
- **Concurrent throughput:** 10x+ improvement
- **Latency reduction:** 50-80% with pooling

## Benchmark 2: Database Connection Pooling

### Goal
Measure database query speedup from Supabase client caching.

### Benchmark Script

Create `benchmark_db_pooling.py`:

```python
"""Benchmark database connection pooling."""

import time
from statistics import mean, stdev

from pheno.optimization import get_supabase, reset_supabase_cache


def benchmark_without_cache(num_queries: int = 100):
    """Benchmark without client caching (creates new client each time)."""
    from supabase import create_client
    import os

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    times = []
    for _ in range(num_queries):
        start = time.perf_counter()
        client = create_client(url, key)
        result = client.table("users").select("id").limit(1).execute()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return times


def benchmark_with_cache(num_queries: int = 100):
    """Benchmark with client caching (reuses cached client)."""
    times = []

    for _ in range(num_queries):
        start = time.perf_counter()
        client = get_supabase()
        result = client.table("users").select("id").limit(1).execute()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return times


def main():
    print("=" * 60)
    print("DATABASE CONNECTION POOLING BENCHMARK")
    print("=" * 60)

    # Benchmark without caching
    print("\n1. Without client caching (100 queries)...")
    reset_supabase_cache()
    times_without = benchmark_without_cache(100)
    avg_without = mean(times_without)
    std_without = stdev(times_without)
    print(f"   Average: {avg_without:.3f}s")
    print(f"   Std Dev: {std_without:.3f}s")
    print(f"   Total: {sum(times_without):.2f}s")

    # Benchmark with caching
    print("\n2. With client caching (100 queries)...")
    reset_supabase_cache()
    # First query creates cache
    get_supabase()

    times_with = benchmark_with_cache(100)
    avg_with = mean(times_with)
    std_with = stdev(times_with)
    print(f"   Average: {avg_with:.3f}s")
    print(f"   Std Dev: {std_with:.3f}s")
    print(f"   Total: {sum(times_with):.2f}s")

    # Calculate speedup
    speedup = avg_without / avg_with
    print(f"\n📊 SPEEDUP: {speedup:.1f}x faster with connection pooling")

    # Cache statistics
    from pheno.optimization import cache_stats
    stats = cache_stats()
    print(f"\n📈 Cache Stats:")
    print(f"   Entries: {stats['entries']}")
    print(f"   TTL: {stats['ttl_seconds']}s")

    print("\n" + "=" * 60)
    print("✅ Benchmark complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

### Run Benchmark

```bash
python benchmark_db_pooling.py
```

### Expected Results

- **Query speedup:** 5-8x faster with caching
- **Cache hit rate:** >95% after warmup
- **Latency reduction:** 80-90%

## Benchmark 3: Response Compression

### Goal
Measure response size reduction from GZip compression.

### Benchmark Script

```bash
#!/bin/bash
# benchmark_compression.sh

echo "==================================================="
echo "RESPONSE COMPRESSION BENCHMARK"
echo "==================================================="

# Start the example app in background
echo "Starting app..."
uvicorn examples.optimization.fastapi_complete_example:app --port 8000 &
APP_PID=$!
sleep 3

# Test without compression
echo -e "\n1. Large response WITHOUT compression:"
size_uncompressed=$(curl -s -H "Accept-Encoding: identity" \
  http://localhost:8000/large-response \
  -w "%{size_download}" -o /dev/null)
echo "   Size: $size_uncompressed bytes"

# Test with compression
echo -e "\n2. Large response WITH compression:"
size_compressed=$(curl -s -H "Accept-Encoding: gzip" \
  http://localhost:8000/large-response \
  -w "%{size_download}" -o /dev/null)
echo "   Size: $size_compressed bytes"

# Calculate reduction
reduction=$(echo "scale=2; 100 - ($size_compressed / $size_uncompressed * 100)" | bc)
echo -e "\n📊 SIZE REDUCTION: ${reduction}%"

# Cleanup
kill $APP_PID

echo -e "\n==================================================="
echo "✅ Benchmark complete"
echo "==================================================="
```

### Run Benchmark

```bash
chmod +x benchmark_compression.sh
./benchmark_compression.sh
```

### Expected Results

- **Size reduction:** 60-90% for JSON responses
- **Transfer time:** 70-80% faster on slow connections
- **Overhead:** <5ms compression time

## Benchmark 4: Rate Limiting

### Goal
Verify rate limiting works correctly and protects API from overload.

### Benchmark Script

Create `benchmark_rate_limiting.py`:

```python
"""Benchmark and test rate limiting."""

import asyncio
import time
import httpx
from statistics import mean


async def test_rate_limit(
    url: str = "http://localhost:8000/api/limited",
    num_requests: int = 20,
):
    """Test rate limiting by making requests beyond limit."""
    async with httpx.AsyncClient() as client:
        results = []

        print(f"Making {num_requests} requests to rate-limited endpoint...")
        print("(Limit: 10 requests/minute)")

        for i in range(num_requests):
            start = time.perf_counter()
            try:
                resp = await client.get(url)
                elapsed = time.perf_counter() - start

                results.append({
                    "request": i + 1,
                    "status": resp.status_code,
                    "time": elapsed,
                })

                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After", "unknown")
                    print(f"  Request {i+1}: 429 Too Many Requests (retry after: {retry_after}s)")
                else:
                    print(f"  Request {i+1}: {resp.status_code} OK")

            except Exception as e:
                print(f"  Request {i+1}: Error - {e}")

            # Small delay to allow burst
            await asyncio.sleep(0.1)

        return results


async def main():
    print("=" * 60)
    print("RATE LIMITING BENCHMARK")
    print("=" * 60)

    results = await test_rate_limit(num_requests=20)

    # Analyze results
    success_count = sum(1 for r in results if r["status"] == 200)
    rate_limited_count = sum(1 for r in results if r["status"] == 429)

    print(f"\n📊 Results:")
    print(f"   Successful: {success_count}/20")
    print(f"   Rate limited: {rate_limited_count}/20")
    print(f"   Expected: ~10 successful (within burst), rest rate limited")

    if rate_limited_count > 0:
        print("\n✅ Rate limiting is working correctly!")
    else:
        print("\n⚠️  Warning: No requests were rate limited")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

### Run Benchmark

```bash
python benchmark_rate_limiting.py
```

### Expected Results

- First ~10 requests: Success (200 OK)
- Subsequent requests: Rate limited (429)
- Retry-After header: Present in 429 responses

## Load Testing with Locust

### Goal
Comprehensive load testing to measure all optimizations under realistic load.

### Locust Script

Create `locustfile.py`:

```python
"""Load testing for optimized FastAPI application."""

from locust import HttpUser, task, between


class OptimizedAPIUser(HttpUser):
    """Simulated user for load testing."""

    wait_time = between(0.1, 0.5)  # Wait 0.1-0.5s between requests

    @task(3)
    def get_root(self):
        """Test root endpoint (high frequency)."""
        self.client.get("/")

    @task(2)
    def get_users(self):
        """Test database pooling."""
        self.client.get("/users")

    @task(2)
    def call_external_api(self):
        """Test HTTP connection pooling."""
        self.client.get("/external/get")

    @task(1)
    def large_response(self):
        """Test compression."""
        self.client.get("/large-response")

    @task(1)
    def rate_limited(self):
        """Test rate limiting."""
        with self.client.get("/api/limited", catch_response=True) as response:
            if response.status_code == 429:
                response.success()  # 429 is expected


class HeavyLoadUser(HttpUser):
    """Simulate heavy concurrent load."""

    wait_time = between(0.01, 0.1)  # Very short wait

    @task
    def concurrent_external_calls(self):
        """Stress test HTTP pooling."""
        self.client.get("/external/get")
```

### Run Load Test

```bash
# Start app
uvicorn examples.optimization.fastapi_complete_example:app --port 8000

# Run load test (separate terminal)
locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

### Open Web UI

```
http://localhost:8089
```

### Expected Results

- **Throughput:** 1000+ req/s with optimizations
- **Response time:** p95 < 100ms
- **Error rate:** <1% (mostly rate limit 429s)
- **CPU usage:** 50-70% lower than without optimizations

## Continuous Benchmarking

### Setup GitHub Actions

Create `.github/workflows/benchmark.yml`:

```yaml
name: Performance Benchmarks

on:
  pull_request:
    paths:
      - 'pheno-sdk/src/pheno/optimization/**'
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install aiohttp supabase fastapi uvicorn pytest

      - name: Run HTTP pooling benchmark
        run: python examples/optimization/benchmark_http_pooling.py

      - name: Run DB pooling benchmark
        run: python examples/optimization/benchmark_db_pooling.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark_results.json
```

## Monitoring in Production

### Add metrics endpoint

```python
from pheno.optimization import get_optimization_status

@app.get("/metrics/optimizations")
async def optimization_metrics():
    """Prometheus-compatible optimization metrics."""
    status = get_optimization_status()

    # Format as Prometheus metrics
    metrics = []

    # HTTP pooling metrics
    if status["http_pooling"]["stats"]:
        stats = status["http_pooling"]["stats"]
        metrics.append(f'http_pool_connections_active {stats.get("active_connections", 0)}')
        metrics.append(f'http_pool_requests_total {stats.get("total_requests", 0)}')

    # DB pooling metrics
    db_stats = status["db_pooling"]["stats"]
    metrics.append(f'db_pool_clients_cached {db_stats["entries"]}')

    return "\n".join(metrics)
```

## Summary

| Benchmark | Command | Expected Result |
|-----------|---------|-----------------|
| HTTP Pooling | `python benchmark_http_pooling.py` | 4-10x speedup |
| DB Pooling | `python benchmark_db_pooling.py` | 6x speedup |
| Compression | `./benchmark_compression.sh` | 60-90% reduction |
| Rate Limiting | `python benchmark_rate_limiting.py` | Enforced limits |
| Load Test | `locust -f locustfile.py` | 1000+ req/s |

## Troubleshooting

**Low speedup in HTTP pooling:**
- Check network latency - benefits are greater with remote APIs
- Ensure `total` and `per_host` limits are configured correctly

**DB pooling not showing improvement:**
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- Check cache stats with `cache_stats()` - cache might be expiring

**Compression not reducing size:**
- Ensure `Accept-Encoding: gzip` header is sent
- Check `Content-Type` - only text/JSON/HTML are compressed

**Rate limiting not working:**
- Verify middleware is added to app
- Check that decorator is applied to endpoint
- Ensure requests are coming from same IP/user

## Next Steps

1. Run all benchmarks to establish baseline
2. Integrate benchmarks into CI/CD pipeline
3. Monitor metrics in production
4. Tune configuration based on results
5. Document findings in performance report
