# Pytest Configuration Kit

This package provides comprehensive pytest configurations, plugins, fixtures, and test data management utilities for Python projects.

## Features

- **Multiple Configuration Profiles**: Basic, comprehensive, CI, parallel, performance, and security configurations
- **Architecture Testing**: File size validation, import boundary enforcement, dependency direction validation
- **Performance Testing**: Benchmark testing, memory profiling, performance regression detection
- **Security Testing**: Vulnerability scanning, authentication testing, authorization testing
- **Rich Fixtures**: Common, performance, and security fixtures for testing
- **Test Data Management**: Factory for generating test data across different entity types

## Quick Start

### Basic Usage

```python
# Use basic configuration
pytest --ini=pytest/basic.ini

# Use comprehensive configuration
pytest --ini=pytest/comprehensive.ini

# Use CI configuration
pytest --ini=pytest/ci.ini
```

### Advanced Usage

```python
# Use parallel execution
pytest --ini=pytest/parallel.ini -m "fast and not serial" -n auto

# Use performance testing
pytest --ini=pytest/performance.ini -m performance

# Use security testing
pytest --ini=pytest/security.ini -m security
```

## Configuration Files

### Basic Configuration (`basic.ini`)

Simple configuration for basic projects:

```ini
[pytest]
minversion = 7.4
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --tb=short
    --strict-markers
    --maxfail=5
    --durations=10

markers =
    unit: Unit tests (fast, isolated, no I/O)
    integration: Integration tests (slower, may use I/O)
    slow: Slow running tests (> 5 seconds)
    fast: Fast running tests (< 1 second)
```

### Comprehensive Configuration (`comprehensive.ini`)

Enterprise-grade configuration with parallel execution, coverage, and extensive markers:

```ini
[pytest]
minversion = 7.4
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --tb=short
    --strict-markers
    --strict-config
    --maxfail=10
    --durations=10
    --durations-min=2.0
    --cache-clear
    # Parallel execution
    -n auto
    --dist=loadscope
    # Coverage analysis
    --cov=src
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=80
    --cov-branch
    # JUnit XML for CI integration
    --junitxml=reports/pytest-junit.xml
```

### CI Configuration (`ci.ini`)

Optimized for CI/CD environments with parallel execution and comprehensive reporting:

```ini
[pytest]
# CI/CD-optimized options
addopts =
    -ra
    --strict-markers
    --strict-config
    --tb=short
    --maxfail=10
    --durations=10
    --durations-min=1.0
    --cache-clear
    # Parallel execution optimized for CI
    -n auto
    --dist=worksteal
    # Include integration tests but exclude external service dependencies
    -m "not external and not nats and not redis and not temporal"
    # Coverage reporting
    --cov=src
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=85
    # JUnit XML for CI integration
    --junitxml=reports/pytest-junit.xml
```

### Parallel Configuration (`parallel.ini`)

Optimized for parallel test execution:

```ini
[pytest]
# Fast unit tests only (no external dependencies)
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
    --strict-config
    --maxfail=3
    --durations=5
    --durations-min=1.0
    -n auto
    --dist=loadscope
```

### Performance Configuration (`performance.ini`)

Specialized for performance testing:

```ini
[pytest]
# Performance testing options
addopts =
    -v
    --tb=short
    --strict-markers
    --maxfail=5
    --durations=20
    --durations-min=0.1
    # Performance-specific options
    --benchmark-only
    --benchmark-sort=mean
    --benchmark-skip
    --benchmark-save=performance_results
    --benchmark-save-data
    # Memory profiling
    --profile
    --profile-svg
    # Coverage for performance tests
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
```

### Security Configuration (`security.ini`)

Specialized for security testing:

```ini
[pytest]
# Security testing options
addopts =
    -v
    --tb=short
    --strict-markers
    --maxfail=5
    --durations=10
    --durations-min=1.0
    # Security-specific options
    --bandit
    --bandit-config=.bandit
    --safety
    --safety-json
    # Coverage for security tests
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
```

## Plugins

### Architecture Plugin

Provides architecture fitness tests:

```python
# Test import boundaries
def test_import_boundaries():
    """Test that import boundaries are respected."""
    pass

# Test dependency direction
def test_dependency_direction():
    """Test that dependency direction is respected."""
    pass

# Test file sizes
def test_file_sizes():
    """Test that file sizes are within limits."""
    pass

# Test cyclomatic complexity
def test_cyclomatic_complexity():
    """Test that cyclomatic complexity is within limits."""
    pass
```

### Performance Plugin

Provides performance testing capabilities:

```python
# Monitor performance during test execution
@pytest.fixture
def performance_monitor():
    """Monitor performance during test execution."""
    pass

# Benchmark testing
@pytest.mark.performance
def test_benchmark_performance():
    """Test that benchmark performance meets thresholds."""
    pass

# Memory usage testing
@pytest.mark.memory
def test_memory_usage():
    """Test that memory usage is within thresholds."""
    pass
```

### Security Plugin

Provides security testing capabilities:

```python
# Vulnerability scanning
@pytest.mark.security
def test_vulnerability_scan():
    """Scan code for common vulnerabilities."""
    pass

# Forbidden imports check
@pytest.mark.security
def test_forbidden_imports():
    """Check for forbidden imports that could be security risks."""
    pass

# Hardcoded secrets check
@pytest.mark.security
def test_hardcoded_secrets():
    """Check for hardcoded secrets in the code."""
    pass
```

## Fixtures

### Common Fixtures

