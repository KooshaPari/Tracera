#!/usr/bin/env python3
"""Performance Comparison Script.

Compares current test results against baseline to detect regressions.
Fails if performance degradation exceeds threshold.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> dict[str, Any]:
    """Load JSON file."""
    with Path(file_path).open(encoding="utf-8") as f:
        return json.load(f)


def compare_metrics(baseline: dict, current: dict, threshold: float) -> tuple[bool, list]:
    """Compare metrics between baseline and current results.

    Args:
        baseline: Baseline metrics
        current: Current test metrics
        threshold: Maximum allowed degradation percentage

    Returns:
        Tuple of (passed, issues) where issues is list of regression messages
    """
    issues = []
    passed = True

    # Key metrics to compare
    metrics_to_check = {
        "http_req_duration": {
            "p95": "P95 Response Time",
            "p99": "P99 Response Time",
            "avg": "Average Response Time",
        },
        "http_req_failed": {
            "rate": "Error Rate",
        },
        "http_reqs": {
            "rate": "Request Rate",
        },
    }

    for metric_name, sub_metrics in metrics_to_check.items():
        if metric_name not in baseline.get("metrics", {}):
            continue

        baseline_metric = baseline["metrics"][metric_name]
        current_metric = current["metrics"].get(metric_name, {})

        for sub_key, label in sub_metrics.items():
            baseline_val = baseline_metric.get(sub_key)
            current_val = current_metric.get(sub_key)

            if baseline_val is None or current_val is None:
                continue

            # Calculate percentage change
            if baseline_val == 0:
                continue

            change_pct = ((current_val - baseline_val) / baseline_val) * 100

            # For error rates, any increase is bad
            # For response times, increase is bad
            # For request rates, decrease is bad
            if metric_name == "http_reqs":
                # Request rate - decrease is bad
                if change_pct < -threshold:
                    issues.append(
                        f"❌ {label} decreased by {abs(change_pct):.2f}% "
                        f"(baseline: {baseline_val:.2f}, current: {current_val:.2f})",
                    )
                    passed = False
                elif change_pct < 0:
                    issues.append(
                        f"⚠️  {label} decreased by {abs(change_pct):.2f}% "
                        f"(baseline: {baseline_val:.2f}, current: {current_val:.2f})",
                    )
            # Response time and error rate - increase is bad
            elif change_pct > threshold:
                issues.append(
                    f"❌ {label} increased by {change_pct:.2f}% "
                    f"(baseline: {baseline_val:.4f}, current: {current_val:.4f})",
                )
                passed = False
            elif change_pct > threshold / 2:
                issues.append(
                    f"⚠️  {label} increased by {change_pct:.2f}% "
                    f"(baseline: {baseline_val:.4f}, current: {current_val:.4f})",
                )

            # Also report improvements
            if metric_name == "http_reqs" and change_pct > 5:
                issues.append(
                    f"✅ {label} improved by {change_pct:.2f}% "
                    f"(baseline: {baseline_val:.2f}, current: {current_val:.2f})",
                )
            elif metric_name != "http_reqs" and change_pct < -5:
                issues.append(
                    f"✅ {label} improved by {abs(change_pct):.2f}% "
                    f"(baseline: {baseline_val:.4f}, current: {current_val:.4f})",
                )

    return passed, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare k6 test results against baseline")
    parser.add_argument("--baseline", type=Path, required=True, help="Path to baseline results JSON")
    parser.add_argument("--current", type=Path, required=True, help="Path to current test results JSON")
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Performance degradation threshold percentage (default: 10)",
    )
    parser.add_argument("--output", type=Path, help="Optional output file for comparison report")

    args = parser.parse_args()

    # Load results
    try:
        baseline = load_json(args.baseline)
        current = load_json(args.current)
    except FileNotFoundError:
        sys.exit(1)
    except json.JSONDecodeError:
        sys.exit(1)

    # Compare metrics
    passed, issues = compare_metrics(baseline, current, args.threshold)

    # Print results

    if issues:
        for _issue in issues:
            pass

    # Save report if output specified
    if args.output:
        report = {
            "baseline_file": str(args.baseline),
            "current_file": str(args.current),
            "threshold": args.threshold,
            "passed": passed,
            "issues": issues,
        }
        with Path(args.output).open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    # Exit with appropriate code
    if not passed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
