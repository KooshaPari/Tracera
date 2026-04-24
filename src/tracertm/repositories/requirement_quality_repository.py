"""Repository for RequirementQuality CRUD operations."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.requirement_quality import RequirementQuality


class RequirementQualityRepository:
    """Repository for RequirementQuality CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        item_id: str,
        project_id: str,
        quality_scores: dict[str, float] | None = None,
        overall_quality_score: float = 0.5,
        quality_issues: list[dict[str, Any]] | None = None,
        change_propagation_index: float = 0.0,
        downstream_impact_count: int = 0,
        upstream_dependency_count: int = 0,
        impact_assessment: dict[str, Any] | None = None,
        volatility_index: float = 0.0,
        wsjf_score: float | None = None,
        wsjf_components: dict[str, float] | None = None,
        is_verified: bool = False,
        **_kwargs: object,
    ) -> RequirementQuality:
        """Create new requirement quality specification."""
        spec = RequirementQuality(
            id=str(uuid4()),
            item_id=item_id,
            project_id=project_id,
            quality_scores=quality_scores or {},
            overall_quality_score=overall_quality_score,
            quality_issues=quality_issues or [],
            change_propagation_index=change_propagation_index,
            downstream_impact_count=downstream_impact_count,
            upstream_dependency_count=upstream_dependency_count,
            impact_assessment=impact_assessment or {},
            volatility_index=volatility_index,
            wsjf_score=wsjf_score,
            wsjf_components=wsjf_components or {},
            is_verified=is_verified,
            last_analyzed_at=datetime.now(UTC),
        )
        self.session.add(spec)
        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def get_by_id(self, spec_id: str) -> RequirementQuality | None:
        """Get requirement quality spec by ID."""
        result = await self.session.execute(select(RequirementQuality).where(RequirementQuality.id == spec_id))
        return result.scalar_one_or_none()

    async def get_by_item_id(self, item_id: str) -> RequirementQuality | None:
        """Get requirement quality spec by item ID."""
        result = await self.session.execute(select(RequirementQuality).where(RequirementQuality.item_id == item_id))
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        descending: bool = True,
    ) -> list[RequirementQuality]:
        """List requirement quality specs for a project."""
        query = select(RequirementQuality).where(RequirementQuality.project_id == project_id)

        # Order by specified field
        order_field = getattr(RequirementQuality, order_by, RequirementQuality.created_at)
        query = query.order_by(order_field.desc()) if descending else query.order_by(order_field.asc())

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_quality_score(
        self,
        project_id: str,
        min_score: float = 0.0,
        max_score: float = 1.0,
        limit: int = 100,
    ) -> list[RequirementQuality]:
        """List specs within quality score range."""
        result = await self.session.execute(
            select(RequirementQuality)
            .where(
                RequirementQuality.project_id == project_id,
                RequirementQuality.overall_quality_score >= min_score,
                RequirementQuality.overall_quality_score <= max_score,
            )
            .order_by(RequirementQuality.overall_quality_score.asc())
            .limit(limit),
        )
        return list(result.scalars().all())

    async def list_high_volatility(
        self,
        project_id: str,
        threshold: float = 0.5,
        limit: int = 50,
    ) -> list[RequirementQuality]:
        """List specs with high volatility."""
        result = await self.session.execute(
            select(RequirementQuality)
            .where(
                RequirementQuality.project_id == project_id,
                RequirementQuality.volatility_index >= threshold,
            )
            .order_by(RequirementQuality.volatility_index.desc())
            .limit(limit),
        )
        return list(result.scalars().all())

    async def list_high_impact(
        self,
        project_id: str,
        threshold: float = 0.3,
        limit: int = 50,
    ) -> list[RequirementQuality]:
        """List specs with high change propagation index."""
        result = await self.session.execute(
            select(RequirementQuality)
            .where(
                RequirementQuality.project_id == project_id,
                RequirementQuality.change_propagation_index >= threshold,
            )
            .order_by(RequirementQuality.change_propagation_index.desc())
            .limit(limit),
        )
        return list(result.scalars().all())

    async def list_unverified(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[RequirementQuality]:
        """List unverified requirements."""
        result = await self.session.execute(
            select(RequirementQuality)
            .where(
                RequirementQuality.project_id == project_id,
                RequirementQuality.is_verified.is_(False),
            )
            .order_by(RequirementQuality.created_at.desc())
            .limit(limit),
        )
        return list(result.scalars().all())

    async def list_by_wsjf_priority(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[RequirementQuality]:
        """List specs ordered by WSJF score (highest priority first)."""
        result = await self.session.execute(
            select(RequirementQuality)
            .where(
                RequirementQuality.project_id == project_id,
                RequirementQuality.wsjf_score.isnot(None),
            )
            .order_by(RequirementQuality.wsjf_score.desc())
            .limit(limit),
        )
        return list(result.scalars().all())

    async def update(
        self,
        spec_id: str,
        quality_scores: dict[str, float] | None = None,
        overall_quality_score: float | None = None,
        quality_issues: list[dict[str, Any]] | None = None,
        change_propagation_index: float | None = None,
        downstream_impact_count: int | None = None,
        upstream_dependency_count: int | None = None,
        impact_assessment: dict[str, Any] | None = None,
        change_count: int | None = None,
        volatility_index: float | None = None,
        change_history: list[dict[str, Any]] | None = None,
        last_changed_at: datetime | None = None,
        wsjf_score: float | None = None,
        wsjf_components: dict[str, float] | None = None,
        is_verified: bool | None = None,
        verified_by: str | None = None,
        verified_at: datetime | None = None,
        verification_evidence: list[dict[str, Any]] | None = None,
        last_analyzed_at: datetime | None = None,
        **_kwargs: object,
    ) -> RequirementQuality:
        """Update requirement quality spec."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            msg = f"RequirementQuality {spec_id} not found"
            raise ValueError(msg)

        # Update fields conditionally
        if quality_scores is not None:
            spec.quality_scores = quality_scores
        if overall_quality_score is not None:
            spec.overall_quality_score = overall_quality_score
        if quality_issues is not None:
            spec.quality_issues = quality_issues
        if change_propagation_index is not None:
            spec.change_propagation_index = change_propagation_index
        if downstream_impact_count is not None:
            spec.downstream_impact_count = downstream_impact_count
        if upstream_dependency_count is not None:
            spec.upstream_dependency_count = upstream_dependency_count
        if impact_assessment is not None:
            spec.impact_assessment = impact_assessment
        if change_count is not None:
            spec.change_count = change_count
        if volatility_index is not None:
            spec.volatility_index = volatility_index
        if change_history is not None:
            spec.change_history = change_history
        if last_changed_at is not None:
            spec.last_changed_at = last_changed_at
        if wsjf_score is not None:
            spec.wsjf_score = wsjf_score
        if wsjf_components is not None:
            spec.wsjf_components = wsjf_components
        if is_verified is not None:
            spec.is_verified = is_verified
        if verified_by is not None:
            spec.verified_by = verified_by
        if verified_at is not None:
            spec.verified_at = verified_at
        if verification_evidence is not None:
            spec.verification_evidence = verification_evidence
        if last_analyzed_at is not None:
            spec.last_analyzed_at = last_analyzed_at

        spec.version = (spec.version or 1) + 1

        await self.session.flush()
        await self.session.refresh(spec)
        return spec

    async def delete(self, spec_id: str) -> bool:
        """Delete requirement quality spec."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            return False
        await self.session.delete(spec)
        await self.session.flush()
        return True

    async def delete_by_item_id(self, item_id: str) -> bool:
        """Delete requirement quality spec by item ID."""
        spec = await self.get_by_item_id(item_id)
        if not spec:
            return False
        return await self.delete(spec.id)

    async def count_by_project(self, project_id: str) -> int:
        """Count specs in a project."""
        result = await self.session.execute(
            select(func.count(RequirementQuality.id)).where(RequirementQuality.project_id == project_id),
        )
        return result.scalar() or 0

    async def get_stats(self, project_id: str) -> dict[str, Any]:
        """Get aggregate statistics for project."""
        result = await self.session.execute(
            select(
                func.count(RequirementQuality.id).label("total"),
                func.avg(RequirementQuality.overall_quality_score).label("avg_quality"),
                func.avg(RequirementQuality.volatility_index).label("avg_volatility"),
                func.avg(RequirementQuality.change_propagation_index).label("avg_cpi"),
                func.sum(func.cast(RequirementQuality.is_verified, Integer)).label("verified_count"),
            ).where(RequirementQuality.project_id == project_id),
        )

        row = result.one()
        total = row.total or 0
        verified = row.verified_count or 0

        return {
            "total_specs": total,
            "average_quality_score": float(row.avg_quality or 0),
            "average_volatility": float(row.avg_volatility or 0),
            "average_impact_index": float(row.avg_cpi or 0),
            "verified_count": verified,
            "verification_rate": (verified / total) if total > 0 else 0,
        }
