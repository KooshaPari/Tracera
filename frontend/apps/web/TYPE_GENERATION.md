# TypeScript Type Generation from OpenAPI Specification

## Overview

This document describes the automated TypeScript type generation system for the TraceRTM API frontend. Types are generated directly from the OpenAPI 3.1.0 specification to ensure type safety and consistency between the frontend and backend.

## Architecture

### Generation Pipeline

```
OpenAPI Spec (public/specs/openapi.json)
           ↓
openapi-typescript (6.7.3)
           ↓
Generated Schema (src/api/schema.ts)
           ↓
Type Utilities (src/api/types.ts)
           ↓
API Clients & Components
```

### Key Files

1. **`public/specs/openapi.json`** - OpenAPI 3.1.0 specification (source of truth)
2. **`src/api/schema.ts`** - Auto-generated types from OpenAPI spec
3. **`src/api/types.ts`** - Type utilities and type extractors
4. **`package.json`** - Generation scripts and build integration

## Usage Guide

### Running Type Generation

```bash
# Manual generation
bun run generate:types

# Automatic generation (runs before dev/build)
bun run dev    # Generates types automatically
bun run build  # Generates types automatically
```

### Accessing Types

#### Using Path Operations

```typescript
import type { paths } from '@/api/schema';

// Get all path keys
type AllPaths = keyof paths;

// Get operations for a specific path
type ItemsOps = keyof paths['/api/v1/items'];
```

#### Using Type Extractors

```typescript
import type {
  ApiRequestBody,
  ApiResponse,
  ApiQueryParams,
  ApiPathParams,
  ApiAllParams,
} from '@/api/types';

// Extract request body type
type CreateItemBody = ApiRequestBody<'/api/v1/items', 'post'>;
// Type: { name: string; description?: string; ... }

// Extract response type
type ListItemsResponse = ApiResponse<'/api/v1/items', 'get'>;
// Type: { items: Item[]; total: number; page: number; pageSize: number; hasMore: boolean; }

// Extract query parameters
type ListItemsQuery = ApiQueryParams<'/api/v1/items', 'get'>;
// Type: { page?: number; limit?: number; ... }

// Extract path parameters
type GetItemParams = ApiPathParams<'/api/v1/items/{item_id}', 'get'>;
// Type: { item_id: string; }

// Extract all parameters
type ListItemsAllParams = ApiAllParams<'/api/v1/items', 'get'>;
// Type: { query?: { ... }; path?: { ... }; }
```

### In API Handlers

```typescript
import type { ApiResponse, ApiAllParams } from '@/api/types';

async function listItems(params: ApiAllParams<'/api/v1/items', 'get'>) {
  const response = await fetch('/api/v1/items', {
    query: params.query,
  });

  const data: ApiResponse<'/api/v1/items', 'get'> = await response.json();
  return data;
}
```

### In React Components

```typescript
import type { ApiResponse } from '@/api/types';
import { useQuery } from '@tanstack/react-query';

interface UseItemsProps {
  page?: number;
  limit?: number;
}

export function useItems(props: UseItemsProps) {
  return useQuery({
    queryKey: ['items', props],
    queryFn: async () => {
      const response = await fetch(
        `/api/v1/items?page=${props.page}&limit=${props.limit}`
      );

      const data: ApiResponse<'/api/v1/items', 'get'> =
        await response.json();

      return data.items;
    },
  });
}
```

## Type Utility Reference

### `ApiPaths`

All valid API path keys

```typescript
type ValidPath = ApiPaths;
// "health" | "/api/v1/items" | "/api/v1/items/{item_id}" | ...
```

### `PathOperations<P>`

All HTTP methods available for a path

```typescript
type ItemsOps = PathOperations<'/api/v1/items'>;
// "get" | "post"
```

### `ApiRequestBody<P, M>`

Request body type for operation

- Returns `never` if operation has no request body
- Returns typed request body object if operation accepts JSON

### `ApiResponse<P, M, Status>`

Response type for specific status code

- `Status` defaults to `200`
- Returns `never` if path/method/status doesn't exist
- Automatically extracts from `application/json` content

### `ApiQueryParams<P, M>`

Query string parameters

- Returns `never` if no query parameters
- Includes parameter descriptions as JSDoc comments

### `ApiPathParams<P, M>`

URL path parameters (e.g., `{id}` in `/items/{id}`)

- Returns `never` if path has no parameters
- Includes parameter descriptions as JSDoc comments

### `ApiAllParams<P, M>`

Combined parameters object

