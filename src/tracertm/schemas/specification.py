"""Pydantic schemas for Specification Engine.

Comprehensive schemas for ADRs, Contracts, Features, Scenarios, and Step Definitions.
"""

from datetime import date as date_type
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# ADR Enums & Schemas
# =============================================================================


class ADRStatus(StrEnum):
    """Valid ADR statuses following MADR 4.0 standard."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


class ADROption(BaseModel):
    """A considered option in ADR decision."""

    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    is_chosen: bool = False


class ADRCreate(BaseModel):
    """Schema for creating an ADR."""

    project_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=500)
    status: ADRStatus = ADRStatus.PROPOSED

    # MADR Format
    context: str = Field(..., min_length=1)
    decision: str = Field(..., min_length=1)
    consequences: str = Field(..., min_length=1)

    # Decision Details
    decision_drivers: list[str] = Field(default_factory=list)
    considered_options: list[dict[str, object]] = Field(default_factory=list)

    # Traceability
    related_requirements: list[str] = Field(default_factory=list)
    related_adrs: list[str] = Field(default_factory=list)
    supersedes: str | None = None

    # Metadata
    stakeholders: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    date: date_type | None = None
    metadata: dict[str, object] = Field(default_factory=dict)

    model_config = ConfigDict(protected_namespaces=())


class ADRUpdate(BaseModel):
    """Schema for updating an ADR."""

    title: str | None = Field(None, min_length=1, max_length=500)
    status: ADRStatus | None = None

    # MADR Format
    context: str | None = None
    decision: str | None = None
    consequences: str | None = None

    # Decision Details
    decision_drivers: list[str] | None = None
    considered_options: list[dict[str, object]] | None = None

    # Traceability
    related_requirements: list[str] | None = None
    related_adrs: list[str] | None = None
    supersedes: str | None = None

    # Metadata
    stakeholders: list[str] | None = None
    tags: list[str] | None = None
    date: date_type | None = None
    metadata: dict[str, object] | None = None

    model_config = ConfigDict(protected_namespaces=())


class ADRResponse(BaseModel):
    """Schema for ADR response."""

    id: str
    project_id: str
    adr_number: str
    title: str
    status: str
    date: date_type

    # MADR Format
    context: str
    decision: str
    consequences: str

    # Decision Details
    decision_drivers: list[str]
    considered_options: list[dict[str, object]]

    # Traceability
    related_requirements: list[str]
    related_adrs: list[str]
    supersedes: str | None
    superseded_by: str | None

    # Compliance
    compliance_score: float

    # Metadata
    stakeholders: list[str]
    tags: list[str]
    metadata: dict[str, object]
    version: int

    # Timestamps
    last_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ADRListResponse(BaseModel):
    """Schema for ADR list response."""

    total: int
    adrs: list[ADRResponse]


class ADRActivityResponse(BaseModel):
    """Schema for ADR activity log entry."""

    id: str
    adr_id: str
    activity_type: str
    from_value: str | None = None
    to_value: str | None = None
    description: str | None = None
    performed_by: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class ADRActivityListResponse(BaseModel):
    """Schema for ADR activity list response."""

    activities: list[ADRActivityResponse]


# =============================================================================
# Contract Enums & Schemas
# =============================================================================


class ContractStatus(StrEnum):
    """Valid contract statuses."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ContractType(StrEnum):
    """Types of contracts."""

    API = "api"
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    WORKFLOW = "workflow"
    SERVICE = "service"
    OTHER = "other"


class ContractCondition(BaseModel):
    """A pre/post condition or invariant."""

    id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    condition_code: str | None = None
    required: bool = True
    priority: str | None = Field(None, pattern="^(critical|high|medium|low)$")


class StateTransition(BaseModel):
    """A state machine transition."""

    id: str = Field(..., min_length=1)
    from_state: str = Field(..., min_length=1)
    to_state: str = Field(..., min_length=1)
    trigger: str | None = None
    condition: str | None = None
    action: str | None = None


