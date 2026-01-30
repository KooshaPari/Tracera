# Item Specs API Contract

This document specifies the REST API contract expected by the `useItemSpecs` hooks.

## Base URL

```
/api/v1/projects/{projectId}/item-specs
```

## Requirement Specs Endpoints

### List Requirements
```
GET /api/v1/projects/{projectId}/item-specs/requirements
```

**Query Parameters**
- `requirement_type` (optional): One of ubiquitous, event_driven, state_driven, optional, complex, unwanted
- `risk_level` (optional): One of critical, high, medium, low, minimal
- `verification_status` (optional): One of unverified, pending, verified, failed, expired
- `limit` (optional, default 50): Maximum results
- `offset` (optional, default 0): Pagination offset

**Response**
```json
{
  "specs": [
    {
      "id": "spec-123",
      "item_id": "item-456",
      "requirement_type": "ubiquitous",
      "constraint_type": "hard",
      "constraint_target": 1000,
      "constraint_tolerance": 10,
      "constraint_unit": "ms",
      "ears_trigger": "When user logs in",
      "ears_precondition": "User has account",
      "ears_postcondition": "User is authenticated",
      "verification_status": "unverified",
      "verified_at": "2025-01-29T12:00:00Z",
      "verified_by": "qa-lead@example.com",
      "verification_evidence": { "test_id": "tc-789" },
      "formal_spec": "∀ user, authenticate(user) → logged_in(user)",
      "invariants": [],
      "preconditions": ["Network available"],
      "postconditions": ["Token stored"],
      "quality_scores": {
        "clarity": 0.95,
        "completeness": 0.85,
        "testability": 0.92
      },
      "ambiguity_score": 0.05,
      "completeness_score": 0.85,
      "testability_score": 0.92,
      "overall_quality_score": 0.90,
      "quality_issues": [
        {
          "dimension": "clarity",
          "severity": "info",
          "message": "Could be more specific about timeout behavior",
          "suggestion": "Add specific timeout value"
        }
      ],
      "volatility_index": 0.2,
      "change_count": 3,
      "last_changed_at": "2025-01-25T10:00:00Z",
      "change_history": [],
      "change_propagation_index": 0.15,
      "downstream_count": 5,
      "upstream_count": 2,
      "impact_assessment": {
        "affected_components": ["auth-service", "api-gateway"],
        "risk_level": "medium"
      },
      "risk_level": "high",
      "risk_factors": ["External dependency", "Performance critical"],
      "wsjf_score": 42.5,
      "business_value": 85,
      "time_criticality": 90,
      "risk_reduction": 75,
      "similar_items": [],
      "auto_tags": ["security", "authentication", "critical"],
      "complexity_estimate": "high",
      "source_reference": "SEC-2024-001",
      "rationale": "Required for compliance with OAuth 2.0",
      "stakeholders": ["security-lead@example.com", "product@example.com"],
      "spec_metadata": { "source": "requirements_doc_v2.docx" },
      "created_at": "2025-01-20T08:00:00Z",
      "updated_at": "2025-01-29T12:00:00Z"
    }
  ],
  "total": 142
}
```

### Get Requirement
```
GET /api/v1/projects/{projectId}/item-specs/requirements/{specId}
```

**Response**: Single RequirementSpec object (same schema as list)

**Error Responses**
- 404: Spec not found
- 403: Unauthorized

### Get Requirement by Item
```
GET /api/v1/projects/{projectId}/item-specs/requirements/by-item/{itemId}
```

**Response**: Single RequirementSpec object

### Unverified Requirements
```
GET /api/v1/projects/{projectId}/item-specs/requirements/unverified
```

**Query Parameters**
- `limit` (optional, default 100): Maximum results

**Response**
```json
{
  "specs": [...],
  "total": 45
}
```

### High-Risk Requirements
```
GET /api/v1/projects/{projectId}/item-specs/requirements/high-risk
```

**Query Parameters**
- `limit` (optional, default 100): Maximum results

**Response**
```json
{
  "specs": [...],
  "total": 12
}
```

### Create Requirement
```
POST /api/v1/projects/{projectId}/item-specs/requirements
```

