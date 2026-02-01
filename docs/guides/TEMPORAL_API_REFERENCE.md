# Temporal API Reference Guide

## Quick Start

### Base URL
```
/api/v1
```

### Authentication
All endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

---

## Branch Management

### Create Branch
```http
POST /api/v1/projects/{projectId}/branches
Content-Type: application/json

{
  "name": "feature/payment-flow",
  "slug": "feature-payment-flow",
  "branch_type": "feature",
  "description": "Payment flow implementation",
  "metadata": {}
}
```

**Response:** `201 Created`
```json
{
  "id": "b-uuid",
  "project_id": "proj-123",
  "name": "feature/payment-flow",
  "slug": "feature-payment-flow",
  "branch_type": "feature",
  "status": "active",
  "is_default": false,
  "is_protected": false,
  "version_count": 0,
  "item_count": 0,
  "created_at": "2026-01-29T12:00:00Z",
  "created_by": "user-123"
}
```

### Get Branch
```http
GET /api/v1/branches/{branchId}
```

**Response:** `200 OK`
```json
{
  "id": "b-uuid",
  "project_id": "proj-123",
  "name": "feature/payment-flow",
  "status": "active",
  "version_count": 5,
  "item_count": 42,
  ...
}
```

### List Project Branches
```http
GET /api/v1/projects/{projectId}/branches
```

**Response:** `200 OK`
```json
{
  "branches": [
    { "id": "b-1", "name": "main", "status": "active" },
    { "id": "b-2", "name": "develop", "status": "active" },
    { "id": "b-3", "name": "feature/payment", "status": "review" }
  ],
  "count": 3
}
```

### Update Branch
```http
PUT /api/v1/branches/{branchId}
Content-Type: application/json

{
  "name": "feature/payment-flow-v2",
  "status": "review",
  "is_protected": true
}
```

**Response:** `200 OK`

### Delete Branch
```http
DELETE /api/v1/branches/{branchId}
```

**Response:** `204 No Content`

---

## Version Management

### Create Version
```http
POST /api/v1/branches/{branchId}/versions
Content-Type: application/json

{
  "project_id": "proj-123",
  "message": "Add payment processing integration",
  "tag": "v1.2.0",
  "item_count": 42,
  "change_count": 5
}
```

**Response:** `201 Created`
```json
{
  "id": "v-uuid",
  "branch_id": "b-uuid",
  "version_number": 5,
  "status": "draft",
  "message": "Add payment processing integration",
  "tag": "v1.2.0",
  "created_at": "2026-01-29T12:05:00Z",
  "created_by": "user-123"
}
```

### Get Version
```http
GET /api/v1/versions/{versionId}
```

**Response:** `200 OK`

### List Versions by Branch
```http
GET /api/v1/branches/{branchId}/versions
```

**Response:** `200 OK`
```json
{
  "versions": [
    { "id": "v-1", "version_number": 1, "status": "approved" },
    { "id": "v-2", "version_number": 2, "status": "approved" },
    { "id": "v-3", "version_number": 3, "status": "draft" }
  ],
  "count": 3
}
```

### Approve Version
```http
POST /api/v1/versions/{versionId}/approve
Content-Type: application/json

{
  "approved_by": "user-456"
}
```

**Response:** `200 OK`
```json
{
  "status": "approved"
}
```

### Reject Version
```http
POST /api/v1/versions/{versionId}/reject
Content-Type: application/json

{
  "reason": "Missing test coverage"
}
```

**Response:** `200 OK`

---

## Item Versioning

### Get Item at Version
```http
GET /api/v1/items/{itemId}/versions/{versionId}
```

**Response:** `200 OK`
```json
{
  "id": "iv-uuid",
  "item_id": "item-1",
  "version_id": "v-1",
  "lifecycle": "implemented",
  "state": {
    "title": "User Authentication",
    "description": "OAuth2 integration",
    "status": "done",
    "priority": "high"
  },
  "introduced_in_version_id": "v-0",
  "last_modified_in_version_id": "v-1",
  "created_at": "2026-01-29T10:00:00Z"
}
```

### Get Item History
```http
GET /api/v1/items/{itemId}/version-history?branch_id={branchId}
```

**Response:** `200 OK`
```json
{
  "history": [
    { "id": "iv-1", "version_id": "v-1", "lifecycle": "idea" },
    { "id": "iv-2", "version_id": "v-2", "lifecycle": "proposed" },
    { "id": "iv-3", "version_id": "v-3", "lifecycle": "implemented" }
  ],
  "count": 3
}
```

### Restore Item to Version
```http
POST /api/v1/items/{itemId}/restore
Content-Type: application/json

{
  "version_id": "v-2"
}
```

**Response:** `200 OK`
```json
{
  "status": "restored"
}
```

---

## Item Alternatives

### List Alternatives
```http
GET /api/v1/items/{itemId}/alternatives
```

**Response:** `200 OK`
```json
{
  "alternatives": [
    {
      "id": "alt-1",
      "base_item_id": "item-1",
      "alternative_item_id": "item-2",
      "relationship": "alternative_to",
      "description": "Stripe vs PayPal payment",
      "is_chosen": false
    },
    {
      "id": "alt-2",
      "base_item_id": "item-1",
      "alternative_item_id": "item-3",
      "relationship": "alternative_to",
      "description": "Stripe vs Square payment",
      "is_chosen": false
    }
  ],
  "count": 2
}
```

### Create Alternative
```http
POST /api/v1/items/{itemId}/alternatives
Content-Type: application/json

{
  "project_id": "proj-123",
  "alternative_item_id": "item-2",
  "relationship": "alternative_to",
  "description": "Alternative payment gateway",
  "metrics": {
    "effort": 40,
    "risk": "medium",
    "coverage": 95
  }
}
```

