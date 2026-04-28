# OpenAPI Specifications

This directory contains auto-generated OpenAPI specifications for the TraceRTM APIs.

## Files

- `python-api.json` - Python FastAPI backend specification
- `go-api.json` - Go Echo backend specification
- `gateway-api.json` - **Merged gateway contract** (single entrypoint for external clients; server URL = gateway).

**Gateway contract (no servers needed):** Backend spec **files** (`go-api.json`, `python-api.json`) are produced **from source** by `bun run generate:openapi` (Python: FastAPI in-process; Go: swag from code). Then run `bun run generate:openapi:gateway` to merge them, or `bun run generate:all` to do both plus types/clients.

## Generation Methods

### Method 1: From Running Servers (Recommended)

Fetch specs from running API servers:

```bash
# Start the servers first
overmind start

# Then generate
./scripts/generate-openapi-from-server.sh
```

**Pros:**
- No dependency issues
- Always reflects current server state
- Fast and reliable

**Cons:**
- Requires servers to be running
- Can't generate offline

### Method 2: From Source Code

Generate directly from code (offline):

```bash
# Python API
./scripts/generate-openapi-python.sh

# Go API
./scripts/generate-openapi-go.sh
```

**Pros:**
- Works offline
- Doesn't require running servers

**Cons:**
- Requires all dependencies installed
- Python: needs `uv sync --extra full`
- Go: needs `swag` installed

## Usage

After generating specs, create type-safe clients:

```bash
# Generate TypeScript types for frontend
./scripts/generate-typescript-types.sh

# Generate Python clients for CLI
./scripts/generate-python-client.sh

# Or generate everything
./scripts/generate-all-api-contracts.sh
```

## Documentation

Full documentation: [API Contract Generation Guide](../docs/guides/API_CONTRACT_GENERATION.md)

## Interactive API Documentation

View interactive docs from running servers:

- **Python FastAPI** (direct): http://localhost:4000/docs (Swagger UI). Prefer gateway: http://localhost:4000
- **Go Echo**: http://localhost:8080/swagger/index.html (Swagger UI)
