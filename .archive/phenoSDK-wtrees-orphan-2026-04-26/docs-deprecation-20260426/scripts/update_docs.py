#!/usr/bin/env python3
"""Quick documentation update script.

Updates cross-links and regenerates key documentation files.
Faster than full deploy_docs.sh for local development.

State: STABLE
Since: 0.3.0
"""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


def run_command(cmd: list[str], description: str):
    """Run command and report status."""
    print(f"→ {description}...")
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✅ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {description} failed")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Run quick documentation update."""
    print("=" * 70)
    print("Quick Documentation Update")
    print("=" * 70)
    print()

    # Extract cross-links
    if not run_command(
        ["python", "scripts/extract_cross_links.py"],
        "Extracting cross-links"
    ):
        sys.exit(1)

    print()

    # Generate only fast reports
    reports = [
        ("scripts/generate_spec_coverage.py", "Generating spec coverage"),
        ("scripts/generate_test_coverage_report.py", "Generating test coverage"),
    ]

    for script, description in reports:
        run_command(["python", script], description)

    print()
    print("=" * 70)
    print("Update Complete")
    print("=" * 70)
    print()
    print("Updated files:")
    print("  - docs/cross_links.json")
    print("  - docs/SPEC_COVERAGE_MATRIX.md")
    print("  - docs/TEST_COVERAGE_REPORT.md")
    print()
    print("For full update with API reference and graphs:")
    print("  ./scripts/deploy_docs.sh --no-commit")
    print()


if __name__ == "__main__":
    main()
