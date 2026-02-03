"""Neo4j-backed session graph for tracking session relationships and lineage."""

import logging
from datetime import UTC, datetime
from typing import Any

from tracertm.agent.events import AgentEventPublisher, SessionStatus
from tracertm.agent.session_store import SessionSandboxStoreDB
from tracertm.agent.types import SandboxConfig

logger = logging.getLogger(__name__)


class GraphSessionStore(SessionSandboxStoreDB):
    """Session store that writes to both PostgreSQL and Neo4j graph.

    In addition to PostgreSQL persistence, creates Neo4j nodes for:
    - Session nodes with metadata
    - Project relationships
    - Session lineage (forked from, merged with)
    - Tool call tracking
    - Publishes events to NATS for real-time updates
    """

    def __init__(
        self,
        sandbox_provider: Any = None,
        cache_service: Any = None,
        neo4j_client: Any = None,
        nats_client: Any = None,
    ):
        super().__init__(sandbox_provider, cache_service)
        self._neo4j = neo4j_client
        self._event_publisher = AgentEventPublisher(nats_client) if nats_client else None

    async def get_or_create(
        self,
        session_id: str,
        config: SandboxConfig | None = None,
        db_session: Any = None,
    ) -> tuple[str, bool]:
        """Create session in PostgreSQL and Neo4j graph."""
        # Create in PostgreSQL first
        sandbox_root, created = await super().get_or_create(session_id, config, db_session)

        # If newly created and Neo4j is available, create graph node
        if created and self._neo4j is not None:
            try:
                await self._create_session_node(session_id, sandbox_root, config)
            except Exception as e:
                logger.warning("Failed to create Neo4j session node: %s", e)

        return sandbox_root, created

    async def _create_session_node(
        self,
        session_id: str,
        sandbox_root: str,
        config: SandboxConfig | None = None,
    ):
        """Create Session node in Neo4j with relationships."""
        if self._neo4j is None:
            return

        project_id = getattr(config, "project_id", None) if config else None
        provider = getattr(config, "provider", "claude") if config else "claude"
        model = getattr(config, "model", None) if config else None

        # Cypher query to create session node and project relationship
        query = """
        // Create Session node
        CREATE (s:Session {
            session_id: $session_id,
            sandbox_root: $sandbox_root,
            provider: $provider,
            model: $model,
            status: 'ACTIVE',
            created_at: datetime($created_at),
            updated_at: datetime($created_at)
        })

        // Link to Project if exists
        WITH s
        OPTIONAL MATCH (p:Project {id: $project_id})
        FOREACH (ignored IN CASE WHEN p IS NOT NULL THEN [1] ELSE [] END |
            CREATE (s)-[:BELONGS_TO]->(p)
        )

        RETURN s.session_id as session_id
        """

        params = {
            "session_id": session_id,
            "sandbox_root": sandbox_root,
            "provider": provider,
            "model": model or "unknown",
            "project_id": str(project_id) if project_id else None,
            "created_at": datetime.now(UTC).isoformat(),
        }

        try:
            # Execute via Neo4j driver
            async with self._neo4j.driver.session() as session:
                result = await session.run(query, params)
                await result.consume()
                logger.info("Created Neo4j session node: %s", session_id)
        except Exception as e:
            logger.error("Neo4j session creation failed: %s", e)
            raise

    async def create_session_fork(
        self,
        new_session_id: str,
        parent_session_id: str,
        config: SandboxConfig | None = None,
        db_session: Any = None,
    ) -> tuple[str, bool]:
        """Create a new session forked from an existing session.

        Creates FORKED_FROM relationship in Neo4j graph.
        """
        # Create new session
        sandbox_root, created = await self.get_or_create(new_session_id, config, db_session)

        # Create fork relationship in Neo4j
        if created and self._neo4j is not None:
            try:
                await self._create_fork_relationship(new_session_id, parent_session_id)
            except Exception as e:
                logger.warning("Failed to create fork relationship: %s", e)

        return sandbox_root, created

    async def _create_fork_relationship(self, new_session_id: str, parent_session_id: str):
        """Create FORKED_FROM relationship between sessions."""
        if self._neo4j is None:
            return

        query = """
        MATCH (parent:Session {session_id: $parent_id})
        MATCH (child:Session {session_id: $child_id})
        CREATE (child)-[:FORKED_FROM {created_at: datetime($created_at)}]->(parent)
        RETURN child.session_id as child_id, parent.session_id as parent_id
        """

        params = {
            "parent_id": parent_session_id,
            "child_id": new_session_id,
            "created_at": datetime.now(UTC).isoformat(),
        }

        async with self._neo4j.driver.session() as session:
            result = await session.run(query, params)
            await result.consume()
            logger.info("Created fork relationship: %s -> %s", new_session_id, parent_session_id)

    async def track_tool_call(
        self,
        session_id: str,
        tool_name: str,
        input_data: dict,
        output_data: Any = None,
        success: bool = True,
        project_id: str | None = None,
    ):
        """Track tool execution in Neo4j graph and publish event."""
        # Publish tool use event
        if self._event_publisher:
            try:
                error_msg = None if success else str(output_data)
                await self._event_publisher.publish_chat_tool_use(
                    session_id=session_id,
                    project_id=project_id,
                    tool_name=tool_name,
                    tool_input=input_data,
                    tool_output=output_data if success else None,
                    success=success,
                    error=error_msg,
                )
            except Exception as e:
                logger.debug(f"Failed to publish tool use event: {e}")

        # Store in Neo4j
        if self._neo4j is None:
            return

        query = """
        MATCH (s:Session {session_id: $session_id})
        CREATE (s)-[:TOOL_CALL {
            tool_name: $tool_name,
            success: $success,
            timestamp: datetime($timestamp),
            input_summary: $input_summary,
            output_summary: $output_summary
        }]->(s)
        """

        # Summarize input/output to avoid storing huge data
        input_summary = str(input_data)[:500] if input_data else ""
        output_summary = str(output_data)[:500] if output_data else ""

        params = {
            "session_id": session_id,
            "tool_name": tool_name,
            "success": success,
            "timestamp": datetime.now(UTC).isoformat(),
            "input_summary": input_summary,
            "output_summary": output_summary,
        }

        try:
            async with self._neo4j.driver.session() as session:
                result = await session.run(query, params)
                await result.consume()
        except Exception as e:
            logger.debug("Tool call tracking failed: %s", e)

    async def get_session_lineage(self, session_id: str) -> list[dict]:
        """Get all parent sessions (FORKED_FROM chain)."""
        if self._neo4j is None:
            return []

        query = """
        MATCH path = (s:Session {session_id: $session_id})-[:FORKED_FROM*]->(ancestor:Session)
        RETURN [node in nodes(path) | {
            session_id: node.session_id,
            created_at: node.created_at,
            provider: node.provider,
            model: node.model
        }] as lineage
        ORDER BY length(path) DESC
        LIMIT 1
        """

        params = {"session_id": session_id}

        try:
            async with self._neo4j.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                if record:
                    return record["lineage"]
                return []
        except Exception as e:
            logger.error("Failed to get session lineage: %s", e)
            return []

    async def get_related_sessions(
        self,
        session_id: str,
        relationship_type: str | None = None,
    ) -> list[dict]:
        """Get sessions related via any relationship (or specific type)."""
        if self._neo4j is None:
            return []

        rel_pattern = f"[r:{relationship_type}]" if relationship_type else "[r]"

        query = f"""
        MATCH (s:Session {{session_id: $session_id}})-{rel_pattern}-(related:Session)
        RETURN DISTINCT {{
            session_id: related.session_id,
            relationship: type(r),
            created_at: related.created_at,
            provider: related.provider,
            model: related.model,
            status: related.status
        }} as related_session
        """

        params = {"session_id": session_id}

        try:
            async with self._neo4j.driver.session() as session:
                result = await session.run(query, params)
                records = await result.data()
                return [r["related_session"] for r in records]
        except Exception as e:
            logger.error("Failed to get related sessions: %s", e)
            return []

    async def update_session_status(
        self,
        session_id: str,
        status: str,
        old_status: str | None = None,
        project_id: str | None = None,
    ):
        """Update session status in Neo4j and publish event."""
        # Publish status change event
        if self._event_publisher and old_status:
            try:
                await self._event_publisher.publish_session_status_changed(
                    session_id=session_id,
                    project_id=project_id,
                    old_status=SessionStatus(old_status),
                    new_status=SessionStatus(status),
                )
            except Exception as e:
                logger.debug(f"Failed to publish status change event: {e}")

        # Update in Neo4j
        if self._neo4j is None:
            return

        query = """
        MATCH (s:Session {session_id: $session_id})
        SET s.status = $status,
            s.updated_at = datetime($updated_at)
        RETURN s.session_id as session_id
        """

        params = {
            "session_id": session_id,
            "status": status,
            "updated_at": datetime.now(UTC).isoformat(),
        }

        try:
            async with self._neo4j.driver.session() as session:
                result = await session.run(query, params)
                await result.consume()
        except Exception as e:
            logger.debug("Session status update failed: %s", e)

    async def delete_session(
        self,
        session_id: str,
        db_session: Any = None,
        project_id: str | None = None,
        reason: str | None = None,
    ):
        """Delete session from PostgreSQL and Neo4j, publish event."""
        # Publish destruction event
        if self._event_publisher:
            try:
                await self._event_publisher.publish_session_destroyed(
                    session_id=session_id,
                    project_id=project_id,
                    reason=reason or "Session deleted",
                )
            except Exception as e:
                logger.debug(f"Failed to publish session destruction event: {e}")

        # Delete from PostgreSQL
        if db_session is not None:
            from sqlalchemy import delete

            from tracertm.models.agent_session import AgentSession

            await db_session.execute(delete(AgentSession).where(AgentSession.session_id == session_id))
            await db_session.flush()

        # Delete from in-memory store
        self.delete(session_id)

        # Delete from Neo4j
        if self._neo4j is not None:
            try:
                await self._delete_session_node(session_id)
            except Exception as e:
                logger.warning("Failed to delete Neo4j session node: %s", e)

    async def _delete_session_node(self, session_id: str):
        """Delete Session node and all its relationships."""
        if self._neo4j is None:
            return
        neo4j = self._neo4j
        query = """
        MATCH (s:Session {session_id: $session_id})
        DETACH DELETE s
        """

        params = {"session_id": session_id}

        async with neo4j.driver.session() as session:
            result = await session.run(query, params)
            await result.consume()
            logger.info("Deleted Neo4j session node: %s", session_id)
