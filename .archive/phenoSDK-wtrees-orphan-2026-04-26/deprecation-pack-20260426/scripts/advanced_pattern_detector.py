#!/usr/bin/env python3
"""Advanced Pattern Detection Tool.

Comprehensive detection of anti-patterns, vibe-patterns, code smells, and architectural
violations in Python codebases.
"""

import argparse
import ast
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PatternFinding:
    """
    Represents a pattern detection finding.
    """

    file_path: str
    line_number: int
    pattern_type: str
    category: str  # 'anti-pattern', 'vibe-pattern', 'code-smell', 'architectural'
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    message: str
    suggestion: str = ""
    context: str = ""
    confidence: float = 1.0
    autofix: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file_path,
            "line": self.line_number,
            "pattern_type": self.pattern_type,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
            "context": self.context,
            "confidence": self.confidence,
            "autofix": self.autofix,
        }


@dataclass
class PatternAnalysisResults:
    """
    Container for pattern analysis results.
    """

    findings: list[PatternFinding] = field(default_factory=list)
    files_scanned: int = 0
    lines_scanned: int = 0
    total_findings: int = 0
    pattern_counts: dict[str, int] = field(default_factory=dict)
    category_counts: dict[str, int] = field(default_factory=dict)
    severity_counts: dict[str, int] = field(default_factory=dict)

    def add_finding(self, finding: PatternFinding) -> None:
        """
        Add a finding to the results.
        """
        self.findings.append(finding)
        self.total_findings += 1

        # Update counters
        self.pattern_counts[finding.pattern_type] = (
            self.pattern_counts.get(finding.pattern_type, 0) + 1
        )
        self.category_counts[finding.category] = self.category_counts.get(finding.category, 0) + 1
        self.severity_counts[finding.severity] = self.severity_counts.get(finding.severity, 0) + 1

    def get_findings_by_category(self, category: str) -> list[PatternFinding]:
        """
        Get findings by category.
        """
        return [f for f in self.findings if f.category == category]

    def get_findings_by_severity(self, severity: str) -> list[PatternFinding]:
        """
        Get findings by severity.
        """
        return [f for f in self.findings if f.severity == severity]

    def get_findings_by_pattern(self, pattern_type: str) -> list[PatternFinding]:
        """
        Get findings by pattern type.
        """
        return [f for f in self.findings if f.pattern_type == pattern_type]

    def summary(self) -> dict[str, Any]:
        """
        Generate summary statistics.
        """
        return {
            "files_scanned": self.files_scanned,
            "lines_scanned": self.lines_scanned,
            "total_findings": self.total_findings,
            "pattern_counts": self.pattern_counts,
            "category_counts": self.category_counts,
            "severity_counts": self.severity_counts,
            "top_patterns": sorted(self.pattern_counts.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
            "top_categories": sorted(
                self.category_counts.items(), key=lambda x: x[1], reverse=True,
            ),
        }


class BasePatternVisitor(ast.NodeVisitor):
    """
    Base class for pattern detection visitors.
    """

    def __init__(self, results: PatternAnalysisResults, file_path: Path, lines: list[str]):
        self.results = results
        self.file_path = str(file_path)
        self.lines = lines
        self.current_class = None
        self.current_function = None
        self.imports = set()
        self.function_complexity = {}
        self.class_methods = defaultdict(list)

    def add_finding(
        self,
        line_number: int,
        pattern_type: str,
        category: str,
        severity: str,
        message: str,
        suggestion: str = "",
        context: str = "",
        confidence: float = 1.0,
        autofix: dict[str, Any] = None,
    ):
        """
        Add a pattern finding.
        """
        if context == "" and 0 < line_number <= len(self.lines):
            context = self.lines[line_number - 1].strip()

        finding = PatternFinding(
            file_path=self.file_path,
            line_number=line_number,
            pattern_type=pattern_type,
            category=category,
            severity=severity,
            message=message,
            suggestion=suggestion,
            context=context,
            confidence=confidence,
            autofix=autofix or {},
        )

        self.results.add_finding(finding)

    def get_line_content(self, line_number: int) -> str:
        """
        Get content of a specific line.
        """
        if 0 < line_number <= len(self.lines):
            return self.lines[line_number - 1].strip()
        return ""


class AntiPatternVisitor(BasePatternVisitor):
    """
    Detects common anti-patterns in Python code.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Check function definitions for anti-patterns.
        """
        self.current_function = node.name

        # Check for too many parameters
        if len(node.args.args) > 7:
            self.add_finding(
                node.lineno,
                "too_many_parameters",
                "anti-pattern",
                "medium",
                f"Function '{node.name}' has {len(node.args.args)} parameters (max recommended: 7)",
                "Consider using a data class or dictionary to group related parameters",
            )

        # Check for too many local variables
        local_vars = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                local_vars.add(child.id)

        if len(local_vars) > 15:
            self.add_finding(
                node.lineno,
                "too_many_local_variables",
                "anti-pattern",
                "medium",
                f"Function '{node.name}' has {len(local_vars)} local variables (max recommended: 15)",
                "Consider breaking the function into smaller functions",
            )

        # Check for long functions
        if hasattr(node, "end_lineno") and node.end_lineno:
            function_length = node.end_lineno - node.lineno
            if function_length > 50:
                self.add_finding(
                    node.lineno,
                    "long_function",
                    "anti-pattern",
                    "high",
                    f"Function '{node.name}' is {function_length} lines long (max recommended: 50)",
                    "Consider breaking the function into smaller, focused functions",
                )

        # Check for nested functions (too deep)
        self._check_nested_functions(node, 0)

        self.generic_visit(node)
        self.current_function = None

    def _check_nested_functions(self, node: ast.AST, depth: int) -> None:
        """
        Check for deeply nested functions.
        """
        if isinstance(node, ast.FunctionDef):
            if depth > 3:
                self.add_finding(
                    node.lineno,
                    "deeply_nested_function",
                    "anti-pattern",
                    "medium",
                    f"Function '{node.name}' is nested {depth} levels deep (max recommended: 3)",
                    "Consider extracting nested functions to module level",
                )
            for child in ast.iter_child_nodes(node):
                self._check_nested_functions(child, depth + 1)
        else:
            for child in ast.iter_child_nodes(node):
                self._check_nested_functions(child, depth)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Check class definitions for anti-patterns.
        """
        self.current_class = node.name

        # Check for too many methods
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            self.add_finding(
                node.lineno,
                "too_many_methods",
                "anti-pattern",
                "medium",
                f"Class '{node.name}' has {len(methods)} methods (max recommended: 20)",
                "Consider splitting the class into smaller, more focused classes",
            )

        # Check for too many instance variables
        instance_vars = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                    ):
                        instance_vars.add(target.attr)

        if len(instance_vars) > 10:
            self.add_finding(
                node.lineno,
                "too_many_instance_variables",
                "anti-pattern",
                "medium",
                f"Class '{node.name}' has {len(instance_vars)} instance variables (max recommended: 10)",
                "Consider using composition or data classes to group related variables",
            )

        self.generic_visit(node)
        self.current_class = None

    def visit_For(self, node: ast.For) -> None:
        """
        Check for loop anti-patterns.
        """
        # Check for range(len()) anti-pattern
        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "range"
        ):
            if len(node.iter.args) == 1 and isinstance(node.iter.args[0], ast.Call):
                if (
                    isinstance(node.iter.args[0].func, ast.Name)
                    and node.iter.args[0].func.id == "len"
                ):
                    self.add_finding(
                        node.lineno,
                        "range_len_antipattern",
                        "anti-pattern",
                        "low",
                        "Using range(len()) instead of enumerate()",
                        "Consider using enumerate() for better readability: for i, item in enumerate(items):",
                    )

        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """
        Check for conditional anti-patterns.
        """
        # Check for Yoda conditions
        if isinstance(node.test, ast.Compare):
            if len(node.test.comparators) == 1:
                left = node.test.left
                right = node.test.comparators[0]

                # Check if constant is on the left (Yoda condition)
                if isinstance(left, ast.Constant) and not isinstance(right, ast.Constant):
                    self.add_finding(
                        node.lineno,
                        "yoda_condition",
                        "anti-pattern",
                        "low",
                        "Yoda condition detected (constant on left side)",
                        "Consider reversing the comparison for better readability",
                    )

        self.generic_visit(node)


class VibePatternVisitor(BasePatternVisitor):
    """
    Detects vibe-patterns and code style issues.
    """

    def visit_Import(self, node: ast.Import) -> None:
        """
        Check import patterns.
        """
        for alias in node.names:
            self.imports.add(alias.name)

            # Check for wildcard imports
            if alias.name == "*":
                self.add_finding(
                    node.lineno,
                    "wildcard_import",
                    "vibe-pattern",
                    "high",
                    f"Wildcard import detected: {alias.name}",
                    "Import specific functions/classes instead of using wildcard imports",
                )

            # Check for very long import lines
            import_line = self.get_line_content(node.lineno)
            if len(import_line) > 120:
                self.add_finding(
                    node.lineno,
                    "long_import_line",
                    "vibe-pattern",
                    "low",
                    f"Import line is {len(import_line)} characters long (max recommended: 120)",
                    "Consider breaking long import lines across multiple lines",
                )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Check from-import patterns.
        """
        if node.module:
            # Check for relative imports that are too deep
            if node.level > 2:
                self.add_finding(
                    node.lineno,
                    "deep_relative_import",
                    "vibe-pattern",
                    "medium",
                    f"Relative import with {node.level} levels (max recommended: 2)",
                    "Consider using absolute imports or restructuring the package",
                )

            # Check for importing from parent modules
            if node.level > 0 and ".." in (node.module or ""):
                self.add_finding(
                    node.lineno,
                    "parent_module_import",
                    "vibe-pattern",
                    "medium",
                    "Importing from parent module detected",
                    "Consider restructuring to avoid parent module imports",
                )

    def visit_Str(self, node: ast.Str) -> None:
        """
        Check string patterns.
        """
        # Check for magic strings
        if isinstance(node.s, str) and len(node.s) > 10:
            # Check if it's a magic string (not a docstring)
            if not (isinstance(node.parent, ast.Expr) and isinstance(node.parent.value, ast.Str)):
                if node.s.isupper() and "_" in node.s:
                    self.add_finding(
                        node.lineno,
                        "magic_string",
                        "vibe-pattern",
                        "low",
                        f"Magic string detected: '{node.s[:20]}...'",
                        "Consider defining as a named constant",
                    )

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """
        Check list comprehension patterns.
        """
        # Check for overly complex list comprehensions
        complexity = self._calculate_comprehension_complexity(node)
        if complexity > 5:
            self.add_finding(
                node.lineno,
                "complex_list_comprehension",
                "vibe-pattern",
                "medium",
                f"List comprehension complexity: {complexity} (max recommended: 5)",
                "Consider breaking into multiple lines or using a regular loop",
            )

    def visit_DictComp(self, node: ast.DictComp) -> None:
        """
        Check dict comprehension patterns.
        """
        complexity = self._calculate_comprehension_complexity(node)
        if complexity > 5:
            self.add_finding(
                node.lineno,
                "complex_dict_comprehension",
                "vibe-pattern",
                "medium",
                f"Dict comprehension complexity: {complexity} (max recommended: 5)",
                "Consider breaking into multiple lines or using a regular loop",
            )

    def _calculate_comprehension_complexity(self, node: ast.AST) -> int:
        """
        Calculate complexity of a comprehension.
        """
        complexity = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity


class CodeSmellVisitor(BasePatternVisitor):
    """
    Detects code smells and maintainability issues.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Check for function code smells.
        """
        # Check for too many return statements
        return_count = len([n for n in ast.walk(node) if isinstance(n, ast.Return)])
        if return_count > 5:
            self.add_finding(
                node.lineno,
                "too_many_returns",
                "code-smell",
                "medium",
                f"Function '{node.name}' has {return_count} return statements (max recommended: 5)",
                "Consider using early returns or restructuring the function logic",
            )

        # Check for too many nested levels
        max_nesting = self._calculate_max_nesting(node)
        if max_nesting > 4:
            self.add_finding(
                node.lineno,
                "excessive_nesting",
                "code-smell",
                "high",
                f"Function '{node.name}' has {max_nesting} levels of nesting (max recommended: 4)",
                "Consider extracting nested code into separate functions",
            )

        # Check for duplicate code patterns
        self._check_duplicate_code_patterns(node)

        self.generic_visit(node)

    def _calculate_max_nesting(self, node: ast.AST, current_level: int = 0) -> int:
        """
        Calculate maximum nesting level in a function.
        """
        max_level = current_level

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_level = self._calculate_max_nesting(child, current_level + 1)
                max_level = max(max_level, child_level)
            else:
                child_level = self._calculate_max_nesting(child, current_level)
                max_level = max(max_level, child_level)

        return max_level

    def _check_duplicate_code_patterns(self, node: ast.FunctionDef) -> None:
        """
        Check for duplicate code patterns within a function.
        """
        # Simple duplicate code detection based on AST structure
        statements = [
            n
            for n in node.body
            if isinstance(n, (ast.Assign, ast.Expr, ast.If, ast.For, ast.While))
        ]

        # Group similar statements
        statement_groups = defaultdict(list)
        for stmt in statements:
            stmt_type = type(stmt).__name__
            statement_groups[stmt_type].append(stmt)

        # Check for repeated patterns
        for stmt_type, stmts in statement_groups.items():
            if len(stmts) > 3:  # More than 3 similar statements
                self.add_finding(
                    node.lineno,
                    "repeated_patterns",
                    "code-smell",
                    "medium",
                    f"Function '{node.name}' has {len(stmts)} similar {stmt_type} statements",
                    "Consider extracting repeated patterns into a helper function",
                )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Check for class code smells.
        """
        # Check for God class (too many responsibilities)
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 15:
            self.add_finding(
                node.lineno,
                "god_class",
                "code-smell",
                "high",
                f"Class '{node.name}' has {len(methods)} methods (max recommended: 15)",
                "Consider splitting into multiple classes with single responsibilities",
            )

        # Check for feature envy
        self._check_feature_envy(node)

        self.generic_visit(node)

    def _check_feature_envy(self, node: ast.ClassDef) -> None:
        """
        Check for feature envy (methods that use more of another class than their own).
        """
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

        for method in methods:
            # Count references to self vs other objects
            self_refs = 0
            other_refs = 0

            for child in ast.walk(method):
                if isinstance(child, ast.Attribute):
                    if isinstance(child.value, ast.Name) and child.value.id == "self":
                        self_refs += 1
                    else:
                        other_refs += 1

            if other_refs > self_refs * 2 and other_refs > 5:
                self.add_finding(
                    method.lineno,
                    "feature_envy",
                    "code-smell",
                    "medium",
                    f"Method '{method.name}' uses more external references than self references",
                    "Consider moving this method to the class it uses most",
                )


class ArchitecturalPatternVisitor(BasePatternVisitor):
    """
    Detects architectural pattern violations.
    """

    def __init__(self, results: PatternAnalysisResults, file_path: Path, lines: list[str]):
        super().__init__(results, file_path, lines)
        self.layer_violations = defaultdict(list)
        self.dependency_graph = defaultdict(set)
        self.current_layer = self._determine_layer(file_path)

    def _determine_layer(self, file_path: Path) -> str:
        """
        Determine the architectural layer based on file path.
        """
        path_str = str(file_path)

        if "domain" in path_str or "entities" in path_str:
            return "domain"
        if "application" in path_str or "services" in path_str or "use_cases" in path_str:
            return "application"
        if "infrastructure" in path_str or "adapters" in path_str:
            return "infrastructure"
        if "tests" in path_str:
            return "tests"
        return "unknown"

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Check for architectural layer violations.
        """
        if node.module:
            imported_layer = self._determine_imported_layer(node.module)

            if imported_layer != "unknown" and self.current_layer != "unknown":
                # Check for layer violations
                if self._is_layer_violation(self.current_layer, imported_layer):
                    self.add_finding(
                        node.lineno,
                        "layer_violation",
                        "architectural",
                        "high",
                        f"Layer violation: {self.current_layer} importing from {imported_layer}",
                        "Consider using dependency inversion or moving the import to a higher layer",
                    )

                # Build dependency graph
                self.dependency_graph[self.current_layer].add(imported_layer)

    def _determine_imported_layer(self, module_name: str) -> str:
        """
        Determine the layer of an imported module.
        """
        if any(keyword in module_name.lower() for keyword in ["domain", "entities", "models"]):
            return "domain"
        if any(
            keyword in module_name.lower() for keyword in ["application", "services", "use_cases"]
        ):
            return "application"
        if any(
            keyword in module_name.lower()
            for keyword in ["infrastructure", "adapters", "repositories"]
        ):
            return "infrastructure"
        return "unknown"

    def _is_layer_violation(self, from_layer: str, to_layer: str) -> bool:
        """
        Check if importing from one layer to another violates architectural principles.
        """
        # Clean Architecture layer order: domain < application < infrastructure
        layer_order = {"domain": 0, "application": 1, "infrastructure": 2, "tests": 3}

        if from_layer in layer_order and to_layer in layer_order:
            # Higher layers can import from lower layers, but not vice versa
            return layer_order[from_layer] < layer_order[to_layer]

        return False

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Check for SOLID principle violations.
        """
        # Check for Single Responsibility Principle
        self._check_single_responsibility(node)

        # Check for Open/Closed Principle
        self._check_open_closed_principle(node)

        self.generic_visit(node)

    def _check_single_responsibility(self, node: ast.ClassDef) -> None:
        """
        Check for Single Responsibility Principle violations.
        """
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

        # Group methods by apparent responsibility
        responsibilities = defaultdict(list)

        for method in methods:
            method_name = method.name.lower()
            if any(
                keyword in method_name
                for keyword in ["get", "set", "load", "save", "create", "update", "delete"]
            ):
                responsibilities["data_access"].append(method)
            elif any(keyword in method_name for keyword in ["validate", "check", "verify"]):
                responsibilities["validation"].append(method)
            elif any(
                keyword in method_name for keyword in ["format", "render", "display", "print"]
            ):
                responsibilities["presentation"].append(method)
            elif any(keyword in method_name for keyword in ["calculate", "compute", "process"]):
                responsibilities["business_logic"].append(method)
            else:
                responsibilities["other"].append(method)

        # If class has methods in too many responsibility areas, it might violate SRP
        if len(responsibilities) > 3:
            self.add_finding(
                node.lineno,
                "single_responsibility_violation",
                "architectural",
                "medium",
                f"Class '{node.name}' appears to have multiple responsibilities",
                "Consider splitting into multiple classes with single responsibilities",
            )

    def _check_open_closed_principle(self, node: ast.ClassDef) -> None:
        """
        Check for Open/Closed Principle violations.
        """
        # Look for switch-like statements or if-elif chains that might indicate OCP violation
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Check for long if-elif chains
                elif_count = 0
                current = child
                while (
                    hasattr(current, "orelse")
                    and current.orelse
                    and len(current.orelse) == 1
                    and isinstance(current.orelse[0], ast.If)
                ):
                    elif_count += 1
                    current = current.orelse[0]

                if elif_count > 5:
                    self.add_finding(
                        child.lineno,
                        "open_closed_violation",
                        "architectural",
                        "medium",
                        f"Long if-elif chain detected ({elif_count} conditions)",
                        "Consider using polymorphism or strategy pattern instead",
                    )


class AdvancedPatternDetector:
    """
    Main detector for advanced patterns.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.results = PatternAnalysisResults()
        self.visitors = [
            AntiPatternVisitor,
            VibePatternVisitor,
            CodeSmellVisitor,
            ArchitecturalPatternVisitor,
        ]

    def scan_file(self, file_path: Path) -> None:
        """
        Scan a single file for patterns.
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            # Parse AST
            tree = ast.parse(content, filename=str(file_path))

            # Run all visitors
            for visitor_class in self.visitors:
                visitor = visitor_class(self.results, file_path, lines)
                visitor.visit(tree)

            self.results.files_scanned += 1
            self.results.lines_scanned += len(lines)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def scan_directory(self, directory: Path, extensions: list[str] = None) -> None:
        """
        Scan a directory for patterns.
        """
        if extensions is None:
            extensions = [".py"]

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip certain directories
                if any(
                    part in str(file_path)
                    for part in ["__pycache__", ".git", ".venv", "node_modules"]
                ):
                    continue

                self.scan_file(file_path)

    def generate_report(self) -> str:
        """
        Generate a comprehensive pattern analysis report.
        """
        summary = self.results.summary()

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("ADVANCED PATTERN ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Files scanned: {summary['files_scanned']}")
        report_lines.append(f"Lines scanned: {summary['lines_scanned']}")
        report_lines.append(f"Total findings: {summary['total_findings']}")
        report_lines.append("")

        # Category breakdown
        report_lines.append("FINDINGS BY CATEGORY:")
        report_lines.append("-" * 40)
        for category, count in summary["top_categories"]:
            report_lines.append(f"{category:<20} {count:>6}")
        report_lines.append("")

        # Severity breakdown
        report_lines.append("FINDINGS BY SEVERITY:")
        report_lines.append("-" * 40)
        for severity, count in summary["severity_counts"].items():
            report_lines.append(f"{severity:<20} {count:>6}")
        report_lines.append("")

        # Top patterns
        report_lines.append("TOP PATTERN TYPES:")
        report_lines.append("-" * 40)
        for pattern, count in summary["top_patterns"]:
            report_lines.append(f"{pattern:<30} {count:>6}")
        report_lines.append("")

        # Detailed findings by severity
        for severity in ["critical", "high", "medium", "low", "info"]:
            findings = self.results.get_findings_by_severity(severity)
            if findings:
                report_lines.append(f"{severity.upper()} SEVERITY FINDINGS:")
                report_lines.append("-" * 40)
                for finding in findings[:10]:  # Show top 10
                    report_lines.append(
                        f"{finding.file_path}:{finding.line_number} - {finding.pattern_type}",
                    )
                    report_lines.append(f"  {finding.message}")
                    if finding.suggestion:
                        report_lines.append(f"  Suggestion: {finding.suggestion}")
                    report_lines.append("")

        return "\n".join(report_lines)


def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="Advanced Pattern Detection Tool")
    parser.add_argument("--path", type=str, default=".", help="Path to scan")
    parser.add_argument("--output", type=str, help="Output file for report")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--severity", type=str, help="Filter by severity")

    args = parser.parse_args()

    root_path = Path(args.path)
    detector = AdvancedPatternDetector(root_path)

    print("🔍 Scanning for advanced patterns...")
    detector.scan_directory(root_path)

    if args.json:
        # Output JSON
        output = {
            "summary": detector.results.summary(),
            "findings": [f.to_dict() for f in detector.results.findings],
        }

        if args.category:
            output["findings"] = [f for f in output["findings"] if f["category"] == args.category]

        if args.severity:
            output["findings"] = [f for f in output["findings"] if f["severity"] == args.severity]

        json_output = json.dumps(output, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(json_output)
        else:
            print(json_output)
    else:
        # Output text report
        report = detector.generate_report()

        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
        else:
            print(report)


if __name__ == "__main__":
    main()
