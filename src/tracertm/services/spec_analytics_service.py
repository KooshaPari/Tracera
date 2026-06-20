"""Enhanced Specification Analytics Service V2.

A comprehensive, deeply-integrated analytics engine for specification objects
inspired by smart contract/blockchain/NFT entity patterns.

Based on extensive research from:
- IBM DOORS Next, Jama Connect, Polarion ALM enterprise patterns
- ERC-721/1155, Merkle Trees, IPFS content addressing
- Z3 Theorem Prover, Alloy, TLA+ formal methods
- ISO 29148, ISO 26262, DO-178C, IEC 62304 standards
- ISTQB, ODC, CVSS defect classification
- SAFe WSJF, RICE, Cost of Delay prioritization
- Metamorphic testing, property-based testing, mutation testing
- Graph algorithms (Neo4j patterns, knowledge graph embeddings)
- ML/AI: sentence-transformers, spaCy NER, CodeBERT

This service provides:
1. EARS Pattern Analysis with formal validation
2. ISO 29148 Quality Scoring (8 dimensions)
3. Cryptographic Version Chain (blockchain-style audit)
4. Merkle Proof Generation for baseline verification
5. Content Addressing (IPFS-style CIDs)
6. Flakiness Detection (Meta probabilistic model)
7. Orthogonal Defect Classification (IBM ODC)
8. CVSS Security Scoring
9. WSJF/RICE/MoSCoW Prioritization
10. Semantic Similarity Detection
11. Graph-based Impact Analysis
12. Suspect Link Detection
13. Formal Constraint Verification (Z3-style)
14. Coverage Gap Analysis
15. Test Oracle Pattern Detection


Functional Requirements: FR-QUAL-010
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from collections import Counter
from datetime import UTC, datetime
from enum import StrEnum
from itertools import starmap
from typing import Any, ClassVar

from pydantic import BaseModel, Field

# Threshold constants for analysis
_MIN_SAMPLES_FOR_METRICS = 2
_MIN_TEST_COUNT_THRESHOLD = 10
_RECENT_ITEMS_THRESHOLD = 20
_SMALL_PROJECT_SIZE = 30
_MEDIUM_PROJECT_SIZE = 50
_MAX_DEPTH_THRESHOLD = 3
_TREND_MIN_ITEMS = 5
_GAP_ANALYSIS_THRESHOLD = 0.90
_QUALITY_EXCELLENT = 0.90
_QUALITY_GOOD = 0.80
_QUALITY_FAIR = 0.70
_QUALITY_POOR = 0.60
_SIMILARITY_HIGH = 0.95
_SIMILARITY_MEDIUM = 0.80
_SIMILARITY_LOW = 0.60
_SCORE_DECIMAL_PLACES = 0.01
_SCORE_LOW_DECIMAL = 0.05
_SCORE_MEDIUM_LOW = 0.15
_SCORE_MEDIUM = 0.30

# =============================================================================
# CONSTANTS - Thresholds and Limits
# =============================================================================

QUALITY_IMPROVEMENT_THRESHOLD = 0.7
QUALITY_MIN_LENGTH = 30
QUALITY_AND_COUNT_THRESHOLD = 2

GRADE_A_THRESHOLD = 0.90
GRADE_B_THRESHOLD = 0.80
GRADE_C_THRESHOLD = 0.70
GRADE_D_THRESHOLD = 0.60

FLAKINESS_VARIANCE_MIN_SAMPLES = 2
FLAKINESS_QUARANTINE_FAILURES = 3
FLAKINESS_QUARANTINE_SCORE = 0.15
FLAKINESS_QUARANTINE_RATE = 0.1
FLAKINESS_ENTROPY_MIN_LENGTH = 2
FLAKINESS_TRANSITION_MIN_LENGTH = 2
FLAKINESS_DURATION_MIN_SAMPLES = 5
FLAKINESS_DURATION_CV_THRESHOLD = 0.5
FLAKINESS_RACE_MIN_LENGTH = 5
FLAKINESS_STABLE_PASS_THRESHOLD = 15
FLAKINESS_STABLE_FAILURE_RATE = 0.1
FLAKINESS_BROKEN_FAILURE_THRESHOLD = 8
FLAKINESS_VARIANCE_THRESHOLD = 0.5
FLAKINESS_CLUSTER_MIN_FAILURES = 2

FLAKINESS_SEVERITY_STABLE_MAX = 0.01
FLAKINESS_SEVERITY_LOW_MAX = 0.05
FLAKINESS_SEVERITY_MEDIUM_MAX = 0.15
FLAKINESS_SEVERITY_HIGH_MAX = 0.30

# =============================================================================
# ENUMS - Comprehensive Classification Systems
# =============================================================================


class EARSPatternType(StrEnum):
    """EARS (Easy Approach to Requirements Syntax) pattern types."""

    UBIQUITOUS = "ubiquitous"  # "The system shall..."
    EVENT_DRIVEN = "event_driven"  # "When <event>, the system shall..."
    STATE_DRIVEN = "state_driven"  # "While <state>, the system shall..."
    OPTIONAL = "optional"  # "Where <feature>, the system shall..."
    COMPLEX = "complex"  # Combination of triggers
    UNWANTED = "unwanted"  # "If <condition>, the system shall NOT..."
    UNCLASSIFIED = "unclassified"


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
    CORRECTNESS = "correctness"


class VerificationMethod(StrEnum):
    """ISO 29148 verification methods (IDAT)."""

    INSPECTION = "inspection"
    DEMONSTRATION = "demonstration"
    ANALYSIS = "analysis"
    TEST = "test"


class ODCDefectType(StrEnum):
    """IBM Orthogonal Defect Classification - Defect Types."""

    FUNCTION = "function"  # Missing/incorrect function
    INTERFACE = "interface"  # Module interface issues
    CHECKING = "checking"  # Missing/incorrect validation
    ASSIGNMENT = "assignment"  # Incorrect variable assignment
    TIMING = "timing"  # Race conditions, deadlocks
    BUILD = "build"  # Build/package/merge issues
    DOCUMENTATION = "documentation"  # Doc errors affecting behavior
    ALGORITHM = "algorithm"  # Algorithm/logic errors


class ODCTrigger(StrEnum):
    """IBM ODC - What triggered the defect discovery."""

    REVIEW = "review"
    WALKTHROUGH = "walkthrough"
    UNIT_TEST = "unit_test"
    FUNCTION_TEST = "function_test"
    SYSTEM_TEST = "system_test"
    REGRESSION_TEST = "regression_test"
    CUSTOMER_FOUND = "customer_found"
    STATIC_ANALYSIS = "static_analysis"


class ODCImpact(StrEnum):
    """IBM ODC - Customer impact category."""

    INSTALLABILITY = "installability"
    SERVICEABILITY = "serviceability"
    STANDARDS = "standards"
    INTEGRITY = "integrity"
    SECURITY = "security"
    PERFORMANCE = "performance"
    REQUIREMENTS = "requirements"
    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"
    CAPABILITY = "capability"
    RELIABILITY = "reliability"
    MIGRATION = "migration"


class FlakinessSeverity(StrEnum):
    """Flakiness severity levels (Meta model)."""

    STABLE = "stable"  # < 1% flakiness
    LOW = "low"  # 1-5%
    MEDIUM = "medium"  # 5-15%
    HIGH = "high"  # 15-30%
    CRITICAL = "critical"  # > _SMALL_PROJECT_SIZE%


class FlakinessPattern(StrEnum):
    """Detected flakiness patterns."""

    ORDER_DEPENDENT = "order_dependent"
    TIME_DEPENDENT = "time_dependent"
    RESOURCE_DEPENDENT = "resource_dependent"
    ENVIRONMENT_DEPENDENT = "environment_dependent"
    DATA_DEPENDENT = "data_dependent"
    RACE_CONDITION = "race_condition"
    EXTERNAL_DEPENDENCY = "external_dependency"
    MEMORY_PRESSURE = "memory_pressure"
    NETWORK_INSTABILITY = "network_instability"
    ASYNC_TIMING = "async_timing"


class TestOracleType(StrEnum):
    """Test oracle pattern types."""

    EXPECTED_OUTPUT = "expected_output"
    METAMORPHIC = "metamorphic"
    PROPERTY_BASED = "property_based"
    DIFFERENTIAL = "differential"
    REGRESSION = "regression"
    STATISTICAL = "statistical"
    HUMAN = "human"
    CONTRACT = "contract"


class CoverageType(StrEnum):
    """Coverage measurement types (DO-178C levels)."""

    STATEMENT = "statement"
    BRANCH = "branch"
    CONDITION = "condition"
    MCDC = "mcdc"  # Modified Condition/Decision Coverage
    PATH = "path"
    MUTATION = "mutation"


class SuspectLinkReason(StrEnum):
    """Reasons for marking a trace link as suspect."""

    UPSTREAM_MODIFIED = "upstream_modified"
    CONTENT_CHANGED = "content_changed"
    STATUS_CHANGED = "status_changed"
    DEPENDENCY_BROKEN = "dependency_broken"
    VERSION_MISMATCH = "version_mismatch"
    COVERAGE_GAP = "coverage_gap"


class SafetyLevel(StrEnum):
    """Safety integrity levels (combined from multiple standards)."""

    # ISO 26262 Automotive
    ASIL_D = "asil_d"
    ASIL_C = "asil_c"
    ASIL_B = "asil_b"
    ASIL_A = "asil_a"
    QM = "qm"
    # DO-178C Airborne
    DAL_A = "dal_a"
    DAL_B = "dal_b"
    DAL_C = "dal_c"
    DAL_D = "dal_d"
    DAL_E = "dal_e"
    # IEC 62304 Medical
    CLASS_A = "class_a"
    CLASS_B = "class_b"
    CLASS_C = "class_c"
    # Generic
    NONE = "none"


class PriorityFramework(StrEnum):
    """Prioritization frameworks."""

    WSJF = "wsjf"  # Weighted Shortest Job First (SAFe)
    RICE = "rice"  # Reach, Impact, Confidence, Effort
    MOSCOW = "moscow"  # Must, Should, Could, Won't
    KANO = "kano"  # Basic, Performance, Excitement
    ICE = "ice"  # Impact, Confidence, Ease
    VALUE_VS_EFFORT = "value_vs_effort"
    COST_OF_DELAY = "cost_of_delay"


# =============================================================================
# PYDANTIC MODELS - Rich Structured Data
# =============================================================================


class EARSComponents(BaseModel):
    """Extracted EARS components from a requirement."""

    trigger: str | None = None
    precondition: str | None = None
    postcondition: str | None = None
    system_response: str | None = None
    constraint: str | None = None
    actor: str | None = None
    system_name: str | None = None
    negation: bool = False


class EARSAnalysisResult(BaseModel):
    """Complete EARS pattern analysis result."""

    pattern_type: EARSPatternType
    confidence: float = Field(ge=0, le=1)
    components: EARSComponents
    is_valid: bool
    validation_issues: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    formal_structure: str | None = None  # Normalized EARS form
    ambiguous_terms: list[str] = Field(default_factory=list)
    incomplete_markers: list[str] = Field(default_factory=list)


class QualityIssue(BaseModel):
    """A detected quality issue with full context."""

    dimension: QualityDimension
    severity: str = Field(pattern="^(error|warning|info)$")
    message: str
    suggestion: str | None = None
    position: int | None = None
    context: str | None = None
    rule_id: str | None = None


class QualityScore(BaseModel):
    """Comprehensive quality scoring result."""

    dimension_scores: dict[str, float]
    overall_score: float
    issues: list[QualityIssue]
    grade: str  # A, B, C, D, F
    percentile: int | None = None
    improvement_priority: list[str] = Field(default_factory=list)


class VersionBlock(BaseModel):
    """Immutable version record with cryptographic linking (blockchain-style)."""

    block_id: str  # SHA-256 hash
    previous_block_id: str | None
    timestamp: datetime
    author_id: str
    change_type: str
    change_summary: str
    content_hash: str
    merkle_root: str | None = None
    signature: str | None = None
    nonce: int | None = None


class MerkleProof(BaseModel):
    """Merkle proof for verifying item inclusion in a baseline."""

    leaf_hash: str
    proof_path: list[tuple[str, str]]  # (hash, direction: 'left'|'right')
    root_hash: str
    item_id: str
    baseline_id: str


class ContentAddress(BaseModel):
    """IPFS-style content identifier."""

    cid: str  # Content Identifier
    algorithm: str = "sha256"
    size_bytes: int
    content_type: str
    created_at: datetime


class ODCClassification(BaseModel):
    """Complete IBM ODC classification for a defect."""

    defect_type: ODCDefectType
    trigger: ODCTrigger
    impact: ODCImpact
    qualifier: str | None = None  # missing, incorrect, extraneous
    age: str | None = None  # new, old, rewritten
    source: str | None = None  # vendor, in-house, ported
    confidence: float = Field(ge=0, le=1, default=1.0)


class CVSSScore(BaseModel):
    """CVSS v3.1 security vulnerability scoring."""

    base_score: float = Field(ge=0, le=10)
    temporal_score: float | None = Field(None, ge=0, le=10)
    environmental_score: float | None = Field(None, ge=0, le=10)
    severity: str  # None, Low, Medium, High, Critical
    vector_string: str
    attack_vector: str
    attack_complexity: str
    privileges_required: str
    user_interaction: str
    scope: str
    confidentiality_impact: str
    integrity_impact: str
    availability_impact: str


class FlakinessAnalysis(BaseModel):
    """Complete flakiness analysis result."""

    flakiness_score: float = Field(ge=0, le=1)
    severity: FlakinessSeverity
    detected_patterns: list[FlakinessPattern] = Field(default_factory=list)
    failure_rate_24h: float | None = None
    failure_rate_7d: float | None = None
    failure_rate_30d: float | None = None
    entropy_score: float
    transition_count: int
    consecutive_failures_max: int
    consecutive_passes_max: int
    quarantine_recommended: bool
    suggested_fix_category: str | None = None
    confidence: float = Field(ge=0, le=1)
    run_time_variance: float | None = None
    failure_clustering_score: float | None = None


class WSJFScore(BaseModel):
    """WSJF (Weighted Shortest Job First) scoring from SAFe."""

    business_value: int = Field(ge=1, le=10)
    time_criticality: int = Field(ge=1, le=10)
    risk_reduction: int = Field(ge=1, le=10)
    opportunity_enablement: int = Field(ge=1, le=10, default=1)
    job_size: int = Field(ge=1, le=21)  # Fibonacci
    cost_of_delay: float
    wsjf_score: float
    percentile: int | None = None
    rank: int | None = None


class RICEScore(BaseModel):
    """RICE scoring model."""

    reach: int
    impact: float = Field(ge=0.25, le=3)
    confidence: float = Field(ge=0, le=1)
    effort: int
    rice_score: float
    percentile: int | None = None
    rank: int | None = None


class SemanticSimilarity(BaseModel):
    """Semantic similarity between items."""

    source_id: str
    target_id: str
    similarity_score: float = Field(ge=0, le=1)
    similarity_type: str  # duplicate, related, contradicts, implements
    embedding_model: str
    matched_phrases: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ImpactAnalysisResult(BaseModel):
    """Graph-based impact analysis result."""

    source_item_id: str
    direct_impacts: list[str] = Field(default_factory=list)
    transitive_impacts: list[str] = Field(default_factory=list)
    impact_depth: int
    blast_radius: int
    critical_path_items: list[str] = Field(default_factory=list)
    affected_tests: list[str] = Field(default_factory=list)
    affected_documents: list[str] = Field(default_factory=list)
    risk_score: float = Field(ge=0, le=100)
    estimated_effort_hours: float | None = None


class SuspectLink(BaseModel):
    """A suspect traceability link requiring review."""

    link_id: str
    source_id: str
    target_id: str
    reason: SuspectLinkReason
    detected_at: datetime
    source_version_before: int
    source_version_after: int
    change_summary: str
    requires_verification: bool = True
    auto_resolvable: bool = False


class CoverageGap(BaseModel):
    """Identified coverage gap in traceability."""

    gap_type: str  # no_tests, no_verification, orphaned_test, missing_link
    item_id: str
    item_type: str
    severity: str  # critical, high, medium, low
    expected_coverage_type: CoverageType | None = None
    current_coverage: float
    required_coverage: float
    safety_level: SafetyLevel | None = None
    suggestion: str


class FormalConstraint(BaseModel):
    """A formal constraint for Z3-style verification."""

    constraint_id: str
    expression: str  # SMT-LIB or custom DSL
    constraint_type: str  # equality, inequality, range, implies, iff
    variables: list[str]
    is_satisfiable: bool | None = None
    counter_example: dict[str, Any] | None = None
    verification_time_ms: int | None = None


class MetamorphicRelation(BaseModel):
    """Metamorphic testing relation definition."""

    relation_id: str
    name: str
    description: str
    source_transformation: str
    expected_output_relation: str
    applicable_to: list[str]  # test types
    confidence: float = Field(ge=0, le=1)


# =============================================================================
# ANALYZERS - Core Analysis Logic
# =============================================================================


class EARSPatternAnalyzer:
    """Advanced EARS pattern analyzer with formal structure extraction.

    Implements the full EARS specification from INCOSE with extensions
    for complex patterns and formal verification readiness.
    """

    # Pattern regexes ordered by specificity
    PATTERNS: ClassVar[dict[EARSPatternType, re.Pattern[str]]] = {
        EARSPatternType.UNWANTED: re.compile(
            r"^(?:if|when)\s+(.+?),?\s+(?:then\s+)?(?:the\s+)?(\w+)\s+shall\s+(?:not|never)\s+(.+)$",
            re.IGNORECASE,
        ),
        EARSPatternType.COMPLEX: re.compile(
            r"^(?:while\s+(.+?)\s+)?(?:when|if|upon)\s+(.+?),?\s+(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE,
        ),
        EARSPatternType.STATE_DRIVEN: re.compile(
            r"^(?:while|during|as\s+long\s+as)\s+(.+?),?\s+(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE,
        ),
        EARSPatternType.EVENT_DRIVEN: re.compile(
            r"^(?:when|upon|after|once|if)\s+(.+?),?\s+(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE,
        ),
        EARSPatternType.OPTIONAL: re.compile(
            r"^(?:where|if|in\s+case)\s+(.+?)\s+(?:is\s+)?(?:enabled|configured|available|supported),?\s+(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE,
        ),
        EARSPatternType.UBIQUITOUS: re.compile(r"^(?:the\s+)?(\w+)\s+shall\s+(.+)$", re.IGNORECASE),
    }

    # Ambiguous words from IEEE 830 and ISO 29148
    AMBIGUOUS_WORDS = frozenset({
        "appropriate",
        "adequate",
        "reasonable",
        "sufficient",
        "timely",
        "easy",
        "simple",
        "fast",
        "quick",
        "efficient",
        "effective",
        "user-friendly",
        "flexible",
        "scalable",
        "robust",
        "secure",
        "good",
        "bad",
        "better",
        "best",
        "optimal",
        "minimal",
        "maximum",
        "some",
        "several",
        "many",
        "few",
        "various",
        "etc",
        "and/or",
        "normally",
        "usually",
        "typically",
        "generally",
        "often",
        "may",
        "might",
        "could",
        "possibly",
        "perhaps",
        "probably",
        "as appropriate",
        "as needed",
        "if necessary",
        "when required",
        "similar",
        "etc.",
        "and so on",
        "such as",
        "for example",
    })

    # Incomplete markers
    INCOMPLETE_MARKERS = frozenset({
        "tbd",
        "tba",
        "todo",
        "fixme",
        "xxx",
        "???",
        "...",
        "placeholder",
        "pending",
        "to be determined",
        "to be defined",
    })

    # Weak modals
    WEAK_MODALS = frozenset({"may", "might", "could", "should", "would"})

    def analyze(self, requirement_text: str) -> EARSAnalysisResult:
        """Perform complete EARS analysis on a requirement."""
        text = requirement_text.strip()
        text_lower = text.lower()

        issues = []
        suggestions = []

        # Find ambiguous terms
        ambiguous = [w for w in self.AMBIGUOUS_WORDS if w in text_lower]

        # Find incomplete markers
        incomplete = [m for m in self.INCOMPLETE_MARKERS if m in text_lower]

        # Try pattern matching
        for pattern_type, pattern in self.PATTERNS.items():
            match = pattern.match(text)
            if match:
                components = self._extract_components(pattern_type, match)
                confidence = self._calculate_confidence(text, pattern_type, components, ambiguous, incomplete)

                # Validate
                validation_issues = self._validate(text, components, ambiguous, incomplete)
                issues.extend(validation_issues)

                if validation_issues:
                    suggestions.extend(self._generate_suggestions(validation_issues))

                # Generate formal structure
                formal_structure = self._to_formal_structure(pattern_type, components)

                return EARSAnalysisResult(
                    pattern_type=pattern_type,
                    confidence=confidence,
                    components=components,
                    is_valid=len([i for i in validation_issues if "error" in i.lower()]) == 0,
                    validation_issues=validation_issues,
                    improvement_suggestions=suggestions,
                    formal_structure=formal_structure,
                    ambiguous_terms=ambiguous,
                    incomplete_markers=incomplete,
                )

        # No pattern matched
        return EARSAnalysisResult(
            pattern_type=EARSPatternType.UNCLASSIFIED,
            confidence=0.0,
            components=EARSComponents(),
            is_valid=False,
            validation_issues=["Requirement does not match any EARS pattern"],
            improvement_suggestions=[
                "Restructure as: 'The <system> shall <action>'",
                "For conditions: 'When <trigger>, the <system> shall <action>'",
                "For states: 'While <state>, the <system> shall <action>'",
            ],
            ambiguous_terms=ambiguous,
            incomplete_markers=incomplete,
        )

    def _extract_components(self, pattern_type: EARSPatternType, match: re.Match[str]) -> EARSComponents:
        """Extract structured components from regex match."""
        groups = match.groups()

        if pattern_type == EARSPatternType.UBIQUITOUS:
            return EARSComponents(
                system_name=groups[0] if len(groups) > 0 else None,
                system_response=groups[1] if len(groups) > 1 else None,
            )
        if pattern_type == EARSPatternType.EVENT_DRIVEN:
            return EARSComponents(
                trigger=groups[0] if len(groups) > 0 else None,
                system_name=groups[1] if len(groups) > 1 else None,
                system_response=groups[2] if len(groups) > _MIN_SAMPLES_FOR_METRICS else None,
            )
        if pattern_type == EARSPatternType.STATE_DRIVEN:
            return EARSComponents(
                precondition=groups[0] if len(groups) > 0 else None,
                system_name=groups[1] if len(groups) > 1 else None,
                system_response=groups[2] if len(groups) > _MIN_SAMPLES_FOR_METRICS else None,
            )
        if pattern_type == EARSPatternType.OPTIONAL:
            return EARSComponents(
                constraint=groups[0] if len(groups) > 0 else None,
                system_name=groups[1] if len(groups) > 1 else None,
                system_response=groups[2] if len(groups) > _MIN_SAMPLES_FOR_METRICS else None,
            )
        if pattern_type == EARSPatternType.UNWANTED:
            return EARSComponents(
                precondition=groups[0] if len(groups) > 0 else None,
                system_name=groups[1] if len(groups) > 1 else None,
                postcondition=groups[2] if len(groups) > _MIN_SAMPLES_FOR_METRICS else None,
                negation=True,
            )
        if pattern_type == EARSPatternType.COMPLEX:
            return EARSComponents(
                precondition=groups[0] if len(groups) > 0 and groups[0] else None,
                trigger=groups[1] if len(groups) > 1 else None,
                system_name=groups[2] if len(groups) > _MIN_SAMPLES_FOR_METRICS else None,
                system_response=groups[3] if len(groups) > 3 else None,
            )

        return EARSComponents()

    def _calculate_confidence(
        self,
        text: str,
        _pattern_type: EARSPatternType,
        components: EARSComponents,
        ambiguous: list[str],
        incomplete: list[str],
    ) -> float:
        """Calculate confidence score for pattern match."""
        confidence = 0.6  # Base for any match

        # Boost for "shall"
        if "shall" in text.lower():
            confidence += 0.15

        # Boost for clear system identification
        if components.system_name and len(components.system_name) > _MIN_SAMPLES_FOR_METRICS:
            confidence += 0.1

        # Boost for substantive response
        if components.system_response and len(components.system_response) > 15:
            confidence += 0.1

        # Penalties
        confidence -= len(ambiguous) * 0.03
        confidence -= len(incomplete) * 0.15

        # Penalty for weak modals
        text_lower = text.lower()
        weak_count = sum(1 for w in self.WEAK_MODALS if f" {w} " in f" {text_lower} ")
        confidence -= weak_count * 0.05

        return max(0.0, min(1.0, confidence))

    def _validate(
        self,
        text: str,
        _components: EARSComponents,
        ambiguous: list[str],
        incomplete: list[str],
    ) -> list[str]:
        """Validate requirement for quality issues."""
        issues = []

        if ambiguous:
            issues.append(f"Ambiguous terms: {', '.join(ambiguous[:5])}")

        if incomplete:
            issues.append(f"[ERROR] Incomplete markers: {', '.join(incomplete)}")

        # Check for compound requirements
        if text.count(" and ") > _MIN_SAMPLES_FOR_METRICS or text.count(" or ") > 1:
            issues.append("Possible compound requirement - consider splitting")

        # Check for performance without metrics
        perf_words = ["fast", "quick", "efficient", "responsive", "performance"]
        if any(w in text.lower() for w in perf_words) and not any(c.isdigit() for c in text):
            issues.append("Performance requirement lacks quantifiable metric")

        # Check minimum length
        if len(text) < 25:
            issues.append("Requirement may be too brief")

        # Check for passive voice
        passive_indicators = [" be ", " been ", " being ", " was ", " were "]
        if any(p in text.lower() for p in passive_indicators):
            issues.append("Consider using active voice for clarity")

        return issues

    def _generate_suggestions(self, issues: list[str]) -> list[str]:
        """Generate actionable suggestions from issues."""
        suggestions = []

        for issue in issues:
            issue_lower = issue.lower()
            if "ambiguous" in issue_lower:
                suggestions.append("Replace ambiguous terms with specific, measurable criteria")
            elif "incomplete" in issue_lower:
                suggestions.append("Complete all TBD/placeholder sections")
            elif "compound" in issue_lower:
                suggestions.append("Split into separate atomic requirements for better traceability")
            elif "quantifiable" in issue_lower or "metric" in issue_lower:
                suggestions.append("Add measurable targets (e.g., 'within 200ms', '99.9% uptime')")
            elif "passive" in issue_lower:
                suggestions.append("Rewrite using active voice: 'The system shall...' not 'It shall be...'")

        return suggestions

    def _to_formal_structure(self, pattern_type: EARSPatternType, components: EARSComponents) -> str:
        """Generate normalized formal EARS structure."""
        if pattern_type == EARSPatternType.UBIQUITOUS:
            return f"The {components.system_name or '<system>'} shall {components.system_response or '<response>'}."
        if pattern_type == EARSPatternType.EVENT_DRIVEN:
            return f"WHEN {components.trigger or '<trigger>'}, the {components.system_name or '<system>'} shall {components.system_response or '<response>'}."
        if pattern_type == EARSPatternType.STATE_DRIVEN:
            return f"WHILE {components.precondition or '<state>'}, the {components.system_name or '<system>'} shall {components.system_response or '<response>'}."
        if pattern_type == EARSPatternType.OPTIONAL:
            return f"WHERE {components.constraint or '<feature>'} is enabled, the {components.system_name or '<system>'} shall {components.system_response or '<response>'}."
        if pattern_type == EARSPatternType.UNWANTED:
            return f"IF {components.precondition or '<condition>'}, THEN the {components.system_name or '<system>'} shall NOT {components.postcondition or '<action>'}."
        if pattern_type == EARSPatternType.COMPLEX:
            parts = []
            if components.precondition:
                parts.append(f"WHILE {components.precondition}")
            if components.trigger:
                parts.append(f"WHEN {components.trigger}")
            parts.append(
                f"the {components.system_name or '<system>'} shall {components.system_response or '<response>'}",
            )
            return ", ".join(parts) + "."

        return "<unclassified>"


class RequirementQualityAnalyzer:
    """ISO 29148 compliant quality analyzer with 9 dimensions.

    Implements weighted scoring based on IEEE/ISO standards with
    automated detection of common quality issues.
    """

    # ISO 29148 dimension weights
    DIMENSION_WEIGHTS: ClassVar[dict[QualityDimension, float]] = {
        QualityDimension.UNAMBIGUITY: 0.18,
        QualityDimension.COMPLETENESS: 0.18,
        QualityDimension.VERIFIABILITY: 0.14,
        QualityDimension.CONSISTENCY: 0.12,
        QualityDimension.NECESSITY: 0.10,
        QualityDimension.SINGULARITY: 0.10,
        QualityDimension.FEASIBILITY: 0.06,
        QualityDimension.TRACEABILITY: 0.06,
        QualityDimension.CORRECTNESS: 0.06,
    }

    def analyze(
        self,
        requirement_text: str,
        related_requirements: list[str] | None = None,
        linked_tests: list[str] | None = None,
        linked_items: dict[str, list[str]] | None = None,
    ) -> QualityScore:
        """Analyze requirement quality across all ISO 29148 dimensions."""
        issues: list[QualityIssue] = []
        scores: dict[str, float] = {}

        # Analyze each dimension
        scores[QualityDimension.UNAMBIGUITY.value], unambiguity_issues = self._analyze_unambiguity(requirement_text)
        issues.extend(unambiguity_issues)

        scores[QualityDimension.COMPLETENESS.value], completeness_issues = self._analyze_completeness(requirement_text)
        issues.extend(completeness_issues)

        scores[QualityDimension.VERIFIABILITY.value], verifiability_issues = self._analyze_verifiability(
            requirement_text,
        )
        issues.extend(verifiability_issues)

        scores[QualityDimension.SINGULARITY.value], singularity_issues = self._analyze_singularity(requirement_text)
        issues.extend(singularity_issues)

        scores[QualityDimension.NECESSITY.value], necessity_issues = self._analyze_necessity(requirement_text)
        issues.extend(necessity_issues)

        scores[QualityDimension.TRACEABILITY.value], traceability_issues = self._analyze_traceability(
            linked_tests,
            linked_items,
        )
        issues.extend(traceability_issues)

        scores[QualityDimension.CONSISTENCY.value], consistency_issues = self._analyze_consistency(
            requirement_text,
            related_requirements,
        )
        issues.extend(consistency_issues)

        # Feasibility and correctness are harder to automate
        scores[QualityDimension.FEASIBILITY.value] = 0.8
        scores[QualityDimension.CORRECTNESS.value] = 0.8

        # Calculate weighted overall score
        overall = sum(scores.get(dim.value, 0.8) * weight for dim, weight in self.DIMENSION_WEIGHTS.items())

        grade = self._score_to_grade(overall)

        # Determine improvement priorities
        improvement_priority = sorted(
            [d.value for d in QualityDimension if scores.get(d.value, 1.0) < QUALITY_IMPROVEMENT_THRESHOLD],
            key=lambda d: scores.get(d, 1.0),
        )

        return QualityScore(
            dimension_scores=scores,
            overall_score=overall * 100,
            issues=issues,
            grade=grade,
            improvement_priority=improvement_priority,
        )

    def _analyze_unambiguity(self, text: str) -> tuple[float, list[QualityIssue]]:
        """Analyze unambiguity dimension."""
        issues = []
        score = 1.0
        text_lower = text.lower()

        # Ambiguous terms from IEEE 830 and ISO 29148
        ambiguous_terms = {
            "appropriate": "Define specific criteria",
            "adequate": "Specify measurable thresholds",
            "reasonable": "Provide concrete bounds",
            "sufficient": "Quantify the requirement",
            "timely": "Specify time constraints in ms/s/min",
            "fast": "Define performance target (e.g., <200ms)",
            "quick": "Define performance target",
            "efficient": "Specify efficiency metrics",
            "user-friendly": "Define usability criteria (e.g., SUS score >68)",
            "flexible": "Enumerate supported variations",
            "scalable": "Define scaling parameters and limits",
            "robust": "Specify error handling requirements",
            "secure": "Reference security standards (e.g., OWASP)",
            "etc": "List all items explicitly",
            "and/or": "Choose 'and' or 'or' - not both",
        }

        for term, suggestion in ambiguous_terms.items():
            if term in text_lower:
                pos = text_lower.find(term)
                score -= 0.12
                issues.append(
                    QualityIssue(
                        dimension=QualityDimension.UNAMBIGUITY,
                        severity="warning",
                        message=f"Ambiguous term '{term}' detected",
                        suggestion=suggestion,
                        position=pos,
                        rule_id="ISO29148-AMB-001",
                    ),
                )

        # Weak modals
        weak_modals = {"may", "might", "could", "possibly", "perhaps", "probably"}
        for modal in weak_modals:
            if f" {modal} " in f" {text_lower} ":
                score -= 0.08
                issues.append(
                    QualityIssue(
                        dimension=QualityDimension.UNAMBIGUITY,
                        severity="info",
                        message=f"Weak modal '{modal}' suggests uncertainty",
                        suggestion="Use 'shall' for mandatory, 'may' only for truly optional",
                        rule_id="ISO29148-AMB-002",
                    ),
                )

        return max(0.0, score), issues

    def _analyze_completeness(self, text: str) -> tuple[float, list[QualityIssue]]:
        """Analyze completeness dimension."""
        issues = []
        score = 1.0
        text_lower = text.lower()

        # Incomplete markers
        incomplete_markers = {
            "tbd": "To Be Determined",
            "tba": "To Be Announced",
            "todo": "TODO marker",
            "fixme": "FIXME marker",
            "xxx": "XXX placeholder",
            "???": "Question marks",
            "...": "Ellipsis",
            "pending": "Pending content",
            "placeholder": "Placeholder text",
        }

        for marker, desc in incomplete_markers.items():
            if marker in text_lower:
                score -= 0.25
                issues.append(
                    QualityIssue(
                        dimension=QualityDimension.COMPLETENESS,
                        severity="error",
                        message=f"Incomplete marker found: {desc}",
                        suggestion="Complete all placeholder sections before baseline",
                        rule_id="ISO29148-COMP-001",
                    ),
                )

        # Minimum length check
        if len(text) < QUALITY_MIN_LENGTH:
            score -= 0.15
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.COMPLETENESS,
                    severity="warning",
                    message="Requirement may be too brief to be complete",
                    suggestion="Ensure actor, action, and conditions are specified",
                    rule_id="ISO29148-COMP-002",
                ),
            )

        # Check for missing actor
        if "shall" in text_lower and not any(
            actor in text_lower for actor in ["system", "user", "operator", "administrator"]
        ):
            score -= 0.10
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.COMPLETENESS,
                    severity="info",
                    message="No clear actor/system identified",
                    suggestion="Specify who/what performs the action",
                    rule_id="ISO29148-COMP-003",
                ),
            )

        return max(0.0, score), issues

    def _analyze_verifiability(self, text: str) -> tuple[float, list[QualityIssue]]:
        """Analyze verifiability dimension."""
        issues = []
        score = 1.0
        text_lower = text.lower()

        # Check for quantifiable metrics
        has_numbers = bool(re.search(r"\d+", text))
        has_units = any(
            unit in text_lower
            for unit in [
                "ms",
                "seconds",
                "minutes",
                "hours",
                "days",
                "bytes",
                "kb",
                "mb",
                "gb",
                "tb",
                "%",
                "percent",
                "percentage",
                "users",
                "requests",
                "transactions",
                "items",
                "times",
                "attempts",
                "retries",
            ]
        )

        # Performance/quality requirements need metrics
        perf_indicators = [
            "performance",
            "speed",
            "response",
            "latency",
            "throughput",
            "availability",
            "uptime",
            "reliability",
            "accuracy",
        ]

        if any(ind in text_lower for ind in perf_indicators) and not has_numbers:
            score -= 0.30
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.VERIFIABILITY,
                    severity="error",
                    message="Performance/quality requirement lacks metrics",
                    suggestion="Add specific targets (e.g., 'response time <200ms', 'uptime >99.9%')",
                    rule_id="ISO29148-VER-001",
                ),
            )

        # Generic check
        if not has_numbers and not has_units:
            score -= 0.10
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.VERIFIABILITY,
                    severity="info",
                    message="No quantifiable metrics found",
                    suggestion="Consider adding measurable acceptance criteria",
                    rule_id="ISO29148-VER-002",
                ),
            )

        # Check for verification method hints
        verification_hints = ["test", "verify", "validate", "inspect", "demonstrate"]
        if not any(hint in text_lower for hint in verification_hints):
            # Not an error, just info
            pass

        return max(0.0, score), issues

    def _analyze_singularity(self, text: str) -> tuple[float, list[QualityIssue]]:
        """Analyze singularity dimension (atomic requirements)."""
        issues = []
        score = 1.0

        # Count conjunctions
        and_count = text.lower().count(" and ")
        or_count = text.lower().count(" or ")

        if and_count > QUALITY_AND_COUNT_THRESHOLD:
            score -= 0.15 * (and_count - QUALITY_AND_COUNT_THRESHOLD)
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.SINGULARITY,
                    severity="warning",
                    message=f"Multiple 'and' conjunctions ({and_count}) - possible compound requirement",
                    suggestion="Split into separate atomic requirements for better traceability",
                    rule_id="ISO29148-SING-001",
                ),
            )

        if or_count > 0:
            score -= 0.20 * or_count
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.SINGULARITY,
                    severity="warning",
                    message="'Or' conjunction detected - ambiguous alternatives",
                    suggestion="Split into separate requirements or clarify as enumeration",
                    rule_id="ISO29148-SING-002",
                ),
            )

        # Check for multiple "shall" statements
        shall_count = text.lower().count(" shall ")
        if shall_count > 1:
            score -= 0.15 * (shall_count - 1)
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.SINGULARITY,
                    severity="warning",
                    message=f"Multiple 'shall' statements ({shall_count}) in one requirement",
                    suggestion="Each requirement should contain exactly one 'shall'",
                    rule_id="ISO29148-SING-003",
                ),
            )

        return max(0.0, score), issues

    def _analyze_necessity(self, text: str) -> tuple[float, list[QualityIssue]]:
        """Analyze necessity dimension (proper requirement language)."""
        issues = []
        score = 1.0
        text_lower = text.lower()

        if "shall" in text_lower:
            score = 1.0
        elif "will" in text_lower:
            score = 0.85
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.NECESSITY,
                    severity="info",
                    message="'Will' is weaker than 'shall' for requirements",
                    suggestion="Use 'shall' for mandatory requirements",
                    rule_id="ISO29148-NEC-001",
                ),
            )
        elif "should" in text_lower:
            score = 0.65
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.NECESSITY,
                    severity="warning",
                    message="'Should' indicates recommendation, not requirement",
                    suggestion="Use 'shall' for mandatory, 'should' for recommendations only",
                    rule_id="ISO29148-NEC-002",
                ),
            )
        elif "must" in text_lower:
            score = 0.90
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.NECESSITY,
                    severity="info",
                    message="'Must' is acceptable but 'shall' is preferred per IEEE 830",
                    suggestion="Consider using 'shall' for consistency",
                    rule_id="ISO29148-NEC-003",
                ),
            )
        else:
            score = 0.5
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.NECESSITY,
                    severity="warning",
                    message="No requirement keyword found",
                    suggestion="Use 'The system shall...' format",
                    rule_id="ISO29148-NEC-004",
                ),
            )

        return score, issues

    def _analyze_traceability(
        self,
        linked_tests: list[str] | None,
        linked_items: dict[str, list[str]] | None,
    ) -> tuple[float, list[QualityIssue]]:
        """Analyze traceability dimension."""
        issues = []
        score = 1.0

        # Check for linked tests
        if not linked_tests or len(linked_tests) == 0:
            score -= 0.30
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.TRACEABILITY,
                    severity="warning",
                    message="No linked test cases for verification",
                    suggestion="Link test cases to enable verification traceability",
                    rule_id="ISO29148-TRACE-001",
                ),
            )

        # Check for upstream/downstream links
        if linked_items and not linked_items.get("upstream"):
            score -= 0.10
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.TRACEABILITY,
                    severity="info",
                    message="No upstream links (parent requirements/features)",
                    suggestion="Link to parent requirement or feature for derivation trace",
                    rule_id="ISO29148-TRACE-002",
                ),
            )

        return max(0.0, score), issues

    def _analyze_consistency(
        self,
        text: str,
        _related_requirements: list[str] | None,
    ) -> tuple[float, list[QualityIssue]]:
        """Analyze consistency dimension."""
        issues = []
        score = 0.85  # Default - full analysis needs requirement set

        # Basic self-consistency checks
        if "shall" in text.lower() and "shall not" in text.lower():
            # Might be intentional (negative requirement)
            pass

        # Check for contradictory modals
        text_lower = text.lower()
        if "must" in text_lower and "may" in text_lower:
            score -= 0.15
            issues.append(
                QualityIssue(
                    dimension=QualityDimension.CONSISTENCY,
                    severity="warning",
                    message="Mixed mandatory ('must') and optional ('may') language",
                    suggestion="Clarify which parts are mandatory vs optional",
                    rule_id="ISO29148-CONS-001",
                ),
            )

        return score, issues

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= GRADE_A_THRESHOLD:
            return "A"
        if score >= GRADE_B_THRESHOLD:
            return "B"
        if score >= GRADE_C_THRESHOLD:
            return "C"
        if score >= GRADE_D_THRESHOLD:
            return "D"
        return "F"


class VersionChain:
    """Blockchain-style cryptographic version chain.

    Provides immutable audit trail with:
    - SHA-256 content hashing
    - Chain linking (previous block reference)
    - Merkle root for baseline verification
    - Chain integrity verification
    """

    @staticmethod
    def create_genesis_block(
        content: dict[str, Any],
        author_id: str,
        change_summary: str = "Initial creation",
    ) -> VersionBlock:
        """Create the first block in a version chain."""
        content_hash = VersionChain._hash_content(content)
        timestamp = datetime.now(UTC)

        block_data = {
            "previous_block_id": None,
            "timestamp": timestamp.isoformat(),
            "author_id": author_id,
            "change_type": "created",
            "change_summary": change_summary,
            "content_hash": content_hash,
        }

        block_id = VersionChain._hash_block(block_data)

        return VersionBlock(
            block_id=block_id,
            previous_block_id=None,
            timestamp=timestamp,
            author_id=author_id,
            change_type="created",
            change_summary=change_summary,
            content_hash=content_hash,
        )

    @staticmethod
    def add_block(
        previous_block: VersionBlock,
        content: dict[str, Any],
        author_id: str,
        change_type: str,
        change_summary: str,
    ) -> VersionBlock:
        """Add a new block linked to previous."""
        content_hash = VersionChain._hash_content(content)
        timestamp = datetime.now(UTC)

        block_data = {
            "previous_block_id": previous_block.block_id,
            "timestamp": timestamp.isoformat(),
            "author_id": author_id,
            "change_type": change_type,
            "change_summary": change_summary,
            "content_hash": content_hash,
        }

        block_id = VersionChain._hash_block(block_data)

        return VersionBlock(
            block_id=block_id,
            previous_block_id=previous_block.block_id,
            timestamp=timestamp,
            author_id=author_id,
            change_type=change_type,
            change_summary=change_summary,
            content_hash=content_hash,
        )

    @staticmethod
    def verify_chain(blocks: list[VersionBlock]) -> tuple[bool, list[str]]:
        """Verify integrity of the entire version chain."""
        if not blocks:
            return True, []

        issues = []

        # Check genesis
        if blocks[0].previous_block_id is not None:
            issues.append("Genesis block has non-null previous_block_id")

        # Verify linkage
        for i in range(1, len(blocks)):
            current = blocks[i]
            previous = blocks[i - 1]

            if current.previous_block_id != previous.block_id:
                issues.append(f"Block {i}: previous_block_id mismatch (expected {previous.block_id[:16]}...)")

            if current.timestamp < previous.timestamp:
                issues.append(f"Block {i}: timestamp before previous block")

        return len(issues) == 0, issues

    @staticmethod
    def _hash_content(content: dict[str, Any]) -> str:
        """SHA-256 hash of content."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()

    @staticmethod
    def _hash_block(block_data: dict[str, Any]) -> str:
        """SHA-256 hash of block data."""
        block_str = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()


