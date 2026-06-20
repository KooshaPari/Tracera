"""Core MCP server instance for TraceRTM.

This module defines the single FastMCP server instance used across all tools.
All tool modules should import `mcp` from here and register via decorators.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

# Disable optional Pydantic plugins that are not part of this repo (ex: logfire).
if os.getenv("PYDANTIC_DISABLE_PLUGINS") is None:
    os.environ["PYDANTIC_DISABLE_PLUGINS"] = "logfire-plugin"

from fastmcp import FastMCP
from fastmcp.server.transforms import Namespace, PromptsAsTools, ResourcesAsTools, ToolTransform
from fastmcp.server.transforms.version_filter import VersionFilter
from fastmcp.tools.tool_transform import ToolTransformConfig

from tracertm.mcp.auth import build_auth_provider
from tracertm.mcp.middleware import LoggingMiddleware, RateLimitMiddleware

# Import monitoring components (optional, won't fail if not installed)
try:
    from tracertm.mcp.error_handlers import ErrorEnhancementMiddleware
    from tracertm.mcp.logging_config import configure_structured_logging
    from tracertm.mcp.metrics import MetricsMiddleware
    from tracertm.mcp.telemetry import PerformanceMonitoringMiddleware, TelemetryMiddleware

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        msg = f"{name} is required for MCP startup"
        raise RuntimeError(msg)
    return value.strip()


def _require_truthy_env(name: str) -> str:
    value = _require_env(name).lower()
    if value in {"0", "false", "no", "off"}:
        msg = f"{name} must be enabled for MCP startup"
        raise RuntimeError(msg)
    return value


def _ensure_paths_exist(label: str, paths: list[str]) -> None:
    expanded = [Path(p).expanduser() for p in paths]
    if not any(p.exists() for p in expanded):
        msg = f"{label} has no existing paths: {', '.join(paths)}"
        raise RuntimeError(msg)


def _validate_required_mcp_env() -> None:
    if not MONITORING_AVAILABLE:
        msg = "MCP monitoring dependencies are required but not installed"
        raise RuntimeError(msg)
    _require_env("TRACERTM_MCP_FILESYSTEM_ROOT")
    _require_env("TRACERTM_MCP_SKILLS_ROOTS")
    _require_env("TRACERTM_MCP_OPENAPI_SPEC")
    _require_env("TRACERTM_MCP_PROXY_TARGETS")
    _require_env("TRACERTM_MCP_NAMESPACE")
    _require_env("TRACERTM_MCP_TOOL_TRANSFORMS")
    _require_env("TRACERTM_MCP_VERSION_GTE")
    _require_env("TRACERTM_MCP_VERSION_LT")
    _require_env("TRACERTM_MCP_SESSION_STATE_REDIS")

    _require_truthy_env("TRACERTM_MCP_STRUCTURED_LOGGING")
    _require_truthy_env("TRACERTM_MCP_TELEMETRY_ENABLED")
    _require_truthy_env("TRACERTM_MCP_METRICS_ENABLED")
    _require_env("TRACERTM_MCP_METRICS_HOST")
    _require_env("TRACERTM_MCP_METRICS_PORT")
    _require_truthy_env("TRACERTM_MCP_PERF_MONITORING")
    _require_truthy_env("TRACERTM_MCP_ENHANCED_ERRORS")
    _require_truthy_env("TRACERTM_MCP_RATE_LIMIT_ENABLED")

    filesystem_root = Path(_require_env("TRACERTM_MCP_FILESYSTEM_ROOT")).expanduser()
    if not filesystem_root.exists():
        msg = "TRACERTM_MCP_FILESYSTEM_ROOT does not exist"
        raise RuntimeError(msg)

    skills_roots = _parse_csv(_require_env("TRACERTM_MCP_SKILLS_ROOTS"))
    if not skills_roots:
        msg = "TRACERTM_MCP_SKILLS_ROOTS must include at least one path"
        raise RuntimeError(msg)
    _ensure_paths_exist("TRACERTM_MCP_SKILLS_ROOTS", skills_roots)

    _parse_csv(_require_env("TRACERTM_MCP_PROXY_TARGETS"))

    openapi_spec = Path(_require_env("TRACERTM_MCP_OPENAPI_SPEC")).expanduser()
    if not openapi_spec.exists():
        msg = "TRACERTM_MCP_OPENAPI_SPEC does not exist"
        raise RuntimeError(msg)


def _load_tool_transforms(require: bool = True) -> dict[str, ToolTransformConfig]:
    raw = os.getenv("TRACERTM_MCP_TOOL_TRANSFORMS")
    if not raw:
        if require:
            msg = "TRACERTM_MCP_TOOL_TRANSFORMS is required for MCP startup"
            raise RuntimeError(msg)
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "TRACERTM_MCP_TOOL_TRANSFORMS must be a JSON object"
        raise ValueError(msg)
    transforms: dict[str, ToolTransformConfig] = {}
    for name, config in data.items():
        if not isinstance(config, dict):
            msg = f"Tool transform for {name} must be a JSON object"
            raise ValueError(msg)
        transforms[name] = ToolTransformConfig(**config)
    return transforms


def _add_providers(mcp: FastMCP) -> None:
    fs_root = os.getenv("TRACERTM_MCP_FILESYSTEM_ROOT")
    if fs_root:
        from fastmcp.server.providers import FileSystemProvider

        reload_flag = os.getenv("TRACERTM_MCP_FILESYSTEM_RELOAD", "").lower() in {"1", "true", "yes"}
        mcp.add_provider(FileSystemProvider(Path(fs_root).expanduser(), reload=reload_flag))

    # Skills provider: always added when roots are set or default paths used (no ENABLE gate).
    roots = _parse_csv(os.getenv("TRACERTM_MCP_SKILLS_ROOTS"))
    if roots:
        from fastmcp.server.providers.skills import CodexSkillsProvider, SkillsDirectoryProvider

        provider_mode = (os.getenv("TRACERTM_MCP_SKILLS_PROVIDER") or "directory").lower()
        if provider_mode == "codex":
            mcp.add_provider(CodexSkillsProvider())
        else:
            reload_flag = os.getenv("TRACERTM_MCP_SKILLS_RELOAD", "").lower() in {"1", "true", "yes"}
            mcp.add_provider(
                SkillsDirectoryProvider(
                    roots=[Path(p).expanduser() for p in roots],
                    reload=reload_flag,
                ),
            )

    openapi_spec = os.getenv("TRACERTM_MCP_OPENAPI_SPEC")
    if openapi_spec:
        # OpenAPIProvider requires (openapi_spec: dict[str, object], client: httpx.AsyncClient); skip if only URL/path string
        pass

    proxy_targets = _parse_csv(os.getenv("TRACERTM_MCP_PROXY_TARGETS"))
    if proxy_targets:
        from fastmcp.server import create_proxy

        base_url = (os.getenv("TRACERTM_MCP_BASE_URL") or "").rstrip("/")
        filtered_targets: list[str] = []
        for target in proxy_targets:
            if target.rstrip("/") == base_url:
                logger.warning("Skipping MCP proxy target that points to self: %s", target)
                continue
            filtered_targets.append(target)

        if not filtered_targets:
            logger.warning("No MCP proxy targets available after filtering; proxy provider disabled")
            return

        for target in filtered_targets:
            mcp.add_provider(create_proxy(target))


def _add_transforms(mcp: FastMCP, require_tool_transforms: bool = True) -> None:
    namespace = os.getenv("TRACERTM_MCP_NAMESPACE")
    if namespace:
        mcp.add_transform(Namespace(namespace))

    # No resource or feature is optional: always expose resources and prompts as tools.
    mcp.add_transform(ResourcesAsTools(mcp))
    mcp.add_transform(PromptsAsTools(mcp))

    tool_transforms = _load_tool_transforms(require=require_tool_transforms)
    if tool_transforms:
        mcp.add_transform(ToolTransform(tool_transforms))

    version_gte = os.getenv("TRACERTM_MCP_VERSION_GTE")
    version_lt = os.getenv("TRACERTM_MCP_VERSION_LT")
    if version_gte or version_lt:
        mcp.add_transform(VersionFilter(version_gte=version_gte, version_lt=version_lt))


def _build_session_state_store() -> Any:
    redis_url = _require_env("TRACERTM_MCP_SESSION_STATE_REDIS")
    from key_value.aio.stores.redis import RedisStore

    return RedisStore(url=redis_url)


def build_mcp_server(transport: str = "http") -> FastMCP:
    """Build and configure the MCP server with auth, middleware, providers, and transforms.

    Full-feature: all MCP env and preflight are required (no optionality).

    Args:
        transport: Transport mode - "http" only (stdio is not supported).

    Returns:
        Configured FastMCP server instance
    """
    from tracertm.preflight import build_mcp_checks, check_cli_available, run_preflight

    if transport == "stdio":
        msg = (
            "MCP stdio transport is not supported. Use HTTP only "
            "(e.g. API /api/v1/mcp/... or rtm mcp --transport http)."
        )
        raise RuntimeError(
            msg,
        )

    _validate_required_mcp_env()
    is_pytest = bool(os.getenv("PYTEST_RUNNING") or os.getenv("PYTEST_CURRENT_TEST") or os.getenv("PYTEST_WORKER"))
    if not is_pytest:
        run_preflight("mcp", build_mcp_checks(), strict=True)
        if not check_cli_available():
            logger.warning("[mcp] CLI module unavailable; CLI-backed tools will be limited")

    # Configure structured logging if available
    if MONITORING_AVAILABLE and os.getenv("TRACERTM_MCP_STRUCTURED_LOGGING", "true").lower() == "true":
        log_level = os.getenv("TRACERTM_MCP_LOG_LEVEL", "INFO")
        json_output = os.getenv("TRACERTM_MCP_JSON_LOGS", "true").lower() == "true"
        log_file = os.getenv("TRACERTM_MCP_LOG_FILE")
        configure_structured_logging(log_level, json_output, log_file)

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
    session_state_store = _build_session_state_store()

    auth_provider = build_auth_provider(transport=transport)
    mcp = FastMCP(
        name="tracertm-mcp",
        instructions=instructions,
        auth=auth_provider,
        tasks=True,
        session_state_store=session_state_store,
    )

    # Add middleware in order (most specific to most general)
    # First: Telemetry and metrics (outermost layer, captures everything)
    if MONITORING_AVAILABLE and os.getenv("TRACERTM_MCP_TELEMETRY_ENABLED", "true").lower() == "true":
        mcp.add_middleware(TelemetryMiddleware())

    if MONITORING_AVAILABLE and os.getenv("TRACERTM_MCP_METRICS_ENABLED", "true").lower() == "true":
        track_payload = os.getenv("TRACERTM_MCP_TRACK_PAYLOAD_SIZE", "true").lower() == "true"
        mcp.add_middleware(MetricsMiddleware(track_payload_size=track_payload))
        metrics_host = os.getenv("TRACERTM_MCP_METRICS_HOST", "0.0.0.0")  # nosec B104 -- configurable via env var
        metrics_port = int(os.getenv("TRACERTM_MCP_METRICS_PORT", "9090"))
        from tracertm.mcp.metrics_endpoint import start_metrics_server

        start_metrics_server(host=metrics_host, port=metrics_port)

    if MONITORING_AVAILABLE and os.getenv("TRACERTM_MCP_PERF_MONITORING", "true").lower() == "true":
        slow_threshold = float(os.getenv("TRACERTM_MCP_SLOW_THRESHOLD", "5.0"))
        very_slow_threshold = float(os.getenv("TRACERTM_MCP_VERY_SLOW_THRESHOLD", "30.0"))
        mcp.add_middleware(PerformanceMonitoringMiddleware(slow_threshold, very_slow_threshold))

    # Second: Error enhancement (wraps errors before they bubble up)
    if MONITORING_AVAILABLE and os.getenv("TRACERTM_MCP_ENHANCED_ERRORS", "true").lower() == "true":
        include_traces = os.getenv("TRACERTM_MCP_INCLUDE_STACK_TRACES", "false").lower() == "true"
        mcp.add_middleware(ErrorEnhancementMiddleware(include_stack_traces=include_traces))

    # Third: Rate limiting (before auth to avoid auth overhead for rate-limited requests)
    if os.getenv("TRACERTM_MCP_RATE_LIMIT_ENABLED", "true").lower() != "false":
        rate_limit_per_min = int(os.getenv("TRACERTM_MCP_RATE_LIMIT_PER_MIN", "60"))
        rate_limit_per_hour = int(os.getenv("TRACERTM_MCP_RATE_LIMIT_PER_HOUR", "1000"))
        rate_limiter = RateLimitMiddleware(
            calls_per_minute=rate_limit_per_min,
            calls_per_hour=rate_limit_per_hour,
            per_user=True,
        )
        mcp.add_middleware(rate_limiter)

    # Fourth: Logging (innermost layer, logs the actual tool execution)
    verbose_logging = os.getenv("TRACERTM_MCP_VERBOSE_LOGGING", "false").lower() == "true"
    logging_middleware = LoggingMiddleware(verbose=verbose_logging)
    mcp.add_middleware(logging_middleware)

    _add_providers(mcp)
    _add_transforms(mcp, require_tool_transforms=True)

    return mcp


# Lazy HTTP instance (full MCP env required on first use).
_http_instance: FastMCP | None = None


def get_mcp(transport: str = "http") -> FastMCP:
    """Return cached MCP server (HTTP only). Builds on first call."""
    global _http_instance
    if transport != "http":
        msg = "MCP stdio is not supported. Use transport='http' only."
        raise RuntimeError(msg)
    if _http_instance is None:
        _http_instance = build_mcp_server(transport="http")
    return _http_instance


# Single MCP instance is HTTP-only (for server.py and CLI list commands).
def __getattr__(name: str) -> FastMCP:
    if name == "mcp":
        return get_mcp("http")
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


def create_mcp_server(transport: str = "http") -> FastMCP:
    """Factory function to create MCP server (HTTP only)."""
    return build_mcp_server(transport=transport)


__all__ = ["build_mcp_server", "create_mcp_server", "get_mcp", "mcp"]
