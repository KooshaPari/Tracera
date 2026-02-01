"""
TraceRTM MCP Server - FastMCP 3.0.0b1 based MCP server for AI-native CLI.

This module provides:
- Tools: Actions the AI can perform (CRUD, analysis, verification)
- Resources: Data the AI can access (projects, graphs, reports)
- Prompts: Reusable prompt templates (ADR creation, analysis)
- Monitoring: OpenTelemetry tracing, Prometheus metrics, structured logging
"""

from __future__ import annotations


def run_server() -> None:
    """Standalone MCP is not allowed. MCP runs only as part of the backend (mounted ASGI)."""
    import sys
    print("Standalone MCP is not allowed.", file=sys.stderr)
    print("MCP is only available as part of the backend (mounted ASGI process).", file=sys.stderr)
    print("Start the TraceRTM API server (e.g. uvicorn tracertm.api.main:app, or rtm dev) and use /api/v1/mcp/...", file=sys.stderr)
    sys.exit(1)


try:
    from tracertm.mcp.server import mcp
except Exception:  # pragma: no cover - allow imports in limited test envs
    mcp = None

# Export HTTP transport utilities (Phase 3)
try:
    from tracertm.mcp.http_transport import (
        create_standalone_http_app,
        run_http_server,
        mount_mcp_to_fastapi,
        create_progress_stream,
        get_transport_type,
        DEFAULT_HTTP_HOST,
        DEFAULT_HTTP_PORT,
        DEFAULT_MCP_PATH,
    )
except Exception:  # pragma: no cover - allow imports in limited test envs
    pass

# Export monitoring components (optional, may not be available in all environments)
try:
    from tracertm.mcp.telemetry import (
        TelemetryMiddleware,
        PerformanceMonitoringMiddleware,
        setup_telemetry,
        get_tracer,
    )
    from tracertm.mcp.metrics import (
        MetricsMiddleware,
        MetricsExporter,
        mcp_registry,
        track_rate_limit_hit,
        track_auth_failure,
    )
    from tracertm.mcp.error_handlers import (
        LLMFriendlyError,
        ProjectNotSelectedError,
        ItemNotFoundError,
        DatabaseError,
        ValidationError,
        ErrorEnhancementMiddleware,
    )
    from tracertm.mcp.logging_config import (
        configure_structured_logging,
        StructuredLogger,
        get_structured_logger,
    )
    from tracertm.mcp.metrics_endpoint import (
        MetricsServer,
        start_metrics_server,
        get_metrics_server,
    )

    __all__ = [
        # Core
        "mcp",
        "run_server",
        # HTTP Transport (Phase 3)
        "create_standalone_http_app",
        "run_http_server",
        "mount_mcp_to_fastapi",
        "create_progress_stream",
        "get_transport_type",
        "DEFAULT_HTTP_HOST",
        "DEFAULT_HTTP_PORT",
        "DEFAULT_MCP_PATH",
        # Telemetry
        "TelemetryMiddleware",
        "PerformanceMonitoringMiddleware",
        "setup_telemetry",
        "get_tracer",
        # Metrics
        "MetricsMiddleware",
        "MetricsExporter",
        "mcp_registry",
        "track_rate_limit_hit",
        "track_auth_failure",
        # Errors
        "LLMFriendlyError",
        "ProjectNotSelectedError",
        "ItemNotFoundError",
        "DatabaseError",
        "ValidationError",
        "ErrorEnhancementMiddleware",
        # Logging
        "configure_structured_logging",
        "StructuredLogger",
        "get_structured_logger",
        # Endpoints
        "MetricsServer",
        "start_metrics_server",
        "get_metrics_server",
    ]
except ImportError:
    # Monitoring dependencies not available, but HTTP transport still works
    __all__ = [
        "mcp",
        "run_server",
        "create_standalone_http_app",
        "run_http_server",
        "mount_mcp_to_fastapi",
        "create_progress_stream",
        "get_transport_type",
        "DEFAULT_HTTP_HOST",
        "DEFAULT_HTTP_PORT",
        "DEFAULT_MCP_PATH",
    ]
