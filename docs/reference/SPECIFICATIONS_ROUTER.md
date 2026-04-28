# Specifications API Router

Comprehensive API router for managing Architecture Decision Records (ADRs), Contracts, Features, and Scenarios.

## Overview

The Specifications Router provides a unified interface for all specification-related endpoints, following RESTful conventions with proper authentication, validation, and error handling.

**Base Path:** `/api/v1/specifications`

**Authentication:** All endpoints require valid JWT token via `Authorization: Bearer <token>` header

## Architecture Decision Records (ADRs)

ADRs document significant technical decisions and their context, following the MADR 4.0 standard.

### Create ADR
```http
POST /api/v1/specifications/adrs
Content-Type: application/json
Authorization: Bearer {token}

{
  "project_id": "proj-123",
  "title": "Use PostgreSQL for persistence",
  "context": "We need a reliable ACID-compliant database for our traceability system...",
  "decision": "We will use PostgreSQL as the primary database",
  "consequences": "Requires PostgreSQL expertise on the team, scaling considerations...",
  "status": "proposed",
  "decision_drivers": [
    "ACID compliance requirement",
    "Team expertise with PostgreSQL",
    "Cost-effectiveness"
  ],
  "considered_options": [
    {
      "id": "opt-1",
      "title": "MongoDB",
      "pros": ["Flexible schema", "High scalability"],
      "cons": ["No ACID for multi-document"],
      "is_chosen": false
    }
  ],
  "related_requirements": ["REQ-123", "REQ-456"],
  "related_adrs": ["ADR-0001"],
  "tags": ["database", "persistence"],
  "stakeholders": ["tech-lead", "backend-team"]
}
```

**Response (201 Created):**
```json
{
  "id": "adr-789",
  "project_id": "proj-123",
  "adr_number": "ADR-0002",
  "title": "Use PostgreSQL for persistence",
  "status": "proposed",
  "context": "We need a reliable ACID-compliant database...",
  "decision": "We will use PostgreSQL as the primary database",
  "consequences": "Requires PostgreSQL expertise...",
  "decision_drivers": ["ACID compliance requirement", ...],
  "considered_options": [...],
  "related_requirements": ["REQ-123", "REQ-456"],
  "related_adrs": ["ADR-0001"],
  "supersedes": null,
  "superseded_by": null,
  "compliance_score": 0.0,
  "stakeholders": ["tech-lead", "backend-team"],
  "tags": ["database", "persistence"],
  "metadata": {},
  "version": 1,
  "last_verified_at": null,
  "created_at": "2025-01-29T10:30:00Z",
  "updated_at": "2025-01-29T10:30:00Z",
  "deleted_at": null
}
```

### Get ADR
```http
GET /api/v1/specifications/adrs/{adr_id}
Authorization: Bearer {token}
```

Returns a single ADR by ID with all details.

### Update ADR
```http
PUT /api/v1/specifications/adrs/{adr_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "accepted",
  "related_adrs": ["ADR-0001", "ADR-0003"]
}
```

Partial updates supported - only provided fields are updated.

### Delete ADR
```http
DELETE /api/v1/specifications/adrs/{adr_id}
Authorization: Bearer {token}
```

Soft deletes - sets `deleted_at` timestamp.

### List Project ADRs
```http
GET /api/v1/specifications/projects/{project_id}/adrs?status=proposed&tags=database
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: Filter by ADR status (proposed, accepted, deprecated, superseded, rejected)
- `tags`: Filter by tags (comma-separated or repeated)

**Response:**
```json
{
  "total": 2,
  "adrs": [
    { /* ADRResponse */ },
    { /* ADRResponse */ }
  ]
}
```

### Verify ADR Compliance
```http
POST /api/v1/specifications/adrs/{adr_id}/verify
Authorization: Bearer {token}
```

**Response:**
```json
{
  "is_valid": true,
  "score": 85.0,
  "issues": [],
  "warnings": [
    "Decision drivers should be documented"
  ],
  "timestamp": "2025-01-29T10:31:00Z"
}
```

**Verification Checks:**
- Context presence and detail (minimum 50 characters)
- Decision clarity (minimum 20 characters)
- Consequences documentation
- Traceability to requirements or other ADRs
- Decision drivers documentation

## Contracts

Contracts define pre/post-conditions and invariants for components.

### Create Contract
```http
POST /api/v1/specifications/contracts
Content-Type: application/json
Authorization: Bearer {token}

