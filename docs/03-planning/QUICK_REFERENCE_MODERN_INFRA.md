# Quick Reference: Modern Python Infrastructure

## Installation

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Or with pip
pip install -e ".[dev]"
```

## Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit settings
nano .env
```

## Common Commands

### Code Quality
```bash
uv run ruff check --fix src/    # Lint and fix
uv run ruff format src/         # Format code
uv run mypy src/                # Type check
```

### Testing
```bash
uv run pytest                   # Run all tests
uv run pytest --cov            # With coverage
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests
```

### Development
```bash
uv run rtm --help              # CLI help
uv run pytest -v               # Verbose tests
uv run pytest -k "test_name"   # Specific test
```

## Settings Usage

### In Python
```python
from tracertm.config import get_settings

settings = get_settings()
print(settings.log_level)           # INFO
print(settings.database.url)        # sqlite:///tracertm.db
print(settings.max_agents)          # 1000
```

### Environment Variables
```bash
export TRACERTM_LOG_LEVEL=DEBUG
export TRACERTM_DATABASE__URL=postgresql://...
export TRACERTM_MAX_AGENTS=500
```

### .env File
```
TRACERTM_LOG_LEVEL=DEBUG
TRACERTM_DATABASE__URL=postgresql://user:pass@localhost/tracertm
TRACERTM_MAX_AGENTS=500
```

## File Locations

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project config, dependencies, tools |
| `settings.yml` | Default application settings |
| `.env.example` | Environment variables template |
| `.env` | Local environment (git-ignored) |
| `src/tracertm/config/settings.py` | Settings module |

## Tool Versions

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| Ruff | 0.14.0+ | Linting & formatting |
| MyPy | 1.18.0+ | Type checking |
| PyTest | 9.0.0+ | Testing |
| Pydantic | 2.5.0+ | Validation |
| Pydantic-Settings | 2.3.0+ | Configuration |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: tracertm` | Run `pip install -e .` or `uv sync` |
| Settings not loading | Check `.env` exists, verify `TRACERTM_` prefix |
| Ruff not found | Run `uv sync --group dev` |
| Type errors | Run `uv run mypy src/` to see all errors |

## Configuration Hierarchy

1. CLI flags (when implemented)
2. Environment variables (`TRACERTM_*`)
3. `.env` file
4. `settings.yml`
5. Hardcoded defaults

## Key Features

✅ Type-safe configuration with pydantic  
✅ Environment variable support  
✅ .env file support  
✅ Automatic validation  
✅ Nested configuration  
✅ Singleton pattern  
✅ Auto-create directories  

## Documentation

- `MODERN_PYTHON_INFRA.md` - Full infrastructure guide
- `SETUP_MODERN_INFRA.md` - Detailed setup instructions
- `MODERNIZATION_SUMMARY.md` - Changes overview
- `pyproject.toml` - Tool configurations
- `settings.yml` - Available settings

## Next Steps

1. Run `uv sync` to install dependencies
2. Copy `.env.example` to `.env`
3. Run `uv run pytest` to verify setup
4. Read `MODERN_PYTHON_INFRA.md` for details

