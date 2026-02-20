"""Repositories for enhanced Item specifications.

Provides data access layer for RequirementSpec, TestSpec, EpicSpec,
UserStorySpec, TaskSpec, and DefectSpec entities with:
- CRUD operations
- Specialized query methods (by risk, status, type)
- Calculated field updates (volatility, flakiness, quality scores)
- Batch operations for efficiency

Architecture:
- Each spec type has its own repository class
- Repositories use AsyncSession for async/await
- All queries use parameterized statements
- Optimistic locking with version column
- Soft deletes via deleted_at
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Constants for spec metrics calculation
_FAKINESS_MIN_RUNS = 5
_FAKINESS_WINDOW_DEFAULT = 20
_FAKINESS_HIGH_THRESHOLD = 0.3
_PERFORMANCE_P95_MIN_SAMPLES = 20
_PERFORMANCE_P99_MIN_SAMPLES = 100
_PERFORMANCE_TREND_MIN_SAMPLES = 10
_PERFORMANCE_RECENT_SAMPLES = 5
_PERFORMANCE_OLDER_SAMPLES = 5


# Type Enums for specifications
class RequirementType(StrEnum):
    """Types of requirements."""

    UBIQUITOUS = "ubiquitous"
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"
    QUALITY = "quality"


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
# Base Repository Utility
# ==============================================================================


class BaseSpecRepository:
    """Base repository with common CRUD operations for all spec types."""

    def __init__(self, session: AsyncSession, model_class: type[Any]) -> None:
        """Initialize repository with database session and model class.

        Args:
            session: AsyncSession for database operations.
            model_class: SQLAlchemy model class for this repository.
        """
        self.session = session
        self.model_class: type[Any] = model_class

    async def get_by_id(self, spec_id: str) -> Any | None:
        """Get specification by ID."""
        query = select(self.model_class).where(self.model_class.id == spec_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_item_id(self, item_id: str) -> Any | None:
        """Get specification by associated item ID."""
        query = select(self.model_class).where(self.model_class.item_id == item_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, spec_id: str, **updates: Any) -> Any:
        """Update specification fields."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            msg = f"{self.model_class.__name__} {spec_id} not found"
            raise ValueError(msg)

        for key, value in updates.items():
            if hasattr(spec, key):
                setattr(spec, key, value)

        spec.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def delete(self, spec_id: str) -> bool:
        """Soft delete specification."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            return False
        spec.deleted_at = datetime.now(UTC)
        await self.session.flush()
        return True

    async def restore(self, spec_id: str) -> Any:
        """Restore soft-deleted specification."""
        query = select(self.model_class).where(self.model_class.id == spec_id)
        result = await self.session.execute(query)
        spec = result.scalar_one_or_none()
        if not spec:
            msg = f"{self.model_class.__name__} {spec_id} not found"
            raise ValueError(msg)
        spec.deleted_at = None
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def batch_update(self, updates: dict[str, dict[str, Any]]) -> list[Any]:
        """Batch update multiple specifications.

        Args:
            updates: Dict mapping spec_id to update dict

        Returns:
            List of updated specs
        """
        updated = []
        for spec_id, update_dict in updates.items():
            updated_spec = await self.update(spec_id, **update_dict)
            updated.append(updated_spec)
        await self.session.flush()
        return updated

    async def batch_delete(self, spec_ids: list[str]) -> int:
        """Soft delete multiple specifications.

        Returns:
            Count of deleted specs
        """
        now = datetime.now(UTC)
        query = (
            select(self.model_class)
            .where(self.model_class.id.in_(spec_ids))
            .where(self.model_class.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        specs = result.scalars().all()

        for spec in specs:
            spec.deleted_at = now

        await self.session.flush()
        return len(specs)

    async def get_active_count_by_project(self, project_id: str) -> int:
        """Get count of active (not deleted) specs for project."""
        from tracertm.models.item import Item

        query = (
            select(func.count(self.model_class.id))
            .join(Item, self.model_class.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                self.model_class.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0


# ==============================================================================
# RequirementSpecRepository
# ==============================================================================


class RequirementSpecRepository(BaseSpecRepository):
    """Repository for RequirementSpec CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize requirement specification repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        from tracertm.models.item_spec import RequirementSpec

        super().__init__(session, RequirementSpec)

    async def create(
        self,
        item_id: str,
        requirement_type: str = RequirementType.UBIQUITOUS.value,
        constraint_type: str = ConstraintType.HARD.value,
        **kwargs: Any,
    ) -> Any:
        """Create a new requirement specification."""
        from tracertm.models.item_spec import RequirementSpec

        spec = RequirementSpec(
            id=str(uuid4()),
            item_id=item_id,
            requirement_type=requirement_type,
            constraint_type=constraint_type,
            **kwargs,
        )
        self.session.add(spec)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def list_by_project(
        self,
        project_id: str,
        requirement_type: str | None = None,
        risk_level: str | None = None,
        verification_status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """List requirement specs for a project with filters."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import RequirementSpec

        query = (
            select(RequirementSpec)
            .join(Item, RequirementSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                RequirementSpec.deleted_at.is_(None),
            )
        )

        if requirement_type:
            query = query.where(RequirementSpec.requirement_type == requirement_type)
        if risk_level:
            query = query.where(RequirementSpec.risk_level == risk_level)
        if verification_status:
            query = query.where(RequirementSpec.verification_status == verification_status)

        query = query.order_by(RequirementSpec.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_quality_scores(
        self,
        spec_id: str,
        quality_scores: dict[str, float],
        ambiguity_score: float | None = None,
        completeness_score: float | None = None,
        testability_score: float | None = None,
        overall_quality_score: float | None = None,
        quality_issues: list[Any] | None = None,
    ) -> Any:
        """Update quality scores for a requirement spec."""
        return await self.update(
            spec_id,
            quality_scores=quality_scores,
            ambiguity_score=ambiguity_score,
            completeness_score=completeness_score,
            testability_score=testability_score,
            overall_quality_score=overall_quality_score,
            quality_issues=quality_issues or [],
        )

    async def update_volatility(self, spec_id: str, volatility_index: float, change_count: int) -> Any:
        """Update volatility metrics for a requirement spec."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            msg = f"RequirementSpec {spec_id} not found"
            raise ValueError(msg)

        spec.volatility_index = volatility_index
        spec.change_count = change_count
        spec.last_changed_at = datetime.now(UTC)

        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def verify(
        self,
        spec_id: str,
        verified_by: str,
        evidence: dict[str, Any],
    ) -> Any:
        """Mark a requirement as verified."""
        return await self.update(
            spec_id,
            verification_status=VerificationStatus.VERIFIED.value,
            verified_at=datetime.now(UTC),
            verified_by=verified_by,
            verification_evidence=evidence,
        )

    async def get_unverified_by_project(
        self,
        project_id: str,
        limit: int = 100,
    ) -> list[Any]:
        """Get unverified requirements for a project."""
        return await self.list_by_project(
            project_id,
            verification_status=VerificationStatus.UNVERIFIED.value,
            limit=limit,
        )

    async def get_high_risk_by_project(
        self,
        project_id: str,
        limit: int = 100,
    ) -> list[Any]:
        """Get high/critical risk requirements for a project."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import RequirementSpec

        query = (
            select(RequirementSpec)
            .join(Item, RequirementSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                RequirementSpec.deleted_at.is_(None),
                RequirementSpec.risk_level.in_([RiskLevel.CRITICAL.value, RiskLevel.HIGH.value]),
            )
            .order_by(
                RequirementSpec.risk_level,
                RequirementSpec.wsjf_score.desc().nullslast(),
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def calculate_wsjf(self, spec_id: str) -> float | None:
        """Calculate WSJF score for a requirement.

        WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size
        """
        spec = await self.get_by_id(spec_id)
        if not spec:
            return None

        if spec.business_value and spec.time_criticality and spec.risk_reduction:
            # Map complexity to job size estimate
            size_map = {"XS": 1, "S": 2, "M": 3, "L": 5, "XL": 8}
            job_size = size_map.get(spec.complexity_estimate, 3)

            wsjf: float = (spec.business_value + spec.time_criticality + spec.risk_reduction) / job_size
            spec.wsjf_score = wsjf
            await self.session.flush()
            return wsjf

        return None

    async def get_by_risk_level_and_status(
        self,
        project_id: str,
        risk_level: str,
        verification_status: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get requirements by risk level and verification status."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import RequirementSpec

        query = (
            select(RequirementSpec)
            .join(Item, RequirementSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                RequirementSpec.deleted_at.is_(None),
                RequirementSpec.risk_level == risk_level,
                RequirementSpec.verification_status == verification_status,
            )
            .order_by(RequirementSpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


# ==============================================================================
# TestSpecRepository
# ==============================================================================


class TestSpecRepository(BaseSpecRepository):
    """Repository for TestSpec CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TestSpec repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        from tracertm.models.item_spec import TestSpec

        super().__init__(session, TestSpec)

    async def create(
        self,
        item_id: str,
        test_type: str = TestType.UNIT.value,
        **kwargs: Any,
    ) -> Any:
        """Create a new test specification."""
        from tracertm.models.item_spec import TestSpec

        spec = TestSpec(
            id=str(uuid4()),
            item_id=item_id,
            test_type=test_type,
            **kwargs,
        )
        self.session.add(spec)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def list_by_project(
        self,
        project_id: str,
        test_type: str | None = None,
        is_quarantined: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """List test specs for a project with filters."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import TestSpec

        query = (
            select(TestSpec)
            .join(Item, TestSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                TestSpec.deleted_at.is_(None),
            )
        )

        if test_type:
            query = query.where(TestSpec.test_type == test_type)
        if is_quarantined is not None:
            query = query.where(TestSpec.is_quarantined == is_quarantined)

        query = query.order_by(TestSpec.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def record_run(
        self,
        spec_id: str,
        status: str,
        duration_ms: int,
        error_message: str | None = None,
        environment: str | None = None,
    ) -> Any:
        """Record a test run and update statistics."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            msg = f"TestSpec {spec_id} not found"
            raise ValueError(msg)

        # Update counts
        spec.total_runs = (spec.total_runs or 0) + 1
        if status == "passed":
            spec.pass_count = (spec.pass_count or 0) + 1
        elif status == "failed":
            spec.fail_count = (spec.fail_count or 0) + 1
        elif status == "skipped":
            spec.skip_count = (spec.skip_count or 0) + 1

        # Update last run info
        spec.last_run_at = datetime.now(UTC)
        spec.last_run_status = status
        spec.last_run_duration_ms = duration_ms
        spec.last_run_error = error_message

        # Add to run history (keep last 50)
        run_entry = {
            "run_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "status": status,
            "duration_ms": duration_ms,
            "error_message": error_message,
            "environment": environment,
        }
        # Create new list instead of mutating to trigger SQLAlchemy change detection
        spec.run_history = [run_entry, *(spec.run_history or [])[:49]]

        # Recalculate flakiness
        await self._recalculate_flakiness(spec)

        # Recalculate performance metrics
        await self._recalculate_performance(spec)

        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def _recalculate_flakiness(self, spec: Any) -> None:
        """Recalculate flakiness score based on recent runs."""
        history = spec.run_history or []
        window_size = getattr(spec, "flakiness_window_runs", _FAKINESS_WINDOW_DEFAULT)
        window = history[:window_size]

        if len(window) < _FAKINESS_MIN_RUNS:
            # Not enough data
            spec.flakiness_score = None
            return

        # Count status transitions
        transitions = 0
        for i in range(1, len(window)):
            if window[i]["status"] != window[i - 1]["status"]:
                transitions += 1

        spec.flakiness_score = transitions / (len(window) - 1)

        # Detect flaky patterns
        patterns = []
        if spec.flakiness_score > _FAKINESS_HIGH_THRESHOLD:
            patterns.append("high_transition_rate")
        spec.flaky_patterns = patterns

    async def _recalculate_performance(self, spec: Any) -> None:
        """Recalculate performance metrics."""
        history = spec.run_history or []
        durations = [r["duration_ms"] for r in history if r.get("duration_ms")]

        if not durations:
            return

        durations_sorted = sorted(durations)
        n = len(durations_sorted)

        spec.avg_duration_ms = sum(durations) / n
        spec.p50_duration_ms = durations_sorted[n // 2]
        spec.p95_duration_ms = durations_sorted[int(n * 0.95)] if n >= _PERFORMANCE_P95_MIN_SAMPLES else None
        spec.p99_duration_ms = durations_sorted[int(n * 0.99)] if n >= _PERFORMANCE_P99_MIN_SAMPLES else None

        # Determine trend
        if n >= _PERFORMANCE_TREND_MIN_SAMPLES:
            recent = durations[:_PERFORMANCE_RECENT_SAMPLES]
            older = durations[_PERFORMANCE_RECENT_SAMPLES : _PERFORMANCE_RECENT_SAMPLES + _PERFORMANCE_OLDER_SAMPLES]
            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)

            if recent_avg > older_avg * 1.1:
                spec.duration_trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                spec.duration_trend = "decreasing"
            else:
                spec.duration_trend = "stable"

    async def quarantine(
        self,
        spec_id: str,
        reason: str,
    ) -> Any:
        """Quarantine a flaky test."""
        return await self.update(
            spec_id,
            is_quarantined=True,
            quarantine_reason=reason,
            quarantined_at=datetime.now(UTC),
        )

    async def unquarantine(self, spec_id: str) -> Any:
        """Remove test from quarantine."""
        return await self.update(
            spec_id,
            is_quarantined=False,
            quarantine_reason=None,
            quarantined_at=None,
        )

    async def get_flaky_tests(
        self,
        project_id: str,
        threshold: float = 0.2,
        limit: int = 50,
    ) -> list[Any]:
        """Get flaky tests above threshold."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import TestSpec

        query = (
            select(TestSpec)
            .join(Item, TestSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                TestSpec.deleted_at.is_(None),
                TestSpec.flakiness_score >= threshold,
            )
            .order_by(TestSpec.flakiness_score.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_test_type_and_status(
        self,
        project_id: str,
        test_type: str,
        limit: int = 100,
    ) -> list[Any]:
        """Get tests by type."""
        return await self.list_by_project(
            project_id,
            test_type=test_type,
            limit=limit,
        )

    async def get_slowest_tests(
        self,
        project_id: str,
        limit: int = 20,
    ) -> list[Any]:
        """Get slowest tests by average duration."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import TestSpec

        query = (
            select(TestSpec)
            .join(Item, TestSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                TestSpec.deleted_at.is_(None),
                TestSpec.avg_duration_ms.isnot(None),
            )
            .order_by(TestSpec.avg_duration_ms.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


# ==============================================================================
# EpicSpecRepository
# ==============================================================================


class EpicSpecRepository(BaseSpecRepository):
    """Repository for EpicSpec CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize EpicSpec repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        from tracertm.models.item_spec import EpicSpec

        super().__init__(session, EpicSpec)

    async def create(
        self,
        item_id: str,
        epic_type: str = EpicType.FEATURE.value,
        **kwargs: Any,
    ) -> Any:
        """Create a new epic specification."""
        from tracertm.models.item_spec import EpicSpec

        spec = EpicSpec(
            id=str(uuid4()),
            item_id=item_id,
            epic_type=epic_type,
            **kwargs,
        )
        self.session.add(spec)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def list_by_project(
        self,
        project_id: str,
        epic_type: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """List epic specs for a project with filters."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import EpicSpec

        query = (
            select(EpicSpec)
            .join(Item, EpicSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                EpicSpec.deleted_at.is_(None),
            )
        )

        if epic_type:
            query = query.where(EpicSpec.epic_type == epic_type)
        if status:
            query = query.where(EpicSpec.status == status)

        query = query.order_by(EpicSpec.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_metrics(
        self,
        spec_id: str,
        user_story_count: int | None = None,
        completed_story_count: int | None = None,
        defect_count: int | None = None,
        progress_percentage: float | None = None,
    ) -> Any:
        """Update epic metrics."""
        updates: dict[str, int | float] = {}
        if user_story_count is not None:
            updates["user_story_count"] = user_story_count
        if completed_story_count is not None:
            updates["completed_story_count"] = completed_story_count
        if defect_count is not None:
            updates["defect_count"] = defect_count
        if progress_percentage is not None:
            updates["progress_percentage"] = progress_percentage

        return await self.update(spec_id, **updates)

    async def get_by_team(
        self,
        project_id: str,
        team_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get epics assigned to a team."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import EpicSpec

        query = (
            select(EpicSpec)
            .join(Item, EpicSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                EpicSpec.deleted_at.is_(None),
                EpicSpec.team_id == team_id,
            )
            .order_by(EpicSpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_in_progress(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get epics currently in progress."""
        return await self.list_by_project(
            project_id,
            status="in_progress",
            limit=limit,
        )


# ==============================================================================
# UserStorySpecRepository
# ==============================================================================


class UserStorySpecRepository(BaseSpecRepository):
    """Repository for UserStorySpec CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize UserStorySpec repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        from tracertm.models.item_spec import UserStorySpec

        super().__init__(session, UserStorySpec)

    async def create(
        self,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Create a new user story specification."""
        from tracertm.models.item_spec import UserStorySpec

        spec = UserStorySpec(
            id=str(uuid4()),
            item_id=item_id,
            **kwargs,
        )
        self.session.add(spec)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """List user story specs for a project with filters."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import UserStorySpec

        query = (
            select(UserStorySpec)
            .join(Item, UserStorySpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                UserStorySpec.deleted_at.is_(None),
            )
        )

        if status:
            query = query.where(UserStorySpec.status == status)

        query = query.order_by(UserStorySpec.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_acceptance_criteria(
        self,
        spec_id: str,
        acceptance_criteria: list[str],
    ) -> Any:
        """Update acceptance criteria for a user story."""
        return await self.update(
            spec_id,
            acceptance_criteria=acceptance_criteria,
        )

    async def get_by_epic(
        self,
        epic_item_id: str,
        limit: int = 100,
    ) -> list[Any]:
        """Get user stories for an epic."""
        from tracertm.models.item_spec import UserStorySpec

        query = (
            select(UserStorySpec)
            .where(
                UserStorySpec.epic_item_id == epic_item_id,
                UserStorySpec.deleted_at.is_(None),
            )
            .order_by(UserStorySpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_assignee(
        self,
        project_id: str,
        assignee_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get user stories assigned to a user."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import UserStorySpec

        query = (
            select(UserStorySpec)
            .join(Item, UserStorySpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                UserStorySpec.deleted_at.is_(None),
                UserStorySpec.assignee_id == assignee_id,
            )
            .order_by(UserStorySpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


# ==============================================================================
# TaskSpecRepository
# ==============================================================================


class TaskSpecRepository(BaseSpecRepository):
    """Repository for TaskSpec CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TaskSpec repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        from tracertm.models.item_spec import TaskSpec

        super().__init__(session, TaskSpec)

    async def create(
        self,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Create a new task specification."""
        from tracertm.models.item_spec import TaskSpec

        spec = TaskSpec(
            id=str(uuid4()),
            item_id=item_id,
            **kwargs,
        )
        self.session.add(spec)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """List task specs for a project with filters."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import TaskSpec

        query = (
            select(TaskSpec)
            .join(Item, TaskSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                TaskSpec.deleted_at.is_(None),
            )
        )

        if status:
            query = query.where(TaskSpec.status == status)

        query = query.order_by(TaskSpec.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_progress(
        self,
        spec_id: str,
        progress_percentage: float,
        completed_checklist_items: int | None = None,
    ) -> Any:
        """Update task progress."""
        updates = {
            "progress_percentage": progress_percentage,
        }
        if completed_checklist_items is not None:
            updates["completed_checklist_items"] = completed_checklist_items
        return await self.update(spec_id, **updates)

    async def get_by_parent_story(
        self,
        story_item_id: str,
        limit: int = 100,
    ) -> list[Any]:
        """Get tasks for a user story."""
        from tracertm.models.item_spec import TaskSpec

        query = (
            select(TaskSpec)
            .where(
                TaskSpec.parent_story_item_id == story_item_id,
                TaskSpec.deleted_at.is_(None),
            )
            .order_by(TaskSpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_blocked_tasks(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get blocked tasks."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import TaskSpec

        query = (
            select(TaskSpec)
            .join(Item, TaskSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                TaskSpec.deleted_at.is_(None),
                TaskSpec.is_blocked,
            )
            .order_by(TaskSpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_assignee(
        self,
        project_id: str,
        assignee_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get tasks assigned to a user."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import TaskSpec

        query = (
            select(TaskSpec)
            .join(Item, TaskSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                TaskSpec.deleted_at.is_(None),
                TaskSpec.assignee_id == assignee_id,
            )
            .order_by(TaskSpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


# ==============================================================================
# DefectSpecRepository
# ==============================================================================


class DefectSpecRepository(BaseSpecRepository):
    """Repository for DefectSpec CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize DefectSpec repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        from tracertm.models.item_spec import DefectSpec

        super().__init__(session, DefectSpec)

    async def create(
        self,
        item_id: str,
        severity: str = DefectSeverity.MAJOR.value,
        status: str = DefectStatus.NEW.value,
        **kwargs: Any,
    ) -> Any:
        """Create a new defect specification."""
        from tracertm.models.item_spec import DefectSpec

        spec = DefectSpec(
            id=str(uuid4()),
            item_id=item_id,
            severity=severity,
            status=status,
            **kwargs,
        )
        self.session.add(spec)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def list_by_project(
        self,
        project_id: str,
        severity: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """List defect specs for a project with filters."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import DefectSpec

        query = (
            select(DefectSpec)
            .join(Item, DefectSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                DefectSpec.deleted_at.is_(None),
            )
        )

        if severity:
            query = query.where(DefectSpec.severity == severity)
        if status:
            query = query.where(DefectSpec.status == status)

        query = query.order_by(DefectSpec.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_critical_defects(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get critical and blocker defects."""
        return await self.list_by_project(
            project_id,
            severity=DefectSeverity.CRITICAL.value,
            limit=limit,
        )

    async def get_blockers(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get blocker defects."""
        return await self.list_by_project(
            project_id,
            severity=DefectSeverity.BLOCKER.value,
            limit=limit,
        )

    async def get_by_status(
        self,
        project_id: str,
        status: str,
        limit: int = 100,
    ) -> list[Any]:
        """Get defects by status."""
        return await self.list_by_project(
            project_id,
            status=status,
            limit=limit,
        )

    async def assign_defect(
        self,
        spec_id: str,
        assigned_to: str,
    ) -> Any:
        """Assign a defect to a developer."""
        return await self.update(
            spec_id,
            assigned_to=assigned_to,
            status=DefectStatus.ASSIGNED.value,
            assigned_at=datetime.now(UTC),
        )

    async def resolve_defect(
        self,
        spec_id: str,
        resolution_type: str,
        resolution_notes: str,
        resolved_by: str,
    ) -> Any:
        """Mark a defect as resolved."""
        return await self.update(
            spec_id,
            status=DefectStatus.CLOSED.value,
            resolution_type=resolution_type,
            resolution_notes=resolution_notes,
            resolved_by=resolved_by,
            resolved_at=datetime.now(UTC),
        )

    async def reopen_defect(
        self,
        spec_id: str,
        reason: str,
    ) -> Any:
        """Reopen a closed defect."""
        return await self.update(
            spec_id,
            status=DefectStatus.REOPENED.value,
            reopen_reason=reason,
            reopened_at=datetime.now(UTC),
        )

    async def get_by_component(
        self,
        project_id: str,
        component: str,
        limit: int = 100,
    ) -> list[Any]:
        """Get defects for a component."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import DefectSpec

        query = (
            select(DefectSpec)
            .join(Item, DefectSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                DefectSpec.deleted_at.is_(None),
                DefectSpec.component == component,
            )
            .order_by(DefectSpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_assignee(
        self,
        project_id: str,
        assignee_id: str,
        limit: int = 50,
    ) -> list[Any]:
        """Get defects assigned to a user."""
        from tracertm.models.item import Item
        from tracertm.models.item_spec import DefectSpec

        query = (
            select(DefectSpec)
            .join(Item, DefectSpec.item_id == Item.id)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                DefectSpec.deleted_at.is_(None),
                DefectSpec.assigned_to == assignee_id,
            )
            .order_by(DefectSpec.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


# ==============================================================================
# Batch Repository for Cross-Type Operations
# ==============================================================================


class ItemSpecBatchRepository:
    """Repository for batch operations across all spec types."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.requirements = RequirementSpecRepository(session)
        self.tests = TestSpecRepository(session)
        self.epics = EpicSpecRepository(session)
        self.stories = UserStorySpecRepository(session)
        self.tasks = TaskSpecRepository(session)
        self.defects = DefectSpecRepository(session)

    async def get_all_specs_for_item(self, item_id: str) -> dict[str, Any]:
        """Get all spec types for an item."""
        return {
            "requirement": await self.requirements.get_by_item_id(item_id),
            "test": await self.tests.get_by_item_id(item_id),
            "epic": await self.epics.get_by_item_id(item_id),
            "story": await self.stories.get_by_item_id(item_id),
            "task": await self.tasks.get_by_item_id(item_id),
            "defect": await self.defects.get_by_item_id(item_id),
        }

    async def get_project_summary(self, project_id: str) -> dict[str, Any]:
        """Get summary counts for all spec types in a project."""
        return {
            "total_requirements": await self.requirements.get_active_count_by_project(project_id),
            "total_tests": await self.tests.get_active_count_by_project(project_id),
            "total_epics": await self.epics.get_active_count_by_project(project_id),
            "total_stories": await self.stories.get_active_count_by_project(project_id),
            "total_tasks": await self.tasks.get_active_count_by_project(project_id),
            "total_defects": await self.defects.get_active_count_by_project(project_id),
        }

    async def delete_all_specs_for_item(self, item_id: str) -> int:
        """Delete all specs for an item (cascade delete).

        Returns:
            Count of deleted specs
        """
        from tracertm.models.item_spec import (
            DefectSpec,
            EpicSpec,
            RequirementSpec,
            TaskSpec,
            TestSpec,
            UserStorySpec,
        )

        count = 0
        now = datetime.now(UTC)

        spec_classes: list[type[Any]] = [
            RequirementSpec,
            TestSpec,
            EpicSpec,
            UserStorySpec,
            TaskSpec,
            DefectSpec,
        ]
        for spec_class in spec_classes:
            query = select(spec_class).where(spec_class.item_id == item_id).where(spec_class.deleted_at.is_(None))
            result = await self.session.execute(query)
            specs = result.scalars().all()

            for spec in specs:
                spec.deleted_at = now
            count += len(specs)

        await self.session.flush()
        return count
