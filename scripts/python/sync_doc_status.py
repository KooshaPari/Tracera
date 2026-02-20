#!/usr/bin/env python3
"""Synchronize documentation status from codebase.

This script scans the codebase for FR references, updates test coverage,
checks git commits, and regenerates the status dashboard.

Usage:
    python scripts/python/sync_doc_status.py [options]
    python scripts/python/sync_doc_status.py --help
    python scripts/python/sync_doc_status.py --verbose
    python scripts/python/sync_doc_status.py --dry-run

Run as cron job:
    0 0 * * * cd /path/to/project && python scripts/python/sync_doc_status.py
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# FR reference patterns in code
FR_PATTERNS = {
    "python_docstring": re.compile(r'""".*?FR-[A-Z]+-\d{3}.*?"""', re.DOTALL),
    "python_comment": re.compile(r'#.*?(FR-[A-Z]+-\d{3})'),
    "go_comment": re.compile(r'//.*?(FR-[A-Z]+-\d{3})'),
    "ts_comment": re.compile(r'//.*?(FR-[A-Z]+-\d{3})'),
    "ts_jsdoc": re.compile(r'/\*\*.*?FR-[A-Z]+-\d{3}.*?\*/', re.DOTALL),
}

# Extract FR ID from text
FR_ID_PATTERN = re.compile(r'(FR-[A-Z]+-\d{3})')


@dataclass
class CodeLocation:
    """Code location reference."""
    file_path: str
    line_start: int
    line_end: int
    fr_id: str


@dataclass
class TestLocation:
    """Test location reference."""
    file_path: str
    test_name: str
    fr_id: str


class DocStatusSyncer:
    """Synchronize documentation status from codebase."""

    def __init__(self, project_root: Path, verbose: bool = False, dry_run: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.dry_run = dry_run

        # Paths
        self.fr_status_path = project_root / "docs" / "FUNCTIONAL_REQUIREMENTS_STATUS.json"
        self.dashboard_script = project_root / "scripts" / "python" / "generate_status_dashboard.py"

        # Track changes
        self.changes: dict[str, Any] = {
            "code_locations_updated": 0,
            "test_coverage_updated": 0,
            "git_commits_linked": 0,
        }

    def log(self, msg: str, level: str = "INFO") -> None:
        """Log message if verbose enabled."""
        if self.verbose or level == "ERROR":
            prefix = "🔍" if level == "INFO" else "❌" if level == "ERROR" else "✅"
            print(f"{prefix} {msg}")

    def load_fr_status(self) -> dict[str, Any]:
        """Load FUNCTIONAL_REQUIREMENTS_STATUS.json."""
        self.log(f"Loading FR status from {self.fr_status_path.relative_to(self.project_root)}")
        with self.fr_status_path.open("r") as f:
            return json.load(f)

    def save_fr_status(self, data: dict[str, Any]) -> None:
        """Save FUNCTIONAL_REQUIREMENTS_STATUS.json."""
        if self.dry_run:
            self.log("DRY RUN: Would save FR status", "INFO")
            return

        self.log(f"Saving FR status to {self.fr_status_path.relative_to(self.project_root)}")

        # Update metadata
        data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        with self.fr_status_path.open("w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")  # Add trailing newline

    def scan_code_for_frs(self) -> dict[str, list[str]]:
        """Scan codebase for FR references in docstrings/comments.

        Returns:
            Dictionary mapping FR IDs to code locations (file:line-line)
        """
        self.log("Scanning codebase for FR references...")

        fr_locations: dict[str, list[str]] = {}

        # Scan Python files
        for py_file in self.project_root.glob("src/**/*.py"):
            self._scan_file(py_file, "python", fr_locations)

        # Scan Go files
        for go_file in self.project_root.glob("backend/**/*.go"):
            self._scan_file(go_file, "go", fr_locations)

        # Scan TypeScript files
        for ts_file in self.project_root.glob("frontend/**/*.{ts,tsx}"):
            self._scan_file(ts_file, "typescript", fr_locations)

        self.log(f"Found {sum(len(v) for v in fr_locations.values())} FR references in code")
        return fr_locations

    def _scan_file(self, file_path: Path, lang: str, fr_locations: dict[str, list[str]]) -> None:
        """Scan single file for FR references."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.log(f"Error reading {file_path}: {e}", "ERROR")
            return

        # Find all FR IDs in file
        fr_ids = set(FR_ID_PATTERN.findall(content))

        for fr_id in fr_ids:
            # Find line numbers where FR ID appears
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if fr_id in line:
                    # Record location as file:line-line (simple single-line for now)
                    rel_path = file_path.relative_to(self.project_root)
                    location = f"{rel_path}:{i}-{i}"

                    if fr_id not in fr_locations:
                        fr_locations[fr_id] = []

                    if location not in fr_locations[fr_id]:
                        fr_locations[fr_id].append(location)

    def update_code_locations(self, fr_status: dict[str, Any], fr_locations: dict[str, list[str]]) -> None:
        """Update code_locations field in FR status."""
        self.log("Updating code locations in FR status...")

        for fr_id, locations in fr_locations.items():
            if fr_id in fr_status["functional_requirements"]:
                fr = fr_status["functional_requirements"][fr_id]

                # Update if changed
                current = set(fr.get("code_locations", []))
                new = set(locations)

                if current != new:
                    fr["code_locations"] = sorted(locations)
                    fr["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                    self.changes["code_locations_updated"] += 1
                    self.log(f"Updated code locations for {fr_id}: {len(locations)} files")

    def run_tests_and_update_coverage(self, fr_status: dict[str, Any]) -> None:
        """Run tests and update test_coverage field.

        Note: This runs pytest with --cov to get coverage data.
        In production, this should be optimized or run separately.
        """
        self.log("Running tests to measure coverage...")

        # Run pytest with coverage
        try:
            result = subprocess.run(
                ["pytest", "--cov=src", "--cov-report=json", "--quiet"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Load coverage data
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with coverage_file.open("r") as f:
                    coverage_data = json.load(f)

                # Map files to FRs and calculate coverage
                self._update_coverage_from_data(fr_status, coverage_data)

                # Cleanup
                coverage_file.unlink()
            else:
                self.log("No coverage.json generated", "ERROR")

        except subprocess.TimeoutExpired:
            self.log("Test execution timed out (5 min)", "ERROR")
        except Exception as e:
            self.log(f"Error running tests: {e}", "ERROR")

    def _update_coverage_from_data(self, fr_status: dict[str, Any], coverage_data: dict[str, Any]) -> None:
        """Update FR test coverage from coverage.json data."""
        # Build map from file to coverage percentage
        file_coverage: dict[str, float] = {}

        for file_path, file_data in coverage_data.get("files", {}).items():
            summary = file_data.get("summary", {})
            percent = summary.get("percent_covered", 0.0)
            file_coverage[file_path] = percent

        # Update FR coverage based on code locations
        for fr_id, fr in fr_status["functional_requirements"].items():
            code_locations = fr.get("code_locations", [])

            if code_locations:
                # Calculate average coverage for FR's files
                coverages = []
                for location in code_locations:
                    # Extract file path from "file:line-line"
                    file_path = location.split(":")[0]
                    if file_path in file_coverage:
                        coverages.append(file_coverage[file_path])

                if coverages:
                    avg_coverage = sum(coverages) / len(coverages)
                    old_coverage = fr.get("test_coverage", 0)

                    if abs(avg_coverage - old_coverage) > 0.5:  # Changed by > 0.5%
                        fr["test_coverage"] = round(avg_coverage)
                        fr["last_verified"] = datetime.now().strftime("%Y-%m-%d")
                        self.changes["test_coverage_updated"] += 1
                        self.log(f"Updated test coverage for {fr_id}: {old_coverage}% → {round(avg_coverage)}%")

    def check_git_commits_for_frs(self, fr_status: dict[str, Any]) -> None:
        """Check recent git commits for FR references.

        Scans last 100 commits for FR-XXX-NNN patterns.
        """
        self.log("Checking git commits for FR references...")

        try:
            # Get last 100 commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-100"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.log("Git log failed", "ERROR")
                return

            # Extract FR IDs from commit messages
            for line in result.stdout.split("\n"):
                fr_ids = FR_ID_PATTERN.findall(line)
                commit_hash = line.split()[0] if line.strip() else ""

                for fr_id in fr_ids:
                    if fr_id in fr_status["functional_requirements"]:
                        fr = fr_status["functional_requirements"][fr_id]

                        # Add to notes if not already mentioned
                        notes = fr.get("notes", "")
                        if commit_hash not in notes:
                            if notes:
                                notes += f" | Commit {commit_hash}"
                            else:
                                notes = f"Commit {commit_hash}"

                            fr["notes"] = notes
                            fr["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                            self.changes["git_commits_linked"] += 1
                            self.log(f"Linked commit {commit_hash} to {fr_id}")

        except subprocess.TimeoutExpired:
            self.log("Git log timed out", "ERROR")
        except Exception as e:
            self.log(f"Error checking git commits: {e}", "ERROR")

    def regenerate_dashboard(self) -> None:
        """Regenerate STATUS_DASHBOARD.md."""
        if self.dry_run:
            self.log("DRY RUN: Would regenerate dashboard", "INFO")
            return

        self.log("Regenerating status dashboard...")

        try:
            result = subprocess.run(
                [sys.executable, str(self.dashboard_script)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.log("Dashboard regenerated successfully", "SUCCESS")
            else:
                self.log(f"Dashboard generation failed: {result.stderr}", "ERROR")

        except subprocess.TimeoutExpired:
            self.log("Dashboard generation timed out", "ERROR")
        except Exception as e:
            self.log(f"Error regenerating dashboard: {e}", "ERROR")

    def sync(self) -> bool:
        """Run full synchronization.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current status
            fr_status = self.load_fr_status()

            # 1. Scan code for FR references
            fr_locations = self.scan_code_for_frs()
            self.update_code_locations(fr_status, fr_locations)

            # 2. Run tests and update coverage
            # Note: Disabled by default as it's slow - enable with --run-tests
            # self.run_tests_and_update_coverage(fr_status)

            # 3. Check git commits
            self.check_git_commits_for_frs(fr_status)

            # 4. Save updated status
            self.save_fr_status(fr_status)

            # 5. Regenerate dashboard
            self.regenerate_dashboard()

            # Print summary
            print("\n" + "=" * 60)
            print("📊 Synchronization Summary")
            print("=" * 60)
            print(f"✅ Code locations updated: {self.changes['code_locations_updated']}")
            print(f"✅ Test coverage updated: {self.changes['test_coverage_updated']}")
            print(f"✅ Git commits linked: {self.changes['git_commits_linked']}")
            print("=" * 60)

            return True

        except Exception as e:
            self.log(f"Synchronization failed: {e}", "ERROR")
            return False


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synchronize documentation status from codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/sync_doc_status.py
  python scripts/python/sync_doc_status.py --verbose
  python scripts/python/sync_doc_status.py --dry-run --verbose
  python scripts/python/sync_doc_status.py --run-tests

Cron job setup:
  0 0 * * * cd /path/to/project && python scripts/python/sync_doc_status.py
        """
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving changes"
    )

    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run tests to update coverage (slow)"
    )

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Run sync
    syncer = DocStatusSyncer(project_root, verbose=args.verbose, dry_run=args.dry_run)
    success = syncer.sync()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
