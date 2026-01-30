# Item Specification Repository - Quick Reference

## Files Location

- **Models**: `/src/tracertm/models/item_spec.py`
- **Repositories**: `/src/tracertm/repositories/item_spec_repository.py`
- **Full Guide**: `ITEM_SPEC_IMPLEMENTATION_GUIDE.md`

## Quick Import

```python
from tracertm.models.item_spec import (
    RequirementSpec, TestSpec, EpicSpec, UserStorySpec, TaskSpec, DefectSpec,
    RequirementType, ConstraintType, RiskLevel, VerificationStatus,
    TestType, EpicType, DefectSeverity, DefectStatus
)

from tracertm.repositories.item_spec_repository import (
    RequirementSpecRepository, TestSpecRepository, EpicSpecRepository,
    UserStorySpecRepository, TaskSpecRepository, DefectSpecRepository,
    ItemSpecBatchRepository
)
```

## Repository Initialization

```python
from sqlalchemy.ext.asyncio import AsyncSession

# Single repository
req_repo = RequirementSpecRepository(session)
test_repo = TestSpecRepository(session)

# Batch repository (all types)
batch_repo = ItemSpecBatchRepository(session)
# Access individual repos: batch_repo.requirements, batch_repo.tests, etc.
```

## Common Operations

### Create

```python
# Requirement
spec = await req_repo.create(
    item_id="item-123",
    requirement_type=RequirementType.FUNCTIONAL.value,
    objective="...",
    acceptance_criteria=["criterion 1", "criterion 2"],
    risk_level=RiskLevel.MEDIUM.value
)

# Test
spec = await test_repo.create(
    item_id="item-test-1",
    test_type=TestType.UNIT.value,
    test_framework="pytest",
    required_for_release=True
)

# Epic
spec = await batch_repo.epics.create(
    item_id="item-epic",
    epic_type=EpicType.FEATURE.value,
    scope_description="...",
    team_id="team-123"
)

# User Story
spec = await batch_repo.stories.create(
    item_id="item-story",
    as_a="user",
    i_want="feature",
    so_that="benefit",
    epic_item_id="item-epic"
)

# Task
spec = await batch_repo.tasks.create(
    item_id="item-task",
    description="...",
    parent_story_item_id="item-story",
    assignee_id="user-123"
)

# Defect
spec = await batch_repo.defects.create(
    item_id="item-defect",
    severity=DefectSeverity.CRITICAL.value,
    component="authentication"
)
```

### Read

```python
# By ID
spec = await req_repo.get_by_id("spec-id")

# By item ID
spec = await req_repo.get_by_item_id("item-123")

# List by project
specs = await req_repo.list_by_project("project-123", limit=50)

# Filtered queries
high_risk = await req_repo.get_high_risk_by_project("project-123")
unverified = await req_repo.get_unverified_by_project("project-123")
flaky = await test_repo.get_flaky_tests("project-123", threshold=0.2)
```

### Update

```python
# Generic update
spec = await req_repo.update(
    spec_id="spec-id",
    risk_level=RiskLevel.HIGH.value,
    status="in_progress"
)

# Specialized updates
await req_repo.update_quality_scores(
    spec_id="spec-id",
    quality_scores={"clarity": 0.9},
    overall_quality_score=0.88
)

await req_repo.update_volatility(
    spec_id="spec-id",
    volatility_index=0.15,
    change_count=3
)

await test_repo.record_run(
    spec_id="spec-id",
    status="passed",
    duration_ms=523
)

await batch_repo.stories.update_acceptance_criteria(
    spec_id="spec-id",
    acceptance_criteria=["criteria 1", "criteria 2"]
)

await batch_repo.tasks.update_progress(
    spec_id="spec-id",
    progress_percentage=75.0
)
```

### Lifecycle Operations

```python
# Verify requirement
await req_repo.verify(
    spec_id="spec-id",
    verified_by="user-456",
    evidence={"method": "review"}
)

# Quarantine flaky test
await test_repo.quarantine(
    spec_id="spec-id",
    reason="Timeout issues detected"
)
await test_repo.unquarantine(spec_id="spec-id")

# Defect lifecycle
await batch_repo.defects.assign_defect(spec_id="spec-id", assigned_to="user-123")
await batch_repo.defects.resolve_defect(
    spec_id="spec-id",
    resolution_type="fixed",
    resolution_notes="...",
    resolved_by="user-456"
)
await batch_repo.defects.reopen_defect(spec_id="spec-id", reason="Still reproducible")
```

### Delete

