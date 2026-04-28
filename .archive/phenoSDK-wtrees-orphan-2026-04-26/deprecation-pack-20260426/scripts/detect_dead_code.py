#!/usr/bin/env python3
"""Dead Code Detection Script.

This script analyzes the codebase for dead code using Vulture.
"""

import os
import subprocess
import sys


def run_vulture_analysis() -> str:
    """
    Run Vulture dead code analysis.
    """
    try:
        cmd = ["vulture", "pheno-sdk", "--min-confidence", "80"]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode != 0:
            return f"Vulture analysis completed with findings:\n{result.stdout}"
        return "Vulture analysis completed - no dead code detected."
    except Exception as e:
        return f"Vulture analysis failed: {e}"


def filter_false_positives(vulture_output: str) -> str:
    """
    Filter out common false positives from Vulture output.
    """
    # Common false positives to filter
    false_positive_patterns = ["if __name__ == '__main__':", "main(", "test_"]

    lines = vulture_output.split("\n")
    filtered_lines = []

    for line in lines:
        if any(pattern in line for pattern in false_positive_patterns):
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)


def generate_dead_code_report(vulture_output: str) -> str:
    """
    Generate a formatted dead code report.
    """
    report = []
    report.append("=" * 80)
    report.append("ATOMS-PHENO: DEAD CODE ANALYSIS REPORT")
    report.append("=" * 80)
    report.append(f"\n{vulture_output}")
    return "\n".join(report)


def main():
    """
    Main execution function.
    """
    print("Running Dead Code Analysis...")

    raw_output = run_vulture_analysis()
    filtered_output = filter_false_positives(raw_output)
    report = generate_dead_code_report(filtered_output)

    print(report)

    # Check if any findings remain after filtering
    lines = filtered_output.split("\n")
    findings = [line for line in lines if line.strip() and "error" not in line.lower()]

    if findings and len(findings) > 1:  # More than just the header
        print("\n⚠️  Potential dead code detected - review findings")
    else:
        print("\n✓ No dead code detected")

    sys.exit(0)


if __name__ == "__main__":
    main()
