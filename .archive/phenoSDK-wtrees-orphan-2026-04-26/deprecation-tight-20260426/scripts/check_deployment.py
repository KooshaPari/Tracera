#!/usr/bin/env python3
"""
Deployment Readiness Checker Script Comprehensive pre-deployment validation.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.deployment_checker import CheckPriority, ReadinessChecker


def main():
    """
    Main deployment checker entry point.
    """
    parser = argparse.ArgumentParser(
        description="Check deployment readiness for ATOMS-PHENO project",
    )

    parser.add_argument(
        "--format", choices=["json", "markdown", "text"], default="text", help="Output format",
    )

    parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        action="append",
        help="Check priorities to run (can be specified multiple times)",
    )

    parser.add_argument("--check", help="Run specific check by name")

    parser.add_argument("--list-checks", action="store_true", help="List all available checks")

    parser.add_argument(
        "--parallel", action="store_true", default=True, help="Run checks in parallel",
    )

    parser.add_argument("--sequential", action="store_true", help="Run checks sequentially")

    parser.add_argument("--output-file", help="Write report to file")

    parser.add_argument("--project-dir", help="Project directory (default: current directory)")

    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Fail exit code on warnings (not just failures)",
    )

    args = parser.parse_args()

    # Create checker
    checker = ReadinessChecker(args.project_dir)

    # List checks if requested
    if args.list_checks:
        available_checks = list(checker._check_registry.keys())
        print("Available deployment readiness checks:")
        for i, check_name in enumerate(available_checks, 1):
            print(f"  {i:2d}. {check_name}")
        return 0

    # Determine priorities to run
    if args.priority:
        priority_map = {
            "critical": CheckPriority.CRITICAL,
            "high": CheckPriority.HIGH,
            "medium": CheckPriority.MEDIUM,
            "low": CheckPriority.LOW,
        }
        priorities = [priority_map[p] for p in args.priority]
    else:
        priorities = None  # Default to all

    # Run checks
    if args.check:
        # Run single check
        result = checker.run_check(args.check)
        results = [result] if result else []
    else:
        # Run all checks
        parallel = args.parallel and not args.sequential
        results = checker.run_all_checks(priorities=priorities, parallel=parallel)

    # Generate report
    report_format = args.format if args.format != "text" else "json"
    report = checker.generate_report(results, format=report_format)

    # Output report
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(report)
        print(f"Deployment readiness report written to {args.output_file}")
    elif args.format == "markdown":
        print(report)
    elif args.format == "json":
        print(json.dumps(json.loads(report), indent=2))
    else:
        # Summary for text output
        print("🚀 ATOMS-PHENO Deployment Readiness Check")
        print("=" * 50)

        total_checks = len(results)
        passed = sum(1 for r in results if r.status.value in ["passed", "PASSED"])
        failed = sum(1 for r in results if r.status.value in ["failed", "FAILED"])
        warnings = sum(1 for r in results if r.status.value in ["warning", "WARNING"])

        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")

        readiness_score = (passed / total_checks * 100) if total_checks > 0 else 0
        print(f"📊 Readiness Score: {readiness_score:.1f}%")

        # Determine if deployment is ready
        critical_failures = sum(
            1
            for r in results
            if r.priority == CheckPriority.CRITICAL and r.status.value in ["failed", "FAILED"]
        )

        if critical_failures == 0:
            print("\n🎉 DEPLOYMENT READY")
        else:
            print(f"\n🚫 DEPLOYMENT BLOCKED ({critical_failures} critical failures)")

        # Show individual results
        print("\nDetailed Results:")
        print("-" * 30)

        for result in results:
            status_emoji = {
                "passed": "✅",
                "PASSED": "✅",
                "failed": "❌",
                "FAILED": "❌",
                "warning": "⚠️",
                "WARNING": "⚠️",
                "error": "🚨",
                "ERROR": "🚨",
                "skipped": "⏭️",
                "SKIPPED": "⏭️",
            }.get(result.status.value, "❓")

            priority_badge = result.priority.value.upper()
            print(f"{status_emoji} {result.name} [{priority_badge}]")
            print(f"   {result.message}")

            if result.details:
                for key, value in result.details.items():
                    print(f"   {key}: {value}")

            if result.duration > 0:
                print(f"   Duration: {result.duration:.2f}s")
            print()

    # Determine exit code
    if args.fail_on_warning:
        has_issues = any(
            r.status.value in ["failed", "FAILED", "warning", "WARNING", "error", "ERROR"]
            for r in results
        )
    else:
        critical_failures = sum(
            1
            for r in results
            if r.priority == CheckPriority.CRITICAL and r.status.value in ["failed", "FAILED"]
        )
        has_issues = critical_failures > 0

    return 1 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main())
