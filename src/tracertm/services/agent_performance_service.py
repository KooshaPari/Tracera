"""Service for agent performance analytics."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.event_repository import EventRepository


class AgentPerformanceService:
    """Service for analyzing agent performance."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = AgentRepository(session)
        self.events = EventRepository(session)

    async def get_agent_stats(
        self,
        agent_id: str,
        time_window_hours: int = 24,
    ) -> dict[str, Any]:
        """Get agent performance statistics."""
        agent = await self.agents.get_by_id(agent_id)
        if not agent:
            return {"error": "Agent not found"}

        # Get events for this agent
        events = await self.events.get_by_agent(agent_id)

        # Filter by time window
        cutoff_time = datetime.now(UTC) - timedelta(hours=time_window_hours)
        recent_events = [e for e in events if hasattr(e, "created_at") and e.created_at >= cutoff_time]

        # Calculate stats
        event_types = {}
        for event in recent_events:
            event_type = event.event_type if hasattr(event, "event_type") else "unknown"
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "agent_id": agent_id,
            "agent_name": agent.name if hasattr(agent, "name") else "Unknown",
            "total_events": len(recent_events),
            "event_types": event_types,
            "time_window_hours": time_window_hours,
            "events_per_hour": (len(recent_events) / time_window_hours if time_window_hours > 0 else 0),
        }

    async def get_team_performance(
        self,
        project_id: str,
    ) -> dict[str, Any]:
        """Get team performance metrics."""
        agents = await self.agents.get_by_project(project_id)

        team_stats = {
            "project_id": project_id,
            "total_agents": len(agents),
            "agents": [],
            "total_events": 0,
        }

        agents_list = team_stats.get("agents")
        if not isinstance(agents_list, list):
            agents_list = []
            team_stats["agents"] = agents_list
        for agent in agents:
            stats = await self.get_agent_stats(str(agent.id), time_window_hours=24)
            if "error" not in stats:
                agents_list.append(stats)
                team_stats["total_events"] += stats.get("total_events", 0)

        return team_stats

    async def get_agent_efficiency(
        self,
        agent_id: str,
    ) -> dict[str, Any]:
        """Calculate agent efficiency score."""
        stats = await self.get_agent_stats(agent_id, time_window_hours=24)

        if "error" in stats:
            return stats

        # Calculate efficiency (0-100)
        # Based on event frequency and diversity
        total_events = stats.get("total_events", 0)
        event_types_count = len(stats.get("event_types", {}))

        # Efficiency = (events * 10) + (event_types * 5), capped at 100
        efficiency = min(100, (total_events * 10) + (event_types_count * 5))

        return {
            "agent_id": agent_id,
            "efficiency_score": efficiency,
            "total_events": total_events,
            "event_type_diversity": event_types_count,
            "rating": self._get_efficiency_rating(efficiency),
        }

    def _get_efficiency_rating(self, score: float) -> str:
        """Get efficiency rating based on score."""
        if score >= 90:
            return "Excellent"
        if score >= 75:
            return "Good"
        if score >= 50:
            return "Fair"
        return "Poor"

    async def get_agent_workload(
        self,
        agent_id: str,
    ) -> dict[str, Any]:
        """Get agent workload metrics."""
        stats = await self.get_agent_stats(agent_id, time_window_hours=24)

        if "error" in stats:
            return stats

        events_per_hour = stats.get("events_per_hour", 0)

        # Classify workload
        if events_per_hour > 10:
            workload = "Heavy"
        elif events_per_hour > 5:
            workload = "Moderate"
        elif events_per_hour > 1:
            workload = "Light"
        else:
            workload = "Idle"

        return {
            "agent_id": agent_id,
            "workload": workload,
            "events_per_hour": events_per_hour,
            "total_events_24h": stats.get("total_events", 0),
        }

    async def recommend_agent_assignment(
        self,
        project_id: str,
        task_complexity: str = "medium",
    ) -> dict[str, Any]:
        """Recommend best agent for task assignment."""
        team_stats = await self.get_team_performance(project_id)

        if not team_stats["agents"]:
            return {"error": "No agents available"}

        # Find agent with lowest workload
        best_agent = None
        lowest_workload = float("inf")

        for agent_stats in team_stats["agents"]:
            workload = agent_stats.get("events_per_hour", 0)
            if workload < lowest_workload:
                lowest_workload = workload
                best_agent = agent_stats

        return {
            "recommended_agent_id": best_agent.get("agent_id") if best_agent else None,
            "agent_name": best_agent.get("agent_name") if best_agent else None,
            "current_workload": lowest_workload,
            "task_complexity": task_complexity,
            "reason": f"Agent has lowest workload ({lowest_workload:.2f} events/hour)",
        }
