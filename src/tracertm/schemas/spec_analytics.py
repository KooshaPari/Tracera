"""Pydantic schemas for spec analytics API responses.

These schemas define the response models for the blockchain/NFT-like
analytics endpoints including EARS analysis, quality scoring, flakiness
detection, ODC classification, CVSS scoring, and impact analysis.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Enums
# =============================================================================


class EARSPatternType(StrEnum):
    """EARS pattern types for requirements."""

    UBIQUITOUS = "ubiquitous"
    EVENT_DRIVEN = "event_driven"
    STATE_DRIVEN = "state_driven"
    OPTIONAL = "optional"
    COMPLEX = "complex"
    UNWANTED = "unwanted"


class QualityDimension(StrEnum):
    """ISO 29148 quality dimensions."""

    UNAMBIGUITY = "unambiguity"
    COMPLETENESS = "completeness"
    VERIFIABILITY = "verifiability"
    CONSISTENCY = "consistency"
    NECESSITY = "necessity"
    SINGULARITY = "singularity"
    FEASIBILITY = "feasibility"
    TRACEABILITY = "traceability"


class QualityGrade(StrEnum):
    """Quality grade classification."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class FlakinessPattern(StrEnum):
    """Test flakiness pattern types."""

    TIMING = "timing"
    ASYNC = "async"
    ENVIRONMENT = "environment"
    NETWORK = "network"
    RESOURCE = "resource"
    ORDER_DEPENDENT = "order_dependent"
    RANDOM = "random"


class ODCDefectType(StrEnum):
    """IBM ODC defect types."""

    FUNCTION = "function"
    INTERFACE = "interface"
    CHECKING = "checking"
    ASSIGNMENT = "assignment"
    TIMING = "timing"
    BUILD = "build"
    DOCUMENTATION = "documentation"
    ALGORITHM = "algorithm"


class ODCTrigger(StrEnum):
    """IBM ODC defect triggers."""

    COVERAGE = "coverage"
    DESIGN_CONFORMANCE = "design_conformance"
    EXCEPTION_HANDLING = "exception_handling"
    SIMPLE_PATH = "simple_path"
    COMPLEX_PATH = "complex_path"
    SIDE_EFFECTS = "side_effects"
    RARE_SITUATION = "rare_situation"


class ODCImpact(StrEnum):
    """IBM ODC defect impacts."""

    CAPABILITY = "capability"
    USABILITY = "usability"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    INSTALLABILITY = "installability"
    SERVICEABILITY = "serviceability"
    DOCUMENTATION = "documentation"
    STANDARDS = "standards"


