#!/usr/bin/env python3
"""
Validate that code quality gates meet requirements.
"""

import json
import os
import sys


class QualityGateValidator:
    """
    Validates quality gates against thresholds.
    """

    def __init__(self):
        self.thresholds = {
            "ruff_max_issues": 50,
            "mypy_max_errors": 20,
            "prospector_max_issues": 100,
            "complexity_max_complexity": 10,  # Maximum McCabe complexity
            "maintainability_min_score": 65,  # Minimum maintainability index
            "duplicated_lines_max_percent": 3,
            "test_coverage_min_percent": 65,
        }

        self.failures = []

    def validate_ruff_issues(self, report_path: str):
        """
        Validate Ruff issues count.
        """
        if not os.path.exists(report_path):
            self.failures.append(f"Ruff report not found: {report_path}")
            return

        try:
            with open(report_path) as f:
                data = json.load(f)

            issue_count = len(data)
            if issue_count > self.thresholds["ruff_max_issues"]:
                self.failures.append(
                    f"Ruff issues ({issue_count}) exceed threshold ({self.thresholds['ruff_max_issues']})",
                )
            else:
                print(f"✅ Ruff issues ({issue_count}) within threshold")

        except (json.JSONDecodeError, KeyError) as e:
            self.failures.append(f"Failed to parse Ruff report: {e}")

    def validate_mypy_errors(self, report_dir: str):
        """
        Validate MyPy error count.
        """
        report_path = os.path.join(report_dir, "report.json")
        if not os.path.exists(report_path):
            self.failures.append(f"MyPy report not found: {report_path}")
            return

        try:
            with open(report_path) as f:
                data = json.load(f)

            error_count = len(data.get("errors", []))
            if error_count > self.thresholds["mypy_max_errors"]:
                self.failures.append(
                    f"MyPy errors ({error_count}) exceed threshold ({self.thresholds['mypy_max_errors']})",
                )
            else:
                print(f"✅ MyPy errors ({error_count}) within threshold")

        except (json.JSONDecodeError, KeyError) as e:
            self.failures.append(f"Failed to parse MyPy report: {e}")

    def validate_prospector_issues(self, report_path: str):
        """
        Validate Prospector issues count.
        """
        if not os.path.exists(report_path):
            self.failures.append(f"Prospector report not found: {report_path}")
            return

        try:
            with open(report_path) as f:
                data = json.load(f)

            messages = data.get("messages", [])
            issue_count = len(messages)

            if issue_count > self.thresholds["prospector_max_issues"]:
                self.failures.append(
                    f"Prospector issues ({issue_count}) exceed threshold ({self.thresholds['prospector_max_issues']})",
                )
            else:
                print(f"✅ Prospector issues ({issue_count}) within threshold")

        except (json.JSONDecodeError, KeyError) as e:
            self.failures.append(f"Failed to parse Prospector report: {e}")

    def validate_complexity(self, report_path: str):
        """
        Validate cyclomatic complexity.
        """
        if not os.path.exists(report_path):
            self.failures.append(f"Complexity report not found: {report_path}")
            return

        try:
            with open(report_path) as f:
                data = json.load(f)

            max_complexity = 0
            for filename, functions in data.items():
                for func_name, metrics in functions.items():
                    complexity = metrics.get("complexity", 0)
                    max_complexity = max(max_complexity, complexity)

                    if complexity > self.thresholds["complexity_max_complexity"]:
                        self.failures.append(
                            f"Complexity too high in {filename}:{func_name} ({complexity} > {self.thresholds['complexity_max_complexity']})",
                        )

            if max_complexity <= self.thresholds["complexity_max_complexity"]:
                print(f"✅ Maximum complexity ({max_complexity}) within threshold")

        except (json.JSONDecodeError, KeyError) as e:
            self.failures.append(f"Failed to parse complexity report: {e}")

    def validate_maintainability(self, report_path: str):
        """
        Validate maintainability index.
        """
        if not os.path.exists(report_path):
            self.failures.append(f"Maintainability report not found: {report_path}")
            return

        try:
            with open(report_path) as f:
                data = json.load(f)

            min_score = 100
            for filename, metrics in data.items():
                score = metrics.get("mi", 100)
                min_score = min(min_score, score)

                if score < self.thresholds["maintainability_min_score"]:
                    self.failures.append(
                        f"Maintainability index too low in {filename} ({score:.1f} < {self.thresholds['maintainability_min_score']})",
                    )

            if min_score >= self.thresholds["maintainability_min_score"]:
                print(f"✅ Minimum maintainability index ({min_score:.1f}) meets threshold")

        except (json.JSONDecodeError, KeyError) as e:
            self.failures.append(f"Failed to parse maintainability report: {e}")

    def validate_test_coverage(self):
        """
        Validate test coverage from pytest coverage.
        """
        coverage_file = "coverage.xml"
        if not os.path.exists(coverage_file):
            self.failures.append("Coverage XML file not found")
            return

        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(coverage_file)
            root = tree.getroot()

            # Find overall coverage
            coverage_elem = root if root.tag == "coverage" else root.find(".//coverage")
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get("line-rate", 0))
                coverage_percent = line_rate * 100

                if coverage_percent < self.thresholds["test_coverage_min_percent"]:
                    self.failures.append(
                        f"Test coverage ({coverage_percent:.1f}%) below threshold ({self.thresholds['test_coverage_min_percent']}%)",
                    )
                else:
                    print(f"✅ Test coverage ({coverage_percent:.1f}%) meets threshold")
            else:
                self.failures.append("Could not parse coverage percentage")

        except Exception as e:
            self.failures.append(f"Failed to parse coverage XML: {e}")

    def validate_loc_guard(self):
        """
        Validate line count hasn't exceeded threshold.
        """
        try:
            import subprocess

            result = subprocess.run(
                ["python", "scripts/count_loc.py", "--threshold", "8500", "--json"],
                check=False, capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.failures.append(f"LOC guard failed: {result.stderr}")
            else:
                data = json.loads(result.stdout)
                if data.get("exceeded", False):
                    self.failures.append(
                        f"LOC count ({data['total_loc']}) exceeds threshold ({data['threshold']})",
                    )
                else:
                    print(f"✅ LOC count ({data['total_loc']}) within threshold")

        except Exception as e:
            self.failures.append(f"Failed to check LOC guard: {e}")

    def run_validation(self):
        """
        Run all quality gate validations.
        """
        print("🚀 Running Quality Gate Validation...")
        print(f"Working directory: {os.getcwd()}")

        # Validate each tool
        self.validate_ruff_issues("ruff_report.json")
        self.validate_mypy_errors("mypy_report")
        self.validate_prospector_issues("prospector_report.json")
        self.validate_complexity("radon_complexity.json")
        self.validate_maintainability("radon_maintainability.json")
        self.validate_test_coverage()
        self.validate_loc_guard()

        # Report results
        print("\n" + "=" * 50)
        print("QUALITY GATE RESULTS")
        print("=" * 50)

        if self.failures:
            print("❌ QUALITY GATES FAILED")
            print("\nFailures:")
            for failure in self.failures:
                print(f"  • {failure}")
            return False
        print("✅ ALL QUALITY GATES PASSED")
        return True


def main():
    """
    Main validation entry point.
    """
    validator = QualityGateValidator()
    success = validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
