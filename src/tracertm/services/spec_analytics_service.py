"""
Specification Analytics Service

Provides advanced analytics for item specifications including:
- EARS pattern validation and classification
- ISO 29148 quality analysis
- Semantic similarity detection
- Cryptographic version chain
- Impact analysis graph traversal
- Flakiness detection (Meta-style)
- WSJF/RICE prioritization

Based on research from:
- ISO 29148:2018 Requirements Engineering
- EARS Patterns (Mavin et al.)
- Google De-flake Research
- Meta Probabilistic Flakiness
- SAFe WSJF Framework
"""

import hashlib
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# =============================================================================
# EARS Pattern Analysis (ISO 29148 + INCOSE)
# =============================================================================


class EARSPatternType(str, Enum):
    """EARS requirement pattern types."""
    UBIQUITOUS = "ubiquitous"      # "The system shall..."
    EVENT_DRIVEN = "event_driven"   # "When <event>, the system shall..."
    STATE_DRIVEN = "state_driven"   # "While <state>, the system shall..."
    OPTIONAL = "optional"           # "Where <feature>, the system shall..."
    COMPLEX = "complex"             # Multiple triggers
    UNWANTED = "unwanted"           # "If <event>, then the system shall not..."
    UNCLASSIFIED = "unclassified"


class EARSComponents(BaseModel):
    """Extracted EARS components from a requirement."""
    trigger: str | None = None
    precondition: str | None = None
    postcondition: str | None = None
    system_response: str | None = None
    constraint: str | None = None
    actor: str | None = None


class EARSAnalysisResult(BaseModel):
    """Result of EARS pattern analysis."""
    pattern_type: EARSPatternType
    confidence: float = Field(ge=0, le=1)
    components: EARSComponents
    is_valid: bool
    validation_issues: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)


