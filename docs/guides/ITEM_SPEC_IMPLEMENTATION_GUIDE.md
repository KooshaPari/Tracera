# Item Specification Repository Layer - Implementation Guide

## Overview

This document describes the comprehensive repository layer for enhanced Item specifications in TraceRTM. The implementation provides a complete data access layer for six specification types with specialized operations, batch processing, and quality metrics tracking.

## Files Created

### 1. Models: `/src/tracertm/models/item_spec.py` (27 KB)
Defines six SQLAlchemy ORM models for different item specification types:

#### Models Included:

**RequirementSpec**
- Tracks detailed requirement information with quality metrics
- Fields: requirement_type, constraint_type, objective, acceptance_criteria, risk_level
- Quality metrics: ambiguity_score, completeness_score, testability_score, overall_quality_score
- Volatility tracking: volatility_index, change_count, last_changed_at
- Verification: verification_status, verified_at, verified_by, verification_evidence
- WSJF scoring: business_value, time_criticality, risk_reduction, wsjf_score, complexity_estimate
- Indexes: item_id, (project_id, requirement_type), risk_level, verification_status

**TestSpec**
- Comprehensive test specification tracking with execution history
- Fields: test_type, test_framework, language, test_code, setup_code, teardown_code
- Execution stats: total_runs, pass_count, fail_count, skip_count, last_run_*
- Run history: run_history (list of last 50 runs with timestamps, status, duration, errors)
- Flakiness: flakiness_score, flakiness_window_runs, flaky_patterns
- Performance: avg_duration_ms, p50_duration_ms, p95_duration_ms, p99_duration_ms, duration_trend
- Quarantine: is_quarantined, quarantine_reason, quarantined_at
- Coverage: code_coverage_percentage, required_for_release, depends_on_tests
- Indexes: item_id, (project_id, test_type), flakiness_score, is_quarantined

**EpicSpec**
- Epic scope and progress tracking
- Fields: epic_type, status (planned, in_progress, completed, cancelled)
- Scope: scope_description, objectives, success_criteria, out_of_scope
- Team: team_id, epic_owner, stakeholders
- Metrics: user_story_count, completed_story_count, progress_percentage, defect_count
- Timeline: planned_start_date, planned_end_date, actual_start_date, actual_end_date
- Dependencies: depends_on_epics, related_features
- Indexes: item_id, (project_id, epic_type), team_id, status

**UserStorySpec**
- User story with acceptance criteria and estimation
- Fields: as_a, i_want, so_that (standard user story format)
- Content: business_value, acceptance_criteria, acceptance_test_scenarios
- Estimation: story_points, estimated_hours, actual_hours
- Status: status (backlog, ready, in_progress, review, done), assignee_id, reviewer_id
- Epic relationship: epic_item_id (foreign key to items table)
- Dependencies: depends_on_stories, related_stories
- Timeline: created_date, started_date, completed_date
- Indexes: item_id, epic_item_id, assignee_id, status

**TaskSpec**
- Task with progress tracking and blocking status
- Fields: description, acceptance_criteria
- Parent: parent_story_item_id (foreign key to user story item)
- Progress: status (todo, in_progress, review, done), progress_percentage
- Checklist: checklist_items, completed_checklist_items
- Assignment: assignee_id, reviewer_id
- Blocking: is_blocked, blocking_reason, blocks_tasks, blocked_by_tasks
- Estimation: estimated_hours, actual_hours
- Timeline: started_date, completed_date
- Indexes: item_id, parent_story_item_id, assignee_id, is_blocked

**DefectSpec**
- Defect/bug with severity, reproduction, and resolution tracking
- Fields: severity, status, component
- Reproduction: reproducible, steps_to_reproduce, expected_behavior, actual_behavior
- Environment: found_in_version, found_in_environment, affects_versions
- Assignment: reported_by, assigned_to, assigned_at
- Resolution: resolution_type (fixed, duplicate, wontfix, invalid), resolution_notes, resolved_by, resolved_at
- Reopening: reopen_reason, reopened_at, reopen_count
- Relationships: related_defects, related_requirement_ids, related_test_ids
- Evidence: attachments, screenshots, logs
- Indexes: item_id, severity, status, component, assigned_to

