#!/usr/bin/env python3
"""Generate maintainability dashboard with current metrics.

Usage:
    python scripts/maintainability_dashboard.py

Requires:
    - radon (pip install radon)
    - pytest-cov (for coverage metrics)
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    """Run command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Warning: Command failed: {' '.join(cmd)}")
        return ""


def calculate_maintainability_score() -> float:
    """Calculate average maintainability index from radon."""
    output = run_command(["radon", "mi", "src/", "-s", "-j"])
    if not output:
        return 0.0

    try:
        data = json.loads(output)
        scores = []

        for file_data in data.values():
            if isinstance(file_data, dict) and "mi" in file_data:
                scores.append(file_data["mi"])

        return sum(scores) / len(scores) if scores else 0.0
    except (json.JSONDecodeError, KeyError, ZeroDivisionError):
        return 0.0


def count_files_over_limit(limit: int = 500) -> int:
    """Count Python files over line limit."""
    count = 0
    for file in Path("src").rglob("*.py"):
        if any(part in file.parts for part in ["migrations", "__pycache__"]):
            continue

        line_count = sum(1 for _ in file.open())
        if line_count > limit:
            count += 1

    return count


def count_low_grade_files() -> int:
    """Count files with B or C maintainability grade."""
    output = run_command(["radon", "mi", "src/", "-s"])
    if not output:
        return 0

    count = 0
    for line in output.split("\n"):
        if " - B " in line or " - C " in line:
            count += 1

    return count


def count_todos() -> int:
    """Count TODO/FIXME comments."""
    output = run_command([
        "grep", "-r", "-E",
        "TODO|FIXME|XXX|HACK",
        "src/",
        "--include=*.py"
    ])

    return len(output.split("\n")) if output else 0


def get_test_coverage() -> float:
    """Get test coverage percentage."""
    # Try to read from .coverage or pytest output
    coverage_file = Path(".coverage")
    if not coverage_file.exists():
        return 0.0

    # Run pytest with coverage
    output = run_command([
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--quiet"
    ])

    # Parse coverage from output
    for line in output.split("\n"):
        if "TOTAL" in line:
            parts = line.split()
            for part in parts:
                if "%" in part:
                    return float(part.rstrip("%"))

    return 0.0


def calculate_avg_complexity() -> float:
    """Calculate average cyclomatic complexity."""
    output = run_command(["radon", "cc", "src/", "-a", "-s"])
    if not output:
        return 0.0

    # Parse average from last line
    for line in reversed(output.split("\n")):
        if "Average complexity:" in line:
            parts = line.split("(")
            if len(parts) > 1:
                complexity_str = parts[1].split(")")[0]
                return float(complexity_str)

    return 0.0


def get_trend_indicator(current: float, previous: float) -> str:
    """Get trend indicator emoji."""
    if current > previous:
        return "📈"
    elif current < previous:
        return "📉"
    else:
        return "➡️"


