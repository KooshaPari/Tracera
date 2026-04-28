# TraceRTM API Reference

Complete REST API documentation for TraceRTM backend server.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Health](#health)
  - [Projects](#projects)
  - [Items](#items)
  - [Links](#links)
  - [Agents](#agents)
  - [Events](#events)
- [Examples](#examples)

## Overview

The TraceRTM API is a RESTful API built with Go and Echo framework. It provides comprehensive endpoints for managing projects, items, links, and agents in a multi-view requirements traceability system.

**Technology Stack:**
- Go 1.23+
- Echo web framework
- PostgreSQL 14+ with pgx driver
- sqlc for type-safe database queries
- JWT authentication (optional)

## Authentication

Currently, the API is open for development. JWT authentication will be added in Phase 2.

**Future Authentication Header:**
```
Authorization: Bearer <your-jwt-token>
```

## Base URL

**Development:**
```
http://localhost:8080/api/v1
```

**Production:**
```
https://api.tracertm.com/api/v1
```

## Response Format

All API responses follow this structure:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Error Handling

| HTTP Status | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Resource deleted successfully |
| 400 | Bad Request - Invalid request parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

## Rate Limiting

**Current:** No rate limiting (development)
**Future:** 100 requests per minute per IP

## Endpoints

### Health

#### Check API Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-11-29T12:00:00Z"
}
```

---

### Projects

Projects are the top-level organizational units in TraceRTM.

#### Create Project
```http
POST /api/v1/projects
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description",
  "metadata": {
    "team": "Engineering",
    "priority": "high"
  }
}
```

**Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My Project",
  "description": "Project description",
  "metadata": {
    "team": "Engineering",
    "priority": "high"
  },
  "created_at": "2025-11-29T12:00:00Z",
  "updated_at": "2025-11-29T12:00:00Z",
  "deleted_at": null
}
```

#### List Projects
```http
GET /api/v1/projects?limit=10&offset=0
```

**Query Parameters:**
- `limit` (integer, default: 10): Number of results per page
- `offset` (integer, default: 0): Pagination offset

**Response (200):**
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "My Project",
      "description": "Project description",
      "metadata": {},
      "created_at": "2025-11-29T12:00:00Z",
      "updated_at": "2025-11-29T12:00:00Z",
      "deleted_at": null
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### Get Project
```http
GET /api/v1/projects/:id
```

**Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My Project",
  "description": "Project description",
  "metadata": {},
  "created_at": "2025-11-29T12:00:00Z",
  "updated_at": "2025-11-29T12:00:00Z",
  "deleted_at": null
}
```

#### Update Project
```http
PUT /api/v1/projects/:id
Content-Type: application/json

{
  "name": "Updated Project Name",
  "description": "Updated description",
  "metadata": {
    "team": "Platform"
  }
}
```

**Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Updated Project Name",
  "description": "Updated description",
  "metadata": {
    "team": "Platform"
  },
  "created_at": "2025-11-29T12:00:00Z",
  "updated_at": "2025-11-29T12:05:00Z",
  "deleted_at": null
}
```

#### Delete Project
```http
DELETE /api/v1/projects/:id
```

**Response (204):**
No content. Project is soft-deleted (deleted_at timestamp set).

---

### Items

Items represent features, code, tests, APIs, and other trackable entities.

#### Create Item
```http
POST /api/v1/items
Content-Type: application/json

{
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "User Authentication Feature",
  "description": "Implement JWT-based authentication",
  "type": "feature",
  "status": "todo",
  "priority": 75,
  "metadata": {
    "assignee": "john.doe",
    "sprint": "Sprint 1"
  }
}
```

**Item Types:**
- `feature` - Feature requirement
- `code` - Code implementation
- `test` - Test case
- `api` - API endpoint
- `database` - Database schema
- `wireframe` - UI wireframe
- `architecture` - Architecture component
- `infrastructure` - Infrastructure resource
- `dataflow` - Data flow diagram
- `security` - Security requirement
- `performance` - Performance requirement
- `monitoring` - Monitoring configuration
- `domain` - Domain model
- `journey` - User journey
- `config` - Configuration item
- `dependency` - External dependency

**Item Status:**
- `todo` - Not started
- `in_progress` - Work in progress
- `done` - Completed
- `blocked` - Blocked

**Priority:** 0-100 (higher is more important)

**Response (201):**
```json
{
  "id": "223e4567-e89b-12d3-a456-426614174001",
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "User Authentication Feature",
  "description": "Implement JWT-based authentication",
  "type": "feature",
  "status": "todo",
  "priority": 75,
  "metadata": {
    "assignee": "john.doe",
    "sprint": "Sprint 1"
  },
  "created_at": "2025-11-29T12:00:00Z",
  "updated_at": "2025-11-29T12:00:00Z",
  "deleted_at": null
}
```

#### List Items by Project
```http
GET /api/v1/items?project_id=123e4567-e89b-12d3-a456-426614174000&limit=10&offset=0
```

**Query Parameters:**
- `project_id` (uuid, required): Project ID
- `limit` (integer, default: 10): Number of results per page
- `offset` (integer, default: 0): Pagination offset

**Response (200):**
```json
{
  "data": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "project_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "User Authentication Feature",
      "description": "Implement JWT-based authentication",
      "type": "feature",
      "status": "todo",
      "priority": 75,
      "metadata": {},
      "created_at": "2025-11-29T12:00:00Z",
      "updated_at": "2025-11-29T12:00:00Z",
      "deleted_at": null
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### List Items by Type
```http
GET /api/v1/items?project_id=123e4567-e89b-12d3-a456-426614174000&type=feature
```

**Query Parameters:**
- `project_id` (uuid, required): Project ID
- `type` (string, required): Item type
- `limit` (integer, default: 10): Number of results per page
- `offset` (integer, default: 0): Pagination offset

#### Get Item
```http
GET /api/v1/items/:id
```

**Response (200):**
```json
{
  "id": "223e4567-e89b-12d3-a456-426614174001",
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "User Authentication Feature",
  "description": "Implement JWT-based authentication",
  "type": "feature",
  "status": "todo",
  "priority": 75,
  "metadata": {},
  "created_at": "2025-11-29T12:00:00Z",
  "updated_at": "2025-11-29T12:00:00Z",
  "deleted_at": null
}
```

#### Update Item
```http
PUT /api/v1/items/:id
Content-Type: application/json

{
  "title": "User Authentication Feature (Updated)",
  "description": "Implement JWT-based authentication with refresh tokens",
  "type": "feature",
  "status": "in_progress",
  "priority": 90,
  "metadata": {
    "assignee": "jane.doe",
    "sprint": "Sprint 1"
  }
}
```

#### Delete Item
```http
DELETE /api/v1/items/:id
```

**Response (204):**
No content. Item is soft-deleted.

---

### Links

Links define relationships between items (60+ link types across 12 categories).

#### Create Link
```http
POST /api/v1/links
Content-Type: application/json

{
  "source_id": "223e4567-e89b-12d3-a456-426614174001",
  "target_id": "323e4567-e89b-12d3-a456-426614174002",
  "type": "depends_on",
  "metadata": {
    "strength": "strong",
    "bidirectional": false
  }
}
```

**Link Types by Category:**

**1. Hierarchical Links:**
- `parent_of` / `child_of`
- `contains` / `contained_by`
- `composed_of` / `part_of`

**2. Dependency Links:**
- `depends_on` / `required_by`
- `blocks` / `blocked_by`
- `enables` / `enabled_by`

**3. Implementation Links:**
- `implements` / `implemented_by`
- `realizes` / `realized_by`
- `satisfies` / `satisfied_by`

**4. Testing Links:**
- `tests` / `tested_by`
- `verifies` / `verified_by`
- `validates` / `validated_by`

**5. Temporal Links:**
- `precedes` / `follows`
- `triggers` / `triggered_by`
- `supersedes` / `superseded_by`

**6. Conflict Links:**
- `conflicts_with`
- `contradicts`
- `mutually_exclusive_with`

**7. Communication Links:**
- `relates_to`
- `references` / `referenced_by`
- `derived_from` / `derives`

**8. Data Links:**
- `produces` / `consumes`
- `transforms` / `transformed_by`
- `aggregates` / `aggregated_by`

**9. Deployment Links:**
- `deploys_to` / `hosts`
- `runs_on` / `executes`
- `scales_with`

**10. Security Links:**
- `authenticates` / `authenticated_by`
- `authorizes` / `authorized_by`
- `encrypts` / `encrypted_by`

**11. Performance Links:**
- `optimizes` / `optimized_by`
- `caches` / `cached_by`
- `indexes` / `indexed_by`

**12. Monitoring Links:**
- `monitors` / `monitored_by`
- `alerts_on` / `alerted_by`
- `logs` / `logged_by`

**Response (201):**
```json
{
  "id": "423e4567-e89b-12d3-a456-426614174003",
  "source_id": "223e4567-e89b-12d3-a456-426614174001",
  "target_id": "323e4567-e89b-12d3-a456-426614174002",
  "type": "depends_on",
  "metadata": {
    "strength": "strong",
    "bidirectional": false
  },
  "created_at": "2025-11-29T12:00:00Z",
  "updated_at": "2025-11-29T12:00:00Z",
  "deleted_at": null
}
```

#### List Links by Source
```http
GET /api/v1/links?source_id=223e4567-e89b-12d3-a456-426614174001
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "423e4567-e89b-12d3-a456-426614174003",
      "source_id": "223e4567-e89b-12d3-a456-426614174001",
      "target_id": "323e4567-e89b-12d3-a456-426614174002",
      "type": "depends_on",
      "metadata": {},
      "created_at": "2025-11-29T12:00:00Z",
      "updated_at": "2025-11-29T12:00:00Z",
      "deleted_at": null
    }
  ]
}
```

#### List Links by Target
```http
GET /api/v1/links?target_id=323e4567-e89b-12d3-a456-426614174002
```

#### Get Link
```http
GET /api/v1/links/:id
```

#### Delete Link
```http
DELETE /api/v1/links/:id
```

**Response (204):**
No content. Link is soft-deleted.

---

### Agents

Agents represent autonomous actors that can interact with the system (1-1000 concurrent agents supported).

#### Create Agent
```http
POST /api/v1/agents
Content-Type: application/json

{
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Developer Agent 01",
  "status": "active",
  "metadata": {
    "type": "developer",
    "capabilities": ["code", "test", "review"]
  }
}
```

**Agent Status:**
- `active` - Currently working
- `idle` - Waiting for work
- `error` - Error state

**Response (201):**
```json
{
  "id": "523e4567-e89b-12d3-a456-426614174004",
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Developer Agent 01",
  "status": "active",
  "metadata": {
    "type": "developer",
    "capabilities": ["code", "test", "review"]
  },
  "last_activity_at": null,
  "created_at": "2025-11-29T12:00:00Z",
  "updated_at": "2025-11-29T12:00:00Z",
  "deleted_at": null
}
```

#### List Agents by Project
```http
GET /api/v1/agents?project_id=123e4567-e89b-12d3-a456-426614174000
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "523e4567-e89b-12d3-a456-426614174004",
      "project_id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Developer Agent 01",
      "status": "active",
      "metadata": {},
      "last_activity_at": "2025-11-29T12:05:00Z",
      "created_at": "2025-11-29T12:00:00Z",
      "updated_at": "2025-11-29T12:00:00Z",
      "deleted_at": null
    }
  ]
}
```

#### Get Agent
```http
GET /api/v1/agents/:id
```

#### Update Agent
```http
PUT /api/v1/agents/:id
Content-Type: application/json

