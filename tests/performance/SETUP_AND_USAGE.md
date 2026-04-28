# Performance Testing Setup and Usage

## Quick Setup

### 1. Install Dependencies

The required packages are already listed in `pyproject.toml`:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or install specific performance testing packages
pip install pytest-benchmark locust
```

### 2. Verify Installation

```bash
# Check pytest-benchmark is available
pytest --version
python -c "import pytest_benchmark; print('OK')"

# Check locust is available
locust --version
```

## Running Performance Tests

### Option 1: Using pytest directly

#### Run all performance tests:
```bash
pytest tests/performance/ -v
```

#### Run with benchmark measurements:
```bash
pytest tests/performance/ --benchmark-only -v
```

#### Run specific test suite:
```bash
# Database tests
pytest tests/performance/test_database_performance.py -v

# Bulk operations
pytest tests/performance/test_bulk_operations_performance.py -v

# Concurrent operations
pytest tests/performance/test_concurrent_performance.py -v
```

#### Run single test:
```bash
pytest tests/performance/test_database_performance.py::test_item_lookup_by_id_indexed -v
```

### Option 2: Using the runner script

```bash
# List available tests
python tests/performance/run_performance_tests.py --list

# Run all tests
python tests/performance/run_performance_tests.py --all

# Establish baseline
python tests/performance/run_performance_tests.py --baseline

# Check for regressions
python tests/performance/run_performance_tests.py --compare

# Run specific suite
python tests/performance/run_performance_tests.py --suite database

# Generate report
python tests/performance/run_performance_tests.py --report
```

## Test Files Overview

### test_database_performance.py (19 tests)
Tests for database query performance:
- Index lookups (3 tests)
- Multi-row queries (4 tests)
- Pagination (3 tests)
- Joins (1 test)
- Aggregations (3 tests)
- Bulk operations (5 tests)

### test_bulk_operations_performance.py (12 tests)
Tests for bulk data operations:
- Bulk item creation (4 tests)
- Bulk item updates (3 tests)
- Bulk item deletion (2 tests)
- Bulk link creation (2 tests)
- Performance scaling (1 test)

### test_concurrent_performance.py (8 tests)
Tests for concurrent workloads:
- Concurrent creates (3 tests)
- Concurrent updates (1 test)
- Concurrent queries (1 test)
- Concurrent links (1 test)
- Lock contention (2 tests)

### locustfile.py
HTTP load testing configuration with:
- User behaviors (CRUD operations)
- Query operations
- Link operations
- Mixed workload scenarios

## Configuration Files

### conftest.py
Provides fixtures and utilities:
- `perf_tracker`: Track performance metrics
- `perf_sync_session`: Synchronous DB session
- `perf_async_session`: Asynchronous DB session
- `measure_time()`: Context manager for timing
- `PerfDataGenerator`: Generate test data
- Performance thresholds and baselines

### performance_baselines.json
Baseline performance targets:
- Single operations (create, read, update, delete)
- Bulk operations (throughput)
- Query operations (latency)
- Concurrent operations (multi-threaded)
- Regression thresholds

## Expected Test Results

All tests use fixtures to create temporary databases, so they can run independently:

```
tests/performance/test_database_performance.py::test_item_lookup_by_id_indexed
  PASSED [ 5%]

tests/performance/test_database_performance.py::test_query_all_items_1000
  PASSED [10%]

tests/performance/test_bulk_operations_performance.py::test_bulk_create_100_items
  PASSED [15%]

...

