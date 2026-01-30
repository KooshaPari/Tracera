# TraceRTM Multi-Dimensional Traceability API Specification

## Overview

This document describes the comprehensive OpenAPI 3.1.0 specification for TraceRTM's multi-dimensional traceability endpoints. The specification includes new endpoints for managing equivalences, canonical concepts, journeys, and component libraries alongside the existing items, links, and analysis APIs.

**Specification Location:** `/frontend/apps/web/public/specs/openapi.json`

**API Version:** 1.0.0

**OpenAPI Version:** 3.1.0

---

## Base Information

- **Title:** TraceRTM API
- **Description:** Traceability Requirements Tracking Management API - Comprehensive REST API for managing requirements, items, links, and performing advanced analysis including multi-dimensional traceability
- **Contact:** support@tracertm.com
- **License:** MIT

### Server Endpoints

- Local Development: `http://localhost:8000`
- Production: `https://api.tracertm.com`
- Staging: `https://staging-api.tracertm.com`

### Authentication

Two authentication methods are supported:

1. **Bearer Token (JWT)**
   - Header: `Authorization: Bearer <token>`
   - Format: JWT
   - Recommended for most use cases

2. **API Key**
   - Header: `X-API-Key: <key>`
   - Alternative for integrations and automation

---

## API Tags

### 1. Health
Health check and system status endpoints

### 2. Items
Operations for managing requirements items

### 3. Links
Operations for managing relationships between items

### 4. Analysis
Advanced analysis operations including impact analysis, cycle detection, and path finding

### 5. Equivalences
Operations for managing equivalent items across different projects and dimensions

### 6. Canonical Concepts
Operations for managing canonical concepts and their projections across dimensions

### 7. Journeys
Operations for managing user and system journeys through requirements

### 8. Component Libraries
Operations for managing component libraries and design tokens

---

## Detailed Endpoint Reference

### Health Check Endpoints

#### GET /health
- **Summary:** Health Check
- **Description:** Check the health status of the API service
- **Authentication:** Not required
- **Response:** `HealthResponse`
  - `status`: "healthy", "degraded", or "unhealthy"
  - `version`: API version string
  - `service`: Service name

---

### Items Endpoints

#### GET /api/v1/items
- **Summary:** List Items
- **Description:** Retrieve a paginated list of items in a project
- **Parameters:**
  - `project_id` (required, query): UUID of the project
  - `skip` (optional, query): Number of items to skip (default: 0)
  - `limit` (optional, query): Max items to return (1-1000, default: 100)
- **Response:** `ItemListResponse` with total count and array of items

#### GET /api/v1/items/{item_id}
- **Summary:** Get Item
- **Description:** Retrieve detailed information about a specific item
- **Parameters:**
  - `item_id` (required, path): UUID of the item
- **Response:** `ItemDetailResponse` with full item information

---

### Links Endpoints

#### GET /api/v1/links
- **Summary:** List Links
- **Description:** Retrieve a paginated list of links between items in a project
- **Parameters:**
  - `project_id` (required, query): UUID of the project
  - `skip` (optional, query): Number of items to skip (default: 0)
  - `limit` (optional, query): Max items to return (1-1000, default: 100)
- **Response:** `LinkListResponse` with total count and array of links

---

### Analysis Endpoints

#### GET /api/v1/analysis/impact/{item_id}
- **Summary:** Impact Analysis
- **Description:** Analyze the impact of changes to a specific item, including all downstream dependencies
- **Parameters:**
  - `item_id` (required, path): UUID of the item to analyze
  - `project_id` (required, query): UUID of the project
- **Response:** `ImpactAnalysisResponse` with affected items and metrics

#### GET /api/v1/analysis/cycles/{project_id}
- **Summary:** Detect Cycles
- **Description:** Detect circular dependencies in the project's dependency graph
- **Parameters:**
  - `project_id` (required, path): UUID of the project
- **Response:** `CycleDetectionResponse` with cycle information and affected items