def generate_dashboard():
    """Generate and display maintainability dashboard."""
    print("\n" + "="*50)
    print("  PHENO-SDK MAINTAINABILITY DASHBOARD")
    print("="*50 + "\n")

    # Gather metrics
    metrics = {
        "score": calculate_maintainability_score(),
        "large_files": count_files_over_limit(500),
        "target_files": count_files_over_limit(350),
        "low_grade": count_low_grade_files(),
        "todos": count_todos(),
        "coverage": get_test_coverage(),
        "complexity": calculate_avg_complexity(),
    }

    # Calculate normalized score (0-100)
    # Based on: MI score, file sizes, grades, TODOs, coverage
    normalized_score = min(100, max(0, (
        metrics["score"] * 0.4 +                    # 40% MI
        (100 - metrics["large_files"] * 2) * 0.2 +  # 20% file size
        (100 - metrics["low_grade"] * 5) * 0.15 +   # 15% grades
        (100 - metrics["todos"]) * 0.1 +            # 10% TODOs
        metrics["coverage"] * 0.15                  # 15% coverage
    )))

    # Display dashboard
    print("╔" + "="*48 + "╗")
    print("║" + " "*16 + "OVERALL SCORE" + " "*19 + "║")
    print("║" + " "*48 + "║")

    # Score with visual bar
    score_int = int(normalized_score)
    bar_length = int(score_int * 30 / 100)
    bar = "█" * bar_length + "░" * (30 - bar_length)

    print(f"║  {score_int:3d}/100  {bar}  ║")
    print("╠" + "="*48 + "╣")

    # Detailed metrics
    print("║" + " "*15 + "DETAILED METRICS" + " "*16 + "║")
    print("╠" + "="*48 + "╣")

    print(f"║  Maintainability Index    {metrics['score']:6.1f} / 100.0  ║")
    print(f"║  Files >500 LOC           {metrics['large_files']:6d} files    ║")
    print(f"║  Files >350 LOC (target)  {metrics['target_files']:6d} files    ║")
    print(f"║  Low Grade (B/C)          {metrics['low_grade']:6d} files    ║")
    print(f"║  TODO/FIXME Comments      {metrics['todos']:6d} items    ║")
    print(f"║  Test Coverage            {metrics['coverage']:6.1f}%         ║")
    print(f"║  Avg Complexity           {metrics['complexity']:6.2f}          ║")

    print("╠" + "="*48 + "╣")

    # Status indicators
    print("║" + " "*18 + "STATUS" + " "*23 + "║")
    print("╠" + "="*48 + "╣")

    # Determine status for each metric
    statuses = []

    if metrics["score"] >= 20:
        statuses.append(("Maintainability Index", "✅ Excellent"))
    else:
        statuses.append(("Maintainability Index", "⚠️  Needs work"))

    if metrics["large_files"] == 0:
        statuses.append(("File Size Compliance", "✅ Perfect"))
    elif metrics["large_files"] < 10:
        statuses.append(("File Size Compliance", "⚠️  Good"))
    else:
        statuses.append(("File Size Compliance", "❌ Needs work"))

    if metrics["low_grade"] == 0:
        statuses.append(("Code Quality Grades", "✅ All A-grade"))
    else:
        statuses.append(("Code Quality Grades", f"⚠️  {metrics['low_grade']} B/C files"))

    if metrics["todos"] == 0:
        statuses.append(("TODO Comments", "✅ None"))
    elif metrics["todos"] < 50:
        statuses.append(("TODO Comments", f"⚠️  {metrics['todos']} remaining"))
    else:
        statuses.append(("TODO Comments", f"❌ {metrics['todos']} items"))

    if metrics["coverage"] >= 90:
        statuses.append(("Test Coverage", "✅ Excellent"))
    elif metrics["coverage"] >= 80:
        statuses.append(("Test Coverage", "⚠️  Good"))
    else:
        statuses.append(("Test Coverage", "❌ Needs work"))

    # Display statuses
    for label, status in statuses:
        padding = " " * (24 - len(label))
        status_padding = " " * (20 - len(status))
        print(f"║  {label}{padding}{status}{status_padding}║")

    print("╚" + "="*48 + "╝\n")

    # Recommendations
    if normalized_score < 100:
        print("📋 RECOMMENDATIONS:\n")

        if metrics["large_files"] > 0:
            print(f"  • Decompose {metrics['large_files']} files over 500 lines")

        if metrics["low_grade"] > 0:
            print(f"  • Improve {metrics['low_grade']} files with B/C maintainability")

        if metrics["todos"] > 0:
            print(f"  • Resolve {metrics['todos']} TODO/FIXME comments")

        if metrics["coverage"] < 90:
            needed = 90 - metrics["coverage"]
            print(f"  • Increase test coverage by {needed:.1f}%")

        print()

    # Return normalized score for CI/CD
    return int(normalized_score)


def main() -> int:
    """Run dashboard and return score."""
    try:
        score = generate_dashboard()

        # Exit with appropriate code
        if score >= 90:
            return 0  # Success
        else:
            return 1  # Needs improvement

    except Exception as e:
        print(f"Error generating dashboard: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