```python
# Soft delete (sets deleted_at)
deleted = await req_repo.delete(spec_id="spec-id")

# Restore from soft delete
restored = await req_repo.restore(spec_id="spec-id")

# Batch soft delete
count = await req_repo.batch_delete(["spec-1", "spec-2", "spec-3"])

# Cascade delete all specs for item
count = await batch_repo.delete_all_specs_for_item("item-123")
```

## Specialized Methods by Type

### RequirementSpecRepository

```python
# Query methods
await req_repo.list_by_project(project_id, requirement_type, risk_level, verification_status)
await req_repo.get_unverified_by_project(project_id)
await req_repo.get_high_risk_by_project(project_id)
await req_repo.get_by_risk_level_and_status(project_id, risk_level, verification_status)

# Scoring
wsjf = await req_repo.calculate_wsjf(spec_id)  # Returns float

# Verification
await req_repo.verify(spec_id, verified_by, evidence)

# Quality
await req_repo.update_quality_scores(spec_id, quality_scores, ...)

# Volatility
await req_repo.update_volatility(spec_id, volatility_index, change_count)
```

### TestSpecRepository

```python
# Query methods
await test_repo.list_by_project(project_id, test_type, is_quarantined)
await test_repo.get_flaky_tests(project_id, threshold=0.2)
await test_repo.get_slowest_tests(project_id)
await test_repo.get_by_test_type_and_status(project_id, test_type)

# Execution
await test_repo.record_run(spec_id, status, duration_ms, error_message, environment)

# Quarantine
await test_repo.quarantine(spec_id, reason)
await test_repo.unquarantine(spec_id)

# Metrics auto-calculated during record_run:
# - flakiness_score (transitions / (runs - 1))
# - avg/p50/p95/p99 duration
# - duration_trend (increasing/stable/decreasing)
```

### EpicSpecRepository

```python
# Query methods
await epics.list_by_project(project_id, epic_type, status)
await epics.get_by_team(project_id, team_id)
await epics.get_in_progress(project_id)

# Metrics
await epics.update_metrics(
    spec_id,
    user_story_count=N,
    completed_story_count=M,
    progress_percentage=P,
    defect_count=D
)
```

### UserStorySpecRepository

```python
# Query methods
await stories.list_by_project(project_id, status)
await stories.get_by_epic(epic_item_id)
await stories.get_by_assignee(project_id, assignee_id)

# Content
await stories.update_acceptance_criteria(spec_id, acceptance_criteria)
```

### TaskSpecRepository

```python
# Query methods
await tasks.list_by_project(project_id, status)
await tasks.get_by_parent_story(story_item_id)
await tasks.get_blocked_tasks(project_id)
await tasks.get_by_assignee(project_id, assignee_id)

# Progress
await tasks.update_progress(spec_id, progress_percentage, completed_checklist_items)
```

### DefectSpecRepository

```python
# Query methods
await defects.list_by_project(project_id, severity, status)
await defects.get_critical_defects(project_id)
await defects.get_blockers(project_id)
await defects.get_by_status(project_id, status)
await defects.get_by_component(project_id, component)
await defects.get_by_assignee(project_id, assignee_id)

# Lifecycle
await defects.assign_defect(spec_id, assigned_to)
await defects.resolve_defect(spec_id, resolution_type, resolution_notes, resolved_by)
await defects.reopen_defect(spec_id, reason)
```

## Batch Operations

```python
# Get project summary
summary = await batch_repo.get_project_summary("project-123")
# Returns: {total_requirements, total_tests, total_epics, total_stories, total_tasks, total_defects}

# Get all specs for item
specs = await batch_repo.get_all_specs_for_item("item-123")
# Returns: {requirement, test, epic, story, task, defect}

# Batch update
updates = {
    "spec-1": {"status": "done", "progress_percentage": 100},
    "spec-2": {"status": "in_progress", "progress_percentage": 50}
}
updated = await batch_repo.tasks.batch_update(updates)

# Cascade delete
count = await batch_repo.delete_all_specs_for_item("item-123")
```

## Enum Values

### RequirementType
- `UBIQUITOUS` - Universal language requirement
- `FUNCTIONAL` - Feature/capability requirement
- `NON_FUNCTIONAL` - Performance, security, scalability
- `CONSTRAINT` - Limitation or boundary
- `QUALITY` - Quality attribute requirement

### TestType
- `UNIT` - Single component test
- `INTEGRATION` - Component integration test
- `E2E` - End-to-end workflow
- `PERFORMANCE` - Performance/load testing
- `SECURITY` - Security/penetration testing
- `SMOKE` - Quick sanity check
- `REGRESSION` - Prevent breaking existing features
- `ACCEPTANCE` - Acceptance criteria validation

