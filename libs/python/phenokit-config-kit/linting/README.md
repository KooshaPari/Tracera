# Linting Configurations for config-kit

This directory contains comprehensive linting configurations for the config-kit package, including all major linting tools, pre-commit hooks, and CI/CD integration.

## Overview

The linting configuration includes:

- **Code Style**: Black, isort, Ruff
- **Type Checking**: MyPy
- **Security**: Bandit, Safety, detect-secrets
- **Documentation**: pydocstyle, interrogate, docformatter
- **Performance**: Radon (complexity)
- **Quality**: Vulture (dead code), PyUp (upgrade checks)
- **YAML/Markdown**: yamllint, markdownlint
- **Shell**: shellcheck
- **Pre-commit Hooks**: Automated checks on commit
- **CI/CD Integration**: Quality gates and automated checks

## Directory Structure

```
linting/
├── pyproject.toml              # Main linting configuration
├── linters.toml               # Centralized linter configuration
├── .editorconfig              # Editor configuration
├── .markdownlint.json         # Markdown linting rules
├── pre-commit-hooks.yaml      # Pre-commit configuration
├── ci-cd/
│   ├── gatekeeper.toml        # Quality gate definitions
│   └── scripts/
│       └── quality-gate.sh    # Comprehensive quality check script
├── git-hooks/                 # Custom git hooks
│   ├── pre-commit             # Custom pre-commit hook
│   └── commit-msg             # Commit message validation
└── README.md                 # This file
```

## Usage

### 1. Basic Linting

Run individual linters:

```bash
# Code formatting
black .
black --check  # Check without modifying

# Import sorting
isort .
isort --check-only

# Ruff (all-in-one)
ruff check .
ruff check --fix  # Fix auto-fixable issues
ruff format .     # Format code

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Documentation
pydocstyle src/
interrogate src/
```

### 2. Pre-commit Hooks

Set up pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

### 3. Comprehensive Quality Gate

Run all quality checks:

```bash
# Run comprehensive quality gate
./linting/ci-cd/scripts/quality-gate.sh

# Run specific sections
./linting/ci-cd/scripts/quality-gate.sh 2>&1 | grep "LINTING CHECKS"
```

### 4. CI/CD Integration

The quality gate configuration can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run quality gate
  run: ./linting/ci-cd/scripts/quality-gate.sh
  
- name: Upload quality reports
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: quality-reports
    path: |
      quality_gate_results.json
      bandit-report.json
      safety-report.json
```

## Configuration Details

### pyproject.toml

Contains configuration for all Python-based linters:

- **Ruff**: Fast Python linter and formatter
- **Black**: Code formatter
- **isort**: Import sorter
- **MyPy**: Type checker
- **Bandit**: Security linter
- **Safety**: Vulnerability scanner
- **yamllint**: YAML linter
- **markdownlint**: Markdown linter
- **pydocstyle**: Docstring checker
- **interrogate**: Coverage checker for docstrings
- **vulture**: Dead code finder
- **radon**: Code complexity analyzer

### Pre-commit Hooks

The pre-commit configuration includes:

1. **Automatic formatting**: Black, isort, Ruff
2. **Type checking**: MyPy
3. **Security scanning**: Bandit
4. **Documentation**: pydocstyle, interrogate
5. **File-specific**: yamllint, markdownlint, shellcheck

### Quality Gates

The quality gate system defines thresholds for:

- **Code Coverage**: 80% minimum
- **Documentation**: 80% docstring coverage
- **Security**: Zero critical/high vulnerabilities
- **Complexity**: Max 10 cyclomatic complexity
- **File Size**: Max 50KB per file
- **Dependencies**: No known vulnerabilities

## Customization

### Adding New Linters

1. Add linter to `pyproject.toml`
2. Update `pre-commit-hooks.yaml`
3. Add checks to `quality-gate.sh`
4. Update `gatekeeper.toml`

### Adjusting Rules

Edit the respective configuration files:

- **Python linters**: `pyproject.toml`
- **Markdown**: `.markdownlint.json`
- **YAML**: `yamllint` configuration in `pyproject.toml`
- **Quality gates**: `gatekeeper.toml`

### Excluding Files

Use `exclude` patterns in configurations:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["ARG001"]
"__init__.py" = ["F401"]
```

## Troubleshooting

### Common Issues

1. **Pre-commit hooks not running**: Ensure `pre-commit install` was run
2. **Linter dependencies missing**: Run `pip install -e .`
3. **Quality gate failing**: Check `quality_gate_results.json` for details
4. **Configuration conflicts**: Resolve by updating specific tool configurations

### Debug Mode

Run linters with verbose output:

```bash
# Ruff verbose
ruff check --verbose

# Black verbose
black --verbose

# MyPy verbose
mypy --verbose
```

## Maintenance

- Update linter versions regularly in `pre-commit-hooks.yaml`
- Monitor new rule releases in `pyproject.toml`
- Review quality gate thresholds in `gatekeeper.toml`
- Keep dependencies updated with `pip-compile`

## Integration with Other Projects

This linting configuration can be used as a template for other projects by:

1. Copying the `linting/` directory
2. Adjusting paths and exclusions
3. Updating quality gate thresholds as needed
4. Integrating with project-specific requirements

For full integration, ensure the configuration is included in the package data and properly referenced in each project's pyproject.toml.
