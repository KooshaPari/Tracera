"""Service for advanced analytics and reporting."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


class AdvancedAnalyticsService:
    """Service for advanced analytics and reporting."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.events = EventRepository(session)

    async def project_metrics(self, project_id: str) -> dict[str, Any]:
        """Get comprehensive project metrics."""
        items = await self.items.query(project_id, {})

        # Count by status
        status_counts: dict[str, int] = {}
        for item in items:
            status = str(getattr(item, "status", None) or "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count by view
        view_counts: dict[str, int] = {}
        for item in items:
            view = str(getattr(item, "view", None) or "unknown")
            view_counts[view] = view_counts.get(view, 0) + 1

        return {
            "project_id": project_id,
            "total_items": len(items),
            "by_status": status_counts,
            "by_view": view_counts,
            "completion_rate": self._calculate_completion_rate(status_counts),
        }

    def _calculate_completion_rate(self, status_counts: dict[str, int]) -> float:
        """Calculate project completion rate."""
        total = sum(status_counts.values())
        if total == 0:
            return 0.0

        completed = status_counts.get("done", 0) + status_counts.get("complete", 0)
        return (completed / total) * 100

    async def team_analytics(self, project_id: str) -> dict[str, Any]:
        """Get team analytics."""
        events = await self.events.get_by_project(project_id)

        # Count by agent
        agent_counts: dict[str, int] = {}
        for event in events:
            agent_id = str(getattr(event, "agent_id", None) or "unknown")
            agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1

        return {
            "project_id": project_id,
            "total_agents": len(agent_counts),
            "agent_activity": agent_counts,
            "total_events": len(events),
        }

    async def trend_analysis(
        self,
        project_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Analyze trends over time."""
        await self.items.query(project_id, {})
        events = await self.events.get_by_project(project_id)

        # Group events by day
        daily_events: dict[str, int] = {}
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        for event in events:
            created_at = getattr(event, "created_at", None)
            if isinstance(created_at, datetime) and created_at >= cutoff_date:
                date_key = created_at.date().isoformat()
                daily_events[date_key] = daily_events.get(date_key, 0) + 1

        return {
            "project_id": project_id,
            "days": days,
            "daily_events": daily_events,
            "total_events": len(events),
            "average_daily_events": len(events) / days if days > 0 else 0,
        }

    async def dependency_metrics(self, project_id: str) -> dict[str, Any]:
        """Get dependency metrics."""
        items = await self.items.query(project_id, {})

        # Calculate link statistics
        total_links = 0
        link_types: dict[str, int] = {}

        for item in items:
            outgoing = getattr(item, "outgoing_links", [])
            for link in outgoing:
                total_links += 1
                link_type = str(getattr(link, "link_type", None) or "unknown")
                link_types[link_type] = link_types.get(link_type, 0) + 1

        # Calculate average links per item
        avg_links = total_links / len(items) if items else 0

        return {
            "project_id": project_id,
            "total_links": total_links,
            "total_items": len(items),
            "average_links_per_item": avg_links,
            "link_types": link_types,
        }

    async def quality_metrics(self, project_id: str) -> dict[str, Any]:
        """Get quality metrics."""
        items = await self.items.query(project_id, {})

        # Calculate quality indicators
        items_with_description = 0
        items_with_links = 0

        for item in items:
            if hasattr(item, "description") and item.description:
                items_with_description += 1

            if len(getattr(item, "outgoing_links", [])) > 0:
                items_with_links += 1

        return {
            "project_id": project_id,
            "total_items": len(items),
            "items_with_description": items_with_description,
            "description_coverage": ((items_with_description / len(items) * 100) if items else 0),
            "items_with_links": items_with_links,
            "link_coverage": (items_with_links / len(items) * 100) if items else 0,
        }

    async def generate_report(self, project_id: str) -> dict[str, Any]:
        """Generate comprehensive project report."""
        metrics = await self.project_metrics(project_id)
        team = await self.team_analytics(project_id)
        trends = await self.trend_analysis(project_id)
        dependencies = await self.dependency_metrics(project_id)
        quality = await self.quality_metrics(project_id)

        return {
            "project_id": project_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "project_metrics": metrics,
            "team_analytics": team,
            "trend_analysis": trends,
            "dependency_metrics": dependencies,
            "quality_metrics": quality,
        }
