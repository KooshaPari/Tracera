#!/usr/bin/env python3
"""
Quality Metrics and Analytics Collector
Comprehensive quality metrics collection and trend analysis.
"""

import argparse
import json
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class QualityMetric:
    """Quality metric measurement."""
    name: str
    value: float
    unit: str
    timestamp: float
    category: str
    trend: str = "stable"  # "improving", "stable", "declining"
    target: float | None = None
    threshold: float | None = None


@dataclass
class QualityTrend:
    """Quality trend analysis."""
    metric_name: str
    period: str
    trend_direction: str
    change_percent: float
    data_points: int
    forecast: float | None = None


class QualityMetricsCollector:
    """Comprehensive quality metrics collection system."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "quality"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = []
        self.trends = []

        # Quality targets and thresholds
        self.targets = {
            "test_coverage": 90.0,
            "code_quality_score": 85.0,
            "security_score": 95.0,
            "performance_score": 80.0,
            "documentation_score": 85.0,
            "maintainability_index": 80.0,
            "cyclomatic_complexity": 10.0,
            "technical_debt_ratio": 5.0,
        }

    def collect_all_metrics(self) -> dict[str, Any]:
        """Collect all quality metrics."""
        print("📊 Collecting Quality Metrics...")

        # Collect different types of metrics
        self._collect_test_metrics()
        self._collect_code_quality_metrics()
        self._collect_security_metrics()
        self._collect_performance_metrics()
        self._collect_documentation_metrics()
        self._collect_maintainability_metrics()
        self._collect_complexity_metrics()
        self._collect_technical_debt_metrics()

        # Analyze trends
        self._analyze_trends()

        # Generate comprehensive report
        return self._generate_quality_report()

    def _collect_test_metrics(self) -> None:
        """Collect test-related metrics."""
        print("  🧪 Collecting test metrics...")

        # Test coverage
        coverage_file = self.project_root / "coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)

            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
            self.metrics.append(QualityMetric(
                name="test_coverage",
                value=total_coverage,
                unit="percent",
                timestamp=time.time(),
                category="testing",
                target=self.targets["test_coverage"],
                threshold=80.0,
            ))

            # Line coverage
            line_coverage = coverage_data.get("totals", {}).get("covered_lines", 0)
            total_lines = coverage_data.get("totals", {}).get("num_statements", 0)
            if total_lines > 0:
                line_coverage_percent = (line_coverage / total_lines) * 100
                self.metrics.append(QualityMetric(
                    name="line_coverage",
                    value=line_coverage_percent,
                    unit="percent",
                    timestamp=time.time(),
                    category="testing",
                    target=90.0,
                    threshold=80.0,
                ))

        # Test execution metrics
        self._collect_test_execution_metrics()

    def _collect_test_execution_metrics(self) -> None:
        """Collect test execution metrics."""
        try:
            # Run pytest with JSON output
            result = subprocess.run([
                "python", "-m", "pytest", "tests/", "--json-report",
                "--json-report-file=test_report.json", "-q",
            ], check=False, capture_output=True, text=True, cwd=self.project_root, timeout=300)

            test_report_file = self.project_root / "test_report.json"
            if test_report_file.exists():
                with open(test_report_file) as f:
                    test_data = json.load(f)

                summary = test_data.get("summary", {})
                total_tests = summary.get("total", 0)
                passed_tests = summary.get("passed", 0)
                failed_tests = summary.get("failed", 0)

                if total_tests > 0:
                    success_rate = (passed_tests / total_tests) * 100
                    self.metrics.append(QualityMetric(
                        name="test_success_rate",
                        value=success_rate,
                        unit="percent",
                        timestamp=time.time(),
                        category="testing",
                        target=95.0,
                        threshold=90.0,
                    ))

                self.metrics.append(QualityMetric(
                    name="total_tests",
                    value=total_tests,
                    unit="count",
                    timestamp=time.time(),
                    category="testing",
                ))

                self.metrics.append(QualityMetric(
                    name="failed_tests",
                    value=failed_tests,
                    unit="count",
                    timestamp=time.time(),
                    category="testing",
                    threshold=0.0,
                ))

        except Exception as e:
            print(f"Error collecting test execution metrics: {e}")

    def _collect_code_quality_metrics(self) -> None:
        """Collect code quality metrics."""
        print("  🔍 Collecting code quality metrics...")

        # Ruff linting
        try:
            result = subprocess.run([
                "python", "-m", "ruff", "check", "src/", "--output-format=json",
            ], check=False, capture_output=True, text=True, cwd=self.project_root, timeout=120)

            if result.returncode == 0:
                # No issues found
                self.metrics.append(QualityMetric(
                    name="ruff_violations",
                    value=0,
                    unit="count",
                    timestamp=time.time(),
                    category="code_quality",
                    threshold=0.0,
                ))
            else:
                try:
                    ruff_data = json.loads(result.stdout)
                    violation_count = len(ruff_data)
                    self.metrics.append(QualityMetric(
                        name="ruff_violations",
                        value=violation_count,
                        unit="count",
                        timestamp=time.time(),
                        category="code_quality",
                        threshold=0.0,
                    ))
                except json.JSONDecodeError:
                    # Count lines in output
                    violation_count = len([line for line in result.stdout.split("\n") if line.strip()])
                    self.metrics.append(QualityMetric(
                        name="ruff_violations",
                        value=violation_count,
                        unit="count",
                        timestamp=time.time(),
                        category="code_quality",
                        threshold=0.0,
                    ))

        except Exception as e:
            print(f"Error collecting ruff metrics: {e}")

        # MyPy type checking
        try:
            result = subprocess.run([
                "python", "-m", "mypy", "src/", "--json-report", "mypy_report.json",
            ], check=False, capture_output=True, text=True, cwd=self.project_root, timeout=300)

            mypy_report_file = self.project_root / "mypy_report.json"
            if mypy_report_file.exists():
                with open(mypy_report_file) as f:
                    mypy_data = json.load(f)

                error_count = mypy_data.get("summary", {}).get("error_count", 0)
                self.metrics.append(QualityMetric(
                    name="mypy_errors",
                    value=error_count,
                    unit="count",
                    timestamp=time.time(),
                    category="code_quality",
                    threshold=0.0,
                ))

        except Exception as e:
            print(f"Error collecting mypy metrics: {e}")

    def _collect_security_metrics(self) -> None:
        """Collect security-related metrics."""
        print("  🔒 Collecting security metrics...")

        # Bandit security scan
        bandit_file = self.project_root / "bandit-report.json"
        if bandit_file.exists():
            with open(bandit_file) as f:
                bandit_data = json.load(f)

            results = bandit_data.get("results", [])
            high_severity = len([r for r in results if r.get("issue_severity") == "HIGH"])
            medium_severity = len([r for r in results if r.get("issue_severity") == "MEDIUM"])
            low_severity = len([r for r in results if r.get("issue_severity") == "LOW"])

            self.metrics.append(QualityMetric(
                name="security_high_severity",
                value=high_severity,
                unit="count",
                timestamp=time.time(),
                category="security",
                threshold=0.0,
            ))

            self.metrics.append(QualityMetric(
                name="security_medium_severity",
                value=medium_severity,
                unit="count",
                timestamp=time.time(),
                category="security",
                threshold=5.0,
            ))

            self.metrics.append(QualityMetric(
                name="security_low_severity",
                value=low_severity,
                unit="count",
                timestamp=time.time(),
                category="security",
                threshold=10.0,
            ))

            # Calculate security score
            total_issues = high_severity + medium_severity + low_severity
            security_score = max(0, 100 - (high_severity * 20 + medium_severity * 10 + low_severity * 2))
            self.metrics.append(QualityMetric(
                name="security_score",
                value=security_score,
                unit="percent",
                timestamp=time.time(),
                category="security",
                target=self.targets["security_score"],
                threshold=80.0,
            ))

    def _collect_performance_metrics(self) -> None:
        """Collect performance metrics."""
        print("  ⚡ Collecting performance metrics...")

        # Check for performance test results
        performance_reports = list(self.project_root.glob("reports/performance/*.json"))
        if performance_reports:
            latest_report = max(performance_reports, key=lambda x: x.stat().st_mtime)
            with open(latest_report) as f:
                perf_data = json.load(f)

            # Extract performance metrics
            for result in perf_data.get("results", []):
                if "metrics" in result:
                    for metric in result["metrics"]:
                        if metric["name"] == "avg_response_time":
                            self.metrics.append(QualityMetric(
                                name="avg_response_time",
                                value=metric["value"],
                                unit=metric["unit"],
                                timestamp=time.time(),
                                category="performance",
                                threshold=2.0,
                            ))
                        elif metric["name"] == "throughput":
                            self.metrics.append(QualityMetric(
                                name="throughput",
                                value=metric["value"],
                                unit=metric["unit"],
                                timestamp=time.time(),
                                category="performance",
                                threshold=10.0,
                            ))

    def _collect_documentation_metrics(self) -> None:
        """Collect documentation metrics."""
        print("  📚 Collecting documentation metrics...")

        # Count documentation files
        doc_files = list(self.project_root.rglob("*.md"))
        self.metrics.append(QualityMetric(
            name="documentation_files",
            value=len(doc_files),
            unit="count",
            timestamp=time.time(),
            category="documentation",
        ))

        # Check for README
        readme_files = list(self.project_root.glob("README*.md"))
        self.metrics.append(QualityMetric(
            name="has_readme",
            value=1 if readme_files else 0,
            unit="boolean",
            timestamp=time.time(),
            category="documentation",
            target=1.0,
        ))

        # Check for docstrings in Python files
        python_files = list(self.project_root.rglob("src/**/*.py"))
        total_functions = 0
        documented_functions = 0

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Count function definitions
                import re
                functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
                total_functions += len(functions)

                # Count documented functions
                for func_name in functions:
                    func_pattern = rf'def\s+{func_name}\s*\([^)]*\):\s*\n\s*""".*?"""'
                    if re.search(func_pattern, content, re.DOTALL):
                        documented_functions += 1

            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        if total_functions > 0:
            docstring_coverage = (documented_functions / total_functions) * 100
            self.metrics.append(QualityMetric(
                name="docstring_coverage",
                value=docstring_coverage,
                unit="percent",
                timestamp=time.time(),
                category="documentation",
                target=80.0,
                threshold=60.0,
            ))

    def _collect_maintainability_metrics(self) -> None:
        """Collect maintainability metrics."""
        print("  🔧 Collecting maintainability metrics...")

        # Count lines of code
        python_files = list(self.project_root.rglob("src/**/*.py"))
        total_lines = 0
        total_files = len(python_files)

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    lines = f.readlines()
                    total_lines += len(lines)
            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        self.metrics.append(QualityMetric(
            name="total_lines_of_code",
            value=total_lines,
            unit="lines",
            timestamp=time.time(),
            category="maintainability",
        ))

        self.metrics.append(QualityMetric(
            name="total_python_files",
            value=total_files,
            unit="count",
            timestamp=time.time(),
            category="maintainability",
        ))

        # Average file size
        if total_files > 0:
            avg_file_size = total_lines / total_files
            self.metrics.append(QualityMetric(
                name="avg_file_size",
                value=avg_file_size,
                unit="lines",
                timestamp=time.time(),
                category="maintainability",
                threshold=500.0,
            ))

    def _collect_complexity_metrics(self) -> None:
        """Collect complexity metrics."""
        print("  🧮 Collecting complexity metrics...")

        # This would typically use tools like radon or xenon
        # For now, we'll do basic analysis
        python_files = list(self.project_root.rglob("src/**/*.py"))

        total_functions = 0
        complex_functions = 0

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Basic complexity analysis (count control structures)
                import re
                functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
                total_functions += len(functions)

                # Simple complexity estimation
                for func_name in functions:
                    func_pattern = rf"def\s+{func_name}\s*\([^)]*\):(.*?)(?=def|\Z)"
                    match = re.search(func_pattern, content, re.DOTALL)
                    if match:
                        func_body = match.group(1)
                        # Count control structures
                        complexity = len(re.findall(r"\b(if|for|while|try|except|with)\b", func_body))
                        if complexity > 10:  # Threshold for complex functions
                            complex_functions += 1

            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        if total_functions > 0:
            complexity_ratio = (complex_functions / total_functions) * 100
            self.metrics.append(QualityMetric(
                name="complex_functions_ratio",
                value=complexity_ratio,
                unit="percent",
                timestamp=time.time(),
                category="complexity",
                threshold=20.0,
            ))

    def _collect_technical_debt_metrics(self) -> None:
        """Collect technical debt metrics."""
        print("  💳 Collecting technical debt metrics...")

        # Count TODO/FIXME comments
        python_files = list(self.project_root.rglob("src/**/*.py"))
        todo_count = 0
        fixme_count = 0

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                todo_count += content.count("TODO")
                todo_count += content.count("todo")
                fixme_count += content.count("FIXME")
                fixme_count += content.count("fixme")

            except Exception as e:
                print(f"Error processing {py_file}: {e}")

        self.metrics.append(QualityMetric(
            name="todo_comments",
            value=todo_count,
            unit="count",
            timestamp=time.time(),
            category="technical_debt",
            threshold=50.0,
        ))

        self.metrics.append(QualityMetric(
            name="fixme_comments",
            value=fixme_count,
            unit="count",
            timestamp=time.time(),
            category="technical_debt",
            threshold=10.0,
        ))

        # Calculate technical debt ratio
        total_lines = sum(len(open(f, encoding="utf-8").readlines()) for f in python_files)
        if total_lines > 0:
            debt_ratio = ((todo_count + fixme_count) / total_lines) * 100
            self.metrics.append(QualityMetric(
                name="technical_debt_ratio",
                value=debt_ratio,
                unit="percent",
                timestamp=time.time(),
                category="technical_debt",
                target=self.targets["technical_debt_ratio"],
                threshold=10.0,
            ))

    def _analyze_trends(self) -> None:
        """Analyze quality trends."""
        print("  📈 Analyzing quality trends...")

        # Group metrics by name
        metrics_by_name = {}
        for metric in self.metrics:
            name = metric.name
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append(metric)

        # Calculate trends for each metric
        for name, metrics_list in metrics_by_name.items():
            if len(metrics_list) > 1:
                # Sort by timestamp
                sorted_metrics = sorted(metrics_list, key=lambda x: x.timestamp)

                # Calculate trend
                first_value = sorted_metrics[0].value
                last_value = sorted_metrics[-1].value

                if first_value == 0:
                    change_percent = 0
                else:
                    change_percent = ((last_value - first_value) / first_value) * 100

                if change_percent > 5:
                    trend_direction = "improving"
                elif change_percent < -5:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"

                self.trends.append(QualityTrend(
                    metric_name=name,
                    period="recent",
                    trend_direction=trend_direction,
                    change_percent=change_percent,
                    data_points=len(metrics_list),
                ))

    def _generate_quality_report(self) -> dict[str, Any]:
        """Generate comprehensive quality report."""
        print("📊 Generating Quality Report...")

        # Calculate overall quality score
        quality_score = self._calculate_overall_quality_score()

        # Group metrics by category
        metrics_by_category = {}
        for metric in self.metrics:
            category = metric.category
            if category not in metrics_by_category:
                metrics_by_category[category] = []
            metrics_by_category[category].append(asdict(metric))

        # Calculate category scores
        category_scores = {}
        for category, metrics in metrics_by_category.items():
            category_scores[category] = self._calculate_category_score(metrics)

        # Generate recommendations
        recommendations = self._generate_quality_recommendations()

        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_quality_score": quality_score,
            "category_scores": category_scores,
            "metrics_by_category": metrics_by_category,
            "trends": [asdict(trend) for trend in self.trends],
            "targets": self.targets,
            "recommendations": recommendations,
            "summary": {
                "total_metrics": len(self.metrics),
                "categories": len(metrics_by_category),
                "trends_analyzed": len(self.trends),
                "improving_trends": len([t for t in self.trends if t.trend_direction == "improving"]),
                "declining_trends": len([t for t in self.trends if t.trend_direction == "declining"]),
            },
        }

        # Save report
        self._save_quality_report(report)

        return report

    def _calculate_overall_quality_score(self) -> float:
        """Calculate overall quality score."""
        if not self.metrics:
            return 0.0

        # Weight different categories
        category_weights = {
            "testing": 0.25,
            "code_quality": 0.20,
            "security": 0.20,
            "performance": 0.15,
            "documentation": 0.10,
            "maintainability": 0.10,
        }

        weighted_score = 0.0
        total_weight = 0.0

        # Group metrics by category
        metrics_by_category = {}
        for metric in self.metrics:
            category = metric.category
            if category not in metrics_by_category:
                metrics_by_category[category] = []
            metrics_by_category[category].append(metric)

        # Calculate weighted score
        for category, metrics in metrics_by_category.items():
            if category in category_weights:
                category_score = self._calculate_category_score(metrics)
                weight = category_weights[category]
                weighted_score += category_score * weight
                total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _calculate_category_score(self, metrics: list[dict[str, Any]]) -> float:
        """Calculate score for a category."""
        if not metrics:
            return 0.0

        # Calculate score based on targets and thresholds
        total_score = 0.0
        valid_metrics = 0

        for metric in metrics:
            value = metric["value"]
            target = metric.get("target")
            threshold = metric.get("threshold")

            if target is not None:
                # Score based on target (higher is better)
                if value >= target:
                    score = 100.0
                elif threshold is not None and value >= threshold:
                    # Linear interpolation between threshold and target
                    score = 50.0 + ((value - threshold) / (target - threshold)) * 50.0
                else:
                    score = (value / target) * 50.0
            elif threshold is not None:
                # Score based on threshold (lower is better)
                if value <= threshold:
                    score = 100.0
                else:
                    score = max(0, 100.0 - (value - threshold) * 10.0)
            else:
                # Default scoring
                score = min(100.0, value)

            total_score += score
            valid_metrics += 1

        return total_score / valid_metrics if valid_metrics > 0 else 0.0

    def _generate_quality_recommendations(self) -> list[str]:
        """Generate quality improvement recommendations."""
        recommendations = []

        # Check for low scores
        for metric in self.metrics:
            if metric.target and metric.value < metric.target:
                recommendations.append(f"Improve {metric.name}: {metric.value:.1f}% (target: {metric.target}%)")

            if metric.threshold and metric.value > metric.threshold:
                recommendations.append(f"Address {metric.name}: {metric.value:.1f} (threshold: {metric.threshold})")

        # Check for declining trends
        for trend in self.trends:
            if trend.trend_direction == "declining" and abs(trend.change_percent) > 10:
                recommendations.append(f"Reverse declining trend in {trend.metric_name}: {trend.change_percent:.1f}%")

        return recommendations

    def _save_quality_report(self, report: dict[str, Any]) -> None:
        """Save quality report."""
        # Save JSON report
        json_file = self.reports_dir / f"quality_metrics_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save summary report
        summary_file = self.reports_dir / f"quality_summary_{int(time.time())}.md"
        self._save_quality_summary(report, summary_file)

        print("📊 Quality reports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Summary: {summary_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Quality Metrics Collector")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    collector = QualityMetricsCollector(args.project_root)
    report = collector.collect_all_metrics()

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        # Pretty print format
        output = f"""
📊 QUALITY METRICS REPORT
{'=' * 50}
Overall Quality Score: {report['overall_quality_score']:.1f}/100

Category Scores:
"""
        for category, score in report["category_scores"].items():
            output += f"  {category.title()}: {score:.1f}/100\n"

        output += f"\nTrends Analyzed: {report['summary']['trends_analyzed']}\n"
        output += f"Improving Trends: {report['summary']['improving_trends']}\n"
        output += f"Declining Trends: {report['summary']['declining_trends']}\n"

        if report["recommendations"]:
            output += "\nRecommendations:\n"
            for rec in report["recommendations"]:
                output += f"  • {rec}\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