## Shared Features Across All Models

1. **Optimistic Locking**: version column with SQLAlchemy mapper support
2. **Soft Delete**: deleted_at column with timezone support
3. **Timestamps**: created_at and updated_at via TimestampMixin
4. **Metadata**: spec_metadata JSON column for flexible extensibility
5. **Foreign Keys**: item_id and project_id with CASCADE delete
6. **Type Safety**: Enum classes for all status/type fields

### Enums Provided:

```python
RequirementType: UBIQUITOUS, FUNCTIONAL, NON_FUNCTIONAL, CONSTRAINT, QUALITY
ConstraintType: HARD, SOFT, PREFERENCE
RiskLevel: CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
VerificationStatus: UNVERIFIED, PENDING, VERIFIED, FAILED, SUPERSEDED
TestType: UNIT, INTEGRATION, E2E, PERFORMANCE, SECURITY, SMOKE, REGRESSION, ACCEPTANCE
EpicType: FEATURE, CAPABILITY, INITIATIVE, PROGRAM
DefectSeverity: BLOCKER, CRITICAL, MAJOR, MINOR, TRIVIAL
DefectStatus: NEW, ASSIGNED, IN_PROGRESS, TESTING, VERIFIED, CLOSED, REOPENED
```

---

### 2. Repositories: `/src/tracertm/repositories/item_spec_repository.py` (42 KB)

Comprehensive repository layer with specialized operations for each spec type.

## Repository Classes

### BaseSpecRepository
Provides common CRUD operations inherited by all spec repositories:

```python
# Core operations
async def get_by_id(spec_id: str) -> Optional[Any]
async def get_by_item_id(item_id: str) -> Optional[Any]
async def update(spec_id: str, **updates: Any) -> Any
async def delete(spec_id: str) -> bool  # Soft delete
async def restore(spec_id: str) -> Any  # Restore from soft delete

# Batch operations
async def batch_update(updates: dict[str, dict[str, Any]]) -> list[Any]
async def batch_delete(spec_ids: list[str]) -> int
async def get_active_count_by_project(project_id: str) -> int
```

### RequirementSpecRepository
Specialized operations for requirements:

```python
# Create
async def create(item_id, requirement_type, constraint_type, **kwargs) -> RequirementSpec

# Query
async def list_by_project(project_id, requirement_type=None, risk_level=None,
                         verification_status=None, limit=100, offset=0) -> list
async def get_unverified_by_project(project_id, limit=100) -> list
async def get_high_risk_by_project(project_id, limit=100) -> list
async def get_by_risk_level_and_status(project_id, risk_level, verification_status) -> list

# Quality and Scoring
async def update_quality_scores(spec_id, quality_scores, ambiguity_score,
                               completeness_score, testability_score,
                               overall_quality_score, quality_issues) -> RequirementSpec

# Volatility and Change Tracking
async def update_volatility(spec_id, volatility_index, change_count) -> RequirementSpec

# Verification
async def verify(spec_id, verified_by, evidence: dict) -> RequirementSpec

# WSJF Calculation
async def calculate_wsjf(spec_id) -> Optional[float]
```

**Key Methods Explained:**

- `update_quality_scores()`: Tracks ambiguity, completeness, testability, and overall quality
- `update_volatility()`: Records requirement changes and calculates volatility index
- `verify()`: Records verification with evidence for traceability
- `calculate_wsjf()`: Computes Weighted Shortest Job First score for prioritization
- `get_high_risk_by_project()`: Returns critical and high-risk requirements sorted by WSJF

### TestSpecRepository
Advanced test execution tracking and flakiness detection:

```python
# Create
async def create(item_id, test_type=TestType.UNIT, **kwargs) -> TestSpec

# Query
async def list_by_project(project_id, test_type=None, is_quarantined=None,
                         limit=100, offset=0) -> list
async def get_flaky_tests(project_id, threshold=0.2, limit=50) -> list
async def get_by_test_type_and_status(project_id, test_type, limit=100) -> list
async def get_slowest_tests(project_id, limit=20) -> list

# Execution Tracking
async def record_run(spec_id, status, duration_ms, error_message=None,
                    environment=None) -> TestSpec
# - Updates pass/fail/skip counts
# - Records to run_history (keeps last 50)
# - Recalculates flakiness and performance metrics automatically

# Flakiness Detection
async def _recalculate_flakiness(spec) -> None
# - Analyzes last N runs (window_runs)
# - Counts status transitions
# - Detects patterns (high_transition_rate if > 30%)

# Performance Analysis
async def _recalculate_performance(spec) -> None
# - Calculates avg, p50, p95, p99 duration
# - Determines trend (increasing, decreasing, stable)

# Quarantine Management
async def quarantine(spec_id, reason) -> TestSpec
async def unquarantine(spec_id) -> TestSpec
```

**Key Metrics:**

- **Flakiness Score**: Computed as transitions / (runs - 1) in recent window
- **Duration Trend**: Increasing (>1.1x), stable, or decreasing (<0.9x)
- **Percentiles**: P50, P95, P99 for performance analysis
- **Run History**: Last 50 runs with timestamp, status, duration, error, environment

### EpicSpecRepository
Epic scope and team management:

```python
# Create
async def create(item_id, epic_type=EpicType.FEATURE, **kwargs) -> EpicSpec

# Query
async def list_by_project(project_id, epic_type=None, status=None,
                         limit=100, offset=0) -> list
async def get_by_team(project_id, team_id, limit=50) -> list
async def get_in_progress(project_id, limit=50) -> list

# Metrics Update
async def update_metrics(spec_id, user_story_count=None, completed_story_count=None,
                        defect_count=None, progress_percentage=None) -> EpicSpec
```

### UserStorySpecRepository
User story with epic relationships:

```python
# Create
async def create(item_id, **kwargs) -> UserStorySpec

# Query
async def list_by_project(project_id, status=None, limit=100, offset=0) -> list
async def get_by_epic(epic_item_id, limit=100) -> list
async def get_by_assignee(project_id, assignee_id, limit=50) -> list

# Content Management
async def update_acceptance_criteria(spec_id, acceptance_criteria: list) -> UserStorySpec
```

### TaskSpecRepository
Task progress and blocking status:

```python
# Create
async def create(item_id, **kwargs) -> TaskSpec

# Query
async def list_by_project(project_id, status=None, limit=100, offset=0) -> list
async def get_by_parent_story(story_item_id, limit=100) -> list
async def get_blocked_tasks(project_id, limit=50) -> list
async def get_by_assignee(project_id, assignee_id, limit=50) -> list

# Progress Management
async def update_progress(spec_id, progress_percentage: float,
                         completed_checklist_items=None) -> TaskSpec
```

### DefectSpecRepository
Defect lifecycle management with severity and resolution:

```python
# Create
async def create(item_id, severity=DefectSeverity.MAJOR,
                status=DefectStatus.NEW, **kwargs) -> DefectSpec

# Query
async def list_by_project(project_id, severity=None, status=None,
                         limit=100, offset=0) -> list
async def get_critical_defects(project_id, limit=50) -> list
async def get_blockers(project_id, limit=50) -> list
async def get_by_status(project_id, status, limit=100) -> list
async def get_by_component(project_id, component, limit=100) -> list
async def get_by_assignee(project_id, assignee_id, limit=50) -> list

# Lifecycle Management
async def assign_defect(spec_id, assigned_to) -> DefectSpec
# - Sets status to ASSIGNED
# - Records assigned_at timestamp

async def resolve_defect(spec_id, resolution_type, resolution_notes, resolved_by) -> DefectSpec
# - Sets status to CLOSED
# - Records resolution details and timestamp

async def reopen_defect(spec_id, reason) -> DefectSpec
# - Sets status to REOPENED
# - Records reason and increments reopen_count
```

### ItemSpecBatchRepository
Cross-type batch operations:

