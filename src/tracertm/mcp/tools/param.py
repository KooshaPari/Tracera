"""Parameterized MCP tools (atoms-style) for TraceRTM.

This module provides implementation functions only. Tool registration (@mcp.tool) is done
in tracertm.mcp.tools.params.* so each tool is registered once. Registering here would
cause "Component already exists" when server.py loads the params modules.
"""

from __future__ import annotations

import asyncio
import gzip
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Never, cast

# Define optional import errors early for exception handling
_OPTIONAL_IMPORT_ERRORS = (ImportError, RuntimeError, ValueError)


def _path_write_text(path_str: str, content: str, encoding: str = "utf-8") -> None:
    """Sync helper: write text to path (run via asyncio.to_thread)."""
    Path(path_str).write_text(content, encoding=encoding)


def _path_read_text(path_str: str, encoding: str = "utf-8") -> str:
    """Sync helper: read text from path (run via asyncio.to_thread)."""
    return Path(path_str).read_text(encoding=encoding)


def _path_exists(path_str: str) -> bool:
    """Sync helper: path exists (run via asyncio.to_thread)."""
    return Path(path_str).exists()


def _path_cwd() -> Path:
    """Sync helper: current working directory (run via asyncio.to_thread)."""
    return Path.cwd()


def _load_data_from_path(path: str) -> object:
    """Sync helper: load import data from file path (run via asyncio.to_thread)."""
    p = Path(path)
    if not p.exists():
        msg = f"File not found: {path}"
        raise ToolError(msg)
    if p.suffix.lower() in {".yaml", ".yml"}:
        result = yaml.safe_load(p.read_text(encoding="utf-8"))
        if result is None:
            msg = f"Failed to parse YAML file: {path}"
            raise ToolError(msg)
        return result
    return json.loads(p.read_text(encoding="utf-8"))


def _list_ingestable_paths(dir_path: str, *, recursive: bool) -> list[tuple[str, str]]:
    """Sync helper: list (path_str, suffix) for ingestable files (run via asyncio.to_thread)."""
    directory = Path(dir_path)
    if not directory.exists():
        msg = f"Directory not found: {dir_path}"
        raise ToolError(msg)
    patterns = {".md", ".mdx", ".yaml", ".yml"}
    files = directory.rglob("*") if recursive else directory.iterdir()
    return [(str(p), p.suffix.lower()) for p in files if p.is_file() and p.suffix.lower() in patterns]


def _backup_write(output_path_str: str, backup_data: dict[str, Any], *, compress: bool) -> None:
    """Sync helper: write backup to path (run via asyncio.to_thread)."""
    output_path = Path(output_path_str)
    if compress:
        with gzip.open(output_path, "wt", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, default=str)
    else:
        output_path.write_text(json.dumps(backup_data, indent=2, default=str), encoding="utf-8")


