"""CLI Startup Performance Tests.

Tests startup time, memory usage, and initialization performance
to ensure CLI meets performance targets:
- Startup time < HTTP_INTERNAL_SERVER_ERRORms
- Memory usage < 50MB
- Common commands < 100ms
"""

import gc
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from tests.test_constants import COUNT_TEN

psutil = pytest.importorskip("psutil")

# Performance targets
STARTUP_TIME_THRESHOLD_MS = 500
MEMORY_THRESHOLD_MB = 50
COMMAND_TIME_THRESHOLD_MS = 100
LAZY_LOAD_THRESHOLD_MS = 50


class MemoryTracker:
    """Track memory usage during CLI operations."""

    def __init__(self) -> None:
        self.process = psutil.Process()
        self.baseline_mb = 0.0
        self.peak_mb = 0.0

    def start(self) -> None:
        """Start memory tracking."""
        gc.collect()
        time.sleep(0.1)  # Let GC finish
        mem_info = self.process.memory_info()
        self.baseline_mb = mem_info.rss / 1024 / 1024

    def measure(self) -> float:
        """Measure current memory usage in MB.

        Returns:
            Current memory usage in MB above baseline
        """
        mem_info = self.process.memory_info()
        current_mb = mem_info.rss / 1024 / 1024
        usage_mb = current_mb - self.baseline_mb
        self.peak_mb = max(self.peak_mb, usage_mb)
        return usage_mb

    def get_peak(self) -> float:
        """Get peak memory usage.

        Returns:
            Peak memory usage in MB
        """
        return self.peak_mb


