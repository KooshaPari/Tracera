# API Generation Quick Reference

## Quick Commands

```bash
# Generate everything (recommended)
bun run generate:all

# Individual steps
bun run generate:openapi        # Both Python and Go specs
bun run generate:types          # TypeScript types
bun run generate:client         # Python clients

# From running servers (alternative)
./scripts/generate-openapi-from-server.sh
```

## File Locations

| Generated Files | Location |
|----------------|----------|
| OpenAPI Specs | `openapi/python-api.json`, `openapi/go-api.json` |
| TypeScript Types | `frontend/apps/web/src/api/generated/*.ts` |
| Python Clients | `src/tracertm/generated/python_api_client/`, `src/tracertm/generated/go_api_client/` |

## Prerequisites

### Python API Generation
```bash
# Option 1: From source (requires dependencies)
uv sync --extra full

# Option 2: From running server
overmind start
```

### Go API Generation
```bash
# Install swag
go install github.com/swaggo/swag/cmd/swag@latest

# Generate docs
cd backend && swag init
```

### TypeScript Generation
```bash
# Already installed in frontend
cd frontend && bun install
```

### Python Client Generation
```bash
# Install generator
uv pip install openapi-python-client
```

## Common Workflows

### Development Workflow
```bash
# 1. Make API changes
# 2. Regenerate contracts
bun run generate:all
# 3. Update dependent code
# 4. Test
bun test
```

### CI/CD Workflow
```yaml
- name: Generate API Contracts
  run: bun run generate:all

- name: Check for changes
  run: git diff --exit-code
```

### Watch Mode
Add to `Procfile`:
```
api_types: watchexec -w src/tracertm/api -w backend/internal -- bun run generate:all
```

## Usage Examples

### TypeScript
```typescript
import createClient from 'openapi-fetch';
import type { paths } from '@/api/generated/python-api';

const client = createClient<paths>({ baseUrl: 'http://localhost:4000' });
const { data } = await client.GET('/items/{id}', { params: { path: { id: '123' } } });
```

### Python
```python
from tracertm.generated import PythonAPIClient

async with PythonAPIClient(base_url="http://localhost:4000") as client:
    item = await client.items.get_item(item_id="123")
    print(item.parsed)
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| Virtual environment not found | `uv sync --extra full` |
| swag not found | `go install github.com/swaggo/swag/cmd/swag@latest` |
| OpenAPI spec not found | Generate specs first: `bun run generate:openapi` |
| Server not running | `overmind start` then use `generate-openapi-from-server.sh` |

## Interactive Documentation

- Python FastAPI: http://localhost:4000/docs
- Go Echo: http://localhost:8080/swagger/index.html

## Scripts

| Script | Purpose |
|--------|---------|
| `generate-openapi-python.sh` | Python spec from source |
| `generate-openapi-go.sh` | Go spec from source |
| `generate-openapi-from-server.sh` | Specs from running servers |
| `generate-typescript-types.sh` | TypeScript types |
| `generate-python-client.sh` | Python clients |
| `generate-all-api-contracts.sh` | All of the above |

## Best Practices

✓ **DO**
- Regenerate after API changes
- Commit OpenAPI specs to git
- Use generated types throughout codebase
- Add generation to CI/CD

✗ **DON'T**
- Edit generated files manually
- Skip type generation
- Ignore API contract changes
- Commit without regenerating

## Next Steps

1. **Setup**: Install dependencies and generate initial contracts
2. **Integrate**: Use generated types in your code
3. **Automate**: Add to development workflow
4. **Test**: Write contract tests

See: [API Contract Generation Guide](../guides/API_CONTRACT_GENERATION.md)
