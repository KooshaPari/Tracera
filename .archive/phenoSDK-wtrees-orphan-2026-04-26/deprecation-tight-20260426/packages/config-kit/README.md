# Config Kit

Centralized configuration management for the pheno-sdk ecosystem.

## Features

- **Pre-commit Configuration**: Comprehensive pre-commit hooks
- **Pytest Configuration**: Standardized testing configuration
- **Linting Configuration**: Code quality and style enforcement
- **Quality Configuration**: Code quality gates and validation
- **Template System**: Reusable configuration templates
- **Validation**: Configuration validation and error reporting
- **Documentation**: Auto-generated configuration documentation

## Quick Start

```bash
# Install the package
pip install -e packages/config-kit

# Use in your project
from config_kit import ConfigManager
from config_kit.precommit import PreCommitConfig
from config_kit.pytest import PytestConfig
```

## Configuration Files

### Pre-commit Configuration
- `pre-commit/comprehensive.yaml` - Full pre-commit configuration
- `pre-commit/basic.yaml` - Basic pre-commit configuration
- `pre-commit/security.yaml` - Security-focused configuration

### Pytest Configuration
- `pytest/standard.ini` - Standard pytest configuration
- `pytest/coverage.ini` - Coverage-focused configuration
- `pytest/performance.ini` - Performance testing configuration

### Linting Configuration
- `linting/ruff.toml` - Ruff configuration
- `linting/black.toml` - Black configuration
- `linting/isort.toml` - isort configuration
- `linting/mypy.ini` - MyPy configuration

### Quality Configuration
- `quality/gates.yaml` - Quality gates configuration
- `quality/architecture.yaml` - Architecture validation
- `quality/security.yaml` - Security validation

## Usage

### Basic Configuration

```python
from config_kit import ConfigManager

# Initialize config manager
config = ConfigManager()

# Load configuration
config.load("config.yaml")

# Get configuration value
value = config.get("section.key")
```

### Pre-commit Configuration

```python
from config_kit.precommit import PreCommitConfig

# Create pre-commit configuration
precommit = PreCommitConfig()

# Add hooks
precommit.add_hook("black", "black .")
precommit.add_hook("isort", "isort .")
precommit.add_hook("mypy", "mypy .")

# Generate configuration file
precommit.generate(".pre-commit-config.yaml")
```

### Pytest Configuration

```python
from config_kit.pytest import PytestConfig

# Create pytest configuration
pytest = PytestConfig()

# Set test paths
pytest.set_test_paths(["tests/"])

# Set markers
pytest.add_marker("unit", "Unit tests")
pytest.add_marker("integration", "Integration tests")

# Generate configuration file
pytest.generate("pytest.ini")
```

## Configuration Templates

### Project Template

```yaml
project:
  name: "your-project"
  type: "python"
  version: "0.1.0"

precommit:
  enabled: true
  hooks:
    - black
    - isort
    - mypy
    - ruff

pytest:
  enabled: true
  test_paths: ["tests/"]
  markers:
    - unit
    - integration
    - performance

linting:
  enabled: true
  tools:
    - ruff
    - black
    - isort
    - mypy

quality:
  enabled: true
  gates:
    - coverage: 80
    - complexity: 10
    - duplication: 5
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Proprietary - PHENO-SDK Team