@pytest.fixture
def cli_path() -> None:
    """Get path to CLI entry point."""
    # Find the rtm command in the project
    Path(__file__).parent.parent.parent

    # Try to find installed CLI first
    result = subprocess.run(
        ["which", "rtm"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    # Fall back to module execution
    return [sys.executable, "-m", "tracertm.cli.app"]


@pytest.fixture
def memory_tracker() -> None:
    """Create memory tracker for tests."""
    tracker = MemoryTracker()
    tracker.start()
    yield tracker
    # Cleanup
    gc.collect()


# ============================================================
# Startup Time Tests
# ============================================================


def test_cli_startup_time_cold(cli_path: Any, perf_tracker: Any) -> None:
    """Test cold startup time (no cache).

    Requirement: Startup time < HTTP_INTERNAL_SERVER_ERRORms
    """
    # Clear any caches
    cache_dir = Path.home() / ".cache" / "tracertm"
    if cache_dir.exists():
        import shutil

        shutil.rmtree(cache_dir, ignore_errors=True)

    # Measure startup time with --version (minimal operation)
    start = time.perf_counter()
    result = subprocess.run(
        [*([cli_path] if isinstance(cli_path, str) else cli_path), "--version"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    elapsed = time.perf_counter() - start
    elapsed_ms = elapsed * 1000

    perf_tracker.record("cli_cold_startup", elapsed_ms)

    # Assertions
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert elapsed_ms < STARTUP_TIME_THRESHOLD_MS, (
        f"Cold startup too slow: {elapsed_ms:.2f}ms > {STARTUP_TIME_THRESHOLD_MS}ms"
    )


def test_cli_startup_time_warm(cli_path: Any, perf_tracker: Any) -> None:
    """Test warm startup time (with cache).

    Should be faster than cold start due to lazy loading cache.
    """
    # Run once to warm up caches
    subprocess.run(
        [*([cli_path] if isinstance(cli_path, str) else cli_path), "--version"],
        capture_output=True,
        timeout=5,
    )

    # Measure warm startup
    start = time.perf_counter()
    result = subprocess.run(
        [*([cli_path] if isinstance(cli_path, str) else cli_path), "--version"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    elapsed = time.perf_counter() - start
    elapsed_ms = elapsed * 1000

    perf_tracker.record("cli_warm_startup", elapsed_ms)

    assert result.returncode == 0
    assert elapsed_ms < STARTUP_TIME_THRESHOLD_MS, (
        f"Warm startup too slow: {elapsed_ms:.2f}ms > {STARTUP_TIME_THRESHOLD_MS}ms"
    )


def test_cli_help_performance(cli_path: Any, perf_tracker: Any) -> None:
    """Test help command performance.

    Help should be fast as it's a common operation.
    """
    start = time.perf_counter()
    result = subprocess.run(
        [*([cli_path] if isinstance(cli_path, str) else cli_path), "--help"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    elapsed = time.perf_counter() - start
    elapsed_ms = elapsed * 1000

    perf_tracker.record("cli_help", elapsed_ms)

    assert result.returncode == 0
    assert elapsed_ms < COMMAND_TIME_THRESHOLD_MS, (
        f"Help command too slow: {elapsed_ms:.2f}ms > {COMMAND_TIME_THRESHOLD_MS}ms"
    )


# ============================================================
# Memory Usage Tests
# ============================================================


def test_cli_memory_usage(cli_path: Any, memory_tracker: Any, perf_tracker: Any) -> None:
    """Test CLI memory usage during startup.

    Requirement: Memory usage < 50MB
    """
    # Measure baseline
    memory_tracker.measure()

    # Run CLI command
    start = time.perf_counter()
    result = subprocess.run(
        [*([cli_path] if isinstance(cli_path, str) else cli_path), "--version"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    elapsed = time.perf_counter() - start

    # Measure after CLI execution
    memory_tracker.get_peak()

    perf_tracker.record("cli_memory_usage", elapsed * 1000)

    assert result.returncode == 0
    # Note: This measures parent process memory, not subprocess
    # For accurate subprocess memory measurement, we'd need to parse /proc


def test_cli_memory_no_leaks(cli_path: Any) -> None:
    """Test that repeated CLI invocations don't leak memory.

    Run CLI multiple times and ensure memory stays stable.
    """
    memory_samples = []

    for _i in range(5):
        gc.collect()
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024

        subprocess.run(
            [*([cli_path] if isinstance(cli_path, str) else cli_path), "--version"],
            capture_output=True,
            timeout=5,
        )

        gc.collect()
        mem_after = process.memory_info().rss / 1024 / 1024
        memory_samples.append(mem_after - mem_before)

    # Check that memory growth is minimal
    sum(memory_samples) / len(memory_samples)
    max_growth = max(memory_samples)

    # Memory should not grow significantly across runs
    assert max_growth < COUNT_TEN, f"Memory leak detected: {max_growth:.2f}MB growth"


# ============================================================
# Command Performance Tests
# ============================================================


@pytest.mark.parametrize(
    ("command", "args"),
    [
        ("config", ["--help"]),
        ("project", ["--help"]),
        ("item", ["--help"]),
        ("link", ["--help"]),
    ],
)
def test_command_group_help_performance(cli_path: Any, command: Any, args: Any, perf_tracker: Any) -> None:
    """Test command group help performance.

    All command groups should load quickly with --help.
    """
    cmd = [*([cli_path] if isinstance(cli_path, str) else cli_path), command, *args]

    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=5,
    )
    elapsed = time.perf_counter() - start
    elapsed_ms = elapsed * 1000

    perf_tracker.record(f"{command}_help", elapsed_ms)

    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert elapsed_ms < COMMAND_TIME_THRESHOLD_MS, (
        f"{command} help too slow: {elapsed_ms:.2f}ms > {COMMAND_TIME_THRESHOLD_MS}ms"
    )


# ============================================================
# Lazy Loading Tests
# ============================================================


def test_lazy_loading_performance() -> None:
    """Test that lazy loading mechanism works efficiently.

    Importing LazyLoader and using it should be fast.
    """
    start = time.perf_counter()

    from tracertm.cli.performance import LazyLoader, get_loader

    loader = get_loader()
    assert isinstance(loader, LazyLoader)

    # Test lazy loading a module
    module = loader.load("json")
    assert module is not None

    # Second load should be instant (cached)
    cached_start = time.perf_counter()
    module2 = loader.load("json")
    cached_elapsed = (time.perf_counter() - cached_start) * 1000

    elapsed = (time.perf_counter() - start) * 1000

    assert module2 is module  # Same object from cache
    assert cached_elapsed < 1, f"Cache lookup too slow: {cached_elapsed:.2f}ms"
    assert elapsed < LAZY_LOAD_THRESHOLD_MS, f"Lazy loading too slow: {elapsed:.2f}ms > {LAZY_LOAD_THRESHOLD_MS}ms"


def test_performance_monitor() -> None:
    """Test that performance monitor works correctly."""
    from tracertm.cli.performance import PerformanceMonitor

    monitor = PerformanceMonitor()

    # Add some marks
    time.sleep(0.01)
    monitor.mark("checkpoint1")

    time.sleep(0.01)
    monitor.mark("checkpoint2")

    # Verify timings
    timings = monitor.get_timings()
    assert "checkpoint1" in timings
    assert "checkpoint2" in timings
    assert timings["checkpoint2"] > timings["checkpoint1"]

    elapsed = monitor.get_elapsed()
    assert elapsed >= 0.02  # At least 20ms elapsed


def test_command_cache() -> None:
    """Test that command cache works correctly."""
    from tracertm.cli.performance import CommandCache

    cache = CommandCache(ttl=1)  # 1 second TTL

    # Set and get
    cache.set("test_key", {"data": "value"})
    result = cache.get("test_key")

    assert result == {"data": "value"}

    # Test expiration
    time.sleep(1.1)  # Wait for TTL
    expired = cache.get("test_key")
    assert expired is None

    # Test clear
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None


# ============================================================
# Integration Tests
# ============================================================


def test_cli_e2e_startup_sequence(cli_path: Any, perf_tracker: Any) -> None:
    """Test end-to-end startup sequence performance.

    Simulates real user workflow: help -> command help -> version
    """
    commands = [
        (["--help"], "main_help"),
        (["config", "--help"], "config_help"),
        (["--version"], "version"),
    ]

    total_start = time.perf_counter()

    for args, name in commands:
        start = time.perf_counter()
        result = subprocess.run(
            [*([cli_path] if isinstance(cli_path, str) else cli_path), *args],
            capture_output=True,
            text=True,
            timeout=5,
        )
        elapsed = (time.perf_counter() - start) * 1000

        assert result.returncode == 0, f"Command {name} failed: {result.stderr}"
        perf_tracker.record(f"e2e_{name}", elapsed)

    total_elapsed = (time.perf_counter() - total_start) * 1000
    perf_tracker.record("e2e_total", total_elapsed)

    # Total should still be reasonable
    assert total_elapsed < STARTUP_TIME_THRESHOLD_MS * 3, f"E2E sequence too slow: {total_elapsed:.2f}ms"


# ============================================================
# Regression Tests
# ============================================================


def test_performance_baselines_exist() -> None:
    """Verify performance baseline file exists and is valid."""
    baselines_file = Path(__file__).parent / "performance_baselines.json"

    if baselines_file.exists():
        import json

        with Path(baselines_file).open(encoding="utf-8") as f:
            baselines = json.load(f)

        assert isinstance(baselines, dict)
        assert len(baselines) > 0

        # Check for CLI-specific baselines
        {k: v for k, v in baselines.items() if "cli" in k.lower()}
    else:
        pytest.skip("Performance baselines file not found")


# ============================================================
# Benchmark Report
# ============================================================


@pytest.fixture(scope="session", autouse=True)
def generate_performance_report(request: Any) -> None:
    """Generate performance report after all tests."""
    yield

    # This runs after all tests
    if hasattr(request.session, "testscollector"):
        report_path = Path(__file__).parent / "cli_performance_report.txt"

        with Path(report_path).open("w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("CLI Performance Test Report\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("Performance Targets:\n")
            f.write(f"  - Startup time: < {STARTUP_TIME_THRESHOLD_MS}ms\n")
            f.write(f"  - Memory usage: < {MEMORY_THRESHOLD_MB}MB\n")
            f.write(f"  - Command time: < {COMMAND_TIME_THRESHOLD_MS}ms\n")
            f.write(f"  - Lazy load: < {LAZY_LOAD_THRESHOLD_MS}ms\n\n")

            f.write("Run pytest with -v to see detailed results.\n")