class MerkleTree:
    """Merkle tree for efficient baseline verification.

    Enables O(log n) proof that an item is in a baseline
    without revealing the entire baseline content.
    """

    def __init__(self, items: list[tuple[str, str]]) -> None:
        """Initialize Merkle tree from items.

        Args:
            items: List of (item_id, content_hash) tuples
        """
        self.items = items
        self.leaves = list(starmap(self._hash_leaf, items))
        self.tree = self._build_tree(self.leaves.copy())
        self.root = self.tree[-1][0] if self.tree else ""

    def get_proof(self, item_id: str) -> MerkleProof | None:
        """Generate inclusion proof for an item."""
        # Find leaf index
        leaf_index = None
        for i, (iid, _) in enumerate(self.items):
            if iid == item_id:
                leaf_index = i
                break

        if leaf_index is None:
            return None

        proof_path = []
        index = leaf_index
        level_size = len(self.leaves)

        for level in range(len(self.tree) - 1):
            sibling_index = index ^ 1  # XOR to get sibling

            if sibling_index < level_size:
                sibling_hash = self.tree[level][sibling_index]
                direction = "right" if index % 2 == 0 else "left"
                proof_path.append((sibling_hash, direction))

            index //= 2
            level_size = (level_size + 1) // 2

        return MerkleProof(
            leaf_hash=self.leaves[leaf_index],
            proof_path=proof_path,
            root_hash=self.root,
            item_id=item_id,
            baseline_id="",
        )

    @staticmethod
    def verify_proof(proof: MerkleProof) -> bool:
        """Verify a Merkle inclusion proof."""
        current_hash = proof.leaf_hash

        for sibling_hash, direction in proof.proof_path:
            if direction == "left":
                current_hash = MerkleTree._hash_pair(sibling_hash, current_hash)
            else:
                current_hash = MerkleTree._hash_pair(current_hash, sibling_hash)

        return current_hash == proof.root_hash

    def _build_tree(self, leaves: list[str]) -> list[list[str]]:
        """Build complete Merkle tree from leaves."""
        if not leaves:
            return []

        tree = [leaves]

        while len(tree[-1]) > 1:
            level = tree[-1]
            next_level = []

            for i in range(0, len(level), 2):
                if i + 1 < len(level):
                    next_level.append(self._hash_pair(level[i], level[i + 1]))
                else:
                    next_level.append(level[i])  # Odd one out

            tree.append(next_level)

        return tree

    @staticmethod
    def _hash_leaf(item_id: str, content_hash: str) -> str:
        """Hash a leaf node."""
        data = f"leaf:{item_id}:{content_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def _hash_pair(left: str, right: str) -> str:
        """Hash two nodes together."""
        data = f"node:{left}:{right}"
        return hashlib.sha256(data.encode()).hexdigest()


