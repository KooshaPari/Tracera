# Defect Specification Implementation Guide

**Purpose:** Practical implementation of comprehensive defect specification patterns in your system

---

## Part 1: Enhanced Defect Model for TraceRTM

### 1.1 Updated Model with All Attributes

```python
# /src/tracertm/models/defect.py

"""
Comprehensive defect model incorporating ISTQB, ODC, RCA, and security frameworks.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import (
    DateTime, ForeignKey, Index, Integer, String, Text, Boolean, Float
)
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_defect_uuid() -> str:
    """Generate a UUID string for defect ID."""
    return str(uuid.uuid4())


# ===== ISTQB ENUMERATIONS =====

class DefectType(str, Enum):
    """ISTQB Defect Types"""
    FUNCTIONAL = "functional"
    STRUCTURAL = "structural"
    DATA = "data"
    NON_FUNCTIONAL = "non_functional"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    UI = "ui"
    ACCESSIBILITY = "accessibility"


class Severity(str, Enum):
    """ISTQB Severity Levels"""
    CRITICAL = "critical"      # L1 - Blocker
    HIGH = "high"              # L2 - Major
    MEDIUM = "medium"          # L3 - Minor
    LOW = "low"                # L4 - Trivial


class Priority(str, Enum):
    """Priority for remediation"""
    P1 = "p1"  # Fix immediately (24h)
    P2 = "p2"  # Fix soon (3-5 days)
    P3 = "p3"  # Fix eventually (1-2 weeks)
    P4 = "p4"  # Backlog (1-4 weeks)
    P5 = "p5"  # Deferred (future)


class DefectStatus(str, Enum):
    """Defect lifecycle states"""
    NEW = "new"
    SUBMITTED = "submitted"
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    VERIFIED = "verified"
    CLOSED = "closed"
    REOPENED = "reopened"
    DEFERRED = "deferred"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"
    CANNOT_REPRODUCE = "cannot_reproduce"


class Reproducibility(str, Enum):
    """How easily can issue be reproduced?"""
    ALWAYS = "always"              # Level 5 - Always reproducible
    USUALLY = "usually"            # Level 4 - 80-95% reproducible
    SOMETIMES = "sometimes"        # Level 3 - 50-80% reproducible
    RARELY = "rarely"              # Level 2 - <50% reproducible
    CANNOT_REPRODUCE = "cannot"    # Level 1 - Not reproducible


# ===== ODC ENUMERATIONS =====

class ODCTrigger(str, Enum):
    """ODC: When was defect detected?"""
    DESIGN_INSPECTION = "design_inspection"
    DESIGN_TESTING = "design_testing"
    CODE_INSPECTION = "code_inspection"
    CODE_TESTING = "code_testing"
    INTEGRATION_TESTING = "integration_testing"
    SYSTEM_TESTING = "system_testing"
    USER_TESTING = "user_testing"
    PRODUCTION = "production"


class ODCDefectType(str, Enum):
    """ODC: What was wrong?"""
    FUNCTIONAL = "functional"          # Missing/incorrect logic
    INTERFACE = "interface"            # Wrong API/message
    CHECKING = "checking"              # Invalid validation
    ASSIGNMENT = "assignment"          # Wrong variable
    TIMING_SERIALIZATION = "timing_serialization"  # Race/order
    BUILD_PACKAGE = "build_package"    # Compilation
    DOCUMENTATION = "documentation"    # Wrong/missing docs
    ALGORITHM = "algorithm"            # Incorrect approach
    INITIALIZATION = "initialization"  # Wrong startup state
    PERFORMANCE = "performance"        # Inefficiency
    STANDARDS = "standards"            # Code standard violation


class ODCOrigin(str, Enum):
    """ODC: Where did defect originate?"""
    DESIGN = "design"
    CODE = "code"
    OTHER = "other"
    UNKNOWN = "unknown"


# ===== SECURITY ENUMERATIONS =====

class CWECategory(str, Enum):
    """CWE Top 25 Categories"""
    SQL_INJECTION = "cwe_89"
    XSS = "cwe_79"
    COMMAND_INJECTION = "cwe_78"
    BROKEN_AUTH = "cwe_287"
    SENSITIVE_DATA = "cwe_327"
    XXE = "cwe_611"
    ACCESS_CONTROL = "cwe_284"
    MISCONFIG = "cwe_16"
    CSRF = "cwe_352"
    COMPONENTS = "cwe_1035"
    LOGGING = "cwe_778"
    OTHER = "other"


class CVSSSeverity(str, Enum):
    """CVSS Severity Rating"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===== RCA ENUMERATIONS =====

class RCAMethod(str, Enum):
    """Root Cause Analysis Methods"""
    FIVE_WHYS = "five_whys"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    FMEA = "fmea"
    PARETO = "pareto"
    OTHER = "other"


class RootCauseCategory(str, Enum):
    """Root Cause Classifications"""
    SYSTEMATIC = "systematic"
    HUMAN = "human"
    ENVIRONMENTAL = "environmental"
    PROCESS = "process"
    TECHNOLOGY = "technology"


# ===== MAIN DEFECT MODEL =====

class Defect(Base, TimestampMixin):
    """
    Comprehensive defect model integrating:
    - ISTQB classification (severity, priority, type)
    - ODC attributes (trigger, defect type, origin)
    - RCA support (methods, analysis data)
    - Security classification (CVE, CVSS, CWE)
    - Quality metrics (complexity, churn, coverage)
    - Regression tracking
    - Clustering metrics
    """

    __tablename__ = "defects"

    __table_args__ = (
        Index("idx_defects_project_status", "project_id", "status"),
        Index("idx_defects_project_severity", "project_id", "severity"),
        Index("idx_defects_project_priority", "project_id", "priority"),
        Index("idx_defects_module", "module"),
        Index("idx_defects_assigned_to", "assigned_to"),
        Index("idx_defects_reproducibility", "reproducibility"),
        Index("idx_defects_is_regression", "is_regression"),
        Index("idx_defects_security_issue", "is_security_issue"),
        Index("idx_defects_rca_performed", "rca_performed"),
        {"extend_existing": True},
    )

    # ===== IDENTIFICATION =====
    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_defect_uuid
    )
    defect_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    component: Mapped[str | None] = mapped_column(String(255), nullable=True)
    module: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # ===== ISTQB CLASSIFICATION =====
    defect_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Severity.MEDIUM.value, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Priority.P3.value, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=DefectStatus.NEW.value, index=True
    )
    reproducibility: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Reproducibility.USUALLY.value, index=True
    )

    # ===== IMPACT ASSESSMENT =====
    impact_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Severity.MEDIUM.value
    )
    urgency: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Severity.MEDIUM.value
    )
    affected_systems: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    affected_users_estimated: Mapped[int | None] = mapped_column(Integer, nullable=True)
    business_impact_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    blast_radius: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=1
    )  # Dependent modules count

    # ===== REPRODUCTION DETAILS =====
    steps_to_reproduce: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    expected_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    environment_details: Mapped[dict[str, str] | None] = mapped_column(
        JSONType, nullable=True
    )  # OS, browser, version, etc.
    reproduction_frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ===== ODC ATTRIBUTES =====
    odc_trigger: Mapped[str | None] = mapped_column(String(50), nullable=True)
    odc_defect_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    odc_origin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    odc_impact_area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    odc_confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ===== ROOT CAUSE ANALYSIS =====
    rca_performed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rca_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rca_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rca_data: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)
    root_cause_identified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    root_cause_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    root_cause_confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rca_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rca_completed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ===== SOLUTIONS =====
    workaround_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    workaround_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    workaround_effectiveness: Mapped[str | None] = mapped_column(String(50), nullable=True)
    permanent_fix_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    permanent_fix_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    permanent_fix_change_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    permanent_fix_implemented_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ===== SECURITY ATTRIBUTES =====
    is_security_issue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    cwe_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cwe_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cwe_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cvss_vector: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cvss_severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    attack_vector: Mapped[str | None] = mapped_column(String(50), nullable=True)
    attack_complexity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    privileges_required: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cve_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # ===== QUALITY METRICS =====
    code_churn_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    cyclomatic_complexity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    affected_lines_of_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    code_coverage_gap: Mapped[float | None] = mapped_column(Float, nullable=True)
    technical_debt_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    code_smell_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ===== REGRESSION TRACKING =====
    is_regression: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    regression_of_defect_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fix_introduced_this_defect: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    introduced_by_defect_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    regression_test_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ===== CLUSTERING METRICS =====
    module_defect_density: Mapped[float | None] = mapped_column(Float, nullable=True)
    module_total_defects: Mapped[int | None] = mapped_column(Integer, nullable=True)
    module_pareto_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    similar_defect_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # ===== QUALITY ASSESSMENT =====
    report_quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reproducibility_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_resolution_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ===== ASSIGNMENT & OWNERSHIP =====
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    assigned_team: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reported_by: Mapped[str] = mapped_column(String(255), nullable=False)
    reporter_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ===== DATES & SLA =====
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    target_resolution_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_resolution_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sla_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sla_status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ===== CLOSURE =====
    resolution_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    closure_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ===== SUPPORTING EVIDENCE =====
    attachments: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONType, nullable=False, default=list
    )
    related_defect_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    related_issue_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    test_case_links: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # ===== METADATA =====
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    custom_fields: Mapped[dict[str, Any]] = mapped_column(
        JSONType, nullable=False, default=dict
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    __mapper_args__: dict[str, Any] = {
        "version_id_col": version,
    }

    def __repr__(self) -> str:
        return f"<Defect(id={self.id!r}, number={self.defect_number!r}, title={self.title!r})>"


class DefectActivity(Base, TimestampMixin):
    """Activity log for defect changes - audit trail"""

    __tablename__ = "defect_activities"

    __table_args__ = (
        Index("idx_defect_activities_defect_id", "defect_id"),
        Index("idx_defect_activities_activity_type", "activity_type"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_defect_uuid
    )
    defect_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("defects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    to_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activity_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONType, nullable=False, default=dict
    )

    def __repr__(self) -> str:
        return f"<DefectActivity(id={self.id!r}, type={self.activity_type!r})>"


class DefectMetrics(Base, TimestampMixin):
    """
    Aggregated metrics for defect analysis.
    Computed periodically for reporting and trends.
    """

    __tablename__ = "defect_metrics"

    __table_args__ = (
        Index("idx_defect_metrics_project", "project_id"),
        Index("idx_defect_metrics_date", "metric_date"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_defect_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Volume metrics
    total_open_defects: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_critical: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_high: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_medium: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_low: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Quality metrics
    average_resolution_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    sla_compliance_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    escape_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    regression_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    rca_completion_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Distribution metrics
    severity_distribution: Mapped[dict[str, int]] = mapped_column(
        JSONType, nullable=False, default=dict
    )
    type_distribution: Mapped[dict[str, int]] = mapped_column(
        JSONType, nullable=False, default=dict
    )
    module_defect_density: Mapped[dict[str, float]] = mapped_column(
        JSONType, nullable=False, default=dict
    )

    # Security metrics
    security_defect_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_security_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Pareto analysis
    hotspot_modules: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONType, nullable=False, default=list
    )

    metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONType, nullable=False, default=dict
    )

    def __repr__(self) -> str:
        return f"<DefectMetrics(project={self.project_id!r}, date={self.metric_date!r})>"
```

