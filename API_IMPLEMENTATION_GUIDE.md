# TraceRTM Multi-Dimensional Traceability API - Implementation Guide

## Quick Start

The comprehensive OpenAPI specification for TraceRTM's multi-dimensional traceability endpoints has been created and is ready for implementation. This guide covers how to use and implement these new API endpoints.

---

## What Was Created

### 1. OpenAPI Specification
**File:** `/frontend/apps/web/public/specs/openapi.json`

A complete OpenAPI 3.1.0 specification including:
- 26 endpoints across 8 API tags
- 40+ reusable schema definitions
- Comprehensive error handling
- Request/response examples
- Security schemes (JWT Bearer and API Key)

### 2. Documentation
**File:** `/OPENAPI_SPECIFICATION.md`

Full reference documentation including:
- Detailed endpoint descriptions
- Parameter and response specifications
- Schema definitions with examples
- Usage examples with curl commands
- HTTP status codes and error codes

---

## New Endpoint Categories

### 1. Equivalences (4 endpoints)
Manage equivalent items across different projects and dimensions.

- **GET** `/api/v1/projects/{projectId}/equivalences` - List all equivalences
- **POST** `/api/v1/projects/{projectId}/equivalences/detect` - Auto-detect equivalences
- **POST** `/api/v1/equivalences/{id}/confirm` - Confirm an equivalence
- **POST** `/api/v1/equivalences/{id}/reject` - Reject an equivalence

**Key Features:**
- Similarity-based detection with configurable threshold (0-1)
- Dimension-aware matching
- Confidence scoring for suggestions
- Manual confirmation/rejection workflow

### 2. Canonical Concepts (5 endpoints)
Manage universal concepts that project across multiple dimensions.

- **GET** `/api/v1/projects/{projectId}/canonical-concepts` - List concepts
- **POST** `/api/v1/projects/{projectId}/canonical-concepts` - Create concept
- **GET** `/api/v1/canonical-concepts/{id}` - Get concept details
- **GET** `/api/v1/canonical-concepts/{id}/projections` - Get projections
- **POST** `/api/v1/items/{id}/pivot` - Convert item to projection

**Key Features:**
- Multi-dimensional concept representation
- Projection mapping across dimensions
- Automatic reference updating
- Confidence-based mapping

### 3. Journeys (4 endpoints)
Track requirements through user flows, data flows, system processes, and integrations.

- **GET** `/api/v1/projects/{projectId}/journeys` - List journeys
- **POST** `/api/v1/projects/{projectId}/journeys` - Create journey
- **POST** `/api/v1/projects/{projectId}/journeys/detect` - Auto-detect journeys
- **GET** `/api/v1/journeys/{id}` - Get journey details

**Key Features:**
- Multiple journey types: user, system, data, integration
- Ordered step sequences
- Automatic journey detection from traces
- Configurable minimum path length

### 4. Component Libraries (4 endpoints)
Manage design components and tokens.

- **GET** `/api/v1/projects/{projectId}/component-libraries` - List libraries
- **GET** `/api/v1/component-libraries/{id}/components` - List components
- **GET** `/api/v1/components/{id}/usage` - Get usage information
- **GET** `/api/v1/component-libraries/{id}/tokens` - Get design tokens

**Key Features:**
- Component categorization
- Design token management (colors, typography, spacing, etc.)
- Usage tracking and analytics
- Category-based filtering

---

## Schema Definitions

### Core Schemas

#### EquivalenceResponse
```typescript
interface EquivalenceResponse {
  id: string;
  item_ids: string[];
  status: "suggested" | "confirmed" | "rejected";
  confidence: number; // 0-1
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  notes?: string;
}
```

#### CanonicalConceptResponse
```typescript
interface CanonicalConceptResponse {
  id: string;
  name: string;
  description?: string;
  item_ids: string[];
  dimensions: string[];
  created_at: string;
  updated_at: string;
}
```

#### JourneyResponse
```typescript
interface JourneyResponse {
  id: string;
  name: string;
  description?: string;
  type: "user" | "system" | "data" | "integration";
  steps: JourneyStep[];
  created_at: string;
  updated_at: string;
}

interface JourneyStep {
  id: string;
  order: number;
  name: string;
  item_id: string;
  description?: string;
  metadata?: Record<string, any>;
}
```

