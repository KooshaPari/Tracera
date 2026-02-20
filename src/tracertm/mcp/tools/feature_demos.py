"""Feature demo tools for FastMCP v3 capabilities."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from fastmcp.server.dependencies import Progress

from tracertm.mcp.core import mcp


def _truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


@mcp.tool(description="Report MCP feature flags and runtime configuration")
async def mcp_feature_status(ctx: object | None = None) -> dict[str, object]:
    """Return server feature flags and runtime config derived from env."""
    await asyncio.sleep(0)
    tool_transforms = os.getenv("TRACERTM_MCP_TOOL_TRANSFORMS")
    return {
        "providers": {
            "filesystem": os.getenv("TRACERTM_MCP_FILESYSTEM_ROOT"),
            "filesystem_reload": _truthy(os.getenv("TRACERTM_MCP_FILESYSTEM_RELOAD")),
            "skills_roots": os.getenv("TRACERTM_MCP_SKILLS_ROOTS") or "default (.codex/skills)",
            "skills_provider": os.getenv("TRACERTM_MCP_SKILLS_PROVIDER") or "directory",
            "skills_reload": _truthy(os.getenv("TRACERTM_MCP_SKILLS_RELOAD")),
            "openapi_spec": os.getenv("TRACERTM_MCP_OPENAPI_SPEC"),
            "proxy_targets": os.getenv("TRACERTM_MCP_PROXY_TARGETS"),
        },
        "transforms": {
            "namespace": os.getenv("TRACERTM_MCP_NAMESPACE"),
            "tool_transforms": json.loads(tool_transforms) if tool_transforms else None,
            "version_gte": os.getenv("TRACERTM_MCP_VERSION_GTE"),
            "version_lt": os.getenv("TRACERTM_MCP_VERSION_LT"),
        },
        "tasks": {
            "tasks": True,
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
def demo_versioned_tool(x: int, y: int) -> dict[str, object]:
    """Demo tool for versioning (v1).

    Args:
        x: First number
        y: Second number

    Returns:
        Result dictionary with version and sum
    """
    return {"version": "1.0", "result": x + y}


@mcp.tool(version="2.0", description="Versioned demo tool v2 (supports z and mode)")
def demo_versioned_tool_extended(x: int, y: int, z: int = 0, mode: str = "sum") -> dict[str, object]:
    """Demo tool for versioning (v2).

    Args:
        x: First number
        y: Second number
        z: Third number (default 0)
        mode: Operation mode (sum or product)

    Returns:
        Result dictionary with version, mode and result
    """
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
    progress: Any = Progress(),
) -> dict[str, object]:
    """Demo tool for long-running tasks with progress updates.

    Args:
        steps: Number of steps to perform
        delay_seconds: Seconds to wait between steps
        progress: Progress tracker

    Returns:
        Result dictionary
    """
    total = max(1, steps)
    await progress.set_total(total)
    for index in range(total):
        await progress.set_message(f"Step {index + 1} of {total}")
        await asyncio.sleep(delay_seconds)
        await progress.increment(1)
    await progress.set_message("Complete")
    return {"status": "done", "steps": total, "delay_seconds": delay_seconds}


__all__ = [
    "demo_long_task",
    "demo_versioned_tool",
    "mcp_feature_status",
]