class FlakinessDetector:
    """Meta-style probabilistic flakiness detector.

    Based on research from:
    - Meta: "Probabilistic flakiness: How we identify and prioritize flaky tests"
    - Google: "Where do flaky tests come from?"

    Key metrics:
    - Failure rate over time windows
    - Entropy (randomness of pass/fail patterns)
    - Transition frequency
    - Duration variance
    - Failure clustering
    """

    def analyze(self, run_history: list[dict[str, Any]], window_size: int = 30) -> FlakinessAnalysis:
        """Analyze test flakiness from execution history."""
        if not run_history:
            return FlakinessAnalysis(
                flakiness_score=0.0,
                severity=FlakinessSeverity.STABLE,
                entropy_score=0.0,
                transition_count=0,
                consecutive_failures_max=0,
                consecutive_passes_max=0,
                quarantine_recommended=False,
                confidence=0.0,
            )

        recent = run_history[-window_size:]
        statuses = [r.get("status", "unknown") for r in recent]
        timestamps = [r.get("timestamp") for r in recent]
        durations = [r.get("duration_ms", 0) for r in recent if r.get("duration_ms")]

        # Calculate metrics
        total = len(statuses)
        failures = sum(1 for s in statuses if s in {"failed", "error", "flaky"})
        failure_rate = failures / total if total > 0 else 0

        # Entropy calculation
        entropy = self._calculate_entropy(statuses)
        transition_count = self._count_transitions(statuses)

        # Consecutive runs
        max_failures = self._max_consecutive(statuses, {"failed", "error", "flaky"})
        max_passes = self._max_consecutive(statuses, {"passed"})

        # Duration variance
        duration_variance = None
        if durations and len(durations) > FLAKINESS_VARIANCE_MIN_SAMPLES:
            mean_duration = statistics.mean(durations)
            if mean_duration > 0:
                std_duration = statistics.stdev(durations)
                duration_variance = std_duration / mean_duration  # Coefficient of variation

        # Detect patterns
        patterns = self._detect_patterns(recent, durations, timestamps)

        # Calculate flakiness score
        flakiness_score = self._calculate_flakiness_score(
            failure_rate,
            entropy,
            max_failures,
            max_passes,
            duration_variance,
        )

        # Determine severity
        severity = self._score_to_severity(flakiness_score)

        # Failure clustering (temporal)
        clustering_score = self._calculate_failure_clustering([
            (r.get("timestamp"), r.get("status") or "") for r in recent
        ])

        # Quarantine recommendation
        quarantine_recommended = (
            severity in {FlakinessSeverity.HIGH, FlakinessSeverity.CRITICAL}
            or max_failures >= FLAKINESS_QUARANTINE_FAILURES
            or (flakiness_score > FLAKINESS_QUARANTINE_SCORE and failure_rate > FLAKINESS_QUARANTINE_RATE)
        )

        # Suggested fix
        suggested_fix = self._suggest_fix(patterns)

        # Confidence based on sample size
        confidence = min(1.0, total / 30)

        return FlakinessAnalysis(
            flakiness_score=round(flakiness_score, 4),
            severity=severity,
            detected_patterns=patterns,
            failure_rate_7d=round(failure_rate, 4),  # Simplified
            failure_rate_30d=round(failure_rate, 4),
            entropy_score=round(entropy, 4),
            transition_count=transition_count,
            consecutive_failures_max=max_failures,
            consecutive_passes_max=max_passes,
            quarantine_recommended=quarantine_recommended,
            suggested_fix_category=suggested_fix,
            confidence=round(confidence, 2),
            run_time_variance=round(duration_variance, 4) if duration_variance else None,
            failure_clustering_score=round(clustering_score, 4) if clustering_score else None,
        )

    def _calculate_entropy(self, statuses: list[str]) -> float:
        """Calculate Shannon entropy of status sequence."""
        if len(statuses) < FLAKINESS_ENTROPY_MIN_LENGTH:
            return 0.0

        # Count symbol frequencies
        counter = Counter(statuses)
        total = len(statuses)

        # Shannon entropy
        entropy = 0.0
        for count in counter.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        # Normalize by max possible entropy
        max_entropy = math.log2(len(counter)) if len(counter) > 1 else 1
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _count_transitions(self, statuses: list[str]) -> int:
        """Count state transitions in sequence."""
        if len(statuses) < FLAKINESS_TRANSITION_MIN_LENGTH:
            return 0

        return sum(1 for i in range(1, len(statuses)) if statuses[i] != statuses[i - 1])

    def _max_consecutive(self, statuses: list[str], target: set[str]) -> int:
        """Find maximum consecutive occurrences of target statuses."""
        max_count = 0
        current = 0

        for status in statuses:
            if status in target:
                current += 1
                max_count = max(max_count, current)
            else:
                current = 0

        return max_count

    def _detect_patterns(
        self,
        runs: list[dict[str, Any]],
        durations: list[float],
        _timestamps: list[object],
    ) -> list[FlakinessPattern]:
        """Detect specific flakiness patterns."""
        patterns = []

        # High duration variance suggests resource issues
        if durations and len(durations) > FLAKINESS_DURATION_MIN_SAMPLES:
            mean_d = statistics.mean(durations)
            if mean_d > 0:
                cv = statistics.stdev(durations) / mean_d
                if cv > FLAKINESS_DURATION_CV_THRESHOLD:
                    patterns.append(FlakinessPattern.RESOURCE_DEPENDENT)

        # Check for alternating pattern (possible race condition)
        statuses_raw = [r.get("status") for r in runs]
        statuses: list[str] = [s for s in statuses_raw if isinstance(s, str)]
        if len(statuses) > FLAKINESS_RACE_MIN_LENGTH:
            transitions = self._count_transitions(statuses)
            if transitions > len(statuses) * 0.6:
                patterns.append(FlakinessPattern.RACE_CONDITION)

        # Check for time-of-day clustering (simplified)
        # Would need proper timestamp parsing in production

        return patterns

    def _calculate_flakiness_score(
        self,
        failure_rate: float,
        entropy: float,
        max_failures: int,
        max_passes: int,
        duration_variance: float | None,
    ) -> float:
        """Calculate composite flakiness score.

        High entropy + moderate failure rate = flaky
        Low entropy + high failure rate = consistently failing (not flaky)
        Low failure rate = stable
        """
        # Base from failure rate
        base_score = failure_rate

        # Entropy multiplier (high entropy = random = flaky)
        entropy_factor = 1 + (entropy * 0.5)

        # Consistency factor
        if max_passes > FLAKINESS_STABLE_PASS_THRESHOLD and failure_rate < FLAKINESS_STABLE_FAILURE_RATE:
            # Mostly stable
            consistency_factor = 0.4
        elif max_failures > FLAKINESS_BROKEN_FAILURE_THRESHOLD:
            # Consistently failing (not really flaky, just broken)
            consistency_factor = 0.3
        else:
            consistency_factor = 1.0

        # Duration variance factor
        variance_factor = 1.0
        if duration_variance and duration_variance > FLAKINESS_VARIANCE_THRESHOLD:
            variance_factor = 1.2

        score = base_score * entropy_factor * consistency_factor * variance_factor
        return min(1.0, max(0.0, score))

    def _calculate_failure_clustering(self, runs: list[tuple[Any, str]]) -> float | None:
        """Calculate temporal clustering of failures."""
        # Simplified - would use proper time series analysis
        failures = [i for i, (_, status) in enumerate(runs) if status in {"failed", "error", "flaky"}]

        if len(failures) < FLAKINESS_CLUSTER_MIN_FAILURES:
            return None

        # Calculate gaps between failures
        gaps = [failures[i + 1] - failures[i] for i in range(len(failures) - 1)]
        if not gaps:
            return None

        # Low variance in gaps = clustered
        mean_gap = statistics.mean(gaps)
        if mean_gap > 0:
            std_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
            return 1.0 - min(1.0, std_gap / mean_gap)

        return None

    def _score_to_severity(self, score: float) -> FlakinessSeverity:
        """Map score to severity level."""
        if score < FLAKINESS_SEVERITY_STABLE_MAX:
            return FlakinessSeverity.STABLE
        if score < FLAKINESS_SEVERITY_LOW_MAX:
            return FlakinessSeverity.LOW
        if score < FLAKINESS_SEVERITY_MEDIUM_MAX:
            return FlakinessSeverity.MEDIUM
        if score < FLAKINESS_SEVERITY_HIGH_MAX:
            return FlakinessSeverity.HIGH
        return FlakinessSeverity.CRITICAL

    def _suggest_fix(self, patterns: list[FlakinessPattern]) -> str | None:
        """Suggest fix based on detected patterns."""
        suggestions = {
            FlakinessPattern.RACE_CONDITION: "Add synchronization barriers or increase wait timeouts",
            FlakinessPattern.RESOURCE_DEPENDENT: "Reduce resource contention, add retry logic, or isolate test",
            FlakinessPattern.TIME_DEPENDENT: "Mock time-dependent behavior or use fixed test timestamps",
            FlakinessPattern.EXTERNAL_DEPENDENCY: "Mock external services or add circuit breakers",
            FlakinessPattern.ORDER_DEPENDENT: "Ensure test isolation with proper setup/teardown",
            FlakinessPattern.ASYNC_TIMING: "Use proper async waits instead of fixed delays",
            FlakinessPattern.NETWORK_INSTABILITY: "Add network retry logic or mock network calls",
        }

        for pattern in patterns:
            if pattern in suggestions:
                return suggestions[pattern]

        return None


