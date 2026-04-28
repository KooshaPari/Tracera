# Performance Testing Guide

## Overview

This guide covers the comprehensive performance testing suite for TraceRTM, including bulk operations, graph traversals, and sync performance.

## Test Files

### 1. `tests/integration/test_performance_benchmarks.py`

**Primary performance baseline tests** with 25 test cases across 7 categories:

- **Bulk Create Performance** (4 tests): 100, 500, 1000, 2000+ items
- **Bulk Update Performance** (3 tests): 100, 500, 1000+ items
- **BulkOperationService** (2 tests): Preview and update operations
- **Graph Traversal** (5 tests): Dependency chains, wide graphs, link graphs, traversal
- **Sync Performance** (3 tests): Events, state tracking, changelog generation
- **Query Performance** (4 tests): Filtering, counting, pagination
- **Concurrency** (2 tests): Concurrent operations, rapid transitions
- **Meta Tests** (2 tests): Report generation, threshold validation

### 2. `tests/integration/test_performance_with_reporting.py`

**Detailed performance tests** with advanced reporting (9 test cases):

- **Bulk Operations with Metadata** (3 tests)
- **Advanced Graph Operations** (3 tests): Binary trees, mesh networks, BFS
- **Advanced Query Operations** (2 tests): Range queries, join aggregation
- **Reporting** (1 test): Report generation and validation

## Running Tests

### Quick Start

```bash
# Run all performance tests
pytest tests/integration/test_performance_benchmarks.py \
        tests/integration/test_performance_with_reporting.py -v

# Expected: 34 passed in ~25-30 seconds
```

### Run Specific Categories

```bash
# Bulk operations only
pytest tests/integration/test_performance_benchmarks.py::TestBulkCreatePerformance -v

# Graph operations only
pytest tests/integration/test_performance_benchmarks.py::TestGraphTraversalPerformance -v

# Sync operations only
pytest tests/integration/test_performance_benchmarks.py::TestSyncPerformance -v

# Detailed tests with reporting
pytest tests/integration/test_performance_with_reporting.py -v
```

### Run Individual Tests

```bash
# Single test
pytest tests/integration/test_performance_benchmarks.py::TestBulkCreatePerformance::test_bulk_create_1000_items -v

# With timing information
pytest tests/integration/test_performance_benchmarks.py::TestBulkCreatePerformance::test_bulk_create_1000_items -v --durations=0
```

### With Detailed Output

```bash
# Show print statements and full timing
pytest tests/integration/test_performance_benchmarks.py -v -s --tb=short

# With even more detail
pytest tests/integration/test_performance_benchmarks.py -v -s --tb=long
```

## Understanding Test Output

### Success Output
```
tests/integration/test_performance_benchmarks.py::TestBulkCreatePerformance::test_bulk_create_100_items PASSED [  4%]
```

Indicates:
- Test passed successfully
- Items created successfully
- Performance was within acceptable range

### Performance Metrics

Each test records:
- **Duration**: Total execution time in milliseconds
- **Item Count**: Number of items processed
- **Per-Item Time**: duration / item_count

Example:
- 100 items in 100ms = 1.0ms per item (Excellent)
- 1000 items in 500ms = 0.5ms per item (Excellent)

## Baseline Metrics

The following metrics are used as baselines:

| Metric | Baseline | Threshold (1.5x) |
|--------|----------|-----------------|
| Bulk create per item | 1.0ms | 1.5ms |
| Bulk update per item | 0.5ms | 0.75ms |
| Graph traversal per level | 5.0ms | 7.5ms |
| Link creation per link | 1.0ms | 1.5ms |
| Sync per item | 0.5ms | 0.75ms |
| Query per 100 items | 10.0ms | 15.0ms |

### Performance Threshold

If any operation exceeds **1.5x the baseline**, the test will fail with a performance warning:

```python
assert per_item_time <= baseline * 1.5
```

