# Item Specs API - Quick Reference

## File Location
```
src/tracertm/api/routers/item_specs.py
```

## Module Summary

Complete REST API router for 6 item specification types with:
- 53 endpoints across all spec types
- Comprehensive validation and error handling
- Full async/await implementation
- WorkOS AuthKit integration
- Pydantic schema validation

## Spec Types

| Type | Endpoint Prefix | Purpose | Key Fields |
|------|-----------------|---------|-----------|
| **RequirementSpec** | `/requirements` | Functional/non-functional requirements | risk_level, verification_status, quality_score |
| **TestSpec** | `/tests` | Test cases with metrics | test_type, coverage_percentage, flakiness_score |
| **EpicSpec** | `/epics` | Feature groupings | story_points, business_value, completion_percentage |
| **UserStorySpec** | `/stories` | User-centric requirements | user_persona, acceptance_criteria, definition_of_done |
| **TaskSpec** | `/tasks` | Work items | effort_estimate_hours, assigned_to, due_date |
| **DefectSpec** | `/defects` | Issues/bugs/regressions | severity, reproduction_steps, resolution_status |

## Endpoint Patterns

### Basic CRUD (all types)
```
POST   /item-specs/{type}              Create
GET    /item-specs/{type}/{id}         Get by ID
GET    /item-specs/{type}              List with filters
PATCH  /item-specs/{type}/{id}         Update
DELETE /item-specs/{type}/{id}         Delete
```

### Requirements-Specific
```
GET    /item-specs/requirements/by-item/{item_id}
POST   /item-specs/requirements/{id}/analyze-quality
POST   /item-specs/requirements/{id}/analyze-impact
POST   /item-specs/requirements/{id}/verify
GET    /item-specs/requirements/unverified
GET    /item-specs/requirements/high-risk
```

### Tests-Specific
```
GET    /item-specs/tests/by-item/{item_id}
POST   /item-specs/tests/{id}/record-run
POST   /item-specs/tests/{id}/quarantine
POST   /item-specs/tests/{id}/unquarantine
GET    /item-specs/tests/flaky
GET    /item-specs/tests/health-report
```

### Defects-Specific
```
GET    /item-specs/defects/critical
```

### Statistics
```
GET    /item-specs/stats
GET    /item-specs/requirements/quality-stats
GET    /item-specs/tests/health-stats
GET    /item-specs/defects/metrics
```

## Response Models

### RequirementSpecResponse
```python
{
    "id": "spec_123",
    "item_id": "item_456",
    "project_id": "proj_789",
    "requirement_type": "functional",
    "risk_level": "high",
    "verification_status": "verified",
    "quality_score": 87.5,
    "impact_score": 92.0,
    "traceability_index": 95.0,
    "acceptance_criteria": "...",
    "verification_evidence": [...],
    "created_at": "2025-01-29T10:00:00Z",
    "updated_at": "2025-01-29T10:30:00Z"
}
```

### TestSpecResponse
```python
{
    "id": "spec_123",
    "item_id": "item_456",
    "project_id": "proj_789",
    "test_type": "unit",
    "coverage_percentage": 85.5,
    "pass_rate": 98.0,
    "flakiness_score": 0.05,
    "is_quarantined": false,
    "quarantine_reason": null,
    "last_run": "2025-01-29T10:30:00Z",
    "average_duration_ms": 125.5,
    "created_at": "2025-01-29T10:00:00Z",
    "updated_at": "2025-01-29T10:30:00Z"
}
```

### TestHealthStats
```python
{
    "total_tests": 450,
    "passing_tests": 425,
    "failing_tests": 15,
    "quarantined_tests": 10,
    "average_pass_rate": 94.4,
    "average_coverage": 87.3,
    "flaky_test_count": 8,
    "average_duration_ms": 120.5,
    "timestamp": "2025-01-29T10:30:00Z"
}
```

## Input Schemas

### RequirementSpecCreate
```python
{
    "item_id": "item_123",
    "requirement_type": "functional",  # functional|non_functional|constraint
    "risk_level": "high",              # low|medium|high|critical
    "acceptance_criteria": "...",
    "metadata": {}                     # optional
}
```

### TestSpecCreate
```python
{
    "item_id": "item_123",
    "test_type": "unit",               # unit|integration|e2e|performance|security
    "coverage_percentage": 85.5,
    "metadata": {}                     # optional
}
```

### Test Run Recording
```python
POST /item-specs/tests/{spec_id}/record-run
{
    "status": "passed",                # passed|failed|skipped|blocked|flaky|timeout|error
    "duration_ms": 245,
    "error_message": null,             # optional
    "environment": "ci"                # optional
}
```

## Authentication

All endpoints require `Authorization: Bearer <token>` header with valid WorkOS AuthKit JWT.

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Common Query Parameters

### List Endpoints
```
?limit=100          (1-500, default 100)
?offset=0           (default 0)
```