class ODCClassifier:
    """IBM Orthogonal Defect Classification system.

    Classifies defects across 3 dimensions:
    - Defect Type (what was wrong)
    - Trigger (how it was found)
    - Impact (customer effect)

    Used for defect prediction and process improvement.
    """

    # Keywords for automatic classification
    TYPE_KEYWORDS: ClassVar[dict[ODCDefectType, list[str]]] = {
        ODCDefectType.FUNCTION: ["missing", "function", "feature", "capability", "not implemented"],
        ODCDefectType.INTERFACE: ["interface", "api", "contract", "protocol", "integration"],
        ODCDefectType.CHECKING: ["validation", "check", "verify", "null", "empty", "bounds"],
        ODCDefectType.ASSIGNMENT: ["variable", "assignment", "initialization", "value", "wrong"],
        ODCDefectType.TIMING: ["race", "deadlock", "timeout", "async", "concurrent", "thread"],
        ODCDefectType.BUILD: ["build", "compile", "link", "package", "dependency", "merge"],
        ODCDefectType.DOCUMENTATION: ["documentation", "comment", "readme", "spec"],
        ODCDefectType.ALGORITHM: ["algorithm", "logic", "calculation", "formula", "incorrect"],
    }

    IMPACT_KEYWORDS: ClassVar[dict[ODCImpact, list[str]]] = {
        ODCImpact.SECURITY: ["security", "vulnerability", "auth", "permission", "injection", "xss"],
        ODCImpact.PERFORMANCE: ["performance", "slow", "memory", "cpu", "latency", "throughput"],
        ODCImpact.RELIABILITY: ["crash", "hang", "freeze", "restart", "failure", "exception"],
        ODCImpact.USABILITY: ["usability", "ux", "user experience", "confusing", "unclear"],
        ODCImpact.ACCESSIBILITY: ["accessibility", "a11y", "screen reader", "keyboard", "wcag"],
        ODCImpact.CAPABILITY: ["feature", "capability", "function", "missing"],
        ODCImpact.INTEGRITY: ["data", "corruption", "integrity", "consistency", "loss"],
    }
    TRIGGER_KEYWORDS: ClassVar[list[tuple[str, ODCTrigger]]] = [
        ("code review", ODCTrigger.REVIEW),
        ("review", ODCTrigger.REVIEW),
        ("unit test", ODCTrigger.UNIT_TEST),
        ("regression", ODCTrigger.REGRESSION_TEST),
        ("customer", ODCTrigger.CUSTOMER_FOUND),
        ("production", ODCTrigger.CUSTOMER_FOUND),
        ("static", ODCTrigger.STATIC_ANALYSIS),
        ("lint", ODCTrigger.STATIC_ANALYSIS),
        ("system test", ODCTrigger.SYSTEM_TEST),
    ]

    def classify(
        self,
        defect_description: str,
        trigger_context: str | None = None,
        impact_description: str | None = None,
    ) -> ODCClassification:
        """Classify a defect using ODC taxonomy."""
        desc_lower = defect_description.lower()

        # Classify defect type
        defect_type = self._classify_type(desc_lower)

        # Classify trigger
        trigger = self._classify_trigger(trigger_context)

        # Classify impact
        impact = self._classify_impact(impact_description or desc_lower)

        # Determine qualifier
        qualifier = self._determine_qualifier(desc_lower)

        return ODCClassification(
            defect_type=defect_type,
            trigger=trigger,
            impact=impact,
            qualifier=qualifier,
            confidence=0.75,  # Keyword-based has moderate confidence
        )

    def _classify_type(self, description: str) -> ODCDefectType:
        """Classify defect type from description."""
        scores = {}
        for dtype, keywords in self.TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in description)
            scores[dtype] = score

        if max(scores.values()) > 0:
            return max(scores, key=lambda k: scores[k])

        return ODCDefectType.FUNCTION  # Default

    def _classify_trigger(self, context: str | None) -> ODCTrigger:
        """Classify how defect was discovered."""
        trigger = ODCTrigger.FUNCTION_TEST
        if not context:
            return trigger

        context_lower = context.lower()
        for keyword, trigger_value in self.TRIGGER_KEYWORDS:
            if keyword in context_lower:
                trigger = trigger_value
                break

        return trigger

    def _classify_impact(self, description: str) -> ODCImpact:
        """Classify customer impact."""
        desc_lower = description.lower()

        scores = {}
        for impact, keywords in self.IMPACT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in desc_lower)
            scores[impact] = score

        if max(scores.values()) > 0:
            return max(scores, key=lambda k: scores[k])

        return ODCImpact.CAPABILITY  # Default

    def _determine_qualifier(self, description: str) -> str:
        """Determine if defect is missing, incorrect, or extraneous."""
        if any(kw in description for kw in ["missing", "not implemented", "need", "should have"]):
            return "missing"
        if any(kw in description for kw in ["extra", "unnecessary", "should not", "extraneous"]):
            return "extraneous"
        return "incorrect"