{
  "name": "Senior Developer Agent 01",
  "status": "idle",
  "metadata": {
    "type": "senior-developer",
    "capabilities": ["code", "test", "review", "architecture"]
  }
}
```

#### Delete Agent
```http
DELETE /api/v1/agents/:id
```

**Response (204):**
No content. Agent is soft-deleted.

---

### Events

Events provide audit trail and event sourcing capabilities (Phase 2).

#### List Events by Project
```http
GET /api/v1/events?project_id=123e4567-e89b-12d3-a456-426614174000&limit=50
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "623e4567-e89b-12d3-a456-426614174005",
      "project_id": "123e4567-e89b-12d3-a456-426614174000",
      "entity_type": "item",
      "entity_id": "223e4567-e89b-12d3-a456-426614174001",
      "event_type": "created",
      "data": {
        "title": "User Authentication Feature",
        "type": "feature"
      },
      "created_at": "2025-11-29T12:00:00Z"
    }
  ]
}
```

---

## Examples

### Create a Complete Feature with Tests

**Step 1: Create Project**
```bash
curl -X POST http://localhost:8080/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "E-commerce Platform",
    "description": "Online shopping platform"
  }'
```

**Step 2: Create Feature Item**
```bash
curl -X POST http://localhost:8080/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Shopping Cart",
    "description": "Allow users to add items to cart",
    "type": "feature",
    "status": "todo",
    "priority": 90
  }'
