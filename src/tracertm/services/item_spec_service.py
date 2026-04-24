"""Services for enhanced Item specifications.

Provides business logic for calculating derived properties, quality scores,
impact analysis, and other smart contract-like behaviors across different
item specification types.

Implements:
- ISO 29148 quality scoring algorithms
- INCOSE requirement patterns and rules
- Flakiness detection and volatility tracking
- Impact analysis and change propagation
- WSJF (Weighted Shortest Job First) priority calculation
- AI-derived property placeholders for future embeddings
"""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.requirement_quality import RequirementQuality
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.requirement_quality_repository import (
    RequirementQualityRepository,
)

# Singularity / conjunctions
MAX_CONJUNCTIONS_SINGULARITY_WARNING = 2

# CPI risk thresholds (0-1)
CPI_CRITICAL = 0.5
CPI_HIGH = 0.3
CPI_MEDIUM = 0.1
CPI_REQUIRES_REVIEW = 0.2
CPI_NOTIFICATION_NEEDED = 0.15

# Volatility / flakiness categorization
VOLATILITY_CRITICAL = 0.7
VOLATILITY_HIGH = 0.4
VOLATILITY_MEDIUM = 0.2
VOLATILITY_LOW = 0.05

# WSJF
WSJF_JOB_SIZE_FLOOR = 0.01

# Dashboard / health
QUALITY_ISSUE_THRESHOLD = 0.6
HIGH_VOLATILITY_INDEX = 0.5
HIGH_IMPACT_INDEX = 0.3
HEALTH_WEIGHT_QUALITY = 0.5
HEALTH_WEIGHT_VOLATILITY = 0.3
HEALTH_WEIGHT_CPI = 0.2

# Flakiness pattern
MIN_FAILURES_FOR_PATTERN = 3
FLAKINESS_TRANSITION_WEIGHT = 0.3
FLAKINESS_BASE_WEIGHT = 0.7
FLAKINESS_ERROR_VARIANCE_WEIGHT = 0.2
FLAKINESS_ERROR_BASE_WEIGHT = 0.8


