#!/usr/bin/env python3
"""
Performance Anti-Pattern Detector Detects performance anti-patterns, memory leaks,
blocking calls, and other performance issues in Python code.
"""
import argparse
import ast
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PerformanceIssue:
    """
    Represents a detected performance issue.
    """

    type: str
    severity: str
    file: str
    line: int
    column: int
    message: str
    suggestion: str
    confidence: float
    impact: str


class PerformanceAntiPatternDetector:
    """
    Detects performance anti-patterns in Python code.
    """

    def __init__(self):
        self.issues = []
        self.file_stats = {}

        # Performance thresholds
        self.thresholds = {
            "max_loop_iterations": 1000,
            "max_nested_loops": 3,
            "max_function_calls": 50,
            "max_memory_usage_mb": 100,
            "max_response_time_ms": 1000,
            "max_database_queries": 10,
            "max_file_operations": 5,
            "max_network_calls": 3,
        }

        # Performance anti-patterns to detect
        self.patterns = {
            "n_plus_one_query": True,
            "memory_leak": True,
            "blocking_calls": True,
            "inefficient_loops": True,
            "unnecessary_computations": True,
            "large_data_structures": True,
            "synchronous_operations": True,
            "resource_leaks": True,
            "inefficient_algorithms": True,
            "excessive_io": True,
        }

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze a single file for performance issues.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            file_issues = []

            # Analyze different performance anti-patterns
            if self.patterns["n_plus_one_query"]:
                file_issues.extend(self._detect_n_plus_one_queries(tree, file_path))

            if self.patterns["memory_leak"]:
                file_issues.extend(self._detect_memory_leaks(tree, file_path))

            if self.patterns["blocking_calls"]:
                file_issues.extend(self._detect_blocking_calls(tree, file_path))

            if self.patterns["inefficient_loops"]:
                file_issues.extend(self._detect_inefficient_loops(tree, file_path))

            if self.patterns["unnecessary_computations"]:
                file_issues.extend(self._detect_unnecessary_computations(tree, file_path))

            if self.patterns["large_data_structures"]:
                file_issues.extend(self._detect_large_data_structures(tree, file_path))

            if self.patterns["synchronous_operations"]:
                file_issues.extend(self._detect_synchronous_operations(tree, file_path))

            if self.patterns["resource_leaks"]:
                file_issues.extend(self._detect_resource_leaks(tree, file_path))

            if self.patterns["inefficient_algorithms"]:
                file_issues.extend(self._detect_inefficient_algorithms(tree, file_path))

            if self.patterns["excessive_io"]:
                file_issues.extend(self._detect_excessive_io(tree, file_path))

            self.issues.extend(file_issues)

            return {
                "file": str(file_path),
                "issues": file_issues,
                "issue_count": len(file_issues),
                "severity_counts": self._count_by_severity(file_issues),
            }

        except Exception as e:
            return {"file": str(file_path), "error": str(e), "issues": [], "issue_count": 0}

    def _detect_n_plus_one_queries(self, tree: ast.AST, file_path: Path) -> list[PerformanceIssue]:
        """
        Detect N+1 query problems.
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Look for loops that make database queries
                if self._loop_contains_database_queries(node):
                    issues.append(
                        PerformanceIssue(
                            type="n_plus_one_query",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message="Potential N+1 query problem detected in loop",
                            suggestion="Use eager loading or batch queries to reduce database calls",
                            confidence=0.8,
                            impact="High - Can cause exponential database load",
                        ),
                    )

        return issues

    def _detect_memory_leaks(self, tree: ast.AST, file_path: Path) -> list[PerformanceIssue]:
        """
        Detect potential memory leaks.
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions that create large objects without cleanup
                if self._function_creates_large_objects(node):
                    issues.append(
                        PerformanceIssue(
                            type="memory_leak",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may create memory leaks",
                            suggestion="Ensure proper cleanup of large objects and use context managers",
                            confidence=0.6,
                            impact="Medium - Can cause memory growth over time",
                        ),
                    )

                # Check for circular references
                if self._has_circular_references(node):
                    issues.append(
                        PerformanceIssue(
                            type="memory_leak",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may have circular references",
                            suggestion="Break circular references or use weak references",
                            confidence=0.7,
                            impact="High - Can prevent garbage collection",
                        ),
                    )

        return issues

    def _detect_blocking_calls(self, tree: ast.AST, file_path: Path) -> list[PerformanceIssue]:
        """
        Detect blocking I/O calls.
        """
        issues = []

        blocking_functions = ["open", "read", "write", "input", "print", "sleep", "time.sleep"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in blocking_functions:
                        issues.append(
                            PerformanceIssue(
                                type="blocking_calls",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Blocking call '{node.func.id}' detected",
                                suggestion="Consider using async/await or threading for non-blocking operations",
                                confidence=0.8,
                                impact="Medium - Can block execution and reduce responsiveness",
                            ),
                        )

        return issues

    def _detect_inefficient_loops(self, tree: ast.AST, file_path: Path) -> list[PerformanceIssue]:
        """
        Detect inefficient loop patterns.
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for nested loops
                nested_depth = self._get_nested_loop_depth(node)
                if nested_depth > self.thresholds["max_nested_loops"]:
                    issues.append(
                        PerformanceIssue(
                            type="inefficient_loops",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Nested loops detected (depth: {nested_depth})",
                            suggestion="Consider using vectorized operations or breaking into smaller functions",
                            confidence=0.9,
                            impact="High - O(n^m) complexity can be very slow",
                        ),
                    )

                # Check for loops with expensive operations
                if self._loop_has_expensive_operations(node):
                    issues.append(
                        PerformanceIssue(
                            type="inefficient_loops",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message="Loop contains expensive operations",
                            suggestion="Move expensive operations outside the loop or use caching",
                            confidence=0.7,
                            impact="Medium - Can significantly slow down execution",
                        ),
                    )

        return issues

    def _detect_unnecessary_computations(
        self, tree: ast.AST, file_path: Path,
    ) -> list[PerformanceIssue]:
        """
        Detect unnecessary or redundant computations.
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions that recompute the same values
                if self._function_recomputes_values(node):
                    issues.append(
                        PerformanceIssue(
                            type="unnecessary_computations",
                            severity="low",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may recompute values unnecessarily",
                            suggestion="Use memoization or caching to avoid redundant computations",
                            confidence=0.6,
                            impact="Low - Minor performance improvement possible",
                        ),
                    )

                # Check for functions that don't use their return values
                if self._function_ignores_return_values(node):
                    issues.append(
                        PerformanceIssue(
                            type="unnecessary_computations",
                            severity="low",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may perform unnecessary computations",
                            suggestion="Remove unused computations or optimize the function",
                            confidence=0.5,
                            impact="Low - Minor performance improvement possible",
                        ),
                    )

        return issues

    def _detect_large_data_structures(
        self, tree: ast.AST, file_path: Path,
    ) -> list[PerformanceIssue]:
        """
        Detect large data structures that may cause memory issues.
        """
        issues = []

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.List)
                or isinstance(node, ast.Dict)
                or isinstance(node, ast.Set)
            ):
                # Check for large list/dict/set literals
                if self._is_large_data_structure(node):
                    issues.append(
                        PerformanceIssue(
                            type="large_data_structures",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message="Large data structure detected",
                            suggestion="Consider using generators or lazy evaluation for large datasets",
                            confidence=0.7,
                            impact="Medium - Can consume significant memory",
                        ),
                    )

        return issues

    def _detect_synchronous_operations(
        self, tree: ast.AST, file_path: Path,
    ) -> list[PerformanceIssue]:
        """
        Detect synchronous operations that could be async.
        """
        issues = []

        async_keywords = ["requests.get", "requests.post", "urllib", "socket", "subprocess"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_str = self._get_call_string(node)
                if any(keyword in call_str for keyword in async_keywords):
                    issues.append(
                        PerformanceIssue(
                            type="synchronous_operations",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Synchronous I/O operation detected: {call_str}",
                            suggestion="Consider using async/await for better concurrency",
                            confidence=0.8,
                            impact="Medium - Can block execution and reduce throughput",
                        ),
                    )

        return issues

    def _detect_resource_leaks(self, tree: ast.AST, file_path: Path) -> list[PerformanceIssue]:
        """
        Detect potential resource leaks.
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                # Check for proper resource management in with statements
                if not self._has_proper_resource_management(node):
                    issues.append(
                        PerformanceIssue(
                            type="resource_leaks",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message="Potential resource leak in with statement",
                            suggestion="Ensure all resources are properly closed and managed",
                            confidence=0.7,
                            impact="High - Can cause resource exhaustion",
                        ),
                    )

            elif isinstance(node, ast.Call):
                # Check for file operations without proper cleanup
                if self._is_file_operation_without_context(node):
                    issues.append(
                        PerformanceIssue(
                            type="resource_leaks",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message="File operation without proper resource management",
                            suggestion="Use context managers (with statements) for file operations",
                            confidence=0.8,
                            impact="Medium - Can cause file handle leaks",
                        ),
                    )

        return issues

    def _detect_inefficient_algorithms(
        self, tree: ast.AST, file_path: Path,
    ) -> list[PerformanceIssue]:
        """
        Detect inefficient algorithm patterns.
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for O(n²) or worse algorithms
                complexity = self._estimate_algorithm_complexity(node)
                if complexity in ["O(n²)", "O(n³)", "O(2^n)", "O(n!)"]:
                    issues.append(
                        PerformanceIssue(
                            type="inefficient_algorithms",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has {complexity} complexity",
                            suggestion="Consider using more efficient algorithms or data structures",
                            confidence=0.8,
                            impact="High - Performance degrades quickly with input size",
                        ),
                    )

        return issues

    def _detect_excessive_io(self, tree: ast.AST, file_path: Path) -> list[PerformanceIssue]:
        """
        Detect excessive I/O operations.
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                io_count = self._count_io_operations(node)
                if io_count > self.thresholds["max_file_operations"]:
                    issues.append(
                        PerformanceIssue(
                            type="excessive_io",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has {io_count} I/O operations",
                            suggestion="Batch I/O operations or use buffering to reduce system calls",
                            confidence=0.7,
                            impact="Medium - Can cause significant I/O overhead",
                        ),
                    )

        return issues

    # Helper methods for pattern detection

    def _loop_contains_database_queries(self, node: ast.For) -> bool:
        """
        Check if loop contains database queries.
        """
        db_keywords = ["query", "execute", "fetch", "select", "insert", "update", "delete"]

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_str = self._get_call_string(child)
                if any(keyword in call_str.lower() for keyword in db_keywords):
                    return True
        return False

    def _function_creates_large_objects(self, node: ast.FunctionDef) -> bool:
        """
        Check if function creates large objects.
        """
        large_object_patterns = ["[]", "{}", "set()", "list(", "dict(", "tuple("]

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_str = self._get_call_string(child)
                if any(pattern in call_str for pattern in large_object_patterns):
                    # Check if it's in a loop or repeated
                    if self._is_in_loop(child):
                        return True
        return False

    def _has_circular_references(self, node: ast.FunctionDef) -> bool:
        """
        Check for potential circular references.
        """
        # This is a simplified check - in practice, you'd need more sophisticated analysis
        assignments = []
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        assignments.append(target.id)

        # Check if function assigns to variables that might create cycles
        return len(assignments) > 5  # Heuristic: many assignments might indicate complexity

    def _get_nested_loop_depth(self, node: ast.For) -> int:
        """
        Get the depth of nested loops.
        """
        depth = 1
        for child in ast.walk(node):
            if isinstance(child, ast.For) and child != node:
                depth += 1
        return depth

    def _loop_has_expensive_operations(self, node: ast.For) -> bool:
        """
        Check if loop contains expensive operations.
        """
        expensive_operations = ["open", "read", "write", "query", "execute", "fetch"]

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_str = self._get_call_string(child)
                if any(op in call_str.lower() for op in expensive_operations):
                    return True
        return False

    def _function_recomputes_values(self, node: ast.FunctionDef) -> bool:
        """
        Check if function recomputes the same values.
        """
        # Look for repeated expressions or calls
        expressions = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                expressions.append(self._get_call_string(child))

        # Check for duplicates
        return len(expressions) != len(set(expressions))

    def _function_ignores_return_values(self, node: ast.FunctionDef) -> bool:
        """
        Check if function ignores return values.
        """
        # Look for function calls that don't assign return values
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Check if this call is not assigned to a variable
                if not isinstance(child.parent, ast.Assign):
                    return True
        return False

    def _is_large_data_structure(self, node) -> bool:
        """
        Check if data structure is large.
        """
        if isinstance(node, ast.List):
            return len(node.elts) > 100
        if isinstance(node, ast.Dict):
            return len(node.keys) > 100
        if isinstance(node, ast.Set):
            return len(node.elts) > 100
        return False

    def _get_call_string(self, node: ast.Call) -> str:
        """
        Get string representation of a function call.
        """
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return f"{self._get_attr_string(node.func.value)}.{node.func.attr}"
        return "unknown"

    def _get_attr_string(self, node) -> str:
        """
        Get string representation of an attribute.
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_attr_string(node.value)}.{node.attr}"
        return "unknown"

    def _has_proper_resource_management(self, node: ast.With) -> bool:
        """
        Check if with statement has proper resource management.
        """
        # Look for context managers that handle resources
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                call_str = self._get_call_string(item.context_expr)
                if any(keyword in call_str.lower() for keyword in ["open", "connect", "acquire"]):
                    return True
        return False

    def _is_file_operation_without_context(self, node: ast.Call) -> bool:
        """
        Check if file operation is used without context manager.
        """
        call_str = self._get_call_string(node)
        file_operations = ["open", "read", "write", "close"]

        if any(op in call_str.lower() for op in file_operations):
            # Check if it's not in a with statement
            return not isinstance(node.parent, ast.With)
        return False

    def _estimate_algorithm_complexity(self, node: ast.FunctionDef) -> str:
        """
        Estimate algorithm complexity.
        """
        # Count nested loops
        loop_count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.For):
                loop_count += 1

        if loop_count == 0:
            return "O(1)"
        if loop_count == 1:
            return "O(n)"
        if loop_count == 2:
            return "O(n²)"
        if loop_count == 3:
            return "O(n³)"
        return "O(n^k)"

    def _count_io_operations(self, node: ast.FunctionDef) -> int:
        """
        Count I/O operations in function.
        """
        io_operations = ["open", "read", "write", "close", "input", "print"]
        count = 0

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_str = self._get_call_string(child)
                if any(op in call_str.lower() for op in io_operations):
                    count += 1

        return count

    def _is_in_loop(self, node) -> bool:
        """
        Check if node is inside a loop.
        """
        current = node
        while hasattr(current, "parent"):
            current = current.parent
            if isinstance(current, ast.For) or isinstance(current, ast.While):
                return True
        return False

    def _count_by_severity(self, issues: list[PerformanceIssue]) -> dict[str, int]:
        """
        Count issues by severity.
        """
        counts = defaultdict(int)
        for issue in issues:
            counts[issue.severity] += 1
        return dict(counts)

    def generate_report(self) -> dict[str, Any]:
        """
        Generate comprehensive performance analysis report.
        """
        total_issues = len(self.issues)
        severity_counts = self._count_by_severity(self.issues)

        # Group by issue type
        issue_types = defaultdict(int)
        for issue in self.issues:
            issue_types[issue.type] += 1

        # Group by impact
        impact_counts = defaultdict(int)
        for issue in self.issues:
            impact_counts[issue.impact] += 1

        # Group by file
        file_issues = defaultdict(list)
        for issue in self.issues:
            file_issues[issue.file].append(issue)

        return {
            "summary": {
                "total_issues": total_issues,
                "severity_counts": severity_counts,
                "issue_types": dict(issue_types),
                "impact_counts": dict(impact_counts),
                "files_affected": len(file_issues),
            },
            "issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "file": issue.file,
                    "line": issue.line,
                    "column": issue.column,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "confidence": issue.confidence,
                    "impact": issue.impact,
                }
                for issue in self.issues
            ],
            "files": {
                file: {
                    "issue_count": len(issues),
                    "severity_counts": self._count_by_severity(issues),
                }
                for file, issues in file_issues.items()
            },
        }


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Performance Anti-Pattern Detector")
    parser.add_argument("path", help="Path to analyze")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--severity", choices=["low", "medium", "high"], help="Filter by severity")
    parser.add_argument("--type", help="Filter by issue type")
    parser.add_argument("--impact", help="Filter by impact level")
    parser.add_argument("--disable", nargs="+", help="Disable specific patterns")

    args = parser.parse_args()

    detector = PerformanceAntiPatternDetector()

    # Disable patterns if requested
    if args.disable:
        for pattern in args.disable:
            if pattern in detector.patterns:
                detector.patterns[pattern] = False

    # Analyze files
    path = Path(args.path)
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))

    for file_path in files:
        detector.analyze_file(file_path)

    # Generate report
    report = detector.generate_report()

    # Filter results if requested
    if args.severity or args.type or args.impact:
        filtered_issues = []
        for issue in report["issues"]:
            if args.severity and issue["severity"] != args.severity:
                continue
            if args.type and issue["type"] != args.type:
                continue
            if args.impact and issue["impact"] != args.impact:
                continue
            filtered_issues.append(issue)
        report["issues"] = filtered_issues
        report["summary"]["total_issues"] = len(filtered_issues)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Pretty print report
        print("⚡ PERFORMANCE ANTI-PATTERN DETECTION REPORT")
        print("=" * 60)
        print(f"Total issues found: {report['summary']['total_issues']}")
        print(f"Files affected: {report['summary']['files_affected']}")
        print()

        print("Severity breakdown:")
        for severity, count in report["summary"]["severity_counts"].items():
            print(f"  {severity}: {count}")
        print()

        print("Issue types:")
        for issue_type, count in report["summary"]["issue_types"].items():
            print(f"  {issue_type}: {count}")
        print()

        print("Impact breakdown:")
        for impact, count in report["summary"]["impact_counts"].items():
            print(f"  {impact}: {count}")
        print()

        if report["issues"]:
            print("Detailed findings:")
            for issue in report["issues"]:
                print(
                    f"  {issue['severity'].upper()}: {issue['type']} in {issue['file']}:{issue['line']}",
                )
                print(f"    {issue['message']}")
                print(f"    Suggestion: {issue['suggestion']}")
                print(f"    Impact: {issue['impact']}")
                print()


if __name__ == "__main__":
    main()