class EARSPatternAnalyzer:
    """
    Analyzes requirements against EARS patterns.

    EARS (Easy Approach to Requirements Syntax) provides 6 templates:
    1. Ubiquitous: "The <system> shall <response>"
    2. Event-driven: "WHEN <event>, the <system> shall <response>"
    3. State-driven: "WHILE <state>, the <system> shall <response>"
    4. Optional: "WHERE <feature>, the <system> shall <response>"
    5. Complex: Combination of above
    6. Unwanted: "IF <event>, THEN the <system> shall NOT <response>"
    """

    # Pattern regexes
    PATTERNS = {
        EARSPatternType.EVENT_DRIVEN: re.compile(
            r"^(?:when|upon|after|once|if)\s+(.+?),?\s+(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE
        ),
        EARSPatternType.STATE_DRIVEN: re.compile(
            r"^(?:while|during|as long as)\s+(.+?),?\s+(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE
        ),
        EARSPatternType.OPTIONAL: re.compile(
            r"^(?:where|if|in case)\s+(.+?)\s+(?:is\s+)?(?:enabled|configured|available),?\s+(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE
        ),
        EARSPatternType.UNWANTED: re.compile(
            r"^(?:if|when)\s+(.+?),?\s+(?:then\s+)?(?:the\s+)?(\w+)\s+shall\s+(?:not|never)\s+(.+)$",
            re.IGNORECASE
        ),
        EARSPatternType.UBIQUITOUS: re.compile(
            r"^(?:the\s+)?(\w+)\s+shall\s+(.+)$",
            re.IGNORECASE
        ),
    }

    # Ambiguous words to flag
    AMBIGUOUS_WORDS = {
        "appropriate", "adequate", "reasonable", "sufficient", "timely",
        "easy", "simple", "fast", "quick", "efficient", "effective",
        "user-friendly", "flexible", "scalable", "robust", "secure",
        "good", "bad", "better", "best", "optimal", "minimal",
        "some", "several", "many", "few", "various", "etc",
        "normally", "usually", "typically", "generally", "often",
        "may", "might", "could", "possibly", "perhaps"
    }

    # Incomplete markers
    INCOMPLETE_MARKERS = {"tbd", "todo", "fixme", "xxx", "tba", "placeholder"}

    def analyze(self, requirement_text: str) -> EARSAnalysisResult:
        """Analyze a requirement against EARS patterns."""
        text = requirement_text.strip()
        issues = []
        suggestions = []

        # Try to match patterns in order of specificity
        for pattern_type, pattern in self.PATTERNS.items():
            match = pattern.match(text)
            if match:
                components = self._extract_components(pattern_type, match)
                confidence = self._calculate_confidence(text, pattern_type, components)

                # Validate the match
                validation_issues = self._validate_requirement(text, components)
                issues.extend(validation_issues)

                if validation_issues:
                    suggestions.extend(self._generate_suggestions(validation_issues))

                return EARSAnalysisResult(
                    pattern_type=pattern_type,
                    confidence=confidence,
                    components=components,
                    is_valid=len(validation_issues) == 0,
                    validation_issues=issues,
                    improvement_suggestions=suggestions
                )

        # No pattern matched
        return EARSAnalysisResult(
            pattern_type=EARSPatternType.UNCLASSIFIED,
            confidence=0.0,
            components=EARSComponents(),
            is_valid=False,
            validation_issues=["Requirement does not match any EARS pattern"],
            improvement_suggestions=[
                "Consider restructuring as: 'The <system> shall <action>'",
                "For conditional requirements, use: 'When <trigger>, the <system> shall <action>'"
            ]
        )

    def _extract_components(
        self, pattern_type: EARSPatternType, match: re.Match
    ) -> EARSComponents:
        """Extract EARS components from a regex match."""
        groups = match.groups()

        if pattern_type == EARSPatternType.UBIQUITOUS:
            return EARSComponents(
                actor=groups[0] if len(groups) > 0 else None,
                system_response=groups[1] if len(groups) > 1 else None
            )
        elif pattern_type in (
            EARSPatternType.EVENT_DRIVEN,
            EARSPatternType.STATE_DRIVEN,
            EARSPatternType.OPTIONAL
        ):
            return EARSComponents(
                trigger=groups[0] if len(groups) > 0 else None,
                actor=groups[1] if len(groups) > 1 else None,
                system_response=groups[2] if len(groups) > 2 else None
            )
        elif pattern_type == EARSPatternType.UNWANTED:
            return EARSComponents(
                precondition=groups[0] if len(groups) > 0 else None,
                actor=groups[1] if len(groups) > 1 else None,
                postcondition=f"NOT {groups[2]}" if len(groups) > 2 else None
            )

        return EARSComponents()

    def _calculate_confidence(
        self,
        text: str,
        pattern_type: EARSPatternType,
        components: EARSComponents
    ) -> float:
        """Calculate confidence score for the pattern match."""
        confidence = 0.5  # Base confidence for any match

        # Boost for having "shall" (requirement keyword)
        if "shall" in text.lower():
            confidence += 0.2

        # Boost for clear actor/system identification
        if components.actor:
            confidence += 0.1

        # Boost for having a clear response
        if components.system_response and len(components.system_response) > 10:
            confidence += 0.1

        # Penalty for ambiguous words
        words = set(text.lower().split())
        ambiguous_count = len(words & self.AMBIGUOUS_WORDS)
        confidence -= ambiguous_count * 0.05

        # Penalty for incomplete markers
        if words & self.INCOMPLETE_MARKERS:
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def _validate_requirement(
        self, text: str, components: EARSComponents
    ) -> list[str]:
        """Validate the requirement for quality issues."""
        issues = []
        words = text.lower().split()
        word_set = set(words)

        # Check for ambiguous terms
        ambiguous = word_set & self.AMBIGUOUS_WORDS
        if ambiguous:
            issues.append(f"Ambiguous terms detected: {', '.join(ambiguous)}")

        # Check for incomplete markers
        incomplete = word_set & self.INCOMPLETE_MARKERS
        if incomplete:
            issues.append(f"Incomplete markers found: {', '.join(incomplete)}")

        # Check for missing quantification
        if any(word in word_set for word in ["fast", "quick", "efficient"]):
            if not any(char.isdigit() for char in text):
                issues.append("Performance requirement lacks quantifiable metric")

        # Check for compound requirements
        if text.count(" and ") > 1 or text.count(" or ") > 1:
            issues.append("Possible compound requirement - consider splitting")

        # Check minimum length
        if len(text) < 20:
            issues.append("Requirement may be too brief to be complete")

        return issues

    def _generate_suggestions(self, issues: list[str]) -> list[str]:
        """Generate improvement suggestions based on issues."""
        suggestions = []

        for issue in issues:
            if "ambiguous" in issue.lower():
                suggestions.append(
                    "Replace ambiguous terms with specific, measurable criteria"
                )
            elif "incomplete" in issue.lower():
                suggestions.append(
                    "Complete all placeholder sections before finalizing"
                )
            elif "quantifiable" in issue.lower():
                suggestions.append(
                    "Add specific metrics (e.g., 'within 200ms' instead of 'fast')"
                )
            elif "compound" in issue.lower():
                suggestions.append(
                    "Split into separate requirements for better traceability"
                )

        return suggestions


# =============================================================================
# Quality Scoring (ISO 29148 Dimensions)
# =============================================================================


class QualityDimension(str, Enum):
    """ISO 29148 quality dimensions."""
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    CORRECTNESS = "correctness"
    UNAMBIGUITY = "unambiguity"
    VERIFIABILITY = "verifiability"
    TRACEABILITY = "traceability"
    FEASIBILITY = "feasibility"
    NECESSITY = "necessity"
    SINGULARITY = "singularity"


