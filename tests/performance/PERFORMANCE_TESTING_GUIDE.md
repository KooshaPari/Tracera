# Performance Testing Guide

This directory contains comprehensive performance and load testing infrastructure for the trace management system.

## Overview

The performance testing suite includes:

1. **Database Query Performance Tests** (`test_database_performance.py`)
   - Index lookup performance
   - Multi-row queries
   - Pagination performance
   - Join operations
   - Aggregation queries
   - Bulk operations

2. **Bulk Operations Performance Tests** (`test_bulk_operations_performance.py`)
   - Bulk item creation (100, 500, 1000 items)
   - Bulk item updates
   - Bulk item deletion
   - Bulk link creation
   - Performance scaling analysis

3. **Concurrent Operations Performance Tests** (`test_concurrent_performance.py`)
   - Concurrent item creation across threads
   - Concurrent item updates
   - Concurrent queries
   - Concurrent link operations
   - Lock contention analysis

4. **Load Testing** (`locustfile.py`)
   - HTTP-based load testing using Locust
   - Simulated user behaviors
   - Item CRUD operations
   - Link operations
   - Query workloads

## Running Performance Tests

### Using pytest-benchmark

#### Run all performance tests:
```bash
pytest tests/performance/ -v --benchmark-only
```

#### Run specific test file:
```bash
pytest tests/performance/test_database_performance.py -v --benchmark-only
```

#### Run specific test:
```bash
pytest tests/performance/test_database_performance.py::test_item_lookup_by_id_indexed -v --benchmark-only
```

#### With custom benchmark options:
```bash
pytest tests/performance/ \
  --benchmark-only \
  --benchmark-min-rounds=10 \
  --benchmark-storage=.benchmarks \
  --benchmark-compare=0001 \
  -v
```

### Benchmark Options

- `--benchmark-only`: Run only benchmark tests
- `--benchmark-min-rounds=N`: Minimum number of rounds (default: 5)
- `--benchmark-storage=PATH`: Storage location for results
- `--benchmark-compare=N`: Compare against previous run N
- `--benchmark-histogram=PATH`: Generate histogram
- `--benchmark-disable-gc`: Disable garbage collection during benchmarks
- `--benchmark-warmup=MODE`: Warmup mode (off, auto, short, long)

### Example: Baseline Establishment

```bash
# Run and establish baselines
pytest tests/performance/ \
  --benchmark-only \
  --benchmark-save=baseline \
  --benchmark-min-rounds=10 \
  --benchmark-warmup=short \
  -v
```

### Example: Regression Detection

```bash
# Compare against baseline
pytest tests/performance/ \
  --benchmark-only \
  --benchmark-compare=baseline \
  --benchmark-compare-fail=mean:10% \
  -v
```

## Running Load Tests with Locust

### Installation

Locust is required for load testing:
```bash
pip install locust
```

### Basic Load Test

```bash
# Start Locust with web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Then open http://localhost:8089 and set:
# - Number of users: 10
# - Spawn rate: 2 users/sec
# - Run duration: 5 minutes
```

### Headless Load Test

```bash
# Run without web UI
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless
```

### Load Test Scenarios

#### Light Load (Test Server):
```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users=10 \
  --spawn-rate=1 \
  --run-time=3m \
  --headless
```

#### Medium Load (Staging):
```bash
locust -f tests/performance/locustfile.py \
  --host=https://staging.example.com \
  --users=50 \
  --spawn-rate=5 \
  --run-time=10m \
  --headless
```

#### High Load (Production):
```bash
locust -f tests/performance/locustfile.py \
  --host=https://api.example.com \
  --users=200 \
  --spawn-rate=20 \
  --run-time=15m \
  --headless
```

## Performance Baselines

Performance baselines are documented in `performance_baselines.json`:

### Item Operations
- Single create: **50ms** (±10%)
- Single read: **20ms** (±15%)
- Single update: **40ms** (±10%)
- Single delete: **30ms** (±15%)

### Link Operations
- Single create: **60ms** (±10%)
- Single read: **30ms** (±15%)
- Single delete: **40ms** (±15%)

### Bulk Operations (throughput)
- Bulk create 100: **0.5s** (±15%) → **200 items/sec**
- Bulk create 500: **2.5s** (±15%) → **200 items/sec**
- Bulk create 1000: **5.0s** (±15%) → **200 items/sec**
- Bulk update 100: **0.4s** (±15%) → **250 items/sec**
- Bulk delete 100: **0.3s** (±15%) → **333 items/sec**