```python
# Temporary directory
@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    pass

# Mock client
@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    pass

# Test data
@pytest.fixture
def test_data():
    """Provide test data for testing."""
    pass

# Performance monitor
@pytest.fixture
def performance_monitor():
    """Monitor performance during test execution."""
    pass

# Security context
@pytest.fixture
def security_context():
    """Provide security context for testing."""
    pass
```

### Performance Fixtures

```python
# Performance monitor
@pytest.fixture
def performance_monitor():
    """Monitor performance during test execution."""
    pass

# Benchmark data
@pytest.fixture
def benchmark_data():
    """Provide benchmark data for testing."""
    pass

# Load test data
@pytest.fixture
def load_test_data():
    """Provide load test data for testing."""
    pass

# Memory profiler
@pytest.fixture
def memory_profiler():
    """Provide memory profiling capabilities."""
    pass
```

### Security Fixtures

```python
# Security context
@pytest.fixture
def security_context():
    """Provide security context for testing."""
    pass

# Mock auth client
@pytest.fixture
def mock_auth_client():
    """Create a mock authentication client for testing."""
    pass

# Test credentials
@pytest.fixture
def test_credentials():
    """Provide test credentials for testing."""
    pass

# Test tokens
@pytest.fixture
def test_tokens():
    """Provide test tokens for testing."""
    pass
```

## Test Data Management

### Test Data Factory

```python
from config_kit.pytest.data.factory import TestDataFactory

# Create factory
factory = TestDataFactory(seed=42)

# Generate user data
user_data = factory.user_data()
# {
#     "id": "uuid-123",
#     "username": "testuser",
#     "email": "test@example.com",
#     "full_name": "Test User",
#     "roles": ["user"],
#     "created_at": datetime.now(),
#     "updated_at": datetime.now(),
#     "is_active": True,
# }

# Generate organization data
org_data = factory.organization_data()
# {
#     "id": "uuid-456",
#     "name": "Test Organization",
#     "description": "Test organization description",
#     "created_at": datetime.now(),
#     "updated_at": datetime.now(),
#     "is_active": True,
# }

# Generate project data
project_data = factory.project_data(organization_id="org-123")
# {
#     "id": "uuid-789",
#     "name": "Test Project",
#     "description": "Test project description",
#     "status": "active",
#     "organization_id": "org-123",
#     "created_at": datetime.now(),
#     "updated_at": datetime.now(),
# }

# Generate related data
users = factory.create_related_data("user", count=5)
organizations = factory.create_related_data("organization", count=3)
```

## Usage Examples

### Basic Testing

```python
import pytest
from config_kit.pytest.fixtures.common import mock_client, test_data

def test_basic_functionality(mock_client, test_data):
    """Test basic functionality."""
    result = mock_client.call_tool("test_tool", test_data["user"])
    assert result["success"] is True
```

### Performance Testing

```python
import pytest
from config_kit.pytest.fixtures.performance import performance_monitor

def test_performance(performance_monitor):
    """Test performance."""
    with performance_monitor["measure"]("test_operation"):
        # Perform operation
        result = expensive_operation()
    
    assert result is not None
    assert performance_monitor["total_duration"] < 1.0
```

### Security Testing

```python
import pytest
from config_kit.pytest.fixtures.security import security_context, test_credentials

def test_authentication(security_context, test_credentials):
    """Test authentication."""
    auth_result = authenticate_user(
        test_credentials["username"],
        test_credentials["password"]
    )
    
    assert auth_result["success"] is True
    assert auth_result["user_id"] == security_context["user_id"]
```

### Architecture Testing

```python
import pytest
from config_kit.pytest.plugins.architecture import ArchitecturePlugin

def test_architecture_fitness():
    """Test architecture fitness."""
    # This test is automatically added by the ArchitecturePlugin
    pass
```

## Command Line Options

### Architecture Testing

```bash
# Set maximum file size
pytest --max-file-size=1000

# Set maximum complexity
pytest --max-complexity=10

# Enable/disable import enforcement
pytest --enforce-imports
pytest --no-enforce-imports

# Enable/disable dependency enforcement
pytest --enforce-dependencies
pytest --no-enforce-dependencies
```

### Performance Testing

```bash
# Set benchmark threshold
pytest --benchmark-threshold=1.0

# Set memory threshold
pytest --memory-threshold=100
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest --ini=pytest/ci.ini
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        args: [--ini=pytest/basic.ini, -m "not slow"]
        language: system
        pass_filenames: false
        always_run: true
```

## Best Practices

1. **Use appropriate configuration**: Choose the right configuration file for your needs
2. **Mark tests appropriately**: Use markers to categorize tests (unit, integration, performance, security)
3. **Use fixtures**: Leverage the provided fixtures for common testing patterns
4. **Generate test data**: Use the TestDataFactory for consistent test data generation
5. **Monitor performance**: Use performance fixtures to monitor test execution
6. **Test security**: Use security fixtures and plugins to test security aspects
7. **Validate architecture**: Use architecture plugins to validate architectural constraints

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the config-kit package is installed and in the Python path
2. **Plugin not found**: Check that the plugin is properly registered in pytest configuration
3. **Fixture not found**: Ensure the fixture is imported or the module is in the Python path
4. **Performance issues**: Use parallel execution and appropriate markers for test categorization

### Debug Mode

```bash
# Enable debug mode
pytest --ini=pytest/comprehensive.ini -v -s --tb=long

# Enable logging
pytest --ini=pytest/comprehensive.ini --log-cli-level=DEBUG
```

## Contributing

1. Add new configurations in the `pytest/` directory
2. Add new plugins in the `pytest/plugins/` directory
3. Add new fixtures in the `pytest/fixtures/` directory
4. Add new test data utilities in the `pytest/data/` directory
5. Update documentation and examples

## License

MIT License - See LICENSE file for details.