"""Code Analysis for Hexagonal Architecture Refactoring.

This module provides tools for analyzing code structure, detecting violations, and
identifying refactoring opportunities in hexagonal architecture projects.
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CodeMetrics:
    """
    Metrics for code analysis.
    """

    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    class_count: int
    function_count: int
    import_count: int
    dependency_depth: int
    violations: list[str] = field(default_factory=list)

    @property
    def is_large_file(self) -> bool:
        """
        Check if file exceeds size threshold (>500 LOC).
        """
        return self.lines_of_code > 500

    @property
    def is_complex(self) -> bool:
        """
        Check if file has high complexity (>10).
        """
        return self.cyclomatic_complexity > 10

    @property
    def needs_refactoring(self) -> bool:
        """
        Check if file needs refactoring.
        """
        return (
            self.is_large_file
            or self.is_complex
            or len(self.violations) > 0
            or self.cognitive_complexity > 15
        )


@dataclass
class ArchitecturalViolation:
    """
    Represents an architectural violation.
    """

    file_path: str
    line_number: int
    violation_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    suggested_fix: str | None = None

    def __str__(self) -> str:
        """
        String representation of violation.
        """
        return (
            f"[{self.severity.upper()}] {self.file_path}:{self.line_number} - "
            f"{self.violation_type}: {self.message}"
        )


@dataclass
class AnalysisResult:
    """
    Result of code analysis.
    """

    file_path: str
    metrics: CodeMetrics
    violations: list[ArchitecturalViolation]
    refactoring_suggestions: list[str]

    @property
    def severity_score(self) -> int:
        """
        Calculate severity score based on violations.
        """
        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        return sum(severity_weights.get(v.severity, 0) for v in self.violations)

    @property
    def priority(self) -> str:
        """
        Get refactoring priority based on severity.
        """
        if self.severity_score >= 20:
            return "critical"
        if self.severity_score >= 10:
            return "high"
        if self.severity_score >= 5:
            return "medium"
        return "low"


class ComplexityAnalyzer(ast.NodeVisitor):
    """
    AST visitor to calculate cyclomatic and cognitive complexity.
    """

    def __init__(self) -> None:
        """
        Initialize complexity analyzer.
        """
        self.cyclomatic_complexity = 1  # Base complexity
        self.cognitive_complexity = 0
        self.nesting_level = 0
        self.function_complexities: dict[str, int] = {}
        self.current_function: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visit function definition.
        """
        previous_function = self.current_function
        self.current_function = node.name
        self.function_complexities[node.name] = 1

        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

        self.current_function = previous_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Visit async function definition.
        """
        self.visit_FunctionDef(node)  # type: ignore

    def visit_If(self, node: ast.If) -> None:
        """
        Visit if statement.
        """
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += self.nesting_level + 1

        if self.current_function:
            self.function_complexities[self.current_function] += 1

        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node: ast.For) -> None:
        """
        Visit for loop.
        """
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += self.nesting_level + 1

        if self.current_function:
            self.function_complexities[self.current_function] += 1

        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node: ast.While) -> None:
        """
        Visit while loop.
        """
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += self.nesting_level + 1

        if self.current_function:
            self.function_complexities[self.current_function] += 1

        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """
        Visit except handler.
        """
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += self.nesting_level + 1

        if self.current_function:
            self.function_complexities[self.current_function] += 1

        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """
        Visit boolean operation.
        """
        # Each additional condition increases complexity
        self.cyclomatic_complexity += len(node.values) - 1
        self.cognitive_complexity += len(node.values) - 1

        if self.current_function:
            self.function_complexities[self.current_function] += len(node.values) - 1

        self.generic_visit(node)


class CodeAnalyzer:
    """
    Analyzer for detecting large files, complexity, and violations.
    """

    # Hexagonal architecture layer patterns
    LAYER_PATTERNS = {
        "domain": ["domain", "entities", "models"],
        "application": ["application", "services", "use_cases", "usecases"],
        "adapters": ["adapters", "controllers", "repositories", "presenters"],
        "infrastructure": ["infrastructure", "infra", "config", "database"],
        "ports": ["ports", "interfaces"],
    }

    # Dependency rules (allowed dependencies)
    DEPENDENCY_RULES = {
        "domain": set(),  # Domain should have no dependencies
        "application": {"domain", "ports"},
        "adapters": {"domain", "ports", "application"},
        "infrastructure": {"domain", "ports", "adapters"},
        "ports": {"domain"},
    }

    def __init__(
        self,
        size_threshold: int = 500,
        complexity_threshold: int = 10,
        cognitive_threshold: int = 15,
    ) -> None:
        """Initialize code analyzer.

        Args:
            size_threshold: Maximum lines of code before file is considered large
            complexity_threshold: Maximum cyclomatic complexity
            cognitive_threshold: Maximum cognitive complexity
        """
        self.size_threshold = size_threshold
        self.complexity_threshold = complexity_threshold
        self.cognitive_threshold = cognitive_threshold

    async def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a single file for metrics and violations.

        Args:
            file_path: Path to file to analyze

        Returns:
            AnalysisResult with metrics and violations
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            metrics = self._calculate_metrics(content, tree)
            violations = self._detect_violations(file_path, tree, content)
            suggestions = self._generate_suggestions(metrics, violations)

            return AnalysisResult(
                file_path=str(file_path),
                metrics=metrics,
                violations=violations,
                refactoring_suggestions=suggestions,
            )

        except Exception as e:
            logger.exception(f"Error analyzing {file_path}: {e}")
            raise

    def _calculate_metrics(self, content: str, tree: ast.AST) -> CodeMetrics:
        """
        Calculate code metrics.
        """
        lines = content.splitlines()
        loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])

        # Calculate complexity
        complexity_analyzer = ComplexityAnalyzer()
        complexity_analyzer.visit(tree)

        # Count classes and functions
        class_count = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
        function_count = sum(
            1 for _ in ast.walk(tree) if isinstance(_, (ast.FunctionDef, ast.AsyncFunctionDef))
        )

        # Count imports
        import_count = sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.Import, ast.ImportFrom)))

        # Calculate dependency depth (max nesting of imports)
        dependency_depth = self._calculate_dependency_depth(tree)

        return CodeMetrics(
            lines_of_code=loc,
            cyclomatic_complexity=complexity_analyzer.cyclomatic_complexity,
            cognitive_complexity=complexity_analyzer.cognitive_complexity,
            class_count=class_count,
            function_count=function_count,
            import_count=import_count,
            dependency_depth=dependency_depth,
        )

    def _calculate_dependency_depth(self, tree: ast.AST) -> int:
        """
        Calculate maximum dependency depth.
        """
        max_depth = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                depth = node.module.count(".") + 1
                max_depth = max(max_depth, depth)
        return max_depth

    def _detect_violations(
        self, file_path: Path, tree: ast.AST, content: str,
    ) -> list[ArchitecturalViolation]:
        """
        Detect architectural violations.
        """
        violations: list[ArchitecturalViolation] = []

        # Detect layer violations
        layer = self._identify_layer(file_path)
        if layer:
            layer_violations = self._check_layer_dependencies(file_path, tree, layer)
            violations.extend(layer_violations)

        # Detect god classes
        god_class_violations = self._detect_god_classes(tree, file_path)
        violations.extend(god_class_violations)

        # Detect circular dependencies (basic check)
        circular_violations = self._detect_circular_dependencies(tree, file_path)
        violations.extend(circular_violations)

        # Detect missing abstractions
        abstraction_violations = self._detect_missing_abstractions(tree, file_path)
        violations.extend(abstraction_violations)

        return violations

    def _identify_layer(self, file_path: Path) -> str | None:
        """
        Identify which hexagonal layer a file belongs to.
        """
        path_str = str(file_path).lower()

        for layer, patterns in self.LAYER_PATTERNS.items():
            if any(pattern in path_str for pattern in patterns):
                return layer

        return None

    def _check_layer_dependencies(
        self, file_path: Path, tree: ast.AST, layer: str,
    ) -> list[ArchitecturalViolation]:
        """
        Check if layer dependencies follow hexagonal architecture rules.
        """
        violations: list[ArchitecturalViolation] = []
        allowed_deps = self.DEPENDENCY_RULES.get(layer, set())

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported_layer = None
                for dep_layer, patterns in self.LAYER_PATTERNS.items():
                    if any(pattern in node.module.lower() for pattern in patterns):
                        imported_layer = dep_layer
                        break

                if (
                    imported_layer
                    and imported_layer not in allowed_deps
                    and imported_layer != layer
                ):
                    violations.append(
                        ArchitecturalViolation(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            violation_type="layer_dependency",
                            severity="high",
                            message=f"{layer} layer should not depend on {imported_layer} layer",
                            suggested_fix="Use dependency inversion or move code to appropriate layer",
                        ),
                    )

        return violations

    def _detect_god_classes(self, tree: ast.AST, file_path: Path) -> list[ArchitecturalViolation]:
        """
        Detect classes with too many responsibilities (god classes).
        """
        violations: list[ArchitecturalViolation] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(
                    1 for _ in node.body if isinstance(_, (ast.FunctionDef, ast.AsyncFunctionDef))
                )

                if method_count > 15:
                    violations.append(
                        ArchitecturalViolation(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            violation_type="god_class",
                            severity="high",
                            message=f"Class '{node.name}' has {method_count} methods (>15)",
                            suggested_fix="Split class into smaller, single-responsibility classes",
                        ),
                    )

        return violations

    def _detect_circular_dependencies(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Detect potential circular dependencies.
        """
        violations: list[ArchitecturalViolation] = []
        # This is a simplified check - would need full project context for complete detection
        # For now, we check for relative imports that might indicate circular deps

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                violations.append(
                    ArchitecturalViolation(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        violation_type="potential_circular_dependency",
                        severity="medium",
                        message="Relative import detected - potential circular dependency risk",
                        suggested_fix="Use absolute imports and ensure proper layer separation",
                    ),
                )

        return violations

    def _detect_missing_abstractions(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Detect missing abstractions (no interfaces/protocols).
        """
        violations: list[ArchitecturalViolation] = []

        # Check if adapters layer has concrete implementations without abstractions
        if "adapter" in str(file_path).lower():
            has_protocol = False
            has_abc = False

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "typing" in node.module:
                        if any(alias.name == "Protocol" for alias in (node.names or [])):
                            has_protocol = True
                    if node.module and "abc" in node.module:
                        has_abc = True

            if not (has_protocol or has_abc):
                violations.append(
                    ArchitecturalViolation(
                        file_path=str(file_path),
                        line_number=1,
                        violation_type="missing_abstraction",
                        severity="medium",
                        message="Adapter implementation without Protocol or ABC",
                        suggested_fix="Define port interface using Protocol or ABC",
                    ),
                )

        return violations

    def _generate_suggestions(
        self, metrics: CodeMetrics, violations: list[ArchitecturalViolation],
    ) -> list[str]:
        """
        Generate refactoring suggestions based on metrics and violations.
        """
        suggestions: list[str] = []

        if metrics.is_large_file:
            suggestions.append(
                f"File has {metrics.lines_of_code} LOC (>{self.size_threshold}). "
                "Consider extracting classes or concerns into separate files.",
            )

        if metrics.cyclomatic_complexity > self.complexity_threshold:
            suggestions.append(
                f"Cyclomatic complexity is {metrics.cyclomatic_complexity} "
                f"(>{self.complexity_threshold}). Consider simplifying logic.",
            )

        if metrics.cognitive_complexity > self.cognitive_threshold:
            suggestions.append(
                f"Cognitive complexity is {metrics.cognitive_complexity} "
                f"(>{self.cognitive_threshold}). Consider extracting methods.",
            )

        if metrics.class_count > 5:
            suggestions.append(
                f"File contains {metrics.class_count} classes. "
                "Consider one class per file for better organization.",
            )

        violation_types = {v.violation_type for v in violations}
        if "layer_dependency" in violation_types:
            suggestions.append(
                "Layer dependency violations detected. Review hexagonal architecture boundaries.",
            )

        if "god_class" in violation_types:
            suggestions.append("God class detected. Apply Single Responsibility Principle.")

        return suggestions


async def detect_large_files(
    directory: Path, threshold: int = 500, exclude_patterns: list[str] | None = None,
) -> list[tuple[Path, int]]:
    """Detect files exceeding size threshold.

    Args:
        directory: Directory to scan
        threshold: Maximum lines of code
        exclude_patterns: Patterns to exclude from scan

    Returns:
        List of (file_path, line_count) tuples
    """
    large_files: list[tuple[Path, int]] = []
    exclude_patterns = exclude_patterns or ["test_", "__pycache__", ".git"]

    for py_file in directory.rglob("*.py"):
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])

            if loc > threshold:
                large_files.append((py_file, loc))

        except Exception as e:
            logger.warning(f"Error reading {py_file}: {e}")

    return sorted(large_files, key=lambda x: x[1], reverse=True)


async def analyze_complexity(file_path: Path) -> dict[str, Any]:
    """Analyze cyclomatic and cognitive complexity of a file.

    Args:
        file_path: Path to Python file

    Returns:
        Dictionary with complexity metrics
    """
    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content, filename=str(file_path))

    analyzer = ComplexityAnalyzer()
    analyzer.visit(tree)

    return {
        "file": str(file_path),
        "cyclomatic_complexity": analyzer.cyclomatic_complexity,
        "cognitive_complexity": analyzer.cognitive_complexity,
        "function_complexities": analyzer.function_complexities,
    }


async def detect_violations(
    directory: Path, exclude_patterns: list[str] | None = None,
) -> list[ArchitecturalViolation]:
    """Detect architectural violations in directory.

    Args:
        directory: Directory to scan
        exclude_patterns: Patterns to exclude from scan

    Returns:
        List of architectural violations
    """
    analyzer = CodeAnalyzer()
    all_violations: list[ArchitecturalViolation] = []
    exclude_patterns = exclude_patterns or ["test_", "__pycache__", ".git"]

    for py_file in directory.rglob("*.py"):
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        try:
            result = await analyzer.analyze_file(py_file)
            all_violations.extend(result.violations)

        except Exception as e:
            logger.warning(f"Error analyzing {py_file}: {e}")

    return sorted(all_violations, key=lambda v: v.severity, reverse=True)
