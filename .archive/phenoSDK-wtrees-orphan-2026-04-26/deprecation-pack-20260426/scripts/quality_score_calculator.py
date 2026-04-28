#!/usr/bin/env python3
"""
Quality Score Calculator for ATOMS-PHENO Comprehensive quality metrics calculation and
scoring.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any


class QualityScoreCalculator:
    """
    Calculates comprehensive quality scores.
    """

    def __init__(self):
        self.weights = {
            "tests": 0.30,  # Test coverage and passing
            "code_quality": 0.25,  # Linting and static analysis
            "security": 0.20,  # Security vulnerabilities
            "complexity": 0.15,  # Code complexity
            "documentation": 0.10,  # Documentation coverage
        }

        self.logger = logging.getLogger(__name__)

    def calculate_component_score(self, component: str, data: dict[str, Any]) -> float:
        """
        Calculate score for a single component.
        """
        try:
            if component == "tests":
                return self._calculate_tests_score(data)
            if component == "code_quality":
                return self._calculate_code_quality_score(data)
            if component == "security":
                return self._calculate_security_score(data)
            if component == "complexity":
                return self._calculate_complexity_score(data)
            if component == "documentation":
                return self._calculate_documentation_score(data)
            return 0.0

        except Exception as e:
            self.logger.error(f"Error calculating {component} score: {e}")
            return 0.0

    def _calculate_tests_score(self, test_data: dict[str, Any]) -> float:
        """
        Calculate tests component score.
        """
        score = 0.0

        # Test passing (40% weight)
        if test_data.get("passing", False):
            score += 40
        else:
            score += 0

        # Test coverage (30% weight)
        coverage = test_data.get("coverage", 0)
        if coverage >= 90:
            score += 30
        elif coverage >= 80:
            score += 25
        elif coverage >= 70:
            score += 20
        elif coverage >= 60:
            score += 10
        else:
            score += 0

        # Test execution time (15% weight)
        avg_duration = test_data.get("avg_duration", 0)
        if avg_duration < 1.0:  # < 1 second
            score += 15
        elif avg_duration < 5.0:  # < 5 seconds
            score += 10
        elif avg_duration < 10.0:  # < 10 seconds
            score += 5
        else:
            score += 0

        # Test reliability (15% weight)
        flaky_rate = test_data.get("flaky_rate", 0)
        if flaky_rate < 0.05:  # < 5% flaky
            score += 15
        elif flaky_rate < 0.10:  # < 10% flaky
            score += 10
        elif flaky_rate < 0.20:  # < 20% flaky
            score += 5
        else:
            score += 0

        return score

    def _calculate_code_quality_score(self, quality_data: dict[str, Any]) -> float:
        """
        Calculate code quality component score.
        """
        score = 0.0

        # Linting issues (40% weight)
        total_issues = quality_data.get("total_issues", 0)
        if total_issues == 0:
            score += 40
        elif total_issues < 10:
            score += 35
        elif total_issues < 25:
            score += 25
        elif total_issues < 50:
            score += 15
        elif total_issues < 100:
            score += 5
        else:
            score += 0

        # Type checking (25% weight)
        type_errors = quality_data.get("type_errors", 0)
        if type_errors == 0:
            score += 25
        elif type_errors < 5:
            score += 20
        elif type_errors < 10:
            score += 15
        elif type_errors < 25:
            score += 10
        else:
            score += 0

        # Code formatting (20% weight)
        format_issues = quality_data.get("format_issues", 0)
        if format_issues == 0:
            score += 20
        elif format_issues < 5:
            score += 15
        elif format_issues < 15:
            score += 10
        else:
            score += 0

        # Import organization (15% weight)
        import_issues = quality_data.get("import_issues", 0)
        if import_issues == 0:
            score += 15
        elif import_issues < 3:
            score += 10
        elif import_issues < 10:
            score += 5
        else:
            score += 0

        return score

    def _calculate_security_score(self, security_data: dict[str, Any]) -> float:
        """
        Calculate security component score.
        """
        score = 0.0

        # Vulnerabilities (50% weight)
        critical_vulns = security_data.get("critical_vulns", 0)
        high_vulns = security_data.get("high_vulns", 0)
        medium_vulns = security_data.get("medium_vulns", 0)
        low_vulns = security_data.get("low_vulns", 0)

        weighted_vulns = critical_vulns * 10 + high_vulns * 5 + medium_vulns * 2 + low_vulns * 1

        if weighted_vulns == 0:
            score += 50
        elif weighted_vulns < 5:
            score += 40
        elif weighted_vulns < 15:
            score += 25
        elif weighted_vulns < 50:
            score += 10
        else:
            score += 0

        # Security scan coverage (25% weight)
        scan_coverage = security_data.get("scan_coverage", 0)
        score += min(25, scan_coverage)

        # Code security best practices (25% weight)
        best_practices = security_data.get("best_practices_violations", 0)
        if best_practices == 0:
            score += 25
        elif best_practices < 3:
            score += 20
        elif best_practices < 10:
            score += 15
        elif best_practices < 20:
            score += 10
        else:
            score += 0

        return score

    def _calculate_complexity_score(self, complexity_data: dict[str, Any]) -> float:
        """
        Calculate complexity component score.
        """
        score = 0.0

        # Cyclomatic complexity (40% weight)
        avg_complexity = complexity_data.get("avg_complexity", 0)
        max_complexity = complexity_data.get("max_complexity", 0)

        complexity_score = 0
        if avg_complexity <= 3:
            complexity_score += 20
        elif avg_complexity <= 5:
            complexity_score += 15
        elif avg_complexity <= 8:
            complexity_score += 10
        elif avg_complexity <= 12:
            complexity_score += 5

        if max_complexity <= 10:
            complexity_score += 20
        elif max_complexity <= 15:
            complexity_score += 15
        elif max_complexity <= 20:
            complexity_score += 10
        elif max_complexity <= 30:
            complexity_score += 5

        score += min(40, complexity_score)

        # Maintainability index (30% weight)
        mi_score = complexity_data.get("maintainability_index", 100)
        if mi_score >= 80:
            score += 30
        elif mi_score >= 70:
            score += 25
        elif mi_score >= 60:
            score += 20
        elif mi_score >= 50:
            score += 15
        elif mi_score >= 40:
            score += 10
        else:
            score += 0

        # Code duplication (30% weight)
        duplication = complexity_data.get("duplication_percent", 0)
        if duplication <= 5:
            score += 30
        elif duplication <= 10:
            score += 25
        elif duplication <= 20:
            score += 20
        elif duplication <= 30:
            score += 15
        elif duplication <= 50:
            score += 10
        else:
            score += 0

        return score

    def _calculate_documentation_score(self, doc_data: dict[str, Any]) -> float:
        """
        Calculate documentation component score.
        """
        score = 0.0

        # Docstring coverage (50% weight)
        doc_coverage = doc_data.get("doc_coverage", 0)
        score += min(50, doc_coverage / 2)

        # API documentation (25% weight)
        api_docs = doc_data.get("api_docs", 0)
        if api_docs >= 90:
            score += 25
        elif api_docs >= 70:
            score += 20
        elif api_docs >= 50:
            score += 15
        elif api_docs >= 30:
            score += 10
        else:
            score += 0

        # README and setup (25% weight)
        readme_quality = doc_data.get("readme_quality", 0)
        if readme_quality >= 80:
            score += 15
        elif readme_quality >= 60:
            score += 10
        elif readme_quality >= 40:
            score += 5
        else:
            score += 0

        setup_docs = doc_data.get("setup_docs", 0)
        if setup_docs >= 80:
            score += 10
        elif setup_docs >= 60:
            score += 5
        else:
            score += 0

        return score

    def calculate_overall_score(self, component_scores: list[float]) -> dict[str, Any]:
        """
        Calculate weighted overall quality score.
        """
        total_score = 0.0

        component_names = list(self.weights.keys())

        for i, component_name in enumerate(component_names):
            if i < len(component_scores):
                component_score = self._get_score_grade(component_scores[i])
                weighted_score = component_scores[i] * self.weights[component_name]
                total_score += weighted_score

        # Determine grade
        grade = self._get_score_grade(total_score)

        # Determine trend (if available)
        trend = self._calculate_trend(component_scores)

        return {
            "overall_score": total_score,
            "grade": grade,
            "trend": trend,
            "component_scores": {
                name: {
                    "score": score if i < len(component_scores) else 0,
                    "weight": self.weights[name],
                    "weighted_score": (
                        score * self.weights[name] if i < len(component_scores) else 0
                    ),
                    "grade": self._get_score_grade(score) if i < len(component_scores) else "F",
                }
                for i, (name, score) in enumerate(zip(component_names, component_scores, strict=False))
            },
            "breakdown": self._generate_breakdown(component_scores),
        }

    def _get_score_grade(self, score: float) -> str:
        """
        Convert score to letter grade.
        """
        if score >= 95:
            return "A+"
        if score >= 90:
            return "A"
        if score >= 85:
            return "B+"
        if score >= 80:
            return "B"
        if score >= 75:
            return "C+"
        if score >= 70:
            return "C"
        if score >= 65:
            return "D"
        return "F"

    def _calculate_trend(self, component_scores: list[float]) -> str | None:
        """
        Calculate quality trend (requires historical data)
        """
        try:
            # Load previous scores if available
            history_file = Path("quality_history.json")
            if not history_file.exists():
                return None

            with open(history_file) as f:
                history = json.load(f)

            if len(history) < 2:
                return None

            prev_score = history[-2].get("overall_score", 0)
            current_score = sum(component_scores) / len(component_scores)

            if current_score > prev_score + 2:
                return "📈 Improving"
            if current_score < prev_score - 2:
                return "📉 Declining"
            return "➡️ Stable"

        except:
            return None

    def _generate_breakdown(self, component_scores: list[float]) -> dict[str, Any]:
        """
        Generate detailed breakdown analysis.
        """
        strengths = []
        weaknesses = []
        recommendations = []

        component_names = list(self.weights.keys())

        for i, (name, score) in enumerate(zip(component_names, component_scores, strict=False)):
            if i < len(component_scores):
                grade = self._get_score_grade(score)

                if grade in ["A+", "A", "B+"]:
                    strengths.append(f"{name.replace('_', ' ').title()}: {grade}")
                elif grade in ["D", "F"]:
                    weaknesses.append(f"{name.replace('_', ' ').title()}: {grade}")
                    recommendations.append(self._get_component_recommendation(name, grade))

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
        }

    def _get_component_recommendation(self, component: str, grade: str) -> str:
        """
        Get recommendation for component based on grade.
        """
        recommendations = {
            "tests": {
                "D": "Run tests more frequently and add missing tests",
                "F": "Comprehensive test suite needed - implement unit, integration, and end-to-end tests",
            },
            "code_quality": {
                "D": "Address linting issues and fix type errors",
                "F": "Major code cleanup required - fix all linting and type issues",
            },
            "security": {
                "D": "Address security vulnerabilities and implement security best practices",
                "F": "Critical security issues - immediate attention required",
            },
            "complexity": {
                "D": "Refactor complex functions and improve code organization",
                "F": "Major refactoring needed - reduce complexity significantly",
            },
            "documentation": {
                "D": "Improve docstring coverage and API documentation",
                "F": "Complete documentation overhaul needed",
            },
        }

        return recommendations.get(component, {}).get(grade, "Review and improve this component")


def main():
    """
    Main quality score calculator entry point.
    """
    parser = argparse.ArgumentParser(
        description="Calculate comprehensive quality scores for ATOMS-PHENO project",
    )

    parser.add_argument(
        "--component",
        choices=["tests", "code_quality", "security", "complexity", "documentation"],
        action="append",
        help="Calculate specific component score(s)",
    )

    parser.add_argument("--data-file", help="JSON file with quality metrics data")

    parser.add_argument("--save-history", action="store_true", help="Save score to history file")

    parser.add_argument(
        "--show-trend", action="store_true", help="Calculate and show quality trend",
    )

    parser.add_argument(
        "--format", choices=["json", "text", "markdown"], default="text", help="Output format",
    )

    args = parser.parse_args()

    calculator = QualityScoreCalculator()

    # Load data
    if args.data_file and Path(args.data_file).exists():
        with open(args.data_file) as f:
            quality_data = json.load(f)
    else:
        # Generate sample data from project analysis
        quality_data = calculator._gather_project_metrics()

    # Calculate scores
    if args.component:
        component_scores = []
        for component in args.component:
            component_data = quality_data.get(component, {})
            score = calculator.calculate_component_score(component, component_data)
            component_scores.append(score)

        # For selected components, show individual scores
        for component, score in zip(args.component, component_scores, strict=False):
            grade = calculator._get_score_grade(score)
            print(f"{component}: {score:.1f}/100 ({grade})")
    else:
        # Calculate all component scores
        component_scores = [
            calculator.calculate_component_score(name, quality_data.get(name, {}))
            for name in calculator.weights.keys()
        ]

        # Calculate overall score
        result = calculator.calculate_overall_score(component_scores)

        # Save to history if requested
        if args.save_history:
            calculator._save_to_history(result)

        # Output results
        if args.format == "json":
            print(json.dumps(result, indent=2))
        elif args.format == "markdown":
            print(calculator._generate_markdown_report(result))
        else:
            calculator._print_text_report(result)

    def _gather_project_metrics(self) -> dict[str, Any]:
        """
        Gather real project metrics for scoring.
        """
        # This would integrate with actual project analysis tools
        # For now, return sample data
        return {
            "tests": {"passing": True, "coverage": 85, "avg_duration": 2.5, "flaky_rate": 0.08},
            "code_quality": {
                "total_issues": 15,
                "type_errors": 3,
                "format_issues": 2,
                "import_issues": 1,
            },
            "security": {
                "critical_vulns": 0,
                "high_vulns": 1,
                "medium_vulns": 3,
                "low_vulns": 5,
                "scan_coverage": 80,
                "best_practices_violations": 8,
            },
            "complexity": {
                "avg_complexity": 6.2,
                "max_complexity": 15,
                "maintainability_index": 72,
                "duplication_percent": 12,
            },
            "documentation": {
                "doc_coverage": 65,
                "api_docs": 70,
                "readme_quality": 80,
                "setup_docs": 75,
            },
        }

    def _save_to_history(self, result: dict[str, Any]) -> None:
        """
        Save result to history file.
        """
        history_file = Path("quality_history.json")

        history = []
        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)

        # Add current result
        history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "overall_score": result["overall_score"],
                "grade": result["grade"],
            },
        )

        # Keep last 50 entries
        history = history[-50:]

        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

    def _generate_markdown_report(self, result: dict[str, Any]) -> str:
        """
        Generate markdown report.
        """
        report = f"""# Quality Score Report