class RequirementQualityAnalyzer:
    """Analyzes requirement text for quality issues using ISO 29148.

    and INCOSE quality patterns.

    ISO 29148 quality dimensions:
    - Unambiguity: Clear, precise language without vague terms
    - Completeness: All necessary information is present
    - Verifiability: Can be tested and objectively verified
    - Necessity: Requirements are essential and not redundant
    - Singularity: One requirement per statement (atomic)
    """

    # Ambiguity indicators (words that make requirements vague)
    AMBIGUOUS_WORDS: ClassVar[set[str]] = {
        "appropriate",
        "adequate",
        "efficient",
        "flexible",
        "friendly",
        "good",
        "high",
        "low",
        "maximum",
        "minimum",
        "normal",
        "optimal",
        "reasonable",
        "robust",
        "significant",
        "sufficient",
        "timely",
        "user-friendly",
        "easy",
        "fast",
        "simple",
        "complex",
        "pretty",
        "nice",
        "clean",
    }

    # Incomplete indicators (regex patterns)
    INCOMPLETE_PATTERNS: ClassVar[list[str]] = [
        r"\bTBD\b",
        r"\bTBC\b",
        r"\bTODO\b",
        r"\bFIXME\b",
        r"\.\.\.",
        r"\b\?\b",
        r"\bnot yet\b",
        r"\blater\b",
        r"\bunknown\b",
        r"\basync\b",
    ]

    # Untestable indicators (absolute/universal quantifiers)
    UNTESTABLE_WORDS: ClassVar[set[str]] = {
        "all",
        "always",
        "never",
        "every",
        "any",
        "none",
        "no",
    }

    # Weak requirement verbs
    WEAK_VERBS: ClassVar[set[str]] = {
        "may",
        "might",
        "could",
        "should",
        "would",
        "can",
        "ought",
        "want",
        "need",
        "desire",
        "wish",
        "try",
        "attempt",
    }

    # Strong requirement verbs (preferred)
    STRONG_VERBS: ClassVar[set[str]] = {
        "shall",
        "must",
        "will",
        "is",
        "are",
        "requires",
        "required",
    }

    def analyze(self, text: str, title: str = "") -> dict[str, Any]:
        """Analyze requirement text and return quality scores and issues.

        Args:
            text: Requirement description text
            title: Requirement title

        Returns:
            Dictionary with scores, issues, and recommendations:
            {
                "scores": {
                    "unambiguity": float,
                    "completeness": float,
                    "verifiability": float,
                    "necessity": float,
                    "singularity": float,
                },
                "issues": [
                    {
                        "dimension": str,
                        "severity": "error|warning|info",
                        "message": str,
                        "suggestion": str
                    }
                ],
                "overall_score": float,
                "ambiguous_terms": list[str],
                "missing_criteria": bool,
                "has_quantifiable_criteria": bool,
            }
        """
        full_text = f"{title} {text}".lower()
        issues = []
        scores = {}

        # 1. Analyze unambiguity (absence of vague terms)
        ambiguous_found = [w for w in self.AMBIGUOUS_WORDS if re.search(r"\b" + w + r"\b", full_text)]
        ambiguity_score = max(0, 1 - len(ambiguous_found) * 0.1)
        scores["unambiguity"] = ambiguity_score

        issues.extend([
            {
                "dimension": "unambiguity",
                "severity": "warning",
                "message": f"Ambiguous term found: '{word}'",
                "suggestion": f"Replace '{word}' with specific, measurable criteria",
            }
            for word in ambiguous_found
        ])

        # 2. Analyze completeness (no TBD/TODO markers)
        incomplete_count = sum(1 for p in self.INCOMPLETE_PATTERNS if re.search(p, full_text, re.IGNORECASE))
        completeness_score = max(0, 1 - incomplete_count * 0.25)
        scores["completeness"] = completeness_score

        if incomplete_count > 0:
            issues.append({
                "dimension": "completeness",
                "severity": "error",
                "message": "Requirement contains incomplete markers (TBD, TODO, etc.)",
                "suggestion": "Complete all placeholder content before finalizing",
            })

        # 3. Analyze verifiability (testability)
        untestable_count = sum(1 for w in self.UNTESTABLE_WORDS if re.search(r"\b" + w + r"\b", full_text))
        verifiability_score = max(0, 1 - untestable_count * 0.15)

        # Boost score if quantifiable criteria present
        has_numbers = bool(re.search(r"\d+", text))
        has_time_constraint = bool(
            re.search(
                r"\d+\s*(ms|sec|min|minute|hour|day|week|month|second)",
                text,
                re.IGNORECASE,
            ),
        )
        has_performance_metric = bool(
            re.search(
                r"(latency|throughput|cpu|memory|bandwidth|percentage|threshold|limit)",
                text,
                re.IGNORECASE,
            ),
        )

        if has_numbers or has_time_constraint or has_performance_metric:
            verifiability_score = min(1.0, verifiability_score + 0.15)

        scores["verifiability"] = verifiability_score

        if untestable_count > 0:
            issues.append({
                "dimension": "verifiability",
                "severity": "warning",
                "message": "Absolute quantifiers found: may be difficult to test",
                "suggestion": "Use measurable acceptance criteria instead of universal quantifiers",
            })

        # 4. Analyze necessity (strong requirement language)
        weak_found = [v for v in self.WEAK_VERBS if re.search(r"\b" + v + r"\b", full_text)]
        strong_found = [v for v in self.STRONG_VERBS if re.search(r"\b" + v + r"\b", full_text)]

        necessity_score = 1.0 if strong_found else 0.5
        necessity_score = max(0, necessity_score - len(weak_found) * 0.1)
        scores["necessity"] = necessity_score

        if weak_found and not strong_found:
            issues.append({
                "dimension": "necessity",
                "severity": "warning",
                "message": f"Weak requirement verbs: {', '.join(weak_found)}",
                "suggestion": "Use 'shall' for mandatory, 'will' for design decisions, 'is' for constraints",
            })

        # 5. Analyze singularity (one requirement per statement)
        and_count = len(re.findall(r"\band\b", full_text, re.IGNORECASE))
        or_count = len(re.findall(r"\bor\b", full_text, re.IGNORECASE))
        conjunction_count = and_count + or_count

        singularity_score = max(0, 1 - conjunction_count * 0.15)
        scores["singularity"] = singularity_score

        if conjunction_count > MAX_CONJUNCTIONS_SINGULARITY_WARNING:
            issues.append({
                "dimension": "singularity",
                "severity": "warning",
                "message": f"Requirement may contain multiple sub-requirements ({conjunction_count} conjunctions)",
                "suggestion": "Split into separate, atomic requirements",
            })

        # Calculate weighted overall score (ISO 29148 weighting)
        weights = {
            "unambiguity": 0.25,
            "completeness": 0.20,
            "verifiability": 0.25,
            "necessity": 0.15,
            "singularity": 0.15,
        }

        overall_score = sum(scores.get(dim, 0.5) * weight for dim, weight in weights.items())

        # Sort issues by severity
        severity_order = {"error": 0, "warning": 1, "info": 2}
        issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return {
            "scores": scores,
            "issues": issues,
            "overall_score": overall_score,
            "ambiguous_terms": ambiguous_found,
            "missing_criteria": not (has_numbers or has_time_constraint),
            "has_quantifiable_criteria": has_numbers or has_time_constraint,
        }