**Request Body**
```json
{
  "item_id": "item-456",
  "requirement_type": "ubiquitous",
  "constraint_type": "hard",
  "constraint_target": 1000,
  "constraint_tolerance": 10,
  "constraint_unit": "ms",
  "ears_trigger": "When user logs in",
  "ears_precondition": "User has account",
  "ears_postcondition": "User is authenticated",
  "formal_spec": "...",
  "risk_level": "high",
  "risk_factors": ["External dependency"],
  "business_value": 85,
  "time_criticality": 90,
  "risk_reduction": 75,
  "source_reference": "SEC-2024-001",
  "rationale": "Required for compliance",
  "stakeholders": ["security-lead@example.com"],
  "spec_metadata": {}
}
```

**Response**: Created RequirementSpec object (201 Created)

### Update Requirement
```
PATCH /api/v1/projects/{projectId}/item-specs/requirements/{specId}
```

**Request Body**: Any subset of RequirementSpec fields

**Response**: Updated RequirementSpec object

### Delete Requirement
```
DELETE /api/v1/projects/{projectId}/item-specs/requirements/{specId}
```

**Response**: 204 No Content

### Analyze Quality
```
POST /api/v1/projects/{projectId}/item-specs/requirements/{specId}/analyze-quality
```

**Response**: RequirementSpec with updated quality_scores and quality_issues

### Analyze Impact
```
POST /api/v1/projects/{projectId}/item-specs/requirements/{specId}/analyze-impact
```

**Response**: RequirementSpec with updated impact_assessment, downstream_count, upstream_count

### Verify Requirement
```
POST /api/v1/projects/{projectId}/item-specs/requirements/{specId}/verify
```

**Query Parameters**
- `evidence_type` (required): Type of evidence (test_case, scenario, integration_test, etc.)
- `evidence_reference` (required): Reference to evidence (test ID, scenario ID, etc.)
- `description` (required): Description of verification

**Response**: RequirementSpec with verification_status = verified

## Test Specs Endpoints

### List Tests
```
GET /api/v1/projects/{projectId}/item-specs/tests
```

**Query Parameters**
- `test_type` (optional): One of unit, integration, e2e, performance, security, accessibility, contract, mutation, fuzz, property
- `is_quarantined` (optional): boolean
- `limit` (optional): Max results
- `offset` (optional): Pagination offset

**Response**
```json
{
  "specs": [
    {
      "id": "test-123",
      "item_id": "item-456",
      "test_type": "unit",
      "test_framework": "jest",
      "test_file_path": "src/__tests__/auth.test.ts",
      "test_function_name": "testLoginFlow",
      "preconditions": ["Mock API server running"],
      "setup_commands": ["npm run setup:test"],
      "teardown_commands": ["npm run cleanup:test"],
      "environment_requirements": { "node_version": "18+", "memory_gb": 4 },
      "test_data_schema": { "user": { "email": "string", "password": "string" } },
      "fixtures": ["user-fixture.json"],
      "parameterized_cases": [
        { "input": "valid_email", "expected": "success" },
        { "input": "invalid_email", "expected": "error" }
      ],
      "total_runs": 500,
      "pass_count": 485,
      "fail_count": 10,
      "skip_count": 5,
      "last_run_at": "2025-01-29T15:30:00Z",
      "last_run_status": "passed",
      "last_run_duration_ms": 245,
      "last_run_error": null,
      "run_history": [],
      "flakiness_score": 0.02,
      "flakiness_window_runs": 20,
      "flaky_patterns": ["network timeout on CI"],
      "is_quarantined": false,
      "quarantine_reason": null,
      "quarantined_at": null,
      "avg_duration_ms": 250,
      "p50_duration_ms": 240,
      "p95_duration_ms": 320,
      "p99_duration_ms": 400,
      "duration_trend": "stable",
      "performance_baseline_ms": 200,
      "performance_threshold_ms": 500,
      "line_coverage": 0.95,
      "branch_coverage": 0.87,
      "mutation_score": 0.92,
      "mcdc_coverage": 0.88,
      "verifies_requirements": ["req-789"],
      "verifies_contracts": ["contract-456"],
      "assertions": ["expect(result).toBe(true)"],
      "depends_on_tests": ["setup-test"],
      "required_services": ["auth-service", "database"],
      "mocked_dependencies": ["external-api"],
      "maintenance_score": 0.85,
      "suggested_actions": ["Update test data", "Add performance check"],
      "spec_metadata": { "owner": "qa-team" },
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-29T15:30:00Z"
    }
  ],
  "total": 342
}
```

### Get Test
```
GET /api/v1/projects/{projectId}/item-specs/tests/{specId}
```

**Response**: Single TestSpec object

### Get Test by Item
```
GET /api/v1/projects/{projectId}/item-specs/tests/by-item/{itemId}
```

**Response**: Single TestSpec object