{
  "project_id": "proj-123",
  "item_id": "item-456",
  "title": "Item Service Contract",
  "contract_type": "service",
  "status": "draft",
  "preconditions": [
    {
      "id": "pre-1",
      "description": "User must be authenticated",
      "condition_code": "user.is_authenticated == True"
    }
  ],
  "postconditions": [
    {
      "id": "post-1",
      "description": "Item is created and stored",
      "condition_code": "item.id is not None"
    }
  ],
  "invariants": [
    {
      "id": "inv-1",
      "description": "Item status is always valid"
    }
  ],
  "states": ["draft", "active", "archived"],
  "transitions": [
    {
      "id": "trans-1",
      "from_state": "draft",
      "to_state": "active",
      "trigger": "publish()",
      "condition": "validation.pass == true"
    }
  ],
  "tags": ["service", "api"]
}
```

### Get Contract
```http
GET /api/v1/specifications/contracts/{contract_id}
Authorization: Bearer {token}
```

### Update Contract
```http
PUT /api/v1/specifications/contracts/{contract_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "approved"
}
```

### Delete Contract
```http
DELETE /api/v1/specifications/contracts/{contract_id}
Authorization: Bearer {token}
```

### List Project Contracts
```http
GET /api/v1/specifications/projects/{project_id}/contracts?item_id=item-456&status=approved
Authorization: Bearer {token}
```

**Query Parameters:**
- `item_id`: Filter by item
- `contract_type`: Filter by type (api, function, class, module, workflow, service)
- `status`: Filter by status

### Verify Contract Compliance
```http
POST /api/v1/specifications/contracts/{contract_id}/verify
Authorization: Bearer {token}
```

**Verification Checks:**
- Preconditions defined
- Postconditions defined
- Clear title
- States defined if transitions exist

## Features

BDD Features describe user-facing functionality.

### Create Feature
```http
POST /api/v1/specifications/features
Content-Type: application/json
Authorization: Bearer {token}

{
  "project_id": "proj-123",
  "name": "User Authentication",
  "description": "Users can authenticate using GitHub OAuth",
  "as_a": "developer",
  "i_want": "to authenticate with GitHub",
  "so_that": "I can access my projects",
  "status": "draft",
  "related_requirements": ["REQ-123"],
  "related_adrs": ["ADR-0001"],
  "tags": ["auth", "oauth"]
}
```

### Get Feature
```http
GET /api/v1/specifications/features/{feature_id}?include_scenarios=true
Authorization: Bearer {token}
```

**Query Parameters:**
- `include_scenarios`: Include associated scenarios in response (default: false)

### Update Feature
```http
PUT /api/v1/specifications/features/{feature_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "in_development"
}
```

### Delete Feature
```http
DELETE /api/v1/specifications/features/{feature_id}
Authorization: Bearer {token}
```

### List Project Features
```http
GET /api/v1/specifications/projects/{project_id}/features?status=in_development&tags=auth
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: Filter by status (draft, in_development, ready_for_test, in_test, ready_for_release, released, deprecated)
- `tags`: Filter by tags

## Scenarios

Gherkin scenarios define behavior in Given-When-Then format.

### Create Scenario
```http
POST /api/v1/specifications/features/{feature_id}/scenarios
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "User logs in with GitHub",
  "description": "Scenario for successful GitHub authentication",
  "gherkin_text": "Feature: User Authentication\n  Scenario: Login with GitHub\n    Given user is on login page\n    When user clicks GitHub button\n    Then user is redirected to GitHub\n    And GitHub requests authorization",
  "status": "draft",
  "given_steps": [
    {
      "step_number": 1,
      "keyword": "Given",
      "text": "user is on login page"
    }
  ],
  "when_steps": [
    {
      "step_number": 2,
      "keyword": "When",
      "text": "user clicks GitHub button"
    }
  ],
  "then_steps": [
    {
      "step_number": 3,
      "keyword": "Then",
      "text": "user is redirected to GitHub"
    }
  ],
  "is_outline": false,
  "tags": ["auth", "critical"]
}
```

