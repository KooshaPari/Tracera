"""Common utilities and helpers for parameterized MCP tools.

This module contains shared helper functions used across all domain-specific tool modules.
By extracting these, we avoid duplication and keep domain modules focused.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Never, cast

from fastmcp.exceptions import ToolError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tracertm.api.client import TraceRTMClient
from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.storage.conflict_resolver import ConflictStrategy as StorageConflictStrategy
from tracertm.storage.local_storage import LocalStorageManager
from tracertm.storage.sync_engine import SyncEngine

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from tracertm.storage.file_watcher import TraceFileWatcher

# Import tool modules (tolerate missing FastMCP deps in tests)
try:
    from tracertm.mcp.tools import core_tools as core
except ImportError:

    async def _core_unavailable(*_args: object, **_kwargs: object) -> Never:
        await asyncio.sleep(0)
        msg = "MCP core tools are unavailable in this environment."
        raise ToolError(msg)

    class _CoreStub:
        select_project = _core_unavailable
        query_items = _core_unavailable

    core = _CoreStub()  # type: ignore[assignment]

try:
    from tracertm.mcp.tools import specifications as spec_tools
except ImportError:

    class _SpecStub:
        pass

    spec_tools = _SpecStub()  # type: ignore[assignment]

# Wire unified dispatch to core tool implementations.
project_tools = core
item_tools = core
link_tools = core
trace_tools = core
graph_tools = core


def _actor_from_context(ctx: object | None) -> dict[str, object] | None:
    """Extract actor information from FastMCP context."""
    if ctx is None:
        return None
    try:
        from fastmcp.server.dependencies import get_access_token
    except ImportError:
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


def _wrap(result: object, ctx: object | None, action: str) -> dict[str, object]:
    """Wrap tool result with metadata."""
    return {
        "ok": True,
        "action": action,
        "data": result,
        "actor": _actor_from_context(ctx),
    }


async def _call_tool(mod: object, tool_name: str, **kwargs: object) -> object:
    """Invoke a tool by name on a module (handles FunctionTool/callable from @mcp.tool())."""
    fn = getattr(mod, tool_name)
    return await cast("Callable[..., Awaitable[Any]]", fn)(**kwargs)


def _get_access_token_from_ctx() -> object | None:
    """Get access token from FastMCP context."""
    try:
        from fastmcp.server.dependencies import get_access_token
    except ImportError:
        return None
    return get_access_token()


def _collect_allowed_project_ids(claims: dict[str, object]) -> list[str]:
    """Collect project IDs from token claims."""
    allowed: list[str] = []
    if claims.get("project_id"):
        allowed.append(claims["project_id"])  # type: ignore[arg-type]
    project_ids = claims.get("project_ids")
    if isinstance(project_ids, str):
        allowed.extend([p.strip() for p in project_ids.split(",") if p.strip()])
    elif isinstance(project_ids, (list, tuple, set)):
        allowed.extend([str(p) for p in project_ids if p])
    return allowed


def _validate_project_id(project_id: str | None, allowed: list[str]) -> str | None:
    """Validate project_id against allowed list."""
    if not allowed:
        return project_id
    if project_id:
        if project_id not in allowed:
            msg = "Project access denied for requested project_id."
            raise ToolError(msg)
        return project_id
    if len(allowed) == 1:
        return allowed[0]
    msg = "project_id required for this request."
    raise ToolError(msg)


def _resolve_project_id(payload: dict[str, object], ctx: object | None) -> str | None:
    """Resolve and validate project_id from payload and context."""
    project_id_obj = payload.get("project_id")
    project_id = str(project_id_obj) if project_id_obj else None
    token = _get_access_token_from_ctx() if ctx else None
    if token is None:
        return project_id

    claims = getattr(token, "claims", {}) or {}
    allowed = _collect_allowed_project_ids(claims)
    return _validate_project_id(project_id, allowed)


async def _maybe_select_project(payload: dict[str, object], ctx: object | None) -> None:
    """Auto-select project if project_id is available."""
    project_id = _resolve_project_id(payload, ctx)
    if project_id:
        payload["project_id"] = project_id
        try:
            await _call_tool(project_tools, "select_project", project_id=project_id, ctx=ctx)
        except TypeError:
            await _call_tool(project_tools, "select_project", project_id=project_id)


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
        async def get_changes(self, **_kwargs: object) -> list[dict[str, object]]:
            return []

    try:
        api_client: TraceRTMClient | _NoopApiClient = TraceRTMClient()
    except (OSError, RuntimeError, ValueError):
        api_client = _NoopApiClient()

    # SyncEngine accepts TraceRTMClient; _NoopApiClient is duck-type compatible (get_changes).
    from tracertm.storage.sync_engine import SyncConfig

    return SyncEngine(
        db_connection=db_connection,
        api_client=cast("Any", api_client),
        storage_manager=storage_manager,
        config=SyncConfig(conflict_strategy=conflict_strategy),
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
            return datetime.now(UTC) - timedelta(hours=hours)
        if value.endswith("d"):
            days = int(value[:-1])
            return datetime.now(UTC) - timedelta(days=days)
    except (AttributeError, TypeError, ValueError, OverflowError):
        return None
    return None


async def _get_async_session() -> AsyncSession:
    """Create async database session."""
    await asyncio.sleep(0)
    config = ConfigManager()
    database_url = config.get("database_url")
    if not database_url:
        msg = "Database URL not configured."
        raise ToolError(msg)

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    session = async_session_maker()
    session._tracertm_engine = engine  # type: ignore[attr-defined]
    return session