```typescript
type Params = ApiAllParams<'/api/v1/items/{id}', 'patch'>;
// { query?: {...}; path?: {id: string}; }
```

## OpenAPI Schema Structure

The generated schema exports the `paths` interface which follows this structure:

```typescript
export interface paths {
  [path: string]: {
    [method: string]: {
      parameters?: {
        query?: Record<string, any>;
        path?: Record<string, any>;
        header?: Record<string, any>;
      };
      requestBody?: {
        content: {
          'application/json': any;
        };
      };
      responses: {
        [statusCode: number]: {
          content: {
            'application/json': any;
          };
        };
      };
    };
  };
}
```

## Build Integration

### Automatic Type Generation

Types are automatically regenerated before `dev` and `build`:

```json
{
  "scripts": {
    "predev": "bun run generate:types",
    "prebuild": "bun run generate:types",
    "generate:types": "openapi-typescript public/specs/openapi.json -o src/api/schema.ts"
  }
}
```

### Skipping Linting

The generated `schema.ts` is excluded from linting to avoid issues with generated code:

```json
{
  "scripts": {
    "lint": "find src -type f ... ! -path 'src/api/schema.ts' | xargs biome check ..."
  }
}
```

## Maintenance

### Updating the OpenAPI Spec

1. Update `public/specs/openapi.json` with new endpoints
2. Run `bun run generate:types`
3. Types will be automatically generated
4. Use new types in components and services

### Validating the Spec

Validate the OpenAPI spec before generation:

```bash
# Using Redocly CLI
bun add -d redocly
bunx redocly lint public/specs/openapi.json
```

### Checking Generated Types

The generated schema includes 1227 lines with full type coverage for:

- 24+ endpoint operations
- All request/response types
- Query and path parameters
- HTTP status codes
- Response schemas

## Best Practices

1. **Always use type extractors** - Prefer `ApiResponse<>` over manual type definitions
2. **Generate before building** - Types are auto-generated, but you can manually run `bun run generate:types`
3. **Keep OpenAPI spec current** - The spec is the source of truth; always update it first
4. **Leverage JSDoc comments** - Parameter descriptions appear in IDE tooltips
5. **Type safety first** - Never use `any` types; always extract from schema
6. **Use specific status codes** - Be explicit about which response status you're handling

## Troubleshooting

### Types Not Updated

```bash
# Clear and regenerate
bun run generate:types

# Or
rm src/api/schema.ts && bun run predev
```

### Generation Fails

Check the OpenAPI spec is valid:

```bash
bunx redocly lint public/specs/openapi.json
```

### Missing Paths in Types

1. Verify the path exists in `public/specs/openapi.json`
2. Ensure the path is under `paths` (not `components`)
3. Regenerate: `bun run generate:types`

## Examples

### Complete API Hook Example

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import type { ApiResponse, ApiRequestBody, ApiAllParams } from '@/api/types';

// List items with type safety
export function useListItems(params?: ApiAllParams<'/api/v1/items', 'get'>) {
  return useQuery({
    queryKey: ['items', params],
    queryFn: async () => {
      const response = await fetch('/api/v1/items', {
        method: 'GET',
        params,
      });

      const data: ApiResponse<'/api/v1/items', 'get'> = await response.json();
      return data;
    },
  });
}

// Create item with type safety
export function useCreateItem() {
  return useMutation({
    mutationFn: async (body: ApiRequestBody<'/api/v1/items', 'post'>) => {
      const response = await fetch('/api/v1/items', {
        method: 'POST',
        body: JSON.stringify(body),
      });

      const data: ApiResponse<'/api/v1/items', 'post'> = await response.json();
      return data;
    },
  });
}
```

### Complete Component Example

```typescript
import { useListItems, useCreateItem } from '@/api/hooks';
import type { ApiRequestBody } from '@/api/types';

export function ItemsList() {
  const { data, isLoading } = useListItems({ page: 1, limit: 10 });
  const { mutate: createItem } = useCreateItem();

  const handleCreate = (body: ApiRequestBody<'/api/v1/items', 'post'>) => {
    createItem(body, {
      onSuccess: (data) => {
        // data is fully typed
        console.log(data);
      },
    });
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {data?.items.map((item) => (
        <div key={item.id}>{item.title}</div>
      ))}
    </div>
  );
}
```

## See Also

- [openapi-typescript Documentation](https://openapi-ts.dev/)
- [OpenAPI 3.1.0 Specification](https://spec.openapis.org/oas/v3.1.0)
- [TraceRTM API Documentation](../public/specs/openapi.json)
