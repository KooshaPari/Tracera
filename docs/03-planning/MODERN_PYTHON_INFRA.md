# Modern Python Infrastructure & Libraries

This document describes the modernized Python infrastructure for TraceRTM (2025).

## Overview

The project now uses modern Python best practices and tools:

- **Package Manager**: `uv` (fast, reliable Python package manager)
- **Build System**: `hatchling` (modern, standards-compliant build backend)
- **Configuration**: `pydantic-settings` (type-safe, validated configuration)
- **Linting**: `ruff` (Rust-based, 10-100x faster than traditional tools)
- **Type Checking**: `mypy` (strict mode enabled)
- **Testing**: `pytest` with async support

## Key Files

### `pyproject.toml`
Central configuration file for all Python tooling:
- Project metadata and dependencies
- Build system configuration (hatchling)
- Tool configurations (ruff, mypy, pytest, coverage)
- UV package manager settings

### `settings.yml`
Default application configuration with all available options documented.

### `.env.example`
Template for environment variables. Copy to `.env` for local development.

### `src/tracertm/config/settings.py`
Modern pydantic-settings based configuration module with:
- Type-safe settings classes
- Environment variable support (TRACERTM_* prefix)
- .env file support
- Automatic directory creation
- Singleton pattern for settings access

## Usage

### Installation

```bash
# Install with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your settings:
   ```bash
   TRACERTM_LOG_LEVEL=DEBUG
   TRACERTM_DATABASE__URL=postgresql://user:pass@localhost/tracertm
   ```

3. In your code:
   ```python
   from tracertm.config import get_settings
   
   settings = get_settings()
   print(settings.log_level)  # DEBUG
   print(settings.database.url)  # postgresql://...
   ```

### Linting & Formatting

```bash
# Check code
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type checking
uv run mypy src/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/tracertm

# Run specific markers
uv run pytest -m unit
uv run pytest -m integration
```

## Configuration Hierarchy

Settings are loaded in this order (highest to lowest precedence):

1. CLI flags (when implemented)
2. Environment variables (`TRACERTM_*`)
3. `.env` file
4. `settings.yml`
5. Hardcoded defaults in `TraceSettings`

## Environment Variables

All settings can be overridden via environment variables with `TRACERTM_` prefix:

```bash
# Simple values
TRACERTM_LOG_LEVEL=DEBUG
TRACERTM_MAX_AGENTS=500

# Nested values (use __)
TRACERTM_DATABASE__URL=postgresql://...
TRACERTM_DATABASE__POOL_SIZE=20
```

## Dependencies

### Core
- `typer[all]`: CLI framework
- `rich`: Terminal formatting
- `pydantic`: Data validation
- `pydantic-settings`: Configuration management
- `sqlalchemy`: ORM
- `alembic`: Database migrations
- `pyyaml`: YAML support

### Development
- `pytest`: Testing framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `ruff`: Linting and formatting
- `mypy`: Type checking

## Migration from Old Setup

If migrating from `requirements.txt`:

1. Dependencies are now in `pyproject.toml`
2. Use `uv sync` instead of `pip install -r requirements.txt`
3. Use `pydantic-settings` instead of `python-dotenv`
4. Use `ruff` instead of black/flake8/isort

## Best Practices

1. **Always use type hints** - mypy strict mode is enabled
2. **Use pydantic-settings** - for all configuration needs
3. **Use ruff** - for linting and formatting
4. **Keep modules small** - ruff enforces max 350 lines
5. **Write tests** - use pytest with appropriate markers
6. **Use async** - leverage async/await for I/O operations

## Troubleshooting

### Settings not loading
- Check `.env` file exists and is readable
- Verify `TRACERTM_` prefix on environment variables
- Use `get_settings()` to access settings

### Ruff errors
- Run `uv run ruff check --fix .` to auto-fix
- Check `pyproject.toml` for rule configuration

### Type errors
- Run `uv run mypy src/` to see all errors
- Add type hints to function signatures
- Use `# type: ignore` sparingly for legitimate cases

## References

- [UV Documentation](https://docs.astral.sh/uv/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Hatchling](https://hatch.pypa.io/latest/build/)