### Requirement Filters
```
?requirement_type=functional
?risk_level=high
?verification_status=verified
```

### Test Filters
```
?test_type=unit
?is_quarantined=false
?threshold=0.2              (for flaky tests, 0-1)
```

### Defect Filters
```
?severity=critical          # trivial|minor|major|critical|blocker
?resolution_status=open     # open|in_progress|resolved|closed|deferred
```

## Error Responses

```json
{
    "detail": "Requirement spec not found"
}
```

| Code | Meaning |
|------|---------|
| 400 | Bad request (validation error) |
| 401 | Unauthorized (missing/invalid auth) |
| 404 | Not found (resource doesn't exist) |
| 501 | Service implementation pending |
| 500 | Server error |

## Path Parameters

All path parameters use curly braces:

```python
project_id: str = Path(..., description="Project ID")
spec_id: str = Path(..., description="Spec ID")
item_id: str = Path(..., description="Item ID")
```

## Implementation Checklist

- [ ] Create schemas in `schemas/item_spec.py`
- [ ] Create models in `models/` directory
- [ ] Implement `RequirementSpecService`
- [ ] Implement `TestSpecService`
- [ ] Implement `EpicSpecService`
- [ ] Implement `UserStorySpecService`
- [ ] Implement `TaskSpecService`
- [ ] Implement `DefectSpecService`
- [ ] Create repositories for each type
- [ ] Write database migrations
- [ ] Register router in `api/main.py`
- [ ] Write unit tests
- [ ] Write API integration tests
- [ ] Write E2E workflow tests

## Service Interface Pattern

```python
class RequirementSpecService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RequirementSpecRepository(db)

    async def create_spec(self, **data) -> RequirementSpec:
        # Validate input
        # Create spec
        # Return result

    async def analyze_quality(self, spec_id: str) -> RequirementSpec:
        # Load spec
        # Perform quality analysis
        # Update spec
        # Return updated spec

    async def verify_requirement(
        self, spec_id: str, user_id: str,
        evidence_type: str, evidence_ref: str, desc: str
    ) -> RequirementSpec:
        # Record verification
        # Update status
        # Log audit event
        # Return updated spec
```

## Repository Interface Pattern

```python
class RequirementSpecRepository:
    async def create(self, data: dict) -> RequirementSpec:
        ...

    async def get_by_id(self, spec_id: str) -> RequirementSpec | None:
        ...

    async def list_by_project(
        self, project_id: str,
        requirement_type: str | None = None,
        risk_level: str | None = None,
        verification_status: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[RequirementSpec]:
        ...

    async def update(self, spec_id: str, **data) -> RequirementSpec | None:
        ...

    async def delete(self, spec_id: str) -> bool:
        ...

    async def get_high_risk_by_project(
        self, project_id: str, limit: int = 100
    ) -> list[RequirementSpec]:
        ...

    async def get_unverified_by_project(
        self, project_id: str, limit: int = 100
    ) -> list[RequirementSpec]:
        ...
```

## Status Codes Used

- `201` - Created (POST)
- `200` - OK (GET, PATCH)
- `204` - No Content (DELETE)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error
- `501` - Not Implemented (placeholder)

## Router Registration Example

```python
# In src/tracertm/api/main.py
from tracertm.api.routers.item_specs import router as item_specs_router

app = FastAPI()
app.include_router(item_specs_router)

# Routes will be available at:
# /item-specs/requirements
# /item-specs/tests
# /item-specs/epics
# /item-specs/stories
# /item-specs/tasks
# /item-specs/defects
# /item-specs/stats
```

## Enum Values

### Requirement Type
```
functional
non_functional
constraint
```

### Risk Levels
```
low
medium
high
critical
```

### Verification Status
```
unverified
verified
rejected
```

### Test Types
```
unit
integration
e2e
performance
security
```

### Test Status (for runs)
```
passed
failed
skipped
blocked
flaky
timeout
error
```

### Severity (Defects)
```
trivial
minor
major
critical
blocker
```

### Resolution Status
```
open
in_progress
resolved
closed
deferred
```

### Business Value
```
low
medium
high
critical
```

## Key Features

- **53 Total Endpoints** across 6 spec types
- **Full CRUD Operations** for all types
- **Specialized Queries** for requirements, tests, and defects
- **Aggregated Statistics** endpoints
- **Quality Analysis** for requirements
- **Impact Analysis** for requirements
- **Flakiness Detection** for tests
- **Quarantine Management** for flaky tests
- **Severity Tracking** for defects
- **Comprehensive Validation** via Pydantic
- **Full Authentication** via WorkOS AuthKit
- **Async Implementation** with SQLAlchemy

## Total Metrics

| Metric | Count |
|--------|-------|
| Lines of Code | 2,122 |
| Endpoints | 53 |
| Response Models | 13 |
| Input Schemas | 12 |
| Spec Types | 6 |
| Authentication Methods | 2 (JWT, API Key) |
