#!/usr/bin/env python3
"""
Comprehensive Test Automation Suite
Orchestrates all testing activities and generates unified reports.
"""

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TestSuiteConfig:
    """Configuration for a test suite."""
    name: str
    command: list[str]
    timeout: int
    parallel: bool
    required: bool
    category: str


@dataclass
class TestExecutionResult:
    """Result of test execution."""
    suite_name: str
    status: str  # "pass", "fail", "timeout", "error"
    duration: float
    output: str
    error: str
    exit_code: int
    metrics: dict[str, Any] = None


class TestAutomationSuite:
    """Comprehensive test automation suite."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Define test suites
        self.test_suites = [
            TestSuiteConfig(
                name="unit_tests",
                command=["python", "-m", "pytest", "tests/unit", "-v", "--tb=short"],
                timeout=300,
                parallel=True,
                required=True,
                category="testing",
            ),
            TestSuiteConfig(
                name="integration_tests",
                command=["python", "-m", "pytest", "tests/integration", "-v", "--tb=short"],
                timeout=600,
                parallel=False,
                required=True,
                category="testing",
            ),
            TestSuiteConfig(
                name="e2e_tests",
                command=["python", "-m", "pytest", "tests/e2e", "-v", "--tb=short"],
                timeout=1200,
                parallel=False,
                required=False,
                category="testing",
            ),
            TestSuiteConfig(
                name="security_tests",
                command=["python", "-m", "pytest", "tests/security", "-v", "--tb=short"],
                timeout=300,
                parallel=True,
                required=True,
                category="security",
            ),
            TestSuiteConfig(
                name="performance_tests",
                command=["python", "scripts/performance_testing_framework.py", "."],
                timeout=1800,
                parallel=False,
                required=False,
                category="performance",
            ),
            TestSuiteConfig(
                name="documentation_tests",
                command=["python", "scripts/test_documentation.py", "."],
                timeout=300,
                parallel=True,
                required=True,
                category="documentation",
            ),
            TestSuiteConfig(
                name="code_quality",
                command=["python", "-m", "ruff", "check", "src/"],
                timeout=120,
                parallel=True,
                required=True,
                category="quality",
            ),
            TestSuiteConfig(
                name="type_checking",
                command=["python", "-m", "mypy", "src/"],
                timeout=300,
                parallel=True,
                required=True,
                category="quality",
            ),
            TestSuiteConfig(
                name="security_scanning",
                command=["python", "scripts/security_policy_enforcer.py", "."],
                timeout=600,
                parallel=True,
                required=True,
                category="security",
            ),
            TestSuiteConfig(
                name="architecture_validation",
                command=["python", "scripts/architectural_pattern_validator.py", "."],
                timeout=300,
                parallel=True,
                required=True,
                category="architecture",
            ),
        ]

    def run_all_tests(self, parallel: bool = True,
                     categories: list[str] | None = None) -> dict[str, Any]:
        """Run all test suites."""
        print("🚀 Running Comprehensive Test Automation Suite...")

        # Filter test suites by category
        if categories:
            filtered_suites = [s for s in self.test_suites if s.category in categories]
        else:
            filtered_suites = self.test_suites

        print(f"📋 Running {len(filtered_suites)} test suites...")

        # Execute tests
        if parallel:
            results = self._run_tests_parallel(filtered_suites)
        else:
            results = self._run_tests_sequential(filtered_suites)

        # Generate comprehensive report
        report = self._generate_comprehensive_report(results)

        return report

    def run_specific_tests(self, test_names: list[str]) -> dict[str, Any]:
        """Run specific test suites."""
        print(f"🎯 Running specific tests: {', '.join(test_names)}")

        selected_suites = [s for s in self.test_suites if s.name in test_names]

        if not selected_suites:
            print(f"❌ No test suites found with names: {test_names}")
            return {"error": "No matching test suites found"}

        results = self._run_tests_sequential(selected_suites)
        return self._generate_comprehensive_report(results)

    def _run_tests_parallel(self, test_suites: list[TestSuiteConfig]) -> list[TestExecutionResult]:
        """Run test suites in parallel."""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tests
            future_to_suite = {
                executor.submit(self._run_single_test, suite): suite
                for suite in test_suites
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_suite):
                suite = future_to_suite[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ {suite.name}: {result.status}")
                except Exception as e:
                    print(f"❌ {suite.name}: Error - {e}")
                    results.append(TestExecutionResult(
                        suite_name=suite.name,
                        status="error",
                        duration=0,
                        output="",
                        error=str(e),
                        exit_code=1,
                    ))

        return results

    def _run_tests_sequential(self, test_suites: list[TestSuiteConfig]) -> list[TestExecutionResult]:
        """Run test suites sequentially."""
        results = []

        for suite in test_suites:
            print(f"🔄 Running {suite.name}...")
            result = self._run_single_test(suite)
            results.append(result)

            status_emoji = "✅" if result.status == "pass" else "❌"
            print(f"{status_emoji} {suite.name}: {result.status} ({result.duration:.1f}s)")

            # Stop on required test failure
            if suite.required and result.status != "pass":
                print(f"🛑 Stopping due to required test failure: {suite.name}")
                break

        return results

    def _run_single_test(self, suite: TestSuiteConfig) -> TestExecutionResult:
        """Run a single test suite."""
        start_time = time.time()

        try:
            # Run the test command
            result = subprocess.run(
                suite.command,
                check=False, cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=suite.timeout,
            )

            duration = time.time() - start_time

            # Determine status
            if result.returncode == 0:
                status = "pass"
            elif result.returncode == 124:  # Timeout
                status = "timeout"
            else:
                status = "fail"

            # Extract metrics from output
            metrics = self._extract_metrics(result.stdout, suite.name)

            return TestExecutionResult(
                suite_name=suite.name,
                status=status,
                duration=duration,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                metrics=metrics,
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestExecutionResult(
                suite_name=suite.name,
                status="timeout",
                duration=duration,
                output="",
                error=f"Test timed out after {suite.timeout} seconds",
                exit_code=124,
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestExecutionResult(
                suite_name=suite.name,
                status="error",
                duration=duration,
                output="",
                error=str(e),
                exit_code=1,
            )

    def _extract_metrics(self, output: str, suite_name: str) -> dict[str, Any]:
        """Extract metrics from test output."""
        metrics = {}

        # Extract common metrics from pytest output
        if "pytest" in suite_name:
            lines = output.split("\n")
            for line in lines:
                if "passed" in line and "failed" in line:
                    # Extract test counts
                    import re
                    match = re.search(r"(\d+) passed.*?(\d+) failed", line)
                    if match:
                        metrics["passed"] = int(match.group(1))
                        metrics["failed"] = int(match.group(2))
                        metrics["total"] = metrics["passed"] + metrics["failed"]

                if "warnings" in line:
                    match = re.search(r"(\d+) warnings", line)
                    if match:
                        metrics["warnings"] = int(match.group(1))

        # Extract coverage metrics
        if "coverage" in output.lower():
            import re
            match = re.search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", output)
            if match:
                metrics["coverage_total"] = int(match.group(1))
                metrics["coverage_missing"] = int(match.group(2))
                metrics["coverage_percent"] = int(match.group(3))

        return metrics

    def _generate_comprehensive_report(self, results: list[TestExecutionResult]) -> dict[str, Any]:
        """Generate comprehensive test report."""
        # Calculate summary statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == "pass")
        failed_tests = sum(1 for r in results if r.status == "fail")
        timeout_tests = sum(1 for r in results if r.status == "timeout")
        error_tests = sum(1 for r in results if r.status == "error")

        # Calculate overall score
        if total_tests == 0:
            score = 100
        else:
            score = (passed_tests / total_tests) * 100

        # Group results by category
        categories = {}
        for result in results:
            # Find the category for this test
            suite_config = next((s for s in self.test_suites if s.name == result.suite_name), None)
            category = suite_config.category if suite_config else "unknown"

            if category not in categories:
                categories[category] = []
            categories[category].append(asdict(result))

        # Generate recommendations
        recommendations = self._generate_recommendations(results)

        # Create comprehensive report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "timeout": timeout_tests,
                "error": error_tests,
                "score": round(score, 1),
                "overall_status": "pass" if failed_tests == 0 and error_tests == 0 else "fail",
            },
            "categories": categories,
            "recommendations": recommendations,
            "execution_time": sum(r.duration for r in results),
            "detailed_results": [asdict(r) for r in results],
        }

        # Save report
        self._save_report(report)

        return report

    def _generate_recommendations(self, results: list[TestExecutionResult]) -> list[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Check for failed tests
        failed_tests = [r for r in results if r.status == "fail"]
        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failed test suites")

        # Check for timeout tests
        timeout_tests = [r for r in results if r.status == "timeout"]
        if timeout_tests:
            recommendations.append(f"Optimize {len(timeout_tests)} slow test suites")

        # Check for error tests
        error_tests = [r for r in results if r.status == "error"]
        if error_tests:
            recommendations.append(f"Fix {len(error_tests)} test suite errors")

        # Check for coverage issues
        coverage_results = [r for r in results if "coverage" in r.suite_name.lower()]
        for result in coverage_results:
            if result.metrics and result.metrics.get("coverage_percent", 100) < 80:
                recommendations.append(f"Improve test coverage (currently {result.metrics.get('coverage_percent', 0)}%)")

        # Check for performance issues
        performance_results = [r for r in results if "performance" in r.suite_name.lower()]
        for result in performance_results:
            if result.duration > 300:  # 5 minutes
                recommendations.append("Optimize performance test execution time")

        return recommendations

    def _save_report(self, report: dict[str, Any]) -> None:
        """Save test report to file."""
        # Save JSON report
        json_file = self.reports_dir / f"test_automation_report_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save human-readable report
        md_file = self.reports_dir / f"test_automation_report_{int(time.time())}.md"
        self._save_markdown_report(report, md_file)

        print("📊 Reports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Markdown: {md_file}")

    def _save_markdown_report(self, report: dict[str, Any], file_path: Path) -> None:
        """Save markdown report."""
        summary = report["summary"]

        content = f"""# Test Automation Report

