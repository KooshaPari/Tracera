"""Configuration management MCP tools."""

from __future__ import annotations

import asyncio
from typing import Any

import yaml
from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except Exception:  # pragma: no cover

    class _StubMCP:
        def tool(self, *args: Any, **kwargs: Any):
            def decorator(fn):
                return fn

            return decorator

    mcp = _StubMCP()

from tracertm.config.manager import ConfigManager

from .common import _wrap


@mcp.tool(description="Unified configuration operations")
async def config_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified configuration management tool.

    Actions:
    - init: Initialize config (requires: database_url)
    - get: Get config value (requires: key; optional: project_id)
    - set: Set config value (requires: key, value; optional: project_id)
    - unset: Remove config value (requires: key; optional: project_id)
    - list: List all config values (optional: project_id)
    """
    return await _config_manage_impl(action, payload, ctx)


async def _config_manage_impl(
    action: str,
    payload: dict[str, Any] | None,
    ctx: Any | None,
) -> dict[str, Any]:
    """Implementation of configuration management."""
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    config = ConfigManager()
    project_id = payload.get("project_id")

    def _action_init() -> dict[str, Any]:
        database_url = payload.get("database_url")
        if not database_url:
            raise ToolError("database_url is required for config init.")
        result = config.init(database_url=database_url).model_dump()
        return _wrap(result, ctx, action)

    def _action_get() -> dict[str, Any]:
        key = payload.get("key")
        if not key:
            raise ToolError("key is required for config get.")
        config_path = config.projects_dir / project_id / "config.yaml" if project_id else config.config_path
        if config_path.exists():
            with config_path.open() as handle:
                stored = yaml.safe_load(handle) or {}
            if key in stored:
                return _wrap({"key": key, "value": stored.get(key)}, ctx, action)
        value = config.get(key, project_id=project_id)
        return _wrap({"key": key, "value": value}, ctx, action)

    def _action_set() -> dict[str, Any]:
        key = payload.get("key")
        if key is None:
            raise ToolError("key is required for config set.")
        value = payload.get("value")
        config.set(key, value, project_id=project_id)
        return _wrap({"key": key, "value": value}, ctx, action)

    def _action_unset() -> dict[str, Any]:
        key = payload.get("key")
        if not key:
            raise ToolError("key is required for config unset.")
        config.set(key, None, project_id=project_id)
        return _wrap({"key": key}, ctx, action)

    def _action_list() -> dict[str, Any]:
        result = config.get_config(project_id=project_id)
        return _wrap(result, ctx, action)

    handlers = {
        "init": _action_init,
        "get": _action_get,
        "set": _action_set,
        "unset": _action_unset,
        "list": _action_list,
    }
    handler = handlers.get(action)
    if handler is None:
        raise ToolError(f"Unknown config action: {action}")
    return handler()
