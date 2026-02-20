"""Enhanced Item Specification Models for TraceRTM.

Provides comprehensive models for:
- RequirementSpec: Detailed requirement specifications with quality metrics
- TestSpec: Test specifications with execution history and flakiness tracking
- EpicSpec: Epic specifications with scope and metrics
- UserStorySpec: User story specifications with acceptance criteria
- TaskSpec: Task specifications with progress tracking
- DefectSpec: Defect specifications with severity and resolution tracking

Architecture:
- Each spec extends Item with specialized attributes
- Uses optimistic locking for concurrency control
- Soft delete support via deleted_at
- JSON columns for flexible metadata storage
- Comprehensive indexing for query performance
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_spec_uuid() -> str:
    """Generate a UUID string for spec ID."""
    return str(uuid.uuid4())


# ==============================================================================
# Enum Definitions
# ==============================================================================


class RequirementType(StrEnum):
    """Types of requirements."""

    UBIQUITOUS = "ubiquitous"
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"
    QUALITY = "quality"


class EARSPatternType(StrEnum):
    """EARS (Easy Approach to Requirements Syntax) pattern types."""

    UBIQUITOUS = "ubiquitous"
    EVENT_DRIVEN = "event_driven"
    STATE_DRIVEN = "state_driven"
    OPTIONAL = "optional"
    COMPLEX = "complex"
    UNWANTED = "unwanted"


class QualityDimension(StrEnum):
    """ISO 29148 quality dimensions for requirements."""

    UNAMBIGUITY = "unambiguity"
    COMPLETENESS = "completeness"
    VERIFIABILITY = "verifiability"
    CONSISTENCY = "consistency"
    NECESSITY = "necessity"
    SINGULARITY = "singularity"
    FEASIBILITY = "feasibility"
    TRACEABILITY = "traceability"


class TestOracleType(StrEnum):
    """Test oracle pattern types."""

    ASSERTION = "assertion"
    GOLDEN = "golden"
    METAMORPHIC = "metamorphic"
    PROPERTY = "property"
    DIFFERENTIAL = "differential"


class CoverageType(StrEnum):
    """Code coverage types."""

    STATEMENT = "statement"
    BRANCH = "branch"
    MCDC = "mcdc"
    PATH = "path"
    CONDITION = "condition"


class SafetyLevel(StrEnum):
    """DO-178C Safety levels (Design Assurance Levels)."""

    DAL_A = "DAL-A"
    DAL_B = "DAL-B"
    DAL_C = "DAL-C"
    DAL_D = "DAL-D"
    DAL_E = "DAL-E"


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
    """IBM Orthogonal Defect Classification defect types."""

    FUNCTION = "function"
    INTERFACE = "interface"
    CHECKING = "checking"
    ASSIGNMENT = "assignment"
    TIMING = "timing"
    BUILD = "build"
    DOCUMENTATION = "documentation"
    ALGORITHM = "algorithm"


class ODCTrigger(StrEnum):
    """IBM ODC defect trigger types."""

    COVERAGE = "coverage"
    DESIGN_CONFORMANCE = "design_conformance"
    EXCEPTION_HANDLING = "exception_handling"
    SIMPLE_PATH = "simple_path"
    COMPLEX_PATH = "complex_path"
    SIDE_EFFECTS = "side_effects"
    RARE_SITUATION = "rare_situation"


class ODCImpact(StrEnum):
    """IBM ODC defect impact types."""

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


class ConstraintType(StrEnum):
    """Types of constraints."""

    HARD = "hard"
    SOFT = "soft"
    PREFERENCE = "preference"


class RiskLevel(StrEnum):
    """Risk levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class VerificationStatus(StrEnum):
    """Verification statuses."""

    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    SUPERSEDED = "superseded"