#### GET /api/v1/analysis/shortest-path
- **Summary:** Find Shortest Path
- **Description:** Find the shortest dependency path between two items
- **Parameters:**
  - `project_id` (required, query): UUID of the project
  - `source_id` (required, query): Starting item ID
  - `target_id` (required, query): Target item ID
- **Response:** `ShortestPathResponse` with path and link types

---

## NEW ENDPOINTS: Equivalences

### GET /api/v1/projects/{projectId}/equivalences
- **Summary:** List Equivalences
- **Description:** Retrieve all equivalence relationships in a project
- **Parameters:**
  - `projectId` (required, path): UUID of the project
  - `status` (optional, query): Filter by status ("suggested", "confirmed", "rejected")
  - `skip` (optional, query): Number of items to skip (default: 0)
  - `limit` (optional, query): Max items to return (1-1000, default: 100)
- **Response:** `EquivalenceListResponse`
  - `total`: Number of equivalences
  - `equivalences`: Array of `EquivalenceResponse` objects

### POST /api/v1/projects/{projectId}/equivalences/detect
- **Summary:** Detect Equivalences
- **Description:** Automatically detect potential equivalent items across different views and dimensions
- **Parameters:**
  - `projectId` (required, path): UUID of the project
- **Request Body:** `DetectEquivalencesRequest`
  - `dimensions` (required): List of dimensions to check
  - `threshold` (optional): Similarity threshold 0-1 (default: 0.8)
  - `exclude_ids` (optional): Item IDs to exclude from detection
- **Response:** `EquivalenceDetectionResponse`
  - `detected_count`: Number of equivalences detected
  - `suggestions`: Array of suggested equivalences

### POST /api/v1/equivalences/{id}/confirm
- **Summary:** Confirm Equivalence
- **Description:** Confirm a suggested equivalence relationship between items
- **Parameters:**
  - `id` (required, path): UUID of the equivalence
- **Request Body:** `ConfirmEquivalenceRequest` (optional)
  - `notes`: Optional notes when confirming
- **Response:** `EquivalenceResponse` with status updated to "confirmed"

### POST /api/v1/equivalences/{id}/reject
- **Summary:** Reject Equivalence
- **Description:** Reject a suggested equivalence relationship between items
- **Parameters:**
  - `id` (required, path): UUID of the equivalence
- **Request Body:** `RejectEquivalenceRequest` (optional)
  - `reason`: Reason for rejecting
- **Response:** `EquivalenceResponse` with status updated to "rejected"

#### EquivalenceResponse Schema
```json
{
  "id": "uuid",
  "item_ids": ["uuid", "uuid"],
  "status": "suggested | confirmed | rejected",
  "confidence": 0.85,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "notes": "Optional notes"
}
```

---

## NEW ENDPOINTS: Canonical Concepts

### GET /api/v1/projects/{projectId}/canonical-concepts
- **Summary:** List Canonical Concepts
- **Description:** Retrieve all canonical concepts in a project
- **Parameters:**
  - `projectId` (required, path): UUID of the project
  - `skip` (optional, query): Number of items to skip (default: 0)
  - `limit` (optional, query): Max items to return (1-1000, default: 100)
- **Response:** `CanonicalConceptListResponse`
  - `total`: Number of concepts
  - `concepts`: Array of `CanonicalConceptResponse` objects

### POST /api/v1/projects/{projectId}/canonical-concepts
- **Summary:** Create Canonical Concept
- **Description:** Create a new canonical concept from equivalent items
- **Parameters:**
  - `projectId` (required, path): UUID of the project
- **Request Body:** `CreateCanonicalConceptRequest`
  - `name` (required): Name of the concept (1-255 characters)
  - `description` (optional): Detailed description
  - `item_ids` (required): Array of item UUIDs to include (minimum 1)
- **Response:** `CanonicalConceptResponse` (HTTP 201)

