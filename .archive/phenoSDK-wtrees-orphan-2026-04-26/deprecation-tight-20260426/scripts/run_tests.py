#!/usr/bin/env python3
"""
Comprehensive test runner for all test suites.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any


class TestRunner:
    """Comprehensive test runner."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def run_all_tests(self, parallel: bool = True, coverage: bool = True) -> dict[str, Any]:
        """Run all test suites."""
        results = {}

        test_suites = [
            ("unit", "tests/unit", ["unit", "fast"]),
            ("integration", "tests/integration", ["integration"]),
            ("e2e", "tests/e2e", ["e2e"]),
            ("security", "tests/security", ["security"]),
            ("performance", "tests/performance", ["performance"]),
            ("contract", "tests/contract", ["contract"]),
        ]

        for suite_name, suite_path, markers in test_suites:
            print(f"Running {suite_name} tests...")
            result = self._run_test_suite(suite_name, suite_path, markers, parallel, coverage)
            results[suite_name] = result

        return results

    def run_specific_suite(self, suite_name: str, parallel: bool = True) -> dict[str, Any]:
        """Run a specific test suite."""
        suite_configs = {
            "unit": ("tests/unit", ["unit", "fast"]),
            "integration": ("tests/integration", ["integration"]),
            "e2e": ("tests/e2e", ["e2e"]),
            "security": ("tests/security", ["security"]),
            "performance": ("tests/performance", ["performance"]),
            "contract": ("tests/contract", ["contract"]),
        }

        if suite_name not in suite_configs:
            raise ValueError(f"Unknown test suite: {suite_name}")

        suite_path, markers = suite_configs[suite_name]
        return self._run_test_suite(suite_name, suite_path, markers, parallel, True)

    def _run_test_suite(self, suite_name: str, suite_path: str, markers: list[str],
                       parallel: bool, coverage: bool) -> dict[str, Any]:
        """Run a specific test suite."""
        cmd = ["python", "-m", "pytest", suite_path, "-v"]

        if parallel:
            cmd.extend(["-n", "auto"])

        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
                "--cov-report=json:coverage.json",
            ])

        # Add markers
        if markers:
            marker_str = " or ".join(markers)
            cmd.extend(["-m", marker_str])

        # Add reporting
        cmd.extend([
            "--html=reports/test-report.html",
            "--self-contained-html",
            "--junitxml=reports/junit.xml",
        ])

        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, cwd=self.project_root)
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except Exception as e:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
            }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive test runner")
    parser.add_argument("--suite", help="Specific test suite to run")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")

    args = parser.parse_args()

    runner = TestRunner(".")

    if args.suite:
        results = runner.run_specific_suite(args.suite, not args.no_parallel)
    else:
        results = runner.run_all_tests(not args.no_parallel, not args.no_coverage)

    # Print summary
    for suite_name, result in results.items():
        status = "PASSED" if result["success"] else "FAILED"
        print(f"{suite_name}: {status}")

    # Exit with error code if any tests failed
    if any(not result["success"] for result in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
