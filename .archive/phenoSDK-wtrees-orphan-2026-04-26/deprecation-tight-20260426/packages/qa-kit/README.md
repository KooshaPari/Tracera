# QA Kit

Comprehensive QA testing and reporting framework for the pheno-sdk ecosystem.

## Features

- **Unified Testing Framework**: Consistent testing across all projects
- **E2E Testing**: End-to-end testing automation with Playwright
- **Performance Testing**: Load testing and performance benchmarking
- **API Testing**: Comprehensive API testing utilities
- **Database Testing**: Database testing and migration validation
- **Reporting**: Rich test reporting and analytics
- **Fixtures**: Reusable test fixtures and data generators
- **Plugins**: Custom pytest plugins for enhanced testing

## Quick Start

```bash
# Install the package
pip install -e packages/qa-kit

# Use in your project
from qa_kit import QAManager
from qa_kit.fixtures import DatabaseFixture
from qa_kit.performance import LoadTester
```

## Scripts

### E2E Testing
- `dashboard_e2e.py` - Dashboard E2E testing
- `ingest_axe.py` - Accessibility testing ingestion
- `ingest_lhci.py` - Lighthouse CI ingestion
- `ingest.py` - General QA data ingestion
- `merge_db.py` - QA database merging
- `seed_from_dir.py` - QA data seeding

### Test Framework
- `test_runner.py` - Unified test runner
- `test_analyzer.py` - Test analysis and reporting
- `coverage_analyzer.py` - Coverage analysis
- `performance_analyzer.py` - Performance analysis

## Fixtures

### Database Fixtures
- `DatabaseFixture` - Database setup and teardown
- `DataGenerator` - Test data generation
- `MigrationFixture` - Database migration testing

### API Fixtures
- `APIClient` - HTTP client for API testing
- `MockServer` - Mock server for testing
- `AuthFixture` - Authentication testing

### Performance Fixtures
- `LoadTestFixture` - Load testing setup
- `BenchmarkFixture` - Performance benchmarking
- `MemoryFixture` - Memory usage testing

## Plugins

### Custom Pytest Plugins
- `qa_plugin.py` - Main QA plugin
- `coverage_plugin.py` - Coverage tracking
- `performance_plugin.py` - Performance monitoring
- `reporting_plugin.py` - Test reporting

## Configuration

Create a `qa-config.yaml` file in your project root:

```yaml
qa:
  test_path: "tests/"
  parallel: true
  workers: 4

e2e:
  browser: "chromium"
  headless: true
  timeout: 30000

performance:
  users: 100
  spawn_rate: 10
  duration: "5m"

reporting:
  format: "html"
  output: "reports/"
  include_coverage: true
```

## Usage

### Basic Testing

```python
from qa_kit import QAManager

# Initialize QA manager
qa = QAManager(config_path="qa-config.yaml")

# Run all tests
result = qa.run_tests()

# Run E2E tests
e2e_result = qa.run_e2e_tests()

# Run performance tests
perf_result = qa.run_performance_tests()
```

### Using Fixtures

```python
import pytest
from qa_kit.fixtures import DatabaseFixture, APIClient

@pytest.fixture
def db_fixture():
    return DatabaseFixture()

@pytest.fixture
def api_client():
    return APIClient(base_url="http://localhost:8000")

def test_api_endpoint(api_client, db_fixture):
    with db_fixture.transaction():
        response = api_client.get("/api/users")
        assert response.status_code == 200
```

### Performance Testing

```python
from qa_kit.performance import LoadTester

# Create load tester
load_tester = LoadTester(
    users=100,
    spawn_rate=10,
    duration="5m"
)

# Run load test
result = load_tester.run_test("http://localhost:8000")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Proprietary - PHENO-SDK Team
