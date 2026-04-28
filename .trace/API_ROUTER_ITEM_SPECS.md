# Item Specifications API Router

## Overview

The Item Specifications API Router (`item_specs.py`) provides a comprehensive REST API surface for managing enhanced item specifications across six distinct specification types:

1. **RequirementSpec** - Functional and non-functional requirements with quality analysis
2. **TestSpec** - Test cases with coverage metrics, flakiness tracking, and quarantine management
3. **EpicSpec** - High-level feature groupings with story points and business value
4. **UserStorySpec** - User-centric requirements with acceptance criteria and definition of done
5. **TaskSpec** - Work items with effort estimation and dependency tracking
6. **DefectSpec** - Issues, bugs, and regressions with severity and resolution tracking

## File Location

```
/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/api/routers/item_specs.py
```

## Architecture

### Design Principles

- **Modular Organization**: Separated endpoints for each spec type with consistent patterns
- **Authentication**: All endpoints require `auth_guard` dependency for WorkOS AuthKit integration
- **Validation**: Pydantic schemas for input/output validation
- **Error Handling**: HTTP exception handling with appropriate status codes
- **Documentation**: Comprehensive docstrings on all endpoints
- **Async/Await**: Full async implementation with SQLAlchemy AsyncSession

### Module Structure

```
item_specs.py
├── Response Models (13 models)
├── Input Models (12 models)
├── Router Setup
├── Requirement Spec Endpoints (13 endpoints)
├── Test Spec Endpoints (14 endpoints)
├── Epic Spec Endpoints (5 endpoints)
├── User Story Spec Endpoints (5 endpoints)
├── Task Spec Endpoints (5 endpoints)
├── Defect Spec Endpoints (7 endpoints)
└── Aggregate Statistics Endpoints (4 endpoints)
```

## Response Models

### RequirementSpecResponse
Represents a requirement specification with quality metrics.

**Fields:**
- `id` (str) - Unique identifier
- `item_id` (str) - Associated item
- `project_id` (str) - Associated project
- `requirement_type` (str) - functional, non_functional, constraint
- `risk_level` (str) - low, medium, high, critical
- `verification_status` (str) - unverified, verified, rejected
- `quality_score` (float) - 0-100 quality assessment
- `impact_score` (float, optional) - 0-100 impact assessment
- `traceability_index` (float) - Traceability score
- `acceptance_criteria` (str) - Acceptance criteria text
- `verification_evidence` (list, optional) - Evidence artifacts
- `created_at` (datetime) - Creation timestamp
- `updated_at` (datetime) - Last update timestamp

### TestSpecResponse
Represents a test specification with execution metrics.

**Fields:**
- `id` (str) - Unique identifier
- `item_id` (str) - Associated item
- `project_id` (str) - Associated project
- `test_type` (str) - unit, integration, e2e, performance, security
- `coverage_percentage` (float) - Code coverage
- `pass_rate` (float) - Pass rate percentage
- `flakiness_score` (float) - Flakiness assessment
- `is_quarantined` (bool) - Quarantine status
- `quarantine_reason` (str, optional) - Reason if quarantined
- `last_run` (datetime, optional) - Last execution time
- `average_duration_ms` (float) - Average execution time

### EpicSpecResponse
Represents an epic specification with planning metrics.

**Fields:**
- `id` (str) - Unique identifier
- `item_id` (str) - Associated item
- `epic_type` (str) - Type classification
- `story_points` (int, optional) - Story point estimation
- `business_value` (str) - low, medium, high, critical
- `timeline` (str, optional) - Timeline description
- `dependencies` (list) - Dependent item IDs
- `child_items` (list) - Child item IDs
- `completion_percentage` (float) - Progress percentage

### UserStorySpecResponse
Represents a user story specification with acceptance criteria.

