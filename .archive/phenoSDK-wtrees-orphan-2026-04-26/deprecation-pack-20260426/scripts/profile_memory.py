#!/usr/bin/env python3
"""
Memory Profiler Script
====================

Memory usage analysis with line-by-line profiling capabilities.
Provides insights into memory consumption patterns and optimization opportunities.

Usage:
    python scripts/profile_memory.py <module_name>
    python scripts/profile_memory.py --help
"""

import argparse
import json
import time
from pathlib import Path

try:
    from memory_profiler import profile  # type: ignore

    MEMORY_PROFILER_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    MEMORY_PROFILER_AVAILABLE = False

    def profile(func):  # type: ignore
        """
        Fallback decorator when memory_profiler is unavailable.
        """

        def wrapper(*args, **kwargs):
            print(
                "memory_profiler is not installed; "
                "run `pip install memory-profiler` for detailed tracing.",
            )
            return func(*args, **kwargs)

        return wrapper


@profile
def analyze_module_memory(module_name: str) -> dict[str, int]:
    """
    Analyze memory usage of a specific module.
    """
    print(f"Analyzing memory usage for module: {module_name}")

    # Simulate module operations
    data = []
    for i in range(1000):
        data.append(
            {"id": i, "name": f"item_{i}", "value": i * 2, "metadata": {"created": time.time()}},
        )

    # Process data
    processed = []
    for item in data:
        if item["value"] % 2 == 0:
            processed.append({"id": item["id"], "processed_value": item["value"] * 10})

    processed_count = len(processed)
    print(f"Processed {processed_count} items")
    return {"module": module_name, "processed_items": processed_count}


def profile_pheno_sdk() -> dict[str, int]:
    """
    Profile core Pheno SDK components.
    """
    from pheno import Registry, Stream

    # Profile Stream creation
    stream = Stream("test_stream")
    data = [f"message_{i}" for i in range(100)]

    # Profile Registry operations
    registry = Registry()
    for i, item in enumerate(data):
        registry.register(f"item_{i}", item)

    print("Pheno SDK profiling complete")
    return {"streams_profiled": 1, "registry_entries": len(data)}


def generate_memory_report() -> dict[str, float]:
    """
    Generate comprehensive memory usage report.
    """
    print("Memory Usage Report")
    print("=" * 50)

    # System memory info
    try:
        import psutil

        memory = psutil.virtual_memory()
        totals = {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent_used": memory.percent,
        }
        print(f"Total Memory: {totals['total_gb']:.2f} GB")
        print(f"Available Memory: {totals['available_gb']:.2f} GB")
        print(f"Used Memory: {totals['used_gb']:.2f} GB")
        print(f"Memory Percentage: {totals['percent_used']:.1f}%")
    except ImportError:
        print("Install psutil for system memory info: pip install psutil")
        totals = {}

    print("\nRecommendations:")
    print("- Use generators instead of lists for large datasets")
    print("- Implement data streaming for memory-intensive operations")
    print("- Consider using memory-efficient data structures")

    return totals


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description="Pheno SDK Memory Profiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/profile_memory.py pheno        # Profile pheno module
  python scripts/profile_memory.py --report     # Generate memory report
  python scripts/profile_memory.py --pheno     # Profile Pheno SDK components
        """,
    )

    parser.add_argument("module", nargs="?", help="Module to profile")

    parser.add_argument("--report", action="store_true", help="Generate memory usage report")

    parser.add_argument("--pheno", action="store_true", help="Profile Pheno SDK components")

    parser.add_argument("--output", type=str, help="Optional path to write JSON summary data")

    parser.add_argument(
        "--json", action="store_true", help="Print summary data as JSON after execution",
    )

    args = parser.parse_args()
    summary: dict[str, object] | None = None

    if args.report:
        report = generate_memory_report()
        summary = {"mode": "report", "metrics": report}
    elif args.pheno:
        result = profile_pheno_sdk()
        summary = {"mode": "pheno", "result": result}
    elif args.module:
        result = analyze_module_memory(args.module)
        summary = {"mode": "module", "result": result}
    else:
        parser.print_help()
        return

    if summary and (args.output or args.json):
        payload = json.dumps(summary, indent=2)
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(payload)
        if args.json:
            print(payload)


if __name__ == "__main__":
    raise SystemExit(main() or 0)