**Overall Score**: {result["overall_score"]:.1f}/100
**Grade**: {result["grade"]}
**Trend**: {result.get("trend", "No historical data")}

## Component Scores

"""

        for component, data in result["component_scores"].items():
            report += f"### {component.replace('_', ' ').title()}\n"
            report += f"- **Score**: {data['score']:.1f}/100\n"
            report += f"- **Grade**: {data['grade']}\n"
            report += f"- **Weight**: {data['weight']*100:.0f}%\n"
            report += f"- **Weighted Score**: {data['weighted_score']:.1f}\n\n"

        if result["breakdown"]["strengths"]:
            report += "### Strengths\n"
            for strength in result["breakdown"]["strengths"]:
                report += f"- ✅ {strength}\n"
            report += "\n"

        if result["breakdown"]["weaknesses"]:
            report += "### Areas for Improvement\n"
            for weakness in result["breakdown"]["weaknesses"]:
                report += f"- ⚠️ {weakness}\n"
            report += "\n"

        if result["breakdown"]["recommendations"]:
            report += "### Recommendations\n"
            for rec in result["breakdown"]["recommendations"]:
                report += f"- 💡 {rec}\n"

        return report

    def _print_text_report(self, result: dict[str, Any]) -> None:
        """
        Print text report.
        """
        print("🏆 ATOMS-PHENO Quality Score")
        print("=" * 40)
        print(f"Overall Score: {result['overall_score']:.1f}/100 ({result['grade']})")

        if result.get("trend"):
            print(f"Trend: {result['trend']}")

        print("\nComponent Scores:")
        print("-" * 20)

        for component, data in result["component_scores"].items():
            print(f"{component.replace('_', ' ').title():}")
            print(f"  Score: {data['score']:.1f}/100 ({data['grade']})")
            print(f"  Weight: {data['weight']*100:.0f}%")
            print(f"  Contribution: {data['weighted_score']:.1f}")
            print()


if __name__ == "__main__":
    from datetime import datetime

    main()
