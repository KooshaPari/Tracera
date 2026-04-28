#!/usr/bin/env python3
"""
Performance Benchmark Script for PhenoSDK

Measures startup time, memory usage, and runtime performance.
"""

import cProfile
import pstats
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def benchmark_startup():
    """Benchmark SDK startup time."""
    print("=" * 60)
    print("Benchmark: SDK Startup Time")
    print("=" * 60)
    
    times = []
    for i in range(10):
        start = time.perf_counter()
        
        # Clear any cached imports
        if "pheno_sdk" in sys.modules:
            del sys.modules["pheno_sdk"]
        if "pheno_sdk.core" in sys.modules:
            del sys.modules["pheno_sdk.core"]
        if "pheno_sdk.components" in sys.modules:
            del sys.modules["pheno_sdk.components"]
        
        # Import SDK
        from pheno_sdk import PhenoConfig, PhenoSDK
        
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"Run {i+1}: {elapsed*1000:.2f}ms")
    
    avg = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\nAverage: {avg*1000:.2f}ms")
    print(f"Min: {min_time*1000:.2f}ms")
    print(f"Max: {max_time*1000:.2f}ms")
    print()


def benchmark_config_validation():
    """Benchmark configuration validation."""
    print("=" * 60)
    print("Benchmark: Configuration Validation")
    print("=" * 60)
    
    from pheno_sdk import PhenoConfig
    from pheno_sdk.performance import clear_all_caches
    
    # Clear cache for fair comparison
    clear_all_caches()
    
    # First validation (no cache)
    start = time.perf_counter()
    config1 = PhenoConfig(
        project_name="test-project",
        stage="dev",
        region="us-east-1",
    )
    first_time = time.perf_counter() - start
    print(f"First validation (no cache): {first_time*1000:.2f}ms")
    
    # Second validation (cached)
    start = time.perf_counter()
    config2 = PhenoConfig(
        project_name="test-project",
        stage="dev",
        region="us-east-1",
    )
    cached_time = time.perf_counter() - start
    print(f"Second validation (cached): {cached_time*1000:.2f}ms")
    
    speedup = first_time / cached_time if cached_time > 0 else float('inf')
    print(f"Speedup: {speedup:.1f}x")
    print()


def benchmark_resource_creation():
    """Benchmark resource creation."""
    print("=" * 60)
    print("Benchmark: Resource Creation")
    print("=" * 60)
    
    from pheno_sdk import PhenoConfig, PhenoSDK
    
    config = PhenoConfig(
        project_name="benchmark",
        stage="dev",
        region="us-east-1",
    )
    
    times = []
    for i in range(10):
        sdk = PhenoSDK(config)
        
        start = time.perf_counter()
        resource = sdk.resource(f"test-{i}", "Bucket")
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"Resource {i+1}: {elapsed*1000:.2f}ms")
    
    avg = sum(times) / len(times)
    print(f"\nAverage: {avg*1000:.2f}ms")
    print()


def benchmark_cli_startup():
    """Benchmark CLI startup time."""
    print("=" * 60)
    print("Benchmark: CLI Startup Time")
    print("=" * 60)
    
    times = []
    for i in range(10):
        # Clear cached imports
        modules_to_clear = [
            "pheno_sdk.cli",
            "rich.console",
            "rich.panel",
            "rich.progress",
            "rich.table",
        ]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]
        
        start = time.perf_counter()
        from pheno_sdk.cli import app
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"Run {i+1}: {elapsed*1000:.2f}ms")
    
    avg = sum(times) / len(times)
    print(f"\nAverage: {avg*1000:.2f}ms")
    print()


def benchmark_cache_performance():
    """Benchmark cache performance."""
    print("=" * 60)
    print("Benchmark: Cache Performance")
    print("=" * 60)
    
    from pheno_sdk.performance import LRUCache
    
    cache = LRUCache(max_size=100)
    
    # Fill cache
    start = time.perf_counter()
    for i in range(100):
        cache.set(f"key_{i}", f"value_{i}")
    fill_time = time.perf_counter() - start
    print(f"Fill 100 items: {fill_time*1000:.2f}ms")
    
    # Read from cache
    start = time.perf_counter()
    for i in range(100):
        cache.get(f"key_{i}")
    read_time = time.perf_counter() - start
    print(f"Read 100 items: {read_time*1000:.2f}ms")
    
    # Cache stats
    stats = cache.stats()
    print(f"\nCache Stats:")
    print(f"  Size: {stats['size']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']}")
    print()


def profile_imports():
    """Profile import performance."""
    print("=" * 60)
    print("Profile: Import Performance")
    print("=" * 60)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Clear modules
    modules_to_clear = [
        "pheno_sdk",
        "pheno_sdk.core",
        "pheno_sdk.components",
        "pheno_sdk.cli",
    ]
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    # Import SDK
    from pheno_sdk import PhenoConfig, PhenoSDK
    from pheno_sdk.cli import app
    
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(20)  # Top 20 functions
    print()


def main():
    """Run all benchmarks."""
    print("\n" + "=" * 60)
    print("PhenoSDK Performance Benchmarks")
    print("=" * 60 + "\n")
    
    try:
        benchmark_startup()
        benchmark_config_validation()
        benchmark_resource_creation()
        benchmark_cli_startup()
        benchmark_cache_performance()
        profile_imports()
        
        print("=" * 60)
        print("All benchmarks completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error running benchmarks: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
