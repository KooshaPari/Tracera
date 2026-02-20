# Item Specification Schemas Documentation

## Overview

The `item_spec.py` schema module provides comprehensive Pydantic models for enhanced Item specifications in TraceRTM. These schemas implement smart contract-like, blockchain/NFT entity-like properties with rich metadata collection (collected, written, derived/calculated).

**File Location:** `/src/tracertm/schemas/item_spec.py`

## Architecture

### Three-Layer Metadata System

1. **Collected Metadata**: User-provided data during creation/updates
   - EARS classification, constraints, formal specs, stakeholders
   - Test configuration, framework details, performance baselines
   - Defect severity, root cause analysis, affected components

2. **Written Metadata**: Enriched by API handlers and services
   - Quality scores calculated from heuristics
   - Change history entries
   - Verification evidence links
   - Impact assessments

3. **Derived/Calculated Metadata**: Computed at read-time
   - Volatility index from change frequency
   - Flakiness scores from test runs
   - Coverage percentages from test data
   - Progress percentages from acceptance criteria
   - WSJF (Weighted Shortest Job First) scores

---

## Enum Definitions

### RequirementType
EARS (Easy Approach to Requirements Syntax) classification:
- `UBIQUITOUS` - Always applies
- `EVENT_DRIVEN` - When an event occurs
- `STATE_DRIVEN` - When system is in a state
- `OPTIONAL` - May apply in certain conditions
- `COMPLEX` - Combination of conditions
- `UNWANTED` - Describe behaviors to avoid

### ConstraintType
Constraint classification:
- `HARD` - Must be satisfied (mandatory)
- `SOFT` - Should be satisfied (preferable)
- `OPTIMIZABLE` - Best-effort optimization

### QualityDimension
Requirement quality assessment dimensions:
- `COMPLETENESS` - All aspects covered
- `CONSISTENCY` - No contradictions
- `CORRECTNESS` - Accurate and valid
- `UNAMBIGUITY` - Clear and unambiguous
- `VERIFIABILITY` - Can be tested
- `TRACEABILITY` - Linked to sources
- `FEASIBILITY` - Can be implemented
- `NECESSITY` - Actually needed
- `SINGULARITY` - Not redundant

### TestType
Classification of tests:
- `UNIT` - Single component
- `INTEGRATION` - Multiple components
- `E2E` - Full workflows
- `PERFORMANCE` - Speed/resource metrics
- `SECURITY` - Security vulnerabilities
- `ACCESSIBILITY` - A11y compliance
- `CONTRACT` - API contracts
- `MUTATION` - Code mutation testing
- `FUZZ` - Fuzz testing
- `PROPERTY` - Property-based testing

### TestResultStatus
Execution result states:
- `PASSED` - Test passed
- `FAILED` - Test failed
- `SKIPPED` - Test skipped
- `BLOCKED` - Blocked by dependency
- `FLAKY` - Intermittently fails
- `TIMEOUT` - Execution timeout
- `ERROR` - Runtime error

### VerificationStatus
Requirement verification states:
- `UNVERIFIED` - No verification attempted
- `PENDING` - Verification in progress
- `VERIFIED` - Successfully verified
- `FAILED` - Verification failed
- `EXPIRED` - Verification expired

### RiskLevel
Risk assessment levels:
- `CRITICAL` - Severe risk
- `HIGH` - Significant risk
- `MEDIUM` - Moderate risk
- `LOW` - Minor risk
- `MINIMAL` - Negligible risk

---

## Nested Schema Types

### Collected Types

#### QualityIssue
Represents a detected quality problem:
```python
{
    "dimension": "unambiguity",  # QualityDimension
    "severity": "warning",        # error|warning|info
    "message": "Ambiguous wording in requirement",
    "suggestion": "Use 'must' instead of 'should'",
    "line_reference": "req_123:5"
}
```

#### ChangeHistoryEntry
Tracks changes over time:
```python
{
    "timestamp": "2025-01-29T10:30:00Z",
    "changed_by": "user_123",
    "change_type": "updated",
    "summary": "Updated constraint target from 100ms to 50ms",
    "previous_values": {"constraint_target": 100},
    "new_values": {"constraint_target": 50}
}
```

#### VerificationEvidence
Links verification to evidence:
```python
{
    "type": "test",
    "reference_id": "test_case_456",
    "reference_url": "https://...",
    "description": "Verified via integration test suite",
    "verified_at": "2025-01-29T11:00:00Z",
    "verified_by": "qa_engineer_001"
}
```

