#!/usr/bin/env python3
"""
Pheno-SDK Legacy Code Scanner
==============================

Comprehensive scanner for detecting legacy code, deprecated patterns,
compatibility issues, bad import systems, and other code quality problems.

Features:
- Legacy import detection (absolute/relative import anti-patterns)
- Deprecated API usage detection
- Shim/polyfill detection
- Lazy import scanning
- Compatibility issue detection
- Bad practice pattern matching
- Security vulnerability patterns
"""

import ast
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScanFinding:
    """
    Represents a finding from the legacy code scan.
    """

    file_path: str
    line_number: int
    code_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: str = ""
    context: str = ""
    pattern: str = ""
    autofix: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file_path,
            "line": self.line_number,
            "type": self.code_type,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
            "context": self.context,
            "pattern": self.pattern,
            "autofix": self.autofix,
        }


@dataclass
class ScanResults:
    """
    Container for scan results.
    """

    findings: list[ScanFinding] = field(default_factory=list)
    files_scanned: int = 0
    lines_scanned: int = 0
    total_findings: int = 0
    _seen_keys: set[tuple[str, int, str, str]] = field(default_factory=set, repr=False)

    def add_finding(self, finding: ScanFinding) -> None:
        key = (finding.file_path, finding.line_number, finding.code_type, finding.message)
        if key in self._seen_keys:
            return
        self._seen_keys.add(key)
        self.findings.append(finding)
        self.total_findings += 1

    def get_findings_by_severity(self, severity: str) -> list[ScanFinding]:
        return [f for f in self.findings if f.severity == severity]

    def get_findings_by_type(self, code_type: str) -> list[ScanFinding]:
        return [f for f in self.findings if f.code_type == code_type]

    def summary(self) -> dict[str, Any]:
        return {
            "files_scanned": self.files_scanned,
            "lines_scanned": self.lines_scanned,
            "total_findings": self.total_findings,
            "findings_by_severity": {
                "error": len(self.get_findings_by_severity("error")),
                "warning": len(self.get_findings_by_severity("warning")),
                "info": len(self.get_findings_by_severity("info")),
            },
            "findings_by_type": {
                code_type: len(self.get_findings_by_type(code_type))
                for code_type in set(f.code_type for f in self.findings)
            },
        }


class LegacyCodeScanner:
    """
    Main scanner for legacy code patterns.
    """

    def __init__(self, root_path: Path, config: dict[str, Any] = None):
        self.root_path = root_path
        self.config = config or self._default_config()
        self.results = ScanResults()
        self._scanned_files = set()

    def _default_config(self) -> dict[str, Any]:
        """
        Default configuration for scanning.
        """
        return {
            "excluded_dirs": [
                ".venv",
                "__pycache__",
                ".git",
                "build",
                "dist",
                "htmlcov",
                "node_modules",
                ".pytest_cache",
                ".mypy_cache",
            ],
            "excluded_files": ["__init__.py"],
            "file_extensions": [".py"],
            "severity_threshold": "warning",  # Report warnings and errors
            "max_findings_per_file": 50,
        }

    def scan(self, paths: list[Path] = None) -> ScanResults:
        """
        Main scanning function.
        """
        if paths is None:
            paths = [self.root_path]

        for path in paths:
            if path.is_file():
                self._scan_file(path)
            elif path.is_dir():
                self._scan_directory(path)

        self.results.files_scanned = len(self._scanned_files)
        return self.results

    def _scan_directory(self, directory: Path) -> None:
        """
        Scan a directory recursively.
        """
        if any(excl in directory.name for excl in self.config["excluded_dirs"]):
            return

        for item in directory.iterdir():
            if item.is_file() and item.suffix in self.config["file_extensions"]:
                if item.name not in self.config["excluded_files"]:
                    self._scan_file(item)
            elif item.is_dir():
                self._scan_directory(item)

    def _scan_file(self, file_path: Path) -> None:
        """
        Scan a single Python file.
        """
        if file_path in self._scanned_files:
            return

        self._scanned_files.add(file_path)

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.splitlines()
            self.results.lines_scanned += len(lines)

            # Parse AST for syntactic analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
                self._scan_ast(file_path, tree, lines)
            except SyntaxError:
                # If AST parsing fails, still do text-based scanning
                pass

            # Text-based scanning for patterns that aren't AST-dependent
            self._scan_text_patterns(file_path, content, lines)

        except OSError as e:
            finding = ScanFinding(
                file_path=str(file_path),
                line_number=0,
                code_type="file_error",
                severity="error",
                message=f"Could not read file: {e}",
            )
            self.results.add_finding(finding)

    def _scan_ast(self, file_path: Path, tree: ast.AST, lines: list[str]) -> None:
        """
        Scan using AST analysis.
        """
        visitors = [
            ImportVisitor,
            DeprecationVisitor,
            CompatibilityVisitor,
            PythonicPatternsVisitor,
            HexagonalArchitectureVisitor,
            TDDPatternsVisitor,
            OverEngineeringVisitor,
            SecurityVisitor,
            PerformanceVisitor,
            ComplexityVisitor,
        ]

        for visitor_cls in visitors:
            visitor_cls(self, file_path, lines).visit(tree)

    def _scan_text_patterns(self, file_path: Path, content: str, lines: list[str]) -> None:
        """
        Scan text patterns that don't require AST.
        """
        # StringPatternScanner handles regex patterns for architecture patterns
        StringPatternScanner(self, file_path, lines).scan(content)

        # Additional pattern scanning for Pythonic patterns
        self._scan_pythonic_patterns(content, lines, file_path)

        # Scan for hexagonal architecture patterns
        self._scan_hexagonal_patterns(content, lines, file_path)

    def _scan_pythonic_patterns(self, content: str, lines: list[str], file_path: Path) -> None:
        """
        Scan for pythonic code patterns in text.
        """
        for i, line in enumerate(lines, 1):
            line_strip = line.strip()

            # Check for non-pythonic patterns
            if "for i in range(len(" in line_strip:
                self.results.add_finding(
                    ScanFinding(
                        file_path=str(file_path),
                        line_number=i,
                        code_type="pythonic",
                        severity="info",
                        message="Consider using enumerate() instead of range(len())",
                        suggestion="Use: for i, item in enumerate(items):",
                        context=line_strip,
                        pattern="range(len())",
                    ),
                )

            # Check for manual list building detected via comments
            if any(keyword in line_strip.lower() for keyword in ["manual list", "build list"]):
                self.results.add_finding(
                    ScanFinding(
                        file_path=str(file_path),
                        line_number=i,
                        code_type="pythonic",
                        severity="info",
                        message="Manual list building detected",
                        suggestion="Consider using list comprehension or generator expression",
                        context=line_strip,
                        pattern="manual list building",
                    ),
                )

    def _scan_hexagonal_patterns(self, content: str, lines: list[str], file_path: Path) -> None:
        """
        Lightweight text heuristics for hexagonal architecture discipline.
        """
        path = Path(file_path)
        lowered_parts = {part.lower() for part in path.parts}
        in_domain_layer = bool(lowered_parts & {"domain", "entities", "value_objects"})
        in_application_layer = bool(
            lowered_parts & {"application", "use_cases", "commands", "services"},
        )

        domain_forbidden_tokens = [
            "import requests",
            "requests.",
            "httpx.",
            "boto3",
            "sqlalchemy",
            "pymongo",
            "redis",
            "kafka",
            "s3client",
            "client(",
            "session(",
            "cursor(",
        ]
        application_forbidden_tokens = [
            "import requests",
            "requests.",
            "httpx.",
            "boto3",
            "sqlalchemy",
            "pymongo",
            "redis",
            "kafka",
            "s3client",
        ]

        for i, line in enumerate(lines, 1):
            check_line = line.strip()
            lowered = check_line.lower()

            if in_domain_layer and any(token in lowered for token in domain_forbidden_tokens):
                self.results.add_finding(
                    ScanFinding(
                        file_path=str(file_path),
                        line_number=i,
                        code_type="hexagonal",
                        severity="warning",
                        message="Domain layer references infrastructure concerns",
                        suggestion="Depend on abstract ports from application layer instead of concrete clients",
                        context=check_line,
                        pattern="domain->infrastructure reference",
                    ),
                )

            if in_application_layer and "adapter" not in lowered:
                if any(token in lowered for token in application_forbidden_tokens):
                    self.results.add_finding(
                        ScanFinding(
                            file_path=str(file_path),
                            line_number=i,
                            code_type="hexagonal",
                            severity="info",
                            message="Application layer reaches into external infrastructure directly",
                            suggestion="Route through adapters/ports to keep application layer pure",
                            context=check_line,
                            pattern="application->external reference",
                        ),
                    )


