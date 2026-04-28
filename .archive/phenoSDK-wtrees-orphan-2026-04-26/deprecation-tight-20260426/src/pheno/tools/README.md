# Tools (732 LOC)

Shared tools and utilities

## Overview

The `tools` module is a utility layer component of the Pheno SDK.

This module follows hexagonal architecture principles with clear separation of concerns.

## Architecture

- **Layer**: Utility
- **Pattern**: Hexagonal Architecture
- **Dependencies**: Core Python libraries
- **Components**: 4 Python files, 1 submodules

## Directory Structure

```
tools/
├── shared/
├── apilookup.py
├── deployment_checker.py
├── embedding_backfill.py
├── schema_sync.py
```

## Key Components

## Quick Start

### Basic Usage

```python
from pheno.tools import *

# Use tools functionality
# See submodule documentation for specific APIs
```

## Testing

```bash
# Run unit tests
pytest tests/unit/tools/

# Run with coverage
pytest --cov=src/pheno/tools tests/unit/tools/
```

## Configuration

Configure via environment variables:

```bash
# Module-specific configuration
PHENO_TOOLS_CONFIG=...
```

## Related Documentation

- [Architecture Guide](../../docs/architecture/README.md)
- [API Reference](../../docs/api/README.md)

### Submodules

- [shared](./shared/README.md)

## Module Statistics

- **Total LOC**: ~732
- **Python Files**: 4
- **Submodules**: 1
- **Public Classes**: 0
- **Public Functions**: 0
