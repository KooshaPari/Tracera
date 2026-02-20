# Team Onboarding Guide

Complete guide for new team members to get started with TraceRTM.

## Welcome to TraceRTM! 👋

TraceRTM is a modern Python project with ultra-strict infrastructure.

## Prerequisites

- Python 3.11+ (3.12 recommended)
- Git
- GitHub account
- IDE (VS Code, PyCharm, etc.)

## Setup (15 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/tracertm.git
cd tracertm
```

### 2. Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install Dependencies

```bash
# Install all dependencies (Phase 1 + 2 + 3)
uv sync --all

# Or just Phase 1 + 2 (recommended for new members)
uv sync --group dev
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

### 5. Verify Setup

```bash
# Run all quality checks
uv run poe all

# Should complete without errors
```

## Daily Workflow

### Before Starting Work

```bash
# Update dependencies
uv sync

# Pull latest changes
git pull origin develop
```

### Writing Code

```bash
# Format code
uv run poe format

# Lint code
uv run poe lint

# Type check
uv run poe type-check

# Run tests
uv run poe test
```

### Committing Code

```bash
# Pre-commit hooks run automatically
git add .
git commit -m "feat: add new feature"

# If hooks fail, fix issues and try again
```

### Creating Pull Request

```bash
# Push to feature branch
git push origin feature-branch

# Create PR on GitHub
# CI/CD workflows run automatically
# Address any failures
```

## Key Commands

### Code Quality

```bash
uv run poe format      # Format code
uv run poe lint        # Lint with auto-fix
uv run ty check src/ --error-on-warning  # Type check (ty)
uv run poe quality     # All quality checks
```

### Testing

```bash
uv run poe test        # Run all tests
uv run poe test-cov    # With coverage
uv run poe test-parallel  # Parallel execution
uv run poe test-unit   # Unit tests only
```

### Architecture

```bash
tach check             # Check architecture
tach show              # Visualize architecture
tach show --mermaid > architecture.md  # Generate diagram
```

### Security

```bash
uv run poe security    # Security scan
```

### Full Pipeline

```bash
uv run poe all         # Run everything
```

## Project Structure

```
tracertm/
├── src/tracertm/           # Source code
│   ├── config/             # Configuration
│   ├── models/             # Data models
│   ├── database/           # ORM layer
│   ├── services/           # Business logic
│   ├── api/                # API endpoints
│   ├── cli/                # CLI commands
│   ├── core/               # Core functionality
│   └── utils/              # Utilities
├── tests/                  # Test files
├── docs/                   # Documentation
├── pyproject.toml          # Project config
├── tach.yaml               # Architecture rules
└── .github/workflows/      # CI/CD workflows
```

## Architecture Layers

TraceRTM uses 8 modular layers:

1. **config** - Configuration management
2. **models** - Data models and schemas
3. **database** - ORM layer
4. **services** - Business logic
5. **api** - API endpoints
6. **cli** - Command-line interface
7. **core** - Core functionality
8. **utils** - Utility functions

**Rule**: Each layer can only depend on layers below it.

## Code Standards

### Type Annotations

```python
# ✅ GOOD: Full type annotations
def process_user(user_id: int) -> User:
    """Process a user by ID."""
    user = get_user(user_id)
    return user

# ❌ BAD: Missing type annotations
def process_user(user_id):
    user = get_user(user_id)
    return user
```

### Docstrings

```python
# ✅ GOOD: Clear docstrings
def calculate_coverage(implemented: int, total: int) -> float:
    """Calculate coverage percentage.
    
    Args:
        implemented: Number of implemented items
        total: Total number of items
        
    Returns:
        Coverage percentage (0-100)
    """
    return (implemented / total) * 100

# ❌ BAD: Missing docstrings
def calculate_coverage(implemented, total):
    return (implemented / total) * 100
```

### Error Handling

```python
# ✅ GOOD: Specific exceptions
try:
    user = get_user(user_id)
except UserNotFoundError:
    logger.error(f"User {user_id} not found")
    raise

# ❌ BAD: Bare except
try:
    user = get_user(user_id)
except:
    pass
```

## Testing

### Unit Tests

```python
def test_calculate_coverage() -> None:
    """Test coverage calculation."""
    result = calculate_coverage(50, 100)
    assert result == 50.0
```

### Property-Based Tests

```python
@given(priority=st.integers(1, 5))
def test_priority_valid(priority: int) -> None:
    """Test priority is always valid."""
    req = Requirement(priority=priority)
    assert 1 <= req.priority <= 5
```

### Running Tests

```bash
# All tests
uv run poe test

# With coverage
uv run poe test-cov

# Specific test
pytest tests/test_models.py::test_requirement_creation -v
```

## Debugging

### Enable Debug Logging

```python
from loguru import logger

logger.enable("tracertm")
logger.debug("Debug message")
```

### Run with Verbose Output

```bash
pytest tests/ -vv -s
```

### Type Check Specific File

```bash
ty check src/tracertm/models.py --error-on-warning
```

## Common Issues

### Pre-commit Hooks Fail

```bash
# Run hooks manually
pre-commit run --all-files

# Fix issues
uv run poe format
uv run poe lint

# Try commit again
```

### Type Errors

```bash
# Check with ty
uv run ty check src/ --error-on-warning

# Fix type annotations
```

### Test Failures

```bash
# Run specific test
pytest tests/test_models.py::test_name -vv

# Run with print statements
pytest tests/ -s

# Run with debugger
pytest tests/ --pdb
```

## Resources

- **Documentation**: See docs/ folder
- **Architecture**: See tach.yaml
- **Configuration**: See pyproject.toml
- **Workflows**: See .github/workflows/

## Getting Help

1. Check documentation
2. Search GitHub issues
3. Ask in team chat
4. Create GitHub issue

## Next Steps

1. Complete setup
2. Read PHASE_1_COMPLETE_SUMMARY.md
3. Read PHASE_2_COMPLETE_SUMMARY.md
4. Create a test PR
5. Ask questions!

Welcome to the team! 🚀