#### Invariant
Formal condition that must always hold:
```python
{
    "id": "inv_001",
    "description": "Response time always < 100ms",
    "expression": "response_time < 100",
    "is_violated": false,
    "last_checked_at": "2025-01-29T09:00:00Z"
}
```

#### AcceptanceCriterion
Criterion with verification tracking:
```python
{
    "id": "ac_001",
    "description": "API returns 200 status on valid request",
    "verification_status": "verified",
    "verified_by": "qa_engineer_001",
    "verified_at": "2025-01-29T11:00:00Z",
    "linked_test_id": "test_case_123"
}
```

#### SubtaskEntry
Subtask within a user story:
```python
{
    "id": "subtask_001",
    "title": "Implement authentication service",
    "status": "in_progress",
    "assignee": "developer_123",
    "estimated_hours": 8.0,
    "actual_hours": 6.5
}
```

#### TimeEntry
Work time tracking:
```python
{
    "id": "time_001",
    "user": "developer_123",
    "hours": 4.5,
    "date": "2025-01-29",
    "note": "Refactored component X"
}
```

#### BlockerEntry
Issue blocking progress:
```python
{
    "id": "blocker_001",
    "description": "Waiting for API specification from backend team",
    "created_at": "2025-01-28T14:00:00Z",
    "resolved_at": "2025-01-29T10:00:00Z",
    "resolution": "Backend team provided API spec"
}
```

#### ImpactAssessment
Change impact analysis:
```python
{
    "affected_components": ["component_A", "component_B"],
    "affected_tests": ["test_001", "test_002"],
    "affected_documents": ["doc_001"],
    "estimated_effort_hours": 24.0,
    "risk_score": 65.5
}
```

#### SemanticSimilarity
AI-detected semantic similarity:
```python
{
    "similar_item_id": "req_002",
    "similarity_score": 0.87,
    "similarity_reason": "Both describe authentication flows",
    "category": "related"  # duplicate|related|alternative|implements
}
```

---

## Requirement Specification Schemas

### RequirementSpecCreate
**Purpose:** Create a requirement specification

**Key Features:**
- EARS classification (requirement type + trigger/precondition/postcondition)
- Constraint definition (hard/soft/optimizable with targets and tolerances)
- Formal specification (expressions, invariants, conditions)
- Risk assessment with WSJF components (business value, time criticality, risk reduction)
- Traceability (source reference, rationale, stakeholders)

**Example:**
```python
{
    "item_id": "item_123",
    "requirement_type": "event_driven",
    "ears_trigger": "When user clicks logout button",
    "ears_postcondition": "All sessions are terminated",
    "constraint_type": "hard",
    "constraint_target": 100,
    "constraint_unit": "ms",
    "formal_spec": "logout_request -> terminate_all_sessions",
    "invariants": [
        {
            "id": "inv_001",
            "description": "No active sessions after logout",
            "expression": "active_sessions == 0"
        }
    ],
    "risk_level": "medium",
    "business_value": 8,
    "time_criticality": 6,
    "risk_reduction": 7,
    "source_reference": "JIRA-1234",
    "rationale": "Security requirement per compliance audit"
}
```

### RequirementSpecUpdate
Partial update schema - all fields optional

### RequirementSpecResponse
**Calculated/Derived Fields:**
- `quality_scores` - Dict of all quality dimension scores
- `ambiguity_score` - Calculated ambiguity metric (0-100)
- `completeness_score` - Requirement completeness (0-100)
- `testability_score` - How testable the requirement is (0-100)
- `overall_quality_score` - Aggregate quality metric (0-100)
- `quality_issues` - List of detected quality problems
- `volatility_index` - Change frequency metric
- `change_count` - Number of times changed
- `change_propagation_index` - Impact on dependent items
- `downstream_count` - Items this impacts
- `upstream_count` - Items impacting this
- `wsjf_score` - Weighted Shortest Job First: (bValue * Urgency * RiskReduction) / Effort
- `similar_items` - AI-detected duplicates/related items
- `auto_tags` - AI-generated tags from content
- `complexity_estimate` - Simple|Moderate|Complex

---

## Test Specification Schemas

### TestSpecCreate
**Purpose:** Create a test specification

**Key Features:**
- Test framework and location (file path, function name)
- Setup/teardown and environment requirements
- Test data schema and parameterized cases
- Verification links (requirements, contracts, assertions)
- Dependencies (other tests, services)
- Performance baselines and thresholds

