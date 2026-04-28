# Setup Guide: Modern Python Infrastructure

This guide walks you through setting up the modernized Python infrastructure for TraceRTM.

## Quick Start

### 1. Install UV (Recommended)

UV is a fast, reliable Python package manager written in Rust.

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. Install Dependencies with UV

```bash
# Install all dependencies (including dev)
uv sync

# Or install specific groups
uv sync --group dev
uv sync --group test
uv sync --group lint
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor
```

### 4. Verify Installation

```bash
# Check settings load correctly
python3 << 'EOF'
from tracertm.config import get_settings
s = get_settings()
print(f"✓ Settings: log_level={s.log_level}, db={s.database.url}")
EOF

# Run tests
uv run pytest tests/ -v

# Check code quality
uv run ruff check src/
uv run mypy src/
```

## Alternative: Using Pip

If you prefer pip over uv:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run commands
pytest tests/ -v
ruff check src/
mypy src/
```

## Development Workflow

### Code Quality Checks

```bash
# Lint code
uv run ruff check src/

# Auto-fix issues
uv run ruff check --fix src/

# Format code
uv run ruff format src/

# Type checking
uv run mypy src/

# All checks at once
uv run ruff check --fix src/ && uv run ruff format src/ && uv run mypy src/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/tracertm --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_config.py -v

# Run tests matching pattern
uv run pytest -k "test_settings" -v

# Run specific marker
uv run pytest -m unit
uv run pytest -m integration
```

### Configuration Management

#### Using Environment Variables

```bash
# Set variables
export TRACERTM_LOG_LEVEL=DEBUG
export TRACERTM_DATABASE__URL=postgresql://user:pass@localhost/tracertm
export TRACERTM_MAX_AGENTS=500

# Run application
python3 -m tracertm.cli
```

#### Using .env File

```bash
# .env file
TRACERTM_LOG_LEVEL=DEBUG
TRACERTM_DATABASE__URL=postgresql://user:pass@localhost/tracertm
TRACERTM_MAX_AGENTS=500
TRACERTM_ENABLE_CACHE=true
```

#### In Python Code

```python
from tracertm.config import get_settings

settings = get_settings()
print(settings.log_level)
print(settings.database.url)
print(settings.max_agents)
```

## Troubleshooting

### UV Installation Issues

```bash
# If UV not found after installation
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Settings Not Loading

```bash
# Check if .env file exists
ls -la .env

# Verify environment variables
env | grep TRACERTM

# Test settings directly
python3 -c "from tracertm.config import get_settings; print(get_settings())"
```

### Import Errors

```bash
# Reinstall package in development mode
pip install --break-system-packages -e .

# Or with UV
uv sync
```

### Ruff/MyPy Not Found

```bash
# Install dev dependencies
uv sync --group dev

# Or with pip
pip install ruff mypy
```

## File Structure

```
tracertm/
├── pyproject.toml              # Main config (dependencies, tools)
├── settings.yml                # Default application settings
├── .env.example                # Environment variables template
├── .env                        # Local environment (git-ignored)
├── src/tracertm/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Modern pydantic-settings
│   │   ├── schema.py           # Legacy config schema
│   │   └── manager.py          # Config manager
│   └── ...
└── tests/
    └── ...
```

## Next Steps

1. Read `MODERN_PYTHON_INFRA.md` for detailed documentation
2. Review `pyproject.toml` for all available configurations
3. Check `settings.yml` for application settings
4. Run tests to verify everything works: `uv run pytest`

## References

- [UV Documentation](https://docs.astral.sh/uv/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [PyTest Documentation](https://docs.pytest.org/)