class BaseASTVisitor(ast.NodeVisitor):
    """
    Base class for AST visitors.
    """

    def __init__(self, scanner: LegacyCodeScanner, file_path: Path, lines: list[str]):
        self.scanner = scanner
        self.file_path = str(file_path)
        self.lines = lines

    def add_finding(
        self,
        node: ast.AST,
        code_type: str,
        severity: str,
        message: str,
        suggestion: str = "",
        pattern: str = "",
        autofix: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a finding at the node's line number.
        """
        line_no = getattr(node, "lineno", 0)
        context = self.lines[line_no - 1].strip() if 0 < line_no <= len(self.lines) else ""

        finding = ScanFinding(
            file_path=self.file_path,
            line_number=line_no,
            code_type=code_type,
            severity=severity,
            message=message,
            suggestion=suggestion,
            context=context,
            pattern=pattern,
            autofix=autofix or {},
        )

        self.scanner.results.add_finding(finding)

    def _get_full_name(self, node: ast.AST) -> str:
        """
        Return dotted name for an AST node.
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._get_full_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        if isinstance(node, ast.Call):
            return self._get_full_name(node.func)
        if isinstance(node, ast.alias):
            return node.name
        return ""

    def _line_text(self, node: ast.AST) -> str:
        """
        Return original source line for node.
        """
        line_no = getattr(node, "lineno", 0)
        if 0 < line_no <= len(self.lines):
            return self.lines[line_no - 1].rstrip()
        return ""

    def _strip_docstring(self, body: list[ast.stmt]) -> list[ast.stmt]:
        """
        Return body without a leading docstring expression.
        """
        if not body:
            return body
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            return body[1:]
        return body


class ImportVisitor(BaseASTVisitor):
    """
    Visitor for detecting problematic imports.
    """

    BAD_IMPORT_PATTERNS = [
        # Relative imports that are too deep
        r"from \.\.\.\.",
        # Lazy imports (import inside functions)
        r"def.*:$[^}]*^import\s|class.*:$[^}]*^import\s",
        # Import * (wildcard imports)
        r"from .* import \*",
        # Circular import patterns
        r"import.*\b(sys|_)\b",
        # Deprecated import patterns
        r"import imp\b|import importlib.util\b",
    ]

    def visit_Import(self, node: ast.Import) -> None:
        """
        Check import statements.
        """
        # Check wildcard imports
        for alias in node.names:
            if alias.name == "*":
                self.add_finding(
                    node,
                    "bad_import",
                    "warning",
                    "Wildcard import 'import *' is discouraged",
                    "Use explicit imports instead",
                    "import *",
                )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Check from-import statements.
        """
        if node.level > 2:  # Deep relative imports
            self.add_finding(
                node,
                "bad_import",
                "warning",
                f"Deep relative import (level {node.level}) is hard to maintain",
                "Use absolute imports or restructure project",
                f"from {'..' * node.level}",
            )

        # Check for wildcard imports
        if any(alias.name == "*" for alias in node.names):
            self.add_finding(
                node,
                "bad_import",
                "error",
                "Wildcard import 'from ... import *' is prohibited",
                "Import specific items: from module import item1, item2",
                "import *",
            )

        # Check for absolute imports in a relative-importing codebase
        if node.level == 0 and not hasattr(node, "module"):
            # This is probably fine, skip validation
            pass


class DeprecationVisitor(BaseASTVisitor):
    """
    Visitor for detecting deprecated usage.
    """

    DEPRECATED_PATTERNS = [
        # Old string formatting
        r"%\(\w+\)s|%[ds]",
        # Old dictionary iteration
        r"\.iteritems\(\)|\.itervalues\(\)",
        # Old file opening
        r"open\(.*,\s*[rw]\)",
        # Old exception syntax
        r"except\s+\w+\s*,",
        # Old division
        r"from\s+__future__\s+import\s+division",
    ]

    def visit_Call(self, node: ast.Call) -> None:
        """
        Check function calls for deprecated patterns.
        """
        # Check calls to deprecated functions
        if hasattr(node.func, "id"):
            func_name = node.func.id
        elif hasattr(node.func, "attr"):
            func_name = node.func.attr
        else:
            func_name = str(node.func)

        # Check for deprecated function usage
        deprecated_funcs = ["imp.", "optparse", "commands.", "cgi.escape"]
        for deprecated in deprecated_funcs:
            if deprecated in func_name:
                self.add_finding(
                    node,
                    "deprecated",
                    "warning",
                    f"Use of deprecated function/module: {func_name}",
                    "Use modern alternatives from the standard library",
                    deprecated,
                )


class PythonicPatternsVisitor(BaseASTVisitor):
    """
    Visitor for detecting non-Pythonic code patterns.
    """

    def visit_For(self, node: ast.For) -> None:
        """
        Check for non-Pythonic loop patterns.
        """
        # Check for manual index tracking instead of enumerate()
        if isinstance(node.iter, ast.Call) and getattr(node.iter.func, "id", None) == "range":
            args = node.iter.args
            len_call_candidates: list[ast.AST] = []

            if len(args) == 1:
                len_call_candidates.append(args[0])
            elif len(args) >= 2:
                # Common anti-patterns: range(0, len(items)) or range(len(items), ...)
                len_call_candidates.extend(args[:2])

            for candidate in len_call_candidates:
                if isinstance(candidate, ast.Call) and getattr(candidate.func, "id", None) == "len":
                    self.add_finding(
                        node,
                        "pythonic",
                        "warning",
                        "Non-pythonic loop: use enumerate() instead of range(len())",
                        "Use: for index, item in enumerate(items)",
                        "range(len())",
                    )
                    break

        # Check for manual zip() simulation
        if (
            isinstance(node.target, ast.Tuple)
            and len(node.target.elts) == 2
            and isinstance(node.iter, ast.Call)
            and getattr(node.iter.func, "id", None) == "range"
        ):
            # for i, j in range(...) pattern suggests manual zip
            self.add_finding(
                node,
                "pythonic",
                "info",
                "Consider using zip() for parallel iteration",
                "Use: for x, y in zip(list1, list2)",
                "manual parallel iteration",
            )

        # Check for EAFP vs LBYL patterns
        self._check_lby_l_patterns(node)

    def _check_lby_l_patterns(self, node: ast.For) -> None:
        """
        Check for Look Before You Leap anti-patterns.
        """
        # This is complex to detect statically, but we can check for common patterns

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """
        Check list comprehensions.
        """
        # Check for nested list comprehensions (can be hard to read)
        if any(isinstance(generator.iter, ast.ListComp) for generator in node.generators):
            self.add_finding(
                node,
                "pythonic",
                "info",
                "Nested list comprehensions can be hard to read",
                "Consider breaking into separate comprehensions or using loops",
                "nested comprehension",
            )

    def visit_Call(self, node: ast.Call) -> None:
        """
        Check function calls for pythonic patterns.
        """
        # Check for len() comparisons that could be truthy checks
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "len"
            and node in self._get_comparison_context()
        ):
            self.add_finding(
                node,
                "pythonic",
                "info",
                "Consider direct truthiness check instead of len() > 0",
                "Use: if items: instead of if len(items) > 0:",
                "len() comparison",
            )

        # Check for manual list building
        if self._is_manual_list_building(node):
            self.add_finding(
                node,
                "pythonic",
                "info",
                "Consider using list comprehension",
                "Use: [x for x in iterable if condition]",
                "manual list building",
            )

    def _get_comparison_context(self) -> list[ast.AST]:
        """
        Get comparison context (simplified).
        """
        return []  # Would need more context tracking

    def _is_manual_list_building(self, node: ast.Call) -> bool:
        """
        Check if this is manual list building.
        """
        # This would require more sophisticated analysis
        return False


class HexagonalArchitectureVisitor(BaseASTVisitor):
    """
    Visitor for validating hexagonal architecture patterns.
    """

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Check import patterns for layer violations.
        """
        if node.module:
            self._check_layer_violations(node.module, node)

    def visit_Import(self, node: ast.Import) -> None:
        """
        Check import statements.
        """
        for alias in node.names:
            self._check_layer_violations(alias.name, node)

    def _check_layer_violations(self, module_name: str, node: ast.AST) -> None:
        """
        Check if imports violate hexagonal architecture layers.
        """
        # Domain layer should not import infrastructure
        if self._is_domain_module(self.file_path) and self._is_infrastructure_module(module_name):
            self.add_finding(
                node,
                "hexagonal",
                "warning",
                "Hexagonal architecture violation: domain layer importing infrastructure",
                "Use dependency inversion: domain should depend on abstractions, not concrete implementations",
                f"domain -> infrastructure: {module_name}",
            )

        # Application layer should not directly import external services
        if self._is_application_module(self.file_path) and self._is_external_service(module_name):
            self.add_finding(
                node,
                "hexagonal",
                "warning",
                "Hexagonal architecture violation: application layer importing external services directly",
                "Use adapters/ports pattern: access external services through interfaces in domain layer",
                f"application -> external: {module_name}",
            )

    def _is_domain_module(self, file_path: str) -> bool:
        """
        Check if file is in domain layer.
        """
        path = Path(file_path)
        return any(part in ["domain", "entities", "value_objects"] for part in path.parts)

    def _is_application_module(self, file_path: str) -> bool:
        """
        Check if file is in application layer.
        """
        path = Path(file_path)
        return any(part in ["application", "use_cases", "commands"] for part in path.parts)

    def _is_infrastructure_module(self, module_name: str) -> bool:
        """
        Check if module is infrastructure.
        """
        return any(
            infra in module_name.lower()
            for infra in [
                "repository",
                "dao",
                "storage",
                "database",
                "api",
                "http",
                "client",
                "service",
                "external",
                "adapter",
            ]
        )

    def _is_external_service(self, module_name: str) -> bool:
        """
        Check if module represents external services.
        """
        return any(
            ext in module_name.lower()
            for ext in [
                "requests",
                "httpx",
                "aiohttp",
                "pydantic",
                "sqlalchemy",
                "redis",
                "kafka",
                "s3",
                "openai",
                "anthropic",
            ]
        )


class TDDPatternsVisitor(BaseASTVisitor):
    """
    Visitor for validating TDD and testing patterns.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Check function definitions for testing patterns.
        """
        if self._is_test_file(self.file_path):
            self._validate_test_function(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Check class definitions.
        """
        if self._is_test_file(self.file_path):
            self._validate_test_class(node)

    def _validate_test_function(self, node: ast.FunctionDef) -> None:
        """
        Validate test function patterns.
        """
        func_name = node.name

        # Check test naming conventions
        if not func_name.startswith("test_"):
            if not any(
                keyword in func_name.lower()
                for keyword in ["setup", "teardown", "fixture", "parametrize"]
            ):
                self.add_finding(
                    node,
                    "tdd",
                    "warning",
                    "Test function should start with 'test_'",
                    "Use: def test_should_do_something(self):",
                    f"function name: {func_name}",
                )

        # Encourage Given-When-Then (or similar) documentation
        docstring = ast.get_docstring(node)
        if not docstring:
            self.add_finding(
                node,
                "tdd",
                "info",
                "Test is missing a descriptive docstring",
                "Add a docstring that outlines Given/When/Then or Arrange/Act/Assert context",
                "missing test docstring",
            )
        elif not self._has_gwt_structure(docstring):
            self.add_finding(
                node,
                "tdd",
                "info",
                "Consider using Given-When-Then structure in test docstring",
                'Use: """Given: some context\\nWhen: some action\\nThen: some outcome"""',
                "missing GWT structure",
            )

    def _validate_test_class(self, node: ast.ClassDef) -> None:
        """
        Validate test class patterns.
        """
        class_name = node.name

        # Check test class naming
        if not class_name.startswith("Test"):
            self.add_finding(
                node,
                "tdd",
                "warning",
                "Test class should start with 'Test'",
                "Use: class TestSomeFeature:",
                f"class name: {class_name}",
            )

    def _is_test_file(self, file_path: str) -> bool:
        """
        Check if file is a test file.
        """
        return "test" in Path(file_path).name.lower() or "tests" in Path(file_path).parts

    def _has_gwt_structure(self, docstring: str) -> bool:
        """
        Check if docstring has Given-When-Then structure.
        """
        if not docstring:
            return False
        text = docstring.lower()
        return all(keyword in text for keyword in ("given", "when", "then"))


class OverEngineeringVisitor(BaseASTVisitor):
    """
    Visitor for identifying over-engineering or code wastage.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        body = self._strip_docstring(list(node.body))
        if not body:
            # Completely empty function
            self.add_finding(
                node,
                "code_wastage",
                "info",
                "Function body is empty",
                "Implement behavior or remove the unused placeholder",
                "empty function",
            )
            return

        first_stmt = body[0]

        if len(body) == 1 and isinstance(first_stmt, ast.Pass):
            # Allow abstract methods via ABC by checking decorators
            if not self._is_abstract(node):
                self.add_finding(
                    node,
                    "code_wastage",
                    "info",
                    "Function contains only 'pass'",
                    "Remove the stub or implement the method",
                    "pass stub",
                )
        elif len(body) == 1 and isinstance(first_stmt, ast.Return):
            call_name = self._is_identity_wrapper(node, first_stmt)
            if call_name:
                self.add_finding(
                    node,
                    "over_engineering",
                    "info",
                    f"Function is a thin wrapper around '{call_name}'",
                    "Inline the wrapped call or provide additional behavior",
                    "thin wrapper",
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        methods = [stmt for stmt in node.body if isinstance(stmt, ast.FunctionDef)]
        if not methods:
            self.generic_visit(node)
            return

        stub_methods = 0
        for method in methods:
            body = self._strip_docstring(list(method.body))
            if not body:
                stub_methods += 1
            elif len(body) == 1:
                stmt = body[0]
                if isinstance(stmt, ast.Pass) or (
                    isinstance(stmt, ast.Raise)
                    and isinstance(stmt.exc, ast.Call)
                    and self._get_full_name(stmt.exc.func) == "NotImplementedError"
                ):
                    stub_methods += 1

        if stub_methods and stub_methods == len(methods):
            self.add_finding(
                node,
                "over_engineering",
                "warning",
                "Class defines only stub methods",
                "Replace with Protocol/ABC or remove unused scaffolding",
                "stub class",
            )

        self.generic_visit(node)

    def _is_abstract(self, node: ast.FunctionDef) -> bool:
        decorators = {self._get_full_name(deco) for deco in node.decorator_list}
        return "abc.abstractmethod" in decorators or "abstractmethod" in decorators

    def _is_identity_wrapper(self, func: ast.FunctionDef, return_stmt: ast.Return) -> str:
        value = return_stmt.value
        if not isinstance(value, ast.Call):
            return ""

        call_name = self._get_full_name(value.func)
        if not call_name:
            return ""

        args = func.args
        if getattr(args, "defaults", None) or getattr(args, "kw_defaults", None):
            # Skip functions with defaulted args to avoid false positives
            return ""

        positional_params = [arg.arg for arg in getattr(args, "args", [])]
        if func.args.vararg or func.args.kwarg:
            return ""

        call_args = []
        for arg in value.args:
            if isinstance(arg, ast.Name):
                call_args.append(arg.id)
            else:
                return ""

        if positional_params != call_args:
            return ""

        for kw in value.keywords:
            if not isinstance(kw.value, ast.Name) or kw.value.id != kw.arg:
                return ""

        return call_name


class SecurityVisitor(BaseASTVisitor):
    """
    Visitor for detecting security-sensitive patterns.
    """

    SUBPROCESS_FUNCS = {
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
        "subprocess.run",
    }

    REQUEST_FUNCS = {
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "requests.request",
    }

    WEAK_HASH_FUNCS = {"hashlib.md5", "hashlib.sha1"}
    INSECURE_RANDOM_FUNCS = {"random.random", "random.randrange", "random.randint"}

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_full_name(node.func)

        if func_name in {"eval", "exec"}:
            self.add_finding(
                node,
                "security",
                "error",
                f"Use of dangerous builtin '{func_name}' detected",
                "Prefer ast.literal_eval or safer parsing utilities",
                func_name,
            )

        if func_name in self.SUBPROCESS_FUNCS and self._has_truthy_keyword(node, "shell"):
            self.add_finding(
                node,
                "security",
                "error",
                "subprocess call with shell=True can lead to shell injection",
                "Avoid shell=True or sanitize inputs thoroughly",
                "shell=True",
            )

        if func_name in {"yaml.load", "yaml.Loader.load"} and not self._has_keyword(node, "Loader"):
            self.add_finding(
                node,
                "security",
                "warning",
                "yaml.load without specifying a safe Loader is unsafe",
                "Use yaml.safe_load or provide Loader=yaml.SafeLoader",
                "yaml.load",
                autofix={
                    "type": "replace_text",
                    "old": "yaml.load",
                    "new": "yaml.safe_load",
                    "scope": "line",
                },
            )

        if func_name in {"pickle.load", "pickle.loads"}:
            self.add_finding(
                node,
                "security",
                "warning",
                "pickle load detected - avoid untrusted pickle data",
                "Use safer serialization formats like json or msgpack",
                func_name,
            )

        if func_name in self.WEAK_HASH_FUNCS:
            self.add_finding(
                node,
                "security",
                "warning",
                f"Weak hash function '{func_name.split('.')[-1]}' detected",
                "Use sha256 or stronger hashing algorithms",
                func_name,
                autofix={
                    "type": "replace_text",
                    "old": func_name,
                    "new": "hashlib.sha256",
                    "scope": "line",
                },
            )

        if func_name in self.REQUEST_FUNCS and self._has_false_keyword(node, "verify"):
            self.add_finding(
                node,
                "security",
                "warning",
                "requests.* with verify=False disables TLS certificate verification",
                "Remove verify=False or supply a CA bundle",
                "verify=False",
                autofix={
                    "type": "replace_text",
                    "old": "verify=False",
                    "new": "verify=True",
                    "scope": "line",
                },
            )

        if func_name in self.REQUEST_FUNCS and not self._has_keyword(node, "timeout"):
            self.add_finding(
                node,
                "performance",
                "info",
                "requests call without timeout can hang indefinitely",
                "Pass timeout=seconds to enforce network timeouts",
                "missing timeout",
            )

        if func_name == "os.system":
            self.add_finding(
                node,
                "security",
                "warning",
                "os.system detected - prefer subprocess.run with explicit args",
                "Use subprocess without shell or shlex.quote inputs",
                "os.system",
            )

        if func_name == "tempfile.mktemp":
            self.add_finding(
                node,
                "security",
                "warning",
                "tempfile.mktemp is insecure due to race conditions",
                "Use tempfile.NamedTemporaryFile or mkstemp",
                "tempfile.mktemp",
            )

        if func_name in self.INSECURE_RANDOM_FUNCS:
            self.add_finding(
                node,
                "security",
                "info",
                f"Insecure random source '{func_name}' detected for security-sensitive operations",
                "Use secrets.randbelow or secrets.token_hex for cryptographic randomness",
                func_name,
            )

        if func_name == "hashlib.new":
            algo = self._first_constant_arg(node)
            if algo and algo.lower() in {"md5", "sha1"}:
                self.add_finding(
                    node,
                    "security",
                    "warning",
                    f"Weak hash algorithm '{algo}' detected via hashlib.new",
                    "Use hashlib.sha256 or stronger alternatives",
                    algo,
                    autofix={
                        "type": "replace_text",
                        "old": f"'{algo}'",
                        "new": "'sha256'",
                        "scope": "line",
                    },
                )

        if func_name == "jwt.decode":
            if self._has_false_keyword(node, "verify"):
                self.add_finding(
                    node,
                    "security",
                    "error",
                    "jwt.decode called with verify=False disables signature verification",
                    "Remove verify=False or validate token using dedicated verification options",
                    "verify=False",
                )
            options_kw = self._get_keyword(node, "options")
            if isinstance(options_kw, ast.Dict):
                for key_node, value_node in zip(options_kw.keys, options_kw.values, strict=False):
                    if (
                        isinstance(key_node, ast.Constant)
                        and str(key_node.value).lower() == "verify_signature"
                    ):
                        if isinstance(value_node, ast.Constant) and value_node.value is False:
                            self.add_finding(
                                node,
                                "security",
                                "error",
                                "jwt.decode options disable signature verification",
                                "Remove verify_signature=False to enforce signature checks",
                                "verify_signature=False",
                            )

    def _has_keyword(self, node: ast.Call, name: str) -> bool:
        return any(kw.arg == name for kw in node.keywords if kw.arg)

    def _has_truthy_keyword(self, node: ast.Call, name: str) -> bool:
        for kw in node.keywords:
            if kw.arg == name and isinstance(kw.value, ast.Constant):
                return bool(kw.value.value)
        return False

    def _has_false_keyword(self, node: ast.Call, name: str) -> bool:
        for kw in node.keywords:
            if kw.arg == name and isinstance(kw.value, ast.Constant):
                return kw.value.value is False
        return False

    def _get_keyword(self, node: ast.Call, name: str) -> ast.AST | None:
        for kw in node.keywords:
            if kw.arg == name:
                return kw.value
        return None

    def _first_constant_arg(self, node: ast.Call) -> str | None:
        if node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                return first.value
        return None


class PerformanceVisitor(BaseASTVisitor):
    """
    Visitor for detecting performance anti-patterns.
    """

    def __init__(self, scanner: LegacyCodeScanner, file_path: Path, lines: list[str]):
        super().__init__(scanner, file_path, lines)
        self._async_depth = 0
        self._loop_depth = 0

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._async_depth += 1
        self.generic_visit(node)
        self._async_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_full_name(node.func)

        if func_name == "time.sleep":
            self.add_finding(
                node,
                "performance",
                "info",
                "Blocking sleep detected; consider using asynchronous sleep or backoff",
                "Use asyncio.sleep in async code or timers in production services",
                "time.sleep",
            )

        if self._async_depth > 0 and func_name in SecurityVisitor.REQUEST_FUNCS:
            self.add_finding(
                node,
                "performance",
                "warning",
                "Blocking HTTP request inside async function",
                "Use an asynchronous HTTP client such as httpx.AsyncClient or aiohttp",
                func_name,
            )

        if func_name.endswith(".iterrows"):
            self.add_finding(
                node,
                "performance",
                "warning",
                "pandas.DataFrame.iterrows is slow",
                "Use itertuples() or vectorized operations",
                "iterrows",
            )

        if func_name.endswith(".apply") and self._is_pandas_series_call(node):
            self.add_finding(
                node,
                "performance",
                "info",
                "pandas apply detected - consider vectorized operations",
                "Vectorize calculations or use assign/transform when possible",
                "pandas.apply",
            )

    def visit_For(self, node: ast.For) -> None:
        self._loop_depth += 1
        if self._contains_blocking_sleep(node):
            self.add_finding(
                node,
                "performance",
                "warning",
                "time.sleep inside loop can lead to significant waits",
                "Consider scheduling or batching instead of per-iteration sleep",
                "sleep in loop",
            )
        self.generic_visit(node)
        self._loop_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        self._loop_depth += 1
        if self._contains_blocking_sleep(node):
            self.add_finding(
                node,
                "performance",
                "warning",
                "time.sleep inside loop can cause long-running CPU idle loops",
                "Use event-driven waits or async sleep with backoff",
                "sleep in loop",
            )
        self.generic_visit(node)
        self._loop_depth -= 1

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if (
            isinstance(node.op, ast.Add)
            and isinstance(node.target, ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and self._loop_depth > 0
        ):
            self.add_finding(
                node,
                "performance",
                "info",
                "String concatenation inside loop detected",
                "Use list accumulation with ''.join() outside the loop",
                "string concat in loop",
            )
        self.generic_visit(node)

    def _is_pandas_series_call(self, node: ast.Call) -> bool:
        # Looks for attribute access like df['col'].apply(...)
        attr = node.func
        if isinstance(attr, ast.Attribute) and attr.attr == "apply":
            return True
        return False

    def _contains_blocking_sleep(self, node: ast.AST) -> bool:
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and self._get_full_name(child.func) == "time.sleep":
                return True
        return False


class ComplexityVisitor(BaseASTVisitor):
    """
    Visitor for measuring code complexity heuristics.
    """

    MAX_FUNCTION_LENGTH = 60
    MAX_BRANCH_NODES = 20
    MAX_PARAMS = 8
    MAX_RETURNS = 6
    BRANCH_TYPES = (
        ast.If,
        ast.For,
        ast.While,
        ast.With,
        ast.Try,
        ast.BoolOp,
    )
    if hasattr(ast, "Match"):
        BRANCH_TYPES = BRANCH_TYPES + (ast.Match,)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function_complexity(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function_complexity(node)
        self.generic_visit(node)

    def _check_function_complexity(self, node: ast.AST) -> None:
        start = getattr(node, "lineno", 0)
        end = getattr(node, "end_lineno", start)
        length = (end - start) + 1 if end and start else 0

        branch_nodes = sum(isinstance(child, self.BRANCH_TYPES) for child in ast.walk(node))

        return_count = sum(isinstance(child, ast.Return) for child in ast.walk(node))

        args = getattr(node, "args", None)
        if args:
            param_count = (
                len(args.args)
                + len(getattr(args, "kwonlyargs", []))
                + (1 if getattr(args, "vararg", None) else 0)
                + (1 if getattr(args, "kwarg", None) else 0)
            )
        else:
            param_count = 0

        if length and length > self.MAX_FUNCTION_LENGTH:
            self.add_finding(
                node,
                "complexity",
                "warning",
                f"Function spans {length} lines which exceeds {self.MAX_FUNCTION_LENGTH}",
                "Refactor into smaller units or extract helper functions",
                "function length",
            )

        if branch_nodes > self.MAX_BRANCH_NODES:
            self.add_finding(
                node,
                "complexity",
                "warning",
                f"Function contains {branch_nodes} branching constructs",
                "Simplify conditionals or break into dedicated functions",
                "branching",
            )

        if param_count > self.MAX_PARAMS:
            self.add_finding(
                node,
                "complexity",
                "info",
                f"Function takes {param_count} parameters",
                "Group parameters into objects or reduce arguments",
                "parameter count",
            )

        if return_count > self.MAX_RETURNS:
            self.add_finding(
                node,
                "complexity",
                "info",
                f"Function has {return_count} return statements",
                "Consider reducing branching or consolidating returns",
                "return count",
            )


class CompatibilityVisitor(BaseASTVisitor):
    """
    Visitor for detecting compatibility issues.
    """

    COMPATIBILITY_ISSUES = [
        # Python 2 style code
        r"print\s+.*(?<!\n$)",
        # Old except syntax
        r"except\s+\w+\s*,",
        # Old division behavior
        r"[0-9]+/[0-9]+",  # Division without __future__ import
    ]

    def visit_Print(self, node: ast.AST) -> None:
        """
        Check for Python 2 style print statements.
        """
        legacy_print = getattr(ast, "Print", None)
        if legacy_print and isinstance(node, legacy_print):
            if hasattr(node, "nl") and not node.nl:  # No newline is old syntax
                self.add_finding(
                    node,
                    "compatibility",
                    "error",
                    "Python 2 style print statement without parentheses",
                    "Use 'print()' instead of 'print'",
                    "print (no parens)",
                )


class StringPatternScanner:
    """
    Scanner for text-based patterns that don't require AST.
    """

    PATTERNS = [
        # TODO/FIXME comments (legacy code markers)
        (r"#\s*TODO", "legacy_code", "warning", "TODO comment indicates incomplete code"),
        (r"#\s*FIXME", "legacy_code", "warning", "FIXME comment indicates problematic code"),
        (r"#\s*HACK", "legacy_code", "info", "HACK comment indicates workaround"),
        (r"#\s*XXX", "legacy_code", "info", "XXX comment indicates temporary code"),
        # Security issues
        (r"password\s*=|PASSWORD\s*=", "security", "error", "Hardcoded password detected"),
        (r"secret\s*=|SECRET\s*=", "security", "error", "Hardcoded secret detected"),
        (r"api_key\s*=|API_KEY\s*=", "security", "error", "Hardcoded API key detected"),
        # Code quality issues
        (r"print\([^)]*\)", "code_quality", "info", "Print statement in production code"),
        (r"exit\(|sys\.exit\(", "code_quality", "warning", "Direct exit calls can break cleanup"),
        (
            r"assert\s+False|assert\s+0|assert\s+None",
            "code_quality",
            "warning",
            "Assertion failures as error handling",
        ),
        # Shim/polyfill patterns
        (
            r"shim|polyfill",
            "shims",
            "info",
            "Shim or polyfill detected - consider modern alternatives",
        ),
        (
            r"self\._import_module|__import__",
            "bad_imports",
            "warning",
            "Runtime import manipulation",
        ),
        # Lazy loading patterns
        (
            r"if.*import|import.*if",
            "lazy_import",
            "info",
            "Conditional import detected - may indicate code organization issues",
        ),
        # Security patterns
        (r"eval\(", "security", "error", "eval detected - validate inputs before execution"),
        (r"exec\(", "security", "error", "exec detected - avoid executing dynamic code"),
        (
            r"requests\.[a-z]+\([^)]*verify\s*=\s*False",
            "security",
            "warning",
            "requests with verify=False disables TLS validation",
        ),
        (
            r"os\.system\(",
            "security",
            "warning",
            "os.system detected - prefer subprocess without shell",
        ),
        # Performance patterns
        (
            r"time\.sleep\(",
            "performance",
            "info",
            "Blocking sleep detected; consider async alternatives",
        ),
        (
            r"\.iterrows\(",
            "performance",
            "warning",
            "pandas iterrows is slow; consider vectorized operations",
        ),
        # Complexity / maintainability
        (
            r"except\s+[^:]+:\s+pass",
            "complexity",
            "warning",
            "Swallowed exception detected; handle or log errors",
        ),
        (r"select\s+\*", "complexity", "info", "SELECT * detected - specify columns explicitly"),
        (
            r"^\s*#\s*(def|class|if|for|while|try)\b",
            "code_wastage",
            "info",
            "Commented-out code detected",
        ),
    ]

    def __init__(self, scanner: LegacyCodeScanner, file_path: Path, lines: list[str]):
        self.scanner = scanner
        self.file_path = str(file_path)
        self.lines = lines

    def scan(self, content: str) -> None:
        """
        Scan content for text patterns.
        """
        for pattern, code_type, severity, message in self.PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                line_no = self._get_line_number(match.start(), content)

                finding = ScanFinding(
                    file_path=self.file_path,
                    line_number=line_no,
                    code_type=code_type,
                    severity=severity,
                    message=message,
                    context=self.lines[line_no - 1] if 0 < line_no <= len(self.lines) else "",
                    pattern=pattern,
                )

                self.scanner.results.add_finding(finding)

    def _get_line_number(self, position: int, content: str) -> int:
        """
        Convert character position to line number.
        """
        return content[:position].count("\n") + 1


def _replace_with_count(text: str, old: str, new: str, count: int) -> tuple[str, bool]:
    """
    Replace text with a limited count, returning whether a change occurred.
    """
    if not old or old not in text:
        return text, False
    return text.replace(old, new, count), True


def apply_autofixes(findings: list[ScanFinding]) -> dict[str, int]:
    """
    Apply autofix directives to files in-place.
    """
    fixes_by_file: dict[str, list[ScanFinding]] = defaultdict(list)
    for finding in findings:
        if finding.autofix:
            fixes_by_file[finding.file_path].append(finding)

    summary: dict[str, int] = {}

    for file_path, file_findings in fixes_by_file.items():
        path = Path(file_path)
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        lines = content.splitlines(keepends=True)
        original_lines = list(lines)
        applied = 0

        for finding in sorted(file_findings, key=lambda f: f.line_number or 0):
            fix = finding.autofix
            if fix.get("type") != "replace_text":
                continue

            target = fix.get("old", "")
            replacement = fix.get("new", "")
            count = fix.get("count", 1)
            scope = fix.get("scope", "line")

            if scope == "line":
                idx = finding.line_number - 1 if finding.line_number else None
                if idx is None or idx < 0 or idx >= len(lines):
                    continue
                updated, changed = _replace_with_count(lines[idx], target, replacement, count)
                if changed:
                    lines[idx] = updated
                    applied += 1
            elif scope == "file":
                joined = "".join(lines)
                updated, changed = _replace_with_count(joined, target, replacement, count)
                if changed:
                    lines = updated.splitlines(keepends=True)
                    applied += 1

        if applied and lines != original_lines:
            try:
                path.write_text("".join(lines), encoding="utf-8")
                summary[str(path)] = applied
            except OSError:
                continue

    return summary


def _relative_path(root: Path, file_path: str) -> Path:
    """
    Return path relative to root when possible.
    """
    try:
        return Path(file_path).resolve().relative_to(root.resolve())
    except Exception:
        try:
            return Path(file_path).relative_to(root)
        except Exception:
            return Path(file_path)


def _classify_area(path: Path) -> str:
    """
    Classify path into logical health buckets.
    """
    lowered = [p.lower() for p in path.parts]
    name = path.name.lower()

    if any("test" in part for part in lowered) or name.startswith("test_"):
        return "tests"
    if any(part in {"domain", "entities", "value_objects"} for part in lowered):
        return "domain"
    if any(part in {"application", "use_cases", "commands", "services"} for part in lowered):
        return "application"
    if any(
        part in {"infra", "infrastructure", "adapters", "adapter", "gateway"} for part in lowered
    ):
        return "infrastructure"
    if any(part in {"scripts", "tools", "cli", "bin"} for part in lowered):
        return "tooling"
    return "core"


def _format_table(
    headers: list[str], rows: list[list[Any]], align: list[str] | None = None,
) -> str:
    """
    Render a simple ASCII table.
    """
    if not rows:
        return "  (none)\n"

    align = align or ["left"] * len(headers)
    widths = [len(header) for header in headers]

    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(str(cell)))

    def format_cell(value: Any, width: int, alignment: str) -> str:
        text = str(value)
        if alignment == "right":
            return text.rjust(width)
        if alignment == "center":
            return text.center(width)
        return text.ljust(width)

    header_line = "  " + " | ".join(
        format_cell(header, widths[i], align[i]) for i, header in enumerate(headers)
    )
    separator = "  " + "-+-".join("-" * width for width in widths)
    body_lines = [
        "  " + " | ".join(format_cell(row[i], widths[i], align[i]) for i in range(len(headers)))
        for row in rows
    ]

    return "\n".join([header_line, separator, *body_lines]) + "\n"


def _bar(value: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return ""
    filled = min(width, int(round(width * (value / total))))
    return "#" * filled + "." * (width - filled)


def compute_health_metrics(
    root: Path, findings: list[ScanFinding], results: ScanResults, severity: str,
) -> dict[str, Any]:
    """
    Compute aggregate health metrics for the atlas report.
    """
    severity_counts = Counter(f.severity for f in findings)
    type_counts = Counter(f.code_type for f in findings)
    dir_counts = Counter()
    area_counts = Counter()
    file_counts = Counter()
    autofix_ready = sum(1 for f in findings if f.autofix)

    for finding in findings:
        rel_path = _relative_path(root, finding.file_path)
        top_dir = (
            rel_path.parts[0]
            if len(rel_path.parts) > 1
            else rel_path.parts[0] if rel_path.parts else "."
        )
        dir_counts[top_dir] += 1
        area_counts[_classify_area(rel_path)] += 1
        file_counts[str(rel_path)] += 1

    total_files = results.files_scanned
    total_lines = results.lines_scanned
    files_with_findings = len({f.file_path for f in findings})
    density = (sum(type_counts.values()) / total_lines) if total_lines else 0.0

    health_score = max(
        0,
        100
        - (severity_counts.get("error", 0) * 7)
        - (severity_counts.get("warning", 0) * 3)
        - int(files_with_findings * 0.5),
    )

    if health_score >= 85:
        health_label = "excellent"
    elif health_score >= 70:
        health_label = "good"
    elif health_score >= 50:
        health_label = "fair"
    else:
        health_label = "critical"

    hotspot_limit = 8

    return {
        "severity_counts": severity_counts,
        "type_counts": type_counts.most_common(10),
        "dir_counts": dir_counts.most_common(8),
        "area_counts": area_counts,
        "file_hotspots": file_counts.most_common(hotspot_limit),
        "total_files": total_files,
        "total_lines": total_lines,
        "files_with_findings": files_with_findings,
        "density": density,
        "health_score": health_score,
        "health_label": health_label,
        "autofix_ready": autofix_ready,
        "filtered_severity": severity,
    }


def render_atlas_report(
    root: Path,
    results: ScanResults,
    metrics: dict[str, Any],
    fix_summary: dict[str, int] | None = None,
    suppressed_count: int = 0,
) -> str:
    """
    Generate the ASCII atlas health report.
    """
    fix_summary = fix_summary or {}
    severity_counts = metrics["severity_counts"]
    total_findings = sum(severity_counts.values())
    lines: list[str] = []
    width = 70
    border = "=" * width

    lines.append(border)
    lines.append("ATLAS HEALTH SUMMARY".center(width))
    lines.append(border)
    lines.append(f"Root: {root}")
    lines.append(f"Health Score: {metrics['health_score']}/100 ({metrics['health_label']})")
    lines.append(f"Severity filter: >= {metrics['filtered_severity']}")
    lines.append(
        f"Files scanned: {metrics['total_files']} | Lines scanned: {metrics['total_lines']}",
    )
    lines.append(
        f"Files with findings: {metrics['files_with_findings']} | Density: {metrics['density']:.4f} issues/line",
    )
    lines.append("")

    lines.append("Severity Distribution")
    severity_rows = []
    for level in ["error", "warning", "info"]:
        count = severity_counts.get(level, 0)
        percent = (count / total_findings * 100) if total_findings else 0
        severity_rows.append(
            [level.upper(), str(count), f"{percent:5.1f}%", _bar(count, total_findings)],
        )
    lines.append(
        _format_table(
            ["Severity", "Count", "%", "Activity"],
            severity_rows,
            ["left", "right", "right", "left"],
        ).rstrip(),
    )
    lines.append("")

    lines.append("Top Finding Types")
    type_rows = [[code_type, count] for code_type, count in metrics["type_counts"]]
    lines.append(_format_table(["Type", "Count"], type_rows, ["left", "right"]).rstrip())
    lines.append("")

    lines.append("Domain Breakdown")
    area_total = sum(metrics["area_counts"].values())
    area_rows = []
    for area in ["domain", "application", "infrastructure", "tooling", "tests", "core"]:
        count = metrics["area_counts"].get(area, 0)
        percent = (count / area_total * 100) if area_total else 0
        area_rows.append([area, count, f"{percent:5.1f}%", _bar(count, area_total)])
    lines.append(
        _format_table(
            ["Area", "Count", "%", "Activity"], area_rows, ["left", "right", "right", "left"],
        ).rstrip(),
    )
    lines.append("")

    lines.append("Top Directories by Findings")
    dir_rows = [[directory, count] for directory, count in metrics["dir_counts"]]
    lines.append(_format_table(["Directory", "Count"], dir_rows, ["left", "right"]).rstrip())
    lines.append("")

    lines.append("Hotspot Files")
    hotspot_rows = [[path, count] for path, count in metrics["file_hotspots"]]
    lines.append(_format_table(["File", "Findings"], hotspot_rows, ["left", "right"]).rstrip())
    lines.append("")

    if fix_summary or metrics["autofix_ready"]:
        lines.append("Autofix Insights")
        lines.append(f"  Findings with autofix suggestions: {metrics['autofix_ready']}")
        if fix_summary:
            for file_path, count in sorted(fix_summary.items()):
                lines.append(f"  Applied {count} autofix change(s) → {file_path}")
        else:
            lines.append("  (dry run; use --apply-fixes to auto-apply supported remediations)")
        lines.append("")

    if suppressed_count:
        lines.append(f"Suppressed findings below current severity threshold: {suppressed_count}")

    lines.append(border)
    return "\n".join(lines) + "\n"


def main():
    """
    CLI entry point.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Pheno-SDK Legacy Code Scanner")
    parser.add_argument("path", nargs="?", default=".", help="Path to scan")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument(
        "--severity",
        choices=["error", "warning", "info"],
        default="warning",
        help="Minimum severity to report",
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[], help="Additional directories to exclude",
    )
    parser.add_argument(
        "--include", nargs="*", default=[], help="Specific file patterns to include",
    )
    parser.add_argument(
        "--apply-fixes", action="store_true", help="Automatically apply safe autofix replacements",
    )

    args = parser.parse_args()

    scanner = LegacyCodeScanner(
        Path(args.path), config={"excluded_dirs": args.exclude, "severity_threshold": args.severity},
    )

    results = scanner.scan()

    fix_summary: dict[str, int] = {}
    if args.apply_fixes:
        fix_summary = apply_autofixes(results.findings)

    # Filter by severity
    severity_levels = {"error": 0, "warning": 1, "info": 2}
    min_level = severity_levels[args.severity]

    filtered_findings = [f for f in results.findings if severity_levels[f.severity] <= min_level]

    # Output results
    if args.format == "json":
        output = {
            "summary": results.summary(),
            "findings": [f.to_dict() for f in filtered_findings],
        }
        if fix_summary:
            output["autofix_summary"] = fix_summary
        print(json.dumps(output, indent=2))
    else:
        # Text output
        summary = results.summary()
        print("\nLegacy Code Scan Results")
        print("=" * 40)
        print(f"Files scanned: {summary['files_scanned']}")
        print(f"Lines scanned: {summary['lines_scanned']}")
        print(f"Total findings: {summary['total_findings']}")
        print()

        if args.apply_fixes:
            if fix_summary:
                print("Autofixes applied:")
                for file_path, count in sorted(fix_summary.items()):
                    print(f"  {file_path}: {count} change(s)")
            else:
                print("Autofixes applied: none")
            print()

        severity_colors = {"error": "\033[91m", "warning": "\033[93m", "info": "\033[94m"}

        if filtered_findings:
            print("Findings:")
            print("-" * 40)

            # Group by file
            findings_by_file = defaultdict(list)
            for finding in filtered_findings:
                findings_by_file[finding.file_path].append(finding)

            for file_path, file_findings in sorted(findings_by_file.items()):
                print(f"\n{file_path}:")
                for finding in sorted(file_findings, key=lambda f: f.line_number):
                    color = severity_colors.get(finding.severity, "\033[0m")
                    reset = "\033[0m"
                    print(f"  {color}{finding.severity.upper()}{reset}: Line {finding.line_number}")
                    print(f"    {finding.message}")
                    if finding.context:
                        print(f"    Context: {finding.context}")
                    if finding.suggestion:
                        print(f"    Suggestion: {finding.suggestion}")

        # Exit code based on findings
        error_count = len([f for f in filtered_findings if f.severity == "error"])
        sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