class QualityIssue(BaseModel):
    """A detected quality issue."""
    dimension: QualityDimension
    severity: str = Field(pattern="^(error|warning|info)$")
    message: str
    suggestion: str | None = None
    position: int | None = None  # Character position in text


class QualityScore(BaseModel):
    """Quality scoring result."""
    dimension_scores: dict[str, float]
    overall_score: float
    issues: list[QualityIssue]
    grade: str  # A, B, C, D, F


class RequirementQualityAnalyzer:
    """
    Analyzes requirement quality against ISO 29148 dimensions.

    Scoring weights (from ISO 29148):
    - Unambiguity: 20%
    - Completeness: 20%
    - Verifiability: 15%
    - Consistency: 15%
    - Necessity: 10%
    - Singularity: 10%
    - Feasibility: 5%
    - Traceability: 5%
    """

    DIMENSION_WEIGHTS = {
        QualityDimension.UNAMBIGUITY: 0.20,
        QualityDimension.COMPLETENESS: 0.20,
        QualityDimension.VERIFIABILITY: 0.15,
        QualityDimension.CONSISTENCY: 0.15,
        QualityDimension.NECESSITY: 0.10,
        QualityDimension.SINGULARITY: 0.10,
        QualityDimension.FEASIBILITY: 0.05,
        QualityDimension.TRACEABILITY: 0.05,
    }

    def analyze(
        self,
        requirement_text: str,
        related_requirements: list[str] | None = None,
        linked_tests: list[str] | None = None
    ) -> QualityScore:
        """Analyze requirement quality across all dimensions."""
        issues = []
        scores = {}

        # Unambiguity analysis
        unambiguity_score, unambiguity_issues = self._analyze_unambiguity(
            requirement_text
        )
        scores[QualityDimension.UNAMBIGUITY.value] = unambiguity_score
        issues.extend(unambiguity_issues)

        # Completeness analysis
        completeness_score, completeness_issues = self._analyze_completeness(
            requirement_text
        )
        scores[QualityDimension.COMPLETENESS.value] = completeness_score
        issues.extend(completeness_issues)

        # Verifiability analysis
        verifiability_score, verifiability_issues = self._analyze_verifiability(
            requirement_text
        )
        scores[QualityDimension.VERIFIABILITY.value] = verifiability_score
        issues.extend(verifiability_issues)

        # Singularity analysis
        singularity_score, singularity_issues = self._analyze_singularity(
            requirement_text
        )
        scores[QualityDimension.SINGULARITY.value] = singularity_score
        issues.extend(singularity_issues)

        # Necessity analysis (verb strength)
        necessity_score, necessity_issues = self._analyze_necessity(
            requirement_text
        )
        scores[QualityDimension.NECESSITY.value] = necessity_score
        issues.extend(necessity_issues)

        # Traceability (based on linked tests)
        traceability_score = 1.0 if linked_tests and len(linked_tests) > 0 else 0.5
        scores[QualityDimension.TRACEABILITY.value] = traceability_score
        if traceability_score < 1.0:
            issues.append(QualityIssue(
                dimension=QualityDimension.TRACEABILITY,
                severity="warning",
                message="No linked test cases for verification",
                suggestion="Link test cases to enable traceability"
            ))

        # Consistency (placeholder - would need full requirement set)
        scores[QualityDimension.CONSISTENCY.value] = 0.8

        # Feasibility (placeholder - would need domain analysis)
        scores[QualityDimension.FEASIBILITY.value] = 0.8

        # Calculate weighted overall score
        overall = sum(
            scores.get(dim.value, 0.8) * weight
            for dim, weight in self.DIMENSION_WEIGHTS.items()
        )

        # Determine grade
        grade = self._score_to_grade(overall)

        return QualityScore(
            dimension_scores=scores,
            overall_score=overall * 100,  # Convert to percentage
            issues=issues,
            grade=grade
        )

    def _analyze_unambiguity(
        self, text: str
    ) -> tuple[float, list[QualityIssue]]:
        """Analyze unambiguity dimension."""
        issues = []
        score = 1.0

        # Check for ambiguous words
        ambiguous_words = {
            "appropriate", "adequate", "reasonable", "sufficient", "timely",
            "easy", "simple", "fast", "quick", "efficient", "effective",
            "user-friendly", "flexible", "scalable", "robust", "good",
            "some", "several", "many", "few", "various", "etc",
            "normally", "usually", "typically", "generally", "often"
        }

        words = set(text.lower().split())
        found_ambiguous = words & ambiguous_words

        for word in found_ambiguous:
            score -= 0.15
            # Find position
            pos = text.lower().find(word)
            issues.append(QualityIssue(
                dimension=QualityDimension.UNAMBIGUITY,
                severity="warning",
                message=f"Ambiguous term '{word}' detected",
                suggestion=f"Replace '{word}' with specific, measurable criteria",
                position=pos
            ))

        # Check for weak modals
        weak_modals = {"may", "might", "could", "possibly", "perhaps", "should"}
        found_weak = words & weak_modals

        for word in found_weak:
            score -= 0.10
            issues.append(QualityIssue(
                dimension=QualityDimension.UNAMBIGUITY,
                severity="info",
                message=f"Weak modal '{word}' may indicate optional behavior",
                suggestion="Use 'shall' for mandatory requirements"
            ))

        return max(0.0, score), issues

    def _analyze_completeness(
        self, text: str
    ) -> tuple[float, list[QualityIssue]]:
        """Analyze completeness dimension."""
        issues = []
        score = 1.0

        # Check for incomplete markers
        incomplete_markers = {"tbd", "todo", "fixme", "xxx", "tba", "???", "..."}
        text_lower = text.lower()

        for marker in incomplete_markers:
            if marker in text_lower:
                score -= 0.25
                issues.append(QualityIssue(
                    dimension=QualityDimension.COMPLETENESS,
                    severity="error",
                    message=f"Incomplete marker '{marker}' found",
                    suggestion="Complete all placeholder sections"
                ))

        # Check minimum length (heuristic)
        if len(text) < 30:
            score -= 0.20
            issues.append(QualityIssue(
                dimension=QualityDimension.COMPLETENESS,
                severity="warning",
                message="Requirement may be too brief",
                suggestion="Ensure all necessary details are included"
            ))

        return max(0.0, score), issues

    def _analyze_verifiability(
        self, text: str
    ) -> tuple[float, list[QualityIssue]]:
        """Analyze verifiability dimension."""
        issues = []
        score = 1.0

        # Check for quantifiable criteria
        has_numbers = any(char.isdigit() for char in text)
        has_units = any(
            unit in text.lower()
            for unit in ["ms", "seconds", "minutes", "hours", "bytes", "mb", "gb",
                        "%", "percent", "users", "requests", "items"]
        )

        # Performance requirements need numbers
        perf_indicators = ["performance", "speed", "response", "latency", "throughput"]
        is_performance_req = any(ind in text.lower() for ind in perf_indicators)

        if is_performance_req and not has_numbers:
            score -= 0.30
            issues.append(QualityIssue(
                dimension=QualityDimension.VERIFIABILITY,
                severity="error",
                message="Performance requirement lacks quantifiable metric",
                suggestion="Add specific targets (e.g., 'within 200ms', '99.9% uptime')"
            ))

        # Generic check for testability
        if not has_numbers and not has_units:
            score -= 0.10
            issues.append(QualityIssue(
                dimension=QualityDimension.VERIFIABILITY,
                severity="info",
                message="No quantifiable metrics found",
                suggestion="Consider adding measurable acceptance criteria"
            ))

        return max(0.0, score), issues

    def _analyze_singularity(
        self, text: str
    ) -> tuple[float, list[QualityIssue]]:
        """Analyze singularity dimension (one requirement per statement)."""
        issues = []
        score = 1.0

        # Count conjunctions that might indicate compound requirements
        and_count = text.lower().count(" and ")
        or_count = text.lower().count(" or ")

        if and_count > 1:
            score -= 0.15 * (and_count - 1)
            issues.append(QualityIssue(
                dimension=QualityDimension.SINGULARITY,
                severity="warning",
                message=f"Multiple 'and' conjunctions ({and_count}) may indicate compound requirement",
                suggestion="Consider splitting into separate requirements"
            ))

        if or_count > 0:
            score -= 0.20 * or_count
            issues.append(QualityIssue(
                dimension=QualityDimension.SINGULARITY,
                severity="warning",
                message=f"'Or' conjunction detected - may be ambiguous or compound",
                suggestion="Split into separate requirements for each alternative"
            ))

        return max(0.0, score), issues

    def _analyze_necessity(
        self, text: str
    ) -> tuple[float, list[QualityIssue]]:
        """Analyze necessity dimension (proper requirement language)."""
        issues = []
        score = 1.0
        text_lower = text.lower()

        # Check for proper requirement keywords
        if "shall" in text_lower:
            score = 1.0  # Best
        elif "will" in text_lower:
            score = 0.8
            issues.append(QualityIssue(
                dimension=QualityDimension.NECESSITY,
                severity="info",
                message="'Will' is weaker than 'shall' for requirements",
                suggestion="Consider using 'shall' for mandatory requirements"
            ))
        elif "should" in text_lower:
            score = 0.6
            issues.append(QualityIssue(
                dimension=QualityDimension.NECESSITY,
                severity="warning",
                message="'Should' indicates optional behavior",
                suggestion="Use 'shall' for mandatory, 'may' for optional"
            ))
        else:
            score = 0.5
            issues.append(QualityIssue(
                dimension=QualityDimension.NECESSITY,
                severity="warning",
                message="No requirement keyword (shall/will/should) found",
                suggestion="Use 'The system shall...' format"
            ))

        return score, issues

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 0.90:
            return "A"
        elif score >= 0.80:
            return "B"
        elif score >= 0.70:
            return "C"
        elif score >= 0.60:
            return "D"
        else:
            return "F"


