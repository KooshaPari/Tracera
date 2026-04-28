# Performance Testing Infrastructure

Comprehensive performance and load testing framework for the trace management system.

## Quick Start

### 1. Run All Performance Tests

```bash
pytest tests/performance/ -v --benchmark-only
```

### 2. Establish Baselines

```bash
python tests/performance/run_performance_tests.py --baseline
```

### 3. Check for Regressions

```bash
python tests/performance/run_performance_tests.py --compare
```

### 4. Generate Report

```bash
python tests/performance/run_performance_tests.py --report
```

## Test Suites

### Database Performance Tests (`test_database_performance.py`)

Tests for database query performance:
- **Index lookups**: Primary key and indexed column queries
- **Multi-row queries**: Filtering, pagination, complex conditions
- **Join operations**: Queries with table joins
- **Aggregations**: COUNT, GROUP BY operations
- **Bulk operations**: Insert, update, delete performance

**Run database tests:**
```bash
python tests/performance/run_performance_tests.py --suite database
```

### Bulk Operations Performance (`test_bulk_operations_performance.py`)

Tests for bulk data operations:
- **Bulk create**: 100, 500, 1000 item batches
- **Bulk update**: Updating multiple items
- **Bulk delete**: Deleting multiple items
- **Bulk links**: Creating link relationships
- **Performance scaling**: Analysis of degradation with scale

**Run bulk tests:**
```bash
python tests/performance/run_performance_tests.py --suite bulk
```

### Concurrent Operations Performance (`test_concurrent_performance.py`)

Tests for concurrent workloads:
- **Concurrent creates**: Multiple threads creating items
- **Concurrent updates**: Lock contention scenarios
- **Concurrent queries**: Read-heavy concurrent load
- **Link operations**: Concurrent link creation
- **High contention**: Same-item concurrent updates

**Run concurrent tests:**
```bash
python tests/performance/run_performance_tests.py --suite concurrent
```

### Load Testing (`locustfile.py`)

HTTP-based load testing for real API endpoints:
- Simulated user behaviors
- Item CRUD operations
- Link operations
- Search queries
- Mixed workload scenarios

**Run load tests:**
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## Performance Baselines

Key performance targets (SQLite baseline):

### Single Operations
| Operation | Target | Tolerance |
|-----------|--------|-----------|
| Create item | 50ms | ±10% |
| Read item | 20ms | ±15% |
| Update item | 40ms | ±10% |
| Delete item | 30ms | ±15% |
| Create link | 60ms | ±10% |

### Bulk Operations
| Operation | Target | Throughput |
|-----------|--------|-----------|
| Create 100 items | 0.5s | 200 items/sec |
| Create 1000 items | 5.0s | 200 items/sec |
| Update 100 items | 0.4s | 250 items/sec |
| Delete 100 items | 0.3s | 333 items/sec |

### Query Operations
| Operation | Target | Tolerance |
|-----------|--------|-----------|
| Query 1000 items | 100ms | ±20% |
| Filtered query | 80ms | ±20% |
| Paginated query | 30ms | ±20% |
| Count aggregation | 50ms | ±20% |

### Concurrent Operations
| Scenario | Target | Load |
|----------|--------|------|
| 10 items / 10 threads | 0.5s | Low |
| 100 items / 10 threads | 1.5s | Medium |
| 500 items / 50 threads | 5.0s | High |

## Fixtures and Utilities

### Performance Tracker (`perf_tracker`)

Track performance metrics during tests:
```python
def test_something(perf_tracker):
    perf_tracker.record("operation_name", elapsed_ms, items_count)
    report = perf_tracker.get_summary()
    print(perf_tracker.report())
```

### Timing Context Manager

Measure operation timing:
```python
from conftest import measure_time, assert_performance

def test_performance(perf_tracker):
    with measure_time("operation", perf_tracker, threshold_ms=50) as timing:
        # Code to measure
        result = expensive_operation()
    
    assert_performance(timing["elapsed_ms"], 50, "operation_name")
```

### Data Generator

Generate test data:
```python
from conftest import PerfDataGenerator

items = PerfDataGenerator.create_items(100)
links = PerfDataGenerator.create_links(50)
```

### Database Sessions

```python
# Async session
async def test_async_perf(perf_async_session):
    await perf_async_session.execute(...)

# Sync session
def test_sync_perf(perf_sync_session):
    perf_sync_session.query(...).all()
```

## Running Tests with pytest-benchmark

### Establish Baseline

```bash
pytest tests/performance/ \
  --benchmark-only \
  --benchmark-save=baseline \
  --benchmark-min-rounds=10 \
  -v
```

