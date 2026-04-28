#!/usr/bin/env python3
"""Automated implementation script for all phases.

This script automates the implementation of all improvements across all phases.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Configuration
SRC_DIR = Path("src")
PRINT_PATTERN = re.compile(r'^\s*print\s*\(')
EXCEPTION_PATTERN = re.compile(r'except\s+Exception\s*:')
ANY_PATTERN = re.compile(r'->\s*Any\s*:')
HARDCODED_SECRET_PATTERN = re.compile(
    r'(password|secret|api_key|token|key)\s*=\s*["\']([^"\']+)["\']',
    re.IGNORECASE
)


def find_print_statements() -> List[Tuple[Path, int, str]]:
    """Find all print statements in codebase."""
    results = []
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if PRINT_PATTERN.search(line):
                        results.append((py_file, line_num, line.strip()))
        except Exception:
            pass
    return results


def find_generic_exceptions() -> List[Tuple[Path, int, str]]:
    """Find all generic Exception catches."""
    results = []
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if EXCEPTION_PATTERN.search(line):
                        results.append((py_file, line_num, line.strip()))
        except Exception:
            pass
    return results


def find_any_returns() -> List[Tuple[Path, int, str]]:
    """Find all functions returning Any."""
    results = []
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if ANY_PATTERN.search(line):
                        results.append((py_file, line_num, line.strip()))
        except Exception:
            pass
    return results


def find_hardcoded_secrets() -> List[Tuple[Path, int, str, str]]:
    """Find all hardcoded secrets."""
    results = []
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    match = HARDCODED_SECRET_PATTERN.search(line)
                    if match:
                        results.append((py_file, line_num, match.group(1), line.strip()))
        except Exception:
            pass
    return results


def generate_report() -> str:
    """Generate comprehensive implementation report."""
    report = []
    report.append("=" * 80)
    report.append("AUTOMATED IMPLEMENTATION ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")

    # Print statements
    prints = find_print_statements()
    report.append(f"PRINT STATEMENTS FOUND: {len(prints)}")
    report.append("-" * 80)
    for py_file, line_num, line in prints[:10]:
        report.append(f"  {py_file}:{line_num} - {line[:70]}")
    if len(prints) > 10:
        report.append(f"  ... and {len(prints) - 10} more")
    report.append("")

    # Generic exceptions
    exceptions = find_generic_exceptions()
    report.append(f"GENERIC EXCEPTIONS FOUND: {len(exceptions)}")
    report.append("-" * 80)
    for py_file, line_num, line in exceptions[:10]:
        report.append(f"  {py_file}:{line_num} - {line[:70]}")
    if len(exceptions) > 10:
        report.append(f"  ... and {len(exceptions) - 10} more")
    report.append("")

    # Any returns
    any_returns = find_any_returns()
    report.append(f"ANY RETURNS FOUND: {len(any_returns)}")
    report.append("-" * 80)
    for py_file, line_num, line in any_returns[:10]:
        report.append(f"  {py_file}:{line_num} - {line[:70]}")
    if len(any_returns) > 10:
        report.append(f"  ... and {len(any_returns) - 10} more")
    report.append("")

    # Hardcoded secrets
    secrets = find_hardcoded_secrets()
    report.append(f"HARDCODED SECRETS FOUND: {len(secrets)}")
    report.append("-" * 80)
    for py_file, line_num, secret_type, line in secrets[:10]:
        report.append(f"  {py_file}:{line_num} - {secret_type}")
    if len(secrets) > 10:
        report.append(f"  ... and {len(secrets) - 10} more")
    report.append("")

    report.append("=" * 80)
    report.append("SUMMARY")
    report.append("=" * 80)
    report.append(f"Total Print Statements: {len(prints)}")
    report.append(f"Total Generic Exceptions: {len(exceptions)}")
    report.append(f"Total Any Returns: {len(any_returns)}")
    report.append(f"Total Hardcoded Secrets: {len(secrets)}")
    report.append("")

    return "\n".join(report)


if __name__ == "__main__":
    print(generate_report())
