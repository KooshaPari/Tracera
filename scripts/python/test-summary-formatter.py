#!/usr/bin/env python3
"""test-summary-formatter module."""

import os
import re
import sys
from typing import Any


def print_tree(tree: Any, indent: Any = "") -> None:
    """Print tree."""
    keys = sorted(tree.keys())
    for i, key in enumerate(keys):
        is_last = i == len(keys) - 1
        child_indent = "    " if is_last else "│   "

        val = tree[key]
        if isinstance(val, dict):
            print_tree(val, indent + child_indent)
        else:
            _status, _color = val


def main() -> None:
    """Main."""
    test_type = sys.argv[1] if len(sys.argv) > 1 else "generic"

    # ANSI Colors
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    NC = "\033[0m"

    os.environ["NC"] = NC  # Store for recursion

    results = []

    # Regex patterns
    # Go: --- PASS: TestName (0.00s)
    go_pass = re.compile(r"--- PASS: (\S+)")
    go_fail = re.compile(r"--- FAIL: (\S+)")
    re.compile(r"ok  \t(\S+)")

    # Pytest: tests/path/to/test.py::test_name PASSED
    pytest_res = re.compile(r"^(.+?)::(.+?)\s+(PASSED|FAILED|SKIPPED)")

    # Vitest: ✓ src/path/to/test.ts (10)
    vitest_pass = re.compile(r"✓\s+(\S+)")
    vitest_fail = re.compile(r"×\s+(\S+)")

    lines = []
    try:
        for line in sys.stdin:
            sys.stdout.write(line)
            lines.append(line.strip())
    except BrokenPipeError:
        # Standard behavior for pipe-based CLI tools
        sys.stderr.close()
        sys.exit(0)

    for line in lines:
        if test_type == "go":
            m_pass = go_pass.search(line)
            m_fail = go_fail.search(line)
            if m_pass:
                results.append((m_pass.group(1), "PASS", GREEN))
            elif m_fail:
                results.append((m_fail.group(1), "FAIL", RED))
        elif test_type == "pytest":
            m = pytest_res.search(line)
            if m:
                results.append((f"{m.group(1)}::{m.group(2)}", m.group(3), GREEN if m.group(3) == "PASSED" else RED))
        elif test_type == "vitest":
            m_pass = vitest_pass.search(line)
            m_fail = vitest_fail.search(line)
            if m_pass:
                results.append((m_pass.group(1), "PASS", GREEN))
            elif m_fail:
                results.append((m_fail.group(1), "FAIL", RED))
        elif test_type == "playwright":
            # Playwright:   1) [chromium] › websocket-validation.spec.ts:15:5 › WebSocket Validation
            if "PASSED" in line or "passed" in line.lower():
                m = re.search(r"(\S+\.spec\.ts)", line)
                if m:
                    results.append((m.group(1), "PASS", GREEN))
            elif "FAILED" in line or "failed" in line.lower():
                m = re.search(r"(\S+\.spec\.ts)", line)
                if m:
                    results.append((m.group(1), "FAIL", RED))
        else:
            # Generic fallback for summary lines
            m = re.search(r"(\d+) passed, (\d+) failed", line)
            if m:
                # We don't have individual tests, but we can report totals
                pass

    if not results:
        # Check if we saw any summary lines
        summary_found = False
        for line in lines:
            m = re.search(r"(\d+) passed", line)
            if m:
                summary_found = True
                break
        if not summary_found:
            pass
        return

    # Build tree
    tree = {}
    passed = 0
    total = len(results)

    for name, status, color in results:
        if status in {"PASS", "PASSED"}:
            passed += 1

        # Clean name and determine path parts
        if test_type == "go":
            # Go test names are often TestSomething, package is separate
            # But here we use what we caught.
            parts = name.split(".")
        elif test_type == "pytest":
            parts = name.split("::")[0].split("/")
        elif test_type == "vitest":
            parts = name.split("/")
        else:
            parts = name.split("/")

        curr = tree
        for part in parts[:-1]:
            if not part:
                continue
            if part not in curr or not isinstance(curr[part], dict):
                curr[part] = {}
            curr = curr[part]

        leaf = parts[-1]
        if test_type == "pytest" and "::" in name:
            leaf = name.split("::")[-1]

        curr[leaf] = (status, color)

    print_tree(tree)

    rate = (passed / total) * 100 if total > 0 else 0
    color = GREEN if rate == 100 else (YELLOW if rate > 80 else RED)


if __name__ == "__main__":
    main()