```

**Step 3: Create Test Item**
```bash
curl -X POST http://localhost:8080/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Test: Shopping Cart Add Item",
    "description": "Verify items can be added to cart",
    "type": "test",
    "status": "todo",
    "priority": 90
  }'
```

**Step 4: Link Test to Feature**
```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "323e4567-e89b-12d3-a456-426614174002",
    "target_id": "223e4567-e89b-12d3-a456-426614174001",
    "type": "tests"
  }'
```

### Query All Tests for a Feature

```bash
curl -X GET "http://localhost:8080/api/v1/links?source_id=223e4567-e89b-12d3-a456-426614174001&type=tested_by"
```

### Create Multi-Agent Workflow

```bash
# Create Developer Agent
curl -X POST http://localhost:8080/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Dev Agent",
    "status": "active",
    "metadata": {"role": "developer"}
  }'

# Create Tester Agent
curl -X POST http://localhost:8080/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Test Agent",
    "status": "active",
    "metadata": {"role": "tester"}
  }'
```

## Advanced Features

### Graph Traversal (Future)

Recursive CTEs for finding all descendants:

```http
GET /api/v1/items/:id/descendants?depth=5
```

### Bulk Operations (Future)

```http
POST /api/v1/items/bulk
Content-Type: application/json

{
  "items": [
    {"title": "Item 1", "type": "feature", ...},
    {"title": "Item 2", "type": "test", ...}
  ]
}
```

### Search (Future)

```http
GET /api/v1/search?q=authentication&type=feature&project_id=...
```

## SDK Support (Future)

### Python
```python
from tracertm import Client

client = Client("http://localhost:8080")
project = client.projects.create(name="My Project")
item = client.items.create(
    project_id=project.id,
    title="Feature",
    type="feature"
)
```

### Go
```go
import "github.com/tracertm/sdk-go"

client := tracertm.NewClient("http://localhost:8080")
project, _ := client.Projects.Create(ctx, "My Project")
item, _ := client.Items.Create(ctx, tracertm.CreateItemParams{
    ProjectID: project.ID,
    Title:     "Feature",
    Type:      "feature",
})
```

### JavaScript/TypeScript
```typescript
import { TraceRTM } from '@tracertm/sdk';

const client = new TraceRTM('http://localhost:8080');
const project = await client.projects.create({ name: 'My Project' });
const item = await client.items.create({
  projectId: project.id,
  title: 'Feature',
  type: 'feature'
});
```

## Support

- Documentation: https://docs.tracertm.com
- GitHub: https://github.com/tracertm/tracertm
- Issues: https://github.com/tracertm/tracertm/issues

## License

MIT License - see LICENSE file for details.