### 1.2 Pydantic Schemas

```python
# /src/tracertm/schemas/defect.py

"""Defect schemas for TraceRTM."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

# Import enums from models
from tracertm.models.defect import (
    DefectType, Severity, Priority, DefectStatus, Reproducibility,
    ODCTrigger, ODCDefectType, ODCOrigin,
    CWECategory, CVSSSeverity,
    RCAMethod, RootCauseCategory
)


class DefectCreate(BaseModel):
    """Schema for creating a defect."""

    title: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = None
    component: Optional[str] = None
    module: Optional[str] = None

    # Classification
    defect_type: DefectType
    severity: Severity = Severity.MEDIUM
    priority: Priority = Priority.P3
    reproducibility: Reproducibility = Reproducibility.USUALLY

    # Impact
    impact_level: Severity = Severity.MEDIUM
    urgency: Severity = Severity.MEDIUM
    affected_systems: Optional[list[str]] = None
    affected_users_estimated: Optional[int] = None
    business_impact_description: Optional[str] = None

    # Reproduction
    steps_to_reproduce: Optional[list[str]] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    environment_details: Optional[dict[str, str]] = None
    reproduction_frequency: Optional[str] = None

    # Assignment
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    owner: Optional[str] = None
    reported_by: str
    reporter_contact: Optional[str] = None

    # Target resolution
    target_resolution_date: Optional[datetime] = None

    # Tags and metadata
    tags: Optional[list[str]] = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)


class DefectUpdate(BaseModel):
    """Schema for updating a defect."""

    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = None
    component: Optional[str] = None
    module: Optional[str] = None

    # Classification
    defect_type: Optional[DefectType] = None
    severity: Optional[Severity] = None
    priority: Optional[Priority] = None
    reproducibility: Optional[Reproducibility] = None

    # Impact
    impact_level: Optional[Severity] = None
    urgency: Optional[Severity] = None
    affected_systems: Optional[list[str]] = None
    affected_users_estimated: Optional[int] = None
    business_impact_description: Optional[str] = None
    blast_radius: Optional[int] = None

    # Reproduction
    steps_to_reproduce: Optional[list[str]] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    environment_details: Optional[dict[str, str]] = None
    reproduction_frequency: Optional[str] = None

    # ODC
    odc_trigger: Optional[ODCTrigger] = None
    odc_defect_type: Optional[ODCDefectType] = None
    odc_origin: Optional[ODCOrigin] = None
    odc_impact_area: Optional[str] = None

    # RCA
    rca_performed: Optional[bool] = None
    rca_method: Optional[RCAMethod] = None
    rca_notes: Optional[str] = None
    root_cause_identified: Optional[bool] = None
    root_cause_description: Optional[str] = None
    root_cause_category: Optional[RootCauseCategory] = None

    # Security
    is_security_issue: Optional[bool] = None
    cwe_category: Optional[CWECategory] = None
    cvss_score: Optional[float] = None
    cve_ids: Optional[list[str]] = None

    # Quality metrics
    code_churn_percentage: Optional[float] = None
    cyclomatic_complexity: Optional[int] = None
    affected_lines_of_code: Optional[int] = None
    code_coverage_gap: Optional[float] = None
    technical_debt_hours: Optional[float] = None

    # Regression
    is_regression: Optional[bool] = None
    regression_of_defect_id: Optional[str] = None
    regression_test_coverage: Optional[float] = None

    # Assignment
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    owner: Optional[str] = None

    # Solutions
    workaround_available: Optional[bool] = None
    workaround_description: Optional[str] = None
    permanent_fix_available: Optional[bool] = None
    permanent_fix_description: Optional[str] = None
    permanent_fix_change_id: Optional[str] = None

    # Metadata
    tags: Optional[list[str]] = None
    custom_fields: Optional[dict[str, Any]] = None


class RCARequest(BaseModel):
    """Request for recording Root Cause Analysis."""

    rca_method: RCAMethod
    rca_notes: Optional[str] = None
    rca_data: Optional[dict[str, Any]] = None
    root_cause_identified: bool = False
    root_cause_description: Optional[str] = None
    root_cause_category: Optional[RootCauseCategory] = None
    root_cause_confidence: Optional[str] = Field(
        None, pattern="^(high|medium|low)$"
    )
    performed_by: Optional[str] = None


class DefectResponse(BaseModel):
    """Complete defect response."""

    id: str
    defect_number: str
    project_id: str
    title: str
    description: Optional[str]
    component: Optional[str]
    module: Optional[str]

    # Classification
    defect_type: str
    severity: str
    priority: str
    status: str
    reproducibility: str

    # Impact
    impact_level: str
    urgency: str
    affected_systems: Optional[list[str]]
    affected_users_estimated: Optional[int]
    business_impact_description: Optional[str]
    blast_radius: Optional[int]

    # Reproduction
    steps_to_reproduce: Optional[list[str]]
    expected_result: Optional[str]
    actual_result: Optional[str]
    environment_details: Optional[dict[str, str]]
    reproduction_frequency: Optional[str]

    # ODC
    odc_trigger: Optional[str]
    odc_defect_type: Optional[str]
    odc_origin: Optional[str]
    odc_impact_area: Optional[str]

    # RCA
    rca_performed: bool
    rca_method: Optional[str]
    rca_notes: Optional[str]
    root_cause_identified: bool
    root_cause_description: Optional[str]
    root_cause_category: Optional[str]
    rca_completed_at: Optional[datetime]
    rca_completed_by: Optional[str]

    # Security
    is_security_issue: bool
    cwe_category: Optional[str]
    cwe_id: Optional[str]
    cvss_score: Optional[float]
    cvss_severity: Optional[str]
    cve_ids: Optional[list[str]]

    # Quality metrics
    code_churn_percentage: Optional[float]
    cyclomatic_complexity: Optional[int]
    affected_lines_of_code: Optional[int]
    code_coverage_gap: Optional[float]
    technical_debt_hours: Optional[float]

    # Regression
    is_regression: bool
    regression_of_defect_id: Optional[str]
    regression_test_coverage: Optional[float]

    # Assignment
    assigned_to: Optional[str]
    assigned_team: Optional[str]
    owner: Optional[str]
    reported_by: str
    reporter_contact: Optional[str]

    # Dates
    target_resolution_date: Optional[datetime]
    actual_resolution_date: Optional[datetime]
    sla_hours: Optional[int]
    sla_status: Optional[str]

    # Closure
    resolution_type: Optional[str]
    closure_notes: Optional[str]
    closed_by: Optional[str]
    closed_at: Optional[datetime]

    # Metadata
    tags: Optional[list[str]]
    custom_fields: dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class DefectListResponse(BaseModel):
    """Condensed defect list item."""

    id: str
    defect_number: str
    project_id: str
    title: str
    status: str
    severity: str
    priority: str
    module: Optional[str]
    assigned_to: Optional[str]
    rca_performed: bool
    is_regression: bool
    is_security_issue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DefectMetricsResponse(BaseModel):
    """Defect metrics summary."""

    metric_date: datetime
    total_open_defects: int
    total_critical: int
    total_high: int
    total_medium: int
    total_low: int
    average_resolution_days: Optional[float]
    sla_compliance_percentage: Optional[float]
    escape_rate: Optional[float]
    regression_rate: Optional[float]
    rca_completion_rate: Optional[float]
    severity_distribution: dict[str, int]
    type_distribution: dict[str, int]
    module_defect_density: dict[str, float]
    security_defect_count: int
    hotspot_modules: list[dict[str, Any]]

    class Config:
        from_attributes = True
```