```python
# Initialization combines all repositories
batch_repo = ItemSpecBatchRepository(session)

# Get all specs for an item
async def get_all_specs_for_item(item_id) -> dict[str, Any]
# Returns: {requirement, test, epic, story, task, defect}

# Get project summary
async def get_project_summary(project_id) -> dict[str, int]
# Returns counts for all spec types

# Cascade delete
async def delete_all_specs_for_item(item_id) -> int
# Soft-deletes all associated specs
```

---

## Usage Examples

### 1. Creating and Managing Requirements

```python
from tracertm.repositories.item_spec_repository import RequirementSpecRepository
from tracertm.models.item_spec import RequirementType, RiskLevel

# Initialize repository
req_repo = RequirementSpecRepository(session)

# Create requirement
req_spec = await req_repo.create(
    item_id="item-123",
    requirement_type=RequirementType.FUNCTIONAL.value,
    objective="User can login with GitHub",
    acceptance_criteria=["OAuth flow initiated", "User profile loaded"],
    risk_level=RiskLevel.MEDIUM.value,
    business_value=8,
    time_criticality=7,
    risk_reduction=6,
    complexity_estimate="M"
)

# Calculate WSJF score
wsjf_score = await req_repo.calculate_wsjf(req_spec.id)
# WSJF = (8 + 7 + 6) / 3 = 7.0

# Update quality metrics
await req_repo.update_quality_scores(
    spec_id=req_spec.id,
    quality_scores={"clarity": 0.9, "completeness": 0.85},
    ambiguity_score=0.1,
    completeness_score=0.85,
    testability_score=0.9,
    overall_quality_score=0.88,
    quality_issues=[]
)

# Verify the requirement
await req_repo.verify(
    spec_id=req_spec.id,
    verified_by="user-456",
    evidence={"method": "code_review", "date": "2026-01-29"}
)

# Get unverified requirements
unverified = await req_repo.get_unverified_by_project("project-789")

# Get high-risk requirements
high_risk = await req_repo.get_high_risk_by_project("project-789", limit=10)
```

### 2. Tracking Test Execution and Flakiness

```python
from tracertm.repositories.item_spec_repository import TestSpecRepository
from tracertm.models.item_spec import TestType

# Initialize repository
test_repo = TestSpecRepository(session)

# Create test specification
test_spec = await test_repo.create(
    item_id="item-auth-test",
    test_type=TestType.INTEGRATION.value,
    test_framework="pytest",
    language="python",
    test_code="def test_oauth_flow(): ...",
    required_for_release=True
)

# Record test runs
await test_repo.record_run(
    spec_id=test_spec.id,
    status="passed",
    duration_ms=523,
    environment="ci"
)

await test_repo.record_run(
    spec_id=test_spec.id,
    status="passed",
    duration_ms=489,
    environment="ci"
)

# After 10+ runs with some failures, flakiness is calculated
await test_repo.record_run(
    spec_id=test_spec.id,
    status="failed",
    duration_ms=1024,
    error_message="Timeout connecting to auth service",
    environment="ci"
)

# Flakiness score is auto-updated based on transitions
# If score > 0.2, quarantine the test
if test_spec.flakiness_score and test_spec.flakiness_score > 0.2:
    await test_repo.quarantine(
        spec_id=test_spec.id,
        reason="Excessive flakiness detected - auth service timeout issues"
    )

# Get all flaky tests
flaky_tests = await test_repo.get_flaky_tests("project-789", threshold=0.2, limit=20)

# Get slowest tests
slow_tests = await test_repo.get_slowest_tests("project-789", limit=10)
# p95, p99 duration can indicate regression

# Unquarantine when issue is fixed
await test_repo.unquarantine(test_spec.id)
```

### 3. Epic and Story Hierarchy

