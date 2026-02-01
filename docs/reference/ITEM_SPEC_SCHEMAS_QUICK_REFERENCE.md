# Item Spec Schemas - Quick Reference

## Module Location
```python
from tracertm.schemas.item_spec import *
from tracertm.schemas import (
    RequirementSpecCreate, RequirementSpecResponse,
    TestSpecCreate, TestSpecResponse,
    EpicSpecCreate, EpicSpecResponse,
    UserStorySpecCreate, UserStorySpecResponse,
    TaskSpecCreate, TaskSpecResponse,
    DefectSpecCreate, DefectSpecResponse,
    # ... and all related enums and types
)
```

## Enum Quick Reference

| Enum | Values | Use Case |
|------|--------|----------|
| `RequirementType` | UBIQUITOUS, EVENT_DRIVEN, STATE_DRIVEN, OPTIONAL, COMPLEX, UNWANTED | EARS classification |
| `ConstraintType` | HARD, SOFT, OPTIMIZABLE | Constraint strictness |
| `QualityDimension` | COMPLETENESS, CONSISTENCY, CORRECTNESS, UNAMBIGUITY, VERIFIABILITY, TRACEABILITY, FEASIBILITY, NECESSITY, SINGULARITY | Quality assessment |
| `TestType` | UNIT, INTEGRATION, E2E, PERFORMANCE, SECURITY, ACCESSIBILITY, CONTRACT, MUTATION, FUZZ, PROPERTY | Test classification |
| `TestResultStatus` | PASSED, FAILED, SKIPPED, BLOCKED, FLAKY, TIMEOUT, ERROR | Test execution results |
| `VerificationStatus` | UNVERIFIED, PENDING, VERIFIED, FAILED, EXPIRED | Requirement verification state |
| `RiskLevel` | CRITICAL, HIGH, MEDIUM, LOW, MINIMAL | Risk classification |

## Schema Patterns

### Create Schema (Input)
- User-provided fields only
- Required fields have no defaults
- Optional fields: `field: Type | None = None`
- Validation: `Field(..., constraints)`

```python
class XYZSpecCreate(BaseModel):
    item_id: str
    # Required fields
    # Optional fields with | None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### Response Schema (Output)
- Includes all create fields PLUS
- Calculated/derived fields
- Timestamps and IDs
- `model_config = ConfigDict(from_attributes=True)` for ORM

```python
class XYZSpecResponse(BaseModel):
    id: str
    item_id: str
    project_id: str
    # ... input fields ...
    # Calculated fields
    calculated_field: float | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### List Schema (Pagination)
```python
class XYZSpecListResponse(BaseModel):
    total: int
    xyz_specs: list[XYZSpecResponse]
```

## Calculated Fields by Spec Type

### RequirementSpecResponse
```
✓ quality_scores          - Dict of all dimensions
✓ ambiguity_score         - 0-100 (lower = better)
✓ completeness_score      - 0-100
✓ testability_score       - 0-100
✓ overall_quality_score   - 0-100
✓ quality_issues          - List[QualityIssue]
✓ volatility_index        - Change frequency
✓ change_history          - List[ChangeHistoryEntry]
✓ change_propagation_index- Impact metric
✓ wsjf_score              - Weighted Shortest Job First
✓ similar_items           - List[SemanticSimilarity]
✓ auto_tags               - List[str] from AI
✓ complexity_estimate     - "simple"|"moderate"|"complex"
```

### TestSpecResponse
```
✓ total_runs              - Count
✓ pass_count              - Count
✓ fail_count              - Count
✓ skip_count              - Count
✓ last_run_status         - Status enum
✓ run_history             - List[TestRunSummary]
✓ flakiness_score         - 0-100 (lower = better)
✓ flaky_patterns          - List[str]
✓ is_quarantined          - bool
✓ avg_duration_ms         - float
✓ p50/p95/p99_duration_ms - Percentiles
✓ duration_trend          - "improving"|"stable"|"degrading"
✓ line_coverage           - 0-100%
✓ branch_coverage         - 0-100%
✓ mutation_score          - 0-100
✓ mcdc_coverage           - 0-100
✓ test_age_days           - int
✓ maintenance_score       - 0-100
✓ suggested_actions       - List[str]
```

