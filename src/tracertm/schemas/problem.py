"""Problem schemas for TraceRTM."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProblemStatus(StrEnum):
    """Valid problem statuses."""

    OPEN = "open"
    IN_INVESTIGATION = "in_investigation"
    PENDING_WORKAROUND = "pending_workaround"
    KNOWN_ERROR = "known_error"
    AWAITING_FIX = "awaiting_fix"
    CLOSED = "closed"


class ResolutionType(StrEnum):
    """How the problem was resolved."""

    PERMANENT_FIX = "permanent_fix"
    WORKAROUND_ONLY = "workaround_only"
    CANNOT_REPRODUCE = "cannot_reproduce"
    DEFERRED = "deferred"
    BY_DESIGN = "by_design"


class ImpactLevel(StrEnum):
    """Impact severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RCAMethod(StrEnum):
    """Root Cause Analysis methodologies."""

    FIVE_WHYS = "five_whys"
    FISHBONE = "fishbone"
    KEPNER_TREGOE = "kepner_tregoe"
    FMEA = "fmea"
    PARETO = "pareto"
    OTHER = "other"


class RootCauseCategory(StrEnum):
    """Categories of root causes."""

    SYSTEMATIC = "systematic"
    HUMAN = "human"
    ENVIRONMENTAL = "environmental"
    PROCESS = "process"
    TECHNOLOGY = "technology"


class ProblemCreate(BaseModel):
    """Schema for creating a problem."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None

    # Classification
    category: str | None = Field(None, max_length=100)
    sub_category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None

    # Impact
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    urgency: ImpactLevel = ImpactLevel.MEDIUM
    priority: ImpactLevel = ImpactLevel.MEDIUM
    affected_systems: list[str] | None = None
    affected_users_estimated: int | None = None
    business_impact_description: str | None = None

    # Assignment
    assigned_to: str | None = None
    assigned_team: str | None = None
    owner: str | None = None

    # Target
    target_resolution_date: datetime | None = None

    # Metadata
    metadata: dict[str, object] = Field(default_factory=dict)


class ProblemUpdate(BaseModel):
    """Schema for updating a problem."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None

    # Classification
    category: str | None = Field(None, max_length=100)
    sub_category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None

    # Impact
    impact_level: ImpactLevel | None = None
    urgency: ImpactLevel | None = None
    priority: ImpactLevel | None = None
    affected_systems: list[str] | None = None
    affected_users_estimated: int | None = None
    business_impact_description: str | None = None

    # Assignment
    assigned_to: str | None = None
    assigned_team: str | None = None
    owner: str | None = None

    # Target
    target_resolution_date: datetime | None = None

    # Metadata
    metadata: dict[str, object] | None = None


class ProblemStatusTransition(BaseModel):
    """Schema for transitioning problem status."""

    to_status: ProblemStatus
    reason: str | None = None
    performed_by: str | None = None


class RCARequest(BaseModel):
    """Schema for recording Root Cause Analysis."""

    rca_method: RCAMethod
    rca_notes: str | None = None
    rca_data: dict[str, object] | None = None
    root_cause_identified: bool = False
    root_cause_description: str | None = None
    root_cause_category: RootCauseCategory | None = None
    root_cause_confidence: str | None = Field(None, pattern="^(high|medium|low)$")
    performed_by: str | None = None


class FiveWhysAnalysis(BaseModel):
    """Schema for 5 Whys RCA method."""

    problem_statement: str
    levels: list[dict[str, str]] = Field(..., description="List of why levels: [{'question': '...', 'answer': '...'}]")
    root_cause_conclusion: str


class FishboneAnalysis(BaseModel):
    """Schema for Fishbone (Ishikawa) RCA method."""

    problem_statement: str
    categories: list[dict[str, object]] = Field(
        ...,
        description="List of categories with causes: [{'name': '...', 'causes': [...]}]",
    )
    identified_root_causes: list[str]


class WorkaroundUpdate(BaseModel):
    """Schema for updating workaround information."""

    workaround_available: bool
    workaround_description: str | None = None
    workaround_effectiveness: str | None = Field(None, pattern="^(permanent_fix|partial|temporary)$")


class PermanentFixUpdate(BaseModel):
    """Schema for updating permanent fix information."""

    permanent_fix_available: bool
    permanent_fix_description: str | None = None
    permanent_fix_change_id: str | None = None


class ProblemClosure(BaseModel):
    """Schema for closing a problem."""

    resolution_type: ResolutionType
    closure_notes: str | None = None
    closed_by: str | None = None


class ProblemResponse(BaseModel):
    """Schema for problem response."""

    id: str
    problem_number: str
    project_id: str
    title: str
    description: str | None

    # Status
    status: str
    resolution_type: str | None

    # Classification
    category: str | None
    sub_category: str | None
    tags: list[str] | None

    # Impact
    impact_level: str
    urgency: str
    priority: str
    affected_systems: list[str] | None
    affected_users_estimated: int | None
    business_impact_description: str | None

    # RCA
    rca_performed: bool
    rca_method: str | None
    rca_notes: str | None
    rca_data: dict[str, object] | None
    root_cause_identified: bool
    root_cause_description: str | None
    root_cause_category: str | None
    root_cause_confidence: str | None
    rca_completed_at: datetime | None
    rca_completed_by: str | None

    # Solutions
    workaround_available: bool
    workaround_description: str | None
    workaround_effectiveness: str | None
    permanent_fix_available: bool
    permanent_fix_description: str | None
    permanent_fix_implemented_at: datetime | None
    permanent_fix_change_id: str | None

    # Known Error
    known_error_id: str | None
    knowledge_article_id: str | None

    # Assignment
    assigned_to: str | None
    assigned_team: str | None
    owner: str | None

    # Closure
    closed_by: str | None
    closed_at: datetime | None
    closure_notes: str | None

    # Target
    target_resolution_date: datetime | None

    # Metadata
    metadata: dict[str, object]
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ProblemListResponse(BaseModel):
    """Schema for problem list item (condensed)."""

    id: str
    problem_number: str
    project_id: str
    title: str
    status: str
    priority: str
    impact_level: str
    category: str | None
    assigned_to: str | None
    assigned_team: str | None
    root_cause_identified: bool
    workaround_available: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProblemActivityResponse(BaseModel):
    """Schema for problem activity log entry."""

    id: str
    problem_id: str
    activity_type: str
    from_value: str | None
    to_value: str | None
    description: str | None
    performed_by: str | None
    metadata: dict[str, object]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