class TestType(StrEnum):
    """Types of tests."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SMOKE = "smoke"
    REGRESSION = "regression"
    ACCEPTANCE = "acceptance"


class EpicType(StrEnum):
    """Types of epics."""

    FEATURE = "feature"
    CAPABILITY = "capability"
    INITIATIVE = "initiative"
    PROGRAM = "program"


class DefectSeverity(StrEnum):
    """Defect severity levels."""

    BLOCKER = "blocker"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    TRIVIAL = "trivial"


class DefectStatus(StrEnum):
    """Defect statuses."""

    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    VERIFIED = "verified"
    CLOSED = "closed"
    REOPENED = "reopened"


# ==============================================================================
# RequirementSpec Model
# ==============================================================================


class RequirementSpec(Base, TimestampMixin):
    """Specification for a requirement item.

    Tracks detailed requirement information including type, constraints,
    quality metrics, verification status, and volatility.
    """

    __tablename__ = "requirement_specs"

    __table_args__ = (
        Index("idx_requirement_specs_item_id", "item_id"),
        Index("idx_requirement_specs_project_type", "project_id", "requirement_type"),
        Index("idx_requirement_specs_risk", "risk_level"),
        Index("idx_requirement_specs_verification", "verification_status"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_spec_uuid)
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Requirement Classification
    requirement_type: Mapped[str] = mapped_column(String(50), nullable=False, default=RequirementType.FUNCTIONAL.value)
    constraint_type: Mapped[str] = mapped_column(String(50), nullable=False, default=ConstraintType.HARD.value)

    # Requirement Content
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Risk and Priority
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True, default=RiskLevel.MEDIUM.value)
    business_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_criticality: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    wsjf_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    complexity_estimate: Mapped[str | None] = mapped_column(String(10), nullable=True)  # XS, S, M, L, XL

    # Quality Metrics
    quality_scores: Mapped[dict[str, float]] = mapped_column(JSONType, nullable=False, default=dict)
    ambiguity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    completeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    testability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_issues: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Volatility and Change Tracking
    volatility_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    change_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Verification and Traceability
    verification_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=VerificationStatus.UNVERIFIED.value,
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verification_evidence: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Dependencies and Relations
    depends_on: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)  # Item IDs
    related_requirements: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # =========================================================================
    # BLOCKCHAIN/NFT-LIKE FIELDS - Content Addressing & Audit Trail
    # =========================================================================

    # Content Addressing (IPFS-style)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash of content
    content_cid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )  # IPFS-style Content Identifier
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)  # For baseline verification
    version_chain_head: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Latest version hash

    # Audit Trail (Blockchain-style)
    created_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Creator signature
    previous_version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Blockchain-style linking
    digital_signature: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Optional signing

    # =========================================================================
    # EARS (Easy Approach to Requirements Syntax) Classification
    # =========================================================================
    ears_pattern_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # ubiquitous, event_driven, state_driven, etc.
    ears_trigger: Mapped[str | None] = mapped_column(Text, nullable=True)
    ears_precondition: Mapped[str | None] = mapped_column(Text, nullable=True)
    ears_postcondition: Mapped[str | None] = mapped_column(Text, nullable=True)
    ears_system_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ears_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ears_formal_structure: Mapped[str | None] = mapped_column(Text, nullable=True)

    # =========================================================================
    # ISO 29148 Quality Dimensions
    # =========================================================================
    quality_dimensions: Mapped[dict[str, float]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )  # {dimension: score 0-1}
    quality_grade: Mapped[str | None] = mapped_column(String(5), nullable=True)  # A, B, C, D, F

    # =========================================================================
    # Formal Verification
    # =========================================================================
    formal_constraints: Mapped[list[dict[str, object]] | None] = mapped_column(
        JSONType,
        nullable=True,
    )  # Z3-style constraints
    invariants: Mapped[list[dict[str, object]]] = mapped_column(JSONType, nullable=False, default=list)

    # =========================================================================
    # WSJF/RICE Prioritization
    # =========================================================================
    rice_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_impact: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)
    moscow_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)  # must, should, could, wont

    # Flexible metadata
    spec_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<RequirementSpec(id={self.id!r}, item_id={self.item_id!r})>"


# ==============================================================================
# TestSpec Model
# ==============================================================================


class TestSpec(Base, TimestampMixin):
    """Specification for a test item.

    Tracks test information including type, execution history, flakiness,
    performance metrics, and quarantine status.
    """

    __tablename__ = "test_specs"

    __table_args__ = (
        Index("idx_test_specs_item_id", "item_id"),
        Index("idx_test_specs_project_type", "project_id", "test_type"),
        Index("idx_test_specs_flakiness", "flakiness_score"),
        Index("idx_test_specs_quarantine", "is_quarantined"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_spec_uuid)
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Test Classification
    test_type: Mapped[str] = mapped_column(String(50), nullable=False, default=TestType.UNIT.value)
    test_framework: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Test Content
    test_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    setup_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    teardown_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Execution Statistics
    total_runs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pass_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skip_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_run_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_run_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Run History (keep last 50)
    run_history: Mapped[list[dict[str, object]]] = mapped_column(JSONType, nullable=False, default=list)

    # Flakiness Metrics
    flakiness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    flakiness_window_runs: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    flaky_patterns: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Performance Metrics
    avg_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    p50_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    p95_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    p99_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_trend: Mapped[str | None] = mapped_column(String(50), nullable=True)  # increasing, decreasing, stable

    # Quarantine
    is_quarantined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quarantine_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    quarantined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Coverage and Dependencies
    code_coverage_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    required_for_release: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    depends_on_tests: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)  # Test item IDs

    # =========================================================================
    # BLOCKCHAIN/NFT-LIKE FIELDS - Content Addressing & Audit Trail
    # =========================================================================

    # Content Addressing (IPFS-style)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash of content
    content_cid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )  # IPFS-style Content Identifier
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)  # For baseline verification
    version_chain_head: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Latest version hash

    # Audit Trail (Blockchain-style)
    created_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Creator signature
    previous_version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Blockchain-style linking
    digital_signature: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Optional signing

    # =========================================================================
    # META-STYLE FLAKINESS DETECTION
    # =========================================================================
    flakiness_probability: Mapped[float | None] = mapped_column(Float, nullable=True)  # Bayesian probability 0-1
    flakiness_entropy: Mapped[float | None] = mapped_column(Float, nullable=True)  # Shannon entropy of results
    flakiness_pattern: Mapped[str | None] = mapped_column(String(50), nullable=True)  # timing, async, environment, etc.
    quarantine_recommended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    flakiness_contributing_factors: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # =========================================================================
    # TEST ORACLE PATTERNS
    # =========================================================================
    oracle_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # assertion, golden, metamorphic, etc.
    metamorphic_relations: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)

    # =========================================================================
    # COVERAGE CLASSIFICATION
    # =========================================================================
    coverage_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # statement, branch, MC/DC, etc.
    safety_level: Mapped[str | None] = mapped_column(String(10), nullable=True)  # DO-178C: DAL-A/B/C/D/E
    branch_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    mcdc_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    mutation_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Flexible metadata
    spec_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<TestSpec(id={self.id!r}, item_id={self.item_id!r})>"


# ==============================================================================
# EpicSpec Model
# ==============================================================================


class EpicSpec(Base, TimestampMixin):
    """Specification for an epic item.

    Tracks epic scope, team assignment, metrics, and progress.
    """

    __tablename__ = "epic_specs"

    __table_args__ = (
        Index("idx_epic_specs_item_id", "item_id"),
        Index("idx_epic_specs_project_type", "project_id", "epic_type"),
        Index("idx_epic_specs_team", "team_id"),
        Index("idx_epic_specs_status", "status"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_spec_uuid)
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Epic Classification
    epic_type: Mapped[str] = mapped_column(String(50), nullable=False, default=EpicType.FEATURE.value)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planned",
    )  # planned, in_progress, completed, cancelled

    # Epic Scope
    scope_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    objectives: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    success_criteria: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    out_of_scope: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Team and Ownership
    team_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    epic_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stakeholders: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Metrics
    user_story_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_story_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    progress_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    defect_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timeline
    planned_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Dependencies
    depends_on_epics: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)  # Epic item IDs
    related_features: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # =========================================================================
    # BLOCKCHAIN/NFT-LIKE FIELDS - Content Addressing & Audit Trail
    # =========================================================================

    # Content Addressing (IPFS-style)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash of content
    content_cid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )  # IPFS-style Content Identifier
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)  # For baseline verification
    version_chain_head: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Latest version hash

    # Audit Trail (Blockchain-style)
    created_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Creator signature
    previous_version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Blockchain-style linking
    digital_signature: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Optional signing
    change_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # =========================================================================
    # WSJF/RICE PRIORITIZATION
    # =========================================================================
    wsjf_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    business_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_criticality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_reduction: Mapped[int | None] = mapped_column(Integer, nullable=True)
    job_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    rice_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_impact: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)

    moscow_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)  # must, should, could, wont

    # Flexible metadata
    spec_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<EpicSpec(id={self.id!r}, item_id={self.item_id!r})>"


# ==============================================================================
# UserStorySpec Model
# ==============================================================================


class UserStorySpec(Base, TimestampMixin):
    """Specification for a user story item.

    Tracks user story details including personas, acceptance criteria,
    estimation, and epic relationships.
    """

    __tablename__ = "user_story_specs"

    __table_args__ = (
        Index("idx_user_story_specs_item_id", "item_id"),
        Index("idx_user_story_specs_epic_item_id", "epic_item_id"),
        Index("idx_user_story_specs_assignee", "assignee_id"),
        Index("idx_user_story_specs_status", "status"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_spec_uuid)
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User Story Content (As a ... I want ... So that ...)
    as_a: Mapped[str | None] = mapped_column(String(255), nullable=True)
    i_want: Mapped[str | None] = mapped_column(String(255), nullable=True)
    so_that: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Story Details
    business_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    acceptance_test_scenarios: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Estimation
    story_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Assignment and Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="backlog",
    )  # backlog, ready, in_progress, review, done
    assignee_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Epic Relationship
    epic_item_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Dependencies
    depends_on_stories: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)  # Story item IDs
    related_stories: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Timeline
    created_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # =========================================================================
    # BLOCKCHAIN/NFT-LIKE FIELDS - Content Addressing & Audit Trail
    # =========================================================================

    # Content Addressing (IPFS-style)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash of content
    content_cid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )  # IPFS-style Content Identifier
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)  # For baseline verification
    version_chain_head: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Latest version hash

    # Audit Trail (Blockchain-style)
    created_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Creator signature
    previous_version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Blockchain-style linking
    digital_signature: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Optional signing
    change_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # =========================================================================
    # WSJF/RICE PRIORITIZATION
    # =========================================================================
    wsjf_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_criticality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_reduction: Mapped[int | None] = mapped_column(Integer, nullable=True)
    job_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    rice_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_impact: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)

    moscow_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)  # must, should, could, wont

    # Flexible metadata
    spec_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<UserStorySpec(id={self.id!r}, item_id={self.item_id!r})>"


# ==============================================================================
# TaskSpec Model
# ==============================================================================


class TaskSpec(Base, TimestampMixin):
    """Specification for a task item.

    Tracks task details including parent story, progress, blocking status,
    and checklist items.
    """

    __tablename__ = "task_specs"

    __table_args__ = (
        Index("idx_task_specs_item_id", "item_id"),
        Index("idx_task_specs_parent_story_item_id", "parent_story_item_id"),
        Index("idx_task_specs_assignee", "assignee_id"),
        Index("idx_task_specs_blocked", "is_blocked"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_spec_uuid)
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Task Content
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Parent Story
    parent_story_item_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status and Progress
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="todo")  # TODO, in_progress, review, done
    progress_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Checklist
    checklist_items: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    completed_checklist_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Assignment
    assignee_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Blocking
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocking_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    blocks_tasks: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)  # Task item IDs
    blocked_by_tasks: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)  # Task item IDs

    # Estimation
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Timeline
    started_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # =========================================================================
    # BLOCKCHAIN/NFT-LIKE FIELDS - Content Addressing & Audit Trail
    # =========================================================================

    # Content Addressing (IPFS-style)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash of content
    content_cid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )  # IPFS-style Content Identifier
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)  # For baseline verification
    version_chain_head: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Latest version hash

    # Audit Trail (Blockchain-style)
    created_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Creator signature
    previous_version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Blockchain-style linking
    digital_signature: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Optional signing
    change_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # =========================================================================
    # WSJF/RICE PRIORITIZATION
    # =========================================================================
    wsjf_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    business_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_criticality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_reduction: Mapped[int | None] = mapped_column(Integer, nullable=True)
    job_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    rice_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_impact: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rice_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rice_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)

    moscow_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)  # must, should, could, wont

    # Flexible metadata
    spec_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<TaskSpec(id={self.id!r}, item_id={self.item_id!r})>"


# ==============================================================================
# DefectSpec Model
# ==============================================================================


class DefectSpec(Base, TimestampMixin):
    """Specification for a defect/bug item.

    Tracks defect details including severity, reproduction steps,
    resolution, and assignment.
    """

    __tablename__ = "defect_specs"

    __table_args__ = (
        Index("idx_defect_specs_item_id", "item_id"),
        Index("idx_defect_specs_severity", "severity"),
        Index("idx_defect_specs_status", "status"),
        Index("idx_defect_specs_component", "component"),
        Index("idx_defect_specs_assigned_to", "assigned_to"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_spec_uuid)
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Defect Details
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default=DefectSeverity.MAJOR.value)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=DefectStatus.NEW.value)
    component: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Reproduction
    reproducible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    steps_to_reproduce: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    expected_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Environment
    found_in_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    found_in_environment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    affects_versions: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Assignment and Tracking
    reported_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Resolution
    resolution_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )  # fixed, duplicate, wontfix, invalid
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Reopening
    reopen_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reopened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reopen_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    related_defects: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)  # Defect item IDs
    related_requirement_ids: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    related_test_ids: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Attachments and Evidence
    attachments: Mapped[list[dict[str, str]]] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )  # [{filename, url, type}]
    screenshots: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    logs: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # =========================================================================
    # BLOCKCHAIN/NFT-LIKE FIELDS - Content Addressing & Audit Trail
    # =========================================================================

    # Content Addressing (IPFS-style)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash of content
    content_cid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )  # IPFS-style Content Identifier
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)  # For baseline verification
    version_chain_head: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Latest version hash

    # Audit Trail (Blockchain-style)
    created_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Creator signature
    previous_version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Blockchain-style linking
    digital_signature: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Optional signing
    change_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # =========================================================================
    # IBM ORTHOGONAL DEFECT CLASSIFICATION (ODC)
    # =========================================================================
    odc_defect_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # function, interface, checking, etc.
    odc_trigger: Mapped[str | None] = mapped_column(String(50), nullable=True)  # coverage, design_conformance, etc.
    odc_impact: Mapped[str | None] = mapped_column(String(50), nullable=True)  # capability, usability, etc.
    odc_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # =========================================================================
    # CVSS SECURITY SCORING
    # =========================================================================
    cvss_base_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cvss_vector: Mapped[str | None] = mapped_column(String(255), nullable=True)  # CVSS vector string
    cvss_severity: Mapped[str | None] = mapped_column(String(20), nullable=True)  # none, low, medium, high, critical
    cvss_breakdown: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    # =========================================================================
    # ROOT CAUSE ANALYSIS
    # =========================================================================
    root_cause_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    injection_phase: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # requirements, design, implementation, testing
    detection_phase: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # code_review, unit_test, integration_test, etc.

    # Flexible metadata
    spec_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<DefectSpec(id={self.id!r}, item_id={self.item_id!r})>"