### RiskLevel
- `CRITICAL` - Highest priority/impact
- `HIGH` - Major impact
- `MEDIUM` - Moderate impact
- `LOW` - Minor impact
- `MINIMAL` - Negligible impact

### DefectSeverity
- `BLOCKER` - System unusable
- `CRITICAL` - Major functionality broken
- `MAJOR` - Significant feature broken
- `MINOR` - Minor feature issue
- `TRIVIAL` - Cosmetic/negligible

## Status Values

### Requirement
- `unverified` (default)
- `pending`
- `verified`
- `failed`
- `superseded`

### Test
- `quarantined` (boolean flag)

### Epic
- `planned` (default)
- `in_progress`
- `completed`
- `cancelled`

### UserStory
- `backlog` (default)
- `ready`
- `in_progress`
- `review`
- `done`

### Task
- `todo` (default)
- `in_progress`
- `review`
- `done`

### Defect
- `new` (default)
- `assigned`
- `in_progress`
- `testing`
- `verified`
- `closed`
- `reopened`

## Common Patterns

### Project Dashboard

```python
batch_repo = ItemSpecBatchRepository(session)

# Get summary
summary = await batch_repo.get_project_summary("project-123")

# Get critical items
high_risk_reqs = await req_repo.get_high_risk_by_project("project-123", limit=10)
critical_defects = await defects.get_critical_defects("project-123", limit=10)
blocked_tasks = await tasks.get_blocked_tasks("project-123", limit=10)

dashboard = {
    "summary": summary,
    "alerts": {
        "high_risk_requirements": high_risk_reqs,
        "critical_defects": critical_defects,
        "blocked_tasks": blocked_tasks
    }
}
```

### Quality Reporting

```python
# Get all requirements for project
reqs = await req_repo.list_by_project(project_id="project-123", limit=1000)

# Calculate quality metrics
quality_report = {
    "total": len(reqs),
    "verified": len([r for r in reqs if r.verification_status == "verified"]),
    "unverified": len([r for r in reqs if r.verification_status == "unverified"]),
    "avg_quality_score": sum(r.overall_quality_score or 0 for r in reqs) / len(reqs),
    "high_risk": len([r for r in reqs if r.risk_level == "critical" or r.risk_level == "high"]),
    "high_volatility": len([r for r in reqs if r.volatility_index and r.volatility_index > 0.3])
}
```

### Test Monitoring

```python
# Get all tests for project
tests = await test_repo.list_by_project(project_id="project-123", limit=1000)

# Identify issues
issues = {
    "flaky_tests": [t for t in tests if t.flakiness_score and t.flakiness_score > 0.2],
    "slow_tests": [t for t in tests if t.avg_duration_ms and t.avg_duration_ms > 1000],
    "quarantined": [t for t in tests if t.is_quarantined],
    "regressing": [t for t in tests if t.duration_trend == "increasing"]
}
```

### Defect Triage

```python
# Get new defects
new_defects = await defects.get_by_status("project-123", DefectStatus.NEW.value, limit=100)

# Categorize by severity
by_severity = {
    "blocker": [d for d in new_defects if d.severity == "blocker"],
    "critical": [d for d in new_defects if d.severity == "critical"],
    "major": [d for d in new_defects if d.severity == "major"]
}

# Assign to team
for defect in by_severity["blocker"]:
    await defects.assign_defect(defect.id, assigned_to="team-lead")
```

## Error Handling

```python
try:
    spec = await req_repo.get_by_id("nonexistent")
    if not spec:
        # Handle not found
        pass
except ValueError as e:
    # Handle "not found" errors from update/delete
    print(f"Spec error: {e}")
except Exception as e:
    # Handle database/concurrency errors
    await session.rollback()
    raise
```

## Performance Tips

1. **Use pagination**: `list_by_project(..., limit=100, offset=0)`
2. **Filter early**: Specify type/status in queries, not after fetching
3. **Batch updates**: Use `batch_update()` instead of loop of updates
4. **Leverage indexes**: Query on indexed fields (project_id, status, severity, etc.)
5. **Refresh selectively**: Only call `session.refresh()` when needed

## Testing

```python
# Unit tests
from tests.conftest import async_session

async def test_requirement_creation():
    async with async_session() as session:
        repo = RequirementSpecRepository(session)
        spec = await repo.create(
            item_id="test-item",
            requirement_type=RequirementType.FUNCTIONAL.value
        )
        assert spec.id is not None
        assert spec.verification_status == "unverified"

# E2E tests
async def test_requirement_workflow(browser, api_client):
    # Create via API
    req = await api_client.post("/api/requirements", ...)
    # Verify in UI
    await page.goto(f"/requirements/{req.id}")
    ...
```
