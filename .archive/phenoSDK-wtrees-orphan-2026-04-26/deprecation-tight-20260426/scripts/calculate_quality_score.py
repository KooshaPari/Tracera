#!/usr/bin/env python3
"""
Calculate Quality Score from Analysis Reports
Generates a comprehensive quality score based on various analysis reports.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class QualityScoreCalculator:
    """Calculate quality scores from analysis reports."""

    def __init__(self):
        self.weights = {
            "violations": 0.3,
            "warnings": 0.2,
            "errors": 0.4,
            "coverage": 0.1,
        }

        self.thresholds = {
            "excellent": 90,
            "good": 80,
            "fair": 70,
            "poor": 60,
        }

    def calculate_score(self, reports_dir: str) -> dict[str, Any]:
        """Calculate quality score from reports directory."""
        reports_path = Path(reports_dir)

        if not reports_path.exists():
            return self._error_result("Reports directory not found")

        # Collect all report data
        report_data = self._collect_report_data(reports_path)

        # Calculate individual scores
        scores = self._calculate_individual_scores(report_data)

        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(scores)

        # Determine quality grade
        grade = self._determine_grade(overall_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(scores, overall_score)

        return {
            "overall_score": overall_score,
            "grade": grade,
            "individual_scores": scores,
            "recommendations": recommendations,
            "metadata": {
                "reports_analyzed": len(report_data),
                "calculation_method": "weighted_average",
                "weights": self.weights,
            },
        }

    def _collect_report_data(self, reports_path: Path) -> list[dict[str, Any]]:
        """Collect data from all report files."""
        report_data = []

        # Look for common report files
        report_patterns = [
            "ruff_report.json",
            "mypy_report/report.json",
            "prospector_report.json",
            "radon_*.json",
            "coverage.xml",
            "bandit-report.json",
            "safety-report.json",
            "unified_quality_report.json",
        ]

        for pattern in report_patterns:
            for report_file in reports_path.glob(pattern):
                try:
                    with open(report_file) as f:
                        if report_file.suffix == ".json":
                            data = json.load(f)
                        else:
                            # For XML files, we'll parse them differently
                            data = self._parse_xml_report(report_file)

                        report_data.append({
                            "file": str(report_file),
                            "type": self._determine_report_type(report_file.name),
                            "data": data,
                        })
                except Exception as e:
                    print(f"Warning: Could not parse {report_file}: {e}", file=sys.stderr)

        return report_data

    def _determine_report_type(self, filename: str) -> str:
        """Determine the type of report based on filename."""
        if "ruff" in filename:
            return "linting"
        if "mypy" in filename:
            return "type_checking"
        if "prospector" in filename:
            return "static_analysis"
        if "radon" in filename:
            return "complexity"
        if "coverage" in filename:
            return "coverage"
        if "bandit" in filename:
            return "security"
        if "safety" in filename:
            return "dependencies"
        if "unified" in filename:
            return "comprehensive"
        return "unknown"

    def _parse_xml_report(self, file_path: Path) -> dict[str, Any]:
        """Parse XML report files (like coverage.xml)."""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(file_path)
            root = tree.getroot()

            if "coverage" in file_path.name:
                return {
                    "line_rate": float(root.get("line-rate", 0)),
                    "branch_rate": float(root.get("branch-rate", 0)),
                    "lines_covered": int(root.get("lines-covered", 0)),
                    "lines_valid": int(root.get("lines-valid", 0)),
                }
        except Exception as e:
            print(f"Warning: Could not parse XML {file_path}: {e}", file=sys.stderr)

        return {}

    def _calculate_individual_scores(self, report_data: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate individual scores for each metric."""
        scores = {
            "violations": 100.0,
            "warnings": 100.0,
            "errors": 100.0,
            "coverage": 0.0,
        }

        total_violations = 0
        total_warnings = 0
        total_errors = 0
        coverage_rates = []

        for report in report_data:
            data = report["data"]
            report_type = report["type"]

            if report_type == "linting":
                # Ruff reports
                if isinstance(data, dict):
                    total_violations += len(data.get("violations", []))

            elif report_type == "type_checking":
                # MyPy reports
                if isinstance(data, dict):
                    total_errors += len(data.get("messages", []))

            elif report_type == "static_analysis":
                # Prospector reports
                if isinstance(data, dict):
                    issues = data.get("issues", [])
                    for issue in issues:
                        if issue.get("severity") == "error":
                            total_errors += 1
                        elif issue.get("severity") == "warning":
                            total_warnings += 1
                        else:
                            total_violations += 1

            elif report_type == "coverage":
                # Coverage reports
                if isinstance(data, dict) and "line_rate" in data:
                    coverage_rates.append(data["line_rate"])

            elif report_type == "comprehensive":
                # Unified quality reports
                if isinstance(data, dict):
                    summary = data.get("summary", {})
                    total_violations += summary.get("total_violations", 0)
                    total_warnings += summary.get("total_warnings", 0)
                    total_errors += summary.get("total_errors", 0)

        # Calculate scores based on thresholds
        scores["violations"] = max(0, 100 - (total_violations * 0.5))
        scores["warnings"] = max(0, 100 - (total_warnings * 0.3))
        scores["errors"] = max(0, 100 - (total_errors * 2.0))

        if coverage_rates:
            scores["coverage"] = sum(coverage_rates) / len(coverage_rates) * 100
        else:
            scores["coverage"] = 0.0

        return scores

    def _calculate_overall_score(self, scores: dict[str, float]) -> float:
        """Calculate weighted overall score."""
        weighted_sum = 0
        total_weight = 0

        for metric, score in scores.items():
            if metric in self.weights:
                weighted_sum += score * self.weights[metric]
                total_weight += self.weights[metric]

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _determine_grade(self, score: float) -> str:
        """Determine quality grade based on score."""
        if score >= self.thresholds["excellent"]:
            return "A+"
        if score >= self.thresholds["good"]:
            return "A"
        if score >= self.thresholds["fair"]:
            return "B"
        if score >= self.thresholds["poor"]:
            return "C"
        return "D"

    def _generate_recommendations(self, scores: dict[str, float], overall_score: float) -> list[str]:
        """Generate recommendations based on scores."""
        recommendations = []

        if scores["errors"] < 80:
            recommendations.append("🚨 Critical: Fix all errors immediately - they may cause system failures")

        if scores["violations"] < 70:
            recommendations.append("⚠️ High Priority: Address code violations to improve maintainability")

        if scores["warnings"] < 60:
            recommendations.append("📝 Medium Priority: Resolve warnings to improve code quality")

        if scores["coverage"] < 80:
            recommendations.append("🧪 Testing: Increase test coverage to improve reliability")

        if overall_score >= 90:
            recommendations.append("✅ Excellent: Maintain current quality standards")
        elif overall_score >= 80:
            recommendations.append("👍 Good: Minor improvements recommended")
        elif overall_score >= 70:
            recommendations.append("⚠️ Fair: Significant improvements needed")
        else:
            recommendations.append("🚨 Poor: Major refactoring required")

        return recommendations

    def _error_result(self, message: str) -> dict[str, Any]:
        """Return error result."""
        return {
            "overall_score": 0.0,
            "grade": "F",
            "error": message,
            "individual_scores": {},
            "recommendations": [f"❌ Error: {message}"],
            "metadata": {},
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Calculate Quality Score from Reports")
    parser.add_argument("reports_dir", help="Directory containing analysis reports")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    calculator = QualityScoreCalculator()
    result = calculator.calculate_score(args.reports_dir)

    if args.json:
        output = json.dumps(result, indent=2)
    else:
        # Pretty print format
        output = f"""
📊 QUALITY SCORE CALCULATION
{'=' * 50}
Overall Score: {result['overall_score']:.1f}/100
Grade: {result['grade']}

Individual Scores:
  Violations: {result['individual_scores'].get('violations', 0):.1f}/100
  Warnings: {result['individual_scores'].get('warnings', 0):.1f}/100
  Errors: {result['individual_scores'].get('errors', 0):.1f}/100
  Coverage: {result['individual_scores'].get('coverage', 0):.1f}/100

Recommendations:
"""
        for i, rec in enumerate(result["recommendations"], 1):
            output += f"  {i}. {rec}\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
