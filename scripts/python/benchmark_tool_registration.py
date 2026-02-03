#!/usr/bin/env python3
"""
Benchmark tool registration performance before and after optimization.

This script measures the time to import MCP server components and compares
the optimized split-module approach against the monolithic param.py.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def clear_mcp_imports():
    """Remove all MCP-related imports from sys.modules."""
    to_remove = [k for k in sys.modules if "tracertm.mcp" in k or "fastmcp" in k]
    for mod in to_remove:
        del sys.modules[mod]


def benchmark_monolithic():
    """Benchmark monolithic param.py import."""
    clear_mcp_imports()

    start = time.perf_counter()
    try:
        from tracertm.mcp.tools import param  # noqa: F401

        elapsed = time.perf_counter() - start
        return elapsed * 1000  # Convert to ms
    except Exception as e:
        print(f"Error importing monolithic param.py: {e}")
        return None


def benchmark_split_modules():
    """Benchmark split module imports."""
    clear_mcp_imports()

    start = time.perf_counter()
    try:
        # Import all split modules
        from tracertm.mcp.tools.params import (
            agent,  # noqa: F401
            config,  # noqa: F401
            database,  # noqa: F401
            graph,  # noqa: F401
            io_operations,  # noqa: F401
            item,  # noqa: F401
            link,  # noqa: F401
            project,  # noqa: F401
            query_test,  # noqa: F401
            specification,  # noqa: F401
            storage,  # noqa: F401
            system,  # noqa: F401
            trace,  # noqa: F401
            ui,  # noqa: F401
        )

        elapsed = time.perf_counter() - start
        return elapsed * 1000  # Convert to ms
    except Exception as e:
        print(f"Error importing split modules: {e}")
        import traceback

        traceback.print_exc()
        return None


def benchmark_server_import():
    """Benchmark full server import."""
    clear_mcp_imports()

    start = time.perf_counter()
    try:
        from tracertm.mcp import server  # noqa: F401

        elapsed = time.perf_counter() - start
        return elapsed * 1000  # Convert to ms
    except Exception as e:
        print(f"Error importing server: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    """Run benchmarks and report results."""
    print("=" * 70)
    print("MCP Tool Registration Performance Benchmark")
    print("=" * 70)
    print()

    # Run each benchmark multiple times for accuracy
    num_runs = 5

    print(f"Running {num_runs} iterations of each benchmark...")
    print()

    # Benchmark monolithic
    print("1. Monolithic param.py import:")
    monolithic_times = []
    for i in range(num_runs):
        time_ms = benchmark_monolithic()
        if time_ms:
            monolithic_times.append(time_ms)
            print(f"   Run {i + 1}: {time_ms:.2f}ms")

    # Benchmark split modules
    print()
    print("2. Split modules import:")
    split_times = []
    for i in range(num_runs):
        time_ms = benchmark_split_modules()
        if time_ms:
            split_times.append(time_ms)
            print(f"   Run {i + 1}: {time_ms:.2f}ms")

    # Benchmark full server
    print()
    print("3. Full server import (optimized):")
    server_times = []
    for i in range(num_runs):
        time_ms = benchmark_server_import()
        if time_ms:
            server_times.append(time_ms)
            print(f"   Run {i + 1}: {time_ms:.2f}ms")

    # Calculate statistics
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    if monolithic_times:
        mono_avg = sum(monolithic_times) / len(monolithic_times)
        print(f"Monolithic param.py: {mono_avg:.2f}ms (avg)")

    if split_times:
        split_avg = sum(split_times) / len(split_times)
        print(f"Split modules:       {split_avg:.2f}ms (avg)")

        if monolithic_times:
            improvement = ((mono_avg - split_avg) / mono_avg) * 100
            print(f"Improvement:         {improvement:.1f}%")

    if server_times:
        server_avg = sum(server_times) / len(server_times)
        print(f"\nFull server import:  {server_avg:.2f}ms (avg)")

        # Check if we met the <100ms target
        if server_avg < 100:
            print(f"\n✓ SUCCESS: Server import is {server_avg:.2f}ms < 100ms target!")
        else:
            print(f"\n✗ NEEDS WORK: Server import is {server_avg:.2f}ms > 100ms target")

    print("=" * 70)


if __name__ == "__main__":
    main()