### Flaky Tests
```
GET /api/v1/projects/{projectId}/item-specs/tests/flaky
```

**Query Parameters**
- `threshold` (optional, default 0.2): Flakiness score threshold
- `limit` (optional, default 50): Maximum results

**Response**
```json
{
  "specs": [...flaky test specs...],
  "total": 8
}
```

### Quarantined Tests
```
GET /api/v1/projects/{projectId}/item-specs/tests/quarantined
```

**Query Parameters**
- `limit` (optional): Maximum results

**Response**
```json
{
  "specs": [...quarantined test specs...],
  "total": 3
}
```

### Test Health Report
```
GET /api/v1/projects/{projectId}/item-specs/tests/health-report
```

**Response**
```json
{
  "total_tests": 342,
  "flaky_count": 8,
  "quarantined_count": 3,
  "total_runs": 5000,
  "pass_rate": 0.965,
  "average_duration_ms": 1250,
  "health_score": 0.92
}
```

### Create Test
```
POST /api/v1/projects/{projectId}/item-specs/tests
```

**Request Body**
```json
{
  "item_id": "item-456",
  "test_type": "unit",
  "test_framework": "jest",
  "test_file_path": "src/__tests__/auth.test.ts",
  "test_function_name": "testLoginFlow",
  "preconditions": ["Mock API server running"],
  "setup_commands": ["npm run setup:test"],
  "teardown_commands": ["npm run cleanup:test"],
  "environment_requirements": {},
  "verifies_requirements": ["req-789"],
  "verifies_contracts": [],
  "performance_baseline_ms": 200,
  "performance_threshold_ms": 500,
  "spec_metadata": {}
}
```

**Response**: Created TestSpec object (201 Created)

### Update Test
```
PATCH /api/v1/projects/{projectId}/item-specs/tests/{specId}
```

**Request Body**: Any subset of TestSpec fields

**Response**: Updated TestSpec object

### Delete Test
```
DELETE /api/v1/projects/{projectId}/item-specs/tests/{specId}
```

**Response**: 204 No Content

### Record Test Run
```
POST /api/v1/projects/{projectId}/item-specs/tests/{specId}/record-run
```

**Query Parameters**
- `status` (required): One of passed, failed, skipped, blocked, flaky, timeout, error
- `duration_ms` (required): Execution duration in milliseconds
- `error_message` (optional): Error message if failed
- `environment` (optional): Environment where test ran

**Response**: Updated TestSpec with updated run history and metrics

### Quarantine Test
```
POST /api/v1/projects/{projectId}/item-specs/tests/{specId}/quarantine
```

**Query Parameters**
- `reason` (required): Reason for quarantine

**Response**: Updated TestSpec with is_quarantined = true

### Unquarantine Test
```
POST /api/v1/projects/{projectId}/item-specs/tests/{specId}/unquarantine
```

**Response**: Updated TestSpec with is_quarantined = false

## Epic Specs Endpoints

### List Epics
```
GET /api/v1/projects/{projectId}/item-specs/epics
```

**Query Parameters**
- `status` (optional): One of backlog, in_progress, completed, archived
- `limit`, `offset` (optional): Pagination

**Response**
```json
{
  "specs": [{ ...EpicSpec... }],
  "total": 25
}
```

### Get Epic
```
GET /api/v1/projects/{projectId}/item-specs/epics/{specId}
```

### Get Epic by Item
```
GET /api/v1/projects/{projectId}/item-specs/epics/by-item/{itemId}
```

### Create Epic
```
POST /api/v1/projects/{projectId}/item-specs/epics
```

**Request Body**
```json
{
  "item_id": "item-123",
  "epic_name": "Authentication System Overhaul",
  "business_value": 95,
  "target_release": "v2.0",
  "objectives": ["Improve security", "Reduce latency"],
  "success_criteria": ["Pass security audit"],
  "stakeholders": ["security-lead@example.com"],
  "constraints": ["Must use OAuth 2.0"],
  "assumptions": ["Budget approved"],
  "spec_metadata": {}
}
```

### Update Epic
```
PATCH /api/v1/projects/{projectId}/item-specs/epics/{specId}
```

### Delete Epic
```
DELETE /api/v1/projects/{projectId}/item-specs/epics/{specId}
```

## User Story Specs Endpoints

### List User Stories
```
GET /api/v1/projects/{projectId}/item-specs/user-stories
```

**Query Parameters**
- `status` (optional): One of backlog, ready, in_progress, review, done, archived
- `epic_id` (optional): Filter by parent epic
- `limit`, `offset` (optional): Pagination

