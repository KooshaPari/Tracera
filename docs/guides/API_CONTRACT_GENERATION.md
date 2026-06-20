# API Contract Generation Guide

## Overview

TraceRTM uses OpenAPI specifications to automatically generate type-safe clients and TypeScript types from both the Python FastAPI backend and the Go Echo backend. This ensures type consistency across the entire stack.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     OpenAPI Generation                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐          ┌──────▼───────┐
        │  Python FastAPI │          │   Go Echo    │
        │    Backend      │          │   Backend    │
        └───────┬────────┘          └──────┬───────┘
                │                           │
                │ Auto-generated            │ swag annotations
                │ from code                 │ + swag init
                │                           │
        ┌───────▼────────┐          ┌──────▼───────┐
        │ python-api.json │          │ go-api.json  │
        └───────┬────────┘          └──────┬───────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Type Generation  │
                    └─────────┬─────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐          ┌──────▼───────┐
        │   TypeScript   │          │    Python    │
        │     Types      │          │   Clients    │
        │  (Frontend)    │          │    (CLI)     │
        └────────────────┘          └──────────────┘
```

## Quick Start

### Generate Everything

```bash
# Run all generation steps
bun run generate:all

# Or use the npm script
npm run generate:all
```

### Individual Generation Steps

```bash
# 1. Generate OpenAPI specs only
bun run generate:openapi

# 2. Generate TypeScript types only
bun run generate:types

# 3. Generate Python clients only
bun run generate:client
```

## Generated Files

### OpenAPI Specifications
- `openapi/python-api.json` - Python FastAPI backend spec
- `openapi/go-api.json` - Go Echo backend spec

### TypeScript Types
- `frontend/apps/web/src/api/generated/python-api.ts` - Python API types
- `frontend/apps/web/src/api/generated/go-api.ts` - Go API types
- `frontend/apps/web/src/api/generated/index.ts` - Unified exports

### Python Clients
- `src/tracertm/generated/python_api_client/` - Python API client
- `src/tracertm/generated/go_api_client/` - Go API client
- `src/tracertm/generated/__init__.py` - Client exports

## Python FastAPI Backend

### How It Works

FastAPI automatically generates OpenAPI specs from your code. The generation script:

1. Imports the FastAPI app
2. Calls `app.openapi()` to get the schema
3. Writes it to `openapi/python-api.json`

### Script

```bash
./scripts/generate-openapi-python.sh
```

### Example Usage

```python
# In your FastAPI code
from fastapi import FastAPI

app = FastAPI(
    title="TraceRTM API",
    description="Traceability Requirements Tracking Management API",
    version="1.0.0",
)

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    """Get an item by ID."""
    return {"item_id": item_id}
```

This automatically generates OpenAPI documentation.

## Go Echo Backend

### How It Works

Uses `swag` (Swagger for Go) to generate OpenAPI from annotations:

1. Annotate handlers with swag comments
2. Run `swag init` to generate docs
3. Copy to `openapi/go-api.json`

### Script

```bash
./scripts/generate-openapi-go.sh
```

### Adding Swag Annotations

```go
// main.go
// @title TraceRTM API
// @version 1.0
// @description TraceRTM Backend API
// @host localhost:8080
// @BasePath /api/v1

package main

// Example handler annotation
// @Summary Get item by ID
// @Description Get a single item by its ID
// @Tags items
// @Accept json
// @Produce json
// @Param id path string true "Item ID"
// @Success 200 {object} Item
// @Failure 404 {object} ErrorResponse
// @Router /items/{id} [get]
func getItem(c echo.Context) error {
    // handler code
}
```

### Installing swag

The script automatically installs swag if not present:

```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

## TypeScript Type Generation

### How It Works

Uses `openapi-typescript` to generate TypeScript types from OpenAPI specs:

```bash
./scripts/generate-typescript-types.sh
```

### Using Generated Types

```typescript
// Import the generated types
import type { paths } from '@/api/generated';

// Use them for type-safe API calls
type GetItemResponse = paths['/items/{id}']['get']['responses']['200']['content']['application/json'];

// With openapi-fetch
import createClient from 'openapi-fetch';
import type { paths } from '@/api/generated/python-api';

const client = createClient<paths>({ baseUrl: 'http://localhost:4000' });

// Fully typed request and response
const { data, error } = await client.GET('/items/{id}', {
  params: {
    path: { id: '123' }
  }
});
```

## Python Client Generation

### How It Works

Uses `openapi-python-client` to generate Python clients:

```bash
./scripts/generate-python-client.sh
```

### Using Generated Clients

```python
# Import the generated client
from tracertm.generated import PythonAPIClient, GoAPIClient

# Create a client instance
client = PythonAPIClient(base_url="http://localhost:4000")

# Make type-safe API calls
response = await client.items.get_item(item_id="123")
print(response.parsed)
```

## Development Workflow

### Option 1: Watch Mode (Recommended)

Add to your `Procfile`:

```procfile
# Optional: Auto-regenerate on changes
api_types: watchexec -w src/tracertm/api -w backend/internal -- bun run generate:all
```

### Option 2: Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/sh
# Regenerate API contracts
bun run generate:all

