# Item Spec Schemas - Import Reference

Complete list of all 53 classes available from `tracertm.schemas.item_spec` or `tracertm.schemas` with import examples.

## Enums (7)

```python
from tracertm.schemas import (
    RequirementType,      # UBIQUITOUS, EVENT_DRIVEN, STATE_DRIVEN, OPTIONAL, COMPLEX, UNWANTED
    ConstraintType,       # HARD, SOFT, OPTIMIZABLE
    QualityDimension,     # COMPLETENESS, CONSISTENCY, CORRECTNESS, UNAMBIGUITY, VERIFIABILITY, TRACEABILITY, FEASIBILITY, NECESSITY, SINGULARITY
    TestType,             # UNIT, INTEGRATION, E2E, PERFORMANCE, SECURITY, ACCESSIBILITY, CONTRACT, MUTATION, FUZZ, PROPERTY
    TestResultStatus,     # PASSED, FAILED, SKIPPED, BLOCKED, FLAKY, TIMEOUT, ERROR
    VerificationStatus,   # UNVERIFIED, PENDING, VERIFIED, FAILED, EXPIRED
    RiskLevel,            # CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
)
```

## Nested Type Schemas (12)

```python
from tracertm.schemas import (
    QualityIssue,
    ChangeHistoryEntry,
    VerificationEvidence,
    Invariant,
    TestRunSummary,
    AcceptanceCriterion,
    SubtaskEntry,
    TimeEntry,
    BlockerEntry,
    ChecklistItem,
    ImpactAssessment,
    SemanticSimilarity,
)
```

## Requirement Specification Schemas (4)

```python
from tracertm.schemas import (
    RequirementSpecCreate,        # Input validation schema
    RequirementSpecUpdate,        # Partial update schema
    RequirementSpecResponse,      # Output with calculated fields
    RequirementSpecListResponse,  # Paginated list response
)
```

**Usage Example:**
```python
from tracertm.schemas import RequirementSpecCreate, RequirementType, RiskLevel

spec = RequirementSpecCreate(
    item_id="req_001",
    requirement_type=RequirementType.EVENT_DRIVEN,
    ears_trigger="When user submits form",
    constraint_type=ConstraintType.HARD,
    risk_level=RiskLevel.HIGH,
    business_value=8,
    time_criticality=7,
    risk_reduction=6,
)
```

## Test Specification Schemas (4)

```python
from tracertm.schemas import (
    TestSpecCreate,        # Input validation schema
    TestSpecUpdate,        # Partial update schema
    TestSpecResponse,      # Output with calculated fields
    TestSpecListResponse,  # Paginated list response
)
```

**Usage Example:**
```python
from tracertm.schemas import TestSpecCreate, TestType

spec = TestSpecCreate(
    item_id="test_001",
    test_type=TestType.INTEGRATION,
    test_framework="pytest",
    test_file_path="tests/integration/auth.py",
    verifies_requirements=["req_001"],
    performance_baseline_ms=50.0,
    performance_threshold_ms=100.0,
)
```

## Epic Specification Schemas (4)

```python
from tracertm.schemas import (
    EpicSpecCreate,        # Input validation schema
    EpicSpecUpdate,        # Partial update schema
    EpicSpecResponse,      # Output with calculated fields
    EpicSpecListResponse,  # Paginated list response
)
```

**Usage Example:**
```python
from tracertm.schemas import EpicSpecCreate
from datetime import datetime

spec = EpicSpecCreate(
    item_id="epic_001",
    business_objective="Implement payment system",
    success_criteria=[
        "Support 5 payment methods",
        "99.9% uptime",
        "<500ms transaction time",
    ],
    timeline_start=datetime(2025, 2, 1),
    timeline_end=datetime(2025, 4, 30),
    business_value=10,
    strategic_alignment=9,
)
```

## User Story Specification Schemas (4)

```python
from tracertm.schemas import (
    UserStorySpecCreate,        # Input validation schema
    UserStorySpecUpdate,        # Partial update schema
    UserStorySpecResponse,      # Output with calculated fields
    UserStorySpecListResponse,  # Paginated list response
)
```

**Usage Example:**
```python
from tracertm.schemas import UserStorySpecCreate

spec = UserStorySpecCreate(
    item_id="story_001",
    user_persona="E-commerce customer",
    goal="checkout my cart",
    reason="to complete my purchase",
    estimated_story_points=8,
    business_value=9,
    urgency=8,
)
```