### EpicSpecResponse
```
✓ completed_user_stories  - int
✓ in_progress_user_stories- int
✓ total_user_stories      - int
✓ completion_percentage   - 0-100%
✓ acceptance_criteria_met - int
✓ acceptance_percentage   - 0-100%
✓ unmet_criteria          - List[AcceptanceCriterion]
✓ days_remaining          - int
✓ is_on_track             - bool
✓ identified_risks        - List[str]
✓ roi_estimate            - float
✓ volatility_index        - float
```

### UserStorySpecResponse
```
✓ definition_of_done_met  - int
✓ dod_completion_percentage- 0-100%
✓ acceptance_criteria_met - int
✓ acceptance_percentage   - 0-100%
✓ actual_hours            - float
✓ mow_score               - Minimum Viable Feature score
✓ blocking_items          - List[str]
✓ is_blocked              - bool
✓ subtasks                - List[SubtaskEntry]
✓ time_entries            - List[TimeEntry]
✓ total_time_logged_hours - float
```

### TaskSpecResponse
```
✓ actual_hours            - float
✓ acceptance_percentage   - 0-100%
✓ blocking_items          - List[str]
✓ is_blocked              - bool
✓ active_blockers_count   - int
✓ resolved_blockers_count - int
```

### DefectSpecResponse
```
✓ resolution_status       - "open"|"in_progress"|"resolved"|"verified"
✓ resolved_at             - datetime
✓ resolved_by             - str
✓ resolution_notes        - str
✓ verification_status     - Status enum
✓ verified_at/by          - datetime/str
✓ verification_tests      - List[str]
✓ customer_impact         - str
✓ estimated_user_count    - int
✓ business_impact_score   - float
```

## Statistics Schemas Summary

| Schema | Purpose | Key Metrics |
|--------|---------|-------------|
| `RequirementQualityStats` | Requirement health | quality scores, volatility, risk distribution |
| `TestHealthStats` | Test suite status | pass rate, coverage, flakiness |
| `EpicProgressStats` | Epic tracking | completion %, story count, ROI |
| `UserStoryHealthStats` | Story health | DOD %, acceptance %, blocked count |
| `TaskProgressStats` | Task management | on time, blockers, hours tracking |
| `DefectHealthStats` | Defect status | open count, resolution time, verification |
| `ItemSpecStats` | Aggregate project | all above + coverage % + trends |

## Common Operations

### Create a Requirement
```python
from tracertm.schemas import RequirementSpecCreate, RequirementType, RiskLevel

spec = RequirementSpecCreate(
    item_id="item_123",
    requirement_type=RequirementType.EVENT_DRIVEN,
    ears_trigger="When user clicks submit",
    constraint_type=ConstraintType.HARD,
    risk_level=RiskLevel.HIGH,
    business_value=9,
    time_criticality=8,
    risk_reduction=7
)
```

### Create a Test
```python
from tracertm.schemas import TestSpecCreate, TestType

spec = TestSpecCreate(
    item_id="item_456",
    test_type=TestType.INTEGRATION,
    test_framework="pytest",
    test_file_path="tests/integration/test_login.py",
    test_function_name="test_successful_login",
    verifies_requirements=["req_123"],
    performance_baseline_ms=50.0,
    performance_threshold_ms=100.0
)
```

### Create an Epic
```python
from tracertm.schemas import EpicSpecCreate
from datetime import datetime

spec = EpicSpecCreate(
    item_id="item_789",
    business_objective="Implement payment system",
    success_criteria=[
        "Support 5 payment methods",
        "99.9% uptime",
        "<500ms transaction time"
    ],
    timeline_start=datetime(2025, 2, 1),
    timeline_end=datetime(2025, 4, 30),
    business_value=10,
    strategic_alignment=9
)
```

### Create a User Story
```python
from tracertm.schemas import UserStorySpecCreate, AcceptanceCriterion

spec = UserStorySpecCreate(
    item_id="item_111",
    user_persona="E-commerce customer",
    goal="checkout my cart",
    reason="to complete my purchase",
    estimated_story_points=8,
    business_value=9,
    urgency=8,
    acceptance_criteria=[
        AcceptanceCriterion(
            id="ac_001",
            description="Cart displays all items",
            verification_status="unverified"
        )
    ]
)
```

### Create a Task
```python
from tracertm.schemas import TaskSpecCreate, AcceptanceCriterion

spec = TaskSpecCreate(
    item_id="item_222",
    description="Implement checkout API endpoint",
    task_type="implementation",
    complexity="moderate",
    estimated_hours=8.0,
    assigned_to="dev_001",
    acceptance_criteria=[
        AcceptanceCriterion(
            id="ac_001",
            description="POST /checkout returns 200",
            verification_status="unverified"
        )
    ]
)
```

