"""
Coverage aggregation module for multiple test frameworks.

Provides CoverageReport dataclass and CoverageAggregator class for collecting
and aggregating coverage data from Python, Go, and TypeScript test frameworks.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CoverageReport:
    """Represents coverage statistics for a single file."""
    language: str
    file: str
    line_rate: float
    branch_rate: float
    statements_covered: int
    branches_covered: int


class CoverageAggregator:
    """Aggregates coverage reports from multiple test frameworks."""

    def collect_python_coverage(self) -> List[CoverageReport]:
        """
        Collect Python coverage data from .coverage or coverage.xml.

        Currently returns mock data for demonstration.
        In production, this would parse coverage.xml files.

        Returns:
            List of CoverageReport objects for Python files.
        """
        return [
            CoverageReport(
                language="python",
                file="src/tracertm/cli/commands/test/coverage.py",
                line_rate=0.85,
                branch_rate=0.78,
                statements_covered=127,
                branches_covered=34
            ),
            CoverageReport(
                language="python",
                file="src/tracertm/services/stateless_ingestion_service.py",
                line_rate=0.92,
                branch_rate=0.88,
                statements_covered=456,
                branches_covered=112
            ),
        ]

    def collect_go_coverage(self) -> List[CoverageReport]:
        """
        Collect Go coverage data from go test -cover output.

        Currently returns mock data for demonstration.
        In production, this would parse go test coverage profiles.

        Returns:
            List of CoverageReport objects for Go files.
        """
        return [
            CoverageReport(
                language="go",
                file="cmd/main.go",
                line_rate=0.89,
                branch_rate=0.82,
                statements_covered=234,
                branches_covered=67
            ),
        ]

    def collect_typescript_coverage(self) -> List[CoverageReport]:
        """
        Collect TypeScript coverage data from vitest coverage output.

        Currently returns mock data for demonstration.
        In production, this would parse vitest coverage reports.

        Returns:
            List of CoverageReport objects for TypeScript files.
        """
        return [
            CoverageReport(
                language="typescript",
                file="frontend/apps/web/src/components/CommandPalette.tsx",
                line_rate=0.88,
                branch_rate=0.80,
                statements_covered=156,
                branches_covered=45
            ),
            CoverageReport(
                language="typescript",
                file="frontend/apps/web/src/routes/__root.tsx",
                line_rate=0.91,
                branch_rate=0.85,
                statements_covered=203,
                branches_covered=58
            ),
        ]

    def aggregate(self, reports: List[CoverageReport]) -> Dict[str, Any]:
        """
        Aggregate coverage reports by language and calculate statistics.

        Args:
            reports: List of CoverageReport objects to aggregate.

        Returns:
            Dictionary with total coverage and per-language breakdown.
        """
        if not reports:
            return {
                "total_coverage_percent": 0.0,
                "by_language": {},
                "total_statements": 0,
                "total_branches": 0,
            }

        # Group by language
        by_language: dict[str, Any] = {}
        total_line_rate = 0.0
        total_branch_rate = 0.0

        for report in reports:
            if report.language not in by_language:
                by_language[report.language] = {
                    "files": [],
                    "total_line_rate": 0.0,
                    "total_branch_rate": 0.0,
                    "file_count": 0,
                    "total_statements": 0,
                    "total_branches": 0,
                }

            lang_data = by_language[report.language]
            files = lang_data.get("files")
            if isinstance(files, list):
                files.append(report.file)
            total_lr = lang_data.get("total_line_rate")
            if isinstance(total_lr, (int, float)):
                lang_data["total_line_rate"] = total_lr + report.line_rate
            total_br = lang_data.get("total_branch_rate")
            if isinstance(total_br, (int, float)):
                lang_data["total_branch_rate"] = total_br + report.branch_rate
            fc = lang_data.get("file_count")
            if isinstance(fc, int):
                lang_data["file_count"] = fc + 1
            ts = lang_data.get("total_statements")
            if isinstance(ts, int):
                lang_data["total_statements"] = ts + report.statements_covered
            tb = lang_data.get("total_branches")
            if isinstance(tb, int):
                lang_data["total_branches"] = tb + report.branches_covered

        # Calculate averages per language
        for lang, data in by_language.items():
            file_count = data.get("file_count", 0)
            total_lr = data.get("total_line_rate", 0.0)
            total_br = data.get("total_branch_rate", 0.0)
            if isinstance(total_lr, (int, float)) and isinstance(total_br, (int, float)):
                data["avg_line_rate"] = total_lr / file_count if file_count > 0 else 0
                data["avg_branch_rate"] = total_br / file_count if file_count > 0 else 0
                avg_lr = data.get("avg_line_rate", 0.0)
                if isinstance(avg_lr, (int, float)):
                    data["coverage_percent"] = round(avg_lr * 100, 2)

        # Calculate overall coverage
        avg_line_rate = sum(r.line_rate for r in reports) / len(reports) if reports else 0

        return {
            "total_coverage_percent": round(avg_line_rate * 100, 2),
            "by_language": by_language,
            "total_files": len(reports),
            "languages_tested": list(by_language.keys()),
        }
