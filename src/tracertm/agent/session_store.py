"""Session → sandbox mapping for per-session chat persistence.

In-memory or DB-backed (PostgreSQL). Optional Redis cache for hot-path lookup.
When DB session is provided, can persist agent_sessions for restart survival and querying.
"""

import logging

from tracertm.agent.sandbox.base import SandboxProvider
from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider
from tracertm.agent.types import SandboxConfig, SandboxMetadata

logger = logging.getLogger(__name__)

# Redis cache key and TTL for agent session lookup (reduces DB load)
AGENT_SESSION_CACHE_PREFIX = "tracertm:agent:session"
AGENT_SESSION_CACHE_TTL = 3600  # 1 hour
AGENT_SESSION_CACHE_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
    ConnectionError,
    TimeoutError,
)


def _agent_session_cache_key(session_id: str) -> str:
    return f"{AGENT_SESSION_CACHE_PREFIX}:{session_id}"


class SessionSandboxStore:
    """Maps session_id to sandbox path. Uses SandboxProvider to create sandboxes."""

    def __init__(self, sandbox_provider: SandboxProvider | None = None) -> None:
        """Initialize an in-memory session sandbox store.

        Args:
            sandbox_provider: Optional sandbox provider; defaults to local filesystem.
        """
        self._provider = sandbox_provider or LocalFilesystemSandboxProvider()
        self._store: dict[str, SandboxMetadata] = {}

    async def get_or_create(
        self,
        session_id: str,
        config: SandboxConfig | None = None,
        _db_session: object = None,
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
            msg = f"Provider did not set sandbox_root for {session_id}"
            raise RuntimeError(msg)
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


async def _get_cached_path_async(cache: object, cache_key: str) -> str | None:
    """Return cached sandbox path from async cache if present and valid."""
    if cache is None:
        return None
    try:
        cached = await cache.get(cache_key)  # type: ignore[attr-defined]
        if cached is not None and isinstance(cached, str):
            return str(cached)
    except AGENT_SESSION_CACHE_ERRORS as e:
        logger.debug("Agent session cache get failed: %s", e)
    return None


async def _set_cache_async(cache: object, cache_key: str, path: str) -> None:
    """Write path to cache; log and ignore errors."""
    if cache is None:
        return
    try:
        await cache.set(cache_key, path, AGENT_SESSION_CACHE_TTL)  # type: ignore[attr-defined]
    except AGENT_SESSION_CACHE_ERRORS as e:
        logger.debug("Agent session cache set failed: %s", e)


class SessionSandboxStoreDB(SessionSandboxStore):
    """DB-backed session store: persists agent_sessions in PostgreSQL. Optional Redis cache for lookup."""

    def __init__(
        self,
        sandbox_provider: SandboxProvider | None = None,
        cache_service: object = None,
    ) -> None:
        """Initialize a DB-backed session store.

        Args:
            sandbox_provider: Optional sandbox provider.
            cache_service: Optional async cache service for fast lookups.
        """
        super().__init__(sandbox_provider)
        self._cache = cache_service

    async def _load_from_db(self, db_session: object, session_id: str) -> tuple[str, SandboxMetadata] | None:
        """Load session from DB; return (sandbox_root, meta) or None."""
        from sqlalchemy import select

        from tracertm.agent.types import SandboxStatus
        from tracertm.models.agent_session import AgentSession

        result = await db_session.execute(  # type: ignore[attr-defined]
            select(AgentSession).where(AgentSession.session_id == session_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        meta = SandboxMetadata(
            sandbox_id=session_id,
            status=SandboxStatus.READY,
            created_at=row.created_at,
            started_at=row.created_at,
            sandbox_root=row.sandbox_root,
        )
        self._store[session_id] = meta
        return (row.sandbox_root, meta)

    async def _persist_created(
        self, db_session: object, session_id: str, path: str, config: SandboxConfig | None
    ) -> None:
        """Insert AgentSession row when sandbox was just created."""
        import uuid

        from tracertm.models.agent_session import AgentSession

        raw_pid = getattr(config, "project_id", None) if config else None
        project_id = uuid.UUID(str(raw_pid)) if raw_pid else None
        rec = AgentSession(
            session_id=session_id,
            sandbox_root=path,
            project_id=project_id,
        )
        db_session.add(  # type: ignore[attr-defined]
            rec
        )
        await db_session.flush()  # type: ignore[attr-defined]

    async def get_or_create(
        self,
        session_id: str,
        config: SandboxConfig | None = None,
        db_session: object = None,
    ) -> tuple[str, bool]:
        """Return (sandbox root path, created). Uses Redis cache then DB when available."""
        cache_key = _agent_session_cache_key(session_id)
        cached = await _get_cached_path_async(self._cache, cache_key)
        if cached is not None:
            return cached, False

        if db_session is not None:
            loaded = await self._load_from_db(db_session, session_id)
            if loaded is not None:
                path, _ = loaded
                await _set_cache_async(self._cache, cache_key, path)
                return path, False

        path, created = await super().get_or_create(session_id, config, db_session)
        if created and db_session is not None:
            await self._persist_created(db_session, session_id, path, config)
        await _set_cache_async(self._cache, cache_key, path)
        return path, created