### Create a Defect
```python
from tracertm.schemas import DefectSpecCreate

spec = DefectSpecCreate(
    item_id="item_333",
    defect_title="Login fails with numbers in password",
    defect_description="Users cannot login with numeric passwords",
    reproduction_steps=[
        "Go to login page",
        "Enter password with numbers only",
        "Click submit"
    ],
    severity="high",
    priority="high",
    expected_behavior="Login succeeds",
    actual_behavior="Login fails with validation error",
    affected_components=["auth_service"]
)
```

## Validation Examples

### Valid Requirement
```python
# ✓ All required fields
spec = RequirementSpecCreate(
    item_id="req_001",
    requirement_type=RequirementType.UBIQUITOUS
    # Defaults: risk_level=MEDIUM, constraint_type=HARD
)
```

### Invalid Requirement
```python
# ✗ Missing item_id
spec = RequirementSpecCreate(
    requirement_type=RequirementType.UBIQUITOUS
)
# Pydantic raises ValidationError

# ✗ Invalid enum value
spec = RequirementSpecCreate(
    item_id="req_001",
    requirement_type="INVALID_TYPE"  # Must be from enum
)
# Pydantic raises ValidationError
```

## Key Differences from Regular Item

| Aspect | Regular Item | Item Spec |
|--------|--------------|-----------|
| Granularity | High-level | Detailed specifications |
| Metadata | Basic | Rich (collected/written/derived) |
| Quality Metrics | None | Comprehensive scoring |
| Change Tracking | Limited | Full history |
| Calculated Fields | None | Extensive |
| Verification | Simple status | Evidence-based |
| Risk Assessment | None | Detailed WSJF |
| Impact Analysis | None | Change propagation |

## Field Constraints Quick Lookup

```python
# String lengths
title: str = Field(..., min_length=1, max_length=500)
constraint_unit: str | None = Field(None, max_length=50)
framework: str | None = Field(None, max_length=100)

# Numbers
business_value: int | None = Field(None, ge=1, le=10)      # 1-10
hours: float = Field(gt=0)                                  # > 0
similarity_score: float = Field(..., ge=0, le=1)           # 0-1
score: float | None = Field(None, ge=0, le=100)            # 0-100

# Patterns
status: str = Field(default="todo", pattern="^(todo|in_progress|done)$")
severity: str = Field(..., pattern="^(critical|high|medium|low)$")

# Lists
items: list[str] = Field(default_factory=list)             # Default empty

# Dicts
metadata: dict[str, Any] = Field(default_factory=dict)     # Default empty
```

## Configuration

All Response schemas use:
```python
model_config = ConfigDict(from_attributes=True)
```

This enables:
```python
# Convert SQLAlchemy model to schema
from sqlalchemy import select
from tracertm.models import RequirementSpec

spec_model = db.execute(select(RequirementSpec)).scalar()
spec_schema = RequirementSpecResponse.model_validate(spec_model)
```

## Debugging Tips

### Check validation errors
```python
from pydantic import ValidationError

try:
    spec = RequirementSpecCreate(item_id="")  # Empty string
except ValidationError as e:
    print(e.errors())  # Shows all validation failures
```

### Inspect schema structure
```python
from tracertm.schemas import RequirementSpecResponse

# Get field info
print(RequirementSpecResponse.model_json_schema())

# List all fields
print(RequirementSpecResponse.model_fields.keys())
```

### Serialize to JSON
```python
spec = RequirementSpecResponse(...)
json_data = spec.model_dump_json()
dict_data = spec.model_dump()
```

## Type Hints Cheat Sheet

```python
# Optional types (Python 3.10+)
field: str | None = None              # Either str or None
field: list[str] | None = None        # Either list or None

# Always required
field: str                             # Must provide str
field: RequirementType                 # Must provide enum value

# Collection defaults
items: list[str] = Field(default_factory=list)    # Empty list by default
data: dict[str, Any] = Field(default_factory=dict) # Empty dict by default

# With constraints
hours: float = Field(..., gt=0)        # Required, must be > 0
score: int = Field(None, ge=0, le=100) # Optional, 0-100 if provided
```

---

**Last Updated:** 2025-01-29
**File Location:** `/src/tracertm/schemas/item_spec.py`
**Lines:** ~1,200
**Schemas:** 50+
**Enums:** 7
**Nested Types:** 10+
