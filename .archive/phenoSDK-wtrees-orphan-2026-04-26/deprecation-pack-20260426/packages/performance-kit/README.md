# Performance Kit

Performance monitoring and analysis framework for the pheno-sdk ecosystem.

## Features

- **Benchmarking**: Comprehensive performance benchmarking
- **Load Testing**: Load testing with Locust
- **Memory Profiling**: Memory usage analysis and optimization
- **CPU Profiling**: CPU usage analysis and optimization
- **Response Time Analysis**: API and service response time monitoring
- **Resource Monitoring**: System resource usage tracking
- **Performance Reporting**: Rich performance reports and analytics
- **Performance Regression Detection**: Automated performance regression detection

## Quick Start

```bash
# Install the package
pip install -e packages/performance-kit

# Use in your project
from performance_kit import PerformanceManager
from performance_kit.benchmark import BenchmarkRunner
from performance_kit.load_test import LoadTester
```

## Scripts

### Benchmarking
- `benchmark.py` - Performance benchmarking
- `profiler.py` - Performance profiling
- `nats_benchmarks.py` - NATS performance testing
- `analyze_test_structure.py` - Test structure analysis
- `duration_tracker.py` - Test duration monitoring

### Analysis
- `analyze_complexity.py` - Code complexity analysis
- `analyze_dependencies.py` - Dependency analysis
- `analyze_duplication.py` - Code duplication analysis
- `analyze_response_times.py` - Response time analysis
- `coverage_analysis.py` - Coverage analysis

### Monitoring
- `system_monitor.py` - System resource monitoring
- `memory_monitor.py` - Memory usage monitoring
- `cpu_monitor.py` - CPU usage monitoring
- `network_monitor.py` - Network usage monitoring

## Configuration

Create a `performance-config.yaml` file in your project root:

```yaml
performance:
  benchmark:
    iterations: 100
    warmup: 10
    timeout: 300

  load_test:
    users: 100
    spawn_rate: 10
    duration: "5m"
    host: "http://localhost:8000"

  profiling:
    memory: true
    cpu: true
    line_by_line: false

  monitoring:
    interval: 1
    metrics: ["cpu", "memory", "disk", "network"]

  reporting:
    format: "html"
    output: "reports/performance/"
    include_graphs: true
```

## Usage

### Basic Performance Testing

```python
from performance_kit import PerformanceManager

# Initialize performance manager
pm = PerformanceManager(config_path="performance-config.yaml")

# Run benchmarks
benchmark_result = pm.run_benchmarks()

# Run load tests
load_test_result = pm.run_load_tests()

# Run profiling
profile_result = pm.run_profiling()
```

### Benchmarking

```python
from performance_kit.benchmark import BenchmarkRunner

# Create benchmark runner
runner = BenchmarkRunner()

# Add benchmark functions
@runner.benchmark("api_call")
def api_call():
    # Your API call code
    pass

# Run benchmarks
results = runner.run()
```

### Load Testing

```python
from performance_kit.load_test import LoadTester

# Create load tester
load_tester = LoadTester(
    users=100,
    spawn_rate=10,
    duration="5m"
)

# Run load test
result = load_tester.run_test("http://localhost:8000")
```

### Memory Profiling

```python
from performance_kit.profiling import MemoryProfiler

# Create memory profiler
profiler = MemoryProfiler()

# Profile function
@profiler.profile
def my_function():
    # Your code
    pass

# Get memory usage report
report = profiler.get_report()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Proprietary - PHENO-SDK Team
