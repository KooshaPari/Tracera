#!/usr/bin/env python3
"""Daily Coverage Update Script.

Parses pytest --cov output and updates COVERAGE_PROGRESS_DASHBOARD.md
Run after pytest completes to automatically track metrics.

Usage:
    python3 scripts/update_coverage_daily.py

    Or integrate into CI/CD:
    - .github/workflows/coverage.yml
    - Local cron job: 0 17 * * 1-5 (5 PM EST weekdays)
"""

import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class CoverageMetricsExtractor:
    """Extract coverage metrics from pytest output and coverage.json."""

    def __init__(self, project_dir: Path | None = None) -> None:
        """Initialize."""
        self.project_dir = project_dir or Path.cwd()
        self.coverage_json = self.project_dir / "htmlcov" / "coverage.json"
        self.coverage_file = self.project_dir / ".coverage"
        self.metrics = {}

    def extract_from_json(self) -> dict[str, Any]:
        """Extract metrics from coverage.json."""
        if not self.coverage_json.exists():
            return {}

        try:
            with Path(self.coverage_json).open(encoding="utf-8") as f:
                data = json.load(f)

            totals = data.get("totals", {})
            metrics = {
                "date": datetime.now(UTC).isoformat(),
                "line_coverage": round(totals.get("percent_covered", 0), 2),
                "lines_covered": totals.get("covered_lines", 0),
                "lines_total": totals.get("num_statements", 0),
                "branches": totals.get("num_branches", 0),
                "branches_covered": totals.get("covered_branches", 0),
            }

            # Extract per-module coverage
            modules = {}
            for file_path, file_data in data.get("files", {}).items():
                # Extract module name from path
                if "src/tracertm/" in file_path:
                    parts = file_path.split("src/tracertm/")[-1].split("/")
                    module = parts[0] if parts else "other"
                else:
                    continue

                if module not in modules:
                    modules[module] = []

                summary = file_data.get("summary", {})
                modules[module].append(summary.get("percent_covered", 0))

            # Calculate module averages
            metrics["by_module"] = {module: round(sum(values) / len(values), 2) for module, values in modules.items()}

            return metrics

        except Exception:
            return {}

    def extract_from_pytest_output(self, log_file: Path | None = None) -> dict[str, Any]:
        """Extract metrics from pytest output."""
        metrics = {}

        try:
            if log_file and log_file.exists():
                content = log_file.read_text()
            else:
                # Try to run pytest and capture output
                result = subprocess.run(
                    ["pytest", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    return metrics
                content = ""

            # Extract test counts from output
            passed_match = re.search(r"(\d+)\s+passed", content)
            failed_match = re.search(r"(\d+)\s+failed", content)
            warnings_match = re.search(r"(\d+)\s+warning", content)

            if passed_match:
                metrics["tests_passed"] = int(passed_match.group(1))
            if failed_match:
                metrics["tests_failed"] = int(failed_match.group(1))
            if warnings_match:
                metrics["tests_warnings"] = int(warnings_match.group(1))

            # Calculate total
            if "tests_passed" in metrics or "tests_failed" in metrics:
                metrics["tests_total"] = metrics.get("tests_passed", 0) + metrics.get("tests_failed", 0)

            return metrics

        except Exception:
            return {}

    def get_previous_metrics(self) -> dict[str, Any] | None:
        """Load previous day's metrics for comparison."""
        tracking_dir = self.project_dir / ".coverage_tracking"
        if not tracking_dir.exists():
            return None

        # Find most recent metrics file
        metrics_files = sorted(tracking_dir.glob("metrics_*.json"))
        if not metrics_files:
            return None

        try:
            with Path(metrics_files[-1]).open(encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_metrics(self, metrics: dict[str, Any]) -> Path:
        """Save metrics to JSON file."""
        tracking_dir = self.project_dir / ".coverage_tracking"
        tracking_dir.mkdir(exist_ok=True)

        date_str = datetime.now(UTC).strftime("%Y%m%d")
        output_file = tracking_dir / f"metrics_{date_str}.json"

        with Path(output_file).open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        return output_file

    def calculate_metrics(self) -> dict[str, Any]:
        """Calculate all metrics and return combined dict."""
        metrics = {}

        # Extract from coverage.json
        metrics.update(self.extract_from_json())

        # Extract from pytest output
        pytest_metrics = self.extract_from_pytest_output()
        metrics.update(pytest_metrics)

        # Add timestamp
        if "date" not in metrics:
            metrics["date"] = datetime.now(UTC).isoformat()

        return metrics


class DashboardUpdater:
    """Update COVERAGE_PROGRESS_DASHBOARD.md with latest metrics."""

    def __init__(self, project_dir: Path | None = None) -> None:
        """Initialize."""
        self.project_dir = project_dir or Path.cwd()
        self.dashboard_path = self.project_dir / "COVERAGE_PROGRESS_DASHBOARD.md"

    def update_dashboard(self, metrics: dict[str, Any]) -> bool:
        """Update dashboard with new metrics."""
        if not self.dashboard_path.exists():
            return False

        try:
            content = self.dashboard_path.read_text()
            today = datetime.now(UTC).strftime("%Y-%m-%d")

            # Build metrics section
            metrics_section = self._build_metrics_section(metrics, today)

            # Find today's section and update
            pattern = r"## Date: \d{4}-\d{2}-\d{2}.*?(?=\n## Date: |\n---|\Z)"
            if re.search(pattern, content, re.DOTALL):
                # Replace existing date section
                content = re.sub(
                    pattern,
                    metrics_section,
                    content,
                    count=1,
                    flags=re.DOTALL,
                )
            else:
                # Append new section before last section
                insert_pos = content.rfind("---")
                if insert_pos >= 0:
                    content = content[:insert_pos] + metrics_section + "\n---\n" + content[insert_pos + 3 :]
                else:
                    content += "\n" + metrics_section

            # Update last updated timestamp
            content = re.sub(
                r"\*Last Updated: .*?\*",
                f"*Last Updated: {today}*",
                content,
            )

            self.dashboard_path.write_text(content)
            return True

        except Exception:
            return False

    def _build_metrics_section(self, metrics: dict[str, Any], today: str) -> str:
        """Build markdown section with metrics."""
        coverage = metrics.get("line_coverage", 0)
        lines_covered = metrics.get("lines_covered", 0)
        lines_total = metrics.get("lines_total", 0)
        tests_total = metrics.get("tests_total", "N/A")
        tests_passed = metrics.get("tests_passed", "N/A")
        tests_failed = metrics.get("tests_failed", 0)

        section = f"""## Date: {today}

### Overall Metrics
- **Line Coverage:** {coverage}%
- **Lines Covered:** {lines_covered}/{lines_total}
- **Tests Collected:** {tests_total}
- **Tests Passing:** {tests_passed}
- **Tests Failing:** {tests_failed}

### By Module
"""

        # Add module breakdown
        if metrics.get("by_module"):
            for module, coverage_pct in sorted(metrics["by_module"].items()):
                section += f"- **{module}:** {coverage_pct}%\n"
        else:
            section += "- *No module data available*\n"

        return section


def main() -> int | None:
    """Main execution."""
    try:
        # Create extractor
        extractor = CoverageMetricsExtractor()

        # Calculate metrics
        metrics = extractor.calculate_metrics()

        if not metrics:
            return 1

        # Save metrics
        extractor.save_metrics(metrics)

        # Update dashboard
        updater = DashboardUpdater()
        if updater.update_dashboard(metrics):
            pass

        # Print JSON for CI/CD integration

        return 0

    except Exception:
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