### Get Scenario
```http
GET /api/v1/specifications/scenarios/{scenario_id}
Authorization: Bearer {token}
```

### Update Scenario
```http
PUT /api/v1/specifications/scenarios/{scenario_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "approved"
}
```

### Delete Scenario
```http
DELETE /api/v1/specifications/scenarios/{scenario_id}
Authorization: Bearer {token}
```

### List Feature Scenarios
```http
GET /api/v1/specifications/features/{feature_id}/scenarios?status=approved
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: Filter by status (draft, review, approved, automated, deprecated)

### Run Scenario
```http
POST /api/v1/specifications/scenarios/{scenario_id}/run
Authorization: Bearer {token}
```

**Response:**
```json
{
  "scenario_id": "scenario-123",
  "passed": true,
  "duration_ms": 1234.5,
  "steps_passed": 4,
  "steps_failed": 0,
  "error_message": null,
  "timestamp": "2025-01-29T10:32:00Z"
}
```

## Project-Level Endpoints

### Get Specifications Summary
```http
GET /api/v1/specifications/projects/{project_id}/summary
Authorization: Bearer {token}
```

**Response:**
```json
{
  "project_id": "proj-123",
  "adr_count": 5,
  "contract_count": 12,
  "feature_count": 8,
  "scenario_count": 42,
  "compliance_score": 87.5
}
```

Aggregated metrics across all specifications in a project.

## Error Handling

All endpoints return standard HTTP status codes:

- **200 OK**: Successful GET/PUT
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input, missing fields, validation errors
- **401 Unauthorized**: Missing or invalid authentication token
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

**Error Response Format:**
```json
{
  "detail": "Descriptive error message"
}
```

## Authentication

All endpoints require JWT authentication via WorkOS AuthKit.

Include the token in the Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Validation

All input is validated using Pydantic schemas:

- **Required fields**: Must be present and non-null
- **Field lengths**: String fields have min/max length constraints
- **Enums**: Status and type fields must use valid enum values
- **Nested objects**: Complex structures validated recursively

## Compliance Scoring

Both ADRs and Contracts are scored on completeness and best practices.

**Scoring Factors:**
- Presence of required sections
- Sufficient detail in documentation
- Proper traceability links
- Stakeholder engagement
- Standards adherence

Scores range from 0-100, where 100 is fully compliant.

## Best Practices

1. **ADRs**: Include clear context, document all considered options, link to related items
2. **Contracts**: Define both pre and post conditions, document state machines clearly
3. **Features**: Use proper user story format (As a / I want / So that)
4. **Scenarios**: Write clear Gherkin with proper step structure
5. **Traceability**: Link specifications to requirements and other specifications
6. **Review**: Verify compliance before marking as approved

## Integration Examples

### Python Client
```python
import httpx

async with httpx.AsyncClient() as client:
    # Create ADR
    adr = await client.post(
        "http://api.example.com/api/v1/specifications/adrs",
        json={
            "project_id": "proj-123",
            "title": "Database Choice",
            "context": "...",
            "decision": "...",
            "consequences": "..."
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Verify compliance
    result = await client.post(
        f"http://api.example.com/api/v1/specifications/adrs/{adr.json()['id']}/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Compliance Score: {result.json()['score']}")
```

### JavaScript/TypeScript Client
```typescript
async function createADR(token: string, adr: ADRCreate) {
  const response = await fetch('http://api.example.com/api/v1/specifications/adrs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(adr)
  });
  return response.json();
}

async function verifyADR(token: string, adrId: string) {
  const response = await fetch(
    `http://api.example.com/api/v1/specifications/adrs/${adrId}/verify`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.json();
}
```

## Rate Limiting

Currently no rate limiting is implemented. Contact the API team for production deployment considerations.

## Pagination

List endpoints return all results. For large datasets, pagination may be added in future versions.

## Versioning

API version: v1
Location: `/api/v1/specifications`

## Related Resources

- [ADR Decision Record Format](https://adr.github.io/madr/)
- [Design by Contract](https://en.wikipedia.org/wiki/Design_by_contract)
- [Gherkin Language Specification](https://cucumber.io/docs/gherkin/)
- [BDD Best Practices](https://cucumber.io/school/bdd-with-cucumber/)