---

## Part 2: Service Layer for Analysis

### 2.1 Defect Analysis Service

```python
# /src/tracertm/services/defect_service.py

"""Service layer for defect analysis and metrics."""

from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.defect import (
    Defect, DefectActivity, DefectMetrics,
    Severity, Priority, DefectStatus
)


class DefectService:
    """Service for defect operations and analysis."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ===== QUALITY SCORING =====

    def calculate_report_quality_score(self, defect: Defect) -> int:
        """
        Calculate defect report quality score (0-100).

        Factors:
        - Title quality (15 points)
        - Description (20 points)
        - Reproduction steps (20 points)
        - Expected vs actual (15 points)
        - Environment details (15 points)
        - Supporting evidence (15 points)
        """
        score = 0

        # Title quality
        if defect.title and 20 <= len(defect.title) <= 500:
            score += 15

        # Description
        if defect.description and len(defect.description) > 50:
            score += 20

        # Reproduction steps
        if defect.steps_to_reproduce and len(defect.steps_to_reproduce) >= 3:
            score += 20

        # Expected vs actual
        if defect.expected_result and defect.actual_result:
            score += 15

        # Environment details
        if defect.environment_details and len(defect.environment_details) >= 3:
            score += 15

        # Supporting evidence
        if defect.attachments and len(defect.attachments) > 0:
            score += 15

        return min(score, 100)

    # ===== RISK ASSESSMENT =====

    def calculate_risk_level(self, defect: Defect) -> str:
        """
        Calculate overall risk level based on severity and reproducibility.

        Risk = Severity × Reproducibility
        """
        severity_map = {
            'critical': 4, 'high': 3, 'medium': 2, 'low': 1
        }
        reproducibility_map = {
            'always': 1, 'usually': 1, 'sometimes': 2,
            'rarely': 3, 'cannot': 4
        }

        severity_score = severity_map.get(defect.severity, 2)
        reproducibility_score = reproducibility_map.get(
            defect.reproducibility, 2
        )

        risk_score = severity_score * reproducibility_score

        if risk_score >= 8:
            return "CRITICAL"
        elif risk_score >= 5:
            return "HIGH"
        elif risk_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    # ===== SLA MONITORING =====

    def calculate_sla_status(self, defect: Defect) -> str:
        """
        Check defect SLA status.

        Critical: 24 hours
        High: 72 hours (3 days)
        Medium: 240 hours (10 days)
        Low: 720 hours (30 days)
        """
        if defect.closed_at:
            return "CLOSED"

        sla_hours_map = {
            'critical': 24,
            'high': 72,
            'medium': 240,
            'low': 720
        }

        hours_allowed = sla_hours_map.get(defect.severity, 240)
        hours_elapsed = (
            datetime.now(UTC) - defect.created_at
        ).total_seconds() / 3600

        if hours_elapsed > hours_allowed:
            return "BREACHED"
        elif hours_elapsed > hours_allowed * 0.75:
            return "AT_RISK"
        else:
            return "ON_TRACK"

    # ===== DEFECT CLUSTERING =====

    async def calculate_module_defect_density(
        self, project_id: str
    ) -> dict[str, float]:
        """Calculate defect density (defects/KLOC) by module."""
        query = (
            select(
                Defect.module,
                func.count(Defect.id).label("defect_count"),
                func.avg(Defect.affected_lines_of_code).label("avg_loc")
            )
            .where(
                Defect.project_id == project_id,
                Defect.deleted_at.is_(None)
            )
            .group_by(Defect.module)
        )

        result = await self.session.execute(query)
        densities = {}

        for row in result:
            module = row[0]
            defect_count = row[1]
            avg_loc = row[2] or 1000  # Default if not available

            density = (defect_count / (avg_loc / 1000)) if avg_loc > 0 else 0
            densities[module] = density

        return densities

    async def identify_hotspot_modules(
        self, project_id: str, top_n: int = 10
    ) -> list[dict[str, Any]]:
        """
        Identify hotspot modules using Pareto analysis.

        Returns top N modules by defect count.
        """
        query = (
            select(
                Defect.module,
                func.count(Defect.id).label("defect_count")
            )
            .where(
                Defect.project_id == project_id,
                Defect.deleted_at.is_(None),
                Defect.module.is_not(None)
            )
            .group_by(Defect.module)
            .order_by(func.count(Defect.id).desc())
            .limit(top_n)
        )

        result = await self.session.execute(query)

        total_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.deleted_at.is_(None)
            )
        )
        total_result = await self.session.execute(total_query)
        total_defects = total_result.scalar()

        hotspots = []
        cumulative_pct = 0

        for idx, row in enumerate(result):
            module = row[0]
            count = row[1]
            pct = (count / total_defects * 100) if total_defects > 0 else 0
            cumulative_pct += pct

            hotspots.append({
                "rank": idx + 1,
                "module": module,
                "defect_count": count,
                "percentage": round(pct, 2),
                "cumulative_percentage": round(cumulative_pct, 2),
                "in_vital_few": cumulative_pct <= 80
            })

        return hotspots

    # ===== REGRESSION ANALYSIS =====

    async def calculate_regression_rate(
        self, project_id: str, days: int = 30
    ) -> float:
        """
        Calculate fix-induced defect rate.

        FER = (Regression defects in period) / (Defects fixed in period)
        """
        since = datetime.now(UTC) - __import__('datetime').timedelta(days=days)

        fixed_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.status == DefectStatus.CLOSED.value,
                Defect.closed_at >= since,
                Defect.deleted_at.is_(None)
            )
        )
        fixed_result = await self.session.execute(fixed_query)
        fixed_count = fixed_result.scalar()

        regression_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.is_regression.is_(True),
                Defect.created_at >= since,
                Defect.deleted_at.is_(None)
            )
        )
        regression_result = await self.session.execute(regression_query)
        regression_count = regression_result.scalar()

        if fixed_count == 0:
            return 0.0

        return (regression_count / fixed_count) * 100

    async def get_defect_escape_rate(
        self, project_id: str, days: int = 90
    ) -> float:
        """
        Calculate defect escape rate.

        Escape Rate = (Production defects) / (Total defects)
        """
        since = datetime.now(UTC) - __import__('datetime').timedelta(days=days)

        total_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.created_at >= since,
                Defect.deleted_at.is_(None)
            )
        )
        total_result = await self.session.execute(total_query)
        total_count = total_result.scalar()

        escape_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.odc_trigger == 'production',
                Defect.created_at >= since,
                Defect.deleted_at.is_(None)
            )
        )
        escape_result = await self.session.execute(escape_query)
        escape_count = escape_result.scalar()

        if total_count == 0:
            return 0.0

        return (escape_count / total_count) * 100

    # ===== RCA ANALYSIS =====

    async def get_rca_statistics(
        self, project_id: str
    ) -> dict[str, Any]:
        """Get Root Cause Analysis statistics."""
        total_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.deleted_at.is_(None)
            )
        )
        total_result = await self.session.execute(total_query)
        total_defects = total_result.scalar()

        rca_done_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.rca_performed.is_(True),
                Defect.deleted_at.is_(None)
            )
        )
        rca_done_result = await self.session.execute(rca_done_query)
        rca_done = rca_done_result.scalar()

        root_cause_query = (
            select(func.count(Defect.id))
            .where(
                Defect.project_id == project_id,
                Defect.root_cause_identified.is_(True),
                Defect.deleted_at.is_(None)
            )
        )
        root_cause_result = await self.session.execute(root_cause_query)
        root_cause_found = root_cause_result.scalar()

        return {
            "total_defects": total_defects,
            "rca_performed_count": rca_done,
            "rca_completion_rate": (rca_done / total_defects * 100) if total_defects > 0 else 0,
            "root_cause_identification_rate": (root_cause_found / total_defects * 100) if total_defects > 0 else 0,
        }

    # ===== METRICS AGGREGATION =====

    async def compute_project_metrics(
        self, project_id: str, metric_date: Optional[datetime] = None
    ) -> DefectMetrics:
        """Compute comprehensive defect metrics for project."""
        if metric_date is None:
            metric_date = datetime.now(UTC)

        # Count by severity
        severity_counts = {}
        for severity in ['critical', 'high', 'medium', 'low']:
            query = (
                select(func.count(Defect.id))
                .where(
                    Defect.project_id == project_id,
                    Defect.severity == severity,
                    Defect.deleted_at.is_(None)
                )
            )
            result = await self.session.execute(query)
            severity_counts[severity] = result.scalar() or 0

        # Get hotspot modules
        hotspots = await self.identify_hotspot_modules(project_id, top_n=10)

        # Calculate metrics
        escape_rate = await self.get_defect_escape_rate(project_id)
        regression_rate = await self.calculate_regression_rate(project_id)
        rca_stats = await self.get_rca_statistics(project_id)

        # Create metrics record
        metrics = DefectMetrics(
            id=str(uuid4()),
            project_id=project_id,
            metric_date=metric_date,
            total_open_defects=severity_counts['critical'] + severity_counts['high'] + severity_counts['medium'] + severity_counts['low'],
            total_critical=severity_counts['critical'],
            total_high=severity_counts['high'],
            total_medium=severity_counts['medium'],
            total_low=severity_counts['low'],
            escape_rate=escape_rate,
            regression_rate=regression_rate,
            rca_completion_rate=rca_stats["rca_completion_rate"],
            severity_distribution=severity_counts,
            hotspot_modules=hotspots,
        )

        return metrics
```

