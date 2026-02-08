"""Activity and metrics-related operations for the TraceRTM Python API client."""

from typing import Any

from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link


class ClientActivityMixin:
    """Mixin for TraceRTMClient to handle activity and metrics-related operations."""

    def get_agent_activity(self, agent_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Get agent activity history (FR45)."""
        session = self._ensure_sync_session()
        project_id = self._get_project_id()

        target_agent_id = agent_id or self.agent_id
        if not target_agent_id:
            return []

        events = (
            session
            .query(Event)
            .filter(
                Event.project_id == project_id,
                Event.agent_id == target_agent_id,
            )
            .order_by(Event.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "event_type": event.event_type,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "timestamp": event.created_at.isoformat() if event.created_at else None,
                "data": event.data,
            }
            for event in events
        ]

    def get_all_agents_activity(self, limit: int = 100) -> dict[str, list[dict[str, Any]]]:
        """Get activity for all agents in project (FR45)."""
        session = self._ensure_sync_session()
        project_id = self._get_project_id()

        agents = session.query(Agent).filter(Agent.project_id == project_id).all()

        result = {}
        for agent in agents:
            result[agent.id] = self.get_agent_activity(agent.id, limit)

        return result

    def get_api_metrics(self) -> dict[str, Any]:
        """Lightweight metrics helper used by tests."""
        session = self._ensure_sync_session()
        return {
            "items": session.query(Item).count(),
            "links": session.query(Link).count(),
            "agents": session.query(Agent).count(),
        }

    def get_api_version(self) -> str:
        """Return API version identifier (test helper)."""
        return "v1"

    def get_assigned_items(self, agent_id: str | None = None) -> list[dict[str, Any]]:
        """Get items assigned to an agent (Story 5.6, FR45)."""
        session = self._ensure_sync_session()
        project_id = self._get_project_id()

        target_agent_id = agent_id or self.agent_id
        if not target_agent_id:
            return []

        items = (
            session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.owner == target_agent_id,
                Item.deleted_at.is_(None),
            )
            .all()
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "status": item.status,
                "view": item.view,
                "type": item.item_type,
                "owner": item.owner,
            }
            for item in items
        ]
