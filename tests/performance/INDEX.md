# Performance Testing Infrastructure - Complete Index

## Overview

This directory contains a comprehensive performance and load testing framework for the trace management system. All tests are runnable and measure performance of critical operations.

## Files and Components

### Test Files

1. **test_database_performance.py** (19 tests)
   - Index lookup benchmarks (primary key, indexed columns)
   - Multi-row query performance (filtering, OR/AND conditions)
   - Pagination performance
   - Join operations
   - Aggregation queries (COUNT, GROUP BY)
   - Bulk insert/update operations

2. **test_bulk_operations_performance.py** (12 tests)
   - Bulk item creation (100, 500, 1000 items)
   - Bulk item updates (multiple update strategies)
   - Bulk item deletion
   - Bulk link creation
   - Memory efficiency with large batches

3. **test_concurrent_performance.py** (8 tests)
   - Concurrent item creation across multiple threads
   - Concurrent item updates
   - Concurrent item queries
   - Concurrent link operations
   - Lock contention analysis

### Configuration Files

1. **conftest.py**
   - Performance tracking fixtures
   - Data generation utilities
   - Timing context managers
   - Performance threshold definitions
   - pytest-benchmark plugin registration

2. **performance_baselines.json**
   - Baseline performance targets
   - Thresholds and tolerances
   - Performance tips and best practices
   - Regression alert thresholds

### Load Testing

1. **locustfile.py**
   - HTTP-based load testing configuration
   - User behavior definitions (CRUD operations)
   - Query workloads
   - Link operations
   - Multiple user profiles (Low/Medium/High load)

### Documentation

1. **README.md**
   - Quick start guide
   - Performance baselines
   - Common tasks and workflows

2. **PERFORMANCE_TESTING_GUIDE.md**
   - Detailed guide to running tests
   - Benchmark interpretation
   - Load testing scenarios
   - Optimization tips
   - CI/CD integration examples

3. **SETUP_AND_USAGE.md**
   - Installation instructions
   - Running tests with pytest
   - Using the test runner script
   - Troubleshooting guide

4. **INDEX.md** (this file)
   - Complete file index
   - Running all tests
   - Test inventory

### Utilities

1. **run_performance_tests.py**
   - Python script for running tests
   - Establish baselines
   - Check for regressions
   - Generate reports
   - Run specific test suites

## Test Inventory

### Total Tests: 39

#### Database Performance Tests (19)
- `test_item_lookup_by_id_indexed` - Indexed PK lookup
- `test_item_lookup_by_project_indexed` - Indexed column lookup
- `test_item_lookup_by_status_indexed` - Status index benchmark
- `test_query_all_items_1000` - Full table scan
- `test_query_items_with_filter_status_500` - Single filter
- `test_query_items_with_multiple_filters` - Multiple AND conditions
- `test_query_items_with_or_conditions` - OR conditions
- `test_query_items_pagination_first_page` - First page
- `test_query_items_pagination_middle_page` - Offset pagination
- `test_query_items_pagination_last_page` - Last page
- `test_query_items_with_links_join` - Join operations
- `test_aggregation_count_items` - COUNT aggregation
- `test_aggregation_group_by_status` - GROUP BY
- `test_aggregation_multiple_grouping` - Multi-column grouping
- `test_bulk_insert_100_items` - Bulk insert 100
- `test_bulk_insert_batch_500_items` - Batch insert 500
- `test_single_item_update` - Single update
- `test_bulk_update_100_items` - Update multiple
- `test_single_item_delete` - Single delete

#### Bulk Operations Tests (12)
- `test_bulk_create_100_items` - Create 100
- `test_bulk_create_500_items` - Create 500
- `test_bulk_create_1000_items` - Create 1000
- `test_bulk_create_with_batch_insert` - Optimized batch
- `test_bulk_update_100_items` - Update 100
- `test_bulk_update_500_items` - Update 500
- `test_bulk_update_with_query_update` - Query-based update
- `test_bulk_delete_100_items` - Delete 100
- `test_bulk_delete_500_items` - Delete 500
- `test_bulk_create_links_100` - Create 100 links
- `test_bulk_create_links_500` - Create 500 links
- `test_memory_efficiency_large_batch` - 1000 items memory test