**Fields:**
- `id` (str) - Unique identifier
- `item_id` (str) - Associated item
- `user_persona` (str) - User persona description
- `business_value` (str) - Business value statement
- `acceptance_criteria` (list) - AC items
- `story_points` (int, optional) - Effort estimation
- `priority` (str) - low, medium, high, critical
- `dependencies` (list) - Dependent item IDs
- `definition_of_done` (list) - DoD items
- `test_coverage` (float, optional) - Test coverage percentage

### TaskSpecResponse
Represents a task specification with effort tracking.

**Fields:**
- `id` (str) - Unique identifier
- `item_id` (str) - Associated item
- `task_type` (str) - Task type classification
- `effort_estimate_hours` (float) - Estimated effort
- `actual_effort_hours` (float, optional) - Actual effort
- `subtasks` (list) - Subtask IDs
- `assigned_to` (str, optional) - Assignee
- `due_date` (datetime, optional) - Due date
- `dependencies` (list) - Dependent task IDs
- `completion_percentage` (float) - Progress percentage

### DefectSpecResponse
Represents a defect specification with tracking info.

**Fields:**
- `id` (str) - Unique identifier
- `item_id` (str) - Associated item
- `defect_type` (str) - bug, regression, issue
- `severity` (str) - trivial, minor, major, critical, blocker
- `reproduced` (bool) - Reproducibility status
- `reproduction_steps` (list) - Steps to reproduce
- `root_cause` (str, optional) - Root cause analysis
- `affected_components` (list) - Affected component IDs
- `related_defects` (list) - Related defect IDs
- `resolution_status` (str) - open, in_progress, resolved, closed, deferred

### Aggregate Statistics Models

#### RequirementQualityStats
- `total_requirements` - Total count
- `verified_count` - Verified count
- `verification_rate` - Verification percentage
- `average_quality_score` - Quality average
- `high_risk_count` - High risk items
- `average_traceability` - Traceability score

#### TestHealthStats
- `total_tests` - Total count
- `passing_tests` - Passing count
- `failing_tests` - Failing count
- `quarantined_tests` - Quarantined count
- `average_pass_rate` - Pass rate percentage
- `average_coverage` - Coverage percentage
- `flaky_test_count` - Flaky test count
- `average_duration_ms` - Average duration

#### DefectMetrics
- `total_defects` - Total count
- `open_defects` - Open count
- `closed_defects` - Closed count
- `blocker_count` - Blocker count
- `critical_count` - Critical count
- `average_resolution_time_hours` - Average resolution time

## Endpoints by Type

### Requirement Spec Endpoints (13 total)

#### CRUD Operations
- `POST /item-specs/requirements` - Create requirement spec
- `GET /item-specs/requirements/{spec_id}` - Get by ID
- `GET /item-specs/requirements/by-item/{item_id}` - Get by item ID
- `GET /item-specs/requirements` - List with filters
- `PATCH /item-specs/requirements/{spec_id}` - Update
- `DELETE /item-specs/requirements/{spec_id}` - Delete

#### Analysis Operations
- `POST /item-specs/requirements/{spec_id}/analyze-quality` - Quality analysis
- `POST /item-specs/requirements/{spec_id}/analyze-impact` - Impact analysis
- `POST /item-specs/requirements/{spec_id}/verify` - Mark as verified

#### Specialized Queries
- `GET /item-specs/requirements/unverified` - Get unverified
- `GET /item-specs/requirements/high-risk` - Get high-risk

### Test Spec Endpoints (14 total)

#### CRUD Operations
- `POST /item-specs/tests` - Create test spec
- `GET /item-specs/tests/{spec_id}` - Get by ID
- `GET /item-specs/tests/by-item/{item_id}` - Get by item ID
- `GET /item-specs/tests` - List with filters
- `PATCH /item-specs/tests/{spec_id}` - Update
- `DELETE /item-specs/tests/{spec_id}` - Delete

