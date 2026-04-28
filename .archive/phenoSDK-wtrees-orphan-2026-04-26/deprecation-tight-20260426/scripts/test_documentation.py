#!/usr/bin/env python3
"""
Comprehensive Documentation Testing Framework
Tests documentation quality, accuracy, and completeness.
"""

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class DocTestResult:
    """Result of a documentation test."""
    test_name: str
    status: str  # "pass", "fail", "warning"
    message: str
    file_path: str
    line_number: int = 0
    severity: str = "medium"  # "low", "medium", "high", "critical"


class DocumentationTester:
    """Comprehensive documentation testing framework."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs_path = self.project_root / "docs"
        self.src_path = self.project_root / "src"
        self.results = []

        # Documentation patterns to check
        self.doc_patterns = {
            "code_blocks": r"```(?:python|py|bash|shell|yaml|yml|json|toml)\n(.*?)\n```",
            "todo_comments": r"# TODO|# FIXME|# NOTE|# HACK",
            "broken_links": r"\[([^\]]+)\]\(([^)]+)\)",
            "missing_docstrings": r"def\s+\w+\([^)]*\):",
            "api_examples": r"```python\n.*?def\s+\w+\([^)]*\):",
            "version_info": r'version\s*[:=]\s*["\']?[\d\.]+["\']?',
            "license_info": r"license|copyright|©",
            "contact_info": r"contact|email|@|github|gitlab",
        }

    def run_all_tests(self) -> dict[str, Any]:
        """Run all documentation tests."""
        print("📚 Running Comprehensive Documentation Tests...")

        # Test different aspects of documentation
        self._test_markdown_quality()
        self._test_code_examples()
        self._test_api_documentation()
        self._test_readme_quality()
        self._test_docstring_coverage()
        self._test_link_validation()
        self._test_documentation_structure()
        self._test_examples_accuracy()

        # Generate report
        return self._generate_report()

    def _test_markdown_quality(self) -> None:
        """Test markdown file quality."""
        print("  📝 Testing markdown quality...")

        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                # Check for common markdown issues
                self._check_markdown_headers(md_file, lines)
                self._check_markdown_formatting(md_file, lines)
                self._check_markdown_length(md_file, lines)

            except Exception as e:
                self.results.append(DocTestResult(
                    test_name="markdown_quality",
                    status="fail",
                    message=f"Error reading {md_file}: {e}",
                    file_path=str(md_file),
                    severity="high",
                ))

    def _check_markdown_headers(self, file_path: Path, lines: list[str]) -> None:
        """Check markdown header structure."""
        headers = []
        for i, line in enumerate(lines, 1):
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                headers.append((level, line.strip(), i))

        # Check for proper header hierarchy
        prev_level = 0
        for level, header, line_num in headers:
            if level > prev_level + 1:
                self.results.append(DocTestResult(
                    test_name="markdown_headers",
                    status="warning",
                    message=f"Header level jump from {prev_level} to {level}",
                    file_path=str(file_path),
                    line_number=line_num,
                    severity="medium",
                ))
            prev_level = level

    def _check_markdown_formatting(self, file_path: Path, lines: list[str]) -> None:
        """Check markdown formatting issues."""
        for i, line in enumerate(lines, 1):
            # Check for long lines
            if len(line) > 120:
                self.results.append(DocTestResult(
                    test_name="markdown_formatting",
                    status="warning",
                    message=f"Line too long ({len(line)} characters)",
                    file_path=str(file_path),
                    line_number=i,
                    severity="low",
                ))

            # Check for trailing whitespace
            if line.endswith(" "):
                self.results.append(DocTestResult(
                    test_name="markdown_formatting",
                    status="warning",
                    message="Trailing whitespace",
                    file_path=str(file_path),
                    line_number=i,
                    severity="low",
                ))

    def _check_markdown_length(self, file_path: Path, lines: list[str]) -> None:
        """Check markdown file length."""
        if len(lines) > 1000:
            self.results.append(DocTestResult(
                test_name="markdown_length",
                status="warning",
                message=f"File very long ({len(lines)} lines), consider splitting",
                file_path=str(file_path),
                severity="medium",
            ))

    def _test_code_examples(self) -> None:
        """Test code examples in documentation."""
        print("  💻 Testing code examples...")

        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # Extract code blocks
                code_blocks = re.findall(self.doc_patterns["code_blocks"], content, re.DOTALL)

                for i, code_block in enumerate(code_blocks):
                    self._validate_code_example(md_file, code_block, i + 1)

            except Exception as e:
                self.results.append(DocTestResult(
                    test_name="code_examples",
                    status="fail",
                    message=f"Error processing {md_file}: {e}",
                    file_path=str(md_file),
                    severity="high",
                ))

    def _validate_code_example(self, file_path: Path, code: str, block_num: int) -> None:
        """Validate a code example."""
        lines = code.strip().split("\n")

        # Check for syntax errors (basic check)
        if code.strip():
            # Check for common Python syntax issues
            if "import" in code and "from" in code:
                # Check import order
                import_lines = [line for line in lines if line.strip().startswith(("import ", "from "))]
                if len(import_lines) > 1:
                    # Basic import order check
                    for i in range(len(import_lines) - 1):
                        if import_lines[i].startswith("from") and import_lines[i + 1].startswith("import"):
                            self.results.append(DocTestResult(
                                test_name="code_examples",
                                status="warning",
                                message="Import order issue in code example",
                                file_path=str(file_path),
                                severity="low",
                            ))
                            break

    def _test_api_documentation(self) -> None:
        """Test API documentation completeness."""
        print("  🔌 Testing API documentation...")

        # Check for API documentation files
        api_docs = list(self.docs_path.rglob("*api*.md")) if self.docs_path.exists() else []

        if not api_docs:
            self.results.append(DocTestResult(
                test_name="api_documentation",
                status="warning",
                message="No API documentation found",
                file_path=str(self.docs_path),
                severity="medium",
            ))

        # Check for docstrings in Python files
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for functions without docstrings
                functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
                for func_name in functions:
                    # Simple check for docstring
                    func_pattern = rf'def\s+{func_name}\s*\([^)]*\):\s*\n\s*""".*?"""'
                    if not re.search(func_pattern, content, re.DOTALL):
                        self.results.append(DocTestResult(
                            test_name="api_documentation",
                            status="warning",
                            message=f"Function '{func_name}' missing docstring",
                            file_path=str(py_file),
                            severity="medium",
                        ))

            except Exception as e:
                self.results.append(DocTestResult(
                    test_name="api_documentation",
                    status="fail",
                    message=f"Error processing {py_file}: {e}",
                    file_path=str(py_file),
                    severity="high",
                ))

    def _test_readme_quality(self) -> None:
        """Test README file quality."""
        print("  📖 Testing README quality...")

        readme_files = list(self.project_root.glob("README*.md"))

        if not readme_files:
            self.results.append(DocTestResult(
                test_name="readme_quality",
                status="fail",
                message="No README file found",
                file_path=str(self.project_root),
                severity="critical",
            ))
            return

        for readme_file in readme_files:
            try:
                with open(readme_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for essential sections
                required_sections = [
                    ("installation", r"install|setup|getting started", re.IGNORECASE),
                    ("usage", r"usage|example|how to use", re.IGNORECASE),
                    ("license", r"license|copyright", re.IGNORECASE),
                    ("contributing", r"contribut|develop|contribute", re.IGNORECASE),
                ]

                for section_name, pattern, flags in required_sections:
                    if not re.search(pattern, content, flags):
                        self.results.append(DocTestResult(
                            test_name="readme_quality",
                            status="warning",
                            message=f"Missing '{section_name}' section",
                            file_path=str(readme_file),
                            severity="medium",
                        ))

                # Check for code examples
                if not re.search(self.doc_patterns["code_blocks"], content, re.DOTALL):
                    self.results.append(DocTestResult(
                        test_name="readme_quality",
                        status="warning",
                        message="No code examples found",
                        file_path=str(readme_file),
                        severity="medium",
                    ))

            except Exception as e:
                self.results.append(DocTestResult(
                    test_name="readme_quality",
                    status="fail",
                    message=f"Error reading {readme_file}: {e}",
                    file_path=str(readme_file),
                    severity="high",
                ))

    def _test_docstring_coverage(self) -> None:
        """Test docstring coverage in Python files."""
        print("  📝 Testing docstring coverage...")

        total_functions = 0
        documented_functions = 0

        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Find all function definitions
                functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
                total_functions += len(functions)

                # Check for docstrings
                for func_name in functions:
                    func_pattern = rf'def\s+{func_name}\s*\([^)]*\):\s*\n\s*""".*?"""'
                    if re.search(func_pattern, content, re.DOTALL):
                        documented_functions += 1
                    else:
                        self.results.append(DocTestResult(
                            test_name="docstring_coverage",
                            status="warning",
                            message=f"Function '{func_name}' missing docstring",
                            file_path=str(py_file),
                            severity="medium",
                        ))

            except Exception as e:
                self.results.append(DocTestResult(
                    test_name="docstring_coverage",
                    status="fail",
                    message=f"Error processing {py_file}: {e}",
                    file_path=str(py_file),
                    severity="high",
                ))

        # Calculate coverage percentage
        if total_functions > 0:
            coverage = (documented_functions / total_functions) * 100
            if coverage < 80:
                self.results.append(DocTestResult(
                    test_name="docstring_coverage",
                    status="warning",
                    message=f"Low docstring coverage: {coverage:.1f}%",
                    file_path=str(self.src_path),
                    severity="medium",
                ))

    def _test_link_validation(self) -> None:
        """Test link validation in documentation."""
        print("  🔗 Testing link validation...")

        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # Find all links
                links = re.findall(self.doc_patterns["broken_links"], content)

                for link_text, link_url in links:
                    # Check for common link issues
                    if link_url.startswith("http"):
                        # External link - basic validation
                        if " " in link_url:
                            self.results.append(DocTestResult(
                                test_name="link_validation",
                                status="warning",
                                message=f"Space in URL: {link_url}",
                                file_path=str(md_file),
                                severity="low",
                            ))
                    elif link_url.startswith("#"):
                        # Internal anchor link
                        anchor = link_url[1:]
                        if not re.search(rf'<[^>]*id=["\']?{re.escape(anchor)}["\']?', content):
                            self.results.append(DocTestResult(
                                test_name="link_validation",
                                status="warning",
                                message=f"Broken internal link: {link_url}",
                                file_path=str(md_file),
                                severity="medium",
                            ))
                    elif not link_url.startswith("mailto:"):
                        # File link - check if file exists
                        link_path = self.project_root / link_url
                        if not link_path.exists():
                            self.results.append(DocTestResult(
                                test_name="link_validation",
                                status="fail",
                                message=f"Broken file link: {link_url}",
                                file_path=str(md_file),
                                severity="high",
                            ))

            except Exception as e:
                self.results.append(DocTestResult(
                    test_name="link_validation",
                    status="fail",
                    message=f"Error processing {md_file}: {e}",
                    file_path=str(md_file),
                    severity="high",
                ))

    def _test_documentation_structure(self) -> None:
        """Test documentation structure and organization."""
        print("  📁 Testing documentation structure...")

        # Check for essential documentation files
        essential_files = [
            "README.md",
            "CHANGELOG.md",
            "LICENSE",
            "CONTRIBUTING.md",
        ]

        for file_name in essential_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.results.append(DocTestResult(
                    test_name="documentation_structure",
                    status="warning",
                    message=f"Missing essential file: {file_name}",
                    file_path=str(self.project_root),
                    severity="medium",
                ))

        # Check for docs directory
        if not self.docs_path.exists():
            self.results.append(DocTestResult(
                test_name="documentation_structure",
                status="warning",
                message="No docs/ directory found",
                file_path=str(self.project_root),
                severity="medium",
            ))

    def _test_examples_accuracy(self) -> None:
        """Test accuracy of code examples."""
        print("  ✅ Testing examples accuracy...")

        # This would typically run the code examples to ensure they work
        # For now, we'll do basic syntax checking
        for md_file in self.project_root.rglob("*.md"):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # Extract Python code blocks
                python_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)

                for i, code_block in enumerate(python_blocks):
                    # Basic syntax check
                    try:
                        compile(code_block, f"<example_{i}>", "exec")
                    except SyntaxError as e:
                        self.results.append(DocTestResult(
                            test_name="examples_accuracy",
                            status="fail",
                            message=f"Syntax error in code example: {e}",
                            file_path=str(md_file),
                            severity="high",
                        ))

            except Exception as e:
                self.results.append(DocTestResult(
                    test_name="examples_accuracy",
                    status="fail",
                    message=f"Error processing {md_file}: {e}",
                    file_path=str(md_file),
                    severity="high",
                ))

    def _generate_report(self) -> dict[str, Any]:
        """Generate comprehensive test report."""
        # Count results by status and severity
        status_counts = {}
        severity_counts = {}

        for result in self.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1

        # Calculate overall score
        total_tests = len(self.results)
        passed_tests = status_counts.get("pass", 0)
        failed_tests = status_counts.get("fail", 0)
        warning_tests = status_counts.get("warning", 0)

        if total_tests == 0:
            score = 100
        else:
            score = ((passed_tests + warning_tests * 0.5) / total_tests) * 100

        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "score": round(score, 1),
            "status_counts": status_counts,
            "severity_counts": severity_counts,
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "file_path": r.file_path,
                    "line_number": r.line_number,
                    "severity": r.severity,
                }
                for r in self.results
            ],
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test documentation quality")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    tester = DocumentationTester(args.project_root)
    report = tester.run_all_tests()

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        # Pretty print format
        output = f"""
📚 DOCUMENTATION TEST RESULTS
{'=' * 50}
Total Tests: {report['total_tests']}
Passed: {report['passed']}
Failed: {report['failed']}
Warnings: {report['warnings']}
Score: {report['score']}/100

Status Breakdown:
"""
        for status, count in report["status_counts"].items():
            output += f"  {status}: {count}\n"

        output += "\nSeverity Breakdown:\n"
        for severity, count in report["severity_counts"].items():
            output += f"  {severity}: {count}\n"

        if report["results"]:
            output += "\nIssues Found:\n"
            for result in report["results"][:10]:  # Show first 10
                output += f"  [{result['severity'].upper()}] {result['file_path']}: {result['message']}\n"

            if len(report["results"]) > 10:
                output += f"  ... and {len(report['results']) - 10} more issues\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