**Response:** `201 Created`

### Select Alternative
```http
POST /api/v1/alternatives/{altId}/select
Content-Type: application/json

{
  "selected_by": "user-123",
  "reason": "Better transaction fees"
}
```

**Response:** `200 OK`
```json
{
  "status": "selected"
}
```

---

## Merge Requests

### Create Merge Request
```http
POST /api/v1/projects/{projectId}/merge-requests
Content-Type: application/json

{
  "source_branch_id": "feature/payment",
  "target_branch_id": "main",
  "title": "Add payment gateway integration",
  "description": "Implements Stripe payment processing",
  "reviewers": ["user-456", "user-789"],
  "created_by": "user-123"
}
```

**Response:** `201 Created`
```json
{
  "id": "mr-uuid",
  "project_id": "proj-123",
  "status": "open",
  "title": "Add payment gateway integration",
  "created_at": "2026-01-29T12:15:00Z",
  "created_by": "user-123"
}
```

### Get Merge Request
```http
GET /api/v1/merge-requests/{mrId}
```

**Response:** `200 OK`

### List Merge Requests
```http
GET /api/v1/projects/{projectId}/merge-requests?status=open
```

Query Parameters:
- `status` (optional): Filter by status (open, approved, merged, closed, conflict)

**Response:** `200 OK`
```json
{
  "merge_requests": [
    { "id": "mr-1", "status": "open", "title": "Add feature A" },
    { "id": "mr-2", "status": "approved", "title": "Add feature B" }
  ],
  "count": 2
}
```

### Get Merge Diff
```http
GET /api/v1/merge-requests/{mrId}/diff
```

**Response:** `200 OK`
```json
{
  "version_a_id": "v-1",
  "version_b_id": "v-2",
  "stats": {
    "total_changes": 5,
    "added_count": 2,
    "removed_count": 1,
    "modified_count": 2
  },
  "added": [
    { "item_id": "i-1", "type": "requirement", "title": "New feature" }
  ],
  "removed": [
    { "item_id": "i-2", "type": "task", "title": "Old task" }
  ],
  "modified": [
    { "item_id": "i-3", "type": "spec", "title": "Updated spec", "field_changes": [...] }
  ]
}
```

### Merge Branches
```http
POST /api/v1/merge-requests/{mrId}/merge
Content-Type: application/json

{
  "merged_by": "user-456"
}
```

**Response:** `200 OK`
```json
{
  "status": "merged"
}
```

---

## Version Comparison

### Compare Versions
```http
GET /api/v1/versions/{versionAId}/compare/{versionBId}
```

**Response:** `200 OK`
```json
{
  "version_a_id": "v-1",
  "version_b_id": "v-2",
  "version_a_number": 1,
  "version_b_number": 2,
  "stats": {
    "total_changes": 8,
    "added_count": 3,
    "removed_count": 2,
    "modified_count": 3,
    "unchanged_count": 42
  },
  "added": [
    { "item_id": "item-new-1", "type": "requirement", "title": "New requirement", "significance": "major" }
  ],
  "removed": [
    { "item_id": "item-old-1", "type": "task", "title": "Obsolete task", "significance": "minor" }
  ],
  "modified": [
    {
      "item_id": "item-1",
      "type": "spec",
      "title": "API Specification",
      "field_changes": [
        { "field": "description", "old_value": "...", "new_value": "...", "change_type": "modified" }
      ],
      "significance": "moderate"
    }
  ],
  "computed_at": "2026-01-29T12:20:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request body: missing required field 'message'"
}
```

### 404 Not Found
```json
{
  "error": "Branch not found: branch with ID 'b-invalid' does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to create branch: database connection error"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Server Error |

---

## Lifecycle States

### Item Lifecycle Transitions

```
idea → proposed, retired
proposed → planned, retired
planned → in_progress, retired
in_progress → implemented, planned, retired
implemented → verified, in_progress, retired
verified → released, implemented, retired
released → deprecated
deprecated → retired, released
retired → (no transitions)
```

### Version Status

```
draft → pending_review, approved (admin only)
pending_review → approved, rejected
approved → superseded
rejected → draft (resubmit)
superseded → (final)
```

### Branch Status

```
active → review (when creating merge request)
review → merged, abandoned
merged → archived
abandoned → archived
archived → (final)
```

---

## Common Patterns

### Workflow: Create and Merge Feature Branch

1. Create feature branch:
```bash
POST /api/v1/projects/{projectId}/branches
```

2. Create versions as work progresses:
```bash
POST /api/v1/branches/{branchId}/versions
```

3. Approve version when ready:
```bash
POST /api/v1/versions/{versionId}/approve
```

4. Create merge request:
```bash
POST /api/v1/projects/{projectId}/merge-requests
```

5. Review diff:
```bash
GET /api/v1/merge-requests/{mrId}/diff
```

6. Merge if approved:
```bash
POST /api/v1/merge-requests/{mrId}/merge
```

### Workflow: Compare Two Points in Time

1. Get version IDs:
```bash
GET /api/v1/branches/{branchId}/versions
```

2. Compare:
```bash
GET /api/v1/versions/{v1-id}/compare/{v2-id}
```

3. Restore if needed:
```bash
POST /api/v1/items/{itemId}/restore
```

---

## Rate Limiting

Currently unlimited. Future enhancement: implement rate limiting per user/API key.

---

## Pagination

Not yet implemented. Future enhancement will support:
```
?limit=20&offset=0
```

---

## WebSocket Events (Future)

Planned real-time events:
```
version.created
version.approved
branch.created
branch.merged
merge_request.opened
merge_request.merged
item.reverted
alternative.chosen
```
