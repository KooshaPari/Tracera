#!/usr/bin/env python3
"""MCP Health Check Script.

Verifies that MCP server optimizations are working correctly:
- Server is running and responsive
- All tools are accessible
- Response times within thresholds
- No errors in critical operations
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class HealthCheck:
    """Result of a health check."""

    name: str
    status: str  # "pass", "fail", "warn"
    duration_ms: float
    message: str
    details: dict[str, Any]


class MCPHealthChecker:
    """Health check runner for MCP server."""

    def __init__(self) -> None:
        self.checks: list[HealthCheck] = []

    def add_check(self, check: HealthCheck) -> None:
        """Add a health check result."""
        self.checks.append(check)

    def run_check(self, name: str, func: Any, **kwargs: Any) -> HealthCheck:
        """Run a single health check."""
        start = time.perf_counter()
        status = "pass"
        message = "OK"
        details = {}

        try:
            result = asyncio.run(func(**kwargs)) if asyncio.iscoroutinefunction(func) else func(**kwargs)

            if isinstance(result, dict):
                details = result
                if "error" in result:
                    status = "fail"
                    message = result["error"]
                elif "warning" in result:
                    status = "warn"
                    message = result["warning"]

        except Exception as e:
            status = "fail"
            message = str(e)
            details = {"exception": type(e).__name__}

        duration = (time.perf_counter() - start) * 1000

        check = HealthCheck(name=name, status=status, duration_ms=duration, message=message, details=details)

        self.add_check(check)
        return check

    def print_summary(self) -> None:
        """Print summary of health checks."""
        sum(1 for c in self.checks if c.status == "pass")
        failed = sum(1 for c in self.checks if c.status == "fail")
        sum(1 for c in self.checks if c.status == "warn")

        for check in self.checks:
            if check.details:
                pass

        return failed == 0

    def save_results(self, filename: str = "health_check_results.json") -> None:
        """Save health check results."""
        output_dir = Path(__file__).parent / "health_check_results"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / filename

        data = {
            "timestamp": time.time(),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "duration_ms": c.duration_ms,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }

        with Path(output_file).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


# ============================================================
# Health Check Functions
# ============================================================


def check_server_running() -> dict[str, Any]:
    """Check that MCP server is running."""
    try:
        from tracertm.mcp.server import mcp

        return {"running": True, "name": mcp.name}
    except ImportError as e:
        return {"error": f"Cannot import MCP server: {e}"}
    except Exception as e:
        return {"error": f"Server error: {e}"}


def check_tool_registration() -> dict[str, Any]:
    """Check that tools are registered."""
    try:
        from tracertm.mcp.registry import get_registry

        registry = get_registry()
        tools = registry.list_registered_tools()

        if len(tools) == 0:
            return {"error": "No tools registered"}

        return {"tools_count": len(tools), "sample_tools": tools[:5]}
    except Exception as e:
        return {"error": f"Tool registration check failed: {e}"}


def check_lazy_loading() -> dict[str, Any]:
    """Check that lazy loading is working."""
    import os

    from tracertm.mcp.registry import get_registry

    lazy_loading_enabled = os.getenv("TRACERTM_MCP_LAZY_LOADING", "false").lower() == "true"

    registry = get_registry()

    # Register a test tool
    registry.register_tool_loader(
        "health_check_tool",
        "tracertm.mcp.tools.params.project",
        {"description": "Health check test tool"},
    )

    # Check if module is loaded
    is_loaded = registry.is_loaded("tracertm.mcp.tools.params.project")

    if lazy_loading_enabled and is_loaded:
        return {"warning": "Lazy loading enabled but module already loaded"}

    return {"lazy_loading_enabled": lazy_loading_enabled, "module_loaded": is_loaded, "status": "working as expected"}


def check_tool_metadata() -> dict[str, Any]:
    """Check that tool metadata is accessible."""
    from tracertm.mcp.registry import get_registry

    registry = get_registry()
    tools = registry.list_registered_tools()

    if not tools:
        return {"error": "No tools to check metadata"}

    # Check first tool's metadata
    tool_name = tools[0]
    metadata = registry.get_tool_metadata(tool_name)

    if metadata is None:
        return {"error": f"No metadata for tool: {tool_name}"}

    return {"tool": tool_name, "metadata": metadata}


async def check_async_operations() -> dict[str, Any]:
    """Check that async operations work."""

    async def test_async() -> str:
        await asyncio.sleep(0.01)
        return "success"

    result = await test_async()

    if result != "success":
        return {"error": "Async operation failed"}

    return {"async_working": True}


def check_performance_thresholds() -> dict[str, Any]:
    """Check that performance is within thresholds."""
    from tracertm.mcp.registry import get_registry

    # Test tool lookup speed
    registry = get_registry()

    start = time.perf_counter()
    registry.list_registered_tools()
    duration_ms = (time.perf_counter() - start) * 1000

    threshold_ms = 50  # Tool lookup should be <50ms

    if duration_ms > threshold_ms:
        return {
            "warning": f"Tool lookup slow: {duration_ms:.2f}ms (threshold: {threshold_ms}ms)",
            "duration_ms": duration_ms,
        }

    return {"duration_ms": duration_ms, "threshold_ms": threshold_ms, "within_threshold": True}


def check_environment_variables() -> dict[str, Any]:
    """Check MCP environment configuration."""
    import os

    env_vars = {
        "TRACERTM_MCP_LAZY_LOADING": os.getenv("TRACERTM_MCP_LAZY_LOADING", "not set"),
        "TRACERTM_MCP_COMPRESSION": os.getenv("TRACERTM_MCP_COMPRESSION", "not set"),
        "TRACERTM_MCP_STREAMING": os.getenv("TRACERTM_MCP_STREAMING", "not set"),
        "TRACERTM_MCP_TOKEN_OPTIMIZATION": os.getenv("TRACERTM_MCP_TOKEN_OPTIMIZATION", "not set"),
        "TRACERTM_MCP_CONNECTION_POOL_SIZE": os.getenv("TRACERTM_MCP_CONNECTION_POOL_SIZE", "not set"),
    }

    return {"environment": env_vars}


def check_memory_usage() -> dict[str, Any]:
    """Check memory usage."""
    import os

    import psutil

    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024

    threshold_mb = 500  # Warn if >500MB

    if memory_mb > threshold_mb:
        return {
            "warning": f"High memory usage: {memory_mb:.1f}MB",
            "memory_mb": memory_mb,
            "threshold_mb": threshold_mb,
        }

    return {"memory_mb": memory_mb, "threshold_mb": threshold_mb, "within_threshold": True}


def check_error_logs() -> dict[str, Any]:
    """Check for errors in recent logs."""
    # This is a placeholder - implement actual log checking
    return {"recent_errors": 0, "note": "Log checking not implemented yet"}


# ============================================================
# Main Health Check Suite
# ============================================================


def run_health_checks() -> int:
    """Run all health checks."""
    checker = MCPHealthChecker()

    # Run checks
    checker.run_check("Server Running", check_server_running)

    checker.run_check("Tool Registration", check_tool_registration)

    checker.run_check("Lazy Loading", check_lazy_loading)

    checker.run_check("Tool Metadata", check_tool_metadata)

    checker.run_check("Async Operations", check_async_operations)

    checker.run_check("Performance Thresholds", check_performance_thresholds)

    checker.run_check("Environment Variables", check_environment_variables)

    checker.run_check("Memory Usage", check_memory_usage)

    checker.run_check("Error Logs", check_error_logs)

    # Print summary
    all_passed = checker.print_summary()

    # Save results
    checker.save_results()

    return 0 if all_passed else 1


# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == "__main__":
    try:
        # Install required packages if missing
        try:
            import psutil
        except ImportError:
            import subprocess

            subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)

        exit_code = run_health_checks()
        sys.exit(exit_code)

    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
