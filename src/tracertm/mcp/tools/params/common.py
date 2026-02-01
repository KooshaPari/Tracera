"""
Common utilities and helpers for parameterized MCP tools.

This module contains shared helper functions used across all domain-specific tool modules.
By extracting these, we avoid duplication and keep domain modules focused.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastmcp.exceptions import ToolError

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.storage.local_storage import LocalStorageManager
from tracertm.storage.sync_engine import SyncEngine
from tracertm.storage.conflict_resolver import ConflictStrategy as StorageConflictStrategy
from tracertm.api.client import TraceRTMClient
from tracertm.storage.file_watcher import TraceFileWatcher
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import tool modules (tolerate missing FastMCP deps in tests)
try:
    from tracertm.mcp.tools import core_tools as core
except Exception:  # pragma: no cover - test fallback
    async def _core_unavailable(*_args: Any, **_kwargs: Any):
        raise ToolError("MCP core tools are unavailable in this environment.")

    class _CoreStub:
        select_project = _core_unavailable
        query_items = _core_unavailable

    core = _CoreStub()  # type: ignore[assignment]

try:
    from tracertm.mcp.tools import specifications as spec_tools
except Exception:  # pragma: no cover - test fallback
    class _SpecStub:
        pass

    spec_tools = _SpecStub()  # type: ignore[assignment]

# Wire unified dispatch to core tool implementations.
project_tools = core
item_tools = core
link_tools = core
trace_tools = core
graph_tools = core


def _actor_from_context(ctx: Any | None) -> dict[str, Any] | None:
    """Extract actor information from FastMCP context."""
    if ctx is None:
        return None
    try:
        from fastmcp.server.dependencies import get_access_token
    except Exception:
        return None

    token = get_access_token()
    if token is None:
        return None

    claims = getattr(token, "claims", {}) or {}
    return {
        "client_id": getattr(token, "client_id", None),
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "auth_type": claims.get("auth_type"),
        "scopes": getattr(token, "scopes", None),
        "project_id": claims.get("project_id"),
        "project_ids": claims.get("project_ids"),
    }


def _wrap(result: Any, ctx: Any | None, action: str) -> dict[str, Any]:
    """Wrap tool result with metadata."""
    return {
        "ok": True,
        "action": action,
        "data": result,
        "actor": _actor_from_context(ctx),
    }


def _get_access_token_from_ctx() -> Any | None:
    """Get access token from FastMCP context."""
    try:
        from fastmcp.server.dependencies import get_access_token
    except Exception:
        return None
    return get_access_token()


def _resolve_project_id(payload: dict[str, Any], ctx: Any | None) -> str | None:
    """Resolve and validate project_id from payload and context."""
    project_id = payload.get("project_id")
    token = _get_access_token_from_ctx() if ctx else None
    if token is None:
        return project_id

    claims = getattr(token, "claims", {}) or {}
    allowed = []
    if claims.get("project_id"):
        allowed.append(claims["project_id"])
    project_ids = claims.get("project_ids")
    if isinstance(project_ids, str):
        allowed.extend([p.strip() for p in project_ids.split(",") if p.strip()])
    elif isinstance(project_ids, (list, tuple, set)):
        allowed.extend([str(p) for p in project_ids if p])

    if allowed:
        if project_id:
            if project_id not in allowed:
                raise ToolError("Project access denied for requested project_id.")
            return project_id
        if len(allowed) == 1:
            return allowed[0]
        raise ToolError("project_id required for this request.")

    return project_id


async def _maybe_select_project(payload: dict[str, Any], ctx: Any | None) -> None:
    """Auto-select project if project_id is available."""
    project_id = _resolve_project_id(payload, ctx)
    if project_id:
        payload["project_id"] = project_id
        try:
            await project_tools.select_project(project_id=project_id, ctx=ctx)
        except TypeError:
            await project_tools.select_project(project_id=project_id)


def _build_sync_engine() -> SyncEngine:
    """Build and configure sync engine instance."""
    config = ConfigManager()
    database_url = config.get("database_url")
    if not database_url:
        base_dir = Path.home() / ".tracertm"
        base_dir.mkdir(parents=True, exist_ok=True)
        database_url = f"sqlite:///{base_dir / 'tracertm.db'}"

    db_connection = DatabaseConnection(database_url)
    db_connection.connect()

    storage_manager = LocalStorageManager()
    strategy_name = config.get("sync_conflict_strategy") or "last_write_wins"
    conflict_strategy = StorageConflictStrategy[strategy_name.upper()]

    class _NoopApiClient:
        async def get_changes(self, **_kwargs: Any) -> list[dict[str, Any]]:
            return []

    try:
        api_client = TraceRTMClient()
    except Exception:
        api_client = _NoopApiClient()

    return SyncEngine(
        db_connection=db_connection,
        api_client=api_client,
        storage_manager=storage_manager,
        conflict_strategy=conflict_strategy,
    )


# Global watchers dictionary
_WATCHERS: dict[str, TraceFileWatcher] = {}


def _parse_since(value: str | None) -> datetime | None:
    """Parse relative time strings like '24h' or '7d' into datetime."""
    if not value:
        return None
    try:
        if value.endswith("h"):
            hours = int(value[:-1])
            return datetime.utcnow() - timedelta(hours=hours)
        if value.endswith("d"):
            days = int(value[:-1])
            return datetime.utcnow() - timedelta(days=days)
    except Exception:
        return None
    return None


async def _get_async_session() -> AsyncSession:
    """Create async database session."""
    config = ConfigManager()
    database_url = config.get("database_url")
    if not database_url:
        raise ToolError("Database URL not configured.")

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    session = async_session_maker()
    session._tracertm_engine = engine  # type: ignore[attr-defined]
    return session
