#!/usr/bin/env python3
"""
Architectural Pattern Validator Validates adherence to architectural patterns like
Hexagonal Architecture, Clean Architecture, SOLID principles, and other design patterns.
"""
import argparse
import ast
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ArchitecturalViolation:
    """
    Represents an architectural pattern violation.
    """

    pattern: str
    violation_type: str
    severity: str
    file: str
    line: int
    column: int
    message: str
    suggestion: str
    confidence: float


class ArchitecturalPatternValidator:
    """
    Validates architectural patterns and design principles.
    """

    def __init__(self):
        self.violations = []
        self.file_stats = {}

        # Architectural pattern definitions
        self.patterns = {
            "hexagonal": {
                "ports": ["interface", "port", "contract", "service"],
                "adapters": ["adapter", "implementation", "infrastructure"],
                "domain": ["domain", "model", "entity", "value", "service"],
            },
            "clean_architecture": {
                "entities": ["entity", "model", "domain"],
                "use_cases": ["use_case", "interactor", "service"],
                "interface_adapters": ["controller", "presenter", "gateway"],
                "frameworks": ["framework", "infrastructure", "external"],
            },
            "solid": {
                "srp": "Single Responsibility Principle",
                "ocp": "Open/Closed Principle",
                "lsp": "Liskov Substitution Principle",
                "isp": "Interface Segregation Principle",
                "dip": "Dependency Inversion Principle",
            },
        }

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze a single file for architectural violations.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            file_violations = []

            # Analyze different architectural patterns
            file_violations.extend(self._validate_hexagonal_architecture(tree, file_path))
            file_violations.extend(self._validate_clean_architecture(tree, file_path))
            file_violations.extend(self._validate_solid_principles(tree, file_path))
            file_violations.extend(self._validate_dependency_injection(tree, file_path))
            file_violations.extend(self._validate_interface_segregation(tree, file_path))
            file_violations.extend(self._validate_single_responsibility(tree, file_path))
            file_violations.extend(self._validate_open_closed_principle(tree, file_path))
            file_violations.extend(self._validate_liskov_substitution(tree, file_path))
            file_violations.extend(self._validate_dependency_inversion(tree, file_path))
            file_violations.extend(self._validate_factory_pattern(tree, file_path))
            file_violations.extend(self._validate_strategy_pattern(tree, file_path))
            file_violations.extend(self._validate_observer_pattern(tree, file_path))
            file_violations.extend(self._validate_command_pattern(tree, file_path))
            file_violations.extend(self._validate_repository_pattern(tree, file_path))
            file_violations.extend(self._validate_unit_of_work(tree, file_path))
            file_violations.extend(self._validate_cqrs_pattern(tree, file_path))
            file_violations.extend(self._validate_event_sourcing(tree, file_path))
            file_violations.extend(self._validate_mvc_pattern(tree, file_path))
            file_violations.extend(self._validate_mvp_pattern(tree, file_path))
            file_violations.extend(self._validate_mvvm_pattern(tree, file_path))
            file_violations.extend(self._validate_layered_architecture(tree, file_path))
            file_violations.extend(self._validate_microservices_patterns(tree, file_path))
            file_violations.extend(self._validate_api_gateway_pattern(tree, file_path))
            file_violations.extend(self._validate_circuit_breaker_pattern(tree, file_path))
            file_violations.extend(self._validate_retry_pattern(tree, file_path))
            file_violations.extend(self._validate_bulkhead_pattern(tree, file_path))
            file_violations.extend(self._validate_saga_pattern(tree, file_path))
            file_violations.extend(self._validate_event_driven_architecture(tree, file_path))
            file_violations.extend(self._validate_cqrs_pattern(tree, file_path))
            file_violations.extend(self._validate_domain_driven_design(tree, file_path))

            self.violations.extend(file_violations)

            return {
                "file": str(file_path),
                "violations": file_violations,
                "violation_count": len(file_violations),
                "severity_counts": self._count_by_severity(file_violations),
            }

        except Exception as e:
            return {"file": str(file_path), "error": str(e), "violations": [], "violation_count": 0}

    def _validate_hexagonal_architecture(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Hexagonal Architecture patterns.
        """
        violations = []

        # Check for proper separation of ports and adapters
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for class_node in classes:
            class_name = class_node.name.lower()

            # Check if class is in the right layer
            if any(keyword in class_name for keyword in self.patterns["hexagonal"]["ports"]):
                # Port classes should only contain abstract methods
                methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
                concrete_methods = [
                    m for m in methods if m.body and not self._is_abstract_method(m)
                ]

                if concrete_methods:
                    violations.append(
                        ArchitecturalViolation(
                            pattern="hexagonal",
                            violation_type="port_implementation",
                            severity="high",
                            file=str(file_path),
                            line=class_node.lineno,
                            column=class_node.col_offset,
                            message=f"Port class '{class_node.name}' contains concrete implementations",
                            suggestion="Ports should only contain abstract method signatures",
                            confidence=0.8,
                        ),
                    )

            elif any(keyword in class_name for keyword in self.patterns["hexagonal"]["adapters"]):
                # Adapter classes should implement ports
                if not class_node.bases:
                    violations.append(
                        ArchitecturalViolation(
                            pattern="hexagonal",
                            violation_type="adapter_without_port",
                            severity="medium",
                            file=str(file_path),
                            line=class_node.lineno,
                            column=class_node.col_offset,
                            message=f"Adapter class '{class_node.name}' doesn't implement a port",
                            suggestion="Adapters should implement port interfaces",
                            confidence=0.6,
                        ),
                    )

        return violations

    def _validate_clean_architecture(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Clean Architecture patterns.
        """
        violations = []

        # Check for proper dependency direction
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for class_node in classes:
            class_name = class_node.name.lower()

            # Check if domain entities don't depend on external frameworks
            if any(
                keyword in class_name for keyword in self.patterns["clean_architecture"]["entities"]
            ):
                imports = self._get_imports(tree)
                framework_imports = [
                    imp
                    for imp in imports
                    if any(
                        fw in imp.lower()
                        for fw in ["django", "flask", "fastapi", "sqlalchemy", "requests"]
                    )
                ]

                if framework_imports:
                    violations.append(
                        ArchitecturalViolation(
                            pattern="clean_architecture",
                            violation_type="entity_framework_dependency",
                            severity="high",
                            file=str(file_path),
                            line=class_node.lineno,
                            column=class_node.col_offset,
                            message=f"Domain entity '{class_node.name}' depends on framework: {framework_imports}",
                            suggestion="Domain entities should not depend on external frameworks",
                            confidence=0.9,
                        ),
                    )

            # Check if use cases don't depend on frameworks
            elif any(
                keyword in class_name
                for keyword in self.patterns["clean_architecture"]["use_cases"]
            ):
                imports = self._get_imports(tree)
                framework_imports = [
                    imp
                    for imp in imports
                    if any(
                        fw in imp.lower()
                        for fw in ["django", "flask", "fastapi", "sqlalchemy", "requests"]
                    )
                ]

                if framework_imports:
                    violations.append(
                        ArchitecturalViolation(
                            pattern="clean_architecture",
                            violation_type="use_case_framework_dependency",
                            severity="high",
                            file=str(file_path),
                            line=class_node.lineno,
                            column=class_node.col_offset,
                            message=f"Use case '{class_node.name}' depends on framework: {framework_imports}",
                            suggestion="Use cases should not depend on external frameworks",
                            confidence=0.9,
                        ),
                    )

        return violations

    def _validate_solid_principles(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate SOLID principles.
        """
        violations = []

        # Single Responsibility Principle
        violations.extend(self._validate_single_responsibility(tree, file_path))

        # Open/Closed Principle
        violations.extend(self._validate_open_closed_principle(tree, file_path))

        # Liskov Substitution Principle
        violations.extend(self._validate_liskov_substitution(tree, file_path))

        # Interface Segregation Principle
        violations.extend(self._validate_interface_segregation(tree, file_path))

        # Dependency Inversion Principle
        violations.extend(self._validate_dependency_inversion(tree, file_path))

        return violations

    def _validate_single_responsibility(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Single Responsibility Principle.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes with too many responsibilities
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 10:  # Threshold for too many methods
                    violations.append(
                        ArchitecturalViolation(
                            pattern="solid",
                            violation_type="srp_violation",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' may violate Single Responsibility Principle with {len(methods)} methods",
                            suggestion="Consider splitting into smaller classes with single responsibilities",
                            confidence=0.6,
                        ),
                    )

                # Check for methods with too many responsibilities
                for method in methods:
                    if len(method.body) > 20:  # Threshold for too many statements
                        violations.append(
                            ArchitecturalViolation(
                                pattern="solid",
                                violation_type="srp_method_violation",
                                severity="medium",
                                file=str(file_path),
                                line=method.lineno,
                                column=method.col_offset,
                                message=f"Method '{method.name}' may violate Single Responsibility Principle",
                                suggestion="Consider breaking into smaller, more focused methods",
                                confidence=0.6,
                            ),
                        )

        return violations

    def _validate_open_closed_principle(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Open/Closed Principle.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes with many if/elif statements (violation of OCP)
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        if_elif_count = len([n for n in ast.walk(method) if isinstance(n, ast.If)])
                        if if_elif_count > 5:  # Threshold for too many conditionals
                            violations.append(
                                ArchitecturalViolation(
                                    pattern="solid",
                                    violation_type="ocp_violation",
                                    severity="medium",
                                    file=str(file_path),
                                    line=method.lineno,
                                    column=method.col_offset,
                                    message=f"Method '{method.name}' may violate Open/Closed Principle with {if_elif_count} conditionals",
                                    suggestion="Consider using polymorphism or strategy pattern",
                                    confidence=0.6,
                                ),
                            )

        return violations

    def _validate_liskov_substitution(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Liskov Substitution Principle.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.bases:  # Has base classes
                    # Check for methods that throw exceptions in subclasses
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            # Check for raise statements
                            raises = [n for n in ast.walk(method) if isinstance(n, ast.Raise)]
                            if raises:
                                violations.append(
                                    ArchitecturalViolation(
                                        pattern="solid",
                                        violation_type="lsp_violation",
                                        severity="medium",
                                        file=str(file_path),
                                        line=method.lineno,
                                        column=method.col_offset,
                                        message=f"Method '{method.name}' in subclass raises exceptions",
                                        suggestion="Subclasses should not throw exceptions that base class doesn't",
                                        confidence=0.5,
                                    ),
                                )

        return violations

    def _validate_interface_segregation(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Interface Segregation Principle.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes with too many methods (fat interface)
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 15:  # Threshold for fat interface
                    violations.append(
                        ArchitecturalViolation(
                            pattern="solid",
                            violation_type="isp_violation",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' may violate Interface Segregation Principle with {len(methods)} methods",
                            suggestion="Consider splitting into smaller, more focused interfaces",
                            confidence=0.6,
                        ),
                    )

        return violations

    def _validate_dependency_inversion(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Dependency Inversion Principle.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes that depend on concrete implementations
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        # Check for instantiation of concrete classes
                        instantiations = [
                            n
                            for n in ast.walk(method)
                            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                        ]
                        for inst in instantiations:
                            if not inst.func.id.startswith("_"):  # Not a private method
                                violations.append(
                                    ArchitecturalViolation(
                                        pattern="solid",
                                        violation_type="dip_violation",
                                        severity="low",
                                        file=str(file_path),
                                        line=inst.lineno,
                                        column=inst.col_offset,
                                        message=f"Method '{method.name}' instantiates concrete class '{inst.func.id}'",
                                        suggestion="Consider using dependency injection or abstract interfaces",
                                        confidence=0.4,
                                    ),
                                )

        return violations

    def _validate_dependency_injection(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Dependency Injection patterns.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes with constructor injection
                init_method = None
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name == "__init__":
                        init_method = method
                        break

                if init_method:
                    # Check if constructor takes dependencies as parameters
                    params = init_method.args.args
                    if len(params) > 1:  # More than just self
                        # Check if dependencies are stored as instance variables
                        assignments = [
                            n for n in ast.walk(init_method) if isinstance(n, ast.Assign)
                        ]
                        if len(assignments) < len(params) - 1:  # Not all params assigned
                            violations.append(
                                ArchitecturalViolation(
                                    pattern="dependency_injection",
                                    violation_type="incomplete_di",
                                    severity="medium",
                                    file=str(file_path),
                                    line=init_method.lineno,
                                    column=init_method.col_offset,
                                    message=f"Constructor '{init_method.name}' may not properly inject all dependencies",
                                    suggestion="Ensure all constructor parameters are stored as instance variables",
                                    confidence=0.6,
                                ),
                            )

        return violations

    def _validate_factory_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Factory Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = class_node.name.lower()

                # Check for factory classes
                if "factory" in class_name:
                    # Check if factory has create methods
                    create_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "create" in m.name.lower()
                    ]
                    if not create_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="factory",
                                violation_type="missing_create_method",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Factory class '{node.name}' doesn't have create methods",
                                suggestion="Factory classes should have create methods for object instantiation",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_strategy_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Strategy Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for strategy classes
                if "strategy" in node.name.lower() or "handler" in node.name.lower():
                    # Check if strategy implements execute method
                    execute_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "execute" in m.name.lower()
                    ]
                    if not execute_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="strategy",
                                violation_type="missing_execute_method",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Strategy class '{node.name}' doesn't have execute method",
                                suggestion="Strategy classes should have execute methods",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_observer_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Observer Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for observer classes
                if "observer" in node.name.lower() or "listener" in node.name.lower():
                    # Check if observer has update method
                    update_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "update" in m.name.lower()
                    ]
                    if not update_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="observer",
                                violation_type="missing_update_method",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Observer class '{node.name}' doesn't have update method",
                                suggestion="Observer classes should have update methods",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_command_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Command Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for command classes
                if "command" in node.name.lower():
                    # Check if command has execute method
                    execute_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "execute" in m.name.lower()
                    ]
                    if not execute_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="command",
                                violation_type="missing_execute_method",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Command class '{node.name}' doesn't have execute method",
                                suggestion="Command classes should have execute methods",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_repository_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Repository Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for repository classes
                if "repository" in node.name.lower():
                    # Check if repository has CRUD methods
                    crud_methods = []
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            method_name = method.name.lower()
                            if any(
                                crud in method_name
                                for crud in [
                                    "create",
                                    "read",
                                    "update",
                                    "delete",
                                    "save",
                                    "find",
                                    "get",
                                    "add",
                                    "remove",
                                ]
                            ):
                                crud_methods.append(method)

                    if len(crud_methods) < 3:  # Should have at least 3 CRUD methods
                        violations.append(
                            ArchitecturalViolation(
                                pattern="repository",
                                violation_type="incomplete_crud",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Repository class '{node.name}' has incomplete CRUD methods",
                                suggestion="Repository classes should have complete CRUD operations",
                                confidence=0.6,
                            ),
                        )

        return violations

    def _validate_unit_of_work(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Unit of Work Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for unit of work classes
                if "unit" in node.name.lower() and "work" in node.name.lower():
                    # Check if unit of work has commit and rollback methods
                    commit_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "commit" in m.name.lower()
                    ]
                    rollback_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "rollback" in m.name.lower()
                    ]

                    if not commit_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="unit_of_work",
                                violation_type="missing_commit_method",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Unit of Work class '{node.name}' doesn't have commit method",
                                suggestion="Unit of Work classes should have commit methods",
                                confidence=0.8,
                            ),
                        )

                    if not rollback_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="unit_of_work",
                                violation_type="missing_rollback_method",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Unit of Work class '{node.name}' doesn't have rollback method",
                                suggestion="Unit of Work classes should have rollback methods",
                                confidence=0.8,
                            ),
                        )

        return violations

    def _validate_cqrs_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate CQRS Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for command classes
                if "command" in class_name:
                    # Check if command has execute method
                    execute_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "execute" in m.name.lower()
                    ]
                    if not execute_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="cqrs",
                                violation_type="missing_command_execute",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Command class '{node.name}' doesn't have execute method",
                                suggestion="Command classes should have execute methods",
                                confidence=0.7,
                            ),
                        )

                # Check for query classes
                elif "query" in class_name:
                    # Check if query has execute method
                    execute_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "execute" in m.name.lower()
                    ]
                    if not execute_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="cqrs",
                                violation_type="missing_query_execute",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Query class '{node.name}' doesn't have execute method",
                                suggestion="Query classes should have execute methods",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_event_sourcing(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Event Sourcing Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for event classes
                if "event" in class_name:
                    # Check if event has apply method
                    apply_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "apply" in m.name.lower()
                    ]
                    if not apply_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="event_sourcing",
                                violation_type="missing_apply_method",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Event class '{node.name}' doesn't have apply method",
                                suggestion="Event classes should have apply methods",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_mvc_pattern(self, tree: ast.AST, file_path: Path) -> list[ArchitecturalViolation]:
        """
        Validate MVC Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for controller classes
                if "controller" in class_name:
                    # Check if controller has action methods
                    action_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
                    ]
                    if len(action_methods) < 2:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="mvc",
                                violation_type="incomplete_controller",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Controller class '{node.name}' has too few action methods",
                                suggestion="Controller classes should have multiple action methods",
                                confidence=0.6,
                            ),
                        )

                # Check for model classes
                elif "model" in class_name:
                    # Check if model has data properties
                    properties = [m for m in node.body if isinstance(m, ast.Assign)]
                    if len(properties) < 2:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="mvc",
                                violation_type="incomplete_model",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Model class '{node.name}' has too few properties",
                                suggestion="Model classes should have data properties",
                                confidence=0.6,
                            ),
                        )

        return violations

    def _validate_mvp_pattern(self, tree: ast.AST, file_path: Path) -> list[ArchitecturalViolation]:
        """
        Validate MVP Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for presenter classes
                if "presenter" in class_name:
                    # Check if presenter has view reference
                    view_refs = [
                        m
                        for m in node.body
                        if isinstance(m, ast.Assign) and "view" in str(m).lower()
                    ]
                    if not view_refs:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="mvp",
                                violation_type="missing_view_reference",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Presenter class '{node.name}' doesn't have view reference",
                                suggestion="Presenter classes should have view references",
                                confidence=0.6,
                            ),
                        )

        return violations

    def _validate_mvvm_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate MVVM Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for viewmodel classes
                if "viewmodel" in class_name:
                    # Check if viewmodel has properties
                    properties = [m for m in node.body if isinstance(m, ast.Assign)]
                    if len(properties) < 2:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="mvvm",
                                violation_type="incomplete_viewmodel",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"ViewModel class '{node.name}' has too few properties",
                                suggestion="ViewModel classes should have data properties",
                                confidence=0.6,
                            ),
                        )

        return violations

    def _validate_layered_architecture(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Layered Architecture patterns.
        """
        violations = []

        # Check for proper layer separation
        imports = self._get_imports(tree)

        # Check if presentation layer imports business logic
        if any(
            "presentation" in str(file_path).lower() or "view" in str(file_path).lower()
            for _ in [1]
        ):
            business_imports = [
                imp
                for imp in imports
                if any(biz in imp.lower() for biz in ["business", "service", "domain"])
            ]
            if business_imports:
                violations.append(
                    ArchitecturalViolation(
                        pattern="layered_architecture",
                        violation_type="presentation_business_dependency",
                        severity="medium",
                        file=str(file_path),
                        line=1,
                        column=0,
                        message="Presentation layer imports business logic",
                        suggestion="Presentation layer should not directly import business logic",
                        confidence=0.6,
                    ),
                )

        return violations

    def _validate_microservices_patterns(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Microservices patterns.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for service classes
                if "service" in class_name:
                    # Check if service has proper error handling
                    error_handling = [
                        m for m in node.body if isinstance(m, ast.FunctionDef) and "try" in str(m)
                    ]
                    if not error_handling:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="microservices",
                                violation_type="missing_error_handling",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Service class '{node.name}' lacks error handling",
                                suggestion="Microservice classes should have proper error handling",
                                confidence=0.6,
                            ),
                        )

        return violations

    def _validate_api_gateway_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate API Gateway Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for gateway classes
                if "gateway" in class_name or "proxy" in class_name:
                    # Check if gateway has routing methods
                    routing_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef)
                        and any(route in m.name.lower() for route in ["route", "forward", "proxy"])
                    ]
                    if not routing_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="api_gateway",
                                violation_type="missing_routing_methods",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Gateway class '{node.name}' doesn't have routing methods",
                                suggestion="Gateway classes should have routing methods",
                                confidence=0.8,
                            ),
                        )

        return violations

    def _validate_circuit_breaker_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Circuit Breaker Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for circuit breaker classes
                if "circuit" in class_name and "breaker" in class_name:
                    # Check if circuit breaker has state management
                    state_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef)
                        and any(
                            state in m.name.lower()
                            for state in ["open", "closed", "half_open", "state"]
                        )
                    ]
                    if not state_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="circuit_breaker",
                                violation_type="missing_state_management",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Circuit breaker class '{node.name}' doesn't have state management",
                                suggestion="Circuit breaker classes should have state management methods",
                                confidence=0.8,
                            ),
                        )

        return violations

    def _validate_retry_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Retry Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for retry classes
                if "retry" in class_name:
                    # Check if retry has retry logic
                    retry_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "retry" in m.name.lower()
                    ]
                    if not retry_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="retry",
                                violation_type="missing_retry_logic",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Retry class '{node.name}' doesn't have retry logic",
                                suggestion="Retry classes should have retry logic methods",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_bulkhead_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Bulkhead Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for bulkhead classes
                if "bulkhead" in class_name:
                    # Check if bulkhead has isolation methods
                    isolation_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef)
                        and any(
                            iso in m.name.lower() for iso in ["isolate", "separate", "partition"]
                        )
                    ]
                    if not isolation_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="bulkhead",
                                violation_type="missing_isolation_methods",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Bulkhead class '{node.name}' doesn't have isolation methods",
                                suggestion="Bulkhead classes should have isolation methods",
                                confidence=0.7,
                            ),
                        )

        return violations

    def _validate_saga_pattern(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Saga Pattern implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for saga classes
                if "saga" in class_name:
                    # Check if saga has compensation methods
                    compensation_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef)
                        and any(
                            comp in m.name.lower() for comp in ["compensate", "rollback", "undo"]
                        )
                    ]
                    if not compensation_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="saga",
                                violation_type="missing_compensation_methods",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Saga class '{node.name}' doesn't have compensation methods",
                                suggestion="Saga classes should have compensation methods",
                                confidence=0.8,
                            ),
                        )

        return violations

    def _validate_event_driven_architecture(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Event-Driven Architecture patterns.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for event handler classes
                if "handler" in class_name and "event" in class_name:
                    # Check if event handler has handle method
                    handle_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and "handle" in m.name.lower()
                    ]
                    if not handle_methods:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="event_driven",
                                violation_type="missing_handle_method",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Event handler class '{node.name}' doesn't have handle method",
                                suggestion="Event handler classes should have handle methods",
                                confidence=0.8,
                            ),
                        )

        return violations

    def _validate_domain_driven_design(
        self, tree: ast.AST, file_path: Path,
    ) -> list[ArchitecturalViolation]:
        """
        Validate Domain-Driven Design patterns.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for aggregate classes
                if "aggregate" in class_name:
                    # Check if aggregate has business logic
                    business_methods = [
                        m
                        for m in node.body
                        if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
                    ]
                    if len(business_methods) < 2:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="ddd",
                                violation_type="incomplete_aggregate",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Aggregate class '{node.name}' has too few business methods",
                                suggestion="Aggregate classes should have business logic methods",
                                confidence=0.6,
                            ),
                        )

                # Check for value object classes
                elif "value" in class_name and "object" in class_name:
                    # Check if value object is immutable
                    assignments = [m for m in node.body if isinstance(m, ast.Assign)]
                    if assignments:
                        violations.append(
                            ArchitecturalViolation(
                                pattern="ddd",
                                violation_type="mutable_value_object",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Value object class '{node.name}' may be mutable",
                                suggestion="Value objects should be immutable",
                                confidence=0.6,
                            ),
                        )

        return violations

    def _is_abstract_method(self, method: ast.FunctionDef) -> bool:
        """
        Check if a method is abstract.
        """
        # Simple check for abstract methods
        if not method.body:
            return True

        # Check if method only contains pass or raise NotImplementedError
        if len(method.body) == 1:
            if isinstance(method.body[0], ast.Pass):
                return True
            if isinstance(method.body[0], ast.Raise):
                return True

        return False

    def _get_imports(self, tree: ast.AST) -> list[str]:
        """
        Get all import statements from AST.
        """
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _count_by_severity(self, violations: list[ArchitecturalViolation]) -> dict[str, int]:
        """
        Count violations by severity.
        """
        counts = defaultdict(int)
        for violation in violations:
            counts[violation.severity] += 1
        return dict(counts)

    def generate_report(self) -> dict[str, Any]:
        """
        Generate comprehensive architectural pattern report.
        """
        total_violations = len(self.violations)
        severity_counts = self._count_by_severity(self.violations)

        # Group by pattern
        pattern_counts = defaultdict(int)
        for violation in self.violations:
            pattern_counts[violation.pattern] += 1

        # Group by file
        file_violations = defaultdict(list)
        for violation in self.violations:
            file_violations[violation.file].append(violation)

        return {
            "summary": {
                "total_violations": total_violations,
                "severity_counts": severity_counts,
                "pattern_counts": dict(pattern_counts),
                "files_affected": len(file_violations),
            },
            "violations": [
                {
                    "pattern": violation.pattern,
                    "violation_type": violation.violation_type,
                    "severity": violation.severity,
                    "file": violation.file,
                    "line": violation.line,
                    "column": violation.column,
                    "message": violation.message,
                    "suggestion": violation.suggestion,
                    "confidence": violation.confidence,
                }
                for violation in self.violations
            ],
            "files": {
                file: {
                    "violation_count": len(violations),
                    "severity_counts": self._count_by_severity(violations),
                }
                for file, violations in file_violations.items()
            },
        }


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Architectural Pattern Validator")
    parser.add_argument("path", help="Path to analyze")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--severity", choices=["low", "medium", "high"], help="Filter by severity")
    parser.add_argument("--pattern", help="Filter by architectural pattern")

    args = parser.parse_args()

    validator = ArchitecturalPatternValidator()

    # Analyze files
    path = Path(args.path)
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))

    for file_path in files:
        validator.analyze_file(file_path)

    # Generate report
    report = validator.generate_report()

    # Filter results if requested
    if args.severity or args.pattern:
        filtered_violations = []
        for violation in report["violations"]:
            if args.severity and violation["severity"] != args.severity:
                continue
            if args.pattern and violation["pattern"] != args.pattern:
                continue
            filtered_violations.append(violation)
        report["violations"] = filtered_violations
        report["summary"]["total_violations"] = len(filtered_violations)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Pretty print report
        print("🏗️ ARCHITECTURAL PATTERN VALIDATION REPORT")
        print("=" * 60)
        print(f"Total violations found: {report['summary']['total_violations']}")
        print(f"Files affected: {report['summary']['files_affected']}")
        print()

        print("Severity breakdown:")
        for severity, count in report["summary"]["severity_counts"].items():
            print(f"  {severity}: {count}")
        print()

        print("Pattern breakdown:")
        for pattern, count in report["summary"]["pattern_counts"].items():
            print(f"  {pattern}: {count}")
        print()

        if report["violations"]:
            print("Detailed findings:")
            for violation in report["violations"]:
                print(
                    f"  {violation['severity'].upper()}: {violation['pattern']} - {violation['violation_type']} in {violation['file']}:{violation['line']}",
                )
                print(f"    {violation['message']}")
                print(f"    Suggestion: {violation['suggestion']}")
                print()


if __name__ == "__main__":
    main()