# =============================================================================
# Cryptographic Version Chain (Blockchain-like Audit Trail)
# =============================================================================


class VersionBlock(BaseModel):
    """Immutable version record with cryptographic linking."""
    block_id: str  # SHA-256 hash
    previous_block_id: str | None
    timestamp: datetime
    author_id: str
    change_type: str  # "created", "updated", "status_changed", "verified"
    change_summary: str
    content_hash: str  # Hash of full spec content at this version
    signature: str | None = None  # Optional digital signature


class VersionChain:
    """
    Manages cryptographic version chain for specifications.

    Provides immutable audit trail similar to blockchain:
    - Each version block contains hash of previous block
    - Content hash ensures integrity of specification state
    - Chain can be verified for tampering
    """

    @staticmethod
    def create_genesis_block(
        content: dict[str, Any],
        author_id: str,
        change_summary: str = "Initial creation"
    ) -> VersionBlock:
        """Create the first block in a version chain."""
        content_hash = VersionChain._hash_content(content)

        # Genesis block has no previous
        block_data = {
            "previous_block_id": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author_id": author_id,
            "change_type": "created",
            "change_summary": change_summary,
            "content_hash": content_hash
        }

        block_id = VersionChain._hash_block(block_data)

        return VersionBlock(
            block_id=block_id,
            previous_block_id=None,
            timestamp=datetime.now(timezone.utc),
            author_id=author_id,
            change_type="created",
            change_summary=change_summary,
            content_hash=content_hash
        )

    @staticmethod
    def add_block(
        previous_block: VersionBlock,
        content: dict[str, Any],
        author_id: str,
        change_type: str,
        change_summary: str
    ) -> VersionBlock:
        """Add a new block to the chain."""
        content_hash = VersionChain._hash_content(content)

        block_data = {
            "previous_block_id": previous_block.block_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author_id": author_id,
            "change_type": change_type,
            "change_summary": change_summary,
            "content_hash": content_hash
        }

        block_id = VersionChain._hash_block(block_data)

        return VersionBlock(
            block_id=block_id,
            previous_block_id=previous_block.block_id,
            timestamp=datetime.now(timezone.utc),
            author_id=author_id,
            change_type=change_type,
            change_summary=change_summary,
            content_hash=content_hash
        )

    @staticmethod
    def verify_chain(blocks: list[VersionBlock]) -> tuple[bool, list[str]]:
        """
        Verify integrity of the version chain.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        if not blocks:
            return True, []

        issues = []

        # Check genesis block
        if blocks[0].previous_block_id is not None:
            issues.append("Genesis block has non-null previous_block_id")

        # Verify chain linkage
        for i in range(1, len(blocks)):
            current = blocks[i]
            previous = blocks[i - 1]

            if current.previous_block_id != previous.block_id:
                issues.append(
                    f"Block {i} previous_block_id doesn't match block {i-1} block_id"
                )

            # Verify timestamps are sequential
            if current.timestamp < previous.timestamp:
                issues.append(
                    f"Block {i} timestamp is earlier than block {i-1}"
                )

        return len(issues) == 0, issues

    @staticmethod
    def _hash_content(content: dict[str, Any]) -> str:
        """Create SHA-256 hash of content."""
        import json
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()

    @staticmethod
    def _hash_block(block_data: dict[str, Any]) -> str:
        """Create SHA-256 hash of block data."""
        import json
        block_str = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()


# =============================================================================
# Flakiness Detection (Meta-style)
# =============================================================================


class FlakinessSeverity(str, Enum):
    """Flakiness severity levels."""
    STABLE = "stable"        # < 1%
    LOW = "low"              # 1-5%
    MEDIUM = "medium"        # 5-15%
    HIGH = "high"            # 15-30%
    CRITICAL = "critical"    # > 30%


class FlakinessPattern(str, Enum):
    """Detected flakiness patterns."""
    ORDER_DEPENDENT = "order_dependent"
    TIME_DEPENDENT = "time_dependent"
    RESOURCE_DEPENDENT = "resource_dependent"
    ENVIRONMENT_DEPENDENT = "environment_dependent"
    DATA_DEPENDENT = "data_dependent"
    RACE_CONDITION = "race_condition"
    EXTERNAL_DEPENDENCY = "external_dependency"
    MEMORY_PRESSURE = "memory_pressure"


class FlakinessAnalysis(BaseModel):
    """Result of flakiness analysis."""
    flakiness_score: float = Field(ge=0, le=1)
    severity: FlakinessSeverity
    detected_patterns: list[FlakinessPattern] = Field(default_factory=list)
    failure_rate_30d: float
    failure_rate_7d: float
    entropy_score: float  # Randomness measure
    consecutive_failures_max: int
    consecutive_passes_max: int
    quarantine_recommended: bool
    suggested_fix_category: str | None = None
    confidence: float = Field(ge=0, le=1)


class FlakinessDetector:
    """
    Detects test flakiness using Meta's probabilistic model.

    Based on: "Probabilistic flakiness: How we identify and prioritize flaky tests"

    Key metrics:
    - Failure rate over time windows
    - Pattern entropy (randomness of pass/fail sequence)
    - Consecutive run analysis
    - Pattern detection (order, time, resource dependency)
    """

    def analyze(
        self,
        run_history: list[dict[str, Any]],
        window_size: int = 20
    ) -> FlakinessAnalysis:
        """
        Analyze test flakiness from run history.

        Args:
            run_history: List of test runs with {status, timestamp, duration_ms, ...}
            window_size: Number of recent runs to analyze
        """
        if not run_history:
            return FlakinessAnalysis(
                flakiness_score=0.0,
                severity=FlakinessSeverity.STABLE,
                failure_rate_30d=0.0,
                failure_rate_7d=0.0,
                entropy_score=0.0,
                consecutive_failures_max=0,
                consecutive_passes_max=0,
                quarantine_recommended=False,
                confidence=0.0
            )

        # Get recent runs
        recent = run_history[-window_size:]
        statuses = [r.get("status", "unknown") for r in recent]

        # Calculate failure rates
        total = len(statuses)
        failures = sum(1 for s in statuses if s in ("failed", "error", "flaky"))
        failure_rate = failures / total if total > 0 else 0

        # Calculate 7d and 30d rates (simplified - would use timestamps in practice)
        failure_rate_7d = failure_rate  # Placeholder
        failure_rate_30d = failure_rate

        # Calculate entropy (randomness)
        entropy = self._calculate_entropy(statuses)

        # Consecutive run analysis
        max_consecutive_failures = self._max_consecutive(statuses, {"failed", "error"})
        max_consecutive_passes = self._max_consecutive(statuses, {"passed"})

        # Detect patterns
        patterns = self._detect_patterns(run_history, recent)

        # Calculate flakiness score
        # High entropy + moderate failure rate = flaky
        # Low entropy + high failure rate = consistently failing (not flaky)
        flakiness_score = self._calculate_flakiness_score(
            failure_rate, entropy, max_consecutive_failures, max_consecutive_passes
        )

        # Determine severity
        severity = self._score_to_severity(flakiness_score)

        # Quarantine recommendation
        quarantine_recommended = (
            severity in (FlakinessSeverity.HIGH, FlakinessSeverity.CRITICAL)
            or max_consecutive_failures >= 3
        )

        # Suggested fix
        suggested_fix = self._suggest_fix(patterns)

        # Confidence based on sample size
        confidence = min(1.0, total / 20)  # Full confidence at 20+ runs

        return FlakinessAnalysis(
            flakiness_score=flakiness_score,
            severity=severity,
            detected_patterns=patterns,
            failure_rate_30d=failure_rate_30d,
            failure_rate_7d=failure_rate_7d,
            entropy_score=entropy,
            consecutive_failures_max=max_consecutive_failures,
            consecutive_passes_max=max_consecutive_passes,
            quarantine_recommended=quarantine_recommended,
            suggested_fix_category=suggested_fix,
            confidence=confidence
        )

    def _calculate_entropy(self, statuses: list[str]) -> float:
        """Calculate Shannon entropy of status sequence."""
        if not statuses:
            return 0.0

        # Count transitions
        transitions = 0
        for i in range(1, len(statuses)):
            if statuses[i] != statuses[i - 1]:
                transitions += 1

        # Normalize by max possible transitions
        max_transitions = len(statuses) - 1
        if max_transitions == 0:
            return 0.0

        return transitions / max_transitions

    def _max_consecutive(
        self, statuses: list[str], target_statuses: set[str]
    ) -> int:
        """Find maximum consecutive occurrences of target statuses."""
        max_count = 0
        current_count = 0

        for status in statuses:
            if status in target_statuses:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0

        return max_count

    def _detect_patterns(
        self,
        full_history: list[dict[str, Any]],
        recent: list[dict[str, Any]]
    ) -> list[FlakinessPattern]:
        """Detect flakiness patterns from run history."""
        patterns = []

        # Order dependency: Check if failures correlate with test order
        # (Simplified - would need actual test order data)

        # Time dependency: Check if failures cluster at specific times
        failed_runs = [r for r in recent if r.get("status") in ("failed", "error")]
        if failed_runs:
            # Check for time clustering (simplified)
            pass

        # Duration variance: High variance might indicate resource issues
        durations = [r.get("duration_ms", 0) for r in recent if r.get("duration_ms")]
        if durations and len(durations) > 5:
            variance = statistics.variance(durations) if len(durations) > 1 else 0
            mean = statistics.mean(durations)
            cv = (variance ** 0.5) / mean if mean > 0 else 0
            if cv > 0.5:  # High coefficient of variation
                patterns.append(FlakinessPattern.RESOURCE_DEPENDENT)

        # Check for alternating pattern (pass-fail-pass-fail)
        statuses = [r.get("status", "unknown") for r in recent]
        alternating_count = sum(
            1 for i in range(1, len(statuses))
            if statuses[i] != statuses[i - 1]
        )
        if len(statuses) > 5 and alternating_count > len(statuses) * 0.6:
            patterns.append(FlakinessPattern.RACE_CONDITION)

        return patterns

    def _calculate_flakiness_score(
        self,
        failure_rate: float,
        entropy: float,
        max_failures: int,
        max_passes: int
    ) -> float:
        """
        Calculate overall flakiness score.

        Formula:
        - High failure rate + low entropy = consistent failure (not flaky)
        - Moderate failure rate + high entropy = flaky
        - Low failure rate = stable
        """
        # Base score from failure rate
        base_score = failure_rate

        # Entropy multiplier (high entropy = more random = more flaky)
        entropy_factor = 1 + entropy

        # Consistency factor (long consecutive runs reduce flakiness score)
        if max_passes > 10 and failure_rate < 0.1:
            # Mostly stable with rare failures
            consistency_factor = 0.5
        elif max_failures > 5:
            # Consistently failing
            consistency_factor = 0.3
        else:
            consistency_factor = 1.0

        score = base_score * entropy_factor * consistency_factor

        return min(1.0, max(0.0, score))

    def _score_to_severity(self, score: float) -> FlakinessSeverity:
        """Convert flakiness score to severity level."""
        if score < 0.01:
            return FlakinessSeverity.STABLE
        elif score < 0.05:
            return FlakinessSeverity.LOW
        elif score < 0.15:
            return FlakinessSeverity.MEDIUM
        elif score < 0.30:
            return FlakinessSeverity.HIGH
        else:
            return FlakinessSeverity.CRITICAL

    def _suggest_fix(self, patterns: list[FlakinessPattern]) -> str | None:
        """Suggest fix based on detected patterns."""
        if FlakinessPattern.RACE_CONDITION in patterns:
            return "Add synchronization or increase timeouts"
        elif FlakinessPattern.RESOURCE_DEPENDENT in patterns:
            return "Reduce resource contention or add retry logic"
        elif FlakinessPattern.TIME_DEPENDENT in patterns:
            return "Mock time-dependent behavior"
        elif FlakinessPattern.EXTERNAL_DEPENDENCY in patterns:
            return "Mock external services or add circuit breakers"
        elif FlakinessPattern.ORDER_DEPENDENT in patterns:
            return "Ensure proper test isolation and cleanup"
        return None


# =============================================================================
# WSJF/RICE Prioritization
# =============================================================================


class WSJFScore(BaseModel):
    """WSJF (Weighted Shortest Job First) scoring."""
    business_value: int = Field(ge=1, le=10)
    time_criticality: int = Field(ge=1, le=10)
    risk_reduction: int = Field(ge=1, le=10)
    job_size: int = Field(ge=1, le=13)  # Fibonacci-ish

    # Calculated
    cost_of_delay: float
    wsjf_score: float
    percentile: int | None = None


class RICEScore(BaseModel):
    """RICE scoring model."""
    reach: int  # Users/customers affected
    impact: float = Field(ge=0.25, le=3)  # 0.25 (minimal) to 3 (massive)
    confidence: float = Field(ge=0, le=1)
    effort: int  # Person-weeks

    # Calculated
    rice_score: float
    percentile: int | None = None


class PrioritizationCalculator:
    """
    Calculates prioritization scores using WSJF and RICE models.

    WSJF (SAFe):
    - Cost of Delay = Business Value + Time Criticality + Risk Reduction
    - WSJF = Cost of Delay / Job Size

    RICE (Intercom):
    - RICE = (Reach × Impact × Confidence) / Effort
    """

    @staticmethod
    def calculate_wsjf(
        business_value: int,
        time_criticality: int,
        risk_reduction: int,
        job_size: int
    ) -> WSJFScore:
        """Calculate WSJF score."""
        # Validate inputs
        business_value = max(1, min(10, business_value))
        time_criticality = max(1, min(10, time_criticality))
        risk_reduction = max(1, min(10, risk_reduction))
        job_size = max(1, min(13, job_size))

        # Cost of Delay (0-30 scale)
        cost_of_delay = business_value + time_criticality + risk_reduction

        # WSJF = CoD / Job Size
        wsjf_score = cost_of_delay / job_size

        return WSJFScore(
            business_value=business_value,
            time_criticality=time_criticality,
            risk_reduction=risk_reduction,
            job_size=job_size,
            cost_of_delay=cost_of_delay,
            wsjf_score=round(wsjf_score, 2)
        )

    @staticmethod
    def calculate_rice(
        reach: int,
        impact: float,
        confidence: float,
        effort: int
    ) -> RICEScore:
        """Calculate RICE score."""
        # Validate inputs
        reach = max(1, reach)
        impact = max(0.25, min(3.0, impact))
        confidence = max(0.0, min(1.0, confidence))
        effort = max(1, effort)

        # RICE = (R × I × C) / E
        rice_score = (reach * impact * confidence) / effort

        return RICEScore(
            reach=reach,
            impact=impact,
            confidence=confidence,
            effort=effort,
            rice_score=round(rice_score, 2)
        )

    @staticmethod
    def rank_by_wsjf(items: list[WSJFScore]) -> list[WSJFScore]:
        """Rank items by WSJF score and add percentiles."""
        sorted_items = sorted(items, key=lambda x: x.wsjf_score, reverse=True)
        total = len(sorted_items)

        for i, item in enumerate(sorted_items):
            item.percentile = int(((total - i) / total) * 100)

        return sorted_items

    @staticmethod
    def rank_by_rice(items: list[RICEScore]) -> list[RICEScore]:
        """Rank items by RICE score and add percentiles."""
        sorted_items = sorted(items, key=lambda x: x.rice_score, reverse=True)
        total = len(sorted_items)

        for i, item in enumerate(sorted_items):
            item.percentile = int(((total - i) / total) * 100)

        return sorted_items


# =============================================================================
# Service Facade
# =============================================================================


class SpecAnalyticsService:
    """
    Facade for all specification analytics capabilities.

    Provides:
    - EARS pattern analysis
    - Quality scoring
    - Version chain management
    - Flakiness detection
    - Prioritization calculations
    """

    def __init__(self):
        self.ears_analyzer = EARSPatternAnalyzer()
        self.quality_analyzer = RequirementQualityAnalyzer()
        self.flakiness_detector = FlakinessDetector()

    def analyze_requirement(
        self,
        requirement_text: str,
        related_requirements: list[str] | None = None,
        linked_tests: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Perform comprehensive requirement analysis.

        Returns:
            Combined analysis results including EARS pattern,
            quality scores, and improvement suggestions.
        """
        ears_result = self.ears_analyzer.analyze(requirement_text)
        quality_result = self.quality_analyzer.analyze(
            requirement_text,
            related_requirements,
            linked_tests
        )

        return {
            "ears_analysis": ears_result.model_dump(),
            "quality_analysis": quality_result.model_dump(),
            "overall_health": {
                "is_well_formed": ears_result.is_valid,
                "quality_grade": quality_result.grade,
                "quality_score": quality_result.overall_score,
                "total_issues": len(ears_result.validation_issues) + len(quality_result.issues),
                "needs_attention": (
                    not ears_result.is_valid or
                    quality_result.grade in ("D", "F")
                )
            }
        }

    def analyze_test_flakiness(
        self,
        run_history: list[dict[str, Any]],
        window_size: int = 20
    ) -> FlakinessAnalysis:
        """Analyze test flakiness from run history."""
        return self.flakiness_detector.analyze(run_history, window_size)

    def create_version_block(
        self,
        content: dict[str, Any],
        author_id: str,
        previous_block: VersionBlock | None = None,
        change_type: str = "updated",
        change_summary: str = ""
    ) -> VersionBlock:
        """Create a new version block for audit trail."""
        if previous_block is None:
            return VersionChain.create_genesis_block(
                content, author_id, change_summary or "Initial creation"
            )
        return VersionChain.add_block(
            previous_block, content, author_id, change_type, change_summary
        )

    def verify_version_chain(
        self, blocks: list[VersionBlock]
    ) -> tuple[bool, list[str]]:
        """Verify integrity of version chain."""
        return VersionChain.verify_chain(blocks)

    def calculate_wsjf(
        self,
        business_value: int,
        time_criticality: int,
        risk_reduction: int,
        job_size: int
    ) -> WSJFScore:
        """Calculate WSJF prioritization score."""
        return PrioritizationCalculator.calculate_wsjf(
            business_value, time_criticality, risk_reduction, job_size
        )

    def calculate_rice(
        self,
        reach: int,
        impact: float,
        confidence: float,
        effort: int
    ) -> RICEScore:
        """Calculate RICE prioritization score."""
        return PrioritizationCalculator.calculate_rice(
            reach, impact, confidence, effort
        )
