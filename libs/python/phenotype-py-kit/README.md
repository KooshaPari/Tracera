# Phenotype Python Kit

Shared Python utilities for Phenotype projects, providing base configuration, structured logging, testing utilities, and FastAPI app factory.

## Features

- **BaseConfig**: Pydantic-based settings with environment variable support
- **Structured Logging**: JSON logging with structlog for machine-readable output
- **Testing Utilities**: Shared pytest fixtures (tmp_dir, mock_config, async helpers)
- **FastAPI App Factory**: Pre-configured FastAPI with CORS, request ID injection, and error handling

## Installation

```bash
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### Configuration

```python
from phenotype_kit import BaseConfig

class MySettings(BaseConfig):
    api_key: str
    debug: bool = False

# Loads from environment variables and .env file
settings = MySettings()
```

### Logging

```python
from phenotype_kit import configure_logging, get_logger

configure_logging(level="DEBUG", service_name="my-service")
logger = get_logger(__name__)
logger.info("service started", version="1.0.0")
```

### FastAPI

```python
from fastapi import FastAPI
from phenotype_kit import create_app

app = create_app(
    title="My Service",
    version="1.0.0",
    cors_origins=["http://localhost:3000"],
)

@app.get("/api/example")
async def example():
    return {"message": "Hello"}
```

### Testing

```python
import pytest

def test_something(tmp_dir, mock_config, async_helper):
    # tmp_dir: temporary Path
    # mock_config: BaseConfig with test defaults
    # async_helper: async test utilities
    pass
```

## Structure

```
phenotype-py-kit/
├── pyproject.toml           # Package config with pydantic, structlog deps
└── src/
    └── phenotype_kit/
        ├── __init__.py
        ├── config.py        # BaseSettings factory with env loading
        ├── logging.py       # Structured JSON logging with structlog
        ├── testing.py       # Shared pytest fixtures
        └── api.py           # FastAPI app factory with middleware
```

## License

Proprietary - Phenotype Organization
