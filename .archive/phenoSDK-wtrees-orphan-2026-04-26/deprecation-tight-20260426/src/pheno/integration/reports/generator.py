"""Report generator implementation for pheno-integration.

This module provides comprehensive report generation tools for integration validation
and performance benchmarking.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..benchmarks.performance import BenchmarkResult
from ..migration.validator import MigrationResult
from ..validation.types import ValidationResult


class ReportFormat(Enum):
    """
    Report output formats.
    """

    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"
    PDF = "pdf"

    def __str__(self) -> str:
        return self.value


@dataclass
class ReportConfig:
    """
    Report configuration.
    """

    output_dir: str = "reports"
    format: ReportFormat = ReportFormat.HTML
    include_charts: bool = True
    include_details: bool = True
    include_summary: bool = True
    template: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ReportGenerator:
    """
    Report generator implementation.
    """

    def __init__(self, config: ReportConfig | None = None):
        self.config = config or ReportConfig()
        self._reports: list[dict[str, Any]] = []

    def generate_integration_report(self, validation_results: list[ValidationResult]) -> str:
        """Generate integration validation report.

        Args:
            validation_results: List of validation results

        Returns:
            Path to generated report
        """
        try:
            # Create output directory
            os.makedirs(self.config.output_dir, exist_ok=True)

            # Generate report content
            if self.config.format == ReportFormat.HTML:
                content = self._generate_html_report(validation_results)
                extension = "html"
            elif self.config.format == ReportFormat.JSON:
                content = self._generate_json_report(validation_results)
                extension = "json"
            elif self.config.format == ReportFormat.MARKDOWN:
                content = self._generate_markdown_report(validation_results)
                extension = "md"
            else:
                raise ValueError(f"Unsupported report format: {self.config.format}")

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integration_report_{timestamp}.{extension}"
            filepath = os.path.join(self.config.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Store report metadata
            self._reports.append(
                {
                    "type": "integration",
                    "filename": filename,
                    "filepath": filepath,
                    "timestamp": datetime.now().isoformat(),
                    "format": self.config.format.value,
                },
            )

            return filepath

        except Exception as e:
            raise Exception(f"Failed to generate integration report: {e}")

    def generate_performance_report(self, benchmark_results: list[BenchmarkResult]) -> str:
        """Generate performance benchmark report.

        Args:
            benchmark_results: List of benchmark results

        Returns:
            Path to generated report
        """
        try:
            # Create output directory
            os.makedirs(self.config.output_dir, exist_ok=True)

            # Generate report content
            if self.config.format == ReportFormat.HTML:
                content = self._generate_html_performance_report(benchmark_results)
                extension = "html"
            elif self.config.format == ReportFormat.JSON:
                content = self._generate_json_performance_report(benchmark_results)
                extension = "json"
            elif self.config.format == ReportFormat.MARKDOWN:
                content = self._generate_markdown_performance_report(benchmark_results)
                extension = "md"
            else:
                raise ValueError(f"Unsupported report format: {self.config.format}")

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.{extension}"
            filepath = os.path.join(self.config.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Store report metadata
            self._reports.append(
                {
                    "type": "performance",
                    "filename": filename,
                    "filepath": filepath,
                    "timestamp": datetime.now().isoformat(),
                    "format": self.config.format.value,
                },
            )

            return filepath

        except Exception as e:
            raise Exception(f"Failed to generate performance report: {e}")

    def generate_migration_report(self, migration_results: list[MigrationResult]) -> str:
        """Generate migration validation report.

        Args:
            migration_results: List of migration results

        Returns:
            Path to generated report
        """
        try:
            # Create output directory
            os.makedirs(self.config.output_dir, exist_ok=True)

            # Generate report content
            if self.config.format == ReportFormat.HTML:
                content = self._generate_html_migration_report(migration_results)
                extension = "html"
            elif self.config.format == ReportFormat.JSON:
                content = self._generate_json_migration_report(migration_results)
                extension = "json"
            elif self.config.format == ReportFormat.MARKDOWN:
                content = self._generate_markdown_migration_report(migration_results)
                extension = "md"
            else:
                raise ValueError(f"Unsupported report format: {self.config.format}")

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"migration_report_{timestamp}.{extension}"
            filepath = os.path.join(self.config.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Store report metadata
            self._reports.append(
                {
                    "type": "migration",
                    "filename": filename,
                    "filepath": filepath,
                    "timestamp": datetime.now().isoformat(),
                    "format": self.config.format.value,
                },
            )

            return filepath

        except Exception as e:
            raise Exception(f"Failed to generate migration report: {e}")

    def generate_comprehensive_report(
        self,
        validation_results: list[ValidationResult],
        benchmark_results: list[BenchmarkResult],
        migration_results: list[MigrationResult],
    ) -> str:
        """Generate comprehensive report combining all results.

        Args:
            validation_results: List of validation results
            benchmark_results: List of benchmark results
            migration_results: List of migration results

        Returns:
            Path to generated report
        """
        try:
            # Create output directory
            os.makedirs(self.config.output_dir, exist_ok=True)

            # Generate report content
            if self.config.format == ReportFormat.HTML:
                content = self._generate_html_comprehensive_report(
                    validation_results, benchmark_results, migration_results,
                )
                extension = "html"
            elif self.config.format == ReportFormat.JSON:
                content = self._generate_json_comprehensive_report(
                    validation_results, benchmark_results, migration_results,
                )
                extension = "json"
            elif self.config.format == ReportFormat.MARKDOWN:
                content = self._generate_markdown_comprehensive_report(
                    validation_results, benchmark_results, migration_results,
                )
                extension = "md"
            else:
                raise ValueError(f"Unsupported report format: {self.config.format}")

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_report_{timestamp}.{extension}"
            filepath = os.path.join(self.config.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Store report metadata
            self._reports.append(
                {
                    "type": "comprehensive",
                    "filename": filename,
                    "filepath": filepath,
                    "timestamp": datetime.now().isoformat(),
                    "format": self.config.format.value,
                },
            )

            return filepath

        except Exception as e:
            raise Exception(f"Failed to generate comprehensive report: {e}")

    def get_reports(self) -> list[dict[str, Any]]:
        """
        Get all generated reports.
        """
        return self._reports

    def _generate_html_report(self, validation_results: list[ValidationResult]) -> str:
        """
        Generate HTML report for validation results.
        """
        # Calculate summary
        total = len(validation_results)
        passed = len([r for r in validation_results if r.status.value == "passed"])
        failed = len([r for r in validation_results if r.status.value == "failed"])
        error = len([r for r in validation_results if r.status.value == "error"])

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Integration Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .results {{ margin: 20px 0; }}
        .result {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .error {{ background-color: #f5c6cb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Integration Validation Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {total}</p>
        <p>Passed: {passed}</p>
        <p>Failed: {failed}</p>
        <p>Error: {error}</p>
        <p>Success Rate: {(passed/total)*100:.1f}%</p>
    </div>

    <div class="results">
        <h2>Test Results</h2>
        """

        for result in validation_results:
            status_class = result.status.value
            html += f"""
        <div class="result {status_class}">
            <h3>{result.test_name}</h3>
            <p>Status: {result.status.value}</p>
            <p>Duration: {result.duration:.3f}s</p>
            {f'<p>Error: {result.error_message}</p>' if result.error_message else ''}
        </div>
            """

        html += """
    </div>
</body>
</html>
        """

        return html

    def _generate_json_report(self, validation_results: list[ValidationResult]) -> str:
        """
        Generate JSON report for validation results.
        """
        data = {
            "report_type": "integration_validation",
            "timestamp": datetime.now().isoformat(),
            "summary": self._calculate_summary(validation_results),
            "results": [result.to_dict() for result in validation_results],
        }
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self, validation_results: list[ValidationResult]) -> str:
        """
        Generate Markdown report for validation results.
        """
        summary = self._calculate_summary(validation_results)

        md = self._build_markdown_header()
        md += self._build_markdown_summary(summary)
        md += self._build_markdown_test_results(validation_results)

        return md

    def _build_markdown_header(self) -> str:
        """
        Build the markdown report header.
        """
        return f"""# Integration Validation Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""

    def _build_markdown_summary(self, summary: dict[str, Any]) -> str:
        """
        Build the markdown summary section.
        """
        return f"""## Summary