class ImpactAnalyzer:
    """Analyzes impact propagation and change effects across requirement.

    and work item hierarchies.

    Calculates:
    - Change Propagation Index (CPI)
    - Downstream/upstream impact
    - Risk assessment based on affected items
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.link_repo = LinkRepository(session)
        self.item_repo = ItemRepository(session)

    async def calculate_impact(self, item_id: str, project_id: str) -> dict[str, Any]:
        """Calculate comprehensive impact metrics including change propagation index.

        Change Propagation Index (CPI):
            CPI = (direct_downstream + 0.5 * indirect_downstream) / total_items

        Higher CPI indicates higher risk of cascading impacts.

        Args:
            item_id: Item to analyze
            project_id: Project ID for scope

        Returns:
            Dictionary with impact metrics and assessment
        """
        # Query direct downstream links (outgoing)
        downstream_result = await self.session.execute(
            select(Link.target_item_id).where(Link.source_item_id == item_id, Link.project_id == project_id),
        )
        direct_downstream = [row[0] for row in downstream_result.fetchall()]

        # Query indirect downstream (2 levels deep)
        indirect_downstream = set()
        if direct_downstream:
            indirect_result = await self.session.execute(
                select(Link.target_item_id).where(
                    Link.source_item_id.in_(direct_downstream),
                    Link.project_id == project_id,
                    Link.target_item_id.notin_(direct_downstream),
                    Link.target_item_id != item_id,
                ),
            )
            indirect_downstream = {row[0] for row in indirect_result.fetchall()}

        # Query upstream links (incoming)
        upstream_result = await self.session.execute(
            select(Link.source_item_id).where(Link.target_item_id == item_id, Link.project_id == project_id),
        )
        upstream = [row[0] for row in upstream_result.fetchall()]

        # Get total item count for CPI calculation
        total_count_result = await self.session.execute(
            select(func.count(Item.id)).where(Item.project_id == project_id),
        )
        total_items = total_count_result.scalar() or 1

        # Calculate CPI (normalized 0-1)
        weighted_downstream = len(direct_downstream) + (len(indirect_downstream) * 0.5)
        cpi = min(1.0, weighted_downstream / max(total_items, 1))

        # Determine risk level
        if cpi > CPI_CRITICAL:
            risk_level = "critical"
        elif cpi > CPI_HIGH:
            risk_level = "high"
        elif cpi > CPI_MEDIUM:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "change_propagation_index": cpi,
            "downstream_count": len(direct_downstream) + len(indirect_downstream),
            "upstream_count": len(upstream),
            "direct_downstream": direct_downstream,
            "indirect_downstream": list(indirect_downstream),
            "upstream": upstream,
            "impact_breadth": len(set(direct_downstream + upstream)),
            "impact_assessment": {
                "high_impact": cpi > CPI_HIGH,
                "risk_level": risk_level,
                "requires_review": cpi > CPI_REQUIRES_REVIEW,
                "notification_needed": cpi > CPI_NOTIFICATION_NEEDED,
            },
        }


class VolatilityTracker:
    """Tracks requirement and work item volatility index (RVI).

    Requirements Volatility Index (RVI):
        RVI = (change_frequency * recency_weight) / total_age_days

    Higher RVI indicates unstable, frequently-changing requirements that
    may indicate:
    - Incomplete or poorly understood requirements
    - Scope creep
    - Technical debt
    """

    def calculate_volatility(
        self,
        change_count: int,
        days_since_creation: int,
        change_history: list[dict] | None = None,
    ) -> float:
        """Calculate Requirements Volatility Index.

        Args:
            change_count: Total number of changes/modifications
            days_since_creation: Days since item was created
            change_history: List of recent changes with timestamps

        Returns:
            Volatility score (0.0-1.0), normalized
        """
        if days_since_creation <= 0:
            return 0.0

        # Base volatility: changes per day
        base_volatility = change_count / days_since_creation

        # Recency weight: emphasize recent changes
        recency_weight = 1.0
        if change_history and len(change_history) > 0:
            recent_count = min(len(change_history), 10)
            recency_weight = 1 + (recent_count / 10) * 0.5

        # Calculate RVI
        rvi = base_volatility * recency_weight

        # Normalize to 0-1 range
        # Assumption: >0.5 changes/day is high volatility
        return min(1.0, rvi)

    def categorize_volatility(self, volatility_score: float) -> str:
        """Categorize volatility into levels."""
        if volatility_score > VOLATILITY_CRITICAL:
            return "critical"
        if volatility_score > VOLATILITY_HIGH:
            return "high"
        if volatility_score > VOLATILITY_MEDIUM:
            return "medium"
        if volatility_score > VOLATILITY_LOW:
            return "low"
        return "stable"


class WSJFCalculator:
    """Calculates WSJF (Weighted Shortest Job First) priority.

    WSJF = (Business Value + Time Sensitivity + Risk Reduction) / Job Size

    Used for prioritization in agile/SAFe frameworks.
    """

    # WSJF scales (typically 1-20 or similar)
    DEFAULT_SCALE = 20

    def calculate_wsjf(
        self,
        business_value: float = 0.5,
        time_sensitivity: float = 0.5,
        risk_reduction: float = 0.5,
        job_size: float = 0.5,
    ) -> float:
        """Calculate WSJF priority score.

        Args:
            business_value: Business value score (0-1)
            time_sensitivity: Time sensitivity score (0-1)
            risk_reduction: Risk reduction benefit (0-1)
            job_size: Effort/complexity (0-1)

        Returns:
            WSJF score, higher is better priority
        """
        # Ensure valid range
        business_value = max(0, min(1, business_value))
        time_sensitivity = max(0, min(1, time_sensitivity))
        risk_reduction = max(0, min(1, risk_reduction))
        job_size = max(0, min(1, job_size))

        # Avoid division by zero
        job_size = max(job_size, WSJF_JOB_SIZE_FLOOR)

        # Standard WSJF formula with weights
        numerator = (business_value * 0.4) + (time_sensitivity * 0.3) + (risk_reduction * 0.3)
        wsjf = numerator / job_size

        # Normalize to 0-1 range
        return min(1.0, wsjf)


@dataclass
class RecordChangeInput:
    """Input for recording a change on a requirement spec."""

    item_id: str
    changed_by: str
    change_type: str
    summary: str
    previous_values: dict | None = None
    new_values: dict | None = None


class RequirementSpecService:
    """Service for RequirementSpec business logic and derived calculations.

    Handles:
    - Quality analysis and scoring
    - Impact propagation analysis
    - Change tracking and volatility
    - Requirement verification
    - Traceability updates
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.item_repo = ItemRepository(session)
        self.quality_repo = RequirementQualityRepository(session)
        self.quality_analyzer = RequirementQualityAnalyzer()
        self.impact_analyzer = ImpactAnalyzer(session)
        self.volatility_tracker = VolatilityTracker()
        self.wsjf_calculator = WSJFCalculator()

    async def create_spec(
        self,
        item_id: str,
        business_value: float | None = None,
        time_sensitivity: float | None = None,
        risk_reduction: float | None = None,
        job_size: float | None = None,
        **kwargs: object,
    ) -> RequirementQuality:
        """Create a requirement specification and analyze quality.

        Args:
            item_id: Item to create spec for
            business_value: WSJF business value component
            time_sensitivity: WSJF time sensitivity component
            risk_reduction: WSJF risk reduction component
            job_size: WSJF job size component
            **kwargs: Additional spec data

        Returns:
            Created RequirementQuality with analysis
        """
        # Get the item for text analysis
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        # Analyze quality
        quality = self.quality_analyzer.analyze(item.description or "", item.title)

        # Calculate impact
        impact = await self.impact_analyzer.calculate_impact(item_id, str(item.project_id))

        # Calculate WSJF if components provided
        wsjf_score = None
        if all(x is not None for x in [business_value, time_sensitivity, risk_reduction, job_size]):
            assert business_value is not None
            assert time_sensitivity is not None
            assert risk_reduction is not None
            assert job_size is not None
            wsjf_score = self.wsjf_calculator.calculate_wsjf(
                float(business_value),
                float(time_sensitivity),
                float(risk_reduction),
                float(job_size),
            )

        # Create spec with all derived properties
        return await self.quality_repo.create(
            item_id=item_id,
            project_id=str(item.project_id),
            quality_scores=quality["scores"],
            overall_quality_score=quality["overall_score"],
            quality_issues=quality["issues"],
            change_propagation_index=impact["change_propagation_index"],
            downstream_impact_count=impact["downstream_count"],
            upstream_dependency_count=impact["upstream_count"],
            impact_assessment=impact["impact_assessment"],
            wsjf_score=wsjf_score,
            **kwargs,
        )

    async def refresh_quality_analysis(self, item_id: str) -> RequirementQuality:
        """Re-analyze quality metrics for a requirement.

        Args:
            item_id: Item to re-analyze

        Returns:
            Updated RequirementQuality
        """
        # Get item and existing spec
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        # Analyze quality
        quality = self.quality_analyzer.analyze(item.description or "", item.title)

        # Get or create spec
        existing_spec = await self.quality_repo.get_by_item_id(item_id)

        if existing_spec:
            # Update existing
            spec = await self.quality_repo.update(
                existing_spec.id,
                quality_scores=quality["scores"],
                overall_quality_score=quality["overall_score"],
                quality_issues=quality["issues"],
                last_analyzed_at=datetime.now(UTC),
            )
        else:
            # Create new
            spec = await self.create_spec(item_id)

        return spec

    async def refresh_impact_analysis(self, item_id: str) -> RequirementQuality:
        """Refresh impact analysis for a requirement.

        Args:
            item_id: Item to analyze

        Returns:
            Updated RequirementQuality with impact metrics
        """
        # Get item
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        # Calculate impact
        impact = await self.impact_analyzer.calculate_impact(item_id, str(item.project_id))

        # Get or create spec
        existing_spec = await self.quality_repo.get_by_item_id(item_id)

        if existing_spec:
            spec = await self.quality_repo.update(
                existing_spec.id,
                change_propagation_index=impact["change_propagation_index"],
                downstream_impact_count=impact["downstream_count"],
                upstream_dependency_count=impact["upstream_count"],
                impact_assessment=impact["impact_assessment"],
            )
        else:
            spec = await self.create_spec(item_id)

        return spec

    async def record_change(self, input: RecordChangeInput) -> RequirementQuality:
        """Record a change and update volatility metrics.

        Args:
            input: Change record (item_id, changed_by, change_type, summary, previous_values, new_values).

        Returns:
            Updated RequirementQuality with volatility
        """
        return await self._apply_record_change(input)

    async def _apply_record_change(self, input: RecordChangeInput) -> RequirementQuality:
        spec = await self.quality_repo.get_by_item_id(input.item_id)
        if not spec:
            msg = f"RequirementQuality for item {input.item_id} not found"
            raise ValueError(msg)

        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "changed_by": input.changed_by,
            "change_type": input.change_type,
            "summary": input.summary,
            "previous_values": input.previous_values,
            "new_values": input.new_values,
        }

        # Update change history
        history = spec.change_history or []
        history.insert(0, entry)
        history = history[:100]  # Keep last 100 changes

        # Calculate days since creation
        days_since = (datetime.now(UTC) - spec.created_at.replace(tzinfo=UTC)).days

        # Update volatility
        new_count = spec.change_count + 1
        volatility = self.volatility_tracker.calculate_volatility(new_count, max(1, days_since), history)

        return await self.quality_repo.update(
            spec.id,
            change_count=new_count,
            change_history=history,
            volatility_index=volatility,
            last_changed_at=datetime.now(UTC),
        )

    async def calculate_wsjf(
        self,
        item_id: str,
        business_value: float,
        time_sensitivity: float,
        risk_reduction: float,
        job_size: float,
    ) -> RequirementQuality:
        """Calculate and update WSJF priority for a requirement.

        Args:
            item_id: Item to calculate for
            business_value: Business value (0-1)
            time_sensitivity: Time sensitivity (0-1)
            risk_reduction: Risk reduction (0-1)
            job_size: Job size/effort (0-1)

        Returns:
            Updated RequirementQuality with WSJF score
        """
        spec = await self.quality_repo.get_by_item_id(item_id)
        if not spec:
            msg = f"RequirementQuality for item {item_id} not found"
            raise ValueError(msg)

        wsjf_score = self.wsjf_calculator.calculate_wsjf(business_value, time_sensitivity, risk_reduction, job_size)

        return await self.quality_repo.update(
            spec.id,
            wsjf_score=wsjf_score,
            wsjf_components={
                "business_value": business_value,
                "time_sensitivity": time_sensitivity,
                "risk_reduction": risk_reduction,
                "job_size": job_size,
            },
        )

    async def verify_requirement(
        self,
        item_id: str,
        verified_by: str,
        evidence_type: str,
        evidence_reference: str,
        description: str,
    ) -> RequirementQuality:
        """Mark a requirement as verified with evidence.

        Args:
            item_id: Requirement item
            verified_by: User who verified
            evidence_type: Type of evidence (test, code, review, etc.)
            evidence_reference: Reference/link to evidence
            description: Verification description

        Returns:
            Updated RequirementQuality
        """
        spec = await self.quality_repo.get_by_item_id(item_id)
        if not spec:
            msg = f"RequirementQuality for item {item_id} not found"
            raise ValueError(msg)

        evidence = {
            "type": evidence_type,
            "reference": evidence_reference,
            "description": description,
            "verified_at": datetime.now(UTC).isoformat(),
            "verified_by": verified_by,
        }

        # Add to verification history
        verifications = spec.verification_evidence or []
        verifications.append(evidence)

        return await self.quality_repo.update(
            spec.id,
            is_verified=True,
            verified_at=datetime.now(UTC),
            verified_by=verified_by,
            verification_evidence=verifications,
        )

    async def get_health_report(self, project_id: str) -> dict[str, Any]:
        """Generate requirement health report for a project.

        Args:
            project_id: Project to report on

        Returns:
            Health metrics and issue summary
        """
        # Get all specs for project
        all_specs = await self.quality_repo.list_by_project(project_id, limit=1000)

        if not all_specs:
            return {
                "total_requirements": 0,
                "quality_issues": 0,
                "high_volatility": 0,
                "high_impact": 0,
                "unverified": 0,
                "health_score": 1.0,
            }

        # Analyze metrics
        quality_issues = [s for s in all_specs if s.overall_quality_score < QUALITY_ISSUE_THRESHOLD]
        high_volatility = [s for s in all_specs if (s.volatility_index or 0) > HIGH_VOLATILITY_INDEX]
        high_impact = [s for s in all_specs if (s.change_propagation_index or 0) > HIGH_IMPACT_INDEX]
        unverified = [s for s in all_specs if not s.is_verified]

        # Calculate average scores
        avg_quality = sum(s.overall_quality_score for s in all_specs) / len(all_specs)
        avg_volatility = sum(s.volatility_index or 0 for s in all_specs) / len(all_specs)
        avg_cpi = sum(s.change_propagation_index or 0 for s in all_specs) / len(all_specs)

        # Health score (weighted)
        health_score = (
            avg_quality * HEALTH_WEIGHT_QUALITY
            + (1 - avg_volatility) * HEALTH_WEIGHT_VOLATILITY
            + (1 - avg_cpi) * HEALTH_WEIGHT_CPI
        )

        return {
            "total_requirements": len(all_specs),
            "quality_issues_count": len(quality_issues),
            "high_volatility_count": len(high_volatility),
            "high_impact_count": len(high_impact),
            "unverified_count": len(unverified),
            "average_quality_score": avg_quality,
            "average_volatility": avg_volatility,
            "average_impact_index": avg_cpi,
            "verification_rate": (len(all_specs) - len(unverified)) / len(all_specs),
            "health_score": health_score,
            "issues_by_severity": self._categorize_issues([
                issue for spec in all_specs for issue in (spec.quality_issues or [])
            ]),
        }

    def _categorize_issues(self, issues: list[dict]) -> dict[str, int]:
        """Categorize issues by severity."""
        by_severity = {"error": 0, "warning": 0, "info": 0}
        for issue in issues:
            severity = issue.get("severity", "info")
            if severity in by_severity:
                by_severity[severity] += 1
        return by_severity