#### ComponentLibraryResponse
```typescript
interface ComponentLibraryResponse {
  id: string;
  name: string;
  description?: string;
  version: string;
  component_count: number;
  created_at: string;
  updated_at: string;
}
```

---

## Implementation Steps

### Step 1: Frontend API Client

Create TypeScript interfaces in `/frontend/apps/web/src/api/types.ts`:

```typescript
// Equivalences
export interface Equivalence {
  id: string;
  itemIds: string[];
  status: "suggested" | "confirmed" | "rejected";
  confidence: number;
  createdAt: Date;
  updatedAt: Date;
  notes?: string;
}

// Canonical Concepts
export interface CanonicalConcept {
  id: string;
  name: string;
  description?: string;
  itemIds: string[];
  dimensions: string[];
  createdAt: Date;
  updatedAt: Date;
}

// Journeys
export interface Journey {
  id: string;
  name: string;
  description?: string;
  type: "user" | "system" | "data" | "integration";
  steps: JourneyStep[];
  createdAt: Date;
  updatedAt: Date;
}

// Component Libraries
export interface ComponentLibrary {
  id: string;
  name: string;
  description?: string;
  version: string;
  componentCount: number;
  createdAt: Date;
  updatedAt: Date;
}
```

### Step 2: API Endpoints

Create endpoint definitions in `/frontend/apps/web/src/api/endpoints.ts`:

