# phenotype-config

Shared configuration utilities for Phenotype services using Pydantic.

## Features

- **BaseConfig**: Pydantic BaseSettings for type-safe configuration
- **Environment Variables**: Automatic .env file and environment variable loading
- **Type Safety**: Full type hints and validation
- **Settings Cache**: Avoid repeated parsing with cached settings instances

## Installation

```bash
pip install phenotype-config
```

## Quick Start

```python
from phenotype_config import BaseConfig, get_settings

class MySettings(BaseConfig):
    api_key: str
    debug: bool = False
    database_url: str = "sqlite:///./test.db"

# Loads from environment and .env file
settings = MySettings()

# Or use the cached version
cached = get_settings(MySettings)
```

## License

MIT