class TestSpecFlakinessDector:
    """Detects and tracks test flakiness using statistical analysis.

    Flakiness indicators:
    - Pass rate < 95% with high run count
    - Intermittent failures
    - Failure clustering
    - Environment sensitivity
    """

    def calculate_flakiness_score(
        self,
        _pass_count: int,
        fail_count: int,
        total_runs: int,
        recent_failures: list[dict],
    ) -> float:
        """Calculate test flakiness score (0-1).

        Args:
            pass_count: Number of passes
            fail_count: Number of failures
            total_runs: Total test runs
            recent_failures: Recent failure history

        Returns:
            Flakiness score (0=stable, 1=completely flaky)
        """
        if total_runs == 0:
            return 0.0

        # Base flakiness: failure rate
        failure_rate = fail_count / total_runs
        base_score = failure_rate

        # Pattern analysis: check for intermittent failures
        if len(recent_failures) >= MIN_FAILURES_FOR_PATTERN:
            transitions = sum(
                1
                for i in range(len(recent_failures) - 1)
                if recent_failures[i].get("status") != recent_failures[i + 1].get("status")
            )
            transition_rate = transitions / len(recent_failures)
            base_score = base_score * FLAKINESS_BASE_WEIGHT + transition_rate * FLAKINESS_TRANSITION_WEIGHT

        # Environment factor: same error in different environments suggests flakiness
        error_messages = [f.get("error") for f in recent_failures if f.get("error")]
        if error_messages:
            unique_errors = len(set(error_messages))
            error_variance = unique_errors / max(1, len(error_messages))
            base_score = base_score * FLAKINESS_ERROR_BASE_WEIGHT + error_variance * FLAKINESS_ERROR_VARIANCE_WEIGHT

        return min(1.0, base_score)

    def categorize_flakiness(self, score: float) -> str:
        """Categorize flakiness level."""
        if score > VOLATILITY_CRITICAL:
            return "critical"
        if score > VOLATILITY_HIGH:
            return "high"
        if score > VOLATILITY_MEDIUM:
            return "medium"
        if score > VOLATILITY_LOW:
            return "low"
        return "stable"