### Get User Story
```
GET /api/v1/projects/{projectId}/item-specs/user-stories/{specId}
```

### Get User Story by Item
```
GET /api/v1/projects/{projectId}/item-specs/user-stories/by-item/{itemId}
```

### Create User Story
```
POST /api/v1/projects/{projectId}/item-specs/user-stories
```

**Request Body**
```json
{
  "item_id": "item-123",
  "as_a": "developer",
  "i_want": "to integrate SSO",
  "so_that": "users can login with corporate credentials",
  "story_points": 8,
  "acceptance_criteria": [
    { "criterion": "OIDC provider configured" },
    { "criterion": "User mapping completed" }
  ],
  "definition_of_done": ["Code reviewed", "Tests passing"],
  "priority": 1,
  "parent_epic": "epic-456",
  "spec_metadata": {}
}
```

### Update User Story
```
PATCH /api/v1/projects/{projectId}/item-specs/user-stories/{specId}
```

### Delete User Story
```
DELETE /api/v1/projects/{projectId}/item-specs/user-stories/{specId}
```

## Task Specs Endpoints

### List Tasks
```
GET /api/v1/projects/{projectId}/item-specs/tasks
```

**Query Parameters**
- `status` (optional): One of todo, in_progress, review, done, blocked
- `story_id` (optional): Filter by parent story

### Get Task
```
GET /api/v1/projects/{projectId}/item-specs/tasks/{specId}
```

### Get Task by Item
```
GET /api/v1/projects/{projectId}/item-specs/tasks/by-item/{itemId}
```

### Create Task
```
POST /api/v1/projects/{projectId}/item-specs/tasks
```

**Request Body**
```json
{
  "item_id": "item-123",
  "task_title": "Implement OAuth provider integration",
  "description": "Configure and test OAuth 2.0 provider",
  "priority": 1,
  "estimated_hours": 4,
  "parent_story": "story-456",
  "dependencies": ["task-789"],
  "spec_metadata": {}
}
```

### Update Task
```
PATCH /api/v1/projects/{projectId}/item-specs/tasks/{specId}
```

### Delete Task
```
DELETE /api/v1/projects/{projectId}/item-specs/tasks/{specId}
```

## Defect Specs Endpoints

### List Defects
```
GET /api/v1/projects/{projectId}/item-specs/defects
```

**Query Parameters**
- `severity` (optional): One of critical, major, minor, trivial
- `status` (optional): One of new, assigned, in_progress, resolved, verified, closed, reopened
- `limit`, `offset` (optional): Pagination

### Get Defect
```
GET /api/v1/projects/{projectId}/item-specs/defects/{specId}
```

### Get Defect by Item
```
GET /api/v1/projects/{projectId}/item-specs/defects/by-item/{itemId}
```

### Create Defect
```
POST /api/v1/projects/{projectId}/item-specs/defects
```

**Request Body**
```json
{
  "item_id": "item-123",
  "defect_title": "Login fails on Safari",
  "description": "OIDC callback not processed",
  "severity": "critical",
  "environment": "production",
  "steps_to_reproduce": ["1. Open Safari", "2. Click Login"],
  "expected_behavior": "User logged in",
  "actual_behavior": "Blank page",
  "priority": 1,
  "reported_by": "qa-team@example.com",
  "spec_metadata": {}
}
```

### Update Defect
```
PATCH /api/v1/projects/{projectId}/item-specs/defects/{specId}
```

### Delete Defect
```
DELETE /api/v1/projects/{projectId}/item-specs/defects/{specId}
```

## Common Response Codes

- `200 OK`: Successful GET, PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid input
- `403 Forbidden`: Unauthorized access
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Common Error Response

```json
{
  "error": {
    "message": "Failed to create requirement spec",
    "code": "INVALID_INPUT",
    "details": {
      "field": "risk_level",
      "issue": "Must be one of: critical, high, medium, low, minimal"
    }
  }
}
```

## Header Requirements

All requests should include:
```
Content-Type: application/json
X-Bulk-Operation: true (for list endpoints to skip rate limiting)
```

## Implementation Notes

1. All timestamps should be ISO 8601 format
2. All IDs are strings (UUIDs recommended)
3. All arrays can be empty
4. Pagination uses limit/offset (not page-based)
5. Filter parameters are optional
6. Partial updates (PATCH) only update provided fields
7. Cascading deletes should be handled by backend
8. Timestamps are auto-generated on create/update