class PrioritizationCalculator:
    """Multi-framework prioritization calculator.

    Supports:
    - WSJF (SAFe Weighted Shortest Job First)
    - RICE (Reach, Impact, Confidence, Effort)
    - MoSCoW categorization
    - Cost of Delay
    """

    @staticmethod
    def calculate_wsjf(
        business_value: int,
        time_criticality: int,
        risk_reduction: int,
        job_size: int,
        opportunity_enablement: int = 1,
    ) -> WSJFScore:
        """Calculate WSJF score per SAFe framework.

        WSJF = Cost of Delay / Job Size
        Cost of Delay = Business Value + Time Criticality + Risk Reduction + Opportunity Enablement
        """
        # Clamp inputs
        business_value = max(1, min(10, business_value))
        time_criticality = max(1, min(10, time_criticality))
        risk_reduction = max(1, min(10, risk_reduction))
        opportunity_enablement = max(1, min(10, opportunity_enablement))
        job_size = max(1, min(21, job_size))  # Fibonacci scale

        # Cost of Delay (sum of value factors)
        cost_of_delay = business_value + time_criticality + risk_reduction + opportunity_enablement

        wsjf_score = cost_of_delay / job_size

        return WSJFScore(
            business_value=business_value,
            time_criticality=time_criticality,
            risk_reduction=risk_reduction,
            opportunity_enablement=opportunity_enablement,
            job_size=job_size,
            cost_of_delay=round(cost_of_delay, 2),
            wsjf_score=round(wsjf_score, 2),
        )

    @staticmethod
    def calculate_rice(reach: int, impact: float, confidence: float, effort: int) -> RICEScore:
        """Calculate RICE score.

        RICE = (Reach x Impact x Confidence) / Effort

        Impact scale: 0.25 (minimal), 0.5 (low), 1 (medium), 2 (high), 3 (massive)
        """
        reach = max(1, reach)
        impact = max(0.25, min(3.0, impact))
        confidence = max(0.0, min(1.0, confidence))
        effort = max(1, effort)

        rice_score = (reach * impact * confidence) / effort

        return RICEScore(
            reach=reach,
            impact=impact,
            confidence=confidence,
            effort=effort,
            rice_score=round(rice_score, 2),
        )

    @staticmethod
    def rank_by_wsjf(items: list[WSJFScore]) -> list[WSJFScore]:
        """Rank items by WSJF and assign percentiles."""
        sorted_items = sorted(items, key=lambda x: x.wsjf_score, reverse=True)
        total = len(sorted_items)

        for i, item in enumerate(sorted_items):
            item.percentile = int(((total - i) / total) * 100)
            item.rank = i + 1

        return sorted_items

    @staticmethod
    def rank_by_rice(items: list[RICEScore]) -> list[RICEScore]:
        """Rank items by RICE and assign percentiles."""
        sorted_items = sorted(items, key=lambda x: x.rice_score, reverse=True)
        total = len(sorted_items)

        for i, item in enumerate(sorted_items):
            item.percentile = int(((total - i) / total) * 100)
            item.rank = i + 1

        return sorted_items

    @staticmethod
    def moscow_categorize(
        items: list[dict[str, Any]],
        must_threshold: float = 0.8,
        should_threshold: float = 0.5,
        could_threshold: float = 0.2,
    ) -> dict[str, list[str]]:
        """Categorize items into MoSCoW buckets based on priority score.

        Returns dict with keys: must, should, could, wont
        """
        result: dict[str, list[str]] = {"must": [], "should": [], "could": [], "wont": []}

        for item in items:
            score = item.get("priority_score", 0)
            item_id = item.get("id", "unknown")

            if score >= must_threshold:
                result["must"].append(item_id)
            elif score >= should_threshold:
                result["should"].append(item_id)
            elif score >= could_threshold:
                result["could"].append(item_id)
            else:
                result["wont"].append(item_id)

        return result