---

## Part 3: API Routes

### 3.1 Defect Router

```python
# /src/tracertm/api/routers/defects.py

"""API routes for defect management."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_session, get_current_user
from tracertm.models.defect import Defect
from tracertm.schemas.defect import (
    DefectCreate, DefectUpdate, DefectResponse,
    DefectListResponse, RCARequest, DefectMetricsResponse
)
from tracertm.services.defect_service import DefectService

router = APIRouter(prefix="/defects", tags=["defects"])


@router.post("/{project_id}", response_model=DefectResponse)
async def create_defect(
    project_id: str,
    data: DefectCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
) -> DefectResponse:
    """Create a new defect."""
    from uuid import uuid4

    defect = Defect(
        id=str(uuid4()),
        defect_number=f"DEF-{project_id[:8]}-{str(uuid4())[:8]}",
        project_id=project_id,
        **data.dict(exclude_unset=True)
    )

    session.add(defect)
    await session.flush()
    await session.refresh(defect)

    return DefectResponse.from_orm(defect)


@router.get("/{project_id}", response_model=list[DefectListResponse])
async def list_defects(
    project_id: str,
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
) -> list[DefectListResponse]:
    """List defects with filtering."""
    from sqlalchemy import select

    query = select(Defect).where(
        Defect.project_id == project_id,
        Defect.deleted_at.is_(None)
    )

    if status:
        query = query.where(Defect.status == status)
    if severity:
        query = query.where(Defect.severity == severity)
    if module:
        query = query.where(Defect.module == module)
    if assigned_to:
        query = query.where(Defect.assigned_to == assigned_to)

    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    defects = result.scalars().all()

    return [DefectListResponse.from_orm(d) for d in defects]


@router.get("/{project_id}/{defect_id}", response_model=DefectResponse)
async def get_defect(
    project_id: str,
    defect_id: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
) -> DefectResponse:
    """Get a single defect."""
    from sqlalchemy import select

    result = await session.execute(
        select(Defect).where(
            Defect.id == defect_id,
            Defect.project_id == project_id,
            Defect.deleted_at.is_(None)
        )
    )
    defect = result.scalar_one_or_none()

    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")

    return DefectResponse.from_orm(defect)


@router.patch("/{project_id}/{defect_id}", response_model=DefectResponse)
async def update_defect(
    project_id: str,
    defect_id: str,
    data: DefectUpdate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
) -> DefectResponse:
    """Update a defect."""
    from sqlalchemy import select

    result = await session.execute(
        select(Defect).where(
            Defect.id == defect_id,
            Defect.project_id == project_id
        )
    )
    defect = result.scalar_one_or_none()

    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(defect, key, value)

    defect.version += 1
    await session.flush()
    await session.refresh(defect)

    return DefectResponse.from_orm(defect)


@router.post("/{project_id}/{defect_id}/rca")
async def record_rca(
    project_id: str,
    defect_id: str,
    data: RCARequest,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
) -> DefectResponse:
    """Record Root Cause Analysis."""
    from datetime import UTC, datetime
    from sqlalchemy import select

    result = await session.execute(
        select(Defect).where(
            Defect.id == defect_id,
            Defect.project_id == project_id
        )
    )
    defect = result.scalar_one_or_none()

    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")

    defect.rca_performed = True
    defect.rca_method = data.rca_method.value
    defect.rca_notes = data.rca_notes
    defect.rca_data = data.rca_data
    defect.root_cause_identified = data.root_cause_identified
    defect.root_cause_description = data.root_cause_description
    defect.root_cause_category = data.root_cause_category.value if data.root_cause_category else None
    defect.root_cause_confidence = data.root_cause_confidence
    defect.rca_completed_at = datetime.now(UTC)
    defect.rca_completed_by = current_user.id

    await session.flush()
    await session.refresh(defect)

    return DefectResponse.from_orm(defect)


@router.get("/{project_id}/metrics/summary")
async def get_project_metrics(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
) -> DefectMetricsResponse:
    """Get project defect metrics."""
    service = DefectService(session)
    metrics = await service.compute_project_metrics(project_id)

    session.add(metrics)
    await session.flush()

    return DefectMetricsResponse.from_orm(metrics)


@router.get("/{project_id}/analysis/hotspots")
async def get_hotspot_modules(
    project_id: str,
    top_n: int = Query(10, le=50),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):
    """Identify defect hotspot modules (Pareto analysis)."""
    service = DefectService(session)
    hotspots = await service.identify_hotspot_modules(project_id, top_n)
    return {"hotspots": hotspots}
```

