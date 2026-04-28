"""Agent repository for TraceRTM."""

import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.agent import Agent


class AgentRepository:
    """Repository for Agent operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str | uuid.UUID,
        name: str,
        agent_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> Agent:
        """Create a new agent."""
        agent = Agent(
            id=str(uuid4()),
            project_id=project_id,
            name=name,
            agent_type=agent_type,
            status="active",
            agent_metadata=metadata or {},
        )
        self.session.add(agent)
        await self.session.flush()
        await self.session.refresh(agent)
        return agent

    async def get_by_id(self, agent_id: str | uuid.UUID) -> Agent | None:
        """Get agent by ID."""
        result = await self.session.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: str | uuid.UUID,
        status: str | None = None,
    ) -> list[Agent]:
        """Get all agents for a project."""
        query = select(Agent).where(Agent.project_id == project_id)
        if status:
            query = query.where(Agent.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status(
        self,
        agent_id: str | uuid.UUID,
        status: str,
    ) -> Agent:
        """Update agent status."""
        agent = await self.get_by_id(agent_id)
        if not agent:
            msg = f"Agent {agent_id} not found"
            raise ValueError(msg)
        agent.status = status
        await self.session.flush()
        await self.session.refresh(agent)
        return agent

    async def update_activity(self, agent_id: str | uuid.UUID) -> Agent:
        """Update agent last activity timestamp."""
        agent = await self.get_by_id(agent_id)
        if not agent:
            msg = f"Agent {agent_id} not found"
            raise ValueError(msg)
        agent.last_activity_at = datetime.now(UTC).isoformat()
        await self.session.flush()
        await self.session.refresh(agent)
        return agent

    async def delete(self, agent_id: str | uuid.UUID) -> bool:
        """Delete agent."""
        result = await self.session.execute(delete(Agent).where(Agent.id == agent_id))
        return getattr(result, "rowcount", 0) > 0
