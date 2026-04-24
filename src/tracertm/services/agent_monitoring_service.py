"""Agent monitoring service for Epic 5 (Story 5.8).

Provides health checks, alerting, and monitoring capabilities.


Functional Requirements: FR-AI-003
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from tracertm.models.agent import Agent
from tracertm.models.event import Event

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

CONFLICT_RATE_ALERT_THRESHOLD = 10.0


class AgentMonitoringService:
    """Service for monitoring agent health and status (Story 5.8)."""

    def __init__(self, session: Session) -> None:
        """Initialize agent monitoring service."""
        self.session = session

    def check_agent_health(
        self,
        project_id: str,
        agent_id: str | None = None,
        stale_threshold_hours: float = 24.0,
    ) -> list[dict[str, Any]]:
        """Check health status of agents (Story 5.8).

        Args:
            project_id: Project ID
            agent_id: Optional specific agent ID
            stale_threshold_hours: Hours without activity to consider stale

        Returns:
            List of health status dictionaries
        """
        if agent_id:
            agent = self.session.query(Agent).filter(Agent.id == agent_id).first()
            if agent is None:
                return []
            agents = [agent]
        else:
            agents = self.session.query(Agent).filter(Agent.project_id == project_id).all()

        health_status = []

        for agent in agents:
            if agent is None:
                continue
            # Determine health
            if agent.last_activity_at:
                try:
                    last_activity = datetime.fromisoformat(agent.last_activity_at)
                    hours_since = (datetime.now(UTC) - last_activity.replace(tzinfo=None)).total_seconds() / 3600

                    if hours_since < 1:
                        health = "healthy"
                        health_status_code = "ok"
                    elif hours_since < stale_threshold_hours:
                        health = "idle"
                        health_status_code = "warning"
                    else:
                        health = "stale"
                        health_status_code = "error"
                except (ValueError, AttributeError):
                    health = "unknown"
                    health_status_code = "unknown"
                    hours_since = None
            else:
                health = "no_activity"
                health_status_code = "warning"
                hours_since = None

            health_status.append({
                "agent_id": agent.id,
                "agent_name": agent.name,
                "status": agent.status or "active",
                "health": health,
                "health_status": health_status_code,
                "last_activity": agent.last_activity_at,
                "hours_since_activity": round(hours_since, 2) if hours_since is not None else None,
            })

        return health_status

    def get_alerts(
        self,
        project_id: str,
        alert_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get alerts for agents (Story 5.8).

        Args:
            project_id: Project ID
            alert_types: Optional list of alert types to filter

        Returns:
            List of alert dictionaries
        """
        if alert_types is None:
            alert_types = ["stale", "high_conflict_rate", "error_rate"]

        alerts: list[dict[str, Any]] = []

        # Check for stale agents
        if "stale" in alert_types:
            health_status = self.check_agent_health(project_id)
            alerts.extend(
                {
                    "type": "stale_agent",
                    "severity": "warning",
                    "agent_id": status["agent_id"],
                    "agent_name": status["agent_name"],
                    "message": f"Agent {status['agent_name']} has been inactive for {status['hours_since_activity']} hours",
                }
                for status in health_status
                if status["health"] == "stale"
            )

        # Check for high conflict rates
        if "high_conflict_rate" in alert_types:
            from tracertm.services.agent_metrics_service import AgentMetricsService

            metrics_service = AgentMetricsService(self.session)
            since = datetime.now(UTC) - timedelta(hours=1)
            metrics = metrics_service.calculate_metrics(project_id, since=since)

            alerts.extend(
                {
                    "type": "high_conflict_rate",
                    "severity": "warning",
                    "agent_id": metric["agent_id"],
                    "agent_name": metric["agent_name"],
                    "message": f"Agent {metric['agent_name']} has {metric['conflict_rate']:.1f}% conflict rate",
                }
                for metric in metrics.get("metrics", [])
                if metric.get("conflict_rate", 0) > CONFLICT_RATE_ALERT_THRESHOLD
            )

        # Check for error rates
        if "error_rate" in alert_types:
            # Count error events
            since = datetime.now(UTC) - timedelta(hours=1)
            error_events = (
                self.session
                .query(Event)
                .filter(
                    Event.project_id == project_id,
                    Event.event_type == "error",
                    Event.created_at >= since,
                )
                .all()
            )

            if error_events:
                alerts.append({
                    "type": "error_rate",
                    "severity": "error",
                    "count": len(error_events),
                    "message": f"{len(error_events)} errors in the last hour",
                })

        return alerts