---

## Implementation Checklist

**Phase 1 (Weeks 1-4): Core**
- [ ] Create enhanced `Defect` model with ISTQB attributes
- [ ] Create `DefectMetrics` model for aggregated data
- [ ] Create Pydantic schemas
- [ ] Implement basic CRUD operations
- [ ] Create repository layer
- [ ] Set up unit tests

**Phase 2 (Weeks 5-8): Analysis Services**
- [ ] Implement `DefectService` with quality scoring
- [ ] Implement SLA monitoring
- [ ] Implement defect clustering (Pareto analysis)
- [ ] Implement RCA statistics
- [ ] Create API endpoints for defect operations
- [ ] Create analytics endpoints

**Phase 3 (Weeks 9-12): Advanced Features**
- [ ] Integrate security classification (CVE/CVSS/CWE)
- [ ] Add regression tracking
- [ ] Implement predictive metrics
- [ ] Create dashboards
- [ ] Add data migration scripts

**Phase 4 (Month 4+): Optimization**
- [ ] Performance tuning for large datasets
- [ ] Reporting improvements
- [ ] Integration with external tools
- [ ] Training and documentation

---

## Database Migration

Create Alembic migration for new tables:

```bash
alembic revision --autogenerate -m "Add comprehensive defect specification"
```

This will generate migration scripts that can be reviewed and applied.

---

## Next Steps

1. Review and customize enumerations for your domain
2. Implement repository layer for database operations
3. Create comprehensive test suite
4. Design UI components for defect creation/viewing
5. Set up automated metric computation jobs
6. Create dashboards and reports

