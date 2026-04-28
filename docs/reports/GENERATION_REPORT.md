# OpenAPI Type Generation Report

## Generation Summary

Generated at: $(date)
Tool: openapi-typescript 6.7.3
Source: public/specs/openapi.json
Output: src/api/schema.ts

## Generated Schema Statistics

- Total Lines: 1227
- Number of Endpoint Operations: 24+
- OpenAPI Version: 3.1.0

## Endpoints Coverage

The generated schema includes types for all endpoints in the following categories:

### Health & System

- GET /health - Health check endpoint

### Items Management

- GET /api/v1/items - List items
- GET /api/v1/items/{item_id} - Get item details

### Links Management

- GET /api/v1/links - List links

### Analysis Operations

- GET /api/v1/analysis/impact/{item_id} - Impact analysis
- GET /api/v1/analysis/cycles/{project_id} - Cycle detection
- GET /api/v1/analysis/shortest-path - Path finding

### Equivalences

- GET /api/v1/projects/{projectId}/equivalences - List equivalences
- POST /api/v1/projects/{projectId}/equivalences/detect - Detect equivalences
- POST /api/v1/equivalences/{id}/confirm - Confirm equivalence
- POST /api/v1/equivalences/{id}/reject - Reject equivalence

### Canonical Concepts

- GET /api/v1/projects/{projectId}/canonical-concepts - List concepts
- POST /api/v1/projects/{projectId}/canonical-concepts - Create concept
- GET /api/v1/canonical-concepts/{id} - Get concept details
- GET /api/v1/canonical-concepts/{id}/projections - Get projections
- POST /api/v1/items/{id}/pivot - Pivot to canonical

### Journeys

- GET /api/v1/projects/{projectId}/journeys - List journeys
- POST /api/v1/projects/{projectId}/journeys - Create journey
- POST /api/v1/projects/{projectId}/journeys/detect - Detect journeys
- GET /api/v1/journeys/{id} - Get journey details

### Component Libraries

- GET /api/v1/projects/{projectId}/component-libraries - List libraries
- Additional component-related endpoints

## Type Utilities Generated

File: src/api/types.ts
Utilities:

- ApiPaths - All path keys
- PathOperations<P> - Operations for path
- ApiRequestBody<P, M> - Request body type
- ApiResponse<P, M, Status> - Response type
- ApiQueryParams<P, M> - Query parameters
- ApiPathParams<P, M> - Path parameters
- ApiAllParams<P, M> - Combined parameters

## Build Integration

Scripts Updated in package.json:

- predev: Runs generate:types before dev
- prebuild: Runs generate:types before build
- generate:types: Main generation script

Linting Exclusion:

- src/api/schema.ts excluded from linting
- Prevents issues with auto-generated code

## Validation Results

✓ Schema generated successfully
✓ All 24+ endpoints included
✓ Type utilities created
✓ Build scripts configured
✓ Linting configured for generated file
✓ Type extraction utilities tested

## Next Steps

1. Import types from src/api/schema.ts and src/api/types.ts
2. Use type extractors in API handlers
3. Enjoy full type safety with IDE autocomplete
4. Run bun run generate:types when OpenAPI spec updates

## Documentation

See TYPE_GENERATION.md for:

- Complete usage guide
- Type utility reference
- Best practices
- Real-world examples
- Troubleshooting guide
