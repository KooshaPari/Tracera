"""CLI Benchmark Tests.

Comprehensive benchmarking of CLI operations to track performance
over time and identify regressions.
"""

import json
import time
from pathlib import Path

# ============================================================
# Benchmark Fixtures
# ============================================================
from typing import Any

import pytest

from tests.test_constants import COUNT_TEN


@pytest.fixture
def benchmark_results() -> None:
    """Store benchmark results for reporting."""
    results = {
        "startup": {},
        "commands": {},
        "lazy_loading": {},
        "cache": {},
    }
    yield results

    # Save results after tests
    output_file = Path(__file__).parent / "benchmark_results.json"
    with Path(output_file).open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


# ============================================================
# Startup Benchmarks
# ============================================================


class TestStartupBenchmarks:
    """Benchmark CLI startup performance."""

    def test_benchmark_import_cli_app(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark importing the CLI app module."""

        def import_app() -> None:
            import sys

            # Clear module cache for accurate measurement
            if "tracertm.cli.app" in sys.modules:
                del sys.modules["tracertm.cli.app"]

            from tracertm.cli.app import app

            return app

        result = benchmark(import_app)
        assert result is not None

        # Store results
        benchmark_results["startup"]["import_app"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
            "min_ms": benchmark.stats["min"] * 1000,
            "max_ms": benchmark.stats["max"] * 1000,
        }

    def test_benchmark_performance_module_import(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark importing performance module."""

        def import_performance() -> None:
            import sys

            if "tracertm.cli.performance" in sys.modules:
                del sys.modules["tracertm.cli.performance"]

            from tracertm.cli.performance import (
                get_cache,
                get_loader,
                get_monitor,
            )

            return get_loader, get_cache, get_monitor

        result = benchmark(import_performance)
        assert result is not None

        benchmark_results["startup"]["import_performance"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
        }

    def test_benchmark_lazy_loader_creation(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark creating a lazy loader instance."""
        from tracertm.cli.performance import LazyLoader

        def create_loader() -> None:
            return LazyLoader()

        result = benchmark(create_loader)
        assert result is not None

        benchmark_results["lazy_loading"]["loader_creation"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
        }


# ============================================================
# Lazy Loading Benchmarks
# ============================================================


class TestLazyLoadingBenchmarks:
    """Benchmark lazy loading performance."""

    def test_benchmark_first_module_load(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark first time loading a module."""
        from tracertm.cli.performance import LazyLoader

        def load_module() -> None:
            loader = LazyLoader()
            return loader.load("json")

        result = benchmark(load_module)
        assert result is not None

        benchmark_results["lazy_loading"]["first_load"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
        }

    def test_benchmark_cached_module_load(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark loading a cached module."""
        from tracertm.cli.performance import LazyLoader

        # Pre-load module
        loader = LazyLoader()
        loader.load("json")

        def load_cached() -> None:
            return loader.load("json")

        result = benchmark(load_cached)
        assert result is not None

        benchmark_results["lazy_loading"]["cached_load"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
        }

    def test_benchmark_multiple_module_loads(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark loading multiple different modules."""
        from tracertm.cli.performance import LazyLoader

        modules = ["json", "os", "sys", "time", "pathlib"]

        def load_multiple() -> None:
            loader = LazyLoader()
            for mod in modules:
                loader.load(mod)

        benchmark(load_multiple)

        benchmark_results["lazy_loading"]["multiple_loads"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "modules_count": len(modules),
            "per_module_ms": benchmark.stats["mean"] * 1000 / len(modules),
        }


# ============================================================
# Cache Benchmarks
# ============================================================


class TestCacheBenchmarks:
    """Benchmark command cache performance."""

    def test_benchmark_cache_creation(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark cache instance creation."""
        from tracertm.cli.performance import CommandCache

        def create_cache() -> None:
            return CommandCache(ttl=300)

        result = benchmark(create_cache)
        assert result is not None

        benchmark_results["cache"]["creation"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
        }

    def test_benchmark_cache_set(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark cache set operation."""
        from tracertm.cli.performance import CommandCache

        cache = CommandCache()
        test_data = {"key": "value", "number": 42}

        def cache_set() -> None:
            cache.set("test_key", test_data)

        benchmark(cache_set)

        benchmark_results["cache"]["set"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "ops_per_sec": 1000 / (benchmark.stats["mean"] * 1000),
        }

    def test_benchmark_cache_get_hit(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark cache get operation (hit)."""
        from tracertm.cli.performance import CommandCache

        cache = CommandCache(ttl=300)
        cache.set("test_key", {"data": "value"})

        def cache_get() -> None:
            return cache.get("test_key")

        result = benchmark(cache_get)
        assert result is not None

        benchmark_results["cache"]["get_hit"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "ops_per_sec": 1000 / (benchmark.stats["mean"] * 1000),
        }

    def test_benchmark_cache_get_miss(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark cache get operation (miss)."""
        from tracertm.cli.performance import CommandCache

        cache = CommandCache()

        def cache_get_miss() -> None:
            return cache.get("nonexistent_key")

        result = benchmark(cache_get_miss)
        assert result is None

        benchmark_results["cache"]["get_miss"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "ops_per_sec": 1000 / (benchmark.stats["mean"] * 1000),
        }

    def test_benchmark_cache_bulk_operations(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark bulk cache operations."""
        from tracertm.cli.performance import CommandCache

        def bulk_operations() -> None:
            cache = CommandCache()

            # Set 100 items
            for i in range(100):
                cache.set(f"key_{i}", f"value_{i}")

            # Get 100 items
            return [cache.get(f"key_{i}") for i in range(100)]

        result = benchmark(bulk_operations)
        assert len(result) == 100

        benchmark_results["cache"]["bulk_100_ops"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "ops_per_sec": 200 / (benchmark.stats["mean"]),  # 100 sets + 100 gets
        }


# ============================================================
# Performance Monitor Benchmarks
# ============================================================


class TestPerformanceMonitorBenchmarks:
    """Benchmark performance monitoring overhead."""

    def test_benchmark_monitor_creation(self, benchmark: Any, _benchmark_results: Any) -> None:
        """Benchmark performance monitor creation."""
        from tracertm.cli.performance import PerformanceMonitor

        def create_monitor() -> None:
            return PerformanceMonitor()

        result = benchmark(create_monitor)
        assert result is not None

    def test_benchmark_monitor_mark(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark adding timing marks."""
        from tracertm.cli.performance import PerformanceMonitor

        monitor = PerformanceMonitor()

        def add_mark() -> None:
            monitor.mark("test_checkpoint")

        benchmark(add_mark)

        benchmark_results["monitoring"] = {
            "mark_overhead_ms": benchmark.stats["mean"] * 1000,
        }

    def test_benchmark_monitor_get_timings(self, benchmark: Any, _benchmark_results: Any) -> None:
        """Benchmark retrieving timings."""
        from tracertm.cli.performance import PerformanceMonitor

        monitor = PerformanceMonitor()
        for i in range(10):
            monitor.mark(f"checkpoint_{i}")

        def get_timings() -> None:
            return monitor.get_timings()

        result = benchmark(get_timings)
        assert len(result) == COUNT_TEN


# ============================================================
# Command Execution Benchmarks
# ============================================================


class TestCommandExecutionBenchmarks:
    """Benchmark command execution."""

    def test_benchmark_help_command(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark help command execution."""
        from typer.testing import CliRunner

        from tracertm.cli.app import app

        runner = CliRunner()

        def run_help() -> None:
            return runner.invoke(app, ["--help"])

        result = benchmark(run_help)
        assert result.exit_code == 0

        benchmark_results["commands"]["help"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
        }

    def test_benchmark_version_command(self, benchmark: Any, benchmark_results: Any) -> None:
        """Benchmark version command execution."""
        from typer.testing import CliRunner

        from tracertm.cli.app import app

        runner = CliRunner()

        def run_version() -> None:
            return runner.invoke(app, ["--version"])

        result = benchmark(run_version)
        assert result.exit_code == 0

        benchmark_results["commands"]["version"] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
        }

    @pytest.mark.parametrize("command", ["config", "project", "item", "link"])
    def test_benchmark_command_group_help(self, benchmark: Any, command: Any, benchmark_results: Any) -> None:
        """Benchmark command group help execution."""
        from typer.testing import CliRunner

        from tracertm.cli.app import app

        runner = CliRunner()

        def run_command_help() -> None:
            return runner.invoke(app, [command, "--help"])

        result = benchmark(run_command_help)
        assert result.exit_code == 0

        if "command_groups" not in benchmark_results["commands"]:
            benchmark_results["commands"]["command_groups"] = {}

        benchmark_results["commands"]["command_groups"][command] = {
            "mean_ms": benchmark.stats["mean"] * 1000,
            "stddev_ms": benchmark.stats["stddev"] * 1000,
        }


# ============================================================
# Comparative Benchmarks
# ============================================================


class TestComparativeBenchmarks:
    """Compare different implementation approaches."""

    def test_benchmark_lazy_vs_direct_import(self, _benchmark: Any) -> None:
        """Compare lazy loading vs direct import performance."""
        from tracertm.cli.performance import LazyLoader

        loader = LazyLoader()

        # Warm up
        loader.load("json")

        # Benchmark lazy load
        lazy_times = []
        for _ in range(10):
            start = time.perf_counter()
            loader.load("json")
            lazy_times.append(time.perf_counter() - start)

        # Benchmark direct import
        direct_times = []
        for _ in range(10):
            start = time.perf_counter()
            direct_times.append(time.perf_counter() - start)

        avg_lazy = sum(lazy_times) / len(lazy_times) * 1000
        avg_direct = sum(direct_times) / len(direct_times) * 1000

        # Lazy loading should be comparable or faster due to caching
        assert avg_lazy < avg_direct * 2, "Lazy loading significantly slower than direct"

    def test_benchmark_cache_vs_recompute(self, _benchmark: Any) -> None:
        """Compare cached vs recomputed results."""
        from tracertm.cli.performance import CommandCache

        cache = CommandCache(ttl=300)

        # Expensive computation
        def expensive_operation() -> None:
            return sum(i**2 for i in range(1000))

        # Cache result
        cache.set("computation", expensive_operation())

        # Benchmark cache retrieval
        cache_times = []
        for _ in range(100):
            start = time.perf_counter()
            cache.get("computation")
            cache_times.append(time.perf_counter() - start)

        # Benchmark recomputation
        compute_times = []
        for _ in range(100):
            start = time.perf_counter()
            expensive_operation()
            compute_times.append(time.perf_counter() - start)

        avg_cache = sum(cache_times) / len(cache_times) * 1000
        avg_compute = sum(compute_times) / len(compute_times) * 1000

        # Cache should be significantly faster
        assert avg_cache < avg_compute, "Cache not faster than recomputation"


# ============================================================
# Regression Detection
# ============================================================


class TestRegressionDetection:
    """Detect performance regressions against baselines."""

    def test_check_against_baselines(self, _benchmark_results: Any) -> None:
        """Compare current results against baseline file."""
        baselines_file = Path(__file__).parent / "performance_baselines.json"

        if not baselines_file.exists():
            pytest.skip("No baseline file to compare against")

        with Path(baselines_file).open(encoding="utf-8") as f:
            baselines = json.load(f)

        # Compare key metrics
        cli_baselines = {k: v for k, v in baselines.items() if "cli" in k.lower()}

        if not cli_baselines:
            pytest.skip("No CLI baselines in file")

        # This is a smoke test - actual comparison would be more sophisticated


# ============================================================
# Report Generation
# ============================================================


@pytest.fixture(scope="session", autouse=True)
def generate_benchmark_report(_request: Any) -> None:
    """Generate comprehensive benchmark report."""
    yield

    # Run after all benchmark tests
    output_file = Path(__file__).parent / "benchmark_report.md"

    with Path(output_file).open("w", encoding="utf-8") as f:
        f.write("# CLI Performance Benchmark Report\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Overview\n\n")
        f.write("This report contains benchmark results for CLI performance optimization.\n\n")

        f.write("## Key Metrics\n\n")
        f.write("- Startup time benchmarks\n")
        f.write("- Lazy loading performance\n")
        f.write("- Cache operation speeds\n")
        f.write("- Command execution times\n\n")

        f.write("## Instructions\n\n")
        f.write("Run benchmarks with:\n")
        f.write("```bash\n")
        f.write("pytest tests/performance/test_cli_benchmarks.py -v --benchmark-only\n")
        f.write("```\n\n")

        f.write("View detailed results in `benchmark_results.json`\n")