## Task Specification Schemas (4)

```python
from tracertm.schemas import (
    TaskSpecCreate,        # Input validation schema
    TaskSpecUpdate,        # Partial update schema
    TaskSpecResponse,      # Output with calculated fields
    TaskSpecListResponse,  # Paginated list response
)
```

**Usage Example:**
```python
from tracertm.schemas import TaskSpecCreate

spec = TaskSpecCreate(
    item_id="task_001",
    description="Implement checkout API endpoint",
    task_type="implementation",
    complexity="moderate",
    estimated_hours=8.0,
    assigned_to="dev_001",
)
```

## Defect Specification Schemas (4)

```python
from tracertm.schemas import (
    DefectSpecCreate,        # Input validation schema
    DefectSpecUpdate,        # Partial update schema
    DefectSpecResponse,      # Output with calculated fields
    DefectSpecListResponse,  # Paginated list response
)
```

**Usage Example:**
```python
from tracertm.schemas import DefectSpecCreate

spec = DefectSpecCreate(
    item_id="defect_001",
    defect_title="Login fails with special characters",
    defect_description="Users cannot login if password contains special characters",
    reproduction_steps=[
        "Navigate to login page",
        "Enter password with special characters",
        "Click submit",
    ],
    severity="high",
    priority="high",
)
```

## Statistics Schemas (7)

```python
from tracertm.schemas import (
    RequirementQualityStats,   # Requirement health metrics
    TestHealthStats,            # Test suite status metrics
    EpicProgressStats,          # Epic tracking metrics
    UserStoryHealthStats,       # User story health metrics
    TaskProgressStats,          # Task management metrics
    DefectHealthStats,          # Defect status metrics
    ItemSpecStats,              # Aggregate project metrics
)
```

**Usage Example:**
```python
from tracertm.schemas import ItemSpecStats
from datetime import datetime

stats = ItemSpecStats(
    project_id="proj_001",
    generated_at=datetime.now(),
    requirement_stats=...,
    test_stats=...,
    total_items_with_specs=500,
    specification_coverage_percentage=92.5,
    overall_quality_trend="improving",
)
```

## Bulk Operation Schemas (3)

```python
from tracertm.schemas import (
    ItemSpecBulkCreateRequest,    # Batch creation input
    ItemSpecBulkUpdateRequest,    # Batch update input
    ItemSpecBulkOperationResponse,# Batch operation result
)
```

**Usage Example:**
```python
from tracertm.schemas import ItemSpecBulkCreateRequest, RequirementSpecCreate

request = ItemSpecBulkCreateRequest(
    item_specs=[
        RequirementSpecCreate(item_id="req_001", ...),
        RequirementSpecCreate(item_id="req_002", ...),
        RequirementSpecCreate(item_id="req_003", ...),
    ]
)
```

---

## Complete Import (All at Once)

```python
from tracertm.schemas import (
    # Enums
    RequirementType,
    ConstraintType,
    QualityDimension,
    TestType,
    TestResultStatus,
    VerificationStatus,
    RiskLevel,
    # Nested Types
    QualityIssue,
    ChangeHistoryEntry,
    VerificationEvidence,
    Invariant,
    TestRunSummary,
    AcceptanceCriterion,
    SubtaskEntry,
    TimeEntry,
    BlockerEntry,
    ChecklistItem,
    ImpactAssessment,
    SemanticSimilarity,
    # Requirement Specs
    RequirementSpecCreate,
    RequirementSpecUpdate,
    RequirementSpecResponse,
    RequirementSpecListResponse,
    # Test Specs
    TestSpecCreate,
    TestSpecUpdate,
    TestSpecResponse,
    TestSpecListResponse,
    # Epic Specs
    EpicSpecCreate,
    EpicSpecUpdate,
    EpicSpecResponse,
    EpicSpecListResponse,
    # User Story Specs
    UserStorySpecCreate,
    UserStorySpecUpdate,
    UserStorySpecResponse,
    UserStorySpecListResponse,
    # Task Specs
    TaskSpecCreate,
    TaskSpecUpdate,
    TaskSpecResponse,
    TaskSpecListResponse,
    # Defect Specs
    DefectSpecCreate,
    DefectSpecUpdate,
    DefectSpecResponse,
    DefectSpecListResponse,
    # Statistics
    RequirementQualityStats,
    TestHealthStats,
    EpicProgressStats,
    UserStoryHealthStats,
    TaskProgressStats,
    DefectHealthStats,
    ItemSpecStats,
    # Bulk Operations
    ItemSpecBulkCreateRequest,
    ItemSpecBulkUpdateRequest,
    ItemSpecBulkOperationResponse,
)
```

