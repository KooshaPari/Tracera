"""Pydantic schemas for enhanced Item specifications.

These schemas support the smart contract-like, blockchain/NFT entity-like
properties for Items with rich metadata (collected, written, derived/calculated).
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# ===== Enums (mirror the model enums) =====


class RequirementType(StrEnum):
    """EARS requirement classification types."""

    UBIQUITOUS = "ubiquitous"
    EVENT_DRIVEN = "event_driven"
    STATE_DRIVEN = "state_driven"
    OPTIONAL = "optional"
    COMPLEX = "complex"
    UNWANTED = "unwanted"


class ConstraintType(StrEnum):
    """Types of constraints on requirements."""

    HARD = "hard"
    SOFT = "soft"
    OPTIMIZABLE = "optimizable"


class QualityDimension(StrEnum):
    """Quality dimensions for requirement specification."""

    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    CORRECTNESS = "correctness"
    UNAMBIGUITY = "unambiguity"
    VERIFIABILITY = "verifiability"
    TRACEABILITY = "traceability"
    FEASIBILITY = "feasibility"
    NECESSITY = "necessity"
    SINGULARITY = "singularity"


class TestType(StrEnum):
    """Types of tests."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    CONTRACT = "contract"
    MUTATION = "mutation"
    FUZZ = "fuzz"
    PROPERTY = "property"


class TestResultStatus(StrEnum):
    """Results/statuses of test execution."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    FLAKY = "flaky"
    TIMEOUT = "timeout"
    ERROR = "error"


class VerificationStatus(StrEnum):
    """Status of requirement verification."""

    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class RiskLevel(StrEnum):
    """Risk level assessment."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


# ===== Nested Schemas for Complex Fields =====


class QualityIssue(BaseModel):
    """A detected quality issue/smell."""

    dimension: QualityDimension
    severity: str = Field(..., pattern="^(error|warning|info)$")
    message: str
    suggestion: str | None = None
    line_reference: str | None = None


class ChangeHistoryEntry(BaseModel):
    """A change history entry."""

    timestamp: datetime
    changed_by: str
    change_type: str  # created, updated, status_changed, etc.
    summary: str
    previous_values: dict[str, object] | None = None
    new_values: dict[str, object] | None = None


class VerificationEvidence(BaseModel):
    """Evidence for requirement verification."""

    type: str  # test, review, demo, document
    reference_id: str | None = None
    reference_url: str | None = None
    description: str
    verified_at: datetime
    verified_by: str


class Invariant(BaseModel):
    """A formal invariant condition."""

    id: str
    description: str
    expression: str | None = None  # Formal expression
    is_violated: bool = False
    last_checked_at: datetime | None = None


class TestRunSummary(BaseModel):
    """Summary of a test run."""

    run_id: str
    timestamp: datetime
    status: TestResultStatus
    duration_ms: int
    error_message: str | None = None
    environment: str | None = None


class AcceptanceCriterion(BaseModel):
    """An acceptance criterion with verification status."""

    id: str
    description: str
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_by: str | None = None
    verified_at: datetime | None = None
    linked_test_id: str | None = None


class SubtaskEntry(BaseModel):
    """A subtask within a user story."""

    id: str
    title: str
    status: str = Field(default="todo", pattern="^(todo|in_progress|done)$")
    assignee: str | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None


class TimeEntry(BaseModel):
    """A time tracking entry."""

    id: str
    user: str
    hours: float = Field(gt=0)
    date: str  # ISO date
    note: str | None = None


class BlockerEntry(BaseModel):
    """A blocker entry."""

    id: str
    description: str
    created_at: datetime
    resolved_at: datetime | None = None
    resolution: str | None = None


class ChecklistItem(BaseModel):
    """A checklist item for definition of done."""

    id: str
    text: str
    checked: bool = False


class ImpactAssessment(BaseModel):
    """Impact assessment for a requirement change."""

    affected_components: list[str] = Field(default_factory=list)
    affected_tests: list[str] = Field(default_factory=list)
    affected_documents: list[str] = Field(default_factory=list)
    estimated_effort_hours: float | None = None
    risk_score: float | None = Field(None, ge=0, le=100)