class ContractCreate(BaseModel):
    """Schema for creating a contract."""

    project_id: str = Field(..., min_length=1)
    item_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=500)
    contract_type: ContractType = ContractType.FUNCTION
    status: ContractStatus = ContractStatus.DRAFT

    # Contract Definition
    preconditions: list[dict[str, object]] = Field(default_factory=list)
    postconditions: list[dict[str, object]] = Field(default_factory=list)
    invariants: list[dict[str, object]] = Field(default_factory=list)

    # State Machine
    states: list[str] = Field(default_factory=list)
    transitions: list[dict[str, object]] = Field(default_factory=list)

    # Executable Spec
    executable_spec: str | None = None
    spec_language: str | None = None

    # Metadata
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    model_config = ConfigDict(protected_namespaces=())


class ContractUpdate(BaseModel):
    """Schema for updating a contract."""

    title: str | None = Field(None, min_length=1, max_length=500)
    contract_type: ContractType | None = None
    status: ContractStatus | None = None

    # Contract Definition
    preconditions: list[dict[str, object]] | None = None
    postconditions: list[dict[str, object]] | None = None
    invariants: list[dict[str, object]] | None = None

    # State Machine
    states: list[str] | None = None
    transitions: list[dict[str, object]] | None = None

    # Executable Spec
    executable_spec: str | None = None
    spec_language: str | None = None

    # Metadata
    tags: list[str] | None = None
    metadata: dict[str, object] | None = None

    model_config = ConfigDict(protected_namespaces=())


class ContractResponse(BaseModel):
    """Schema for contract response."""

    id: str
    project_id: str
    item_id: str
    contract_number: str
    title: str
    contract_type: str
    status: str

    # Contract Definition
    preconditions: list[dict[str, object]]
    postconditions: list[dict[str, object]]
    invariants: list[dict[str, object]]

    # State Machine
    states: list[str]
    transitions: list[dict[str, object]]

    # Executable Spec
    executable_spec: str | None
    spec_language: str | None

    # Verification
    last_verified_at: datetime | None
    verification_result: dict[str, object] | None

    # Metadata
    tags: list[str]
    metadata: dict[str, object]
    version: int

    # Timestamps
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ContractListResponse(BaseModel):
    """Schema for contract list response."""

    total: int
    contracts: list[ContractResponse]


class ContractActivityResponse(BaseModel):
    """Schema for contract activity log entry."""

    id: str
    contract_id: str
    activity_type: str
    from_value: str | None = None
    to_value: str | None = None
    description: str | None = None
    performed_by: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class ContractActivityListResponse(BaseModel):
    """Schema for contract activity list response."""

    activities: list[ContractActivityResponse]


# Alias for router compatibility
ContractRead = ContractResponse


# =============================================================================
# Feature & Scenario Enums & Schemas
# =============================================================================


class FeatureStatus(StrEnum):
    """Valid feature statuses."""

    DRAFT = "draft"
    IN_DEVELOPMENT = "in_development"
    READY_FOR_TEST = "ready_for_test"
    IN_TEST = "in_test"
    READY_FOR_RELEASE = "ready_for_release"
    RELEASED = "released"
    DEPRECATED = "deprecated"


