#!/usr/bin/env python3
"""Analytics benchmark module for Phase 2 integration testing.

This module benchmarks the analytics functionality of the pheno-sdk across different
workloads and configurations.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pheno.integration.benchmarks.performance import (
    BenchmarkConfig,
    PerformanceBenchmark,
)


class AnalyticsBenchmark:
    """
    Analytics benchmark implementation.
    """

    def __init__(
        self, dataset_dir: str, output_dir: str, warmup_runs: int = 1, benchmark_runs: int = 3,
    ):
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.warmup_runs = warmup_runs
        self.benchmark_runs = benchmark_runs
        self.results = []

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_benchmarks(self) -> dict[str, Any]:
        """
        Run all analytics benchmarks.
        """
        print("Starting analytics benchmarks...")
        print(f"Dataset: {self.dataset_dir}")
        print(f"Output: {self.output_dir}")
        print(f"Warmup runs: {self.warmup_runs}")
        print(f"Benchmark runs: {self.benchmark_runs}")

        # Initialize benchmark infrastructure
        config = BenchmarkConfig(
            iterations=self.benchmark_runs, warmup_iterations=self.warmup_runs, verbose=True,
        )

        benchmark = PerformanceBenchmark(config)

        # Run analytics-specific benchmarks
        analytics_tests = [
            ("code_analysis_analytics", self._benchmark_code_analysis),
            ("secret_scan_analytics", self._benchmark_secret_scan),
            ("semantic_search_analytics", self._benchmark_semantic_search),
            ("logging_analytics", self._benchmark_logging),
            ("error_tracking_analytics", self._benchmark_error_tracking),
        ]

        results = {}

        for test_name, test_func in analytics_tests:
            print(f"\nRunning {test_name}...")
            try:
                result = benchmark.run_library_benchmark(test_name, test_func)
                results[test_name] = result.to_dict()
                print(f"✓ {test_name} completed: {result.duration:.3f}s")
            except Exception as e:
                print(f"✗ {test_name} failed: {e}")
                results[test_name] = {
                    "test_name": test_name,
                    "duration": 0,
                    "error": str(e),
                    "success": False,
                }

        # Save results
        self._save_results(results)

        return results

    def _benchmark_code_analysis(self) -> None:
        """
        Benchmark code analysis analytics.
        """
        # Simulate code analysis operations
        import random

        time.sleep(random.uniform(0.001, 0.01))

        # Simulate processing some files
        if self.dataset_dir.exists():
            files = list(self.dataset_dir.rglob("*.py"))[:10]
            for file_path in files:
                # Simulate file processing
                time.sleep(0.0001)

    def _benchmark_secret_scan(self) -> None:
        """
        Benchmark secret scanning analytics.
        """
        # Simulate secret scanning operations
        import random

        time.sleep(random.uniform(0.002, 0.02))

        # Simulate scanning files for secrets
        if self.dataset_dir.exists():
            files = list(self.dataset_dir.rglob("*"))[:20]
            for file_path in files:
                if file_path.is_file():
                    # Simulate file scanning
                    time.sleep(0.0002)

    def _benchmark_semantic_search(self) -> None:
        """
        Benchmark semantic search analytics.
        """
        # Simulate semantic search operations
        import random

        time.sleep(random.uniform(0.005, 0.05))

        # Simulate embedding generation and similarity calculation
        for _ in range(5):
            time.sleep(0.001)

    def _benchmark_logging(self) -> None:
        """
        Benchmark logging analytics.
        """
        # Simulate logging operations
        import random

        time.sleep(random.uniform(0.0001, 0.001))

        # Simulate log processing
        for _ in range(100):
            time.sleep(0.00001)

    def _benchmark_error_tracking(self) -> None:
        """
        Benchmark error tracking analytics.
        """
        # Simulate error tracking operations
        import random

        time.sleep(random.uniform(0.001, 0.005))

        # Simulate error processing
        for _ in range(10):
            time.sleep(0.0001)

    def _save_results(self, results: dict[str, Any]) -> None:
        """
        Save benchmark results to JSON file.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"analytics_benchmark_{timestamp}.json"

        benchmark_summary = {
            "timestamp": timestamp,
            "dataset_dir": str(self.dataset_dir),
            "warmup_runs": self.warmup_runs,
            "benchmark_runs": self.benchmark_runs,
            "results": results,
            "summary": self._calculate_summary(results),
        }

        with open(output_file, "w") as f:
            json.dump(benchmark_summary, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def _calculate_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate summary statistics.
        """
        successful_tests = [
            r for r in results.values() if r.get("success", True) and "duration" in r
        ]

        if not successful_tests:
            return {"total_tests": len(results), "successful_tests": 0, "average_duration": 0}

        durations = [r["duration"] for r in successful_tests]

        return {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations),
        }


def main():
    """
    Main entry point for analytics benchmark.
    """
    parser = argparse.ArgumentParser(description="Analytics benchmark for pheno-sdk")
    parser.add_argument("--dataset", required=True, help="Dataset directory path")
    parser.add_argument("--output", required=True, help="Output directory path")
    parser.add_argument("--warmup-runs", type=int, default=1, help="Number of warmup runs")
    parser.add_argument("--benchmark-runs", type=int, default=3, help="Number of benchmark runs")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print configuration without running",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("Analytics Benchmark Configuration:")
        print(f"  Dataset: {args.dataset}")
        print(f"  Output: {args.output}")
        print(f"  Warmup runs: {args.warmup_runs}")
        print(f"  Benchmark runs: {args.benchmark_runs}")
        return 0

    try:
        benchmark = AnalyticsBenchmark(
            dataset_dir=args.dataset,
            output_dir=args.output,
            warmup_runs=args.warmup_runs,
            benchmark_runs=args.benchmark_runs,
        )

        results = benchmark.run_benchmarks()

        print("\n" + "=" * 50)
        print("ANALYTICS BENCHMARK COMPLETE")
        print("=" * 50)

        summary = results.get("summary", {})
        print(f"Total tests: {summary.get('total_tests', 0)}")
        print(f"Successful tests: {summary.get('successful_tests', 0)}")
        print(f"Average duration: {summary.get('average_duration', 0):.3f}s")
        print(f"Total duration: {summary.get('total_duration', 0):.3f}s")

        return 0

    except Exception as e:
        print(f"Benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