### GET /api/v1/canonical-concepts/{id}
- **Summary:** Get Canonical Concept
- **Description:** Retrieve detailed information about a specific canonical concept
- **Parameters:**
  - `id` (required, path): UUID of the canonical concept
- **Response:** `CanonicalConceptResponse`

### GET /api/v1/canonical-concepts/{id}/projections
- **Summary:** Get Concept Projections
- **Description:** Retrieve all projections of a canonical concept across different dimensions
- **Parameters:**
  - `id` (required, path): UUID of the canonical concept
  - `dimension` (optional, query): Filter projections by specific dimension
- **Response:** `ProjectionListResponse`
  - `total`: Number of projections
  - `projections`: Array of `ProjectionResponse` objects

### POST /api/v1/items/{id}/pivot
- **Summary:** Pivot Item to Canonical Concept
- **Description:** Convert an item to a canonical concept projection, updating cross-dimensional references
- **Parameters:**
  - `id` (required, path): UUID of the item to pivot
- **Request Body:** `PivotItemRequest`
  - `canonical_concept_id` (required): UUID of the canonical concept to pivot to
  - `update_references` (optional): Whether to update all references (default: true)
- **Response:** `PivotItemResponse`
  - `item_id`: UUID of the item
  - `canonical_concept_id`: UUID of the canonical concept
  - `updated_references`: Count of references updated

