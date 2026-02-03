"""Agent coordination service for TraceRTM."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.agent import Agent
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.event_repository import EventRepository

CONCURRENT_ACTIVITY_WINDOW_SECONDS = 60


@dataclass
class ConflictResolution:
    """Result of conflict resolution."""

    resolved: bool
    winner_agent_id: str
    loser_agent_id: str
    resolution_strategy: str
    timestamp: str


@dataclass
class AgentConflict:
    """Detected conflict between agents."""

    agent1_id: str
    agent2_id: str
    conflict_type: str
    entity_id: str
    description: str


class AgentCoordinationService:
    """Service for agent coordination and conflict resolution."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = AgentRepository(session)
        self.events = EventRepository(session)

    async def register_agent(
        self,
        project_id: str | uuid.UUID,
        name: str,
        agent_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> Agent:
        """Register a new agent."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        agent = await self.agents.create(
            project_id=pid,
            name=name,
            agent_type=agent_type,
            metadata=metadata,
        )

        # Log registration event
        await self.events.log(
            project_id=pid,
            event_type="agent_registered",
            entity_type="agent",
            entity_id=str(agent.id),
            data={"name": name, "type": agent_type},
            agent_id=str(agent.id),
        )

        return agent

    async def detect_conflicts(
        self,
        project_id: str,
    ) -> list[AgentConflict]:
        """Detect conflicts between agents."""
        # Get all active agents
        agents = await self.agents.get_by_project(project_id, status="active")

        conflicts = []

        # Check for agents working on same items
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i + 1 :]:
                # Check if both agents have recent activity on same entity
                # This is a simplified check
                if agent1.last_activity_at and agent2.last_activity_at:
                    # If both updated within 1 minute, potential conflict
                    time1 = datetime.fromisoformat(agent1.last_activity_at)
                    time2 = datetime.fromisoformat(agent2.last_activity_at)

                    if abs((time1 - time2).total_seconds()) < CONCURRENT_ACTIVITY_WINDOW_SECONDS:
                        conflicts.append(
                            AgentConflict(
                                agent1_id=str(agent1.id),
                                agent2_id=str(agent2.id),
                                conflict_type="concurrent_activity",
                                entity_id="unknown",
                                description=f"Agents {agent1.name} and {agent2.name} have concurrent activity",
                            )
                        )

        return conflicts

    async def resolve_conflict(
        self,
        project_id: str,
        conflict: AgentConflict,
        strategy: str = "last_write_wins",
    ) -> ConflictResolution:
        """Resolve a conflict between agents."""
        agent1 = await self.agents.get_by_id(conflict.agent1_id)
        agent2 = await self.agents.get_by_id(conflict.agent2_id)

        if not agent1 or not agent2:
            raise ValueError("One or both agents not found")

        # Apply resolution strategy
        if strategy == "last_write_wins":
            # Determine which agent wrote last
            time1 = datetime.fromisoformat(agent1.last_activity_at or "1970-01-01T00:00:00")
            time2 = datetime.fromisoformat(agent2.last_activity_at or "1970-01-01T00:00:00")

            if time1 > time2:
                winner_id = agent1.id
                loser_id = agent2.id
            else:
                winner_id = agent2.id
                loser_id = agent1.id

        elif strategy == "priority_based":
            # Use agent priority (could be based on type or metadata)
            winner_id = agent1.id
            loser_id = agent2.id

        else:
            raise ValueError(f"Unknown resolution strategy: {strategy}")

        # Log resolution
        await self.events.log(
            project_id=project_id,
            event_type="conflict_resolved",
            entity_type="conflict",
            entity_id=conflict.entity_id,
            data={
                "conflict_type": conflict.conflict_type,
                "winner": winner_id,
                "loser": loser_id,
                "strategy": strategy,
            },
        )

        return ConflictResolution(
            resolved=True,
            winner_agent_id=str(winner_id),
            loser_agent_id=str(loser_id),
            resolution_strategy=strategy,
            timestamp=datetime.now(UTC).isoformat(),
        )

    async def get_agent_activity(
        self,
        agent_id: str | uuid.UUID,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get activity history for an agent."""
        aid = str(agent_id) if isinstance(agent_id, uuid.UUID) else agent_id
        events = await self.events.get_by_agent(aid)

        return [
            {
                "event_type": e.event_type,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "timestamp": e.created_at,
                "data": e.data,
            }
            for e in events[:limit]
        ]
