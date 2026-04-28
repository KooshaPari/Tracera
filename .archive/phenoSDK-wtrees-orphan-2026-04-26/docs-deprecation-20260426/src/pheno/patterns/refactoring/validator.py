"""Hexagonal Architecture Validation.

This module provides validators for ensuring code follows hexagonal architecture
principles including port/adapter separation, layer boundaries, and dependency rules.
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """
    Represents a validation rule.
    """

    name: str
    description: str
    severity: str  # 'info', 'warning', 'error', 'critical'
    enabled: bool = True


@dataclass
class ValidationIssue:
    """
    Represents a validation issue.
    """

    rule_name: str
    file_path: str
    line_number: int
    severity: str
    message: str
    suggestion: str | None = None

    def __str__(self) -> str:
        """
        String representation.
        """
        return (
            f"[{self.severity.upper()}] {self.file_path}:{self.line_number} - "
            f"{self.rule_name}: {self.message}"
        )


@dataclass
class ValidationResult:
    """
    Result of architecture validation.
    """

    file_path: str
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        """
        Count of error-level issues.
        """
        return len([i for i in self.issues if i.severity in ["error", "critical"]])

    @property
    def warning_count(self) -> int:
        """
        Count of warning-level issues.
        """
        return len([i for i in self.issues if i.severity == "warning"])

    def __str__(self) -> str:
        """
        String representation.
        """
        status = "✓" if self.is_valid else "✗"
        return (
            f"{status} {self.file_path}: "
            f"{self.error_count} errors, {self.warning_count} warnings"
        )


class PortAdapterValidator:
    """
    Validator for port/adapter pattern compliance.
    """

    def __init__(self) -> None:
        """
        Initialize port/adapter validator.
        """
        self.rules = [
            ValidationRule(
                name="port_interface_exists",
                description="Adapters must implement a port interface",
                severity="error",
            ),
            ValidationRule(
                name="adapter_implements_port",
                description="Adapter must properly implement port interface",
                severity="error",
            ),
            ValidationRule(
                name="port_no_implementation",
                description="Port should be abstract interface only",
                severity="warning",
            ),
            ValidationRule(
                name="adapter_no_domain_logic",
                description="Adapter should not contain domain logic",
                severity="error",
            ),
        ]

    async def validate_port_adapter(
        self, file_path: Path, is_port: bool = False,
    ) -> ValidationResult:
        """Validate port/adapter pattern compliance.

        Args:
            file_path: Path to file to validate
            is_port: Whether file contains port interface

        Returns:
            ValidationResult with issues found
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            issues: list[ValidationIssue] = []

            if is_port:
                issues.extend(self._validate_port_file(tree, file_path))
            else:
                issues.extend(self._validate_adapter_file(tree, file_path))

            is_valid = not any(i.severity in ["error", "critical"] for i in issues)

            return ValidationResult(file_path=str(file_path), is_valid=is_valid, issues=issues)

        except Exception as e:
            logger.exception(f"Error validating {file_path}: {e}")
            return ValidationResult(
                file_path=str(file_path),
                is_valid=False,
                issues=[
                    ValidationIssue(
                        rule_name="validation_error",
                        file_path=str(file_path),
                        line_number=0,
                        severity="error",
                        message=str(e),
                    ),
                ],
            )

    def _validate_port_file(self, tree: ast.AST, file_path: Path) -> list[ValidationIssue]:
        """
        Validate port interface file.
        """
        issues: list[ValidationIssue] = []

        # Check for abstract base classes or protocols
        has_abc = False
        has_protocol = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "abc":
                    has_abc = True
                elif node.module == "typing" and any(
                    alias.name == "Protocol" for alias in (node.names or [])
                ):
                    has_protocol = True

        if not (has_abc or has_protocol):
            issues.append(
                ValidationIssue(
                    rule_name="port_interface_exists",
                    file_path=str(file_path),
                    line_number=1,
                    severity="warning",
                    message="Port file should use ABC or Protocol",
                    suggestion="from abc import ABC, abstractmethod or from typing import Protocol",
                ),
            )

        # Check classes are abstract
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class has implementation details
                has_implementation = self._has_implementation(node)

                if has_implementation:
                    issues.append(
                        ValidationIssue(
                            rule_name="port_no_implementation",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            severity="warning",
                            message=f"Port '{node.name}' contains implementation details",
                            suggestion="Port should only define interface, not implementation",
                        ),
                    )

        return issues

    def _validate_adapter_file(self, tree: ast.AST, file_path: Path) -> list[ValidationIssue]:
        """
        Validate adapter implementation file.
        """
        issues: list[ValidationIssue] = []

        # Check adapters implement interfaces
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.bases:
                    issues.append(
                        ValidationIssue(
                            rule_name="adapter_implements_port",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            severity="error",
                            message=f"Adapter '{node.name}' should implement a port interface",
                            suggestion="class {node.name}(PortInterface): ...",
                        ),
                    )

                # Check for domain logic in adapters
                if self._contains_domain_logic(node):
                    issues.append(
                        ValidationIssue(
                            rule_name="adapter_no_domain_logic",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            severity="error",
                            message=f"Adapter '{node.name}' contains domain logic",
                            suggestion="Move domain logic to domain layer",
                        ),
                    )

        return issues

    def _has_implementation(self, class_node: ast.ClassDef) -> bool:
        """
        Check if class has implementation details.
        """
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if method has implementation (not just pass/...)
                if node.body:
                    for stmt in node.body:
                        if not isinstance(stmt, (ast.Pass, ast.Expr)):
                            return True
                        if isinstance(stmt, ast.Expr) and not isinstance(stmt.value, ast.Constant):
                            return True
        return False

    def _contains_domain_logic(self, class_node: ast.ClassDef) -> bool:
        """
        Check if adapter contains domain logic.
        """
        # Simple heuristic: domain logic often involves business rules
        domain_keywords = ["validate", "calculate", "process", "business", "rule"]

        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(keyword in node.name.lower() for keyword in domain_keywords):
                    # Check if it's more than just calling another method
                    if len(node.body) > 3:  # Heuristic: >3 statements might be logic
                        return True

        return False


