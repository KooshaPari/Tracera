"""Configuration management MCP tools."""

from __future__ import annotations

import asyncio
from typing import Any

import yaml
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

from .common import _wrap


@mcp.tool(description="Unified configuration operations")
async def config_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified configuration management tool.

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
    payload: dict[str, object] | None,
    ctx: object | None,
) -> dict[str, object]:
    """Implementation of configuration management."""
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    config = ConfigManager()
    project_id_obj = payload.get("project_id")
    project_id = str(project_id_obj) if project_id_obj else None

    def _action_init() -> dict[str, object]:
        database_url_obj = payload.get("database_url")
        database_url = str(database_url_obj) if database_url_obj else None
        if not database_url:
            msg = "database_url is required for config init."
            raise ToolError(msg)
        result = config.init(database_url=database_url).model_dump()
        return _wrap(result, ctx, action)

    def _action_get() -> dict[str, object]:
        key_obj = payload.get("key")
        if not key_obj:
            msg = "key is required for config get."
            raise ToolError(msg)
        key = str(key_obj)
        config_path = config.projects_dir / project_id / "config.yaml" if project_id else config.config_path
        if config_path.exists():
            with config_path.open() as handle:
                stored = yaml.safe_load(handle) or {}
            if key in stored:
                return _wrap({"key": key, "value": stored.get(key)}, ctx, action)
        value = config.get(key, project_id=project_id)
        return _wrap({"key": key, "value": value}, ctx, action)

    def _action_set() -> dict[str, object]:
        key_obj = payload.get("key")
        if key_obj is None:
            msg = "key is required for config set."
            raise ToolError(msg)
        key = str(key_obj)
        value = payload.get("value")
        config.set(key, value, project_id=project_id)
        return _wrap({"key": key, "value": value}, ctx, action)

    def _action_unset() -> dict[str, object]:
        key_obj = payload.get("key")
        if not key_obj:
            msg = "key is required for config unset."
            raise ToolError(msg)
        key = str(key_obj)
        config.set(key, None, project_id=project_id)
        return _wrap({"key": key}, ctx, action)

    def _action_list() -> dict[str, object]:
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
        msg = f"Unknown config action: {action}"
        raise ToolError(msg)
    return handler()
