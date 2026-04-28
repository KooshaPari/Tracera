"""Performance optimization service for TraceRTM.

Functional Requirements: FR-INFRA-007
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.repositories.project_repository import ProjectRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

# Density thresholds for complexity classification
DENSITY_HIGH = 0.5
DENSITY_MEDIUM = 0.1
# Recommendation thresholds
ITEM_COUNT_ARCHIVE_THRESHOLD = 10000
LINK_COUNT_CACHE_THRESHOLD = 50000


class PerformanceService:
    """Service for performance analysis and optimization."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.projects = ProjectRepository(session)

    async def analyze_query_performance(
        self,
        project_id: str,
    ) -> dict[str, Any]:
        """Analyze query performance metrics."""
        # Count items
        items_result = await self.session.execute(
            select(func.count(Item.id)).where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            ),
        )
        item_count = items_result.scalar() or 0

        # Count links
        links_result = await self.session.execute(
            select(func.count(Link.id)).where(
                Link.project_id == project_id,
            ),
        )
        link_count = links_result.scalar() or 0

        # Calculate density
        density = link_count / max(item_count * (item_count - 1), 1)

        if density > DENSITY_HIGH:
            complexity = "high"
        elif density > DENSITY_MEDIUM:
            complexity = "medium"
        else:
            complexity = "low"

        return {
            "item_count": item_count,
            "link_count": link_count,
            "density": density,
            "complexity": complexity,
        }

    async def get_slow_queries(self) -> list[dict[str, Any]]:
        """Get information about slow queries."""
        # This would typically query database logs
        # For now, return empty list
        return []

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_enabled": True,
            "cache_size": 1000,
            "cache_ttl": 3600,
        }

    async def recommend_optimizations(
        self,
        project_id: str,
    ) -> list[str]:
        """Recommend optimizations based on analysis."""
        recommendations: list[dict[str, Any]] = []

        analysis = await self.analyze_query_performance(project_id)

        if analysis["item_count"] > ITEM_COUNT_ARCHIVE_THRESHOLD:
            recommendations.append("Consider archiving old items")  # type: ignore[arg-type]

        if analysis["density"] > DENSITY_HIGH:
            recommendations.append("High link density detected - consider refactoring structure")  # type: ignore[arg-type]

        if analysis["link_count"] > LINK_COUNT_CACHE_THRESHOLD:
            recommendations.append("Consider implementing link caching")  # type: ignore[arg-type]

        return recommendations  # type: ignore[return-value]

    async def get_project_statistics(
        self,
        project_id: str,
    ) -> dict[str, Any]:
        """Get comprehensive project statistics."""
        analysis = await self.analyze_query_performance(project_id)

        # Get view distribution
        views_result = await self.session.execute(
            select(Item.view, func.count(Item.id))
            .where(Item.project_id == project_id, Item.deleted_at.is_(None))
            .group_by(Item.view),
        )
        views = {row[0]: row[1] for row in views_result.all()}

        # Get status distribution
        status_result = await self.session.execute(
            select(Item.status, func.count(Item.id))
            .where(Item.project_id == project_id, Item.deleted_at.is_(None))
            .group_by(Item.status),
        )
        statuses = {row[0]: row[1] for row in status_result.all()}

        return {
            "item_count": analysis["item_count"],
            "link_count": analysis["link_count"],
            "density": analysis["density"],
            "complexity": analysis["complexity"],
            "views": views,
            "statuses": statuses,
        }