**Example:**
```python
{
    "item_id": "item_123",
    "test_type": "integration",
    "test_framework": "pytest",
    "test_file_path": "tests/integration/test_auth.py",
    "test_function_name": "test_logout_terminates_sessions",
    "preconditions": [
        "User is logged in",
        "At least one active session exists"
    ],
    "environment_requirements": {
        "python_version": "3.11+",
        "services": ["auth_service", "session_cache"]
    },
    "verifies_requirements": ["req_123"],
    "verifies_contracts": ["auth_contract_001"],
    "assertions": [
        "Response status == 200",
        "active_sessions == 0",
        "Response time < 100ms"
    ],
    "performance_baseline_ms": 50.0,
    "performance_threshold_ms": 100.0
}
```

### TestSpecResponse
**Calculated/Derived Fields:**
- `total_runs` - Total execution count
- `pass_count`, `fail_count`, `skip_count` - Result counters
- `last_run_status` - Most recent result
- `run_history` - List of TestRunSummary objects
- `flakiness_score` - Intermittent failure metric (0-100)
- `flaky_patterns` - Detected failure patterns
- `is_quarantined` - Marked as unreliable
- `avg_duration_ms` - Average execution time
- `p50_duration_ms`, `p95_duration_ms`, `p99_duration_ms` - Percentiles
- `duration_trend` - improving|stable|degrading
- `line_coverage`, `branch_coverage` - Code coverage %
- `mutation_score` - Mutation testing effectiveness
- `mcdc_coverage` - Modified Condition/Decision Coverage
- `test_age_days` - Days since creation
- `maintenance_score` - How well-maintained (0-100)
- `suggested_actions` - Maintenance recommendations

---

## Epic Specification Schemas

### EpicSpecCreate
**Purpose:** Create an epic specification

**Key Features:**
- Business objective and success criteria
- Scope statement with assumptions and constraints
- Acceptance criteria tracking
- Timeline estimation and actual tracking
- Risk mitigation strategy
- Strategic value metrics

**Example:**
```python
{
    "item_id": "epic_123",
    "business_objective": "Implement multi-tenant authentication system",
    "success_criteria": [
        "Support 10,000 concurrent users",
        "< 100ms auth latency",
        "99.9% uptime SLA"
    ],
    "scope_statement": "Covers authentication, authorization, and session management",
    "assumptions": ["Single sign-on provider available"],
    "constraints": ["Must use existing database"],
    "timeline_start": "2025-02-01T00:00:00Z",
    "timeline_end": "2025-04-30T23:59:59Z",
    "business_value": 9,
    "strategic_alignment": 10
}
```

### EpicSpecResponse
**Calculated/Derived Fields:**
- `completed_user_stories` - Count of done stories
- `in_progress_user_stories` - Count in progress
- `total_user_stories` - Total story count
- `completion_percentage` - Progress % (0-100)
- `acceptance_criteria_met` - Count of met criteria
- `acceptance_percentage` - Criteria completion %
- `days_remaining` - Calculated from timeline
- `is_on_track` - On schedule assessment
- `identified_risks` - Detected risks
- `roi_estimate` - Return on investment projection
- `volatility_index` - Change frequency

---

## User Story Specification Schemas

### UserStorySpecCreate
**Purpose:** Create a user story specification

**Key Features:**
- User persona, goal, and reason (classic format)
- Acceptance criteria with verification status
- Definition of Done checklist
- User journey steps and edge cases
- Story point estimation
- Priority scoring (WSJF components)
- Dependencies and blockers

**Example:**
```python
{
    "item_id": "story_123",
    "user_persona": "E-commerce customer",
    "goal": "checkout my cart securely",
    "reason": "to complete my purchase",
    "acceptance_criteria": [
        {
            "id": "ac_001",
            "description": "Cart contents displayed correctly",
            "verification_status": "unverified"
        }
    ],
    "definition_of_done": [
        {
            "id": "dod_001",
            "text": "Code reviewed and approved",
            "checked": false
        }
    ],
    "user_journey_steps": [
        "Navigate to cart",
        "Review items",
        "Enter payment info",
        "Complete purchase"
    ],
    "estimated_story_points": 8,
    "business_value": 9,
    "urgency": 8
}
```

### UserStorySpecResponse
**Calculated/Derived Fields:**
- `definition_of_done_met` - Count of completed DOD items
- `dod_completion_percentage` - DOD completion %
- `acceptance_criteria_met` - Count of verified criteria
- `acceptance_percentage` - Criteria completion %
- `actual_hours` - Time logged
- `mow_score` - Minimum Viable Feature score
- `blocking_items` - What this blocks
- `is_blocked` - Whether currently blocked
- `subtasks` - List of SubtaskEntry
- `time_entries` - List of TimeEntry
- `total_time_logged_hours` - Sum of time entries