```python
from tracertm.repositories.item_spec_repository import ItemSpecBatchRepository
from tracertm.models.item_spec import EpicType

# Initialize batch repository for cross-type operations
batch_repo = ItemSpecBatchRepository(session)

# Create epic
epic_repo = batch_repo.epics
epic = await epic_repo.create(
    item_id="item-epic-oauth",
    epic_type=EpicType.FEATURE.value,
    scope_description="Implement GitHub OAuth integration",
    objectives=["Enable OAuth login", "Sync user profile"],
    success_criteria=["Login works", "User data synced"],
    team_id="team-backend",
    epic_owner="user-owner"
)

# Create user stories under epic
story_repo = batch_repo.stories
story = await story_repo.create(
    item_id="item-story-oauth-login",
    as_a="developer",
    i_want="to login with GitHub",
    so_that="I don't need to manage credentials",
    acceptance_criteria=[
        "OAuth prompt shown",
        "User redirected to GitHub",
        "Credentials exchanged"
    ],
    story_points=5,
    estimated_hours=8,
    status="in_progress",
    assignee_id="user-dev",
    epic_item_id="item-epic-oauth"
)

# Create tasks under story
task_repo = batch_repo.tasks
task1 = await task_repo.create(
    item_id="item-task-oauth-endpoint",
    description="Implement OAuth token exchange endpoint",
    acceptance_criteria=["POST /oauth/callback works", "Returns JWT"],
    parent_story_item_id="item-story-oauth-login",
    status="in_progress",
    progress_percentage=75,
    assignee_id="user-dev",
    checklist_items=["Write endpoint", "Add tests", "Document API"],
    completed_checklist_items=2,
    estimated_hours=4,
    actual_hours=3.5
)

# Get all stories for epic
stories = await story_repo.get_by_epic("item-epic-oauth", limit=100)

# Get all tasks for story
tasks = await task_repo.get_by_parent_story("item-story-oauth-login", limit=50)

# Update epic metrics after story completion
await epic_repo.update_metrics(
    spec_id=epic.id,
    user_story_count=3,
    completed_story_count=1,
    progress_percentage=33.3
)
```

### 4. Defect Management Lifecycle

```python
from tracertm.repositories.item_spec_repository import DefectSpecRepository
from tracertm.models.item_spec import DefectSeverity, DefectStatus

# Initialize repository
defect_repo = DefectSpecRepository(session)

# Report defect
defect = await defect_repo.create(
    item_id="item-defect-oauth-crash",
    severity=DefectSeverity.CRITICAL.value,
    component="authentication",
    reproducible=True,
    steps_to_reproduce=[
        "Click 'Login with GitHub'",
        "Enter invalid credentials",
        "Observe crash"
    ],
    expected_behavior="Error message displayed",
    actual_behavior="Application crashes",
    found_in_version="0.1.0",
    found_in_environment="staging",
    reported_by="user-qa",
    attachments=[
        {"filename": "crash.log", "url": "s3://...", "type": "text"}
    ]
)

# Assign defect
await defect_repo.assign_defect(
    spec_id=defect.id,
    assigned_to="user-dev"
)

# Record steps during investigation
await defect_repo.update(
    spec_id=defect.id,
    status=DefectStatus.IN_PROGRESS.value
)

# Resolve defect
await defect_repo.resolve_defect(
    spec_id=defect.id,
    resolution_type="fixed",
    resolution_notes="Added input validation in OAuth handler",
    resolved_by="user-dev"
)

# Get critical defects
critical = await defect_repo.get_critical_defects("project-789", limit=10)

# Get all defects for a component
component_defects = await defect_repo.get_by_component(
    "project-789",
    "authentication",
    limit=50
)

# If QA finds issue still present, reopen
await defect_repo.reopen_defect(
    spec_id=defect.id,
    reason="Issue still reproducible in staging"
)
```

### 5. Batch Operations and Project Summaries