- **Total Tests**: {summary['total']}
- **Passed**: {summary['passed']}
- **Failed**: {summary['failed']}
- **Error**: {summary['error']}
- **Success Rate**: {summary['success_rate']:.1f}%

"""

    def _build_markdown_test_results(self, validation_results: list[ValidationResult]) -> str:
        """
        Build the markdown test results section.
        """
        md = "## Test Results\n\n"

        for result in validation_results:
            md += self._build_markdown_test_result(result)

        return md

    def _build_markdown_test_result(self, result: ValidationResult) -> str:
        """
        Build markdown for a single test result.
        """
        status_emoji = self._get_status_emoji(result.status.value)

        md = f"""### {status_emoji} {result.test_name}

- **Status**: {result.status.value}
- **Duration**: {result.duration:.3f}s
"""

        if result.error_message:
            md += f"- **Error**: {result.error_message}\n"

        md += "\n"
        return md

    def _get_status_emoji(self, status: str) -> str:
        """
        Get emoji for test status.
        """
        if status == "passed":
            return "✅"
        if status == "failed":
            return "❌"
        return "⚠️"

    def _calculate_summary(self, results: list[ValidationResult]) -> dict[str, Any]:
        """
        Calculate summary statistics.
        """
        if not results:
            return {"total": 0, "passed": 0, "failed": 0, "error": 0}

        total = len(results)
        passed = len([r for r in results if r.status.value == "passed"])
        failed = len([r for r in results if r.status.value == "failed"])
        error = len([r for r in results if r.status.value == "error"])

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error": error,
            "success_rate": (passed / total) * 100 if total > 0 else 0,
        }

    # Placeholder methods for other report types
    def _generate_html_performance_report(self, benchmark_results: list[BenchmarkResult]) -> str:
        """
        Generate HTML performance report.
        """
        return (
            "<html><body><h1>Performance Report</h1><p>Performance report content</p></body></html>"
        )

    def _generate_json_performance_report(self, benchmark_results: list[BenchmarkResult]) -> str:
        """
        Generate JSON performance report.
        """
        data = {
            "report_type": "performance_benchmark",
            "timestamp": datetime.now().isoformat(),
            "results": [result.to_dict() for result in benchmark_results],
        }
        return json.dumps(data, indent=2)

    def _generate_markdown_performance_report(
        self, benchmark_results: list[BenchmarkResult],
    ) -> str:
        """
        Generate Markdown performance report.
        """
        return "# Performance Report\n\nPerformance report content"

    def _generate_html_migration_report(self, migration_results: list[MigrationResult]) -> str:
        """
        Generate HTML migration report.
        """
        return "<html><body><h1>Migration Report</h1><p>Migration report content</p></body></html>"

    def _generate_json_migration_report(self, migration_results: list[MigrationResult]) -> str:
        """
        Generate JSON migration report.
        """
        data = {
            "report_type": "migration_validation",
            "timestamp": datetime.now().isoformat(),
            "results": [result.to_dict() for result in migration_results],
        }
        return json.dumps(data, indent=2)

    def _generate_markdown_migration_report(self, migration_results: list[MigrationResult]) -> str:
        """
        Generate Markdown migration report.
        """
        return "# Migration Report\n\nMigration report content"

    def _generate_html_comprehensive_report(
        self,
        validation_results: list[ValidationResult],
        benchmark_results: list[BenchmarkResult],
        migration_results: list[MigrationResult],
    ) -> str:
        """
        Generate HTML comprehensive report.
        """
        return "<html><body><h1>Comprehensive Report</h1><p>Comprehensive report content</p></body></html>"

    def _generate_json_comprehensive_report(
        self,
        validation_results: list[ValidationResult],
        benchmark_results: list[BenchmarkResult],
        migration_results: list[MigrationResult],
    ) -> str:
        """
        Generate JSON comprehensive report.
        """
        data = {
            "report_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "validation_results": [result.to_dict() for result in validation_results],
            "benchmark_results": [result.to_dict() for result in benchmark_results],
            "migration_results": [result.to_dict() for result in migration_results],
        }
        return json.dumps(data, indent=2)

    def _generate_markdown_comprehensive_report(
        self,
        validation_results: list[ValidationResult],
        benchmark_results: list[BenchmarkResult],
        migration_results: list[MigrationResult],
    ) -> str:
        """
        Generate Markdown comprehensive report.
        """
        return "# Comprehensive Report\n\nComprehensive report content"