class ScenarioStatus(StrEnum):
    """Valid scenario statuses."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    AUTOMATED = "automated"
    DEPRECATED = "deprecated"


class BDDStep(BaseModel):
    """A single BDD step (Given, When, Then)."""

    id: str = Field(..., min_length=1)
    step_number: int = Field(..., ge=1)
    keyword: str = Field(..., pattern="^(Given|When|Then|And|But)$")
    text: str = Field(..., min_length=1)
    docstring: str | None = None
    data_table: list[dict[str, str]] | None = None


class ScenarioExample(BaseModel):
    """Examples for a scenario outline."""

    name: str = Field(..., min_length=1)
    description: str | None = None
    parameters: dict[str, str] = Field(...)


class FeatureCreate(BaseModel):
    """Schema for creating a feature."""

    project_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    status: FeatureStatus = FeatureStatus.DRAFT

    # User Story Format
    as_a: str | None = None
    i_want: str | None = None
    so_that: str | None = None

    # File Management
    file_path: str | None = None

    # Traceability
    related_requirements: list[str] = Field(default_factory=list)
    related_adrs: list[str] = Field(default_factory=list)

    # Metadata
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    model_config = ConfigDict(protected_namespaces=())


class FeatureUpdate(BaseModel):
    """Schema for updating a feature."""

    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: FeatureStatus | None = None

    # User Story Format
    as_a: str | None = None
    i_want: str | None = None
    so_that: str | None = None

    # File Management
    file_path: str | None = None

    # Traceability
    related_requirements: list[str] | None = None
    related_adrs: list[str] | None = None

    # Metadata
    tags: list[str] | None = None
    metadata: dict[str, object] | None = None

    model_config = ConfigDict(protected_namespaces=())


class FeatureResponse(BaseModel):
    """Schema for feature response."""

    id: str
    project_id: str
    feature_number: str
    name: str
    description: str | None
    status: str

    # User Story Format
    as_a: str | None
    i_want: str | None
    so_that: str | None

    # File Management
    file_path: str | None

    # Traceability
    related_requirements: list[str]
    related_adrs: list[str]

    # Metadata
    tags: list[str]
    metadata: dict[str, object]
    version: int

    # Timestamps
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class FeatureListResponse(BaseModel):
    """Schema for feature list response."""

    total: int
    features: list[FeatureResponse]


class FeatureActivityResponse(BaseModel):
    """Schema for feature activity log entry."""

    id: str
    feature_id: str
    activity_type: str
    from_value: str | None = None
    to_value: str | None = None
    description: str | None = None
    performed_by: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class FeatureActivityListResponse(BaseModel):
    """Schema for feature activity list response."""

    activities: list[FeatureActivityResponse]


# =============================================================================
# Scenario Schemas
# =============================================================================


class ScenarioCreate(BaseModel):
    """Schema for creating a scenario."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    gherkin_text: str = Field(..., min_length=1)
    status: ScenarioStatus = ScenarioStatus.DRAFT

    # Steps
    background: list[dict[str, object]] = Field(default_factory=list)
    given_steps: list[dict[str, object]] = Field(default_factory=list)
    when_steps: list[dict[str, object]] = Field(default_factory=list)
    then_steps: list[dict[str, object]] = Field(default_factory=list)

    # Outline
    is_outline: bool = False
    examples: dict[str, object] | None = None

    # Traceability
    requirement_ids: list[str] = Field(default_factory=list)
    test_case_ids: list[str] = Field(default_factory=list)

    # Metadata
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    model_config = ConfigDict(protected_namespaces=())


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    gherkin_text: str | None = None
    status: ScenarioStatus | None = None

    # Steps
    background: list[dict[str, object]] | None = None
    given_steps: list[dict[str, object]] | None = None
    when_steps: list[dict[str, object]] | None = None
    then_steps: list[dict[str, object]] | None = None

    # Outline
    is_outline: bool | None = None
    examples: dict[str, object] | None = None

    # Traceability
    requirement_ids: list[str] | None = None
    test_case_ids: list[str] | None = None

    # Metadata
    tags: list[str] | None = None
    metadata: dict[str, object] | None = None

    model_config = ConfigDict(protected_namespaces=())


class ScenarioResponse(BaseModel):
    """Schema for scenario response."""

    id: str
    feature_id: str
    scenario_number: str
    title: str
    description: str | None
    gherkin_text: str
    status: str

    # Steps
    background: list[dict[str, object]]
    given_steps: list[dict[str, object]]
    when_steps: list[dict[str, object]]
    then_steps: list[dict[str, object]]

    # Outline
    is_outline: bool
    examples: dict[str, object] | None

    # Traceability
    requirement_ids: list[str]
    test_case_ids: list[str]

    # Metadata
    tags: list[str]
    metadata: dict[str, object]
    version: int

    # Execution
    pass_rate: float

    # Timestamps
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ScenarioListResponse(BaseModel):
    """Schema for scenario list response."""

    total: int
    scenarios: list[ScenarioResponse]


