#!/usr/bin/env python3
"""Benchmark tool registration performance before and after optimization.

This script measures the time to import MCP server components and compares
the optimized split-module approach against the monolithic param.py.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def clear_mcp_imports() -> None:
    """Remove all MCP-related imports from sys.modules."""
    to_remove = [k for k in sys.modules if "tracertm.mcp" in k or "fastmcp" in k]
    for mod in to_remove:
        del sys.modules[mod]


def benchmark_monolithic() -> float | None:
    """Benchmark monolithic param.py import."""
    clear_mcp_imports()

    start = time.perf_counter()
    try:
        from tracertm.mcp.tools import param

        _ = param  # ensure import is not optimized away
        elapsed = time.perf_counter() - start
        return elapsed * 1000  # Convert to ms
    except Exception:
        return None


def benchmark_split_modules() -> float | None:
    """Benchmark split module imports."""
    clear_mcp_imports()

    start = time.perf_counter()
    try:
        # Import all split modules
        from tracertm.mcp.tools.params import (
            agent,
            config,
            database,
            graph,
            io_operations,
            item,
            link,
            project,
            query_test,
            specification,
            storage,
            system,
            trace,
            ui,
        )

        # Ensure imports are not optimized away
        _ = (
            agent,
            config,
            database,
            graph,
            io_operations,
            item,
            link,
            project,
            query_test,
            specification,
            storage,
            system,
            trace,
            ui,
        )
        elapsed = time.perf_counter() - start
        return elapsed * 1000  # Convert to ms
    except Exception:
        import traceback

        traceback.print_exc()
        return None


def benchmark_server_import() -> float | None:
    """Benchmark full server import."""
    clear_mcp_imports()

    start = time.perf_counter()
    try:
        from tracertm.mcp import server

        _ = server  # ensure import is not optimized away
        elapsed = time.perf_counter() - start
        return elapsed * 1000  # Convert to ms
    except Exception:
        import traceback

        traceback.print_exc()
        return None


def main() -> None:
    """Run benchmarks and report results."""
    # Run each benchmark multiple times for accuracy
    num_runs = 5

    # Benchmark monolithic
    monolithic_times = []
    for _i in range(num_runs):
        time_ms = benchmark_monolithic()
        if time_ms:
            monolithic_times.append(time_ms)

    # Benchmark split modules
    split_times = []
    for _i in range(num_runs):
        time_ms = benchmark_split_modules()
        if time_ms:
            split_times.append(time_ms)

    # Benchmark full server
    server_times = []
    for _i in range(num_runs):
        time_ms = benchmark_server_import()
        if time_ms:
            server_times.append(time_ms)

    # Calculate statistics

    if monolithic_times:
        mono_avg = sum(monolithic_times) / len(monolithic_times)

    if split_times:
        split_avg = sum(split_times) / len(split_times)

        if monolithic_times:
            ((mono_avg - split_avg) / mono_avg) * 100

    if server_times:
        server_avg = sum(server_times) / len(server_times)

        # Check if we met the <100ms target
        if server_avg < 100:
            pass


if __name__ == "__main__":
    main()
