"""Performance optimization service for TraceRTM."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.repositories.project_repository import ProjectRepository


class PerformanceService:
    """Service for performance analysis and optimization."""

    def __init__(self, session: AsyncSession):
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
            )
        )
        item_count = items_result.scalar() or 0

        # Count links
        links_result = await self.session.execute(
            select(func.count(Link.id)).where(
                Link.project_id == project_id,
            )
        )
        link_count = links_result.scalar() or 0

        # Calculate density
        density = link_count / max(item_count * (item_count - 1), 1)

        return {
            "item_count": item_count,
            "link_count": link_count,
            "density": density,
            "complexity": (
                "high" if density > 0.5 else "medium" if density > 0.1 else "low"
            ),
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
        recommendations = []

        analysis = await self.analyze_query_performance(project_id)

        if analysis["item_count"] > 10000:
            recommendations.append("Consider archiving old items")

        if analysis["density"] > 0.5:
            recommendations.append(
                "High link density detected - consider refactoring structure"
            )

        if analysis["link_count"] > 50000:
            recommendations.append("Consider implementing link caching")

        return recommendations

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
            .group_by(Item.view)
        )
        views = dict(views_result.all())

        # Get status distribution
        status_result = await self.session.execute(
            select(Item.status, func.count(Item.id))
            .where(Item.project_id == project_id, Item.deleted_at.is_(None))
            .group_by(Item.status)
        )
        statuses = dict(status_result.all())

        return {
            "item_count": analysis["item_count"],
            "link_count": analysis["link_count"],
            "density": analysis["density"],
            "complexity": analysis["complexity"],
            "views": views,
            "statuses": statuses,
        }