```typescript
// ============================================================================
// EQUIVALENCES
// ============================================================================

export const equivalencesApi = {
  list: async (projectId: string, params?: { status?: string; skip?: number; limit?: number }) => {
    return handleApiResponse<{ total: number; equivalences: Equivalence[] }>(
      apiClient.GET("/api/v1/projects/{projectId}/equivalences", {
        params: { path: { projectId }, query: params },
      }),
    );
  },

  detect: async (projectId: string, data: { dimensions: string[]; threshold?: number; exclude_ids?: string[] }) => {
    return handleApiResponse<{ detected_count: number; suggestions: Equivalence[] }>(
      apiClient.POST("/api/v1/projects/{projectId}/equivalences/detect", {
        params: { path: { projectId } },
        body: data,
      }),
    );
  },

  confirm: async (id: string, notes?: string) => {
    return handleApiResponse<Equivalence>(
      apiClient.POST("/api/v1/equivalences/{id}/confirm", {
        params: { path: { id } },
        body: notes ? { notes } : undefined,
      }),
    );
  },

  reject: async (id: string, reason?: string) => {
    return handleApiResponse<Equivalence>(
      apiClient.POST("/api/v1/equivalences/{id}/reject", {
        params: { path: { id } },
        body: reason ? { reason } : undefined,
      }),
    );
  },
};

// ============================================================================
// CANONICAL CONCEPTS
// ============================================================================

export const canonicalConceptsApi = {
  list: async (projectId: string, params?: { skip?: number; limit?: number }) => {
    return handleApiResponse<{ total: number; concepts: CanonicalConcept[] }>(
      apiClient.GET("/api/v1/projects/{projectId}/canonical-concepts", {
        params: { path: { projectId }, query: params },
      }),
    );
  },

  create: async (projectId: string, data: { name: string; description?: string; item_ids: string[] }) => {
    return handleApiResponse<CanonicalConcept>(
      apiClient.POST("/api/v1/projects/{projectId}/canonical-concepts", {
        params: { path: { projectId } },
        body: data,
      }),
    );
  },

  get: async (id: string) => {
    return handleApiResponse<CanonicalConcept>(
      apiClient.GET("/api/v1/canonical-concepts/{id}", {
        params: { path: { id } },
      }),
    );
  },

  getProjections: async (id: string, dimension?: string) => {
    return handleApiResponse<{ total: number; projections: Projection[] }>(
      apiClient.GET("/api/v1/canonical-concepts/{id}/projections", {
        params: { path: { id }, query: dimension ? { dimension } : undefined },
      }),
    );
  },

  pivot: async (itemId: string, data: { canonical_concept_id: string; update_references?: boolean }) => {
    return handleApiResponse<{ item_id: string; canonical_concept_id: string; updated_references: number }>(
      apiClient.POST("/api/v1/items/{id}/pivot", {
        params: { path: { id: itemId } },
        body: data,
      }),
    );
  },
};

// ============================================================================
// JOURNEYS
// ============================================================================

export const journeysApi = {
  list: async (projectId: string, params?: { type?: string; skip?: number; limit?: number }) => {
    return handleApiResponse<{ total: number; journeys: Journey[] }>(
      apiClient.GET("/api/v1/projects/{projectId}/journeys", {
        params: { path: { projectId }, query: params },
      }),
    );
  },

  create: async (projectId: string, data: CreateJourneyRequest) => {
    return handleApiResponse<Journey>(
      apiClient.POST("/api/v1/projects/{projectId}/journeys", {
        params: { path: { projectId } },
        body: data,
      }),
    );
  },

  detect: async (projectId: string, data: { journey_type: string; min_path_length?: number; max_results?: number }) => {
    return handleApiResponse<{ detected_count: number; journeys: Journey[] }>(
      apiClient.POST("/api/v1/projects/{projectId}/journeys/detect", {
        params: { path: { projectId } },
        body: data,
      }),
    );
  },

  get: async (id: string) => {
    return handleApiResponse<Journey>(
      apiClient.GET("/api/v1/journeys/{id}", {
        params: { path: { id } },
      }),
    );
  },
};

// ============================================================================
// COMPONENT LIBRARIES
// ============================================================================

export const componentLibrariesApi = {
  list: async (projectId: string, params?: { skip?: number; limit?: number }) => {
    return handleApiResponse<{ total: number; libraries: ComponentLibrary[] }>(
      apiClient.GET("/api/v1/projects/{projectId}/component-libraries", {
        params: { path: { projectId }, query: params },
      }),
    );
  },

  getComponents: async (libraryId: string, params?: { category?: string; skip?: number; limit?: number }) => {
    return handleApiResponse<{ total: number; components: Component[] }>(
      apiClient.GET("/api/v1/component-libraries/{id}/components", {
        params: { path: { id: libraryId }, query: params },
      }),
    );
  },

  getComponentUsage: async (componentId: string) => {
    return handleApiResponse<{ component_id: string; usage_count: number; used_in_items: string[]; last_used?: string }>(
      apiClient.GET("/api/v1/components/{id}/usage", {
        params: { path: { id: componentId } },
      }),
    );
  },

  getDesignTokens: async (libraryId: string, category?: string) => {
    return handleApiResponse<{ library_id: string; tokens: DesignToken[]; total: number }>(
      apiClient.GET("/api/v1/component-libraries/{id}/tokens", {
        params: { path: { id: libraryId }, query: category ? { category } : undefined },
      }),
    );
  },
};
```

### Step 3: React Hooks

Create custom hooks in `/frontend/apps/web/src/hooks/`:

```typescript
// useEquivalences.ts
import { useQuery, useMutation } from "@tanstack/react-query";
import { equivalencesApi } from "@/api/endpoints";

export function useEquivalences(projectId: string) {
  return useQuery({
    queryKey: ["equivalences", projectId],
    queryFn: () => equivalencesApi.list(projectId),
  });
}

export function useDetectEquivalences(projectId: string) {
  return useMutation({
    mutationFn: (data: { dimensions: string[]; threshold?: number }) =>
      equivalencesApi.detect(projectId, data),
  });
}

// useCanonicalConcepts.ts
export function useCanonicalConcepts(projectId: string) {
  return useQuery({
    queryKey: ["canonical-concepts", projectId],
    queryFn: () => canonicalConceptsApi.list(projectId),
  });
}

export function useCreateCanonicalConcept(projectId: string) {
  return useMutation({
    mutationFn: (data: { name: string; item_ids: string[] }) =>
      canonicalConceptsApi.create(projectId, data),
  });
}

// useJourneys.ts
export function useJourneys(projectId: string) {
  return useQuery({
    queryKey: ["journeys", projectId],
    queryFn: () => journeysApi.list(projectId),
  });
}

export function useCreateJourney(projectId: string) {
  return useMutation({
    mutationFn: (data: CreateJourneyRequest) => journeysApi.create(projectId, data),
  });
}

// useComponentLibraries.ts
export function useComponentLibraries(projectId: string) {
  return useQuery({
    queryKey: ["component-libraries", projectId],
    queryFn: () => componentLibrariesApi.list(projectId),
  });
}
```

