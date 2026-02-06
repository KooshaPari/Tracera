"""MCP package exports and optional imports. Not part of public API."""

from __future__ import annotations


def run_server() -> None:
    """Standalone MCP is not allowed. MCP runs only as part of the backend (mounted ASGI)."""
    import sys

    print("Standalone MCP is not allowed.", file=sys.stderr)
    print("MCP is only available as part of the backend (mounted ASGI process).", file=sys.stderr)
    print(
        "Start the TraceRTM API server (e.g. uvicorn tracertm.api.main:app, or rtm dev) and use /api/v1/mcp/...",
        file=sys.stderr,
    )
    sys.exit(1)


try:
    from tracertm.mcp.server import mcp
except Exception:  # pragma: no cover - allow imports in limited test envs
    mcp = None

try:
    from tracertm.mcp.http_transport import (
        DEFAULT_HTTP_HOST,
        DEFAULT_HTTP_PORT,
        DEFAULT_MCP_PATH,
        create_progress_stream,
        create_standalone_http_app,
        get_transport_type,
        mount_mcp_to_fastapi,
        run_http_server,
    )

    _http_ok = True
except Exception:  # pragma: no cover - allow imports in limited test envs
    _http_ok = False

try:
    from tracertm.mcp.error_handlers import (
        DatabaseError,
        ErrorEnhancementMiddleware,
        ItemNotFoundError,
        LLMFriendlyError,
        ProjectNotSelectedError,
        ValidationError,
    )
    from tracertm.mcp.logging_config import (
        StructuredLogger,
        configure_structured_logging,
        get_structured_logger,
    )
    from tracertm.mcp.metrics import (
        MetricsExporter,
        MetricsMiddleware,
        mcp_registry,
        track_auth_failure,
        track_rate_limit_hit,
    )
    from tracertm.mcp.metrics_endpoint import (
        MetricsServer,
        get_metrics_server,
        start_metrics_server,
    )
    from tracertm.mcp.telemetry import (
        PerformanceMonitoringMiddleware,
        TelemetryMiddleware,
        get_tracer,
        setup_telemetry,
    )

    __all__ = [
        "DatabaseError",
        "ErrorEnhancementMiddleware",
        "ItemNotFoundError",
        "LLMFriendlyError",
        "MetricsExporter",
        "MetricsMiddleware",
        "MetricsServer",
        "PerformanceMonitoringMiddleware",
        "ProjectNotSelectedError",
        "StructuredLogger",
        "TelemetryMiddleware",
        "ValidationError",
        "configure_structured_logging",
        "get_metrics_server",
        "get_structured_logger",
        "get_tracer",
        "mcp",
        "mcp_registry",
        "run_server",
        "setup_telemetry",
        "start_metrics_server",
        "track_auth_failure",
        "track_rate_limit_hit",
    ]
    if _http_ok:
        __all__ = [
            "DEFAULT_HTTP_HOST",
            "DEFAULT_HTTP_PORT",
            "DEFAULT_MCP_PATH",
            "create_progress_stream",
            "create_standalone_http_app",
            "get_transport_type",
            "mount_mcp_to_fastapi",
            "run_http_server",
            *__all__,
        ]
except ImportError:
    if _http_ok:
        __all__ = [
            "DEFAULT_HTTP_HOST",
            "DEFAULT_HTTP_PORT",
            "DEFAULT_MCP_PATH",
            "create_progress_stream",
            "create_standalone_http_app",
            "get_transport_type",
            "mcp",
            "mount_mcp_to_fastapi",
            "run_http_server",
            "run_server",
        ]
    else:
        __all__ = ["mcp", "run_server"]