## Test Data Specifications

### Bulk Operations
- Small: 100 items
- Medium: 500 items
- Large: 1000 items
- Very Large: 2000 items (batched)

### Graph Operations
- Deep: 50-level dependency chain
- Wide: 1 parent + 100 children
- Complex: 500 items with 900+ links
- Mesh: 30 nodes with 435 bidirectional links
- Tree: Binary tree with 7 levels (127 nodes)
- Hub-spoke: 1 center + 200 periphery nodes

### Sync Operations
- Events: 500 bulk event creations
- State tracking: 300 items with state updates
- Changelog: 200 items with version history

### Query Operations
- Single filter: 500 items, filter by status
- Multi-filter: 500 items, 4 criteria filters
- Count: 1000 items aggregation
- Pagination: 500 items, 10 pages of 50 items

## Report Generation

### Automatic Reports

Tests can generate detailed reports:

```bash
# Run tests that generate reports
pytest tests/integration/test_performance_with_reporting.py::test_generate_performance_reports -v
```

This creates:
1. `performance_reports/performance_metrics.json` - Machine-readable metrics
2. `performance_reports/performance_report.txt` - Human-readable report

### JSON Report Structure

```json
{
  "timestamp": "2025-12-09T...",
  "summary": {
    "total_duration_ms": 5000.0,
    "total_items_processed": 3000,
    "test_count": 10
  },
  "tests": {
    "test_name": {
      "summary": {
        "item_count": 100,
        "runs": 1,
        "total_duration_ms": 100.0,
        "avg_duration_ms": 100.0,
        "avg_per_item_ms": 1.0
      },
      "runs": [
        {
          "timestamp": "2025-12-09T...",
          "duration_ms": 100.0,
          "per_item_ms": 1.0
        }
      ]
    }
  }
}
```

### Text Report Example

```
================================================================================
PERFORMANCE BENCHMARK REPORT
================================================================================
Generated: 2025-12-09T...

OVERALL SUMMARY
----------------
Total Tests: 25
Total Items Processed: 8500
Total Duration: 12500.00ms (12.50s)
Average Per Item: 1.47ms

PER-TEST BREAKDOWN
----------------

Test: test_bulk_create_100_items
  Items: 100
  Runs: 1
  Duration: 100.00ms (avg: 100.00ms)
  Per Item: avg=1.0000ms, min=1.0000ms, max=1.0000ms
```

## Debugging Performance Issues

### If Tests Fail

1. **Check error message**: Look for performance threshold violation
   ```
   AssertionError: Per-item time 2.5ms exceeds threshold 1.5ms
   ```

2. **Run single test with timing**:
   ```bash
   pytest tests/integration/test_performance_benchmarks.py::TestBulkCreatePerformance::test_bulk_create_1000_items -v --durations=0
   ```

3. **Check system resources**:
   ```bash
   # Monitor CPU/Memory during test
   top -l 1 | grep python
   ```

4. **Verify database performance**:
   - Check SQLite file size
   - Monitor query plans
   - Look for missing indexes

### Common Issues

**Slow bulk create (> 1.0ms per item)**
- Cause: Database I/O bottleneck
- Solution: Check disk speed, use SSD
- Alternative: Increase batch size

**Slow graph traversal (> 5ms per level)**
- Cause: Missing parent_id index
- Solution: Add index on (parent_id, project_id)

**Slow queries with filters (> 10ms per 100 items)**
- Cause: Missing indexes
- Solution: Add indexes on common filter fields (status, owner, priority)

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest

      - name: Run performance tests
        run: |
          pytest tests/integration/test_performance_benchmarks.py \
                  tests/integration/test_performance_with_reporting.py \
                  -v --tb=short

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: performance-reports
          path: performance_reports/