========================= 39 passed in 45.23s ==========================
```

## Benchmark Results

When using `--benchmark-only`, tests produce detailed timing results:

```
Name (time in ms)                    Min      Max     Mean  StdDev  Median    IQR  Outliers      OPS  Rounds  Iterations
----------------------------------------------------------------------------------------------------------
test_item_lookup_by_id_indexed    20.25    28.50   23.45    3.12   23.10  2.50       0   42.65     10        1
test_query_all_items_1000         95.10   112.30  103.45    8.20  102.50  6.30       0    9.67     10        1
test_bulk_create_100_items      450.20   650.30  545.80   95.30  540.20 100.50       0    1.83      5        1
```

Key metrics:
- **Min/Max**: Best and worst case performance
- **Mean**: Average performance (use for regression detection)
- **StdDev**: Consistency of performance
- **OPS**: Operations per second
- **Rounds**: Number of iterations run

## Performance Baselines

Target performance metrics (SQLite baseline):

### Single Item Operations
- Create: 50ms ±10%
- Read: 20ms ±15%
- Update: 40ms ±10%
- Delete: 30ms ±15%

### Bulk Operations (1000 items)
- Create: 5.0 sec ±15% (200 items/sec)
- Update: 4.0 sec ±15% (250 items/sec)
- Delete: 3.0 sec ±15% (333 items/sec)

### Query Operations
- All items (1000): 100ms ±20%
- Filtered items: 80ms ±20%
- Paginated (20): 30ms ±20%
- Count: 50ms ±20%

### Concurrent Operations
- 10 items / 10 threads: 0.5s ±20%
- 100 items / 10 threads: 1.5s ±20%
- 500 items / 50 threads: 5.0s ±20%

## Load Testing with Locust

### Start Load Testing

```bash
# Start with web UI (http://localhost:8089)
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Run headless
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless
```

### Load Testing Scenarios

**Light Load (Dev Server):**
```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users=10 \
  --spawn-rate=1 \
  --run-time=3m \
  --headless
```

**Medium Load (Staging):**
```bash
locust -f tests/performance/locustfile.py \
  --host=https://staging.example.com \
  --users=50 \
  --spawn-rate=5 \
  --run-time=10m \
  --headless
```

**High Load (Production):**
```bash
locust -f tests/performance/locustfile.py \
  --host=https://api.example.com \
  --users=200 \
  --spawn-rate=20 \
  --run-time=15m \
  --headless
```

## Troubleshooting

### pytest-benchmark not found

If you get "unrecognized arguments: --benchmark-only", install benchmark:
```bash
pip install pytest-benchmark>=5.2.0
```

### Database errors in tests

Tests create temporary SQLite databases. Make sure you have write permissions:
```bash
ls -la /tmp
chmod 777 /tmp  # If needed
```

### Slow test execution

Performance tests may be slow depending on your hardware:
- Run with fewer rounds: `pytest --benchmark-min-rounds=2`
- Disable garbage collection: `pytest --benchmark-disable-gc`
- Check system load: `top` or `htop`

### Connection pool exhausted

If running many concurrent tests, increase pool size:
```python
engine = create_engine(url, pool_size=20, max_overflow=10)
```

## Continuous Integration

Add to your CI/CD pipeline:

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
        run: pip install -e ".[dev]"
      
      - name: Run performance tests
        run: |
          pytest tests/performance/ \
            --benchmark-only \
            --benchmark-save=baseline \
            -v
```

## Performance Optimization Workflow

1. **Establish baseline:**
   ```bash
   python tests/performance/run_performance_tests.py --baseline
   ```

2. **Make optimizations** to code

3. **Run regression check:**
   ```bash
   python tests/performance/run_performance_tests.py --compare
   ```

4. **Review results** and update baselines if improved:
   ```bash
   python tests/performance/run_performance_tests.py --baseline
   ```

5. **Commit** baseline changes

## Advanced Features

### Disable Garbage Collection During Benchmarks

```bash
pytest tests/performance/ --benchmark-disable-gc -v
```

### Generate Comparison CSV

```bash
pytest tests/performance/ \
  --benchmark-compare=baseline \
  --benchmark-csv=comparison.csv \
  -v
```

### Profile Test Execution

```bash
pytest tests/performance/ \
  --profile \
  -v
```

### Generate Histogram

```bash
pytest tests/performance/ \
  --benchmark-histogram=results \
  -v
```

## See Also

- [PERFORMANCE_TESTING_GUIDE.md](PERFORMANCE_TESTING_GUIDE.md) - Detailed guide
- [README.md](README.md) - Overview and quick reference
- [performance_baselines.json](performance_baselines.json) - Baseline data