class SemanticSimilarity(BaseModel):
    """Semantic similarity information."""

    similar_item_id: str
    similarity_score: float = Field(..., ge=0, le=1)
    similarity_reason: str
    category: str  # duplicate, related, alternative, implements


# ===== Requirement Spec Schemas =====


class RequirementSpecCreate(BaseModel):
    """Create a requirement specification."""

    item_id: str

    # EARS Classification
    requirement_type: RequirementType = RequirementType.UBIQUITOUS
    ears_trigger: str | None = None
    ears_precondition: str | None = None
    ears_postcondition: str | None = None

    # Constraint Classification
    constraint_type: ConstraintType = ConstraintType.HARD
    constraint_target: float | None = None
    constraint_tolerance: float | None = None
    constraint_unit: str | None = Field(None, max_length=50)

    # Formal Specification
    formal_spec: str | None = None
    invariants: list[Invariant] = Field(default_factory=list)
    preconditions: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)

    # Risk & Priority
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_factors: list[str] = Field(default_factory=list)
    business_value: int | None = Field(None, ge=1, le=10)
    time_criticality: int | None = Field(None, ge=1, le=10)
    risk_reduction: int | None = Field(None, ge=1, le=10)

    # Traceability
    source_reference: str | None = None
    rationale: str | None = None
    stakeholders: list[str] = Field(default_factory=list)

    spec_metadata: dict[str, object] = Field(default_factory=dict)


class RequirementSpecUpdate(BaseModel):
    """Update a requirement specification."""

    requirement_type: RequirementType | None = None
    ears_trigger: str | None = None
    ears_precondition: str | None = None
    ears_postcondition: str | None = None

    constraint_type: ConstraintType | None = None
    constraint_target: float | None = None
    constraint_tolerance: float | None = None
    constraint_unit: str | None = Field(None, max_length=50)

    verification_status: VerificationStatus | None = None
    verification_evidence: dict[str, object] | None = None

    formal_spec: str | None = None
    invariants: list[Invariant] | None = None
    preconditions: list[str] | None = None
    postconditions: list[str] | None = None

    risk_level: RiskLevel | None = None
    risk_factors: list[str] | None = None
    business_value: int | None = Field(None, ge=1, le=10)
    time_criticality: int | None = Field(None, ge=1, le=10)
    risk_reduction: int | None = Field(None, ge=1, le=10)

    source_reference: str | None = None
    rationale: str | None = None
    stakeholders: list[str] | None = None

    spec_metadata: dict[str, object] | None = None


class RequirementSpecResponse(BaseModel):
    """Response for a requirement specification."""

    id: str
    item_id: str
    project_id: str

    # EARS
    requirement_type: str
    ears_trigger: str | None
    ears_precondition: str | None
    ears_postcondition: str | None

    # Constraints
    constraint_type: str
    constraint_target: float | None
    constraint_tolerance: float | None
    constraint_unit: str | None

    # Verification
    verification_status: str
    verified_at: datetime | None
    verified_by: str | None
    verification_evidence: dict[str, object]

    # Formal
    formal_spec: str | None
    invariants: list[dict[str, object]]
    preconditions: list[str]
    postconditions: list[str]

    quality_scores: dict[str, float]
    ambiguity_score: float | None
    completeness_score: float | None
    testability_score: float | None
    overall_quality_score: float | None
    quality_issues: list[QualityIssue]

    # Change Tracking (calculated)
    volatility_index: float | None
    change_count: int
    last_changed_at: datetime | None
    change_history: list[ChangeHistoryEntry]

    change_propagation_index: float | None
    downstream_count: int
    upstream_count: int
    impact_assessment: ImpactAssessment

    # Risk
    risk_level: str
    risk_factors: list[str]
    wsjf_score: float | None
    business_value: int | None
    time_criticality: int | None
    risk_reduction: int | None

    similar_items: list[SemanticSimilarity]
    auto_tags: list[str]
    complexity_estimate: str | None

    # Traceability
    source_reference: str | None
    rationale: str | None
    stakeholders: list[str]

    spec_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequirementSpecListResponse(BaseModel):
    """Response for list of requirement specifications."""

    total: int
    requirement_specs: list[RequirementSpecResponse]