#### Concurrent Operations Tests (8)
- `test_concurrent_create_10_items_10_threads` - Low concurrency
- `test_concurrent_create_100_items_10_threads` - Medium concurrency
- `test_concurrent_create_500_items_50_threads` - High concurrency
- `test_concurrent_update_100_items_10_threads` - Concurrent updates
- `test_concurrent_query_100_items_10_threads` - Concurrent reads
- `test_concurrent_create_links_50_threads` - Link creation
- `test_high_contention_single_item_updates` - Lock contention

## Running All Tests

### Run all performance tests:
```bash
pytest tests/performance/ -v
```

### Run with benchmark statistics:
```bash
pytest tests/performance/ -v --benchmark-only
```

### Run by test file:
```bash
# Database tests only
pytest tests/performance/test_database_performance.py -v

# Bulk operations only
pytest tests/performance/test_bulk_operations_performance.py -v

# Concurrent operations only
pytest tests/performance/test_concurrent_performance.py -v
```

### Run single test:
```bash
pytest tests/performance/test_database_performance.py::test_item_lookup_by_id_indexed -v
```

### Run with custom options:
```bash
# 10 rounds, save baseline
pytest tests/performance/ --benchmark-only --benchmark-min-rounds=10 --benchmark-save=baseline -v

# Compare to baseline
pytest tests/performance/ --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:10% -v

# Disable GC for stable results
pytest tests/performance/ --benchmark-only --benchmark-disable-gc -v
```

## Performance Baselines

Key target metrics (SQLite baseline):

### Single Operations
| Operation | Target | Tolerance |
|-----------|--------|-----------|
| Item create | 50ms | ±10% |
| Item read | 20ms | ±15% |
| Item update | 40ms | ±10% |
| Item delete | 30ms | ±15% |
| Link create | 60ms | ±10% |

### Bulk Operations
| Operation | Target | Throughput |
|-----------|--------|-----------|
| Create 100 items | 0.5s | 200 items/sec |
| Create 1000 items | 5.0s | 200 items/sec |
| Update 100 items | 0.4s | 250 items/sec |
| Delete 100 items | 0.3s | 333 items/sec |

### Query Performance
| Operation | Target | Tolerance |
|-----------|--------|-----------|
| Query 1000 items | 100ms | ±20% |
| Filtered query | 80ms | ±20% |
| Paginated (20) | 30ms | ±20% |
| Count aggregation | 50ms | ±20% |

## Using the Test Runner

```bash
# Establish baseline
python tests/performance/run_performance_tests.py --baseline

# Check for regressions
python tests/performance/run_performance_tests.py --compare

# Run specific suite
python tests/performance/run_performance_tests.py --suite database

# Generate report
python tests/performance/run_performance_tests.py --report

# List available tests
python tests/performance/run_performance_tests.py --list
```

## Load Testing with Locust

```bash
# Start with web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Headless load test
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless
```

## Key Features

### Comprehensive Coverage
- 39 performance tests covering all critical operations
- Single operations, bulk operations, and concurrent scenarios
- Database-level and application-level measurements

### Automated Baseline Management
- `performance_baselines.json` documents expected performance
- Automatic regression detection
- Configurable thresholds and tolerances

### Flexible Execution
- Run all tests or specific suites
- Customize number of rounds and warmup strategies
- Compare against baseline for regression detection

### Load Testing Support
- HTTP-based load testing with Locust
- Multiple user behavior profiles
- Realistic workload scenarios

### Documentation
- Comprehensive guides for all test types
- Setup instructions and troubleshooting
- Performance optimization tips

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Performance Tests
  run: |
    pytest tests/performance/ \
      --benchmark-only \
      --benchmark-compare=baseline \
      --benchmark-compare-fail=mean:10% \
      -v
```

## Next Steps

1. Run baseline establishment to create initial measurements
2. Monitor for performance regressions in CI/CD
3. Use specific test suites to identify bottlenecks
4. Implement optimizations and verify with regression tests
5. Update baselines when improvements are made

## Support

For detailed information:
- See PERFORMANCE_TESTING_GUIDE.md for comprehensive guide
- See SETUP_AND_USAGE.md for setup and troubleshooting
- See README.md for quick reference

## Created

Performance testing infrastructure created: 2024-01-26

All tests are fully functional and ready to use.