class AIPropertyPlaceholder:
    """Placeholder for AI-derived properties.

    Future implementations for:
    - Embedding-based similarity to other items
    - Semantic clustering of requirements
    - Anomaly detection in specifications
    - Auto-generated acceptance criteria
    - Cross-requirement consistency checking
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def calculate_embeddings(self, _item_id: str) -> list[float] | None:
        """Calculate semantic embeddings for requirement text.

        Future: Use OpenAI embeddings or similar.

        Args:
            item_id: Item to embed

        Returns:
            Embedding vector or None if not implemented
        """
        # Placeholder: return None for now
        return None

    async def find_similar_requirements(
        self,
        _item_id: str,
        _project_id: str,
        _threshold: float = 0.85,
    ) -> list[dict[str, Any]]:
        """Find semantically similar requirements.

        Future: Use vector similarity search.

        Args:
            item_id: Reference item
            project_id: Project scope
            threshold: Similarity threshold (0-1)

        Returns:
            List of similar items with scores
        """
        # Placeholder: return empty list for now
        return []

    async def detect_inconsistencies(self, _item_id: str) -> list[dict[str, str]]:
        """Detect inconsistencies with related requirements.

        Future: Use LLM-based analysis.

        Args:
            item_id: Item to check

        Returns:
            List of potential inconsistencies
        """
        # Placeholder: return empty list for now
        return []

    async def suggest_acceptance_criteria(self, _item_id: str) -> list[str]:
        """Generate suggested acceptance criteria for requirement.

        Future: Use generative AI.

        Args:
            item_id: Item to suggest for

        Returns:
            List of potential acceptance criteria
        """
        # Placeholder: return empty list for now
        return []
