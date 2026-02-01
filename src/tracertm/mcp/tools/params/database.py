"""Database management MCP tools."""

from __future__ import annotations

from typing import Any

from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except Exception:  # pragma: no cover
    class _StubMCP:
        def tool(self, *args: Any, **kwargs: Any):
            def decorator(fn):
                return fn
            return decorator
    mcp = _StubMCP()  # type: ignore[assignment]

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from .common import _wrap


@mcp.tool(description="Unified database operations")
async def database_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified database management tool.

    Actions:
    - init: Initialize database (optional: database_url)
    - status: Check database status
    - migrate: Run migrations
    - reset: Drop and recreate tables (requires: confirm=true)
    - rollback: Drop tables (requires: confirm=true)
    """
    payload = payload or {}
    action = action.lower()
    config = ConfigManager()

    if action == "init":
        database_url = payload.get("database_url")
        if database_url:
            config.set("database_url", database_url)
        return _wrap({"database_url": config.get("database_url")}, ctx, action)

    database_url = config.get("database_url")
    if not database_url:
        raise ToolError("Database URL not configured.")

    db = DatabaseConnection(database_url)
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
            raise ToolError("confirm=true is required for destructive operations.")
        if action == "rollback":
            db.drop_tables()
        else:
            db.drop_tables()
            db.create_tables()
        db.close()
        return _wrap({"status": "ok", "action": action}, ctx, action)

    db.close()
    raise ToolError(f"Unknown db action: {action}")