# ===== Test Spec Schemas =====


class TestSpecCreate(BaseModel):
    """Create a test specification."""

    item_id: str

    test_type: TestType = TestType.UNIT
    test_framework: str | None = Field(None, max_length=100)
    test_file_path: str | None = None
    test_function_name: str | None = Field(None, max_length=255)

    preconditions: list[str] = Field(default_factory=list)
    setup_commands: list[str] = Field(default_factory=list)
    teardown_commands: list[str] = Field(default_factory=list)
    environment_requirements: dict[str, object] = Field(default_factory=dict)

    test_data_schema: dict[str, object] = Field(default_factory=dict)
    fixtures: list[str] = Field(default_factory=list)
    parameterized_cases: list[dict[str, object]] = Field(default_factory=list)

    verifies_requirements: list[str] = Field(default_factory=list)
    verifies_contracts: list[str] = Field(default_factory=list)
    assertions: list[str] = Field(default_factory=list)

    depends_on_tests: list[str] = Field(default_factory=list)
    required_services: list[str] = Field(default_factory=list)
    mocked_dependencies: list[str] = Field(default_factory=list)

    performance_baseline_ms: float | None = None
    performance_threshold_ms: float | None = None

    spec_metadata: dict[str, object] = Field(default_factory=dict)


class TestSpecUpdate(BaseModel):
    """Update a test specification."""

    test_type: TestType | None = None
    test_framework: str | None = Field(None, max_length=100)
    test_file_path: str | None = None
    test_function_name: str | None = Field(None, max_length=255)

    preconditions: list[str] | None = None
    setup_commands: list[str] | None = None
    teardown_commands: list[str] | None = None
    environment_requirements: dict[str, object] | None = None

    test_data_schema: dict[str, object] | None = None
    fixtures: list[str] | None = None
    parameterized_cases: list[dict[str, object]] | None = None

    verifies_requirements: list[str] | None = None
    verifies_contracts: list[str] | None = None
    assertions: list[str] | None = None

    depends_on_tests: list[str] | None = None
    required_services: list[str] | None = None
    mocked_dependencies: list[str] | None = None

    is_quarantined: bool | None = None
    quarantine_reason: str | None = None

    performance_baseline_ms: float | None = None
    performance_threshold_ms: float | None = None

    spec_metadata: dict[str, object] | None = None


class TestSpecResponse(BaseModel):
    """Response for a test specification."""

    id: str
    item_id: str
    project_id: str

    test_type: str
    test_framework: str | None
    test_file_path: str | None
    test_function_name: str | None

    preconditions: list[str]
    setup_commands: list[str]
    teardown_commands: list[str]
    environment_requirements: dict[str, object]

    test_data_schema: dict[str, object]
    fixtures: list[str]
    parameterized_cases: list[dict[str, object]]

    # Execution History (calculated)
    total_runs: int
    pass_count: int
    fail_count: int
    skip_count: int
    last_run_at: datetime | None
    last_run_status: str | None
    last_run_duration_ms: int | None
    last_run_error: str | None
    run_history: list[TestRunSummary]

    flakiness_score: float | None
    flakiness_window_runs: int
    flaky_patterns: list[str]
    is_quarantined: bool
    quarantine_reason: str | None
    quarantined_at: datetime | None

    avg_duration_ms: float | None
    p50_duration_ms: float | None
    p95_duration_ms: float | None
    p99_duration_ms: float | None
    duration_trend: str | None
    performance_baseline_ms: float | None
    performance_threshold_ms: float | None

    line_coverage: float | None
    branch_coverage: float | None
    mutation_score: float | None
    mcdc_coverage: float | None
    covered_lines: list[int]
    uncovered_lines: list[int]

    # Verification
    verifies_requirements: list[str]
    verifies_contracts: list[str]
    assertions: list[str]

    # Dependencies
    depends_on_tests: list[str]
    required_services: list[str]
    mocked_dependencies: list[str]

    last_modified_at: datetime | None
    test_age_days: int | None
    maintenance_score: float | None
    suggested_actions: list[str]

    spec_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestSpecListResponse(BaseModel):
    """Response for list of test specifications."""

    total: int
    test_specs: list[TestSpecResponse]


