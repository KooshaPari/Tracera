"""Database management MCP tools."""

from __future__ import annotations

import asyncio
from typing import Any

from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except ImportError:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection

from .common import _wrap


def _require_db(config: ConfigManager) -> DatabaseConnection:
    database_url = config.get("database_url")
    if not database_url:
        msg = "Database URL not configured."
        raise ToolError(msg)
    db = DatabaseConnection(database_url)
    db.connect()
    return db


def _action_init(
    config: ConfigManager, payload: dict[str, object], ctx: object | None, action: str
) -> dict[str, object]:
    database_url_obj = payload.get("database_url")
    database_url = str(database_url_obj) if database_url_obj else None
    if database_url:
        config.set("database_url", database_url)
    return _wrap({"database_url": config.get("database_url")}, ctx, action)


def _action_status(config: ConfigManager, ctx: object | None, action: str) -> dict[str, object]:
    db = _require_db(config)
    try:
        health = db.health_check()
        return _wrap(health, ctx, action)
    finally:
        db.close()


def _action_migrate(config: ConfigManager, ctx: object | None, action: str) -> dict[str, object]:
    db = _require_db(config)
    try:
        db.create_tables()
        health = db.health_check()
        return _wrap(health, ctx, action)
    finally:
        db.close()


def _action_reset(
    config: ConfigManager, payload: dict[str, object], ctx: object | None, action: str
) -> dict[str, object]:
    confirm = bool(payload.get("confirm"))
    if not confirm:
        msg = "confirm=true is required for destructive operations."
        raise ToolError(msg)
    db = _require_db(config)
    try:
        db.drop_tables()
        db.create_tables()
        return _wrap({"status": "ok", "action": action}, ctx, action)
    finally:
        db.close()


def _action_rollback(
    config: ConfigManager, payload: dict[str, object], ctx: object | None, action: str
) -> dict[str, object]:
    confirm = bool(payload.get("confirm"))
    if not confirm:
        msg = "confirm=true is required for destructive operations."
        raise ToolError(msg)
    db = _require_db(config)
    try:
        db.drop_tables()
        return _wrap({"status": "ok", "action": action}, ctx, action)
    finally:
        db.close()


@mcp.tool(description="Unified database operations")
async def database_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified database management tool.

    Actions:
    - init: Initialize database (optional: database_url)
    - status: Check database status
    - migrate: Run migrations
    - reset: Drop and recreate tables (requires: confirm=true)
    - rollback: Drop tables (requires: confirm=true)
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    config = ConfigManager()

    handlers = {
        "init": lambda: _action_init(config, payload, ctx, action),
        "status": lambda: _action_status(config, ctx, action),
        "migrate": lambda: _action_migrate(config, ctx, action),
        "reset": lambda: _action_reset(config, payload, ctx, action),
        "rollback": lambda: _action_rollback(config, payload, ctx, action),
    }
    handler = handlers.get(action)
    if handler is None:
        msg = f"Unknown db action: {action}"
        raise ToolError(msg)
    return handler()