### Step 4: Backend Implementation

The backend API routes should follow these patterns:

#### Equivalences Router
```typescript
export const equivalencesRouter = createTRPCRouter({
  list: protectedProcedure
    .input(z.object({
      projectId: z.string().uuid(),
      status: z.enum(["suggested", "confirmed", "rejected"]).optional(),
      skip: z.number().min(0).default(0),
      limit: z.number().min(1).max(1000).default(100),
    }))
    .query(async ({ input, ctx }) => {
      // Implementation: Query database for equivalences
    }),

  detect: protectedProcedure
    .input(z.object({
      projectId: z.string().uuid(),
      dimensions: z.array(z.string()),
      threshold: z.number().min(0).max(1).default(0.8),
      exclude_ids: z.array(z.string().uuid()).optional(),
    }))
    .mutation(async ({ input, ctx }) => {
      // Implementation: AI-based equivalence detection
    }),

  confirm: protectedProcedure
    .input(z.object({
      id: z.string().uuid(),
      notes: z.string().optional(),
    }))
    .mutation(async ({ input, ctx }) => {
      // Implementation: Update equivalence status
    }),
});
```

---

## Testing Strategy

### Unit Tests (Vitest)
Test pure utility functions and validators:

```typescript
// tests/unit/equivalences.test.ts
import { describe, it, expect } from "vitest";
import { validateEquivalenceInput } from "@/utils/equivalences";

describe("Equivalence Validators", () => {
  it("should validate equivalence input", () => {
    const result = validateEquivalenceInput({
      dimensions: ["req", "design"],
      threshold: 0.8,
    });
    expect(result).toBeValid();
  });
});
```

### API Integration Tests (Playwright API)
Test actual API endpoints:

```typescript
// tests/playwright/api/equivalences.spec.ts
import { test, expect } from "@playwright/test";

test("Detect equivalences", async ({ request }) => {
  const response = await request.post("/api/v1/projects/proj-id/equivalences/detect", {
    data: {
      dimensions: ["requirements", "design"],
      threshold: 0.8,
    },
  });

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data).toHaveProperty("detected_count");
  expect(data).toHaveProperty("suggestions");
});
```

### E2E Workflow Tests (Playwright)
Test complete user workflows:

```typescript
// tests/playwright/workflows/equivalences.spec.ts
test("Complete equivalence workflow", async ({ page }) => {
  // 1. Navigate to equivalences view
  // 2. Trigger detection
  // 3. Review suggestions
  // 4. Confirm/reject equivalences
  // 5. Verify updates
});
```

---

## Documentation Portal Integration

The API docs are accessible at these URLs:

1. **Swagger UI** (Interactive testing)
   ```
   http://localhost:8000/api-docs/swagger
   ```

2. **ReDoc** (Clean reference)
   ```
   http://localhost:8000/api-docs/redoc
   ```

3. **Raw Specification**
   ```
   http://localhost:8000/specs/openapi.json
   ```

### Enabling in Production

Update `frontend/apps/web/src/routes/api-docs.index.tsx` if needed to serve specs from CDN:

```typescript
export function ApiDocsIndex() {
  const specUrl = process.env.NODE_ENV === "production"
    ? "https://cdn.tracertm.com/specs/openapi.json"
    : "/specs/openapi.json";

  return (
    // Render docs UI with specUrl
  );
}
```

---

## Code Generation

Use OpenAPI generators to auto-generate clients:

### TypeScript Client
```bash
npm install -g @openapitools/openapi-generator-cli

openapi-generator-cli generate \
  -i /frontend/apps/web/public/specs/openapi.json \
  -g typescript-fetch \
  -o ./generated-client
```

### Python Client
```bash
openapi-generator-cli generate \
  -i /frontend/apps/web/public/specs/openapi.json \
  -g python \
  -o ./python-client
```