# ===== Epic Spec Schemas =====


class EpicSpecCreate(BaseModel):
    """Create an epic specification."""

    item_id: str

    business_objective: str
    success_criteria: list[str] = Field(default_factory=list)
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)

    scope_statement: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

    estimated_user_stories: int | None = None
    estimated_effort_hours: float | None = None

    timeline_start: datetime | None = None
    timeline_end: datetime | None = None

    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_mitigation_strategy: str | None = None

    business_value: int | None = Field(None, ge=1, le=10)
    strategic_alignment: int | None = Field(None, ge=1, le=10)

    stakeholders: list[str] = Field(default_factory=list)
    spec_metadata: dict[str, object] = Field(default_factory=dict)


class EpicSpecUpdate(BaseModel):
    """Update an epic specification."""

    business_objective: str | None = None
    success_criteria: list[str] | None = None
    acceptance_criteria: list[AcceptanceCriterion] | None = None

    scope_statement: str | None = None
    assumptions: list[str] | None = None
    constraints: list[str] | None = None
    dependencies: list[str] | None = None

    estimated_user_stories: int | None = None
    estimated_effort_hours: float | None = None

    timeline_start: datetime | None = None
    timeline_end: datetime | None = None

    risk_level: RiskLevel | None = None
    risk_mitigation_strategy: str | None = None

    business_value: int | None = Field(None, ge=1, le=10)
    strategic_alignment: int | None = Field(None, ge=1, le=10)

    stakeholders: list[str] | None = None
    spec_metadata: dict[str, object] | None = None


class EpicSpecResponse(BaseModel):
    """Response for an epic specification."""

    id: str
    item_id: str
    project_id: str

    business_objective: str
    success_criteria: list[str]
    acceptance_criteria: list[AcceptanceCriterion]

    scope_statement: str | None
    assumptions: list[str]
    constraints: list[str]
    dependencies: list[str]

    estimated_user_stories: int | None
    estimated_effort_hours: float | None

    completed_user_stories: int
    in_progress_user_stories: int
    total_user_stories: int
    completion_percentage: float

    acceptance_criteria_met: int
    acceptance_criteria_total: int
    acceptance_percentage: float
    unmet_criteria: list[AcceptanceCriterion]

    timeline_start: datetime | None
    timeline_end: datetime | None
    days_remaining: int | None
    is_on_track: bool

    risk_level: str
    risk_mitigation_strategy: str | None
    identified_risks: list[str]

    business_value: int | None
    strategic_alignment: int | None
    roi_estimate: float | None

    stakeholders: list[str]
    change_history: list[ChangeHistoryEntry]
    volatility_index: float | None

    spec_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EpicSpecListResponse(BaseModel):
    """Response for list of epic specifications."""

    total: int
    epic_specs: list[EpicSpecResponse]


# ===== User Story Spec Schemas =====


class UserStorySpecCreate(BaseModel):
    """Create a user story specification."""

    item_id: str

    user_persona: str
    goal: str
    reason: str

    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)
    definition_of_done: list[ChecklistItem] = Field(default_factory=list)

    user_journey_steps: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)

    estimated_story_points: int | None = Field(None, ge=1)
    estimated_hours: float | None = None

    priority_score: float | None = Field(None, ge=0, le=100)
    business_value: int | None = Field(None, ge=1, le=10)
    urgency: int | None = Field(None, ge=1, le=10)

    dependencies: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)

    stakeholders: list[str] = Field(default_factory=list)
    spec_metadata: dict[str, object] = Field(default_factory=dict)


