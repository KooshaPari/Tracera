"""Feature demo tools for FastMCP v3 capabilities."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from fastmcp import Context

from tracertm.mcp.core import mcp


def _truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


@mcp.tool(description="Report MCP feature flags and runtime configuration")
async def mcp_feature_status(ctx: Context | None = None) -> dict[str, Any]:
    """Return server feature flags and runtime config derived from env."""
    tool_transforms = os.getenv("TRACERTM_MCP_TOOL_TRANSFORMS")
    return {
        "providers": {
            "filesystem": os.getenv("TRACERTM_MCP_FILESYSTEM_ROOT"),
            "filesystem_reload": _truthy(os.getenv("TRACERTM_MCP_FILESYSTEM_RELOAD")),
            "skills_enabled": _truthy(os.getenv("TRACERTM_MCP_ENABLE_SKILLS")),
            "skills_provider": os.getenv("TRACERTM_MCP_SKILLS_PROVIDER") or "directory",
            "skills_roots": os.getenv("TRACERTM_MCP_SKILLS_ROOTS"),
            "skills_reload": _truthy(os.getenv("TRACERTM_MCP_SKILLS_RELOAD")),
            "openapi_spec": os.getenv("TRACERTM_MCP_OPENAPI_SPEC"),
            "proxy_targets": os.getenv("TRACERTM_MCP_PROXY_TARGETS"),
        },
        "transforms": {
            "namespace": os.getenv("TRACERTM_MCP_NAMESPACE"),
            "resources_as_tools": _truthy(os.getenv("TRACERTM_MCP_RESOURCES_AS_TOOLS")),
            "prompts_as_tools": _truthy(os.getenv("TRACERTM_MCP_PROMPTS_AS_TOOLS")),
            "tool_transforms": json.loads(tool_transforms) if tool_transforms else None,
            "version_gte": os.getenv("TRACERTM_MCP_VERSION_GTE"),
            "version_lt": os.getenv("TRACERTM_MCP_VERSION_LT"),
        },
        "tasks": {
            "default_task_mode": _truthy(os.getenv("TRACERTM_MCP_TASKS_DEFAULT")),
        },
        "session_state": {
            "redis_url": os.getenv("TRACERTM_MCP_SESSION_STATE_REDIS"),
        },
        "auth": {
            "auth_mode": os.getenv("TRACERTM_MCP_AUTH_MODE"),
            "required_scopes": os.getenv("TRACERTM_MCP_REQUIRED_SCOPES"),
        },
        "middleware": {
            "rate_limit_enabled": os.getenv("TRACERTM_MCP_RATE_LIMIT_ENABLED", "true"),
            "rate_limit_per_min": os.getenv("TRACERTM_MCP_RATE_LIMIT_PER_MIN", "60"),
            "rate_limit_per_hour": os.getenv("TRACERTM_MCP_RATE_LIMIT_PER_HOUR", "1000"),
            "verbose_logging": _truthy(os.getenv("TRACERTM_MCP_VERBOSE_LOGGING")),
        },
        "context": {"has_context": ctx is not None},
    }


@mcp.tool(version="1.0", description="Versioned demo tool v1 (returns sum)")
def demo_versioned_tool(x: int, y: int) -> dict[str, Any]:
    return {"version": "1.0", "result": x + y}


@mcp.tool(version="2.0", description="Versioned demo tool v2 (supports z and mode)")
def demo_versioned_tool(x: int, y: int, z: int = 0, mode: str = "sum") -> dict[str, Any]:
    if mode == "sum":
        result = x + y + z
    elif mode == "product":
        result = x * y * (z if z != 0 else 1)
    else:
        result = x + y + z
    return {"version": "2.0", "mode": mode, "result": result}


@mcp.tool(task=True, description="Task-enabled demo tool with progress updates")
async def demo_long_task(
    steps: int = 5,
    delay_seconds: float = 0.2,
    ctx: Context | None = None,
) -> dict[str, Any]:
    total = max(1, steps)
    for index in range(total):
        if ctx:
            await ctx.report_progress(index, total, f"Step {index + 1} of {total}")
        await asyncio.sleep(delay_seconds)
    if ctx:
        await ctx.report_progress(total, total, "Complete")
    return {"status": "done", "steps": total, "delay_seconds": delay_seconds}


__all__ = [
    "mcp_feature_status",
    "demo_versioned_tool",
    "demo_long_task",
]