class ImpactAnalyzer:
    """Graph-based impact analysis engine.

    Computes:
    - Direct impacts (immediate dependencies)
    - Transitive impacts (full propagation)
    - Blast radius (total affected items)
    - Critical path identification
    - Risk scoring

    Based on Neo4j graph traversal patterns.
    """

    def analyze_impact(
        self,
        source_item_id: str,
        adjacency: dict[str, list[str]],
        item_metadata: dict[str, dict[str, Any]] | None = None,
        max_depth: int = 5,
    ) -> ImpactAnalysisResult:
        """Analyze impact of changes to a source item.

        Args:
            source_item_id: The item being changed
            adjacency: Dict mapping item_id -> list[object] of dependent item_ids
            item_metadata: Optional metadata for items (type, criticality, etc.)
            max_depth: Maximum traversal depth
        """
        (
            direct_impacts,
            transitive_impacts,
            affected_tests,
            affected_docs,
            depth,
        ) = self._collect_impacts(source_item_id, adjacency, item_metadata, max_depth)

        blast_radius = len(direct_impacts) + len(transitive_impacts)
        critical_path = self._find_critical_path(direct_impacts, transitive_impacts, item_metadata)
        risk_score = self._calculate_risk_score(blast_radius, len(critical_path), depth, item_metadata)

        return ImpactAnalysisResult(
            source_item_id=source_item_id,
            direct_impacts=direct_impacts,
            transitive_impacts=transitive_impacts,
            impact_depth=depth,
            blast_radius=blast_radius,
            critical_path_items=critical_path,
            affected_tests=affected_tests,
            affected_documents=affected_docs,
            risk_score=risk_score,
        )

    def _collect_impacts(
        self,
        source_item_id: str,
        adjacency: dict[str, list[str]],
        item_metadata: dict[str, dict[str, Any]] | None,
        max_depth: int,
    ) -> tuple[list[str], list[str], list[str], list[str], int]:
        visited: set[str] = set()
        direct_impacts: list[str] = []
        transitive_impacts: list[str] = []
        affected_tests: list[str] = []
        affected_docs: list[str] = []
        depth = 0
        current_level = [source_item_id]

        while current_level and depth < max_depth:
            next_level = []
            for item_id in current_level:
                if item_id in visited:
                    continue
                visited.add(item_id)
                dependents = adjacency.get(item_id, [])
                next_level.extend(
                    self._process_dependents(
                        dependents=dependents,
                        depth=depth,
                        visited=visited,
                        direct_impacts=direct_impacts,
                        transitive_impacts=transitive_impacts,
                        affected_tests=affected_tests,
                        affected_docs=affected_docs,
                        item_metadata=item_metadata,
                    ),
                )
            current_level = next_level
            depth += 1

        return direct_impacts, transitive_impacts, affected_tests, affected_docs, depth

    def _process_dependents(
        self,
        *,
        dependents: list[str],
        depth: int,
        visited: set[str],
        direct_impacts: list[str],
        transitive_impacts: list[str],
        affected_tests: list[str],
        affected_docs: list[str],
        item_metadata: dict[str, dict[str, Any]] | None,
    ) -> list[str]:
        next_level: list[str] = []
        for dep_id in dependents:
            if dep_id in visited:
                continue
            next_level.append(dep_id)
            self._record_impact(dep_id, depth, direct_impacts, transitive_impacts)
            self._categorize_impact(dep_id, item_metadata, affected_tests, affected_docs)
        return next_level

    def _record_impact(
        self,
        dep_id: str,
        depth: int,
        direct_impacts: list[str],
        transitive_impacts: list[str],
    ) -> None:
        if depth == 0:
            direct_impacts.append(dep_id)
        else:
            transitive_impacts.append(dep_id)

    def _categorize_impact(
        self,
        dep_id: str,
        item_metadata: dict[str, dict[str, Any]] | None,
        affected_tests: list[str],
        affected_docs: list[str],
    ) -> None:
        if not item_metadata:
            return
        meta = item_metadata.get(dep_id, {})
        item_type = meta.get("type", "")
        item_type_lower = item_type.lower()
        if "test" in item_type_lower:
            affected_tests.append(dep_id)
        elif "doc" in item_type_lower:
            affected_docs.append(dep_id)

    def _find_critical_path(
        self,
        direct_impacts: list[str],
        transitive_impacts: list[str],
        item_metadata: dict[str, dict[str, Any]] | None,
    ) -> list[str]:
        if not item_metadata:
            return []
        critical_path: list[str] = []
        for item_id in direct_impacts + transitive_impacts:
            meta = item_metadata.get(item_id, {})
            if meta.get("criticality", "") in {"high", "critical"}:
                critical_path.append(item_id)
        return critical_path

    def _calculate_risk_score(
        self,
        blast_radius: int,
        critical_count: int,
        depth: int,
        _metadata: dict[str, dict[str, Any]] | None,
    ) -> float:
        """Calculate composite risk score."""
        # Base risk from blast radius
        radius_risk = min(40, blast_radius * 2)

        # Critical path risk
        critical_risk = min(30, critical_count * 10)

        # Depth risk (deeper = harder to trace)
        depth_risk = min(20, depth * 4)

        # Base complexity
        base_risk = 10

        return min(100, radius_risk + critical_risk + depth_risk + base_risk)