class UserStorySpecUpdate(BaseModel):
    """Update a user story specification."""

    user_persona: str | None = None
    goal: str | None = None
    reason: str | None = None

    acceptance_criteria: list[AcceptanceCriterion] | None = None
    definition_of_done: list[ChecklistItem] | None = None

    user_journey_steps: list[str] | None = None
    edge_cases: list[str] | None = None

    estimated_story_points: int | None = Field(None, ge=1)
    estimated_hours: float | None = None

    priority_score: float | None = Field(None, ge=0, le=100)
    business_value: int | None = Field(None, ge=1, le=10)
    urgency: int | None = Field(None, ge=1, le=10)

    dependencies: list[str] | None = None
    blocked_by: list[str] | None = None

    stakeholders: list[str] | None = None
    spec_metadata: dict[str, object] | None = None


class UserStorySpecResponse(BaseModel):
    """Response for a user story specification."""

    id: str
    item_id: str
    project_id: str

    user_persona: str
    goal: str
    reason: str

    acceptance_criteria: list[AcceptanceCriterion]
    definition_of_done: list[ChecklistItem]

    user_journey_steps: list[str]
    edge_cases: list[str]

    estimated_story_points: int | None
    estimated_hours: float | None
    actual_hours: float | None

    definition_of_done_met: int
    definition_of_done_total: int
    dod_completion_percentage: float

    acceptance_criteria_met: int
    acceptance_criteria_total: int
    acceptance_percentage: float
    unmet_criteria: list[AcceptanceCriterion]

    priority_score: float | None
    business_value: int | None
    urgency: int | None
    mow_score: float | None  # (bValue * Urgency) / Effort

    dependencies: list[str]
    blocked_by: list[str]
    blocking_items: list[str]
    is_blocked: bool

    subtasks: list[SubtaskEntry]
    time_entries: list[TimeEntry]
    total_time_logged_hours: float

    stakeholders: list[str]
    change_history: list[ChangeHistoryEntry]

    spec_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserStorySpecListResponse(BaseModel):
    """Response for list of user story specifications."""

    total: int
    user_story_specs: list[UserStorySpecResponse]


# ===== Task Spec Schemas =====


class TaskSpecCreate(BaseModel):
    """Create a task specification."""

    item_id: str

    description: str
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)

    task_type: str = Field(default="task", max_length=50)

    estimated_hours: float | None = Field(None, gt=0)
    complexity: str | None = Field(None, pattern="^(simple|moderate|complex)$")

    dependencies: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)

    assigned_to: str | None = None
    reviewed_by: str | None = None

    time_entries: list[TimeEntry] = Field(default_factory=list)
    blockers: list[BlockerEntry] = Field(default_factory=list)

    spec_metadata: dict[str, object] = Field(default_factory=dict)


class TaskSpecUpdate(BaseModel):
    """Update a task specification."""

    description: str | None = None
    acceptance_criteria: list[AcceptanceCriterion] | None = None

    task_type: str | None = Field(None, max_length=50)

    estimated_hours: float | None = Field(None, gt=0)
    complexity: str | None = Field(None, pattern="^(simple|moderate|complex)$")

    dependencies: list[str] | None = None
    blocked_by: list[str] | None = None

    assigned_to: str | None = None
    reviewed_by: str | None = None

    time_entries: list[TimeEntry] | None = None
    blockers: list[BlockerEntry] | None = None

    spec_metadata: dict[str, object] | None = None


class TaskSpecResponse(BaseModel):
    """Response for a task specification."""

    id: str
    item_id: str
    project_id: str

    description: str
    acceptance_criteria: list[AcceptanceCriterion]

    task_type: str

    estimated_hours: float | None
    actual_hours: float | None
    complexity: str | None

    acceptance_criteria_met: int
    acceptance_criteria_total: int
    acceptance_percentage: float

    dependencies: list[str]
    blocked_by: list[str]
    blocking_items: list[str]
    is_blocked: bool

    assigned_to: str | None
    reviewed_by: str | None

    time_entries: list[TimeEntry]
    total_time_logged_hours: float

    blockers: list[BlockerEntry]
    active_blockers_count: int
    resolved_blockers_count: int

    spec_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskSpecListResponse(BaseModel):
    """Response for list of task specifications."""

    total: int
    task_specs: list[TaskSpecResponse]


