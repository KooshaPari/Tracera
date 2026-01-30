"""
Core MCP server instance for TraceRTM.

This module defines the single FastMCP server instance used across all tools.
All tool modules should import `mcp` from here and register via decorators.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.transforms import Namespace, PromptsAsTools, ResourcesAsTools, ToolTransform
from fastmcp.server.transforms.version_filter import VersionFilter
from fastmcp.tools.tool_transform import ToolTransformConfig

from tracertm.mcp.auth import build_auth_provider
from tracertm.mcp.middleware import AuthMiddleware, LoggingMiddleware, RateLimitMiddleware


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_tool_transforms() -> dict[str, ToolTransformConfig]:
    raw = os.getenv("TRACERTM_MCP_TOOL_TRANSFORMS")
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("TRACERTM_MCP_TOOL_TRANSFORMS must be a JSON object")
    transforms: dict[str, ToolTransformConfig] = {}
    for name, config in data.items():
        if not isinstance(config, dict):
            raise ValueError(f"Tool transform for {name} must be a JSON object")
        transforms[name] = ToolTransformConfig(**config)
    return transforms


def _add_providers(mcp: FastMCP) -> None:
    fs_root = os.getenv("TRACERTM_MCP_FILESYSTEM_ROOT")
    if fs_root:
        from fastmcp.server.providers import FileSystemProvider

        reload_flag = os.getenv("TRACERTM_MCP_FILESYSTEM_RELOAD", "").lower() in {"1", "true", "yes"}
        mcp.add_provider(FileSystemProvider(Path(fs_root), reload=reload_flag))

    if os.getenv("TRACERTM_MCP_ENABLE_SKILLS", "").lower() in {"1", "true", "yes"}:
        from fastmcp.server.providers.skills import SkillsDirectoryProvider, CodexSkillsProvider

        provider_mode = (os.getenv("TRACERTM_MCP_SKILLS_PROVIDER") or "directory").lower()
        if provider_mode == "codex":
            mcp.add_provider(CodexSkillsProvider())
        else:
            roots = _parse_csv(os.getenv("TRACERTM_MCP_SKILLS_ROOTS")) or [
                str(Path.cwd() / ".codex" / "skills"),
                str(Path.home() / ".codex" / "skills"),
            ]
            reload_flag = os.getenv("TRACERTM_MCP_SKILLS_RELOAD", "").lower() in {"1", "true", "yes"}
            mcp.add_provider(SkillsDirectoryProvider(roots=[Path(p) for p in roots], reload=reload_flag))

    openapi_spec = os.getenv("TRACERTM_MCP_OPENAPI_SPEC")
    if openapi_spec:
        from fastmcp.server.providers.openapi import OpenAPIProvider

        mcp.add_provider(OpenAPIProvider(openapi_spec))

    proxy_targets = _parse_csv(os.getenv("TRACERTM_MCP_PROXY_TARGETS"))
    if proxy_targets:
        from fastmcp.server import create_proxy

        for target in proxy_targets:
            mcp.add_provider(create_proxy(target))


def _add_transforms(mcp: FastMCP) -> None:
    namespace = os.getenv("TRACERTM_MCP_NAMESPACE")
    if namespace:
        mcp.add_transform(Namespace(namespace))

    if os.getenv("TRACERTM_MCP_RESOURCES_AS_TOOLS", "").lower() in {"1", "true", "yes"}:
        mcp.add_transform(ResourcesAsTools(mcp))

    if os.getenv("TRACERTM_MCP_PROMPTS_AS_TOOLS", "").lower() in {"1", "true", "yes"}:
        mcp.add_transform(PromptsAsTools(mcp))

    tool_transforms = _load_tool_transforms()
    if tool_transforms:
        mcp.add_transform(ToolTransform(tool_transforms))

    version_gte = os.getenv("TRACERTM_MCP_VERSION_GTE")
    version_lt = os.getenv("TRACERTM_MCP_VERSION_LT")
    if version_gte or version_lt:
        mcp.add_transform(VersionFilter(version_gte=version_gte, version_lt=version_lt))


def _build_session_state_store() -> Any | None:
    redis_url = os.getenv("TRACERTM_MCP_SESSION_STATE_REDIS")
    if not redis_url:
        return None
    from key_value.aio.stores.redis import RedisStore

    return RedisStore(redis_url)


def build_mcp_server() -> FastMCP:
    """Build and configure the MCP server with auth, middleware, providers, and transforms."""

    instructions = """TraceRTM MCP Server - AI-native traceability management.

Available tool groups:
- project_manage: Create, list, select, snapshot projects
- item_manage: CRUD for items (requirements, features, tests, etc.)
- link_manage: Create and query traceability links
- trace_analyze: Gap analysis, impact analysis, traceability matrix
- graph_analyze: Cycle detection, shortest path
- spec_analyze: Impact analysis and specification queries
- spec_manage: ADRs, contracts, features, scenarios
- quality_analyze: Requirement quality analysis
- config_manage: Configuration operations
- sync_manage: Offline sync operations

All tools use action/kind-based dispatch for a unified interface.
"""

    tasks_default = os.getenv("TRACERTM_MCP_TASKS_DEFAULT", "").lower() in {"1", "true", "yes"}
    session_state_store = _build_session_state_store()

    mcp = FastMCP(
        name="tracertm-mcp",
        instructions=instructions,
        auth=build_auth_provider(),
        tasks=tasks_default,
        session_state_store=session_state_store,
    )

    # Add middleware in order (most specific to most general)
    if os.getenv("TRACERTM_MCP_RATE_LIMIT_ENABLED", "true").lower() != "false":
        rate_limit_per_min = int(os.getenv("TRACERTM_MCP_RATE_LIMIT_PER_MIN", "60"))
        rate_limit_per_hour = int(os.getenv("TRACERTM_MCP_RATE_LIMIT_PER_HOUR", "1000"))
        rate_limiter = RateLimitMiddleware(
            calls_per_minute=rate_limit_per_min,
            calls_per_hour=rate_limit_per_hour,
            per_user=True,
        )
        mcp.add_middleware(rate_limiter)

    required_scopes = _parse_csv(os.getenv("TRACERTM_MCP_REQUIRED_SCOPES"))
    if required_scopes or os.getenv("TRACERTM_MCP_AUTH_MODE") != "disabled":
        auth_middleware = AuthMiddleware(required_scopes=required_scopes)
        mcp.add_middleware(auth_middleware)

    verbose_logging = os.getenv("TRACERTM_MCP_VERBOSE_LOGGING", "false").lower() == "true"
    logging_middleware = LoggingMiddleware(verbose=verbose_logging)
    mcp.add_middleware(logging_middleware)

    _add_providers(mcp)
    _add_transforms(mcp)

    return mcp


# Create the single MCP server instance
mcp = build_mcp_server()

__all__ = ["mcp", "build_mcp_server"]