```python
from tracertm.repositories.item_spec_repository import ItemSpecBatchRepository

# Initialize batch repository
batch_repo = ItemSpecBatchRepository(session)

# Get project-wide summary
summary = await batch_repo.get_project_summary("project-789")
# Returns:
# {
#     "total_requirements": 42,
#     "total_tests": 156,
#     "total_epics": 5,
#     "total_stories": 28,
#     "total_tasks": 92,
#     "total_defects": 13
# }

# Batch update multiple specs
updates = {
    "spec-1": {"status": "done", "progress_percentage": 100},
    "spec-2": {"status": "in_progress", "progress_percentage": 50},
    "spec-3": {"status": "todo", "progress_percentage": 0}
}
updated_specs = await batch_repo.tasks.batch_update(updates)

# Batch delete (soft delete)
deleted_count = await batch_repo.tasks.batch_delete(["spec-1", "spec-2", "spec-3"])

# Get all specs for an item
all_specs = await batch_repo.get_all_specs_for_item("item-123")
# Returns: {requirement, test, epic, story, task, defect}

# Cascade delete when item is deleted
deleted_spec_count = await batch_repo.delete_all_specs_for_item("item-123")
```

---

## Database Schema

All tables follow consistent patterns:

```sql
-- RequirementSpec table structure
CREATE TABLE requirement_specs (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL UNIQUE,
    project_id VARCHAR(255) NOT NULL,
    requirement_type VARCHAR(50) NOT NULL,
    constraint_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(50),
    volatility_index FLOAT,
    change_count INT DEFAULT 0,
    verification_status VARCHAR(50) DEFAULT 'unverified',
    quality_scores JSON,
    overall_quality_score FLOAT,
    version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    -- Foreign keys
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    -- Indexes for common queries
    INDEX idx_requirement_specs_item_id (item_id),
    INDEX idx_requirement_specs_project_type (project_id, requirement_type),
    INDEX idx_requirement_specs_risk (risk_level),
    INDEX idx_requirement_specs_verification (verification_status)
);

-- TestSpec table structure
CREATE TABLE test_specs (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL UNIQUE,
    project_id VARCHAR(255) NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    total_runs INT DEFAULT 0,
    pass_count INT DEFAULT 0,
    fail_count INT DEFAULT 0,
    skip_count INT DEFAULT 0,
    flakiness_score FLOAT,
    flakiness_window_runs INT DEFAULT 20,
    run_history JSON,
    avg_duration_ms FLOAT,
    p50_duration_ms FLOAT,
    p95_duration_ms FLOAT,
    p99_duration_ms FLOAT,
    is_quarantined BOOLEAN DEFAULT FALSE,
    version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_test_specs_item_id (item_id),
    INDEX idx_test_specs_project_type (project_id, test_type),
    INDEX idx_test_specs_flakiness (flakiness_score),
    INDEX idx_test_specs_quarantine (is_quarantined)
);

-- Similar structure for epic_specs, user_story_specs, task_specs, defect_specs
```

---

## Integration Points

### 1. With Item Model
Each spec has `item_id` foreign key to Items table, enabling:
- Soft delete cascade
- Project scoping via item.project_id
- Status inheritance from item.status

### 2. With Services
```python
from tracertm.repositories.item_spec_repository import ItemSpecBatchRepository

class ItemService:
    def __init__(self, session):
        self.spec_repo = ItemSpecBatchRepository(session)

    async def delete_item(self, item_id: str):
        # Cascade delete all specs
        await self.spec_repo.delete_all_specs_for_item(item_id)
        # Then delete item
        ...
```

### 3. With APIs (tRPC Routers)
```python
from fastapi import APIRouter
from tracertm.repositories.item_spec_repository import RequirementSpecRepository

router = APIRouter(prefix="/requirements", tags=["requirements"])

@router.post("/")
async def create_requirement(item_id: str, spec_data: dict, session: AsyncSession):
    repo = RequirementSpecRepository(session)
    spec = await repo.create(item_id=item_id, **spec_data)
    return spec

@router.get("/project/{project_id}/high-risk")
async def get_high_risk_requirements(project_id: str, session: AsyncSession):
    repo = RequirementSpecRepository(session)
    specs = await repo.get_high_risk_by_project(project_id, limit=50)
    return specs
```

---

## Key Design Patterns

### 1. Async/Await Throughout
All repository methods are async for non-blocking I/O:
```python
spec = await repo.get_by_id(spec_id)
await session.flush()
await session.refresh(spec)
```