# Stage any changes
git add openapi/ frontend/apps/web/src/api/generated/ src/tracertm/generated/
```

### Option 3: CI/CD Pipeline

```yaml
# .github/workflows/api-contracts.yml
name: API Contracts
on: [push, pull_request]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun run generate:all
      - run: git diff --exit-code
```

## Troubleshooting

### Python Virtual Environment Not Found

```bash
Error: Python virtual environment not found
```

**Solution:** Run `uv sync` to create the virtual environment.

### swag Command Not Found

```bash
Error: swag not found
```

**Solution:** Ensure `$GOPATH/bin` is in your PATH:

```bash
export PATH="$PATH:$HOME/go/bin"
```

### OpenAPI Specs Not Found

```bash
Error: No OpenAPI specs found
```

**Solution:** Generate OpenAPI specs first:

```bash
bun run generate:openapi
```

### Type Generation Fails

If TypeScript type generation fails, check:

1. OpenAPI spec is valid JSON
2. `openapi-typescript` is installed
3. File permissions are correct

```bash
# Validate OpenAPI spec
cd frontend
bunx openapi-typescript --help

# Check spec validity
bunx redocly lint ../../openapi/python-api.json
```

## Best Practices

### 1. Keep Specs in Sync

Always regenerate after API changes:

```bash
# After modifying Python API
bun run generate:openapi:python && bun run generate:types

# After modifying Go API
bun run generate:openapi:go && bun run generate:types
```

### 2. Version Control

**Commit** generated specs:
- `openapi/*.json` - OpenAPI specifications

**Consider gitignoring** generated clients (they can be regenerated):
- `frontend/apps/web/src/api/generated/`
- `src/tracertm/generated/`

Or commit them for offline development.

### 3. Documentation

Both backends expose Swagger UI for interactive documentation:

- Python FastAPI: `http://localhost:4000/docs`
- Go Echo: `http://localhost:8080/swagger/index.html`

### 4. Breaking Changes

When making breaking API changes:

1. Update version in OpenAPI spec
2. Regenerate all contracts
3. Update dependent code
4. Run tests

```bash
bun run generate:all
bun test
cd frontend && bun test
```

## Advanced Usage

### Custom Generation Options

Edit the scripts to customize generation:

#### TypeScript Types

```bash
# Edit scripts/generate-typescript-types.sh
bunx openapi-typescript "$OPENAPI_DIR/python-api.json" \
    --output "$OUTPUT_DIR/python-api.ts" \
    --export-type \
    --path-params-as-types \
    --alphabetize \
    --enum
```

#### Python Client

```bash
# Edit scripts/generate-python-client.sh
openapi-python-client generate \
    --path "$OPENAPI_DIR/python-api.json" \
    --output-path "$OUTPUT_DIR/python_api_client" \
    --overwrite \
    --meta setup
```

### Multiple API Versions

To support multiple API versions:

```bash
# Generate v1 types
bunx openapi-typescript openapi/python-api-v1.json -o src/api/generated/v1.ts

# Generate v2 types
bunx openapi-typescript openapi/python-api-v2.json -o src/api/generated/v2.ts
```

## Integration Examples

### Frontend API Client

```typescript
// src/api/client.ts
import createClient from 'openapi-fetch';
import type { paths as PythonPaths } from './generated/python-api';
import type { paths as GoPaths } from './generated/go-api';

export const pythonClient = createClient<PythonPaths>({
  baseUrl: import.meta.env.VITE_PYTHON_API_URL,
});

export const goClient = createClient<GoPaths>({
  baseUrl: import.meta.env.VITE_GO_API_URL,
});

// Usage
const { data, error } = await pythonClient.GET('/items/{id}', {
  params: { path: { id: '123' } }
});
```

### Python CLI Client

```python
# src/tracertm/cli/api_client.py
from tracertm.generated import PythonAPIClient
from tracertm.config.manager import ConfigManager

config = ConfigManager()
client = PythonAPIClient(base_url=config.api_url)

async def get_item(item_id: str):
    """Get item from API."""
    response = await client.items.get_item(item_id=item_id)
    return response.parsed
```

## Scripts Reference

| Script | Purpose | Output |
|--------|---------|--------|
| `generate-openapi-python.sh` | Python API spec | `openapi/python-api.json` |
| `generate-openapi-go.sh` | Go API spec | `openapi/go-api.json` |
| `generate-typescript-types.sh` | TypeScript types | `frontend/apps/web/src/api/generated/` |
| `generate-python-client.sh` | Python clients | `src/tracertm/generated/` |
| `generate-all-api-contracts.sh` | All of the above | All outputs |

## Next Steps

1. **Add to Development Workflow**: Include generation in your Procfile
2. **Set Up CI/CD**: Automate generation in your pipeline
3. **Document Your APIs**: Add detailed descriptions in OpenAPI annotations
4. **Type Everything**: Use generated types throughout your codebase
5. **Test Contracts**: Write contract tests to ensure API compatibility

## Resources

- [FastAPI OpenAPI](https://fastapi.tiangolo.com/advanced/extending-openapi/)
- [swag Documentation](https://github.com/swaggo/swag)
- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