def _backup_read(path_str: str) -> dict[str, Any]:
    """Sync helper: read backup from path (run via asyncio.to_thread)."""
    backup_file = Path(path_str)
    if not backup_file.exists():
        msg = f"Backup file not found: {path_str}"
        raise ToolError(msg)
    if backup_file.suffix == ".gz":
        with gzip.open(backup_file, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(backup_file.read_text(encoding="utf-8"))


import yaml
from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except _OPTIONAL_IMPORT_ERRORS:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tracertm.api.client import TraceRTMClient
from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.services.progress_service import ProgressService
from tracertm.services.stateless_ingestion_service import StatelessIngestionService
from tracertm.storage.conflict_resolver import ConflictStrategy as StorageConflictStrategy
from tracertm.storage.file_watcher import TraceFileWatcher
from tracertm.storage.local_storage import LocalStorageManager
from tracertm.storage.sync_engine import SyncEngine

# Table names from sqlite_master or backup JSON; must be identifier-safe for S608
_TABLE_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# Agent health: hours since last activity for idle vs stale
HOURS_IDLE_THRESHOLD = 24


def _safe_table_name(name: str) -> str:
    if not _TABLE_NAME_RE.match(name):
        msg = f"Invalid table name: {name!r}"
        raise ToolError(msg)
    return name


# Import tool modules (tolerate missing FastMCP deps in tests)
try:
    from tracertm.mcp.tools import core_tools as core
except _OPTIONAL_IMPORT_ERRORS:

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
except _OPTIONAL_IMPORT_ERRORS:

    class _SpecStub:
        pass

    spec_tools = _SpecStub()  # type: ignore[assignment]

try:
    from tracertm.cli.commands import design as design_module
except _OPTIONAL_IMPORT_ERRORS:
    design_module = None  # type: ignore[assignment]

try:
    from tracertm.cli.commands.export import export_to_csv, export_to_json, export_to_markdown, export_to_yaml
except _OPTIONAL_IMPORT_ERRORS:
    export_to_csv = export_to_json = export_to_markdown = export_to_yaml = None

try:
    from tracertm.cli.commands.import_cmd import (
        _import_data,
        _import_github_data,
        _import_jira_data,
        _validate_github_format,
        _validate_import_data,
        _validate_jira_format,
    )
except _OPTIONAL_IMPORT_ERRORS:
    _import_data = _import_github_data = _import_jira_data = None
    _validate_github_format = _validate_import_data = _validate_jira_format = None

try:
    from tracertm.cli.commands.saved_queries import load_saved_queries, save_queries
except _OPTIONAL_IMPORT_ERRORS:
    load_saved_queries = save_queries = None
from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.services.benchmark_service import BenchmarkService
from tracertm.services.chaos_mode_service import ChaosModeService

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_TRACE_CLIENT_INIT_ERRORS = (OSError, RuntimeError, TypeError, ValueError)

# Wire unified dispatch to core tool implementations.
project_tools = core
item_tools = core
link_tools = core
trace_tools = core
graph_tools = core


def _actor_from_context(ctx: object | None) -> dict[str, Any] | None:
    if ctx is None:
        return None
    try:
        from fastmcp.server.dependencies import get_access_token
    except _OPTIONAL_IMPORT_ERRORS:
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


def _wrap(result: object, ctx: object | None, action: str) -> dict[str, Any]:
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
    try:
        from fastmcp.server.dependencies import get_access_token
    except _OPTIONAL_IMPORT_ERRORS:
        return None
    return get_access_token()


def _resolve_project_id(payload: dict[str, Any], ctx: object | None) -> str | None:
    project_id_obj = payload.get("project_id")
    project_id = str(project_id_obj) if project_id_obj else None
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
                msg = "Project access denied for requested project_id."
                raise ToolError(msg)
            return project_id
        if len(allowed) == 1:
            return allowed[0]
        msg = "project_id required for this request."
        raise ToolError(msg)

    return project_id


async def _maybe_select_project(payload: dict[str, Any], ctx: object | None) -> None:
    project_id = _resolve_project_id(payload, ctx)
    if project_id:
        payload["project_id"] = project_id
        try:
            await _call_tool(project_tools, "select_project", project_id=project_id, ctx=ctx)
        except TypeError:
            await _call_tool(project_tools, "select_project", project_id=project_id)


def _build_sync_engine() -> SyncEngine:
    config = ConfigManager()
    database_url_obj = config.get("database_url")
    database_url = str(database_url_obj) if database_url_obj else None
    if not database_url:
        base_dir = Path.home() / ".tracertm"
        base_dir.mkdir(parents=True, exist_ok=True)
        database_url = f"sqlite:///{base_dir / 'tracertm.db'}"

    db_connection = DatabaseConnection(database_url)
    db_connection.connect()

    storage_manager = LocalStorageManager()
    strategy_obj = config.get("sync_conflict_strategy")
    strategy_name = str(strategy_obj) if strategy_obj else "last_write_wins"
    conflict_strategy = StorageConflictStrategy[strategy_name.upper()]

    class _NoopApiClient:
        async def get_changes(self, **_kwargs: object) -> list[dict[str, Any]]:
            return []

    try:
        api_client: Any = TraceRTMClient()
    except _TRACE_CLIENT_INIT_ERRORS:
        api_client = _NoopApiClient()

    from tracertm.storage.sync_engine import SyncConfig

    return SyncEngine(
        db_connection=db_connection,
        api_client=api_client,
        storage_manager=storage_manager,
        config=SyncConfig(conflict_strategy=conflict_strategy),
    )


_WATCHERS: dict[str, TraceFileWatcher] = {}


def _parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("h"):
            hours = int(value[:-1])
            return datetime.now(UTC) - timedelta(hours=hours)
        if value.endswith("d"):
            days = int(value[:-1])
            return datetime.now(UTC) - timedelta(days=days)
    except (AttributeError, TypeError, ValueError):
        return None
    return None


async def _get_async_session() -> AsyncSession:
    await asyncio.sleep(0)
    config = ConfigManager()
    database_url_obj = config.get("database_url")
    if not database_url_obj:
        msg = "Database URL not configured."
        raise ToolError(msg)

    database_url = str(database_url_obj)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    session = async_session_maker()
    session._tracertm_engine = engine  # type: ignore[attr-defined]
    return session


async def project_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage projects via unified operations.

    Args:
        action: Action to perform (list, create, delete, select, etc.)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    payload = payload or {}
    action = action.lower()

    if action == "create":
        result = await _call_tool(
            project_tools,
            "create_project",
            name=(payload.get("name") or ""),
            description=payload.get("description"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "list":
        result = await _call_tool(project_tools, "list_projects", ctx=ctx)
        return _wrap(result, ctx, action)
    if action == "select":
        result = await _call_tool(
            project_tools,
            "select_project",
            project_id=payload.get("project_id"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "snapshot":
        result = await _call_tool(
            project_tools,
            "snapshot_project",
            project_id=payload.get("project_id"),
            label=payload.get("label"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)

    msg = f"Unknown project action: {action}"
    raise ToolError(msg)


async def item_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage items via unified operations.

    Args:
        action: Action to perform (list, create, update, delete, get, etc.)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    return await _item_manage_impl(action, payload, ctx)


async def _item_manage_impl(
    action: str,
    payload: dict[str, Any] | None,
    ctx: object | None,
) -> dict[str, Any]:
    payload = payload or {}
    action = action.lower()

    await _maybe_select_project(payload, ctx)

    if action == "create":
        result = await _call_tool(
            item_tools,
            "create_item",
            title=payload.get("title"),
            view=payload.get("view"),
            item_type=payload.get("item_type"),
            description=payload.get("description"),
            status=payload.get("status", "todo"),
            priority=payload.get("priority", "medium"),
            owner=payload.get("owner"),
            parent_id=payload.get("parent_id"),
            metadata=payload.get("metadata"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "get":
        result = await _call_tool(
            item_tools,
            "get_item",
            item_id=payload.get("item_id"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "update":
        result = await _call_tool(
            item_tools,
            "update_item",
            item_id=payload.get("item_id"),
            title=payload.get("title"),
            description=payload.get("description"),
            status=payload.get("status"),
            priority=payload.get("priority"),
            owner=payload.get("owner"),
            metadata=payload.get("metadata"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "delete":
        result = await _call_tool(
            item_tools,
            "delete_item",
            item_id=payload.get("item_id"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "query":
        result = await _call_tool(
            item_tools,
            "query_items",
            view=payload.get("view"),
            item_type=payload.get("item_type"),
            status=payload.get("status"),
            owner=payload.get("owner"),
            limit=payload.get("limit", 50),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "summarize_view":
        result = await _call_tool(
            item_tools,
            "summarize_view",
            view=payload.get("view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "bulk_update":
        result = await _call_tool(
            item_tools,
            "bulk_update_items",
            view=payload.get("view"),
            status=payload.get("status"),
            new_status=payload.get("new_status"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)

    msg = f"Unknown item action: {action}"
    raise ToolError(msg)


async def link_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage links via unified operations.

    Args:
        action: Action to perform (list, create, delete, etc.)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    payload = payload or {}
    action = action.lower()

    await _maybe_select_project(payload, ctx)

    if action == "create":
        result = await _call_tool(
            link_tools,
            "create_link",
            source_id=payload.get("source_id"),
            target_id=payload.get("target_id"),
            link_type=payload.get("link_type"),
            metadata=payload.get("metadata"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "list":
        result = await _call_tool(
            link_tools,
            "list_links",
            item_id=payload.get("item_id"),
            link_type=payload.get("link_type"),
            limit=payload.get("limit", 50),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "show":
        result = await _call_tool(
            link_tools,
            "show_links",
            item_id=payload.get("item_id"),
            view=payload.get("view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)

    msg = f"Unknown link action: {action}"
    raise ToolError(msg)


async def trace_analyze(
    kind: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Perform traceability analysis.

    Args:
        kind: Kind of analysis (matrix, coverage, impact, etc.)
        payload: Analysis-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    payload = payload or {}
    kind = kind.lower()

    await _maybe_select_project(payload, ctx)

    if kind == "gaps":
        result = await _call_tool(
            trace_tools,
            "find_gaps",
            from_view=payload.get("from_view"),
            to_view=payload.get("to_view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "trace_matrix":
        result = await _call_tool(
            trace_tools,
            "get_trace_matrix",
            source_view=payload.get("source_view"),
            target_view=payload.get("target_view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "impact":
        result = await _call_tool(
            trace_tools,
            "analyze_impact",
            item_id=payload.get("item_id"),
            max_depth=payload.get("max_depth", 5),
            link_types=payload.get("link_types"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "reverse_impact":
        result = await _call_tool(
            trace_tools,
            "analyze_reverse_impact",
            item_id=payload.get("item_id"),
            max_depth=payload.get("max_depth", 5),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "project_health":
        result = await _call_tool(trace_tools, "project_health", ctx=ctx)
        return _wrap(result, ctx, kind)

    msg = f"Unknown trace analysis kind: {kind}"
    raise ToolError(msg)


async def graph_analyze(
    kind: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Perform graph analysis.

    Args:
        kind: Kind of analysis (summary, path, cycles, etc.)
        payload: Analysis-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    payload = payload or {}
    kind = kind.lower()

    await _maybe_select_project(payload, ctx)

    if kind == "detect_cycles":
        result = await _call_tool(graph_tools, "detect_cycles", ctx=ctx)
        return _wrap(result, ctx, kind)
    if kind == "shortest_path":
        result = await _call_tool(
            graph_tools,
            "shortest_path",
            source_id=payload.get("source_id"),
            target_id=payload.get("target_id"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)

    msg = f"Unknown graph analysis kind: {kind}"
    raise ToolError(msg)


async def spec_manage(
    kind: str,
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage specifications via unified operations.

    Args:
        kind: Kind of specification (document, etc.)
        action: Action to perform (list, create, update, delete, etc.)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    payload = payload or {}
    kind = kind.lower()
    action = action.lower()

    await _maybe_select_project(payload, ctx)

    if kind == "adr":
        if action == "create":
            result = await _call_tool(
                spec_tools,
                "create_adr",
                project_id=payload.get("project_id"),
                title=payload.get("title"),
                context=payload.get("context"),
                decision=payload.get("decision"),
                consequences=payload.get("consequences"),
                status=payload.get("status", "proposed"),
                decision_drivers=payload.get("decision_drivers", []),
                tags=payload.get("tags", []),
            )
            return _wrap(result, ctx, f"{kind}.{action}")
        if action == "list":
            result = await _call_tool(
                spec_tools,
                "list_adrs",
                project_id=payload.get("project_id"),
                status=payload.get("status"),
            )
            return _wrap(result, ctx, f"{kind}.{action}")

    if kind == "contract" and action == "create":
        result = await _call_tool(
            spec_tools,
            "create_contract",
            project_id=payload.get("project_id"),
            item_id=payload.get("item_id"),
            title=payload.get("title"),
            contract_type=payload.get("contract_type"),
            status=payload.get("status", "draft"),
        )
        return _wrap(result, ctx, f"{kind}.{action}")

    if kind == "feature" and action == "create":
        result = await _call_tool(
            spec_tools,
            "create_feature",
            project_id=payload.get("project_id"),
            name=(payload.get("name") or ""),
            description=payload.get("description"),
            as_a=payload.get("as_a"),
            i_want=payload.get("i_want"),
            so_that=payload.get("so_that"),
        )
        return _wrap(result, ctx, f"{kind}.{action}")

    if kind == "scenario" and action == "create":
        result = await _call_tool(
            spec_tools,
            "create_scenario",
            feature_id=payload.get("feature_id"),
            title=payload.get("title"),
            gherkin_text=payload.get("gherkin_text"),
        )
        return _wrap(result, ctx, f"{kind}.{action}")

    msg = f"Unknown spec action: {kind}.{action}"
    raise ToolError(msg)


async def quality_analyze(
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Perform quality analysis on requirements.

    Args:
        payload: Analysis-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    payload = payload or {}
    result = await _call_tool(spec_tools, "analyze_quality", item_id=payload.get("item_id"))
    return _wrap(result, ctx, "quality.analyze")


async def config_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage configuration via unified operations.

    Args:
        action: Action to perform (list, set, get, etc.)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    return await _config_manage_impl(action, payload, ctx)


async def _config_manage_impl(
    action: str,
    payload: dict[str, Any] | None,
    ctx: object | None,
) -> dict[str, Any]:
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    config = ConfigManager()
    project_id_obj = payload.get("project_id")
    project_id = str(project_id_obj) if project_id_obj else None

    if action == "init":
        database_url_obj = payload.get("database_url")
        database_url = str(database_url_obj) if database_url_obj else None
        if not database_url:
            msg = "database_url is required for config init."
            raise ToolError(msg)
        result = config.init(database_url=database_url).model_dump()
        return _wrap(result, ctx, action)
    if action == "get":
        key = payload.get("key")
        if not key:
            msg = "key is required for config get."
            raise ToolError(msg)
        config_path = config.projects_dir / project_id / "config.yaml" if project_id else config.config_path
        if config_path.exists():
            with config_path.open() as handle:
                stored = yaml.safe_load(handle) or {}
            if key in stored:
                return _wrap({"key": key, "value": stored.get(key)}, ctx, action)
        value = config.get(key, project_id=project_id)
        return _wrap({"key": key, "value": value}, ctx, action)
    if action == "set":
        key = payload.get("key")
        if key is None:
            msg = "key is required for config set."
            raise ToolError(msg)
        value = payload.get("value")
        config.set(key, value, project_id=project_id)
        return _wrap({"key": key, "value": value}, ctx, action)
    if action == "unset":
        key = payload.get("key")
        if not key:
            msg = "key is required for config unset."
            raise ToolError(msg)
        config.set(key, None, project_id=project_id)
        return _wrap({"key": key}, ctx, action)
    if action == "list":
        result = config.get_config(project_id=project_id)
        return _wrap(result, ctx, action)

    msg = f"Unknown config action: {action}"
    raise ToolError(msg)


async def sync_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage synchronization via unified operations.

    Args:
        action: Action to perform (status, sync, pull, etc.)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    return await _sync_manage_impl(action, payload, ctx)


async def _sync_manage_impl(
    action: str,
    payload: dict[str, Any] | None,
    ctx: object | None,
) -> dict[str, Any]:
    payload = payload or {}
    action = action.lower()
    sync_engine = _build_sync_engine()

    if action == "status":
        state = sync_engine.get_status()
        return _wrap(
            {
                "status": state.status.value,
                "last_sync": state.last_sync.isoformat() if state.last_sync else None,
                "pending_changes": state.pending_changes,
                "conflicts_count": state.conflicts_count,
                "last_error": state.last_error,
            },
            ctx,
            action,
        )
    if action == "sync":
        force = bool(payload.get("force", False))
        result = await sync_engine.sync(_force=force)
        return _wrap(
            {
                "success": result.success,
                "entities_synced": result.entities_synced,
                "conflicts": result.conflicts,
                "errors": result.errors,
                "duration_seconds": result.duration_seconds,
            },
            ctx,
            action,
        )
    if action == "pull":
        result = await sync_engine.pull_changes()
        return _wrap(
            {
                "success": result.success,
                "entities_synced": result.entities_synced,
                "conflicts": result.conflicts,
                "errors": result.errors,
                "duration_seconds": result.duration_seconds,
            },
            ctx,
            action,
        )

    msg = f"Unknown sync action: {action}"
    raise ToolError(msg)


async def export_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage exports via unified operations.

    Args:
        action: Action to perform (json, yaml, csv, markdown)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    format_map = {
        "json": export_to_json,
        "yaml": export_to_yaml,
        "csv": export_to_csv,
        "markdown": export_to_markdown,
    }
    if action not in format_map:
        msg = "Unsupported export format. Use json|yaml|csv|markdown."
        raise ToolError(msg)

    config = ConfigManager()
    project_id_obj = payload.get("project_id")
    if project_id_obj:
        project_id = str(project_id_obj)
    elif config.get("current_project_id"):
        project_id = str(config.get("current_project_id"))
    else:
        project_id = None
    if not project_id:
        msg = "project_id is required for export."
        raise ToolError(msg)

    storage = LocalStorageManager()
    with storage.get_session() as session:
        content = format_map[action](session, project_id)

    output = payload.get("output")
    if output:
        await asyncio.to_thread(_path_write_text, output, content)
        return _wrap(
            {"format": action, "output": str(output), "bytes": len(content)},
            ctx,
            action,
        )

    return _wrap({"format": action, "content": content}, ctx, action)


async def import_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage imports via unified operations.

    Args:
        action: Action to perform (validate, json, yaml, jira, github)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    project_name = payload.get("project_name")

    def _load_data_no_path() -> object:
        data = payload.get("data")
        if isinstance(data, dict):
            return data
        content = payload.get("content")
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError as exc:
                result = yaml.safe_load(content)
                if result is None:
                    msg = "Failed to parse YAML content"
                    raise ToolError(msg) from exc
                return result
        msg = "Provide data, content, or path for import."
        raise ToolError(msg)

    path = payload.get("path")
    if path:
        data = await asyncio.to_thread(_load_data_from_path, path)
    else:
        data = _load_data_no_path()

    if action == "validate":
        errors = _validate_import_data(data)
        return _wrap({"errors": errors, "valid": len(errors) == 0}, ctx, action)

    if action == "json":
        errors = _validate_import_data(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        _import_data(data, project_name, "json")
        return _wrap({"imported": True, "source": "json"}, ctx, action)

    if action == "yaml":
        errors = _validate_import_data(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        _import_data(data, project_name, "yaml")
        return _wrap({"imported": True, "source": "yaml"}, ctx, action)

    if action == "jira":
        errors = _validate_jira_format(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        _import_jira_data(data, project_name)
        return _wrap({"imported": True, "source": "jira"}, ctx, action)

    if action == "github":
        errors = _validate_github_format(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        _import_github_data(data, project_name)
        return _wrap({"imported": True, "source": "github"}, ctx, action)

    msg = f"Unknown import action: {action}"
    raise ToolError(msg)


async def ingest_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage ingestion via unified operations.

    Args:
        action: Action to perform (markdown, mdx, yaml, directory)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    file_path = payload.get("path")
    if not file_path:
        msg = "path is required for ingestion."
        raise ToolError(msg)

    project_id_obj = payload.get("project_id")
    project_id = str(project_id_obj) if project_id_obj else None
    view = payload.get("view", "FEATURE")
    dry_run = bool(payload.get("dry_run", False))
    validate = bool(payload.get("validate", True))

    storage = LocalStorageManager()
    with storage.get_session() as session:
        service = StatelessIngestionService(session)
        if action in {"markdown", "md"}:
            result = service.ingest_markdown(file_path, project_id, view, dry_run, validate)
        elif action == "mdx":
            result = service.ingest_mdx(file_path, project_id, view, dry_run, validate)
        elif action in {"yaml", "yml"}:
            result = service.ingest_yaml(file_path, project_id, view, dry_run, validate)
        elif action == "directory":
            recursive = bool(payload.get("recursive", True))
            paths_suffixes = await asyncio.to_thread(_list_ingestable_paths, file_path, recursive=recursive)
            results = []
            for path_str, suffix in paths_suffixes:
                if suffix in {".md", ".markdown"}:
                    res = service.ingest_markdown(path_str, project_id, view, dry_run, validate)
                elif suffix == ".mdx":
                    res = service.ingest_mdx(path_str, project_id, view, dry_run, validate)
                else:
                    res = service.ingest_yaml(path_str, project_id, view, dry_run, validate)
                results.append({"path": path_str, "result": res})
            if not dry_run:
                session.commit()
            return _wrap({"count": len(results), "results": results}, ctx, action)
        else:
            msg = f"Unknown ingest action: {action}"
            raise ToolError(msg)

        if not dry_run:
            session.commit()

    return _wrap(result, ctx, action)


async def backup_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage backups via unified operations.

    Args:
        action: Action to perform (backup, restore)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()

    storage = LocalStorageManager()

    if action == "backup":
        project_id_obj = payload.get("project_id")
        project_id = str(project_id_obj) if project_id_obj else None
        output = payload.get("output")
        compress = bool(payload.get("compress", True))

        if not output:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            suffix = ".json.gz" if compress else ".json"
            output = f"tracertm_backup_{timestamp}{suffix}"

        backup_data: dict[str, Any] = {
            "version": "1.0",
            "timestamp": datetime.now(UTC).isoformat(),
            "project_id": project_id,
            "tables": {},
        }

        with storage.get_session() as session:
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            for table in tables:
                if table.startswith("alembic"):
                    continue
                safe_table = _safe_table_name(table)
                rows = session.execute(text(f"SELECT * FROM {safe_table}")).all()  # nosec B608
                records = [dict(row._mapping) for row in rows]
                for row in records:
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            row[key] = value.isoformat()
                backup_data["tables"][table] = records

        await asyncio.to_thread(_backup_write, output, backup_data, compress=compress)

        return _wrap({"output": str(output), "tables": len(backup_data["tables"])}, ctx, action)

    if action == "restore":
        path = payload.get("path")
        if not path:
            msg = "path is required for restore."
            raise ToolError(msg)
        backup_data = await asyncio.to_thread(_backup_read, path)

        if not isinstance(backup_data, dict) or "tables" not in backup_data:
            msg = "Invalid backup format."
            raise ToolError(msg)

        with storage.get_session() as session:
            for table, rows in backup_data["tables"].items():
                safe_name = _safe_table_name(table)
                session.execute(text(f"DELETE FROM {safe_name}"))  # nosec B608
                for row in rows:
                    columns = ", ".join(row)
                    placeholders = ", ".join([f":{k}" for k in row])
                    session.execute(
                        text(f"INSERT INTO {safe_name} ({columns}) VALUES ({placeholders})"),  # nosec B608
                        row,
                    )
            session.commit()

        return _wrap({"restored": True, "tables": len(backup_data["tables"])}, ctx, action)

    msg = f"Unknown backup action: {action}"
    raise ToolError(msg)


async def watch_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage file system watchers via unified operations.

    Args:
        action: Action to perform (start, stop, status)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()

    if action == "start":
        path_raw = payload.get("path")
        path = Path(path_raw) if path_raw else await asyncio.to_thread(_path_cwd)
        debounce = int(payload.get("debounce", 500))
        auto_sync = bool(payload.get("auto_sync", False))
        storage = LocalStorageManager()
        watcher = TraceFileWatcher(
            project_path=path,
            storage=storage,
            debounce_ms=debounce,
            auto_sync=auto_sync,
        )
        watcher.start()
        watch_id = payload.get("watch_id") or f"watch-{len(_WATCHERS) + 1}"
        _WATCHERS[watch_id] = watcher
        return _wrap({"watch_id": watch_id, "path": str(path)}, ctx, action)

    if action == "stop":
        watch_id = payload.get("watch_id")
        if not watch_id or watch_id not in _WATCHERS:
            msg = "watch_id not found."
            raise ToolError(msg)
        watcher = _WATCHERS.pop(watch_id)
        watcher.stop()
        return _wrap({"watch_id": watch_id, "stopped": True}, ctx, action)

    if action == "status":
        watch_id = payload.get("watch_id")
        if watch_id:
            watcher_or_none = _WATCHERS.get(watch_id)
            if not watcher_or_none:
                msg = "watch_id not found."
                raise ToolError(msg)
            return _wrap({"watch_id": watch_id, "stats": watcher_or_none.get_stats()}, ctx, action)
        return _wrap({k: v.get_stats() for k, v in _WATCHERS.items()}, ctx, action)

    msg = f"Unknown watch action: {action}"
    raise ToolError(msg)


async def db_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage database via unified operations.

    Args:
        action: Action to perform (init, status, migrate, reset, rollback)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    await asyncio.sleep(0)
    from tracertm.database.connection import DatabaseConnection

    payload = payload or {}
    action = action.lower()
    config = ConfigManager()

    if action == "init":
        database_url_obj = payload.get("database_url")
        database_url = str(database_url_obj) if database_url_obj else None
        if database_url:
            config.set("database_url", database_url)
        return _wrap({"database_url": config.get("database_url")}, ctx, action)

    database_url_obj = config.get("database_url")
    if not database_url_obj:
        msg = "Database URL not configured."
        raise ToolError(msg)

    db = DatabaseConnection(str(database_url_obj))
    db.connect()

    if action == "status":
        health = db.health_check()
        db.close()
        return _wrap(health, ctx, action)

    if action == "migrate":
        db.create_tables()
        health = db.health_check()
        db.close()
        return _wrap(health, ctx, action)

    if action in {"reset", "rollback"}:
        confirm = bool(payload.get("confirm", False))
        if not confirm:
            msg = "confirm=true is required for destructive operations."
            raise ToolError(msg)
        if action == "rollback":
            db.drop_tables()
        else:
            db.drop_tables()
            db.create_tables()
        db.close()
        return _wrap({"status": "ok", "action": action}, ctx, action)

    db.close()
    msg = f"Unknown db action: {action}"
    raise ToolError(msg)


async def agents_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage agents via unified operations.

    Args:
        action: Action to perform (list, activity, metrics, etc.)
        payload: Action-specific data
        ctx: MCP context

    Returns:
        Result dictionary
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    config = ConfigManager()
    project_id_obj = payload.get("project_id")
    if project_id_obj:
        project_id = str(project_id_obj)
    elif config.get("current_project_id"):
        project_id = str(config.get("current_project_id"))
    else:
        project_id = None
    if not project_id:
        msg = "project_id is required."
        raise ToolError(msg)

    storage = LocalStorageManager()
    with storage.get_session() as session:
        if action == "list":
            agents = session.query(Agent).filter(Agent.project_id == project_id).all()
            return _wrap(
                {
                    "agents": [
                        {
                            "id": str(agent.id),
                            "name": agent.name,
                            "type": agent.agent_type,
                            "status": agent.status,
                            "last_activity_at": agent.last_activity_at,
                        }
                        for agent in agents
                    ],
                },
                ctx,
                action,
            )

        if action == "activity":
            agent_id = payload.get("agent_id")
            since_date = _parse_since(payload.get("since"))
            limit = int(payload.get("limit", 50))

            query = session.query(Event).filter(Event.project_id == project_id)
            if agent_id:
                query = query.filter(Event.agent_id == agent_id)
            if since_date:
                query = query.filter(Event.created_at >= since_date)
            events = query.order_by(Event.created_at.desc()).limit(limit).all()

            return _wrap(
                {
                    "events": [
                        {
                            "id": str(event.id),
                            "agent_id": event.agent_id,
                            "event_type": event.event_type,
                            "entity_type": event.entity_type,
                            "entity_id": event.entity_id,
                            "created_at": event.created_at.isoformat() if event.created_at else None,
                            "data": event.data,
                        }
                        for event in events
                    ],
                },
                ctx,
                action,
            )

        if action == "metrics":
            agent_id = payload.get("agent_id")
            since_date = _parse_since(payload.get("since")) or datetime.now(UTC) - timedelta(hours=24)
            query = session.query(Event).filter(
                Event.project_id == project_id,
                Event.created_at >= since_date,
            )
            if agent_id:
                agent_ids = [agent_id]
            else:
                agent_ids = [a.id for a in session.query(Agent).filter(Agent.project_id == project_id).all()]

            metrics_list = []
            for aid in agent_ids:
                agent_events = query.filter(Event.agent_id == aid).all()
                if not agent_events:
                    continue
                total_ops = len(agent_events)
                successful_ops = sum(1 for e in agent_events if e.event_type != "conflict_detected")
                conflicts = sum(1 for e in agent_events if e.event_type == "conflict_detected")
                hours_float = (datetime.now(UTC) - since_date).total_seconds() / 3600
                ops_per_hour = total_ops / hours_float if hours_float > 0 else 0
                success_rate = (successful_ops / total_ops * 100) if total_ops else 0
                conflict_rate = (conflicts / total_ops * 100) if total_ops else 0
                agent = session.query(Agent).filter(Agent.id == aid).first()
                metrics_list.append({
                    "agent_id": str(aid),
                    "agent_name": agent.name if agent else str(aid)[:8],
                    "total_operations": total_ops,
                    "operations_per_hour": round(ops_per_hour, 2),
                    "success_rate": round(success_rate, 2),
                    "conflict_rate": round(conflict_rate, 2),
                    "conflicts": conflicts,
                })

            return _wrap({"metrics": metrics_list}, ctx, action)

        if action == "workload":
            agent_id = payload.get("agent_id")
            if agent_id:
                agent_result = session.query(Agent).filter(Agent.id == agent_id).first()
                agents = [agent_result] if agent_result else []
            else:
                agents = session.query(Agent).filter(Agent.project_id == project_id).all()
            workloads = []
            for agent in agents:
                items = (
                    session
                    .query(Item)
                    .filter(Item.project_id == project_id)
                    .filter(Item.owner == str(agent.id))  # type: ignore[comparison-overlap,arg-type]
                    .filter(Item.deleted_at.is_(None))
                    .all()
                )
                status_counts: dict[str, int] = {}
                for item in items:
                    status_counts[item.status] = status_counts.get(item.status, 0) + 1
                workloads.append({
                    "agent_id": str(agent.id),
                    "agent_name": agent.name,
                    "todo": status_counts.get("todo", 0),
                    "in_progress": status_counts.get("in_progress", 0),
                    "blocked": status_counts.get("blocked", 0),
                    "total": len(items),
                })
            return _wrap({"workloads": workloads}, ctx, action)

        if action == "health":
            agent_id = payload.get("agent_id")
            if agent_id:
                agent_result = session.query(Agent).filter(Agent.id == agent_id).first()
                agents = [agent_result] if agent_result else []
            else:
                agents = session.query(Agent).filter(Agent.project_id == project_id).all()
            healths = []
            for agent in agents:
                health = "unknown"
                if agent.last_activity_at:
                    try:
                        last_activity = datetime.fromisoformat(agent.last_activity_at)
                        hours_since = (datetime.now(UTC) - last_activity.replace(tzinfo=None)).total_seconds() / 3600
                        if hours_since < 1:
                            health = "healthy"
                        elif hours_since < HOURS_IDLE_THRESHOLD:
                            health = "idle"
                        else:
                            health = "stale"
                    except (TypeError, ValueError):
                        health = "unknown"
                else:
                    health = "no_activity"
                healths.append({
                    "agent_id": str(agent.id),
                    "agent_name": agent.name,
                    "status": agent.status or "active",
                    "last_activity_at": agent.last_activity_at,
                    "health": health,
                })
            return _wrap({"health": healths}, ctx, action)

    msg = f"Unknown agents action: {action}"
    raise ToolError(msg)


async def progress_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Progress manage."""
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    config = ConfigManager()
    project_id_obj = payload.get("project_id")
    if project_id_obj:
        project_id = str(project_id_obj)
    elif config.get("current_project_id"):
        project_id = str(config.get("current_project_id"))
    else:
        project_id = None
    if not project_id:
        msg = "project_id is required."
        raise ToolError(msg)

    storage = LocalStorageManager()
    with storage.get_session() as session:
        service = ProgressService(session)
        if action == "show":
            item_id = payload.get("item_id")
            view = payload.get("view")
            if item_id:
                item = session.query(Item).filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id).first()
                if not item:
                    msg = f"Item not found: {item_id}"
                    raise ToolError(msg)
                completion = service.calculate_completion(str(item.id))
                return _wrap(
                    {
                        "item_id": str(item.id),
                        "title": item.title,
                        "status": item.status,
                        "completion": completion,
                    },
                    ctx,
                    action,
                )
            if view:
                items = (
                    session
                    .query(Item)
                    .filter(
                        Item.project_id == project_id,
                        Item.view == view.upper(),
                        Item.deleted_at.is_(None),
                    )
                    .all()
                )
                avg_completion = (
                    sum(service.calculate_completion(str(item.id)) for item in items) / len(items) if items else 0
                )
                return _wrap(
                    {"view": view, "items": len(items), "average_completion": avg_completion},
                    ctx,
                    action,
                )
            items = session.query(Item).filter(Item.project_id == project_id, Item.deleted_at.is_(None)).all()
            avg_completion = (
                sum(service.calculate_completion(str(item.id)) for item in items) / len(items) if items else 0
            )
            return _wrap({"items": len(items), "average_completion": avg_completion}, ctx, action)

        if action == "blocked":
            limit = int(payload.get("limit", 50))
            blocked = service.get_blocked_items(project_id)
            return _wrap({"blocked": blocked[:limit]}, ctx, action)

        if action == "stalled":
            days = int(payload.get("days", 7))
            limit = int(payload.get("limit", 50))
            stalled = service.get_stalled_items(project_id, days)
            return _wrap({"stalled": stalled[:limit]}, ctx, action)

        if action == "velocity":
            days = int(payload.get("days", 7))
            velocity = service.calculate_velocity(project_id, days)
            return _wrap(velocity, ctx, action)

        if action == "report":
            days = int(payload.get("days", 30))
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=days)
            report = service.generate_progress_report(project_id, start_date, end_date)
            return _wrap(report, ctx, action)

    msg = f"Unknown progress action: {action}"
    raise ToolError(msg)


async def saved_queries_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Saved queries manage."""
    return await _saved_queries_manage_impl(action, payload, ctx)


async def _saved_queries_manage_impl(
    action: str,
    payload: dict[str, Any] | None,
    ctx: object | None,
) -> dict[str, Any]:
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()

    if action == "list":
        return _wrap({"queries": load_saved_queries()}, ctx, action)

    if action == "save":
        name = payload.get("name")
        if not name:
            msg = "name is required."
            raise ToolError(msg)
        queries = load_saved_queries()
        query_def = {
            "filter": payload.get("filter"),
            "view": payload.get("view"),
            "status": payload.get("status"),
            "query": payload.get("query"),
        }
        query_def = {k: v for k, v in query_def.items() if v is not None}
        queries[name] = query_def
        save_queries(queries)
        return _wrap({"saved": name, "query": query_def}, ctx, action)

    if action == "delete":
        name = payload.get("name")
        if not name:
            msg = "name is required."
            raise ToolError(msg)
        queries = load_saved_queries()
        if name in queries:
            del queries[name]
            save_queries(queries)
        return _wrap({"deleted": name}, ctx, action)

    if action == "get":
        name = payload.get("name")
        if not name:
            msg = "name is required."
            raise ToolError(msg)
        queries = load_saved_queries()
        return _wrap({"name": name, "query": queries.get(name)}, ctx, action)

    msg = f"Unknown saved-queries action: {action}"
    raise ToolError(msg)


async def test_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Manage."""
    return await _test_manage_impl(action, payload, ctx)


async def _test_manage_impl(
    action: str,
    payload: dict[str, Any] | None,
    ctx: object | None,
) -> dict[str, Any]:
    await asyncio.sleep(0)
    from tracertm.cli.commands.test.discovery import TestDiscovery
    from tracertm.cli.commands.test.runner import TestRunner

    payload = payload or {}
    action = action.lower()

    if action == "discover":
        scope = payload.get("scope", "all")
        language = payload.get("language")
        languages = [language] if language else None
        tests = TestDiscovery(Path.cwd()).discover(languages=languages, scope=scope)
        return _wrap(
            {
                "count": len(tests),
                "tests": [
                    {
                        "path": test.path,
                        "language": test.language,
                        "package": test.package,
                    }
                    for test in tests
                ],
            },
            ctx,
            action,
        )

    if action == "run":
        language = payload.get("language", "python")
        scope = payload.get("scope", "all")
        tests = TestDiscovery(Path.cwd()).discover(languages=[language], scope=scope)
        runner = TestRunner()
        results = [runner.run_test(test) for test in tests]
        return _wrap(
            {
                "results": [
                    {
                        "path": result.test_file.path,
                        "language": result.test_file.language,
                        "passed": result.passed,
                        "duration_ms": result.duration_ms,
                        "output": result.output,
                    }
                    for result in results
                ],
            },
            ctx,
            action,
        )

    msg = f"Unknown test action: {action}"
    raise ToolError(msg)


async def tui_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Tui manage."""
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()

    if action == "list":
        return _wrap(
            {
                "apps": [
                    {"name": "dashboard", "command": "rtm tui dashboard"},
                    {"name": "browser", "command": "rtm tui browser"},
                    {"name": "graph", "command": "rtm tui graph"},
                ],
            },
            ctx,
            action,
        )

    if action == "launch":
        app_name = payload.get("app", "dashboard")
        watch = bool(payload.get("watch", False))
        project_path = payload.get("path")
        spawn = bool(payload.get("spawn", False))

        cmd = ["rtm", "tui", app_name]
        if watch:
            cmd.append("--watch")
        if project_path:
            cmd.extend(["--path", project_path])

        if not spawn:
            return _wrap({"command": " ".join(cmd), "spawned": False}, ctx, action)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=Path.cwd(),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        return _wrap({"command": " ".join(cmd), "spawned": True, "pid": proc.pid}, ctx, action)

    msg = f"Unknown tui action: {action}"
    raise ToolError(msg)


async def benchmark_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Benchmark manage."""
    payload = payload or {}
    action = action.lower()
    session = await _get_async_session()
    engine = getattr(session, "_tracertm_engine", None)
    try:
        service = BenchmarkService(session)
        if action == "views":
            results = await service.benchmark_all_views()
            data = [
                {
                    "view_name": r.view_name,
                    "query_time_ms": r.query_time_ms,
                    "target_ms": r.target_ms,
                    "meets_target": r.meets_target,
                    "row_count": r.row_count,
                    "size_bytes": r.size_bytes,
                }
                for r in results
            ]
            return _wrap({"views": data}, ctx, action)
        if action == "refresh":
            incremental = await service.benchmark_refresh_incremental()
            full = await service.benchmark_refresh_full()
            return _wrap(
                {
                    "incremental": {
                        "duration_ms": incremental.duration_ms,
                        "metadata": incremental.metadata,
                    },
                    "full": {
                        "duration_ms": full.duration_ms,
                        "metadata": full.metadata,
                    },
                },
                ctx,
                action,
            )
        if action == "report":
            report = await service.get_performance_report()
            return _wrap(report, ctx, action)
    finally:
        await session.close()
        if engine is not None:
            await engine.dispose()

    msg = f"Unknown benchmark action: {action}"
    raise ToolError(msg)


async def chaos_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Chaos manage."""
    payload = payload or {}
    action = action.lower()
    project_id_obj = payload.get("project_id")
    project_id = (
        str(project_id_obj)
        if project_id_obj
        else str(ConfigManager().get("current_project_id"))
        if ConfigManager().get("current_project_id")
        else None
    )
    if action in {"explode", "crash", "zombies", "snapshot"} and not project_id:
        msg = "project_id is required."
        raise ToolError(msg)

    session = await _get_async_session()
    engine = getattr(session, "_tracertm_engine", None)
    try:
        service = ChaosModeService(session)
        # Narrow type for actions that require project_id
        pid: str = project_id if isinstance(project_id, str) else str(project_id or "")

        if action == "explode":
            file_path = payload.get("path")
            view = payload.get("view", "FEATURE")
            if not file_path:
                msg = "path is required for explode."
                raise ToolError(msg)
            content = await asyncio.to_thread(_path_read_text, file_path, "utf-8")
            items_created = await service.explode_file(content, pid, view)
            await session.commit()
            return _wrap({"items_created": items_created}, ctx, action)

        if action == "crash":
            reason = payload.get("reason")
            if not reason:
                msg = "reason is required for crash."
                raise ToolError(msg)
            item_ids = payload.get("item_ids") or []
            result = await service.track_scope_crash(pid, str(reason), item_ids)
            await session.commit()
            return _wrap(result, ctx, action)

        if action == "zombies":
            days_inactive = int(payload.get("days_inactive", 30))
            cleanup = bool(payload.get("cleanup", False))
            result = await service.detect_zombies(pid, days_inactive)
            if cleanup:
                deleted = await service.cleanup_zombies(pid, days_inactive)
                result["deleted"] = deleted
                await session.commit()
            return _wrap(result, ctx, action)

        if action == "snapshot":
            name = payload.get("name")
            description = payload.get("description")
            if not name:
                msg = "name is required for snapshot."
                raise ToolError(msg)
            result = await service.create_snapshot(pid, str(name), description)
            await session.commit()
            return _wrap(result, ctx, action)

        if action == "enable":
            return _wrap({"enabled": True}, ctx, action)
        if action == "disable":
            return _wrap({"enabled": False}, ctx, action)
    finally:
        await session.close()
        if engine is not None:
            await engine.dispose()

    msg = f"Unknown chaos action: {action}"
    raise ToolError(msg)


async def design_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: object | None = None,
) -> dict[str, Any]:
    """Design manage."""
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    path = payload.get("path")

    trace_dir = design_module._get_trace_dir(path)

    if action == "init":
        figma_key = payload.get("figma_key", "")
        figma_token = payload.get("figma_token", "")
        designs_config = dict[str, Any](design_module.DESIGNS_YAML_TEMPLATE)
        figma_config = designs_config.get("figma")
        if isinstance(figma_config, dict):
            figma_config["file_key"] = figma_key
            figma_config["access_token"] = figma_token
        design_module._save_designs_config(trace_dir, designs_config)

        components_config = dict[str, Any](design_module.COMPONENTS_YAML_TEMPLATE)
        metadata = components_config.get("metadata")
        if isinstance(metadata, dict):
            metadata["created_at"] = datetime.now(UTC).isoformat()
        design_module._save_components_config(trace_dir, components_config)
        return _wrap({"initialized": True}, ctx, action)

    if action == "link":
        component = payload.get("component")
        figma_url = payload.get("figma_url")
        component_path = payload.get("component_path")
        if not component or not figma_url:
            msg = "component and figma_url are required."
            raise ToolError(msg)
        file_key, node_id = design_module._validate_figma_url(figma_url)
        designs_config = design_module._load_designs_config(trace_dir)
        components_config = design_module._load_components_config(trace_dir)
        if "components" not in designs_config:
            designs_config["components"] = {}
        designs_config["components"][component] = {
            "figma_file_key": file_key,
            "figma_node_id": node_id,
            "figma_url": figma_url,
            "linked_at": datetime.now(UTC).isoformat(),
        }
        design_module._save_designs_config(trace_dir, designs_config)

        components_list = components_config.get("components", [])
        existing_idx = None
        for idx, comp in enumerate(components_list):
            if comp.get("name") == component:
                existing_idx = idx
                break
        component_entry = {
            "name": component,
            "path": component_path or f"src/components/{component}",
            "figma_url": figma_url,
            "figma_node_id": node_id,
            "has_story": False,
            "sync_status": "unsynced",
            "last_synced": None,
        }
        if existing_idx is not None:
            components_list[existing_idx] = component_entry
        else:
            components_list.append(component_entry)
        components_config["components"] = components_list
        design_module._save_components_config(trace_dir, components_config)
        return _wrap({"linked": component, "figma_url": figma_url}, ctx, action)

    if action == "status":
        designs_config = design_module._load_designs_config(trace_dir)
        components_config = design_module._load_components_config(trace_dir)
        figma_config = designs_config.get("figma", {})
        components_list = components_config.get("components", [])
        synced_count = sum(1 for c in components_list if c.get("sync_status") == "synced")
        unsynced_count = sum(1 for c in components_list if c.get("sync_status") == "unsynced")
        with_stories = sum(1 for c in components_list if c.get("has_story"))
        return _wrap(
            {
                "figma_file_key": figma_config.get("file_key"),
                "last_sync": designs_config.get("last_sync"),
                "total_components": len(components_list),
                "synced": synced_count,
                "unsynced": unsynced_count,
                "with_stories": with_stories,
            },
            ctx,
            action,
        )

    if action == "list":
        components_config = design_module._load_components_config(trace_dir)
        components_list = components_config.get("components", [])
        filter_status = payload.get("status")
        if filter_status:
            components_list = [c for c in components_list if c.get("sync_status") == filter_status]
        return _wrap({"components": components_list}, ctx, action)

    if action == "sync":
        direction = payload.get("direction", "both")
        dry_run = bool(payload.get("dry_run", False))
        if dry_run:
            return _wrap({"dry_run": True, "direction": direction}, ctx, action)
        designs_config = design_module._load_designs_config(trace_dir)
        components_config = design_module._load_components_config(trace_dir)
        cwd = Path.cwd()
        if direction in {"pull", "both"}:
            proc = await asyncio.create_subprocess_exec("bun", "run", "figma:pull", cwd=cwd)
            await proc.wait()
        if direction in {"push", "both"}:
            proc = await asyncio.create_subprocess_exec("bun", "run", "figma:push", cwd=cwd)
            await proc.wait()
        designs_config["last_sync"] = datetime.now(UTC).isoformat()
        design_module._save_designs_config(trace_dir, designs_config)
        for component in components_config.get("components", []):
            component["sync_status"] = "synced"
            component["last_synced"] = datetime.now(UTC).isoformat()
        design_module._save_components_config(trace_dir, components_config)
        return _wrap({"synced": True, "direction": direction}, ctx, action)

    if action == "generate":
        component = payload.get("component")
        all_components = bool(payload.get("all", False))
        template = payload.get("template", "default")
        if not all_components and not component:
            msg = "Specify component or all=true."
            raise ToolError(msg)
        components_config = design_module._load_components_config(trace_dir)
        components_list = components_config.get("components", [])
        target_components = (
            components_list if all_components else [c for c in components_list if c.get("name") == component]
        )
        generated = []
        cwd = Path.cwd()
        for comp in target_components:
            comp_name = comp.get("name")
            proc = await asyncio.create_subprocess_exec(
                "bun",
                "run",
                "storybook:generate",
                comp_name,
                "--template",
                template,
                cwd=cwd,
            )
            await proc.wait()
            comp["has_story"] = True
            generated.append(comp_name)
        design_module._save_components_config(trace_dir, components_config)
        return _wrap({"generated": generated}, ctx, action)

    if action == "export":
        component = payload.get("component")
        all_components = bool(payload.get("all", False))
        if not all_components and not component:
            msg = "Specify component or all=true."
            raise ToolError(msg)
        designs_config = design_module._load_designs_config(trace_dir)
        components_config = design_module._load_components_config(trace_dir)
        figma_config = designs_config.get("figma", {})
        figma_file_key = figma_config.get("file_key")
        figma_token = figma_config.get("access_token")
        if not figma_file_key or not figma_token:
            msg = "Figma credentials not configured."
            raise ToolError(msg)
        components_list = components_config.get("components", [])
        target_components = (
            components_list if all_components else [c for c in components_list if c.get("name") == component]
        )
        cwd = Path.cwd()
        exported = []
        for comp in target_components:
            if not comp.get("has_story"):
                continue
            proc = await asyncio.create_subprocess_exec(
                "bun",
                "run",
                "figma:export",
                comp.get("name"),
                "--file-key",
                figma_file_key,
                "--token",
                figma_token,
                cwd=cwd,
            )
            await proc.wait()
            exported.append(comp.get("name"))
        return _wrap({"exported": exported}, ctx, action)

    msg = f"Unknown design action: {action}"
    raise ToolError(msg)