### 2. Optimistic Locking
Version column prevents concurrent update conflicts:
```python
spec.version = 1  # Initial
# Another process updates...
spec.version = 2  # Throws StaleDataError if trying to update with old version
```

### 3. Soft Deletes
Preserves audit trail and referential integrity:
```python
spec.deleted_at = datetime.now(UTC)  # Instead of DELETE
# Queries always filter: WHERE deleted_at IS NULL
```

### 4. Calculated Fields
Metrics are computed on-demand or during updates:
```python
# Flakiness computed during record_run
await test_repo.record_run(spec_id, status, duration_ms)
# Automatically recalculates flakiness_score and patterns

# WSJF computed explicitly
wsjf = await req_repo.calculate_wsjf(spec_id)
```

### 5. Batch Operations
Multiple updates in one transaction:
```python
updates = {spec_id_1: {...}, spec_id_2: {...}}
await repo.batch_update(updates)  # Single session.flush()
```

---

## Performance Considerations

### Indexes
All critical query paths have indexes:
- Single-item lookups: `idx_*_item_id`
- Project + type queries: `idx_*_project_type`
- Status/severity filters: `idx_*_status`, `idx_*_severity`
- Complex queries: `idx_*_team`, `idx_*_assignee`

### Query Optimization
- Use `limit` and `offset` for pagination
- Filter early in WHERE clause
- Leverage database indexes
- Use `session.refresh()` after flush for fresh data

### Batch Processing
```python
# Good: Single flush for 100 updates
updates = {id_1: {...}, ..., id_100: {...}}
await repo.batch_update(updates)

# Avoid: Multiple flushes
for id, data in updates.items():
    await repo.update(id, **data)  # Each flushes
```

---

## Migration Strategy

For existing projects, create Alembic migration:

```python
"""Add item specification tables."""

from alembic import op
import sqlalchemy as sa
from tracertm.models.types import JSONType

def upgrade():
    # RequirementSpec table
    op.create_table(
        'requirement_specs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('item_id', sa.String(255), sa.ForeignKey('items.id'), unique=True, nullable=False),
        sa.Column('project_id', sa.String(255), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('requirement_type', sa.String(50), nullable=False),
        # ... other columns
        sa.Index('idx_requirement_specs_item_id', 'item_id'),
        sa.Index('idx_requirement_specs_project_type', 'project_id', 'requirement_type'),
    )
    # ... repeat for other tables

def downgrade():
    op.drop_table('requirement_specs')
    # ... repeat for other tables
```

---

## Testing Strategy

### Unit Tests (Vitest)
Test pure utility functions:
```python
def test_wsjf_calculation():
    wsjf = (8 + 7 + 6) / 3  # business_value + time_criticality + risk_reduction / job_size
    assert wsjf == 7.0
```

### Integration Tests (Playwright API)
Test repositories with real database:
```python
async def test_create_requirement_spec(async_session):
    repo = RequirementSpecRepository(async_session)
    spec = await repo.create(item_id="test-item", requirement_type="functional")
    assert spec.id is not None
    assert spec.verification_status == "unverified"
```

### E2E Tests (Playwright Workflows)
Test complete workflows:
```python
async def test_requirement_verification_workflow(browser, api_client):
    # Create requirement via API
    req = await api_client.post("/requirements", ...)
    # Verify it appears in UI
    await page.goto(f"/requirements/{req.id}")
    await page.click('[data-testid="verify-button"]')
    # Verify status updates
    assert req.verification_status == "verified"
```

---

## Summary

The item specification repository layer provides:

1. **Six specialized models** with comprehensive attributes for different item types
2. **Seven repository classes** with type-specific operations
3. **Batch operations** for efficient bulk updates and deletes
4. **Calculated metrics** for quality, flakiness, performance, and priority
5. **Flexible querying** with project scoping, type filtering, and status filtering
6. **Optimistic locking** for concurrent update safety
7. **Soft deletes** for audit trail preservation
8. **Async/await** throughout for non-blocking I/O
9. **Proper indexing** for query performance
10. **Type safety** with Enum classes and type hints

This provides a complete, production-ready data access layer for managing items across diverse specification types in TraceRTM.