class SuspectLinkDetector:
    """Detects suspect traceability links after changes.

    Based on Jama Connect and Polarion ALM patterns:
    - Upstream modification detection
    - Version mismatch detection
    - Content change impact
    """

    def detect_suspect_links(
        self,
        links: list[dict[str, Any]],
        item_versions: dict[str, int],
        recent_changes: list[dict[str, Any]],
    ) -> list[SuspectLink]:
        """Detect links that may be invalid after recent changes.

        Args:
            links: List of trace links with {id, source_id, target_id, source_version}
            item_versions: Current version of each item
            recent_changes: Recent change events
        """
        suspect_links = []
        changed_items = {c["item_id"]: c for c in recent_changes}

        for link in links:
            link_id = link.get("id", "")
            source_id = link.get("source_id", "")
            target_id = link.get("target_id", "")
            link_source_version = link.get("source_version", 0)

            # Check if source has been modified since link was created/verified
            current_version = item_versions.get(source_id, 0)

            if source_id in changed_items:
                change = changed_items[source_id]

                # Version mismatch - source was updated
                if current_version > link_source_version:
                    suspect_links.append(
                        SuspectLink(
                            link_id=link_id,
                            source_id=source_id,
                            target_id=target_id,
                            reason=SuspectLinkReason.UPSTREAM_MODIFIED,
                            detected_at=datetime.now(UTC),
                            source_version_before=link_source_version,
                            source_version_after=current_version,
                            change_summary=change.get("summary", "Source item modified"),
                            requires_verification=True,
                            auto_resolvable=False,
                        ),
                    )

                # Status changed
                elif change.get("change_type") == "status_changed":
                    suspect_links.append(
                        SuspectLink(
                            link_id=link_id,
                            source_id=source_id,
                            target_id=target_id,
                            reason=SuspectLinkReason.STATUS_CHANGED,
                            detected_at=datetime.now(UTC),
                            source_version_before=link_source_version,
                            source_version_after=current_version,
                            change_summary=f"Status changed: {change.get('old_status')} -> {change.get('new_status')}",
                            requires_verification=True,
                            auto_resolvable=change.get("new_status") == "approved",
                        ),
                    )

        return suspect_links