#### Execution & Metrics
- `POST /item-specs/tests/{spec_id}/record-run` - Record test execution
- `POST /item-specs/tests/{spec_id}/quarantine` - Quarantine flaky test
- `POST /item-specs/tests/{spec_id}/unquarantine` - Re-enable test

#### Specialized Queries
- `GET /item-specs/tests/flaky` - Get flaky tests (threshold-based)
- `GET /item-specs/tests/health-report` - Get health metrics

### Epic Spec Endpoints (5 total)

- `POST /item-specs/epics` - Create epic
- `GET /item-specs/epics/{spec_id}` - Get by ID
- `GET /item-specs/epics` - List with filters
- `PATCH /item-specs/epics/{spec_id}` - Update
- `DELETE /item-specs/epics/{spec_id}` - Delete

### User Story Spec Endpoints (5 total)

- `POST /item-specs/stories` - Create user story
- `GET /item-specs/stories/{spec_id}` - Get by ID
- `GET /item-specs/stories` - List with filters
- `PATCH /item-specs/stories/{spec_id}` - Update
- `DELETE /item-specs/stories/{spec_id}` - Delete

### Task Spec Endpoints (5 total)

- `POST /item-specs/tasks` - Create task
- `GET /item-specs/tasks/{spec_id}` - Get by ID
- `GET /item-specs/tasks` - List with filters
- `PATCH /item-specs/tasks/{spec_id}` - Update
- `DELETE /item-specs/tasks/{spec_id}` - Delete

### Defect Spec Endpoints (7 total)

#### CRUD Operations
- `POST /item-specs/defects` - Create defect
- `GET /item-specs/defects/{spec_id}` - Get by ID
- `GET /item-specs/defects` - List with filters
- `PATCH /item-specs/defects/{spec_id}` - Update
- `DELETE /item-specs/defects/{spec_id}` - Delete

#### Specialized Queries
- `GET /item-specs/defects/critical` - Get critical/blocker defects

### Aggregate Statistics Endpoints (4 total)

- `GET /item-specs/stats` - Get all statistics
- `GET /item-specs/requirements/quality-stats` - Requirement quality
- `GET /item-specs/tests/health-stats` - Test health
- `GET /item-specs/defects/metrics` - Defect metrics

## Authentication & Authorization

All endpoints require authentication via `auth_guard` dependency:

```python
@router.get("/requirements")
async def list_requirement_specs(
    project_id: str = Path(...),
    claims: dict = Depends(auth_guard),  # Enforces authentication
    db: AsyncSession = Depends(get_db),
):
```

The `auth_guard` dependency:
- Validates WorkOS AuthKit JWT tokens
- Supports API key authentication
- Sets RLS context for database row-level security
- Returns authentication claims for audit logging

## Input Validation

All POST/PATCH operations use Pydantic schemas for validation:

### RequirementSpecCreate
```python
{
    "item_id": "item_123",
    "requirement_type": "functional",  # Enum validation
    "risk_level": "high",              # Enum validation
    "acceptance_criteria": "Must satisfy...",
    "metadata": {}                      # Optional custom data
}
```

### TestSpecCreate
```python
{
    "item_id": "item_456",
    "test_type": "unit",               # Enum validation
    "coverage_percentage": 85.5,        # Range validation
    "metadata": {}
}
```

## Error Handling

Standard HTTP error responses:

| Status | Scenario | Example |
|--------|----------|---------|
| 200 | Success (GET, PATCH) | Resource returned |
| 201 | Created (POST) | New resource created |
| 204 | Deleted (DELETE) | Resource deleted |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid auth |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Database/service error |

Example error response:
```json
{
    "detail": "Requirement spec not found"
}
```

## Implementation Notes

### Current State

The router is **scaffolded and ready for service layer implementation**. All endpoints:
- Have proper request/response models
- Include authentication and validation
- Have comprehensive docstrings
- Return 501 "Service implementation pending"
- Are structured for async/await patterns

### Service Layer Integration