class ScenarioActivityResponse(BaseModel):
    """Schema for scenario activity log entry."""

    id: str
    scenario_id: str
    activity_type: str
    from_value: str | None = None
    to_value: str | None = None
    description: str | None = None
    performed_by: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class ScenarioActivityListResponse(BaseModel):
    """Schema for scenario activity list response."""

    total: int
    activities: list[ScenarioActivityResponse]


# =============================================================================
# Step Definition Enums & Schemas
# =============================================================================


class StepDefinitionType(StrEnum):
    """Types of step definitions."""

    GIVEN = "given"
    WHEN = "when"
    THEN = "then"
    AND = "and"
    BUT = "but"


class StepDefinitionLanguage(StrEnum):
    """Programming languages for step definitions."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GHERKIN = "gherkin"
    SQL = "sql"
    OTHER = "other"


class StepDefinitionImplementation(BaseModel):
    """Implementation details for a step definition."""

    language: StepDefinitionLanguage
    code: str = Field(..., min_length=1)
    imports: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    timeout_seconds: int | None = None


class StepDefinitionCreate(BaseModel):
    """Schema for creating a step definition."""

    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    step_type: StepDefinitionType

    # Pattern for matching in scenarios
    pattern: str = Field(..., min_length=1)
    pattern_type: str = Field(default="regex", pattern="^(regex|literal|glob)$")

    # Implementation
    implementation: StepDefinitionImplementation | None = None

    # Parameters
    parameters: list[str] = Field(default_factory=list)
    return_type: str | None = None

    # Traceability
    related_step_definitions: list[str] = Field(default_factory=list)
    test_case_ids: list[str] = Field(default_factory=list)

    # Metadata
    tags: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    model_config = ConfigDict(protected_namespaces=())


class StepDefinitionUpdate(BaseModel):
    """Schema for updating a step definition."""

    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    step_type: StepDefinitionType | None = None

    # Pattern for matching in scenarios
    pattern: str | None = None
    pattern_type: str | None = Field(None, pattern="^(regex|literal|glob)$")

    # Implementation
    implementation: StepDefinitionImplementation | None = None

    # Parameters
    parameters: list[str] | None = None
    return_type: str | None = None

    # Traceability
    related_step_definitions: list[str] | None = None
    test_case_ids: list[str] | None = None

    # Metadata
    tags: list[str] | None = None
    examples: list[str] | None = None
    metadata: dict[str, object] | None = None

    model_config = ConfigDict(protected_namespaces=())


class StepDefinitionResponse(BaseModel):
    """Schema for step definition response."""

    id: str
    project_id: str
    step_definition_number: str
    name: str
    description: str | None
    step_type: str

    # Pattern for matching in scenarios
    pattern: str
    pattern_type: str

    # Implementation
    implementation: dict[str, object] | None

    # Parameters
    parameters: list[str]
    return_type: str | None

    # Traceability
    related_step_definitions: list[str]
    test_case_ids: list[str]

    # Metadata
    tags: list[str]
    examples: list[str]
    metadata: dict[str, object]
    version: int

    # Execution
    usage_count: int = 0
    last_used_at: datetime | None = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class StepDefinitionListResponse(BaseModel):
    """Schema for step definition list response."""

    total: int
    step_definitions: list[StepDefinitionResponse]


# =============================================================================
# Requirement Quality Schemas
# =============================================================================


class RequirementQualityRead(BaseModel):
    """Schema for requirement quality analysis result."""

    id: str
    item_id: str
    smells: list[str]
    ambiguity_score: float = Field(..., ge=0.0, le=1.0)
    completeness_score: float = Field(..., ge=0.0, le=1.0)
    suggestions: list[str]
    last_analyzed_at: datetime
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# Aliases for router compatibility (Response -> Read naming)
FeatureRead = FeatureResponse
ScenarioRead = ScenarioResponse
StepDefinitionRead = StepDefinitionResponse
ADRRead = ADRResponse
