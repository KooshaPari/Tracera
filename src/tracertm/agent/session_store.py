"""Session → sandbox mapping for per-session chat persistence.

In-memory or DB-backed (PostgreSQL). Optional Redis cache for hot-path lookup.
When DB session is provided, can persist agent_sessions for restart survival and querying.
"""

import logging
from typing import Any

from tracertm.agent.sandbox.base import SandboxProvider
from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider
from tracertm.agent.types import SandboxConfig, SandboxMetadata

logger = logging.getLogger(__name__)

# Redis cache key and TTL for agent session lookup (reduces DB load)
AGENT_SESSION_CACHE_PREFIX = "tracertm:agent:session"
AGENT_SESSION_CACHE_TTL = 3600  # 1 hour


def _agent_session_cache_key(session_id: str) -> str:
    return f"{AGENT_SESSION_CACHE_PREFIX}:{session_id}"


class SessionSandboxStore:
    """Maps session_id to sandbox path. Uses SandboxProvider to create sandboxes."""

    def __init__(self, sandbox_provider: SandboxProvider | None = None):
        self._provider = sandbox_provider or LocalFilesystemSandboxProvider()
        self._store: dict[str, SandboxMetadata] = {}

    async def get_or_create(
        self,
        session_id: str,
        config: SandboxConfig | None = None,
        db_session: Any = None,
    ) -> tuple[str, bool]:
        """Return (sandbox root path, created). created=True if sandbox was just created."""
        if session_id in self._store:
            meta = self._store[session_id]
            if meta.sandbox_root:
                return meta.sandbox_root, False
        cfg = config or SandboxConfig()
        metadata = await self._provider.create_sandbox(cfg, session_id)
        self._store[session_id] = metadata
        if not metadata.sandbox_root:
            raise RuntimeError(f"Provider did not set sandbox_root for {session_id}")
        return metadata.sandbox_root, True

    def get(self, session_id: str) -> SandboxMetadata | None:
        """Return sandbox metadata if session exists."""
        return self._store.get(session_id)

    def delete(self, session_id: str) -> bool:
        """Remove session from store. Does not cleanup sandbox on disk."""
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False


class SessionSandboxStoreDB(SessionSandboxStore):
    """DB-backed session store: persists agent_sessions in PostgreSQL. Optional Redis cache for lookup."""

    def __init__(
        self,
        sandbox_provider: SandboxProvider | None = None,
        cache_service: Any = None,
    ):
        super().__init__(sandbox_provider)
        self._cache = cache_service

    async def get_or_create(
        self,
        session_id: str,
        config: SandboxConfig | None = None,
        db_session: Any = None,
    ) -> tuple[str, bool]:
        """Return (sandbox root path, created). Uses Redis cache then DB when available."""
        cache_key = _agent_session_cache_key(session_id)
        if self._cache is not None:
            try:
                cached = await self._cache.get(cache_key)
                if cached is not None and isinstance(cached, str):
                    return cached, False
            except Exception as e:
                logger.debug("Agent session cache get failed: %s", e)

        if db_session is not None:
            from sqlalchemy import select

            from tracertm.agent.types import SandboxStatus
            from tracertm.models.agent_session import AgentSession

            result = await db_session.execute(select(AgentSession).where(AgentSession.session_id == session_id))
            row = result.scalar_one_or_none()
            if row is not None:
                meta = SandboxMetadata(
                    sandbox_id=session_id,
                    status=SandboxStatus.READY,
                    created_at=row.created_at,
                    started_at=row.created_at,
                    sandbox_root=row.sandbox_root,
                )
                self._store[session_id] = meta
                if self._cache is not None:
                    try:
                        await self._cache.set(cache_key, row.sandbox_root, AGENT_SESSION_CACHE_TTL)
                    except Exception as e:
                        logger.debug("Agent session cache set failed: %s", e)
                return row.sandbox_root, False

        path, created = await super().get_or_create(session_id, config, db_session)
        if created and db_session is not None:
            import uuid

            from tracertm.models.agent_session import AgentSession

            raw_pid = getattr(config, "project_id", None) if config else None
            project_id = uuid.UUID(str(raw_pid)) if raw_pid else None
            rec = AgentSession(
                session_id=session_id,
                sandbox_root=path,
                project_id=project_id,
            )
            db_session.add(rec)
            await db_session.flush()
        if self._cache is not None:
            try:
                await self._cache.set(cache_key, path, AGENT_SESSION_CACHE_TTL)
            except Exception as e:
                logger.debug("Agent session cache set failed: %s", e)
        return path, created