### Query Operations
- Query 1000 items: **100ms** (±20%)
- Query with filter: **80ms** (±20%)
- Pagination (20 items): **30ms** (±20%)
- Count aggregation: **50ms** (±20%)

### Concurrent Operations
- 10 items / 10 threads: **0.5s** (±20%)
- 100 items / 10 threads: **1.5s** (±20%)
- 500 items / 50 threads: **5.0s** (±20%)

## Interpreting Results

### Benchmark Output

```
Name (time in ms)          Min     Max    Mean  StdDev  Median   IQR  Outliers      OPS  Rounds  Iterations
-------------------------------------------------------------------------------------------------------------
test_single_item_create    45.0   55.0   50.2    3.1    50.1  2.5      0    19.92     10        1
test_item_query_1000      95.0  110.0  100.5   6.2   100.2  4.0      0    10.05     10        1
```

Key metrics:
- **Min/Max**: Best/worst case times
- **Mean**: Average execution time (use for regression detection)
- **StdDev**: Standard deviation (consistency)
- **Median**: 50th percentile (typical performance)
- **Outliers**: Values outside IQR
- **OPS**: Operations per second

### Regression Thresholds

- **Critical** (>30% degradation): Immediate investigation required
- **Warning** (15-30% degradation): Schedule investigation
- **Info** (<15% degradation): Monitor for trends

## Performance Optimization Tips

1. **Bulk Operations**: Use `bulk_save_objects()` instead of individual adds
   ```python
   items = [Item(...) for _ in range(1000)]
   session.bulk_save_objects(items)
   session.commit()
   ```

2. **Query Optimization**: Use indexes for frequently queried columns
   ```python
   # Good - indexed columns
   query.filter(Item.project_id == "proj")
   query.filter(Item.status == "done")
   
   # Slower - computed columns
   query.filter(func.length(Item.description) > 100)
   ```

3. **Pagination**: Always use LIMIT/OFFSET for large datasets
   ```python
   query.limit(20).offset(0)  # First page
   ```

4. **Caching**: Cache frequently accessed items
   ```python
   # Implement query caching for hot items
   if item_id in cache:
       return cache[item_id]
   ```

5. **Batch Operations**: Group related operations
   ```python
   # Create items, then links in separate batches
   create_items(items)
   create_links(links)
   ```

6. **Connection Pool**: Monitor and tune connection pool size
   ```python
   engine = create_engine(url, pool_size=20, max_overflow=10)
   ```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Performance Tests
on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run performance tests
        run: |
          pytest tests/performance/ \
            --benchmark-only \
            --benchmark-save=baseline \
            -v
      
      - name: Check for regressions
        run: |
          pytest tests/performance/ \
            --benchmark-only \
            --benchmark-compare=baseline \
            --benchmark-compare-fail=mean:10% \
            -v
```

## Benchmarking Best Practices

1. **Warm up**: Run 1-2 iterations before measuring
2. **Disable background tasks**: Minimize interference
3. **Repeat measurements**: Use `--benchmark-min-rounds=10`
4. **Control environment**: Run on consistent hardware
5. **Monitor resources**: Check CPU/memory during tests
6. **Isolate tests**: Run in separate transactions
7. **Document changes**: Record hardware/configuration changes

## Monitoring Performance in Production

### Key Metrics to Monitor

1. **Request latency** (p50, p95, p99)
2. **Throughput** (requests/sec)
3. **Error rate** (<0.1%)
4. **Database query time** (<100ms p95)
5. **Queue depth** (background jobs)
6. **Resource usage** (CPU, memory, disk)

### Alerting Thresholds

- Item create P95 > 100ms: Warning
- Bulk operations P95 > 2x baseline: Warning
- Query latency P99 > 500ms: Warning
- Error rate > 0.5%: Critical
- Database connection pool exhausted: Critical

## Troubleshooting

### Performance Tests are Slow

- Check system load with `top` or `htop`
- Verify database is not contended
- Run with `--benchmark-warmup=off` to debug
- Check for slow disk I/O

### Inconsistent Results

- Disable CPU frequency scaling
- Close background applications
- Use `--benchmark-min-rounds=15` for more data
- Check for garbage collection pauses

### High Standard Deviation

- Increase `--benchmark-min-rounds`
- Run in isolated environment
- Check for system thermal throttling
- Verify database indexes exist

## Additional Resources

- [pytest-benchmark documentation](https://pytest-benchmark.readthedocs.io/)
- [Locust documentation](https://docs.locust.io/)
- [SQLAlchemy performance tips](https://docs.sqlalchemy.org/en/20/faq/performance.html)
- [Database indexing guide](https://use-the-index-luke.com/)