### Compare to Baseline

```bash
pytest tests/performance/ \
  --benchmark-only \
  --benchmark-compare=baseline \
  --benchmark-compare-fail=mean:10% \
  -v
```

### Generate Histogram

```bash
pytest tests/performance/ \
  --benchmark-only \
  --benchmark-histogram=performance_results \
  -v
```

### Custom Warmup

```bash
pytest tests/performance/ \
  --benchmark-only \
  --benchmark-warmup=short \
  --benchmark-min-rounds=15 \
  -v
```

## Benchmark Output Interpretation

```
Name (time in ms)          Min     Max    Mean  StdDev  Median   IQR  Outliers      OPS  Rounds  Iterations
-------------------------------------------------------------------------------------------------------------
test_single_item_create    45.0   55.0   50.2    3.1    50.1  2.5      0    19.92     10        1
```

- **Min/Max**: Best/worst case performance
- **Mean**: Average time (primary metric for regression)
- **StdDev**: Standard deviation (consistency)
- **Median**: 50th percentile
- **Outliers**: Values outside IQR
- **OPS**: Operations per second

## Performance Regression Thresholds

- **Critical** (>30%): Immediate investigation
- **Warning** (15-30%): Schedule investigation
- **Info** (<15%): Monitor trends

## CI/CD Integration

Add to GitHub Actions:

```yaml
- name: Performance Tests
  run: |
    pytest tests/performance/ \
      --benchmark-only \
      --benchmark-compare=baseline \
      --benchmark-compare-fail=mean:10% \
      -v
```

## File Structure

```
tests/performance/
├── __init__.py                      # Package initialization
├── conftest.py                      # Fixtures and configuration
├── test_database_performance.py     # Database query tests
├── test_bulk_operations_performance.py  # Bulk operation tests
├── test_concurrent_performance.py   # Concurrent operation tests
├── locustfile.py                    # Load testing configuration
├── run_performance_tests.py         # Test runner script
├── performance_baselines.json       # Performance baseline data
├── PERFORMANCE_TESTING_GUIDE.md    # Detailed guide
└── README.md                        # This file
```

## Common Tasks

### Update Baselines After Optimization

```bash
# Run optimized code
python tests/performance/run_performance_tests.py --baseline

# Compare new baselines
python tests/performance/run_performance_tests.py --report
```

### Profile a Specific Test

```bash
pytest tests/performance/test_database_performance.py::test_item_lookup_by_id_indexed \
  --benchmark-only \
  --benchmark-min-rounds=20 \
  -v
```

### Find Performance Bottlenecks

```bash
# Run tests with profiling
pytest tests/performance/ \
  --benchmark-only \
  --profile \
  -v
```

### Load Test Locally

```bash
# Start application
python -m uvicorn app:app --port 8000

# In another terminal, run load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless --users=50 --spawn-rate=5 --run-time=5m
```

## Troubleshooting

### Tests Run Slowly

1. Check system load: `top` or `htop`
2. Disable background applications
3. Run with `--benchmark-min-rounds=5` for quick feedback
4. Verify database is performing well

### Inconsistent Results

1. Increase rounds: `--benchmark-min-rounds=15`
2. Run in isolated environment
3. Disable CPU frequency scaling
4. Check for thermal throttling

### High Standard Deviation

1. Run more rounds: `--benchmark-min-rounds=20`
2. Increase `wait_time` between operations
3. Disable garbage collection: `--benchmark-disable-gc`
4. Check for system interrupts

## Performance Optimization Tips

1. **Use bulk operations** for large datasets
2. **Leverage database indexes** for queries
3. **Implement pagination** for large result sets
4. **Cache frequently accessed** items
5. **Batch related operations** together
6. **Monitor connection pool** under load
7. **Profile slow queries** before optimization
8. **Test optimizations** with this framework

## Additional Resources

- [pytest-benchmark docs](https://pytest-benchmark.readthedocs.io/)
- [Locust docs](https://docs.locust.io/)
- [SQLAlchemy performance](https://docs.sqlalchemy.org/en/20/faq/performance.html)
- [Database indexing guide](https://use-the-index-luke.com/)

## Contributing

When adding new performance tests:

1. Follow existing test patterns
2. Add corresponding baseline in `performance_baselines.json`
3. Document the test purpose
4. Include performance thresholds
5. Test locally before committing

```python
def test_my_operation(benchmark, perf_sync_session, perf_tracker):
    """Benchmark my expensive operation."""
    
    def operation():
        # Code to measure
        return result
    
    result = benchmark(operation)
    perf_tracker.record("my_operation", benchmark.stats.mean * 1000)
    assert result is not None
```