class CoverageGapAnalyzer:
    """Analyzes traceability coverage gaps.

    Detects:
    - Requirements without tests
    - Tests not linked to requirements
    - Missing verification evidence
    - Safety-level coverage requirements (DO-178C, ISO 26262)
    """

    # Coverage requirements by safety level
    SAFETY_COVERAGE_REQUIREMENTS: ClassVar[dict[SafetyLevel, dict[CoverageType, int]]] = {
        SafetyLevel.DAL_A: {CoverageType.MCDC: 100, CoverageType.BRANCH: 100, CoverageType.STATEMENT: 100},
        SafetyLevel.DAL_B: {CoverageType.BRANCH: 100, CoverageType.STATEMENT: 100},
        SafetyLevel.DAL_C: {CoverageType.STATEMENT: 100},
        SafetyLevel.ASIL_D: {CoverageType.MCDC: 100, CoverageType.BRANCH: 100},
        SafetyLevel.ASIL_C: {CoverageType.BRANCH: 100},
        SafetyLevel.ASIL_B: {CoverageType.STATEMENT: 100},
        SafetyLevel.CLASS_C: {CoverageType.BRANCH: 100, CoverageType.STATEMENT: 100},
    }

    def analyze_gaps(
        self,
        requirements: list[dict[str, Any]],
        tests: list[dict[str, Any]],
        trace_links: list[dict[str, Any]],
        safety_level: SafetyLevel | None = None,
    ) -> list[CoverageGap]:
        """Analyze coverage gaps in traceability matrix.

        Args:
            requirements: List of requirements with {id, type, safety_level, ...}
            tests: List of tests with {id, coverage, linked_requirements, ...}
            trace_links: Existing trace links
            safety_level: Project-wide safety level if not per-requirement
        """
        covered_reqs, linked_tests = self._build_trace_sets(trace_links)
        gaps = []
        gaps.extend(self._find_requirement_gaps(requirements, covered_reqs, safety_level))
        gaps.extend(self._find_orphaned_tests(tests, linked_tests))
        gaps.extend(self._find_safety_coverage_gaps(tests, safety_level))
        return gaps

    def _build_trace_sets(self, trace_links: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
        covered_reqs: set[str] = set()
        linked_tests: set[str] = set()
        for link in trace_links:
            if link.get("link_type") != "verifies":
                continue
            target_id = link.get("target_id")
            source_id = link.get("source_id")
            if isinstance(target_id, str):
                covered_reqs.add(target_id)
            if isinstance(source_id, str):
                linked_tests.add(source_id)
        return covered_reqs, linked_tests

    def _find_requirement_gaps(
        self,
        requirements: list[dict[str, Any]],
        covered_reqs: set[str],
        safety_level: SafetyLevel | None,
    ) -> list[CoverageGap]:
        gaps: list[CoverageGap] = []
        for req in requirements:
            req_id = req["id"]
            if req_id in covered_reqs:
                continue
            req_safety = req.get("safety_level") or safety_level
            severity = self._gap_severity(req_safety, req.get("criticality"))
            gaps.append(
                CoverageGap(
                    gap_type="no_tests",
                    item_id=req_id,
                    item_type="requirement",
                    severity=severity,
                    current_coverage=0.0,
                    required_coverage=100.0,
                    safety_level=req_safety,
                    suggestion=f"Add test cases to verify requirement {req_id}",
                ),
            )
        return gaps

    def _find_orphaned_tests(self, tests: list[dict[str, Any]], linked_tests: set[str]) -> list[CoverageGap]:
        gaps: list[CoverageGap] = []
        for test in tests:
            test_id = test["id"]
            if test_id in linked_tests:
                continue
            gaps.append(
                CoverageGap(
                    gap_type="orphaned_test",
                    item_id=test_id,
                    item_type="test",
                    severity="low",
                    current_coverage=0.0,
                    required_coverage=0.0,
                    suggestion=f"Link test {test_id} to its corresponding requirement",
                ),
            )
        return gaps

    def _find_safety_coverage_gaps(
        self,
        tests: list[dict[str, Any]],
        safety_level: SafetyLevel | None,
    ) -> list[CoverageGap]:
        if not safety_level:
            return []
        required_coverage = self.SAFETY_COVERAGE_REQUIREMENTS.get(safety_level)
        if not required_coverage:
            return []
        gaps: list[CoverageGap] = []
        for test in tests:
            test_coverage = test.get("coverage", {})
            for coverage_type, required in required_coverage.items():
                actual = test_coverage.get(coverage_type.value, 0)
                if actual >= required:
                    continue
                gaps.append(
                    CoverageGap(
                        gap_type="insufficient_coverage",
                        item_id=test["id"],
                        item_type="test",
                        severity="critical" if coverage_type == CoverageType.MCDC else "high",
                        expected_coverage_type=coverage_type,
                        current_coverage=actual,
                        required_coverage=required,
                        safety_level=safety_level,
                        suggestion=f"Increase {coverage_type.value} coverage from {actual}% to {required}%",
                    ),
                )
        return gaps

    def _gap_severity(self, safety_level: SafetyLevel | None, criticality: str | None) -> str:
        """Determine gap severity based on safety and criticality."""
        if safety_level in {SafetyLevel.DAL_A, SafetyLevel.DAL_B, SafetyLevel.ASIL_D}:
            return "critical"
        if safety_level in {SafetyLevel.ASIL_C, SafetyLevel.CLASS_C} or criticality == "high":
            return "high"
        if criticality == "medium":
            return "medium"
        return "low"


# =============================================================================
# MAIN SERVICE FACADE
# =============================================================================


class SpecAnalyticsService:
    """Comprehensive specification analytics service.

    Provides unified access to all analytics capabilities:
    - EARS pattern analysis
    - ISO 29148 quality scoring
    - Cryptographic version chains
    - Merkle proof generation
    - Flakiness detection
    - ODC defect classification
    - Prioritization (WSJF/RICE)
    - Impact analysis
    - Suspect link detection
    - Coverage gap analysis
    """

    def __init__(self) -> None:
        """Initialize."""
        self.ears_analyzer = EARSPatternAnalyzer()
        self.quality_analyzer = RequirementQualityAnalyzer()
        self.flakiness_detector = FlakinessDetector()
        self.odc_classifier = ODCClassifier()
        self.impact_analyzer = ImpactAnalyzer()
        self.suspect_link_detector = SuspectLinkDetector()
        self.coverage_gap_analyzer = CoverageGapAnalyzer()

    # -------------------------------------------------------------------------
    # Requirement Analysis
    # -------------------------------------------------------------------------

    def analyze_requirement(
        self,
        requirement_text: str,
        related_requirements: list[str] | None = None,
        linked_tests: list[str] | None = None,
        linked_items: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        """Comprehensive requirement analysis.

        Returns EARS pattern analysis, quality scores, and recommendations.
        """
        ears_result = self.ears_analyzer.analyze(requirement_text)
        quality_result = self.quality_analyzer.analyze(
            requirement_text,
            related_requirements,
            linked_tests,
            linked_items,
        )

        return {
            "ears_analysis": ears_result.model_dump(),
            "quality_analysis": quality_result.model_dump(),
            "overall_health": {
                "is_well_formed": ears_result.is_valid,
                "pattern_type": ears_result.pattern_type.value,
                "quality_grade": quality_result.grade,
                "quality_score": quality_result.overall_score,
                "total_issues": len(ears_result.validation_issues) + len(quality_result.issues),
                "needs_attention": (not ears_result.is_valid or quality_result.grade in {"D", "F"}),
                "improvement_priorities": quality_result.improvement_priority,
            },
            "formal_structure": ears_result.formal_structure,
            "ambiguous_terms": ears_result.ambiguous_terms,
        }

    def batch_analyze_requirements(self, requirements: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Analyze multiple requirements at once."""
        return [{"id": req.get("id", ""), **self.analyze_requirement(req.get("text", ""))} for req in requirements]

    # -------------------------------------------------------------------------
    # Version Chain Management
    # -------------------------------------------------------------------------

    def create_genesis_block(
        self,
        content: dict[str, Any],
        author_id: str,
        change_summary: str = "Initial creation",
    ) -> VersionBlock:
        """Create first block in version chain."""
        return VersionChain.create_genesis_block(content, author_id, change_summary)

    def add_version_block(
        self,
        previous_block: VersionBlock,
        content: dict[str, Any],
        author_id: str,
        change_type: str,
        change_summary: str,
    ) -> VersionBlock:
        """Add new block to version chain."""
        return VersionChain.add_block(previous_block, content, author_id, change_type, change_summary)

    def verify_version_chain(self, blocks: list[VersionBlock]) -> tuple[bool, list[str]]:
        """Verify integrity of version chain."""
        return VersionChain.verify_chain(blocks)

    # -------------------------------------------------------------------------
    # Merkle Tree / Baseline Verification
    # -------------------------------------------------------------------------

    def create_merkle_tree(self, items: list[tuple[str, str]]) -> MerkleTree:
        """Create Merkle tree from items for baseline verification."""
        return MerkleTree(items)

    def get_merkle_proof(self, tree: MerkleTree, item_id: str) -> MerkleProof | None:
        """Get inclusion proof for an item."""
        return tree.get_proof(item_id)

    def verify_merkle_proof(self, proof: MerkleProof) -> bool:
        """Verify Merkle inclusion proof."""
        return MerkleTree.verify_proof(proof)

    # -------------------------------------------------------------------------
    # Test Analytics
    # -------------------------------------------------------------------------

    def analyze_test_flakiness(self, run_history: list[dict[str, Any]], window_size: int = 30) -> FlakinessAnalysis:
        """Analyze test flakiness from execution history."""
        return self.flakiness_detector.analyze(run_history, window_size)

    def batch_analyze_flakiness(self, tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Analyze flakiness for multiple tests."""
        results = []
        for test in tests:
            analysis = self.flakiness_detector.analyze(test.get("run_history", []))
            results.append({"test_id": test.get("id", ""), "flakiness_analysis": analysis.model_dump()})
        return results

    # -------------------------------------------------------------------------
    # Defect Classification
    # -------------------------------------------------------------------------

    def classify_defect(
        self,
        description: str,
        trigger_context: str | None = None,
        impact_description: str | None = None,
    ) -> ODCClassification:
        """Classify defect using IBM ODC taxonomy."""
        return self.odc_classifier.classify(description, trigger_context, impact_description)

    # -------------------------------------------------------------------------
    # Prioritization
    # -------------------------------------------------------------------------

    def calculate_wsjf(
        self,
        business_value: int,
        time_criticality: int,
        risk_reduction: int,
        job_size: int,
        opportunity_enablement: int = 1,
    ) -> WSJFScore:
        """Calculate WSJF prioritization score."""
        return PrioritizationCalculator.calculate_wsjf(
            business_value,
            time_criticality,
            risk_reduction,
            job_size,
            opportunity_enablement,
        )

    def calculate_rice(self, reach: int, impact: float, confidence: float, effort: int) -> RICEScore:
        """Calculate RICE prioritization score."""
        return PrioritizationCalculator.calculate_rice(reach, impact, confidence, effort)

    def rank_items_wsjf(self, items: list[WSJFScore]) -> list[WSJFScore]:
        """Rank items by WSJF score."""
        return PrioritizationCalculator.rank_by_wsjf(items)

    def rank_items_rice(self, items: list[RICEScore]) -> list[RICEScore]:
        """Rank items by RICE score."""
        return PrioritizationCalculator.rank_by_rice(items)

    # -------------------------------------------------------------------------
    # Impact Analysis
    # -------------------------------------------------------------------------

    def analyze_change_impact(
        self,
        source_item_id: str,
        adjacency: dict[str, list[str]],
        item_metadata: dict[str, dict[str, Any]] | None = None,
        max_depth: int = 5,
    ) -> ImpactAnalysisResult:
        """Analyze impact of changing an item."""
        return self.impact_analyzer.analyze_impact(source_item_id, adjacency, item_metadata, max_depth)

    # -------------------------------------------------------------------------
    # Suspect Links
    # -------------------------------------------------------------------------

    def detect_suspect_links(
        self,
        links: list[dict[str, Any]],
        item_versions: dict[str, int],
        recent_changes: list[dict[str, Any]],
    ) -> list[SuspectLink]:
        """Detect suspect trace links after changes."""
        return self.suspect_link_detector.detect_suspect_links(links, item_versions, recent_changes)

    # -------------------------------------------------------------------------
    # Coverage Analysis
    # -------------------------------------------------------------------------

    def analyze_coverage_gaps(
        self,
        requirements: list[dict[str, Any]],
        tests: list[dict[str, Any]],
        trace_links: list[dict[str, Any]],
        safety_level: SafetyLevel | None = None,
    ) -> list[CoverageGap]:
        """Analyze traceability coverage gaps."""
        return self.coverage_gap_analyzer.analyze_gaps(requirements, tests, trace_links, safety_level)

    # -------------------------------------------------------------------------
    # Content Addressing
    # -------------------------------------------------------------------------

    @staticmethod
    def generate_content_address(content: dict[str, Any], content_type: str = "application/json") -> ContentAddress:
        """Generate IPFS-style content address for specification."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        content_bytes = content_str.encode()
        cid = hashlib.sha256(content_bytes).hexdigest()

        return ContentAddress(
            cid=f"tracertm:{cid}",
            algorithm="sha256",
            size_bytes=len(content_bytes),
            content_type=content_type,
            created_at=datetime.now(UTC),
        )

    @staticmethod
    def verify_content_address(content: dict[str, Any], expected_cid: str) -> bool:
        """Verify content matches its address."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        actual_cid = f"tracertm:{hashlib.sha256(content_str.encode()).hexdigest()}"
        return actual_cid == expected_cid


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================


# Create singleton instance for easy import
spec_analytics = SpecAnalyticsService()
spec_analytics_service = spec_analytics


def analyze_requirement(text: str, **kwargs: Any) -> dict[str, Any]:
    """Convenience function for requirement analysis."""
    return spec_analytics.analyze_requirement(text, **kwargs)


def analyze_flakiness(run_history: list[dict[str, Any]]) -> FlakinessAnalysis:
    """Convenience function for flakiness analysis."""
    return spec_analytics.analyze_test_flakiness(run_history)


def calculate_wsjf(**kwargs: Any) -> WSJFScore:
    """Convenience function for WSJF calculation."""
    return spec_analytics.calculate_wsjf(**kwargs)


def calculate_rice(**kwargs: Any) -> RICEScore:
    """Convenience function for RICE calculation."""
    return spec_analytics.calculate_rice(**kwargs)