**Generated**: {report['timestamp']}
**Execution Time**: {report['execution_time']:.1f} seconds

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {summary['total_tests']} |
| Passed | {summary['passed']} |
| Failed | {summary['failed']} |
| Timeout | {summary['timeout']} |
| Error | {summary['error']} |
| Score | {summary['score']}/100 |
| Status | {'✅ PASS' if summary['overall_status'] == 'pass' else '❌ FAIL'} |

## Test Results by Category

"""

        for category, tests in report["categories"].items():
            content += f"### {category.title()}\n\n"
            for test in tests:
                status_emoji = "✅" if test["status"] == "pass" else "❌"
                content += f"- {status_emoji} **{test['suite_name']}**: {test['status']} ({test['duration']:.1f}s)\n"
            content += "\n"

        if report["recommendations"]:
            content += "## Recommendations\n\n"
            for rec in report["recommendations"]:
                content += f"- {rec}\n"
            content += "\n"

        with open(file_path, "w") as f:
            f.write(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive Test Automation Suite")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--categories", nargs="+", help="Test categories to run")
    parser.add_argument("--tests", nargs="+", help="Specific test suites to run")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    suite = TestAutomationSuite(args.project_root)

    try:
        if args.tests:
            report = suite.run_specific_tests(args.tests)
        else:
            report = suite.run_all_tests(args.parallel, args.categories)

        # Print summary
        summary = report.get("summary", {})
        print("\n📊 Test Automation Summary:")
        print(f"  Total Tests: {summary.get('total_tests', 0)}")
        print(f"  Passed: {summary.get('passed', 0)}")
        print(f"  Failed: {summary.get('failed', 0)}")
        print(f"  Score: {summary.get('score', 0)}/100")
        print(f"  Status: {'✅ PASS' if summary.get('overall_status') == 'pass' else '❌ FAIL'}")

        # Exit with error code if tests failed
        if summary.get("overall_status") != "pass":
            print("\n❌ Some tests failed!")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
