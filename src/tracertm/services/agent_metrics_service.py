"""Agent metrics service for Epic 5 (Story 5.6, FR43).

Calculates and provides agent performance metrics.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.item import Item

# Decimal precision for rounding
_DECIMAL_PRECISION = 2


class AgentMetricsService:
    """Service for calculating agent performance metrics (Story 5.6, FR43)."""

    def __init__(self, session: Session) -> None:
        """Initialize agent metrics service."""
        self.session = session

    def calculate_metrics(
        self,
        project_id: str,
        agent_id: str | None = None,
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """Calculate metrics for agent(s) (Story 5.6, FR43).

        Args:
            project_id: Project ID
            agent_id: Optional specific agent ID
            since: Optional start date for metrics

        Returns:
            Metrics dictionary
        """
        if not since:
            since = datetime.now(UTC) - timedelta(hours=24)

        query = self.session.query(Event).filter(
            Event.project_id == project_id,
            Event.created_at >= since,
        )

        if agent_id:
            query = query.filter(Event.agent_id == agent_id)
            agents_to_analyze = [agent_id]
        else:
            # Get all agents in project
            agents = self.session.query(Agent).filter(Agent.project_id == project_id).all()
            agents_to_analyze = [agent.id for agent in agents]

        if not agents_to_analyze:
            return {"metrics": []}

        metrics_list = []

        for aid in agents_to_analyze:
            agent_events = query.filter(Event.agent_id == aid).all()

            if not agent_events:
                continue

            # Calculate metrics
            total_ops = len(agent_events)
            successful_ops = sum(1 for e in agent_events if e.event_type != "conflict_detected")
            conflicts = sum(1 for e in agent_events if e.event_type == "conflict_detected")

            # Time range in hours
            hours = (datetime.now(UTC) - since).total_seconds() / 3600
            ops_per_hour = total_ops / hours if hours > 0 else 0
            success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0
            conflict_rate = (conflicts / total_ops * 100) if total_ops > 0 else 0

            # Calculate average response time (if available in event data)
            response_times: list[float] = []
            for event in agent_events:
                if event.data and "response_time_ms" in event.data:
                    rt = event.data["response_time_ms"]
                    if isinstance(rt, (int, float)):
                        response_times.append(float(rt))

            avg_response_time = sum(response_times) / len(response_times) if response_times else None

            # Get agent name
            agent = self.session.query(Agent).filter(Agent.id == aid).first()
            agent_name = agent.name if agent else aid[:8]

            metrics_list.append({
                "agent_id": aid,
                "agent_name": agent_name,
                "total_operations": total_ops,
                "operations_per_hour": round(ops_per_hour, _DECIMAL_PRECISION),
                "success_rate": round(success_rate, _DECIMAL_PRECISION),
                "conflict_rate": round(conflict_rate, _DECIMAL_PRECISION),
                "conflicts": conflicts,
                "avg_response_time_ms": round(avg_response_time, _DECIMAL_PRECISION) if avg_response_time else None,
                "time_range_hours": round(hours, _DECIMAL_PRECISION),
            })

        return {"metrics": metrics_list, "since": since.isoformat()}

    def get_agent_workload(
        self,
        project_id: str,
        agent_id: str,
    ) -> dict[str, Any]:
        """Get workload for an agent (Story 5.6, FR45).

        Args:
            project_id: Project ID
            agent_id: Agent ID

        Returns:
            Workload dictionary
        """
        items = (
            self.session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.owner == agent_id,
                Item.deleted_at.is_(None),
            )
            .all()
        )

        status_counts: dict[str, int] = {}
        for item in items:
            status_counts[item.status] = status_counts.get(item.status, 0) + 1

        return {
            "agent_id": agent_id,
            "total_items": len(items),
            "by_status": status_counts,
        }
