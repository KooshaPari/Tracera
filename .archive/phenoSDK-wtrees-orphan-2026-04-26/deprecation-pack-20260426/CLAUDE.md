# phenoSDK — CLAUDE.md

## Project Overview

Python SDK for Phenotype MCP and API integration.

**Language**: Python
**Location**: `phenoSDK/`

## Structure

```
src/pheno/
├── mcp/           # MCP entry points
├── shared/        # Shared utilities
├── adapters/      # Protocol adapters
└── application/   # Application services
```

## Key Commands

```bash
uv sync
uv run pytest
uv run ruff check
uv run mypy
```

## Development

1. Install dependencies: `uv sync`
2. Run tests: `uv run pytest`
3. Lint: `uv run ruff check`

## Testing

All tests should reference FRs:
```python
def test_feature():
    # Traces to: FR-XXX-NNN
    pass
```

## See Also

- **Monorepo Root**: `../../CLAUDE.md`
