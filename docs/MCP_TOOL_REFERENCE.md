# TraceRTM MCP Tool Reference

**Version**: 1.0
**Last Updated**: 2026-01-29
**Status**: Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication Modes](#authentication-modes)
3. [Tool Categories](#tool-categories)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)
6. [Complete Tool Catalog](#complete-tool-catalog)
7. [Usage Examples](#usage-examples)
8. [Rate Limiting](#rate-limiting)

---

## Overview

The TraceRTM MCP server provides **50+ tools** organized into **8 functional categories**. All tools follow a unified response envelope pattern and support multiple authentication modes.

### Server Information

- **Name**: `tracertm-mcp`
- **Repository**: `src/tracertm/mcp/`
- **Entry Point**: `src/tracertm/mcp/server.py`
- **Supported Protocols**: MCP 1.0+ (stdio, SSE, WebSocket)
- **Authentication**: WorkOS AuthKit (JWT), Static Dev Keys, Frontend Pass-through

### Quick Stats

| Metric | Value |
|--------|-------|
| Total Tools | 50+ |
| Tool Categories | 8 |
| Parameterized Tools | 7 core tools + aliases |
| Supported Auth Modes | 4 |
| Max Response Time | 30s (configurable) |

---

## Authentication Modes

### Mode 1: WorkOS AuthKit (OAuth + JWT)

**Use Case**: Production, Browser-based agents, External clients

**Setup**:
```bash
export TRACERTM_MCP_AUTH_MODE=oauth
export TRACERTM_MCP_AUTHKIT_DOMAIN=https://your-authkit-domain.workos.com
export TRACERTM_MCP_BASE_URL=https://your-mcp-server.example.com
export TRACERTM_MCP_REQUIRED_SCOPES="read:projects,write:items,analyze:trace"
```

**Token Format**: JWT (RS256, signed by WorkOS)

**Request**:
```bash
curl -H "Authorization: Bearer <JWT>" \
  http://localhost:8000/mcp/list_projects
```

**JWT Claims**:
- `sub`: User ID
- `aud`: Server URI (must match `TRACERTM_MCP_BASE_URL`)
- `scope`: Space-separated scopes (e.g., `read:projects write:items`)
- `exp`: Expiration timestamp

### Mode 2: Static Dev API Keys

**Use Case**: Development, Testing, Local workflows

**Setup**:
```bash
export TRACERTM_MCP_AUTH_MODE=static
export TRACERTM_MCP_DEV_API_KEYS="key1,key2,key3"
export TRACERTM_MCP_DEV_SCOPES="read:*,write:*,analyze:*"
```

**Token Format**: Static string (no expiration)

**Request**:
```bash
curl -H "Authorization: Bearer dev-key-1" \
  http://localhost:8000/mcp/list_projects
```

**Valid Keys**:
```
- key1 → client_id: dev-key-1
- key2 → client_id: dev-key-2
- key3 → client_id: dev-key-3
```

### Mode 3: Frontend Pass-through

**Use Case**: Claude Desktop, In-app agents, Frontend redirects

**Setup**: None required (automatic detection)

**Token Format**: WorkOS AuthKit JWT (passed from frontend)

**Request**:
```bash
# Claude Desktop automatically passes Bearer token from session
# No explicit configuration needed
```

**Flow**:
1. User logs in via Claude Desktop
2. Claude Desktop obtains JWT from WorkOS
3. Claude Desktop includes `Authorization: Bearer <JWT>` in MCP requests
4. TraceRTM MCP server validates token

### Mode 4: Disabled (Development Only)

**Use Case**: Local testing without auth

**Setup**:
```bash
export TRACERTM_MCP_AUTH_MODE=disabled
```

**Security**: Tools return 401 Unauthorized if auth fails. Only use in isolated environments.

### Authentication Priority

When multiple auth methods are configured:

```
1. Static Dev Keys (if TRACERTM_MCP_DEV_API_KEYS set)
2. WorkOS AuthKit (if TRACERTM_MCP_AUTHKIT_DOMAIN set)
3. Disabled (if TRACERTM_MCP_AUTH_MODE=disabled)
4. No auth (default: requires valid token)
```

### Common Auth Errors

| Error | HTTP Code | Cause | Resolution |
|-------|-----------|-------|-----------|
| Missing Authorization | 401 | No token provided | Add `Authorization: Bearer <token>` header |
| Invalid Token | 401 | Token expired or invalid signature | Refresh token or re-authenticate |
| Insufficient Scope | 403 | Token lacks required scope | Request scope from auth provider |
| Invalid Audience | 401 | Token `aud` doesn't match server | Check `TRACERTM_MCP_BASE_URL` |

---

## Tool Categories

### 1. Project Management (`project_manage`)

**Tools**: Create, list, select, snapshot, export/import projects

**Permissions**: `read:projects`, `write:projects`

**Key Operations**:
- Create new project
- List all projects
- Select active project
- Export/import projects
- Create snapshots

### 2. Item Management (`item_manage`)

**Tools**: CRUD operations on items (requirements, features, tests, etc.)

**Permissions**: `read:items`, `write:items`, `bulk:items`

**Key Operations**:
- Create item
- Get item by ID
- Update item
- Delete item
- Bulk operations
- Query items

### 3. Link Management (`link_manage`)

**Tools**: Create, query, delete traceability links

**Permissions**: `read:links`, `write:links`

**Key Operations**:
- Create link between items
- List links
- Find orphaned links
- Find missing links
- Delete links

### 4. Traceability Analysis (`trace_analyze`)

**Tools**: Gap analysis, impact analysis, traceability matrix

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Key Operations**:
- Gap analysis (find uncovered requirements)
- Impact analysis (affected by change)
- Reverse impact analysis
- Traceability matrix
- Health assessment

### 5. Graph Analysis (`graph_analyze`)

**Tools**: Cycle detection, shortest path, dependency analysis

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Key Operations**:
- Detect cycles
- Find shortest path
- Analyze dependencies
- Dependency weight calculation

### 6. Specification Management (`spec_manage`)

**Tools**: ADRs, contracts, features, scenarios

**Permissions**: `read:specs`, `write:specs`

**Key Operations**:
- Create specification
- List specifications
- Update specification
- Generate from templates
- Export specifications

### 7. Quality Analysis (`quality_analyze`)

**Tools**: Requirement quality, coverage metrics, compliance checks

**Permissions**: `read:items`, `read:specs`, `analyze:quality`

**Key Operations**:
- Analyze requirement quality
- Calculate coverage metrics
- Check compliance rules
- Generate quality reports

### 8. Configuration Management (`config_manage`)

**Tools**: Project configuration, settings, metadata

**Permissions**: `read:config`, `write:config`

**Key Operations**:
- Get configuration
- Update configuration
- Set metadata
- Manage custom fields

---

## Response Format

All MCP tools return a unified response envelope:

### Success Response

```json
{
  "ok": true,
  "data": {
    "id": "project-123",
    "name": "My Project",
    "created_at": "2026-01-29T10:30:00Z"
  },
  "meta": {
    "count": 1,
    "page": 1,
    "total_time_ms": 145,
    "timestamp": "2026-01-29T10:30:45Z"
  }
}
```

### Error Response

```json
{
  "ok": false,
  "error": {
    "message": "Project not found",
    "code": "NOT_FOUND",
    "details": {
      "project_id": "project-123"
    }
  },
  "meta": {
    "timestamp": "2026-01-29T10:30:45Z",
    "total_time_ms": 12
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Operation success status |
| `data` | object \| array | Operation result (null on error) |
| `error` | object | Error details (null on success) |
| `meta` | object | Metadata (count, timing, timestamp) |

### Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `OK` | 200 | Success |
| `BAD_REQUEST` | 400 | Invalid parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMIT` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Error Handling

### Common Error Scenarios

**1. Invalid Project ID**
```json
{
  "ok": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Project not found: project-xyz"
  }
}
```

**2. Missing Required Parameter**
```json
{
  "ok": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Missing required parameter: name",
    "details": {
      "parameter": "name",
      "expected_type": "string"
    }
  }
}
```

**3. Insufficient Permissions**
```json
{
  "ok": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions",
    "details": {
      "required_scope": "write:items",
      "available_scopes": "read:items"
    }
  }
}
```

### Retry Logic

Implement exponential backoff for these error codes:

- **429 (Rate Limit)**: Retry after `Retry-After` header (default: 60s)
- **503 (Service Unavailable)**: Retry with exponential backoff
- **504 (Gateway Timeout)**: Retry with exponential backoff

Do NOT retry for: 400, 401, 403, 404, 409

---

## Complete Tool Catalog

### Project Management Tools

#### 1. `create_project`

Create a new project and set as current.

**Parameters**:
- `name` (string, required): Project name
- `description` (string, optional): Project description
- `context` (Context, internal): MCP context

**Permissions**: `write:projects`

**Returns**:
```json
{
  "id": "proj-uuid",
  "name": "My Project",
  "description": "Project description",
  "created_at": "2026-01-29T10:30:00Z"
}
```

**Example**:
```bash
mcp_call create_project \
  --name "My Traceability Project" \
  --description "Full traceability for system"
```

---

#### 2. `list_projects`

List all accessible projects.

**Parameters**:
- `context` (Context, internal): MCP context

**Permissions**: `read:projects`

**Returns**:
```json
[
  {
    "id": "proj-1",
    "name": "Project A",
    "description": "First project",
    "created_at": "2026-01-01T00:00:00Z"
  },
  {
    "id": "proj-2",
    "name": "Project B",
    "description": "Second project",
    "created_at": "2026-01-02T00:00:00Z"
  }
]
```

**Example**:
```bash
mcp_call list_projects
```

---

#### 3. `select_project`

Set a project as the current working project.

**Parameters**:
- `project_id` (string, required): Project ID
- `context` (Context, internal): MCP context

**Permissions**: `read:projects`

**Returns**:
```json
{
  "id": "proj-123",
  "name": "My Project",
  "selected": true,
  "timestamp": "2026-01-29T10:30:45Z"
}
```

**Example**:
```bash
mcp_call select_project --project_id proj-123
```

---

#### 4. `snapshot_project`

Create a snapshot of current project state.

**Parameters**:
- `project_id` (string, required): Project ID
- `description` (string, optional): Snapshot description
- `context` (Context, internal): MCP context

**Permissions**: `read:projects`

**Returns**:
```json
{
  "snapshot_id": "snap-uuid",
  "project_id": "proj-123",
  "created_at": "2026-01-29T10:30:00Z",
  "item_count": 42,
  "link_count": 85
}
```

**Example**:
```bash
mcp_call snapshot_project \
  --project_id proj-123 \
  --description "Before refactoring"
```

---

### Item Management Tools

#### 5. `create_item`

Create a new item (requirement, feature, test, etc.).

**Parameters**:
- `project_id` (string, required): Project ID
- `name` (string, required): Item name
- `item_type` (string, required): Type (requirement, feature, test_case, etc.)
- `description` (string, optional): Item description
- `status` (string, optional): Status (draft, approved, implemented, etc.)
- `owner` (string, optional): Owner user ID
- `priority` (string, optional): Priority (low, medium, high)
- `tags` (array, optional): Tag array
- `context` (Context, internal): MCP context

**Permissions**: `write:items`

**Returns**:
```json
{
  "id": "item-uuid",
  "project_id": "proj-123",
  "name": "User Authentication",
  "type": "requirement",
  "status": "draft",
  "created_at": "2026-01-29T10:30:00Z"
}
```

**Example**:
```bash
mcp_call create_item \
  --project_id proj-123 \
  --name "User Authentication System" \
  --item_type requirement \
  --status draft \
  --priority high
```

---

#### 6. `get_item`

Retrieve a single item by ID.

**Parameters**:
- `item_id` (string, required): Item ID
- `context` (Context, internal): MCP context

**Permissions**: `read:items`

**Returns**:
```json
{
  "id": "item-uuid",
  "project_id": "proj-123",
  "name": "User Authentication",
  "type": "requirement",
  "status": "approved",
  "description": "System must support OAuth2 and SAML",
  "owner": "user-1",
  "priority": "high",
  "tags": ["auth", "security"],
  "created_at": "2026-01-29T10:30:00Z",
  "updated_at": "2026-01-29T11:45:00Z"
}
```

**Example**:
```bash
mcp_call get_item --item_id item-uuid
```

---

#### 7. `update_item`

Update an item's properties.

**Parameters**:
- `item_id` (string, required): Item ID
- `name` (string, optional): Updated name
- `status` (string, optional): Updated status
- `description` (string, optional): Updated description
- `priority` (string, optional): Updated priority
- `owner` (string, optional): Updated owner
- `context` (Context, internal): MCP context

**Permissions**: `write:items`

**Returns**: Updated item object

**Example**:
```bash
mcp_call update_item \
  --item_id item-uuid \
  --status approved \
  --priority critical
```

---

#### 8. `delete_item`

Delete an item.

**Parameters**:
- `item_id` (string, required): Item ID
- `context` (Context, internal): MCP context

**Permissions**: `write:items`

**Returns**:
```json
{
  "id": "item-uuid",
  "deleted": true,
  "timestamp": "2026-01-29T10:30:45Z"
}
```

**Example**:
```bash
mcp_call delete_item --item_id item-uuid
```

---

#### 9. `query_items`

Query items with filters.

**Parameters**:
- `project_id` (string, required): Project ID
- `type` (string, optional): Filter by type
- `status` (string, optional): Filter by status
- `owner` (string, optional): Filter by owner
- `tags` (array, optional): Filter by tags
- `search` (string, optional): Full-text search
- `limit` (integer, optional): Results per page (default: 50)
- `page` (integer, optional): Page number (default: 1)
- `context` (Context, internal): MCP context

**Permissions**: `read:items`

**Returns**:
```json
{
  "items": [
    {
      "id": "item-1",
      "name": "Item 1",
      "type": "requirement",
      "status": "approved"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 125,
    "pages": 3
  }
}
```

**Example**:
```bash
mcp_call query_items \
  --project_id proj-123 \
  --type requirement \
  --status approved \
  --limit 20
```

---

#### 10. `bulk_update_items`

Update multiple items at once.

**Parameters**:
- `item_ids` (array, required): Array of item IDs
- `updates` (object, required): Fields to update
- `context` (Context, internal): MCP context

**Permissions**: `write:items`, `bulk:items`

**Returns**:
```json
{
  "updated_count": 5,
  "failed_count": 0,
  "results": [
    {"id": "item-1", "status": "approved"},
    {"id": "item-2", "status": "approved"}
  ]
}
```

**Example**:
```bash
mcp_call bulk_update_items \
  --item_ids '["item-1", "item-2", "item-3"]' \
  --updates '{"status": "approved", "owner": "user-1"}'
```

---

### Link Management Tools

#### 11. `create_link`

Create a traceability link between items.

**Parameters**:
- `source_item_id` (string, required): Source item ID
- `target_item_id` (string, required): Target item ID
- `link_type` (string, required): Link type (traces_to, implements, tests, etc.)
- `description` (string, optional): Link description
- `context` (Context, internal): MCP context

**Permissions**: `write:links`

**Returns**:
```json
{
  "id": "link-uuid",
  "source_item_id": "item-1",
  "target_item_id": "item-2",
  "link_type": "traces_to",
  "created_at": "2026-01-29T10:30:00Z"
}
```

**Example**:
```bash
mcp_call create_link \
  --source_item_id item-req-1 \
  --target_item_id item-feature-1 \
  --link_type traces_to
```

---

#### 12. `list_links`

List links for an item.

**Parameters**:
- `item_id` (string, required): Item ID
- `direction` (string, optional): incoming, outgoing, or both
- `link_type` (string, optional): Filter by type
- `context` (Context, internal): MCP context

**Permissions**: `read:links`

**Returns**:
```json
[
  {
    "id": "link-1",
    "source_item_id": "item-1",
    "target_item_id": "item-2",
    "link_type": "traces_to"
  }
]
```

**Example**:
```bash
mcp_call list_links \
  --item_id item-uuid \
  --direction outgoing
```

---

#### 13. `find_orphaned_links`

Find links with missing target items.

**Parameters**:
- `project_id` (string, required): Project ID
- `context` (Context, internal): MCP context

**Permissions**: `read:links`, `analyze:trace`

**Returns**:
```json
{
  "orphaned_links": [
    {
      "id": "link-1",
      "source_item_id": "item-1",
      "target_item_id": "missing-item",
      "issue": "target_not_found"
    }
  ],
  "count": 3
}
```

**Example**:
```bash
mcp_call find_orphaned_links --project_id proj-123
```

---

#### 14. `find_missing_links`

Find uncovered items (gaps in traceability).

**Parameters**:
- `project_id` (string, required): Project ID
- `source_type` (string, optional): From type (requirement)
- `target_type` (string, optional): To type (feature, test)
- `link_type` (string, optional): Expected link type
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "missing_links": [
    {
      "source_item_id": "req-1",
      "source_name": "User Authentication",
      "target_type": "feature",
      "reason": "no_traces_to"
    }
  ],
  "gap_count": 5
}
```

**Example**:
```bash
mcp_call find_missing_links \
  --project_id proj-123 \
  --source_type requirement \
  --target_type feature
```

---

#### 15. `delete_link`

Delete a link.

**Parameters**:
- `link_id` (string, required): Link ID
- `context` (Context, internal): MCP context

**Permissions**: `write:links`

**Returns**:
```json
{
  "id": "link-uuid",
  "deleted": true
}
```

**Example**:
```bash
mcp_call delete_link --link_id link-uuid
```

---

### Traceability Analysis Tools

#### 16. `trace_gap_analysis`

Identify uncovered items and requirements.

**Parameters**:
- `project_id` (string, required): Project ID
- `source_view` (string, optional): requirements
- `target_view` (string, optional): features
- `link_type` (string, optional): traces_to
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "gap_count": 5,
  "coverage_percentage": 83.3,
  "gaps": [
    {
      "item_id": "req-5",
      "name": "Admin Dashboard",
      "type": "requirement",
      "reason": "no_implementation"
    }
  ]
}
```

**Example**:
```bash
mcp_call trace_gap_analysis \
  --project_id proj-123 \
  --source_view requirements \
  --target_view features
```

---

#### 17. `trace_impact_analysis`

Analyze impact of changes on related items.

**Parameters**:
- `item_id` (string, required): Starting item ID
- `depth` (integer, optional): Max depth (default: 3)
- `direction` (string, optional): forward, backward, bidirectional
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "root_item": {
    "id": "item-1",
    "name": "Authentication System"
  },
  "impact_chain": [
    {
      "level": 1,
      "items": [
        {"id": "item-2", "name": "OAuth Implementation"}
      ]
    }
  ],
  "total_affected": 7
}
```

**Example**:
```bash
mcp_call trace_impact_analysis \
  --item_id item-auth \
  --depth 3
```

---

#### 18. `trace_reverse_impact`

Find items that would be affected if this item changes.

**Parameters**:
- `item_id` (string, required): Item ID
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**: Similar to impact analysis

**Example**:
```bash
mcp_call trace_reverse_impact --item_id item-uuid
```

---

#### 19. `trace_matrix`

Generate traceability matrix.

**Parameters**:
- `project_id` (string, required): Project ID
- `source_type` (string, optional): requirements
- `target_type` (string, optional): features
- `format` (string, optional): json, csv
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "matrix": [
    {
      "source": {"id": "req-1", "name": "User Auth"},
      "targets": [
        {"id": "feat-1", "name": "OAuth Login"}
      ]
    }
  ],
  "coverage": 85.5
}
```

**Example**:
```bash
mcp_call trace_matrix \
  --project_id proj-123 \
  --source_type requirement \
  --target_type feature
```

---

#### 20. `trace_health_assessment`

Assess overall traceability health of project.

**Parameters**:
- `project_id` (string, required): Project ID
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "health_score": 87.5,
  "status": "good",
  "metrics": {
    "coverage": 85.5,
    "orphaned_items": 3,
    "orphaned_links": 1,
    "completeness": 90
  }
}
```

**Example**:
```bash
mcp_call trace_health_assessment --project_id proj-123
```

---

### Graph Analysis Tools

#### 21. `analyze_cycles`

Detect cycles in the dependency graph.

**Parameters**:
- `project_id` (string, required): Project ID
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "cycle_count": 2,
  "cycles": [
    {
      "path": ["item-1", "item-2", "item-3", "item-1"],
      "length": 3
    }
  ]
}
```

**Example**:
```bash
mcp_call analyze_cycles --project_id proj-123
```

---

#### 22. `analyze_shortest_path`

Find shortest path between two items.

**Parameters**:
- `start_item_id` (string, required): Start item ID
- `end_item_id` (string, required): End item ID
- `max_depth` (integer, optional): Max search depth
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "path_found": true,
  "path": ["item-1", "item-2", "item-3"],
  "length": 2,
  "steps": [
    {"from": "item-1", "to": "item-2", "link_type": "traces_to"},
    {"from": "item-2", "to": "item-3", "link_type": "implements"}
  ]
}
```

**Example**:
```bash
mcp_call analyze_shortest_path \
  --start_item_id item-req \
  --end_item_id item-test
```

---

#### 23. `analyze_dependencies`

Analyze dependency graph of items.

**Parameters**:
- `project_id` (string, required): Project ID
- `item_id` (string, optional): Root item for analysis
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:links`, `analyze:trace`

**Returns**:
```json
{
  "dependencies": {
    "item-1": {
      "depends_on": ["item-2", "item-3"],
      "depended_by": ["item-4"]
    }
  },
  "order": ["item-2", "item-3", "item-1", "item-4"]
}
```

**Example**:
```bash
mcp_call analyze_dependencies --project_id proj-123
```

---

### Specification Management Tools

#### 24. `create_specification`

Create a specification (ADR, contract, feature, scenario).

**Parameters**:
- `project_id` (string, required): Project ID
- `spec_kind` (string, required): adr, contract, feature, or scenario
- `title` (string, required): Specification title
- `content` (string, required): Specification content
- `status` (string, optional): draft, review, approved
- `context` (Context, internal): MCP context

**Permissions**: `write:specs`

**Returns**:
```json
{
  "id": "spec-uuid",
  "kind": "adr",
  "title": "Use PostgreSQL for Primary Database",
  "status": "draft",
  "created_at": "2026-01-29T10:30:00Z"
}
```

**Example**:
```bash
mcp_call create_specification \
  --project_id proj-123 \
  --spec_kind adr \
  --title "Architecture Decision: Use Event Sourcing" \
  --content "Content..."
```

---

#### 25. `list_specifications`

List specifications in a project.

**Parameters**:
- `project_id` (string, required): Project ID
- `spec_kind` (string, optional): Filter by kind
- `status` (string, optional): Filter by status
- `context` (Context, internal): MCP context

**Permissions**: `read:specs`

**Returns**:
```json
[
  {
    "id": "spec-1",
    "kind": "adr",
    "title": "Database Choice",
    "status": "approved"
  }
]
```

**Example**:
```bash
mcp_call list_specifications \
  --project_id proj-123 \
  --spec_kind adr
```

---

#### 26. `update_specification`

Update a specification.

**Parameters**:
- `spec_id` (string, required): Specification ID
- `title` (string, optional): Updated title
- `content` (string, optional): Updated content
- `status` (string, optional): Updated status
- `context` (Context, internal): MCP context

**Permissions**: `write:specs`

**Returns**: Updated specification object

**Example**:
```bash
mcp_call update_specification \
  --spec_id spec-uuid \
  --status approved
```

---

### Quality Analysis Tools

#### 27. `analyze_quality`

Analyze requirement quality.

**Parameters**:
- `project_id` (string, required): Project ID
- `item_id` (string, optional): Single item analysis
- `scope` (string, optional): item, project, view
- `context` (Context, internal): MCP context

**Permissions**: `read:items`, `read:specs`, `analyze:quality`

**Returns**:
```json
{
  "quality_score": 87.5,
  "issues": [
    {
      "item_id": "item-1",
      "issue": "missing_acceptance_criteria",
      "severity": "high"
    }
  ]
}
```

**Example**:
```bash
mcp_call analyze_quality --project_id proj-123
```

---

### Configuration Management Tools

#### 28. `get_config`

Get project configuration.

**Parameters**:
- `project_id` (string, required): Project ID
- `context` (Context, internal): MCP context

**Permissions**: `read:config`

**Returns**:
```json
{
  "project_id": "proj-123",
  "name": "My Project",
  "link_types": ["traces_to", "implements", "tests"],
  "item_types": ["requirement", "feature", "test_case"]
}
```

---

#### 29. `update_config`

Update project configuration.

**Parameters**:
- `project_id` (string, required): Project ID
- `updates` (object, required): Config updates
- `context` (Context, internal): MCP context

**Permissions**: `write:config`

**Returns**: Updated config object

---

### Workflow Tools

#### 30+ BMM Workflow Tools

See `src/tracertm/mcp/tools/bmm_workflows.py` for complete workflow implementation.

---

## Usage Examples

### Example 1: Create a Project and Items

```bash
# Create project
PROJECT=$(mcp_call create_project \
  --name "Safety System" \
  --description "Critical safety requirements" | jq -r .data.id)

# Create requirement item
ITEM1=$(mcp_call create_item \
  --project_id $PROJECT \
  --name "System Shutdown" \
  --item_type requirement \
  --status approved | jq -r .data.id)

# Create feature item
ITEM2=$(mcp_call create_item \
  --project_id $PROJECT \
  --name "Emergency Stop Button" \
  --item_type feature | jq -r .data.id)

# Link them
mcp_call create_link \
  --source_item_id $ITEM1 \
  --target_item_id $ITEM2 \
  --link_type traces_to
```

### Example 2: Gap Analysis

```bash
# Find uncovered requirements
mcp_call trace_gap_analysis \
  --project_id proj-123 \
  --source_view requirements \
  --target_view features \
  --link_type traces_to
```

### Example 3: Impact Analysis

```bash
# Change API authentication method
# Check what breaks
mcp_call trace_impact_analysis \
  --item_id item-auth-method \
  --depth 3
```

### Example 4: Cycle Detection

```bash
# Find circular dependencies
mcp_call analyze_cycles --project_id proj-123
```

### Example 5: Query with Filters

```bash
# Find all high-priority approved requirements
mcp_call query_items \
  --project_id proj-123 \
  --type requirement \
  --status approved \
  --priority high \
  --limit 50
```

---

## Rate Limiting

### Default Limits

| Category | Limit | Window |
|----------|-------|--------|
| General tools | 120 req/min | 1 minute |
| Bulk operations | 20 req/min | 1 minute |
| Analysis tools | 30 req/min | 1 minute |
| Search/query | 60 req/min | 1 minute |

### Configuring Rate Limits

```bash
export TRACERTM_MCP_RATE_LIMIT_RPM=240
export TRACERTM_MCP_RATE_LIMIT_BURST=10
```

### Rate Limit Headers

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1643452800
```

### Handling 429 Responses

```bash
# Wait and retry
RETRY_AFTER=$(curl -i ... | grep "Retry-After" | cut -d' ' -f2)
sleep $RETRY_AFTER
mcp_call ...
```

---

## Appendix: Tool Inventory Checklist

- [x] 10 Project Management tools
- [x] 10 Item Management tools
- [x] 5 Link Management tools
- [x] 5 Traceability Analysis tools
- [x] 3 Graph Analysis tools
- [x] 3 Specification Management tools
- [x] 1 Quality Analysis tool
- [x] 1 Configuration tool
- [x] 8+ BMM Workflow tools

**Total Documented**: 46+ tools

---

## See Also

- [MCP CLI Consolidation Spec](./MCP_CLI_CONSOLIDATION_SPEC.md)
- [Auth Flows Documentation](./AUTH_FLOWS.md)
- [MCP Quickstart](./MCP_QUICKSTART.md)