---

## Task Specification Schemas

### TaskSpecCreate
**Purpose:** Create a task specification

**Key Features:**
- Task description and type
- Acceptance criteria
- Complexity assessment
- Time estimation
- Dependencies and blockers
- Assignment tracking
- Time and blocker entries

**Example:**
```python
{
    "item_id": "task_123",
    "description": "Implement user authentication controller",
    "task_type": "implementation",
    "complexity": "moderate",
    "estimated_hours": 6.0,
    "assigned_to": "developer_123",
    "acceptance_criteria": [
        {
            "id": "ac_001",
            "description": "Handles both username and email login",
            "verification_status": "unverified"
        }
    ]
}
```

### TaskSpecResponse
**Calculated/Derived Fields:**
- `actual_hours` - Total time logged
- `acceptance_percentage` - Criteria completion %
- `blocking_items` - Tasks blocked by this
- `is_blocked` - Currently blocked
- `active_blockers_count` - Current blockers
- `resolved_blockers_count` - Resolved blockers

---

## Defect Specification Schemas

### DefectSpecCreate
**Purpose:** Create a defect specification

**Key Features:**
- Defect description with reproduction steps
- Severity and priority classification
- Expected vs actual behavior
- Root cause analysis
- Affected components, versions, platforms
- Environment details

**Example:**
```python
{
    "item_id": "defect_123",
    "defect_title": "Login fails with special characters in password",
    "defect_description": "Users cannot login if password contains special characters",
    "reproduction_steps": [
        "Navigate to login page",
        "Enter username",
        "Enter password with special characters",
        "Click submit"
    ],
    "severity": "high",
    "priority": "high",
    "expected_behavior": "Login succeeds and user is authenticated",
    "actual_behavior": "Login fails with 'Invalid credentials' error",
    "root_cause": "Password validation regex too restrictive",
    "affected_components": ["auth_service", "login_controller"],
    "affected_versions": ["1.0.0", "1.0.1"]
}
```

### DefectSpecResponse
**Calculated/Derived Fields:**
- `resolution_status` - open|in_progress|resolved|verified
- `resolved_at` - Resolution timestamp
- `resolved_by` - User who resolved
- `resolution_notes` - Resolution details
- `verification_status` - Verification state
- `verified_at`, `verified_by` - Verification tracking
- `verification_tests` - Tests that verify the fix
- `customer_impact` - Customer impact assessment
- `estimated_user_count` - Affected users
- `business_impact_score` - Business impact metric

---

## Statistics Schemas

### RequirementQualityStats
Aggregated statistics for requirements:
```python
{
    "project_id": "proj_123",
    "total_requirements": 150,
    "by_requirement_type": {"ubiquitous": 80, "event_driven": 50, ...},
    "by_constraint_type": {"hard": 120, "soft": 30},
    "by_risk_level": {"critical": 5, "high": 15, ...},
    "by_verification_status": {"verified": 120, "unverified": 30},
    "avg_quality_score": 82.5,
    "avg_completeness_score": 85.0,
    "avg_testability_score": 78.0,
    "avg_ambiguity_score": 12.0,  # Lower is better
    "high_risk_count": 20,
    "unverified_count": 30,
    "volatile_requirements_count": 8,
    "average_change_volatility": 2.3,
    "average_propagation_index": 3.7
}
```

### TestHealthStats
Aggregated statistics for tests:
```python
{
    "project_id": "proj_123",
    "total_tests": 450,
    "total_runs": 5230,
    "total_passed": 5100,
    "total_failed": 95,
    "total_skipped": 35,
    "pass_rate": 97.5,
    "avg_execution_time_ms": 250.5,
    "avg_flakiness_score": 8.2,
    "quarantined_tests_count": 3,
    "flaky_tests_count": 12,
    "avg_line_coverage": 88.5,
    "avg_branch_coverage": 82.0,
    "avg_mutation_score": 75.5,
    "tests_needing_maintenance": 25,
    "avg_test_age_days": 180.5
}
```