```

### GitLab CI Example

```yaml
performance_tests:
  stage: test
  script:
    - pip install -e .
    - pytest tests/integration/test_performance_benchmarks.py
             tests/integration/test_performance_with_reporting.py -v
  artifacts:
    paths:
      - performance_reports/
    when: always
  timeout: 5 minutes
```

## Monitoring and Alerting

### Performance Regression Detection

Add to CI/CD to detect regressions:

```python
# Check if new metrics exceed baseline by 1.5x
if new_metrics.per_item_ms > baseline.per_item_ms * 1.5:
    alert("Performance regression detected!")
```

### Continuous Monitoring

1. **Store baseline metrics** in version control
2. **Track metrics over time** (database or file)
3. **Alert on regressions** (> 1.5x baseline)
4. **Generate trend reports** (weekly, monthly)

## Performance Tuning Recommendations

### For Bulk Operations
1. Use batch insertion (500 items per batch)
2. Disable autocommit, commit in batches
3. Pre-allocate ID sequences

### For Graph Operations
1. Index parent_id column
2. Use denormalization for frequently accessed paths
3. Cache traversal results

### For Sync Operations
1. Use event batching (100 events per batch)
2. Compress sync payloads
3. Use connection pooling

### For Queries
1. Add indexes on filter columns
2. Use query result caching
3. Implement pagination for large results

## Extending the Test Suite

### Add Custom Performance Test

```python
def test_custom_performance(db_session, perf_metrics):
    """Test custom operation."""
    project = Project(id=f"proj-{uuid4()}", name="Test")
    db_session.add(project)
    db_session.commit()

    # Your test code here
    start = time.perf_counter()
    # ... operation ...
    duration_ms = (time.perf_counter() - start) * 1000

    # Record metrics
    perf_metrics.record("test_custom", "operation_type", duration_ms, item_count)
```

### Add Custom Reporter

```python
class CustomReporter(PerformanceReporter):
    def generate_csv_report(self):
        """Generate CSV report."""
        # Implementation
        pass

    def generate_html_report(self):
        """Generate HTML report."""
        # Implementation
        pass
```

## Performance Best Practices

1. **Test regularly**: Run performance tests on every commit
2. **Monitor trends**: Track metrics over time
3. **Compare baselines**: Test on same hardware for consistency
4. **Document changes**: Note any optimizations applied
5. **Alert on regressions**: Fail CI on 1.5x+ performance decrease
6. **Profile hot paths**: Use cProfile for bottleneck analysis
7. **Use realistic data**: Test with real-world data sizes and patterns

## Troubleshooting

### Tests Run Slowly (> 60 seconds)

- Check if using SSD
- Monitor CPU usage (should be high)
- Check RAM availability
- Disable unnecessary background processes

### Tests Fail Intermittently

- Check system load (run during quiet time)
- Use performance_tests mark to run only during stable periods
- Increase threshold temporarily for debugging

### Tests Timeout

- Increase pytest timeout
- Split tests into smaller batches
- Reduce item counts for quick iteration

## Support and Debugging

### Get Detailed Test Output

```bash
pytest tests/integration/test_performance_benchmarks.py -v -s --log-cli-level=DEBUG
```

### Profile Test Execution

```bash
python -m cProfile -s cumtime -m pytest tests/integration/test_performance_benchmarks.py::TestBulkCreatePerformance::test_bulk_create_1000_items
```

### Generate Flamegraph

```bash
pip install py-spy
py-spy record -o profile.svg -- pytest tests/integration/test_performance_benchmarks.py
```

## References

- Performance Test Files: `tests/integration/test_performance_*.py`
- Baseline Report: `PERFORMANCE_BENCHMARKS_REPORT.md`
- Test Summary: `PERFORMANCE_TEST_SUMMARY.md`
- Bulk Operation Service: `src/tracertm/services/bulk_operation_service.py`
- Item Repository: `src/tracertm/repositories/item_repository.py`

---

**Last Updated**: 2025-12-09
**Version**: 1.0
**Status**: Production Ready