# ===== Defect Spec Schemas =====


class DefectSpecCreate(BaseModel):
    """Create a defect specification."""

    item_id: str

    defect_title: str
    defect_description: str
    reproduction_steps: list[str] = Field(default_factory=list)

    severity: str = Field(default="medium", pattern="^(critical|high|medium|low)$")
    priority: str = Field(default="medium", pattern="^(critical|high|medium|low)$")

    expected_behavior: str | None = None
    actual_behavior: str | None = None

    root_cause: str | None = None
    root_cause_analysis: str | None = None

    affected_components: list[str] = Field(default_factory=list)
    affected_versions: list[str] = Field(default_factory=list)
    affected_platforms: list[str] = Field(default_factory=list)

    related_defects: list[str] = Field(default_factory=list)
    regression_detected: bool = False

    estimated_fix_hours: float | None = None

    assigned_to: str | None = None
    found_by: str | None = None

    environment_details: dict[str, object] = Field(default_factory=dict)
    spec_metadata: dict[str, object] = Field(default_factory=dict)


class DefectSpecUpdate(BaseModel):
    """Update a defect specification."""

    defect_title: str | None = None
    defect_description: str | None = None
    reproduction_steps: list[str] | None = None

    severity: str | None = Field(None, pattern="^(critical|high|medium|low)$")
    priority: str | None = Field(None, pattern="^(critical|high|medium|low)$")

    expected_behavior: str | None = None
    actual_behavior: str | None = None

    root_cause: str | None = None
    root_cause_analysis: str | None = None

    affected_components: list[str] | None = None
    affected_versions: list[str] | None = None
    affected_platforms: list[str] | None = None

    related_defects: list[str] | None = None
    regression_detected: bool | None = None

    estimated_fix_hours: float | None = None

    assigned_to: str | None = None
    found_by: str | None = None

    environment_details: dict[str, object] | None = None
    spec_metadata: dict[str, object] | None = None


class DefectSpecResponse(BaseModel):
    """Response for a defect specification."""

    id: str
    item_id: str
    project_id: str

    defect_title: str
    defect_description: str
    reproduction_steps: list[str]

    severity: str
    priority: str

    expected_behavior: str | None
    actual_behavior: str | None

    root_cause: str | None
    root_cause_analysis: str | None

    affected_components: list[str]
    affected_versions: list[str]
    affected_platforms: list[str]

    related_defects: list[str]
    regression_detected: bool

    estimated_fix_hours: float | None
    actual_fix_hours: float | None

    assigned_to: str | None
    found_by: str | None

    resolution_status: str
    resolved_at: datetime | None
    resolved_by: str | None
    resolution_notes: str | None

    verification_status: str
    verified_at: datetime | None
    verified_by: str | None
    verification_tests: list[str]

    customer_impact: str | None
    estimated_user_count: int | None
    business_impact_score: float | None

    environment_details: dict[str, object]
    spec_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DefectSpecListResponse(BaseModel):
    """Response for list of defect specifications."""

    total: int
    defect_specs: list[DefectSpecResponse]


# ===== Statistics Schemas =====


class RequirementQualityStats(BaseModel):
    """Statistics for requirement specifications."""

    project_id: str
    total_requirements: int

    by_requirement_type: dict[str, int]
    by_constraint_type: dict[str, int]
    by_risk_level: dict[str, int]
    by_verification_status: dict[str, int]

    avg_quality_score: float | None
    avg_completeness_score: float | None
    avg_testability_score: float | None
    avg_ambiguity_score: float | None

    quality_distribution: dict[str, int]  # quality_score ranges
    high_risk_count: int
    unverified_count: int
    volatile_requirements_count: int

    average_change_volatility: float | None
    average_propagation_index: float | None


