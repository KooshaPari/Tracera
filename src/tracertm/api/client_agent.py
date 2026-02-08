"""Agent-related operations for the TraceRTM Python API client."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import attributes

from tracertm.models.agent import Agent, generate_agent_uuid


class ClientAgentMixin:
    """Mixin for TraceRTMClient to handle agent-related operations."""

    def get_agent_info(self) -> Agent | None:
        """Return the Agent record for the current agent_id, if set."""
        if not self.agent_id:
            return None
        session = self._get_session()
        try:
            stmt = select(Agent).filter(Agent.id == self.agent_id)
            result = session.execute(stmt)
            agent = result.scalars().first() if hasattr(result, "scalars") else None
        except Exception:
            agent = None

        if agent is None:
            query_fn = getattr(session, "query", None)
            if callable(query_fn):
                try:
                    agent = query_fn(Agent).filter_by(id=self.agent_id).first()
                except Exception:
                    agent = None

        return agent

    def register_agent(
        self,
        name: str,
        capabilities: list[str] | None = None,
        config: dict[str, Any] | None = None,
        agent_type: str = "ai_agent",
        project_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register an agent (FR41, FR51)."""
        session = self._ensure_sync_session()
        capabilities = capabilities or []
        config = config or metadata or {}
        project_id = self.config_manager.get("current_project_id")

        existing = None
        if self.agent_id:
            existing = session.query(Agent).filter(Agent.id == self.agent_id).first()

        if existing:
            existing.name = name or existing.name
            existing.capabilities = list(capabilities) if capabilities else []
            existing.config = config or {}
            existing.agent_metadata = config or {}
            session.commit()
            return str(existing.id)

        agent_id = generate_agent_uuid()

        agent: Agent = Agent(
            id=agent_id,
            project_id=project_id,
            name=name,
            agent_type=agent_type,
            status="active",
            capabilities=capabilities,
            config=config,
            agent_metadata={**config, "assigned_projects": project_ids or []},
            last_activity_at=datetime.now(UTC).isoformat(),
        )
        session.add(agent)
        session.flush()
        session.commit()

        self.agent_id = agent.id or agent_id
        self.agent_name = name

        self._log_operation(
            "agent_registered",
            "agent",
            str(agent.id),
            {"name": name, "type": agent_type, "projects": project_ids or ([project_id] if project_id else [])},
        )

        return str(agent.id)

    def assign_agent_to_projects(self, agent_id: str, project_ids: list[str]) -> None:
        """Assign agent to multiple projects (FR51, FR52)."""
        session = self._ensure_sync_session()

        stmt = select(Agent).filter(Agent.id == agent_id)
        agent = None

        try:
            result = session.execute(stmt)
            if hasattr(result, "scalars"):
                agent = result.scalars().first()
        except Exception:
            agent = None

        if (not agent or not isinstance(agent, Agent)) and hasattr(session, "query"):
            try:
                agent = session.query(Agent).filter(Agent.id == agent_id).first()
            except Exception:
                agent = None

        if not agent:
            msg = f"Agent not found: {agent_id}"
            raise ValueError(msg)

        if agent.agent_metadata is None:
            agent.agent_metadata = {}
        agent.agent_metadata["assigned_projects"] = project_ids

        attributes.flag_modified(agent, "agent_metadata")
        session.commit()

        self._log_operation(
            "agent_assigned",
            "agent",
            agent_id,
            {"project_ids": project_ids},
        )

    def get_agent_projects(self, agent_id: str) -> list[str]:
        """Get projects assigned to an agent (FR52)."""
        session = self._ensure_sync_session()

        agent = session.query(Agent).filter(Agent.id == agent_id).first()

        if not agent:
            return []

        metadata = agent.agent_metadata or {}
        assigned_raw: Any = metadata.get("assigned_projects", [])
        assigned = list(assigned_raw) if assigned_raw else []
        primary = [agent.project_id] if agent.project_id else []
        combined: list[Any] = primary + assigned
        return [str(p) for p in list(set(combined)) if p]

    def get_agent_capabilities(self, agent_id: str | None = None) -> list[str]:
        """Return capabilities for the given agent (or current agent)."""
        session = self._ensure_sync_session()
        target_id = agent_id or self.agent_id
        if not target_id:
            return []
        agent = session.query(Agent).filter(Agent.id == target_id).first()
        if not agent:
            return []
        capabilities_raw: Any = agent.capabilities
        return list(capabilities_raw) if capabilities_raw else []