Each endpoint currently returns:
```python
raise HTTPException(status_code=501, detail="Service implementation pending")
```

To implement, replace with actual service calls:

```python
# Example implementation pattern
service = RequirementSpecService(db)
try:
    spec = await service.create_spec(**data.model_dump())
    await db.commit()
    return spec
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

### Required Service Classes

The router expects these service classes (to be implemented):

1. `RequirementSpecService`
   - `create_spec()` - Create requirement
   - `get_spec()` - Retrieve requirement
   - `list_specs()` - List with filters
   - `update_spec()` - Update requirement
   - `delete_spec()` - Delete requirement
   - `analyze_quality()` - Quality analysis
   - `analyze_impact()` - Impact analysis
   - `verify_requirement()` - Record verification

2. `TestSpecService`
   - `create_spec()` - Create test
   - `get_spec()` - Retrieve test
   - `list_specs()` - List with filters
   - `record_run()` - Record execution
   - `quarantine()` - Quarantine test
   - `unquarantine()` - Re-enable test
   - `get_flaky_tests()` - Find flaky tests
   - `get_health_report()` - Aggregate metrics

3. `EpicSpecService` - Basic CRUD
4. `UserStorySpecService` - Basic CRUD
5. `TaskSpecService` - Basic CRUD
6. `DefectSpecService` - CRUD + specialized queries

### Database Access Pattern

All services should follow the pattern:

```python
class RequirementSpecService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RequirementSpecRepository(db)

    async def create_spec(self, **data) -> RequirementSpec:
        # Validation and business logic
        return await self.repo.create(data)
```

## Registration in Main Router

To register this router with the main FastAPI app:

```python
# In src/tracertm/api/main.py
from tracertm.api.routers.item_specs import router as item_specs_router

app.include_router(item_specs_router)
```

This will register all endpoints under `/api/v1/item-specs/` prefix.

## Testing Strategy

### Unit Tests (Vitest)
- Pydantic schema validation
- Enum value validation
- Range validation for numeric fields

### API Integration Tests (Playwright API)
- CRUD operations for each spec type
- Authentication enforcement
- Error handling

### E2E Tests (Playwright Workflows)
- Create requirement and analyze quality
- Create test and record runs
- Create epic with child items
- Create user story and verify acceptance criteria
- Create task with effort tracking
- Create defect and track resolution

## Example Usage

### Create a Requirement Spec
```bash
POST /item-specs/requirements
Authorization: Bearer <token>
Content-Type: application/json

{
    "item_id": "item_abc123",
    "requirement_type": "functional",
    "risk_level": "high",
    "acceptance_criteria": "User must be able to log in with email and password"
}
```

### List Requirements with Filters
```bash
GET /item-specs/requirements?risk_level=high&verification_status=unverified&limit=50
Authorization: Bearer <token>
```

### Record Test Execution
```bash
POST /item-specs/tests/test_spec_123/record-run
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "passed",
    "duration_ms": 245,
    "environment": "ci"
}
```

### Get Test Health Report
```bash
GET /item-specs/tests/health-report
Authorization: Bearer <token>
```

Response:
```json
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

## File Statistics

- **Total Lines**: 2,122
- **Response Models**: 13
- **Input Models**: 12
- **Endpoints**: 53
- **Spec Types Supported**: 6

## Related Files

- Model Classes: `src/tracertm/models/item*.py`
- Schemas: `src/tracertm/schemas/item_spec.py` (to be created)
- Services: `src/tracertm/services/item_spec_*.py` (to be created)
- Repositories: `src/tracertm/repositories/item_spec_*.py` (to be created)
- Main API: `src/tracertm/api/main.py`

## Next Steps

1. Create schema classes in `schemas/item_spec.py`
2. Create model classes for database tables
3. Implement service layer for each spec type
4. Implement repositories for data access
5. Create migration files for database schema
6. Write comprehensive test suites
7. Register router in main FastAPI app