#### CanonicalConceptResponse Schema
```json
{
  "id": "uuid",
  "name": "Concept Name",
  "description": "Detailed description",
  "item_ids": ["uuid1", "uuid2"],
  "dimensions": ["dimension1", "dimension2"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### ProjectionResponse Schema
```json
{
  "id": "uuid",
  "item_id": "uuid",
  "dimension": "dimension_name",
  "canonical_id": "uuid",
  "mapping_confidence": 0.95
}
```

---

## NEW ENDPOINTS: Journeys

### GET /api/v1/projects/{projectId}/journeys
- **Summary:** List Journeys
- **Description:** Retrieve all journeys in a project
- **Parameters:**
  - `projectId` (required, path): UUID of the project
  - `type` (optional, query): Filter by journey type ("user", "system", "data", "integration")
  - `skip` (optional, query): Number of items to skip (default: 0)
  - `limit` (optional, query): Max items to return (1-1000, default: 100)
- **Response:** `JourneyListResponse`
  - `total`: Number of journeys
  - `journeys`: Array of `JourneyResponse` objects

### POST /api/v1/projects/{projectId}/journeys
- **Summary:** Create Journey
- **Description:** Create a new journey mapping requirements through a process
- **Parameters:**
  - `projectId` (required, path): UUID of the project
- **Request Body:** `CreateJourneyRequest`
  - `name` (required): Name of the journey (1-255 characters)
  - `description` (optional): Journey description
  - `type` (required): Journey type ("user", "system", "data", "integration")
  - `steps` (required): Array of journey steps (minimum 1)
    - `order` (required): Position in sequence
    - `name` (required): Step name
    - `item_id` (required): Associated item UUID
    - `description` (optional): Step description
- **Response:** `JourneyResponse` (HTTP 201)

### POST /api/v1/projects/{projectId}/journeys/detect
- **Summary:** Detect Journeys
- **Description:** Automatically detect potential journeys from requirement traces
- **Parameters:**
  - `projectId` (required, path): UUID of the project
- **Request Body:** `DetectJourneysRequest`
  - `journey_type` (required): Type of journey to detect
  - `min_path_length` (optional): Minimum steps for valid journey (default: 3)
  - `max_results` (optional): Maximum results to return (1-1000, default: 100)
- **Response:** `JourneyDetectionResponse`
  - `detected_count`: Number of journeys detected
  - `journeys`: Array of `JourneyResponse` objects

### GET /api/v1/journeys/{id}
- **Summary:** Get Journey
- **Description:** Retrieve detailed information about a specific journey
- **Parameters:**
  - `id` (required, path): UUID of the journey
- **Response:** `JourneyResponse`

#### JourneyResponse Schema
```json
{
  "id": "uuid",
  "name": "Journey Name",
  "description": "Journey description",
  "type": "user|system|data|integration",
  "steps": [
    {
      "id": "uuid",
      "order": 1,
      "name": "Step Name",
      "item_id": "uuid",
      "description": "Step description",
      "metadata": {}
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## NEW ENDPOINTS: Component Libraries

### GET /api/v1/projects/{projectId}/component-libraries
- **Summary:** List Component Libraries
- **Description:** Retrieve all component libraries in a project
- **Parameters:**
  - `projectId` (required, path): UUID of the project
  - `skip` (optional, query): Number of items to skip (default: 0)
  - `limit` (optional, query): Max items to return (1-1000, default: 100)
- **Response:** `ComponentLibraryListResponse`
  - `total`: Number of libraries
  - `libraries`: Array of `ComponentLibraryResponse` objects

### GET /api/v1/component-libraries/{id}/components
- **Summary:** List Components in Library
- **Description:** Retrieve all components in a specific library
- **Parameters:**
  - `id` (required, path): UUID of the component library
  - `category` (optional, query): Filter by component category
  - `skip` (optional, query): Number of items to skip (default: 0)
  - `limit` (optional, query): Max items to return (1-1000, default: 100)
- **Response:** `ComponentListResponse`
  - `total`: Number of components
  - `components`: Array of `ComponentResponse` objects

### GET /api/v1/components/{id}/usage
- **Summary:** Get Component Usage
- **Description:** Retrieve usage information for a specific component
- **Parameters:**
  - `id` (required, path): UUID of the component
- **Response:** `ComponentUsageResponse`
  - `component_id`: UUID of the component
  - `usage_count`: Total number of usages
  - `used_in_items`: Array of item UUIDs using this component
  - `last_used`: Timestamp of last usage (nullable)

### GET /api/v1/component-libraries/{id}/tokens
- **Summary:** Get Design Tokens
- **Description:** Retrieve design tokens for a component library
- **Parameters:**
  - `id` (required, path): UUID of the component library
  - `category` (optional, query): Filter tokens by category (colors, typography, spacing, shadows, borders, other)
- **Response:** `DesignTokenResponse`
  - `library_id`: UUID of the library
  - `tokens`: Array of `DesignToken` objects
  - `total`: Total number of tokens

#### ComponentLibraryResponse Schema
```json
{
  "id": "uuid",
  "name": "Library Name",
  "description": "Library description",
  "version": "1.0.0",
  "component_count": 42,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DesignToken Schema
```json
{
  "id": "uuid",
  "name": "Primary Color",
  "value": "#007AFF",
  "category": "colors|typography|spacing|shadows|borders|other",
  "description": "Token description"
}
```

---

## Common Response Schemas

### ItemSummary
```json
{
  "id": "uuid",
  "title": "Item Title",
  "view": "view_type",
  "status": "draft|in_progress|completed|approved|rejected"
}
```

### ItemDetailResponse
```json
{
  "id": "uuid",
  "title": "Item Title",
  "description": "Item description",
  "view": "view_type",
  "status": "draft|in_progress|completed|approved|rejected",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong",
  "code": "ERROR_CODE"
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Request completed successfully |
| 201 | Created - Resource successfully created |
| 400 | Bad Request - Invalid input parameters |
| 401 | Unauthorized - Missing or invalid authentication |
| 404 | Not Found - Resource does not exist |
| 500 | Internal Server Error - Unexpected error |

---

## Error Codes

| Code | Description |
|------|-------------|
| INVALID_INPUT | Input validation failed |
| UNAUTHORIZED | Authentication required or invalid |
| NOT_FOUND | Resource does not exist |
| INTERNAL_ERROR | Unexpected server error |

---

## API Usage Examples

### Detecting Equivalences

```bash
curl -X POST https://api.tracertm.com/api/v1/projects/{projectId}/equivalences/detect \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["requirements", "design", "testing"],
    "threshold": 0.8,
    "exclude_ids": ["excluded-uuid"]
  }'
```

**Response:**
```json
{
  "detected_count": 3,
  "suggestions": [
    {
      "id": "equiv-uuid-1",
      "item_ids": ["item-1", "item-2"],
      "status": "suggested",
      "confidence": 0.92,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Creating a Canonical Concept

```bash
curl -X POST https://api.tracertm.com/api/v1/projects/{projectId}/canonical-concepts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "User Authentication",
    "description": "Core authentication requirement across all dimensions",
    "item_ids": ["req-auth-1", "design-auth-1", "test-auth-1"]
  }'
```

**Response:**
```json
{
  "id": "concept-uuid",
  "name": "User Authentication",
  "description": "Core authentication requirement across all dimensions",
  "item_ids": ["req-auth-1", "design-auth-1", "test-auth-1"],
  "dimensions": ["requirements", "design", "testing"],
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Creating a Journey

```bash
curl -X POST https://api.tracertm.com/api/v1/projects/{projectId}/journeys \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "User Login Flow",
    "type": "user",
    "description": "Complete user login process",
    "steps": [
      {
        "order": 1,
        "name": "Enter Credentials",
        "item_id": "step-1-uuid"
      },
      {
        "order": 2,
        "name": "Validate Input",
        "item_id": "step-2-uuid"
      },
      {
        "order": 3,
        "name": "Authenticate User",
        "item_id": "step-3-uuid"
      }
    ]
  }'
```

**Response:**
```json
{
  "id": "journey-uuid",
  "name": "User Login Flow",
  "type": "user",
  "description": "Complete user login process",
  "steps": [
    {
      "id": "step-1",
      "order": 1,
      "name": "Enter Credentials",
      "item_id": "step-1-uuid"
    },
    {
      "id": "step-2",
      "order": 2,
      "name": "Validate Input",
      "item_id": "step-2-uuid"
    },
    {
      "id": "step-3",
      "order": 3,
      "name": "Authenticate User",
      "item_id": "step-3-uuid"
    }
  ],
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

---

## Rate Limiting & Pagination

### Pagination
All list endpoints support pagination:
- `skip`: Number of items to skip (default: 0)
- `limit`: Max items per page (1-1000, default: 100)

### Response Format
```json
{
  "total": 500,
  "items": [...]
}
```

---

## Implementation Notes

1. **UUID Format:** All IDs use UUID v4 format
2. **Timestamps:** All timestamps are ISO 8601 formatted with timezone
3. **Confidence Scores:** Values between 0.0 and 1.0 (0% to 100%)
4. **Pagination:** Cursor-based offset pagination using skip/limit
5. **Authentication:** Bearer tokens must include "Bearer " prefix in Authorization header

---

## File Location

The complete OpenAPI specification is stored at:

```
/frontend/apps/web/public/specs/openapi.json
```

This file is:
- Served at `http://localhost:8000/specs/openapi.json` (development)
- Downloadable from API docs portal at `/api-docs`
- Compatible with Swagger UI and ReDoc
- Available for code generation tools (OpenAPI generators)

---

## Documentation Access

The API documentation is accessible through multiple interfaces:

1. **Swagger UI:** `/api-docs/swagger`
2. **ReDoc:** `/api-docs/redoc`
3. **Raw Spec:** `/specs/openapi.json`

---

## Related Documentation

- API Client Implementation: `/frontend/apps/web/src/api/endpoints.ts`
- API Types: `/frontend/apps/web/src/api/types.ts`
- Example Tests: `/frontend/apps/web/src/__tests__/api/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial release with multi-dimensional endpoints |

---

## Support

For API support and issues:
- Email: support@tracertm.com
- Documentation: https://docs.tracertm.com
- GitHub: https://github.com/tracertm/tracertm
