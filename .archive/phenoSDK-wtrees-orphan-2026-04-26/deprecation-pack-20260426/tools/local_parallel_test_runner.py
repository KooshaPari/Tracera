#!/usr/bin/env python3
"""
Local Test Parallelization Runner
Execute tests locally with 4x parallelization for faster feedback
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any


class LocalParallelTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.test_configs = self._load_test_configs()

    def _load_test_configs(self) -> dict[str, Any]:
        return {
            "database_tier": {
                "processes": ["database_integration", "service_layer", "data_access"],
                "parallel_workers": 2,
                "command": "pytest tests/database_integration.py tests/test_services.py -n {workers}",
            },
            "api_tier": {
                "processes": ["api_endpoints", "auth_service", "business_logic"],
                "parallel_workers": 3,
                "command": "pytest tests/test_api_endpoints.py tests/test_auth.py -n {workers}",
            },
            "external_tier": {
                "processes": ["external_services", "api_client"],
                "parallel_workers": 2,
                "command": "pytest tests/external_services/ -n {workers}",
            },
            "unit_tier": {
                "processes": ["unit_tests", "utility_tests", "validation"],
                "parallel_workers": 3,
                "command": "pytest tests/unit/ tests/utils/ tests/validation/ -n {workers}",
            },
        }

    def run_parallel_tests(self, tiers: list[str] = None, workers: int = 4):
        """Run tests in parallel with specified tiers and worker count"""
        if tiers is None:
            tiers = list(self.test_configs.keys())

        print(f"🚀 starting parallel test execution with {workers} workers...")
        print(f"📋 Tiers to execute: {', '.join(tiers)}")

        # Execute tiers concurrently
        processes = []
        for tier in tiers:
            if tier in self.test_configs:
                config = self.test_configs[tier]
                cmd = config["command"].format(workers=workers)

                print(f"🔄 Launching {tier}: {' '.join(cmd.split())}")
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=self.project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                processes.append((tier, process))

        # Monitor and collect results
        results = {}
        for tier, process in processes:
            print(f"⏳ Waiting for {tier} to complete...")
            output, _ = process.communicate()

            results[tier] = {
                "exit_code": process.returncode,
                "output": output,
                "success": process.returncode == 0,
            }

            print(f"✅ {tier} completed with code {process.returncode}")

            if process.returncode != 0:
                print(f"❌ {tier} failed:")
                print(output)

        # Generate summary
        self._generate_summary(results, workers)
        return results

    def _generate_summary(self, results: dict[str, Any], workers: int):
        """Generate execution summary"""
        total_success = sum(1 for r in results.values() if r["success"])
        total_tiers = len(results)

        print("\n" + "="*60)
        print("🎯 PARALLEL TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"📊 Workers per tier: {workers}")
        print(f"✅ Success rate: {total_success}/{total_tiers}")
        print(f"🔄 Total tiers executed: {total_tiers}")
        print("="*60)

        for tier, result in results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{tier:20s} {status} (exit {result['exit_code']})")

        if total_success == total_tiers:
            print("\n🎉 All tests passed! Parallel execution completed successfully.")
        else:
            print(f"\n⚠️  {total_tiers - total_success} tests failed. Check output above.")

    def run_benchmark(self, iterations: int = 3):
        """Run benchmark comparison between sequential and parallel execution"""
        print(f"🔍 Starting benchmark over {iterations} iterations...")

        results = []

        for i in range(iterations):
            print(f"\n📈 Iteration {i+1}/{iterations}")

            # Sequential execution
            print("🐌 Running sequential tests...")
            start_time = time.time()
            subprocess.run("pytest tests/ -v", check=False, shell=True, cwd=self.project_root)
            sequential_time = time.time() - start_time

            # Parallel execution
            print("🚀 Running parallel tests...")
            start_time = time.time()
            self.run_parallel_tests()
            parallel_time = time.time() - start_time

            speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0

            results.append({
                "iteration": i + 1,
                "sequential_time": sequential_time,
                "parallel_time": parallel_time,
                "speedup": speedup,
            })

            print(f"⚡ Speedup achieved: {speedup:.2f}x")

        # Generate benchmark summary
        self._generate_benchmark_summary(results)

    def _generate_benchmark_summary(self, results: list[dict]):
        """Generate benchmark comparison summary"""
        avg_sequential = sum(r["sequential_time"] for r in results) / len(results)
        avg_parallel = sum(r["parallel_time"] for r in results) / len(results)
        avg_speedup = sum(r["speedup"] for r in results) / len(results)

        print("\n" + "="*60)
        print("📊 BENCHMARK COMPARISON SUMMARY")
        print("="*60)
        print(f"✅ Average sequential time: {avg_sequential:.2f}s")
        print(f"⚡ Average parallel time: {avg_parallel:.2f}s")
        print(f"🚀 Average speedup: {avg_speedup:.2f}x")
        print(f"📈 Speedup target: 4.0x (achieved {(avg_speedup/4.0)*100:.1f}%)")
        print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests in parallel for fast feedback")
    parser.add_argument("--tiers", nargs="+", help="Specific test tiers to run")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark comparison")
    args = parser.parse_args()

    runner = LocalParallelTestRunner()

    if args.benchmark:
        import time
        runner.run_benchmark()
    else:
        results = runner.run_parallel_tests(args.tiers, args.workers)
        sys.exit(0 if all(r["success"] for r in results.values()) else 1)
