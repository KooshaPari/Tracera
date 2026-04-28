#!/usr/bin/env python3
"""
Comprehensive test runner for all test suites.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class ComprehensiveTestRunner:
    """Comprehensive test runner for all test suites."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Test suite configurations
        self.test_suites = {
            "unit": {
                "path": "tests/unit",
                "markers": ["unit", "fast"],
                "coverage_target": 95.0,
                "timeout": 60,
                "parallel": True,
            },
            "integration": {
                "path": "tests/integration",
                "markers": ["integration"],
                "coverage_target": 85.0,
                "timeout": 300,
                "parallel": False,
            },
            "e2e": {
                "path": "tests/e2e",
                "markers": ["e2e"],
                "coverage_target": 80.0,
                "timeout": 600,
                "parallel": False,
            },
            "security": {
                "path": "tests/security",
                "markers": ["security"],
                "coverage_target": 90.0,
                "timeout": 180,
                "parallel": True,
            },
            "performance": {
                "path": "tests/performance",
                "markers": ["performance"],
                "coverage_target": 70.0,
                "timeout": 1200,
                "parallel": False,
            },
            "contract": {
                "path": "tests/contract",
                "markers": ["contract"],
                "coverage_target": 85.0,
                "timeout": 120,
                "parallel": True,
            },
        }

    def run_all_tests(self, parallel: bool = True, coverage: bool = True,
                     exclude_slow: bool = False) -> dict[str, Any]:
        """Run all test suites."""
        print("🧪 Running Comprehensive Test Suite...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_suites": len(self.test_suites),
            "suites": {},
            "summary": {},
        }

        total_tests = 0
        total_passed = 0
        total_failed = 0

        for suite_name, config in self.test_suites.items():
            print(f"\n📋 Running {suite_name} tests...")

            # Skip slow tests if requested
            if exclude_slow and config.get("markers", []) and "slow" in config["markers"]:
                print(f"⏭️  Skipping {suite_name} (slow tests excluded)")
                continue

            suite_result = self._run_test_suite(suite_name, config, parallel, coverage)
            results["suites"][suite_name] = suite_result

            # Update totals
            total_tests += suite_result.get("total_tests", 0)
            total_passed += suite_result.get("passed", 0)
            total_failed += suite_result.get("failed", 0)

        # Generate summary
        results["summary"] = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "overall_success": total_failed == 0,
        }

        # Save results
        self._save_results(results)

        return results

    def run_specific_suite(self, suite_name: str, parallel: bool = True,
                          coverage: bool = True) -> dict[str, Any]:
        """Run a specific test suite."""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")

        config = self.test_suites[suite_name]
        return self._run_test_suite(suite_name, config, parallel, coverage)

    def run_fast_tests_only(self) -> dict[str, Any]:
        """Run only fast tests."""
        print("⚡ Running Fast Tests Only...")

        fast_suites = {name: config for name, config in self.test_suites.items()
                      if "fast" in config.get("markers", [])}

        results = {
            "timestamp": datetime.now().isoformat(),
            "mode": "fast_only",
            "suites": {},
        }

        for suite_name, config in fast_suites.items():
            print(f"📋 Running {suite_name} tests...")
            suite_result = self._run_test_suite(suite_name, config, True, True)
            results["suites"][suite_name] = suite_result

        return results

    def _run_test_suite(self, suite_name: str, config: dict[str, Any],
                       parallel: bool, coverage: bool) -> dict[str, Any]:
        """Run a specific test suite."""
        suite_path = self.project_root / config["path"]

        if not suite_path.exists():
            return {
                "exists": False,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "success": True,
                "message": "Test directory does not exist",
            }

        # Build command
        cmd = ["python", "-m", "pytest", str(suite_path), "-v", "--tb=short"]

        # Add parallel execution
        if parallel and config.get("parallel", True):
            cmd.extend(["-n", "auto"])

        # Add coverage
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
                "--cov-report=json:coverage.json",
                f"--cov-fail-under={config.get('coverage_target', 80)}",
            ])

        # Add markers
        markers = config.get("markers", [])
        if markers:
            marker_str = " or ".join(markers)
            cmd.extend(["-m", marker_str])

        # Add reporting
        cmd.extend([
            f"--html=reports/{suite_name}-report.html",
            "--self-contained-html",
            f"--junitxml=reports/{suite_name}-junit.xml",
        ])

        # Add timeout
        timeout = config.get("timeout", 300)
        cmd.extend(["--timeout", str(timeout)])

        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=False, capture_output=True, text=True,
                                  cwd=self.project_root, timeout=timeout + 60)

            # Parse results
            return self._parse_test_results(result, suite_name)

        except subprocess.TimeoutExpired:
            return {
                "exists": True,
                "total_tests": 0,
                "passed": 0,
                "failed": 1,
                "success": False,
                "message": "Test suite timed out",
            }
        except Exception as e:
            return {
                "exists": True,
                "total_tests": 0,
                "passed": 0,
                "failed": 1,
                "success": False,
                "message": f"Error running tests: {e!s}",
            }

    def _parse_test_results(self, result: subprocess.CompletedProcess, suite_name: str) -> dict[str, Any]:
        """Parse test results from pytest output."""
        output = result.stdout

        # Extract test counts (basic parsing)
        lines = output.split("\n")
        total_tests = 0
        passed = 0
        failed = 0

        for line in lines:
            if "PASSED" in line:
                passed += 1
                total_tests += 1
            elif "FAILED" in line or "ERROR" in line:
                failed += 1
                total_tests += 1

        return {
            "exists": True,
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def _save_results(self, results: dict[str, Any]) -> None:
        """Save test results to file."""
        results_file = self.reports_dir / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        # Generate summary report
        self._generate_summary_report(results)

    def _generate_summary_report(self, results: dict[str, Any]) -> None:
        """Generate a human-readable summary report."""
        summary = results.get("summary", {})

        report = f"""
# Comprehensive Test Results Summary

**Timestamp**: {results.get('timestamp', 'Unknown')}
**Total Tests**: {summary.get('total_tests', 0)}
**Passed**: {summary.get('total_passed', 0)}
**Failed**: {summary.get('total_failed', 0)}
**Success Rate**: {summary.get('success_rate', 0):.1f}%
**Overall Success**: {'✅' if summary.get('overall_success', False) else '❌'}

## Test Suite Results

"""

        for suite_name, suite_result in results.get("suites", {}).items():
            if suite_result.get("exists", False):
                status = "✅" if suite_result.get("success", False) else "❌"
                report += f"### {suite_name.title()}\n"
                report += f"- **Status**: {status}\n"
                report += f"- **Tests**: {suite_result.get('total_tests', 0)}\n"
                report += f"- **Passed**: {suite_result.get('passed', 0)}\n"
                report += f"- **Failed**: {suite_result.get('failed', 0)}\n"
                if suite_result.get("message"):
                    report += f"- **Message**: {suite_result['message']}\n"
                report += "\n"

        # Save report
        report_file = self.reports_dir / "test_summary.md"
        with open(report_file, "w") as f:
            f.write(report)

        print(f"\n📊 Test summary saved to: {report_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive test runner")
    parser.add_argument("--suite", help="Specific test suite to run")
    parser.add_argument("--fast-only", action="store_true", help="Run only fast tests")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--exclude-slow", action="store_true", help="Exclude slow tests")

    args = parser.parse_args()

    runner = ComprehensiveTestRunner(".")

    try:
        if args.suite:
            results = runner.run_specific_suite(args.suite, not args.no_parallel, not args.no_coverage)
        elif args.fast_only:
            results = runner.run_fast_tests_only()
        else:
            results = runner.run_all_tests(not args.no_parallel, not args.no_coverage, args.exclude_slow)

        # Print summary
        summary = results.get("summary", {})
        print("\n📊 Test Summary:")
        print(f"  Total Tests: {summary.get('total_tests', 0)}")
        print(f"  Passed: {summary.get('total_passed', 0)}")
        print(f"  Failed: {summary.get('total_failed', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")

        # Exit with error code if any tests failed
        if not summary.get("overall_success", True):
            print("\n❌ Some tests failed!")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