---

## Import by Category

### For REST API Endpoints

```python
# Creating items
from tracertm.schemas import (
    RequirementSpecCreate,
    TestSpecCreate,
    EpicSpecCreate,
    UserStorySpecCreate,
    TaskSpecCreate,
    DefectSpecCreate,
)

# Returning responses
from tracertm.schemas import (
    RequirementSpecResponse,
    TestSpecResponse,
    EpicSpecResponse,
    UserStorySpecResponse,
    TaskSpecResponse,
    DefectSpecResponse,
)

# Listing items
from tracertm.schemas import (
    RequirementSpecListResponse,
    TestSpecListResponse,
    EpicSpecListResponse,
    UserStorySpecListResponse,
    TaskSpecListResponse,
    DefectSpecListResponse,
)

# Bulk operations
from tracertm.schemas import (
    ItemSpecBulkCreateRequest,
    ItemSpecBulkOperationResponse,
)
```

### For Data Validation

```python
from tracertm.schemas import (
    RequirementType,
    ConstraintType,
    QualityDimension,
    TestType,
    VerificationStatus,
    RiskLevel,
)

# Validate enums
if spec.requirement_type == RequirementType.UBIQUITOUS:
    print("Always applies")
```

### For Statistics & Reporting

```python
from tracertm.schemas import (
    RequirementQualityStats,
    TestHealthStats,
    EpicProgressStats,
    UserStoryHealthStats,
    TaskProgressStats,
    DefectHealthStats,
    ItemSpecStats,
)
```

### For Nested Data

```python
from tracertm.schemas import (
    AcceptanceCriterion,
    ChangeHistoryEntry,
    SubtaskEntry,
    TimeEntry,
    BlockerEntry,
    ChecklistItem,
)
```

---

## Type Hints for Functions

```python
from typing import Sequence
from tracertm.schemas import (
    RequirementSpecCreate,
    RequirementSpecResponse,
    RequirementSpecListResponse,
)

# Create endpoint
def create_requirement(
    spec: RequirementSpecCreate,
) -> RequirementSpecResponse:
    """Create a requirement specification."""
    ...

# List endpoint
def list_requirements(
    project_id: str,
    limit: int = 50,
    offset: int = 0,
) -> RequirementSpecListResponse:
    """List requirement specifications."""
    ...

# Batch endpoint
def bulk_create_requirements(
    specs: Sequence[RequirementSpecCreate],
) -> ItemSpecBulkOperationResponse:
    """Bulk create requirement specifications."""
    ...
```

---

## Migration Guide (from earlier versions)

If migrating from simpler Item schemas:

```python
# Old approach
from tracertm.schemas import ItemCreate, ItemResponse

# New approach - more specific
from tracertm.schemas import (
    RequirementSpecCreate,    # For requirements
    RequirementSpecResponse,  # For requirement details
    TestSpecCreate,           # For tests
    TestSpecResponse,         # For test details
)
```

---

## File Reference

**Module Location:** `/src/tracertm/schemas/item_spec.py`
**Exports:** `/src/tracertm/schemas/__init__.py`
**Documentation:** 
- Full Reference: `ITEM_SPEC_SCHEMAS_DOCUMENTATION.md`
- Quick Reference: `ITEM_SPEC_SCHEMAS_QUICK_REFERENCE.md`
- This File: `ITEM_SPEC_IMPORT_REFERENCE.md`

---

## Schema Count Summary

| Category | Count |
|----------|-------|
| Enums | 7 |
| Nested Types | 12 |
| Create Schemas | 6 |
| Update Schemas | 6 |
| Response Schemas | 6 |
| List Response Schemas | 6 |
| Statistics Schemas | 7 |
| Bulk Operation Schemas | 3 |
| **Total** | **53** |

---

Last Updated: 2025-01-29