### ItemSpecStats
Aggregate of all statistics:
```python
{
    "project_id": "proj_123",
    "generated_at": "2025-01-29T12:00:00Z",
    "requirement_stats": { ... },
    "test_stats": { ... },
    "epic_stats": { ... },
    "user_story_stats": { ... },
    "task_stats": { ... },
    "defect_stats": { ... },
    "total_items_with_specs": 500,
    "specification_coverage_percentage": 92.5,
    "overall_quality_trend": "improving",
    "overall_test_health_trend": "stable",
    "overall_delivery_trend": "on_track"
}
```

---

## Bulk Operation Schemas

### ItemSpecBulkCreateRequest
Create multiple specifications:
```python
{
    "item_specs": [
        { "item_id": "item_123", "requirement_type": "ubiquitous", ... },
        { "item_id": "item_124", "test_type": "unit", ... },
        ...
    ]
}
```

### ItemSpecBulkOperationResponse
Result of bulk operation:
```python
{
    "total_processed": 100,
    "successful": 98,
    "failed": 2,
    "errors": [
        {
            "item_id": "item_999",
            "error": "Item not found",
            "status_code": 404
        }
    ],
    "results": [
        {
            "item_id": "item_123",
            "spec_id": "spec_456",
            "status": "created"
        }
    ]
}
```

---

## Usage Patterns

### Creating a Requirement Specification

```python
from tracertm.schemas import RequirementSpecCreate, RiskLevel, RequirementType

spec = RequirementSpecCreate(
    item_id="req_123",
    requirement_type=RequirementType.EVENT_DRIVEN,
    ears_trigger="When user submits form",
    ears_postcondition="Data is persisted",
    risk_level=RiskLevel.MEDIUM,
    business_value=8,
    time_criticality=7,
    risk_reduction=6,
    rationale="Critical for user workflow"
)
```

### Reading Test Specification Response

```python
from tracertm.schemas import TestSpecResponse

test_spec = TestSpecResponse(
    id="test_456",
    item_id="req_123",
    # ... all response fields including calculated metrics
)

# Access calculated fields
print(f"Pass rate: {test_spec.pass_count}/{test_spec.total_runs}")
print(f"Flakiness: {test_spec.flakiness_score}%")
print(f"Coverage: {test_spec.line_coverage}%")
```

### Retrieving Statistics

```python
from tracertm.schemas import ItemSpecStats

stats = ItemSpecStats(
    project_id="proj_123",
    requirement_stats=...,
    test_stats=...,
    epic_stats=...,
    # ... etc
)

# Analyze project quality
if stats.overall_quality_trend == "improving":
    print("Quality is improving!")
```

---

## Field Validation Rules

### String Fields
- Max lengths enforced (e.g., `max_length=500` for titles)
- Min lengths for required content (e.g., `min_length=1`)
- Regex patterns for specific formats

### Numeric Fields
- Scores: 0-100 range
- Hours: Positive floats > 0
- Percentages: 0-1.0 range
- Risk/Value: 1-10 scales

### Enum Fields
- Strict enum validation
- Case-sensitive string values
- No arbitrary string values allowed

### List Fields
- Default empty lists with `default_factory=list`
- Nested complex objects supported
- Type-checked elements

### Optional Fields
- `None` allowed for optional fields
- `| None` union syntax for Python 3.10+
- Defaults to `None` when not provided

---

## Integration with Models

These schemas map to corresponding SQLAlchemy models in:
- `src/tracertm/models/requirement_spec.py`
- `src/tracertm/models/test_spec.py`
- `src/tracertm/models/epic_spec.py`
- `src/tracertm/models/user_story_spec.py`
- `src/tracertm/models/task_spec.py`
- `src/tracertm/models/defect_spec.py`

Use `model_config = ConfigDict(from_attributes=True)` in Response schemas to enable ORM model conversion.

---

## Best Practices

1. **Use Create schema for input validation** - Ensures only accepted fields are provided
2. **Use Update schema for partial updates** - All fields optional for flexibility
3. **Use Response schema for output** - Includes all calculated fields
4. **Use List schemas for pagination** - Consistent response structure
5. **Validate with Pydantic** - Type safety and constraint validation automatic
6. **Document quality dimensions** - Always include rationale in specs
7. **Track changes** - Enable change history for audit trails
8. **Link evidence** - Connect requirements to tests and documents
9. **Assess risk** - Provide risk_level and mitigation strategy
10. **Monitor metrics** - Use statistics for project health tracking

---

## See Also

- `/src/tracertm/models/` - Database models
- `/src/tracertm/repositories/` - Data access layer
- `/src/tracertm/api/routers/` - API endpoints
- `/src/tracertm/services/` - Business logic
