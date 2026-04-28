#!/usr/bin/env python3
"""Performance test runner script.

Provides utilities for running, analyzing, and comparing performance tests.

Usage:
    python run_performance_tests.py [options]

Examples:
    python run_performance_tests.py --baseline            # Establish baseline
    python run_performance_tests.py --compare             # Compare to baseline
    python run_performance_tests.py --profile database    # Run database tests
    python run_performance_tests.py --report              # Generate report
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class PerformanceTestRunner:
    """Run and manage performance tests."""

    def __init__(self, test_dir: Path) -> None:
        """Initialize runner.

        Args:
            test_dir: Path to performance tests directory
        """
        self.test_dir = test_dir
        self.baselines_file = test_dir / "performance_baselines.json"
        self.results_dir = test_dir / ".benchmarks"
        self.results_dir.mkdir(exist_ok=True)

    def run_baseline(self) -> bool:
        """Establish performance baseline."""
        cmd = [
            "pytest",
            str(self.test_dir),
            "-v",
            "--benchmark-only",
            "--benchmark-save=baseline",
            "--benchmark-min-rounds=10",
            "--benchmark-warmup=short",
        ]

        result = subprocess.run(cmd)

        return result.returncode == 0

    def run_regression_check(self) -> bool:
        """Check for performance regressions."""
        cmd = [
            "pytest",
            str(self.test_dir),
            "-v",
            "--benchmark-only",
            "--benchmark-compare=baseline",
            "--benchmark-compare-fail=mean:10%",
        ]

        result = subprocess.run(cmd)
        return result.returncode == 0

    def run_specific_suite(self, suite: str) -> bool:
        """Run specific test suite.

        Args:
            suite: Test suite name (database, bulk, concurrent)
        """
        suite_map = {
            "database": "test_database_performance.py",
            "bulk": "test_bulk_operations_performance.py",
            "concurrent": "test_concurrent_performance.py",
        }

        if suite not in suite_map:
            return False

        test_file = self.test_dir / suite_map[suite]

        cmd = [
            "pytest",
            str(test_file),
            "-v",
            "--benchmark-only",
        ]

        result = subprocess.run(cmd)
        return result.returncode == 0

    def generate_report(self) -> bool:
        """Generate performance report."""
        try:
            with Path(self.baselines_file).open(encoding="utf-8") as f:
                baselines = json.load(f)
        except FileNotFoundError:
            return False

        # Generate report
        report = self._create_report(baselines)

        # Save report
        report_file = self.test_dir / f"performance_report_{datetime.now().isoformat()}.txt"
        Path(report_file).write_text(report, encoding="utf-8")

        return True

    def _create_report(self, baselines: dict[str, Any]) -> str:
        """Create formatted performance report."""
        lines = [
            "Performance Baselines Report",
            "=" * 70,
            f"Generated: {datetime.now().isoformat()}",
            "",
        ]

        # Add metadata
        metadata = baselines.get("metadata", {})
        lines.extend([
            "Metadata:",
            f"  Version: {metadata.get('version', 'N/A')}",
            f"  Created: {metadata.get('created_date', 'N/A')}",
            f"  Notes: {metadata.get('notes', 'N/A')}",
            "",
        ])

        # Add baselines by category
        baselines_data = baselines.get("baselines", {})
        for category, operations in baselines_data.items():
            lines.extend((f"\n{category.upper()}", "-" * 70))

            for op_name, op_data in operations.items():
                lines.extend((f"\n  {op_name}:", f"    Operation: {op_data.get('operation', 'N/A')}"))

                # Add threshold
                if "threshold_ms" in op_data:
                    lines.append(f"    Threshold: {op_data['threshold_ms']}ms")
                elif "threshold_sec" in op_data:
                    lines.append(f"    Threshold: {op_data['threshold_sec']}s")

                # Add tolerance
                lines.append(f"    Tolerance: ±{op_data.get('tolerance_percent', 'N/A')}%")

                # Add throughput if available
                if "throughput_items_per_sec" in op_data:
                    lines.append(f"    Throughput: {op_data['throughput_items_per_sec']} items/sec")

                # Add notes
                if "notes" in op_data:
                    lines.append(f"    Notes: {op_data['notes']}")

        # Add performance tips
        lines.extend([
            "\n\nPerformance Tips:",
            "-" * 70,
        ])

        tips = baselines.get("performance_tips", [])
        for i, tip in enumerate(tips, 1):
            lines.append(f"{i}. {tip}")

        # Add regression thresholds
        lines.extend([
            "\n\nRegression Thresholds:",
            "-" * 70,
        ])

        thresholds = baselines.get("regression_thresholds", {})
        for level, percent in thresholds.items():
            lines.append(f"  {level.upper()}: >{percent}% degradation")

        return "\n".join(lines)

    def run_all_tests(self) -> bool:
        """Run all performance tests."""
        cmd = [
            "pytest",
            str(self.test_dir),
            "-v",
            "--benchmark-only",
        ]

        result = subprocess.run(cmd)
        return result.returncode == 0

    def list_tests(self) -> None:
        """List available tests."""
        test_files = [
            ("test_database_performance.py", "Database query performance"),
            ("test_bulk_operations_performance.py", "Bulk operations performance"),
            ("test_concurrent_performance.py", "Concurrent operations performance"),
        ]

        for filename, _description in test_files:
            test_path = self.test_dir / filename
            if test_path.exists():
                # Count tests in file
                with Path(test_path).open(encoding="utf-8") as f:
                    content = f.read()
                    content.count("def test_")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Performance test runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_performance_tests.py --baseline
    Establish performance baseline

  python run_performance_tests.py --compare
    Compare current performance to baseline

  python run_performance_tests.py --suite database
    Run only database performance tests

  python run_performance_tests.py --report
    Generate performance report

  python run_performance_tests.py --list
    List available tests
        """,
    )

    parser.add_argument("--baseline", action="store_true", help="Establish performance baseline")
    parser.add_argument("--compare", action="store_true", help="Compare to baseline (detect regressions)")
    parser.add_argument("--suite", choices=["database", "bulk", "concurrent"], help="Run specific test suite")
    parser.add_argument("--all", action="store_true", help="Run all performance tests")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    parser.add_argument("--list", action="store_true", help="List available tests")

    args = parser.parse_args()

    # Get test directory
    test_dir = Path(__file__).parent
    runner = PerformanceTestRunner(test_dir)

    # Handle commands
    if args.list:
        runner.list_tests()
        return 0

    if args.baseline:
        success = runner.run_baseline()
        return 0 if success else 1

    if args.compare:
        success = runner.run_regression_check()
        return 0 if success else 1

    if args.suite:
        success = runner.run_specific_suite(args.suite)
        return 0 if success else 1

    if args.all:
        success = runner.run_all_tests()
        return 0 if success else 1

    if args.report:
        success = runner.generate_report()
        return 0 if success else 1

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