class CVSSSeverity(StrEnum):
    """CVSS severity levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MoSCoWPriority(StrEnum):
    """MoSCoW prioritization categories."""

    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    WONT = "wont"


# =============================================================================
# EARS Analysis Schemas
# =============================================================================


class EARSComponent(BaseModel):
    """Individual component of an EARS analysis."""

    name: str
    value: str | None = None
    confidence: float = Field(ge=0, le=1)


class EARSAnalysisResponse(BaseModel):
    """Response for EARS pattern analysis of a requirement."""

    spec_id: str
    pattern_type: EARSPatternType
    confidence: float = Field(ge=0, le=1)

    # Extracted components
    trigger: str | None = None
    precondition: str | None = None
    postcondition: str | None = None
    system_name: str | None = None

    # Formal structure
    formal_structure: str | None = None
    components: dict[str, EARSComponent] = Field(default_factory=dict)

    # Suggestions for improvement
    suggestions: list[str] = Field(default_factory=list)
    is_well_formed: bool = False

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Quality Analysis Schemas
# =============================================================================


class QualityIssue(BaseModel):
    """A detected quality issue with a requirement."""

    dimension: QualityDimension
    severity: str = Field(pattern="^(error|warning|info)$")
    message: str
    suggestion: str | None = None
    line_reference: str | None = None


class QualityDimensionScore(BaseModel):
    """Score for a single quality dimension."""

    dimension: QualityDimension
    score: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1, default=1.0)
    issues: list[str] = Field(default_factory=list)


class QualityScoreResponse(BaseModel):
    """Response for ISO 29148 quality analysis."""

    spec_id: str

    # Dimension scores
    dimensions: dict[str, float] = Field(default_factory=dict)
    dimension_details: list[QualityDimensionScore] = Field(default_factory=list)

    # Overall assessment
    overall_score: float = Field(ge=0, le=1)
    grade: QualityGrade

    # Issues and suggestions
    issues: list[QualityIssue] = Field(default_factory=list)
    critical_issues_count: int = 0
    warning_issues_count: int = 0

    # Improvement suggestions
    top_improvement_areas: list[str] = Field(default_factory=list)

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Merkle Proof / Content Addressing Schemas
# =============================================================================


class MerkleProofResponse(BaseModel):
    """Response for Merkle proof generation/verification."""

    spec_id: str

    # Merkle proof components
    root: str
    proof: list[str] = Field(default_factory=list)
    leaf_index: int
    leaf_hash: str

    # Verification
    verified: bool
    verification_path: list[dict[str, str]] = Field(default_factory=list)

    # Metadata
    tree_size: int
    algorithm: str = "sha256"
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContentAddressResponse(BaseModel):
    """Response for content addressing information."""

    spec_id: str

    # Content identifiers
    content_hash: str  # SHA-256
    content_cid: str  # IPFS-style CID

    # Version chain
    version_chain_head: str | None = None
    previous_version_hash: str | None = None
    version_number: int = 1

    # Signature
    digital_signature: str | None = None
    signature_valid: bool | None = None

    # Timestamps
    created_at: datetime
    last_modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VersionChainEntry(BaseModel):
    """An entry in the version chain."""

    version_hash: str
    version_number: int
    content_hash: str
    previous_hash: str | None = None
    created_at: datetime
    created_by: str | None = None
    change_summary: str | None = None


class VersionChainResponse(BaseModel):
    """Response for version chain history."""

    spec_id: str

    # Chain info
    chain_head: str
    chain_length: int
    entries: list[VersionChainEntry] = Field(default_factory=list)

    # Integrity
    chain_valid: bool
    broken_links: list[str] = Field(default_factory=list)

    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Flakiness Analysis Schemas
# =============================================================================


class FlakinessContributingFactor(BaseModel):
    """A factor contributing to test flakiness."""

    factor: str
    weight: float = Field(ge=0, le=1)
    evidence: str | None = None


class FlakinessAnalysisResponse(BaseModel):
    """Response for test flakiness analysis."""

    spec_id: str

    # Probability metrics
    probability: float = Field(ge=0, le=1)
    entropy: float = Field(ge=0)
    confidence_interval: tuple[float, float] | None = None

    # Pattern detection
    pattern: FlakinessPattern | None = None
    pattern_confidence: float = Field(ge=0, le=1, default=0)

    # Contributing factors
    contributing_factors: list[FlakinessContributingFactor] = Field(default_factory=list)

    # Recommendation
    quarantine_recommended: bool = False
    recommendation_reason: str | None = None

    # Historical data
    recent_runs: int = 0
    flaky_runs: int = 0
    pass_rate: float = Field(ge=0, le=1, default=0)

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# ODC Classification Schemas
# =============================================================================


class ODCClassificationResponse(BaseModel):
    """Response for IBM Orthogonal Defect Classification."""

    spec_id: str

    # Classification
    defect_type: ODCDefectType
    trigger: ODCTrigger
    impact: ODCImpact

    # Confidence scores
    confidence: float = Field(ge=0, le=1)
    defect_type_confidence: float = Field(ge=0, le=1)
    trigger_confidence: float = Field(ge=0, le=1)
    impact_confidence: float = Field(ge=0, le=1)

    # Evidence
    classification_evidence: dict[str, list[str]] = Field(default_factory=dict)

    # Root cause hints
    likely_injection_phase: str | None = None
    suggested_prevention: list[str] = Field(default_factory=list)

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# CVSS Scoring Schemas
# =============================================================================


class CVSSBreakdown(BaseModel):
    """Breakdown of CVSS score components."""

    attack_vector: str
    attack_complexity: str
    privileges_required: str
    user_interaction: str
    scope: str
    confidentiality_impact: str
    integrity_impact: str
    availability_impact: str


class CVSSScoreResponse(BaseModel):
    """Response for CVSS security scoring."""

    spec_id: str

    # Score
    base_score: float = Field(ge=0, le=10)
    severity: CVSSSeverity

    # Vector string
    vector: str  # e.g., "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"

    # Component breakdown
    breakdown: CVSSBreakdown

    temporal_score: float | None = Field(None, ge=0, le=10)
    environmental_score: float | None = Field(None, ge=0, le=10)

    # Remediation
    remediation_level: str | None = None
    report_confidence: str | None = None

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Impact Analysis Schemas
# =============================================================================


class ImpactedItem(BaseModel):
    """An item impacted by a change."""

    item_id: str
    item_type: str
    item_title: str
    impact_type: str  # direct, transitive
    impact_severity: str  # high, medium, low
    distance: int  # Graph distance from source


class ImpactAnalysisResponse(BaseModel):
    """Response for graph-based impact analysis."""

    spec_id: str

    # Direct impacts
    direct_impacts: list[ImpactedItem] = Field(default_factory=list)
    direct_impact_count: int = 0

    # Transitive impacts
    transitive_impacts: list[ImpactedItem] = Field(default_factory=list)
    transitive_impact_count: int = 0

    # Totals
    total_affected: int = 0
    max_propagation_depth: int = 0

    # Risk assessment
    risk_score: float = Field(ge=0, le=100)
    risk_category: str  # critical, high, medium, low

    # Breakdown by type
    by_item_type: dict[str, int] = Field(default_factory=dict)
    by_severity: dict[str, int] = Field(default_factory=dict)

    # Recommendations
    review_required: bool = False
    suggested_actions: list[str] = Field(default_factory=list)

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Prioritization Schemas
# =============================================================================


class WSJFScore(BaseModel):
    """WSJF (Weighted Shortest Job First) scoring."""

    business_value: int = Field(ge=1, le=10)
    time_criticality: int = Field(ge=1, le=10)
    risk_reduction: int = Field(ge=1, le=10)
    job_size: int = Field(ge=1, le=10)
    wsjf_score: float


class RICEScore(BaseModel):
    """RICE (Reach, Impact, Confidence, Effort) scoring."""

    reach: int = Field(ge=0)
    impact: int = Field(ge=1, le=4)  # 1=minimal, 2=low, 3=medium, 4=high
    confidence: float = Field(ge=0, le=1)
    effort: int = Field(ge=1)
    rice_score: float


class PrioritizationResponse(BaseModel):
    """Response for prioritization calculations."""

    spec_id: str

    # WSJF
    wsjf: WSJFScore | None = None

    # RICE
    rice: RICEScore | None = None

    # MoSCoW
    moscow_priority: MoSCoWPriority | None = None
    moscow_rationale: str | None = None

    # Relative ranking (within project)
    relative_rank: int | None = None
    total_items: int | None = None

    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Batch Analysis Schemas
# =============================================================================


class CoverageGap(BaseModel):
    """A detected coverage gap."""

    requirement_id: str
    requirement_title: str
    gap_type: str  # no_tests, partial_coverage, stale_tests
    severity: str
    recommendation: str


class CoverageGapAnalysisResponse(BaseModel):
    """Response for coverage gap analysis."""

    project_id: str

    # Gaps
    gaps: list[CoverageGap] = Field(default_factory=list)
    total_gaps: int = 0

    # Coverage metrics
    requirements_with_tests: int = 0
    requirements_without_tests: int = 0
    coverage_percentage: float = Field(ge=0, le=100)

    # By severity
    critical_gaps: int = 0
    high_gaps: int = 0
    medium_gaps: int = 0

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SuspectLink(BaseModel):
    """A suspected invalid or stale traceability link."""

    source_id: str
    target_id: str
    link_type: str
    suspicion_reason: str
    confidence: float = Field(ge=0, le=1)


class SuspectLinkAnalysisResponse(BaseModel):
    """Response for suspect link detection."""

    project_id: str

    # Suspect links
    suspect_links: list[SuspectLink] = Field(default_factory=list)
    total_suspect: int = 0

    # Link health
    total_links: int = 0
    valid_links: int = 0
    link_health_percentage: float = Field(ge=0, le=100)

    # By reason
    by_reason: dict[str, int] = Field(default_factory=dict)

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimilarItem(BaseModel):
    """A semantically similar item."""

    item_id: str
    item_title: str
    item_type: str
    similarity_score: float = Field(ge=0, le=1)
    similarity_reason: str
    potential_duplicate: bool = False


class SimilarityAnalysisResponse(BaseModel):
    """Response for semantic similarity analysis."""

    spec_id: str

    # Similar items
    similar_items: list[SimilarItem] = Field(default_factory=list)
    total_similar: int = 0

    # Duplicates
    potential_duplicates: list[SimilarItem] = Field(default_factory=list)
    duplicate_count: int = 0

    # Embedding info
    embedding_model: str = "sentence-transformers"
    similarity_threshold: float = 0.8

    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Analysis Request Schemas
# =============================================================================


class AnalyzeEARSRequest(BaseModel):
    """Request for EARS analysis."""

    requirement_text: str | None = None  # If not provided, uses spec content
    include_suggestions: bool = True


class AnalyzeQualityRequest(BaseModel):
    """Request for quality analysis."""

    dimensions: list[QualityDimension] | None = None  # If None, analyze all
    include_suggestions: bool = True


class AnalyzeFlakinessRequest(BaseModel):
    """Request for flakiness analysis."""

    recent_runs_count: int = Field(default=20, ge=5, le=100)
    include_historical: bool = True


class AnalyzeODCRequest(BaseModel):
    """Request for ODC classification."""

    defect_description: str | None = None  # If not provided, uses spec content
    include_prevention_suggestions: bool = True


class AnalyzeCVSSRequest(BaseModel):
    """Request for CVSS scoring."""

    vulnerability_description: str | None = None
    include_remediation: bool = True


class AnalyzeImpactRequest(BaseModel):
    """Request for impact analysis."""

    max_depth: int = Field(default=3, ge=1, le=10)
    include_transitive: bool = True
    item_types: list[str] | None = None  # Filter by type


class CalculatePrioritizationRequest(BaseModel):
    """Request for prioritization calculation."""

    calculate_wsjf: bool = True
    calculate_rice: bool = True
    suggest_moscow: bool = True

    # WSJF inputs (optional - can use stored values)
    business_value: int | None = Field(None, ge=1, le=10)
    time_criticality: int | None = Field(None, ge=1, le=10)
    risk_reduction: int | None = Field(None, ge=1, le=10)
    job_size: int | None = Field(None, ge=1, le=10)

    # RICE inputs (optional)
    reach: int | None = Field(None, ge=0)
    impact: int | None = Field(None, ge=1, le=4)
    confidence: float | None = Field(None, ge=0, le=1)
    effort: int | None = Field(None, ge=1)


# =============================================================================
# Batch Analysis Request Schemas
# =============================================================================


class AnalyzeCoverageGapsRequest(BaseModel):
    """Request for coverage gap analysis."""

    include_stale: bool = True
    stale_threshold_days: int = Field(default=30, ge=1)


class AnalyzeSuspectLinksRequest(BaseModel):
    """Request for suspect link analysis."""

    link_types: list[str] | None = None  # Filter by type
    confidence_threshold: float = Field(default=0.7, ge=0, le=1)


class AnalyzeSimilarityRequest(BaseModel):
    """Request for similarity analysis."""

    similarity_threshold: float = Field(default=0.8, ge=0, le=1)
    max_results: int = Field(default=10, ge=1, le=50)
    include_all_types: bool = True
    item_types: list[str] | None = None
