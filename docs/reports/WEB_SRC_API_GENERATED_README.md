# Auto-Generated API Types

This directory contains TypeScript types auto-generated from OpenAPI specifications.

## Files

- `python-api.ts` - Types from Python FastAPI backend
- `go-api.ts` - Types from Go Echo backend
- `index.ts` - Unified exports

## Generation

```bash
# From project root
bun run generate:types

# Or with full pipeline
bun run generate:all
```

## Usage Examples

### Type-Safe API Client

```typescript
import createClient from 'openapi-fetch';
import type { paths } from './generated/python-api';

const client = createClient<paths>({
  baseUrl: 'http://localhost:4000',
});

// Fully typed request and response
const { data, error } = await client.GET('/items/{id}', {
  params: {
    path: { id: '123' },
  },
});

if (error) {
  console.error('Error:', error);
} else {
  console.log('Item:', data);
}
```

### Extract Response Types

```typescript
import type { paths } from './generated/python-api';

// Extract response type
type GetItemResponse =
  paths['/items/{id}']['get']['responses']['200']['content']['application/json'];

// Extract request body type
type CreateItemRequest = paths['/items']['post']['requestBody']['content']['application/json'];

// Use in your code
function displayItem(item: GetItemResponse) {
  console.log(item.id, item.title);
}
```

### React Query Integration

```typescript
import { useQuery } from '@tanstack/react-query';
import type { paths } from './generated/python-api';

type ItemsResponse = paths['/items']['get']['responses']['200']['content']['application/json'];

function useItems() {
  return useQuery<ItemsResponse>({
    queryKey: ['items'],
    queryFn: async () => {
      const { data, error } = await client.GET('/items');
      if (error) throw error;
      return data;
    },
  });
}
```

## Notes

- These files are auto-generated - **do not edit manually**
- Regenerate after any API changes
- Types match the OpenAPI specs exactly
- See [API Contract Generation Guide](../../../../../../docs/guides/API_CONTRACT_GENERATION.md) for details