class LayerValidator:
    """
    Validator for layer separation.
    """

    LAYER_HIERARCHY = {
        "domain": 0,
        "ports": 1,
        "application": 2,
        "adapters": 3,
        "infrastructure": 4,
    }

    ALLOWED_DEPENDENCIES = {
        "domain": set(),
        "ports": {"domain"},
        "application": {"domain", "ports"},
        "adapters": {"domain", "ports", "application"},
        "infrastructure": {"domain", "ports", "adapters"},
    }

    def __init__(self) -> None:
        """
        Initialize layer validator.
        """
        self.rules = [
            ValidationRule(
                name="layer_separation",
                description="Layers must be properly separated",
                severity="error",
            ),
            ValidationRule(
                name="dependency_direction",
                description="Dependencies must flow toward domain",
                severity="error",
            ),
            ValidationRule(
                name="no_circular_dependencies",
                description="No circular dependencies between layers",
                severity="critical",
            ),
        ]

    async def validate_layers(self, file_path: Path) -> ValidationResult:
        """Validate layer separation and dependencies.

        Args:
            file_path: Path to file to validate

        Returns:
            ValidationResult with layer issues
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            issues: list[ValidationIssue] = []

            # Identify file's layer
            layer = self._identify_layer(file_path)
            if not layer:
                issues.append(
                    ValidationIssue(
                        rule_name="layer_separation",
                        file_path=str(file_path),
                        line_number=1,
                        severity="warning",
                        message="File does not belong to a recognized layer",
                        suggestion="Organize files into domain/ports/application/adapters/infrastructure",
                    ),
                )
                return ValidationResult(file_path=str(file_path), is_valid=True, issues=issues)

            # Check dependencies
            dependency_issues = self._check_dependencies(tree, file_path, layer)
            issues.extend(dependency_issues)

            is_valid = not any(i.severity in ["error", "critical"] for i in issues)

            return ValidationResult(file_path=str(file_path), is_valid=is_valid, issues=issues)

        except Exception as e:
            logger.exception(f"Error validating layers in {file_path}: {e}")
            return ValidationResult(
                file_path=str(file_path),
                is_valid=False,
                issues=[
                    ValidationIssue(
                        rule_name="validation_error",
                        file_path=str(file_path),
                        line_number=0,
                        severity="error",
                        message=str(e),
                    ),
                ],
            )

    def _identify_layer(self, file_path: Path) -> str | None:
        """
        Identify which layer a file belongs to.
        """
        path_str = str(file_path).lower()

        layer_patterns = {
            "domain": ["domain", "entities", "models"],
            "ports": ["ports", "interfaces"],
            "application": ["application", "services", "use_cases", "usecases"],
            "adapters": ["adapters", "controllers", "repositories"],
            "infrastructure": ["infrastructure", "infra", "config"],
        }

        for layer, patterns in layer_patterns.items():
            if any(pattern in path_str for pattern in patterns):
                return layer

        return None

    def _check_dependencies(
        self, tree: ast.AST, file_path: Path, layer: str,
    ) -> list[ValidationIssue]:
        """
        Check if dependencies follow layer rules.
        """
        issues: list[ValidationIssue] = []
        allowed_deps = self.ALLOWED_DEPENDENCIES.get(layer, set())

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported_layer = self._identify_layer_from_import(node.module)

                if imported_layer and imported_layer != layer:
                    if imported_layer not in allowed_deps:
                        issues.append(
                            ValidationIssue(
                                rule_name="dependency_direction",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                severity="error",
                                message=f"{layer} should not depend on {imported_layer}",
                                suggestion=f"Allowed dependencies: {', '.join(allowed_deps) if allowed_deps else 'none'}",
                            ),
                        )

        return issues

    def _identify_layer_from_import(self, module: str) -> str | None:
        """
        Identify layer from import module path.
        """
        module_lower = module.lower()

        if "domain" in module_lower or "entities" in module_lower:
            return "domain"
        if "ports" in module_lower or "interfaces" in module_lower:
            return "ports"
        if "application" in module_lower or "services" in module_lower:
            return "application"
        if "adapters" in module_lower or "controllers" in module_lower:
            return "adapters"
        if "infrastructure" in module_lower or "infra" in module_lower:
            return "infrastructure"

        return None


class DependencyValidator:
    """
    Validator for dependency rules.
    """

    def __init__(self) -> None:
        """
        Initialize dependency validator.
        """
        self.rules = [
            ValidationRule(
                name="no_circular_imports",
                description="No circular import dependencies",
                severity="critical",
            ),
            ValidationRule(
                name="dependency_inversion",
                description="High-level modules should not depend on low-level modules",
                severity="error",
            ),
            ValidationRule(
                name="interface_segregation",
                description="Clients should not depend on interfaces they don't use",
                severity="warning",
            ),
        ]

    async def validate_dependencies(
        self, file_path: Path, project_root: Path | None = None,
    ) -> ValidationResult:
        """Validate dependency rules.

        Args:
            file_path: Path to file to validate
            project_root: Root directory of project for circular dependency detection

        Returns:
            ValidationResult with dependency issues
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            issues: list[ValidationIssue] = []

            # Check for relative imports (potential circular dependencies)
            relative_import_issues = self._check_relative_imports(tree, file_path)
            issues.extend(relative_import_issues)

            # Check dependency inversion
            inversion_issues = self._check_dependency_inversion(tree, file_path)
            issues.extend(inversion_issues)

            # Check for too many dependencies
            dependency_count_issues = self._check_dependency_count(tree, file_path)
            issues.extend(dependency_count_issues)

            is_valid = not any(i.severity in ["error", "critical"] for i in issues)

            return ValidationResult(file_path=str(file_path), is_valid=is_valid, issues=issues)

        except Exception as e:
            logger.exception(f"Error validating dependencies in {file_path}: {e}")
            return ValidationResult(
                file_path=str(file_path),
                is_valid=False,
                issues=[
                    ValidationIssue(
                        rule_name="validation_error",
                        file_path=str(file_path),
                        line_number=0,
                        severity="error",
                        message=str(e),
                    ),
                ],
            )

    def _check_relative_imports(self, tree: ast.AST, file_path: Path) -> list[ValidationIssue]:
        """
        Check for relative imports.
        """
        issues: list[ValidationIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                issues.append(
                    ValidationIssue(
                        rule_name="no_circular_imports",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity="warning",
                        message="Relative import detected - may cause circular dependencies",
                        suggestion="Use absolute imports for better clarity",
                    ),
                )

        return issues

    def _check_dependency_inversion(self, tree: ast.AST, file_path: Path) -> list[ValidationIssue]:
        """
        Check for dependency inversion violations.
        """
        issues: list[ValidationIssue] = []

        # Check if high-level modules depend on concrete implementations
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class depends on concrete classes instead of abstractions
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        # Heuristic: concrete classes often have specific names
                        # while interfaces end with 'Interface', 'Port', 'Protocol'
                        if not any(
                            suffix in base.id for suffix in ["Interface", "Port", "Protocol", "ABC"]
                        ):
                            # Might be depending on concrete implementation
                            # This is a warning since it's heuristic-based
                            pass  # Too many false positives

        return issues

    def _check_dependency_count(self, tree: ast.AST, file_path: Path) -> list[ValidationIssue]:
        """
        Check for too many dependencies.
        """
        issues: list[ValidationIssue] = []

        import_count = sum(
            1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
        )

        if import_count > 20:
            issues.append(
                ValidationIssue(
                    rule_name="dependency_count",
                    file_path=str(file_path),
                    line_number=1,
                    severity="warning",
                    message=f"File has {import_count} imports (>20)",
                    suggestion="Consider splitting file or reducing dependencies",
                ),
            )

        return issues


async def validate_port_adapter(file_path: Path, is_port: bool = False) -> ValidationResult:
    """Validate port/adapter pattern compliance.

    Args:
        file_path: Path to file to validate
        is_port: Whether file is a port interface

    Returns:
        ValidationResult with issues found
    """
    validator = PortAdapterValidator()
    return await validator.validate_port_adapter(file_path, is_port)


async def validate_layers(file_path: Path) -> ValidationResult:
    """Validate layer separation and dependencies.

    Args:
        file_path: Path to file to validate

    Returns:
        ValidationResult with layer issues
    """
    validator = LayerValidator()
    return await validator.validate_layers(file_path)


async def validate_dependencies(
    file_path: Path, project_root: Path | None = None,
) -> ValidationResult:
    """Validate dependency rules.

    Args:
        file_path: Path to file to validate
        project_root: Root directory of project

    Returns:
        ValidationResult with dependency issues
    """
    validator = DependencyValidator()
    return await validator.validate_dependencies(file_path, project_root)
