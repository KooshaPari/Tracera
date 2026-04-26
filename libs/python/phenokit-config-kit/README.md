# PhenoKit Config Kit

A comprehensive configuration management package for Python projects providing pytest plugins, fixtures, linting configurations, and pre-commit hooks.

## Features

- **Pre-commit Configuration**: Multiple pre-commit hook configurations (basic, comprehensive, security)
- **Pytest Configuration**: Standardized testing configurations for different scenarios
- **Pytest Plugins**: Architecture, performance, and security testing plugins
- **Pytest Fixtures**: Common, performance, and security fixtures for testing
- **Linting Configuration**: Code quality and style enforcement configs
- **Test Data Factory**: Generate consistent test data across projects

## Installation

```bash
# Basic installation
pip install phenokit-config-kit

# With all dependencies
pip install phenokit-config-kit[all]

# With specific extras
pip install phenokit-config-kit[testing,linting]
```

## Quick Start

### Using Pre-commit Configurations

Copy the desired pre-commit configuration to your project:

```bash
# Basic configuration
cp pre-commit/basic.yaml .pre-commit-config.yaml

# Comprehensive configuration
cp pre-commit/comprehensive.yaml .pre-commit-config.yaml

# Security-focused configuration
cp pre-commit/security.yaml .pre-commit-config.yaml
```

Install pre-commit hooks:
```bash
pre-commit install
```

### Using Pytest Configurations

```bash
# Use basic configuration
pytest --ini=config-kit/pytest/basic.ini

# Use comprehensive configuration
pytest --ini=config-kit/pytest/comprehensive.ini

# Use CI configuration
pytest --ini=config-kit/pytest/ci.ini
```

### Using Pytest Plugins

The pytest plugins are automatically registered when you install the package:

```python
# Architecture testing (auto-added to test collection)
pytest --max-file-size=500 --max-complexity=10

# Performance testing
pytest -m performance --benchmark-threshold=1.0

# Security testing
pytest -m security
```

### Using Fixtures

```python
import pytest
from config_kit.pytest.fixtures.common import mock_client, test_data
from config_kit.pytest.fixtures.performance import performance_monitor
from config_kit.pytest.fixtures.security import security_context

def test_with_fixtures(mock_client, test_data):
    result = mock_client.call_tool("test_tool", test_data["user"])
    assert result["success"] is True

@pytest.mark.performance
def test_performance(performance_monitor):
    with performance_monitor["measure"]("test_operation"):
        result = expensive_operation()
    assert result is not None
```

### Using Test Data Factory

```python
from config_kit.pytest.data.factory import TestDataFactory

factory = TestDataFactory(seed=42)

# Generate user data
user_data = factory.user_data()

# Generate organization data
org_data = factory.organization_data()

# Generate project data
project_data = factory.project_data(organization_id="org-123")
```

## Configuration Files

### Pre-commit Configurations
- `pre-commit/basic.yaml` - Basic pre-commit hooks
- `pre-commit/comprehensive.yaml` - Full linting and security suite
- `pre-commit/security.yaml` - Security-focused configuration

### Pytest Configurations
- `pytest/basic.ini` - Basic pytest configuration
- `pytest/comprehensive.ini` - Enterprise-grade configuration
- `pytest/ci.ini` - CI/CD optimized
- `pytest/parallel.ini` - Parallel execution optimized
- `pytest/performance.ini` - Performance testing
- `pytest/security.ini` - Security testing

### Linting Configurations
- `linting/pyproject.toml` - Python linter configs (Ruff, Black, isort, mypy)
- `linting/.editorconfig` - Editor configuration
- `linting/.markdownlint.json` - Markdown linting rules
- `linting/linters.toml` - Centralized linter configuration
- `linting/ci-cd/gatekeeper.toml` - Quality gate definitions

## Pytest Plugins

### Architecture Plugin

Provides architecture fitness tests:
- File size validation
- Import boundary enforcement
- Dependency direction validation
- Cyclomatic complexity analysis

### Performance Plugin

Provides performance testing capabilities:
- Benchmark testing
- Memory profiling
- Performance regression detection

### Security Plugin

Provides security testing capabilities:
- Vulnerability scanning
- Forbidden imports check
- Hardcoded secrets detection

## Git Hooks

The package includes useful git hooks:

### Pre-commit Hook
Validates staged files with linters (Ruff, Black, isort, mypy, bandit, etc.)

### Commit-msg Hook
Validates commit messages for:
- Conventional commits format
- Proper capitalization
- Proper punctuation
- Minimum length requirements

To use the git hooks:
```bash
cp linting/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

cp linting/git-hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

## Quality Gate Script

Run comprehensive quality checks:

```bash
bash linting/ci-cd/scripts/quality-gate.sh
```

This runs all configured linters and generates a `quality_gate_results.json` report.

## Development

### Project Structure

```
config-kit/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── pre-commit/             # Pre-commit configurations
├── pytest/                 # Pytest configurations, plugins, fixtures
│   ├── plugins/            # Pytest plugins
│   ├── fixtures/           # Pytest fixtures
│   └── data/               # Test data utilities
└── linting/                # Linting configurations and scripts
    ├── ci-cd/              # CI/CD scripts
    └── git-hooks/          # Git hooks
```

### Running Tests

```bash
pytest --ini=pytest/comprehensive.ini
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the quality gate script
5. Submit a pull request