---

## Migration Guide

### From Legacy API to New Endpoints

If migrating from older API versions:

1. **Legacy:** Direct item comparison → **New:** Equivalences API
2. **Legacy:** Manual cross-dimension mapping → **New:** Canonical Concepts
3. **Legacy:** Custom trace tracking → **New:** Journeys API
4. **Legacy:** Component metadata → **New:** Component Libraries + Tokens

---

## Performance Considerations

### Caching Strategy
```typescript
// Cache equivalences for 5 minutes
const equivalencesCacheTime = 5 * 60 * 1000;

useQuery({
  queryKey: ["equivalences", projectId],
  queryFn: () => equivalencesApi.list(projectId),
  staleTime: equivalencesCacheTime,
});
```

### Pagination
All list endpoints support pagination - use appropriate limits:

```typescript
// Good: Paginate large result sets
const { data } = useQuery({
  queryFn: () => journeysApi.list(projectId, { limit: 50 }),
});

// Avoid: Fetching all results
const { data } = useQuery({
  queryFn: () => journeysApi.list(projectId, { limit: 10000 }),
});
```

---

## Common Use Cases

### 1. Auto-Detect Equivalences
```typescript
const mutation = useDetectEquivalences(projectId);

await mutation.mutateAsync({
  dimensions: ["requirements", "design", "testing"],
  threshold: 0.85,
});
```

### 2. Create Canonical Concept
```typescript
const mutation = useCreateCanonicalConcept(projectId);

await mutation.mutateAsync({
  name: "User Authentication",
  description: "Core auth requirement",
  item_ids: ["req-1", "design-1", "test-1"],
});
```

### 3. Create User Journey
```typescript
const mutation = useCreateJourney(projectId);

await mutation.mutateAsync({
  name: "Login Flow",
  type: "user",
  steps: [
    { order: 1, name: "Enter Credentials", item_id: "step-1" },
    { order: 2, name: "Validate", item_id: "step-2" },
    { order: 3, name: "Authenticate", item_id: "step-3" },
  ],
});
```

### 4. List Design Tokens
```typescript
const { data } = useQuery({
  queryFn: () => componentLibrariesApi.getDesignTokens(libraryId, "colors"),
});

data?.tokens.forEach(token => {
  console.log(`${token.name}: ${token.value}`);
});
```

---

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Ensure JWT token is included in Authorization header
   - Verify token hasn't expired

2. **404 Not Found**
   - Check resource IDs are valid UUIDs
   - Verify project/item exists in database

3. **400 Bad Request**
   - Validate input matches schema (dimensions array, threshold 0-1)
   - Check required fields are present

4. **500 Internal Error**
   - Check server logs for detailed error
   - Ensure database is accessible
   - Verify all dependencies are running

---

## Files Modified/Created

| File | Type | Description |
|------|------|-------------|
| `/frontend/apps/web/public/specs/openapi.json` | Updated | Complete OpenAPI spec with all new endpoints |
| `/OPENAPI_SPECIFICATION.md` | Created | Comprehensive API documentation |
| `/API_IMPLEMENTATION_GUIDE.md` | Created | This implementation guide |

---

## Next Steps

1. **Review Specification**
   - Read `/OPENAPI_SPECIFICATION.md` for complete endpoint reference

2. **Implement Backend Routes**
   - Create tRPC routers following patterns in guide
   - Implement database queries/mutations
   - Add RLS policies for data security

3. **Develop Frontend**
   - Create TypeScript types
   - Implement API endpoints
   - Build React components using hooks

4. **Write Tests**
   - Unit tests for validators
   - Integration tests for API routes
   - E2E tests for workflows

5. **Document**
   - Update team documentation
   - Create implementation examples
   - Record walkthrough videos

---

## Support & Questions

For implementation questions or issues:
- Review example code in this guide
- Check `/OPENAPI_SPECIFICATION.md` for endpoint details
- Examine test files for usage patterns
- Contact support@tracertm.com for help

---

## Version

- **API Version:** 1.0.0
- **OpenAPI Version:** 3.1.0
- **Created:** 2024-01-29
- **Last Updated:** 2024-01-29