class TestHealthStats(BaseModel):
    """Statistics for test specifications."""

    project_id: str
    total_tests: int

    by_test_type: dict[str, int]
    by_execution_status: dict[str, int]

    total_runs: int
    total_passed: int
    total_failed: int
    total_skipped: int
    pass_rate: float

    avg_execution_time_ms: float | None
    avg_flakiness_score: float | None
    quarantined_tests_count: int
    flaky_tests_count: int

    avg_line_coverage: float | None
    avg_branch_coverage: float | None
    avg_mutation_score: float | None

    tests_needing_maintenance: int
    avg_test_age_days: float | None


class EpicProgressStats(BaseModel):
    """Statistics for epic specifications."""

    project_id: str
    total_epics: int

    by_risk_level: dict[str, int]

    total_user_stories: int
    completed_user_stories: int
    in_progress_user_stories: int

    avg_completion_percentage: float
    on_track_epics_count: int
    at_risk_epics_count: int

    total_estimated_effort_hours: float | None
    total_actual_effort_hours: float | None

    avg_business_value: float | None
    avg_strategic_alignment: float | None

    average_roi_estimate: float | None


class UserStoryHealthStats(BaseModel):
    """Statistics for user story specifications."""

    project_id: str
    total_user_stories: int

    by_priority_range: dict[str, int]
    by_status: dict[str, int]

    avg_story_points: float | None
    avg_estimated_hours: float | None
    avg_actual_hours: float | None

    total_estimated_story_points: int | None
    total_completed_story_points: int | None

    stories_with_unmet_criteria: int
    stories_with_unmet_dod: int

    avg_dod_completion_percentage: float
    avg_acceptance_percentage: float

    blocked_stories_count: int
    stories_with_dependencies: int


class TaskProgressStats(BaseModel):
    """Statistics for task specifications."""

    project_id: str
    total_tasks: int

    by_complexity: dict[str, int]
    by_status: dict[str, int]
    by_assignee: dict[str, int]

    total_estimated_hours: float | None
    total_actual_hours: float | None

    tasks_on_time: int
    tasks_overdue: int
    tasks_with_blockers: int

    active_blockers_total: int
    avg_blockers_per_task: float | None

    avg_acceptance_percentage: float
    tasks_with_unmet_criteria: int


class DefectHealthStats(BaseModel):
    """Statistics for defect specifications."""

    project_id: str
    total_defects: int

    by_severity: dict[str, int]
    by_priority: dict[str, int]
    by_status: dict[str, int]

    open_defects: int
    resolved_defects: int
    avg_resolution_time_days: float | None

    critical_and_high_count: int
    regression_defects_count: int

    by_affected_component: dict[str, int]
    by_root_cause: dict[str, int]

    unverified_fixes_count: int
    avg_verification_time_days: float | None

    avg_estimated_fix_hours: float | None
    avg_actual_fix_hours: float | None


class ItemSpecStats(BaseModel):
    """Aggregate statistics for all item specifications."""

    project_id: str
    generated_at: datetime

    requirement_stats: RequirementQualityStats | None = None
    test_stats: TestHealthStats | None = None
    epic_stats: EpicProgressStats | None = None
    user_story_stats: UserStoryHealthStats | None = None
    task_stats: TaskProgressStats | None = None
    defect_stats: DefectHealthStats | None = None

    total_items_with_specs: int
    specification_coverage_percentage: float

    overall_quality_trend: str | None  # improving, stable, declining
    overall_test_health_trend: str | None
    overall_delivery_trend: str | None


# ===== Bulk Operation Schemas =====


class ItemSpecBulkCreateRequest(BaseModel):
    """Request for bulk creating item specifications."""

    item_specs: list[
        RequirementSpecCreate
        | TestSpecCreate
        | EpicSpecCreate
        | UserStorySpecCreate
        | TaskSpecCreate
        | DefectSpecCreate
    ]


class ItemSpecBulkUpdateRequest(BaseModel):
    """Request for bulk updating item specifications."""

    item_specs: list[dict[str, object]]  # id + update fields


class ItemSpecBulkOperationResponse(BaseModel):
    """Response for bulk operations."""

    total_processed: int
    successful: int
    failed: int
    errors: list[dict[str, object]]
    results: list[dict[str, object]]
