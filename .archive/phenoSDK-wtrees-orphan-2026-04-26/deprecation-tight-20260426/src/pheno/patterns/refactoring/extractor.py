"""Automated Code Extraction for Hexagonal Architecture Refactoring.

This module provides utilities for extracting code components (classes, concerns,
patterns, layers) from existing files to improve code organization and maintainability.
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """
    Result of code extraction.
    """

    source_file: str
    target_file: str
    extracted_code: str
    remaining_code: str
    dependencies: list[str] = field(default_factory=list)
    success: bool = True
    error: str | None = None

    def __str__(self) -> str:
        """
        String representation.
        """
        status = "✓" if self.success else "✗"
        return f"{status} Extracted from {self.source_file} → {self.target_file}"


@dataclass
class ClassInfo:
    """
    Information about a class.
    """

    name: str
    line_start: int
    line_end: int
    methods: list[str]
    base_classes: list[str]
    decorators: list[str]
    imports: set[str] = field(default_factory=set)

    @property
    def method_count(self) -> int:
        """
        Get number of methods.
        """
        return len(self.methods)


@dataclass
class ConcernInfo:
    """
    Information about a functional concern.
    """

    name: str
    classes: list[str]
    functions: list[str]
    related_imports: set[str] = field(default_factory=set)


class ClassExtractor:
    """
    Extract individual classes from files.
    """

    def __init__(self) -> None:
        """
        Initialize class extractor.
        """
        self.extracted_classes: list[ClassInfo] = []

    async def extract_class(
        self, source_file: Path, class_name: str, target_file: Path | None = None,
    ) -> ExtractionResult:
        """Extract a single class from source file.

        Args:
            source_file: Source file containing the class
            class_name: Name of class to extract
            target_file: Target file path (auto-generated if not provided)

        Returns:
            ExtractionResult with extraction details
        """
        try:
            content = source_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(source_file))

            # Find the class
            class_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    class_node = node
                    break

            if not class_node:
                return ExtractionResult(
                    source_file=str(source_file),
                    target_file="",
                    extracted_code="",
                    remaining_code=content,
                    success=False,
                    error=f"Class '{class_name}' not found",
                )

            # Extract class info
            class_info = self._get_class_info(class_node)

            # Extract dependencies
            dependencies = self._extract_dependencies(tree, class_info)

            # Generate target file path
            if not target_file:
                target_file = source_file.parent / f"{class_name.lower()}.py"

            # Build extracted code
            extracted_code = self._build_extracted_code(content, class_node, dependencies)

            # Build remaining code
            remaining_code = self._build_remaining_code(content, class_node)

            return ExtractionResult(
                source_file=str(source_file),
                target_file=str(target_file),
                extracted_code=extracted_code,
                remaining_code=remaining_code,
                dependencies=dependencies,
            )

        except Exception as e:
            logger.exception(f"Error extracting class {class_name} from {source_file}: {e}")
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code="",
                success=False,
                error=str(e),
            )

    def _get_class_info(self, class_node: ast.ClassDef) -> ClassInfo:
        """
        Extract information about a class.
        """
        methods = [
            node.name
            for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        base_classes = [ast.unparse(base) for base in class_node.bases]

        decorators = [ast.unparse(dec) for dec in class_node.decorator_list]

        return ClassInfo(
            name=class_node.name,
            line_start=class_node.lineno,
            line_end=class_node.end_lineno or class_node.lineno,
            methods=methods,
            base_classes=base_classes,
            decorators=decorators,
        )

    def _extract_dependencies(self, tree: ast.AST, class_info: ClassInfo) -> list[str]:
        """
        Extract import dependencies for a class.
        """
        dependencies: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = ", ".join(alias.name for alias in node.names)
                dependencies.append(f"from {node.module} import {names}")

        return dependencies

    def _build_extracted_code(
        self, content: str, class_node: ast.ClassDef, dependencies: list[str],
    ) -> str:
        """
        Build the extracted code with dependencies.
        """
        lines = content.splitlines()

        # Get class code
        class_start = class_node.lineno - 1
        class_end = class_node.end_lineno or class_node.lineno

        class_lines = lines[class_start:class_end]

        # Build final code
        parts = [
            '"""',
            f"Extracted class: {class_node.name}",
            '"""',
            "",
            *dependencies,
            "",
            "",
            *class_lines,
        ]

        return "\n".join(parts)

    def _build_remaining_code(self, content: str, class_node: ast.ClassDef) -> str:
        """
        Build remaining code after extraction.
        """
        lines = content.splitlines()

        class_start = class_node.lineno - 1
        class_end = class_node.end_lineno or class_node.lineno

        # Remove class lines
        remaining_lines = lines[:class_start] + lines[class_end:]

        return "\n".join(remaining_lines)


class ConcernExtractor:
    """
    Extract code by functional concern.
    """

    CONCERN_PATTERNS = {
        "authentication": ["auth", "login", "token", "credential"],
        "validation": ["validate", "verify", "check"],
        "caching": ["cache", "memoize", "store"],
        "logging": ["log", "logger", "audit"],
        "monitoring": ["metric", "monitor", "track", "observe"],
        "serialization": ["serialize", "deserialize", "json", "xml"],
        "database": ["db", "database", "repository", "dao"],
        "api": ["api", "endpoint", "route", "controller"],
    }

    async def extract_concern(
        self, source_file: Path, concern: str, target_dir: Path | None = None,
    ) -> ExtractionResult:
        """Extract code related to a specific concern.

        Args:
            source_file: Source file to analyze
            concern: Type of concern (e.g., 'authentication', 'validation')
            target_dir: Target directory for extracted code

        Returns:
            ExtractionResult with extraction details
        """
        try:
            content = source_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(source_file))

            patterns = self.CONCERN_PATTERNS.get(concern.lower(), [concern.lower()])

            # Find classes and functions related to concern
            related_classes = self._find_related_classes(tree, patterns)
            related_functions = self._find_related_functions(tree, patterns)

            if not related_classes and not related_functions:
                return ExtractionResult(
                    source_file=str(source_file),
                    target_file="",
                    extracted_code="",
                    remaining_code=content,
                    success=False,
                    error=f"No code found for concern '{concern}'",
                )

            # Extract code
            extracted_code = self._build_concern_code(
                content, tree, related_classes, related_functions,
            )

            # Generate target file
            if not target_dir:
                target_dir = source_file.parent
            target_file = target_dir / f"{concern.lower()}.py"

            # Build remaining code
            remaining_code = self._build_remaining_concern_code(
                content, related_classes, related_functions,
            )

            return ExtractionResult(
                source_file=str(source_file),
                target_file=str(target_file),
                extracted_code=extracted_code,
                remaining_code=remaining_code,
            )

        except Exception as e:
            logger.exception(f"Error extracting concern {concern} from {source_file}: {e}")
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code="",
                success=False,
                error=str(e),
            )

    def _find_related_classes(self, tree: ast.AST, patterns: list[str]) -> list[ast.ClassDef]:
        """
        Find classes related to concern patterns.
        """
        related = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any(pattern in node.name.lower() for pattern in patterns):
                    related.append(node)

        return related

    def _find_related_functions(self, tree: ast.AST, patterns: list[str]) -> list[ast.FunctionDef]:
        """
        Find functions related to concern patterns.
        """
        related = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(pattern in node.name.lower() for pattern in patterns):
                    related.append(node)

        return related

    def _build_concern_code(
        self,
        content: str,
        tree: ast.AST,
        classes: list[ast.ClassDef],
        functions: list[ast.FunctionDef],
    ) -> str:
        """
        Build code for extracted concern.
        """
        lines = content.splitlines()
        extracted_lines = []

        # Add imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line = lines[node.lineno - 1]
                if line not in extracted_lines:
                    extracted_lines.append(line)

        extracted_lines.append("")

        # Add classes
        for class_node in classes:
            start = class_node.lineno - 1
            end = class_node.end_lineno or class_node.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        # Add functions
        for func_node in functions:
            start = func_node.lineno - 1
            end = func_node.end_lineno or func_node.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        return "\n".join(extracted_lines)

    def _build_remaining_concern_code(
        self, content: str, classes: list[ast.ClassDef], functions: list[ast.FunctionDef],
    ) -> str:
        """
        Build remaining code after concern extraction.
        """
        lines = content.splitlines()
        lines_to_remove = set()

        # Mark class lines for removal
        for class_node in classes:
            start = class_node.lineno - 1
            end = class_node.end_lineno or class_node.lineno
            lines_to_remove.update(range(start, end))

        # Mark function lines for removal
        for func_node in functions:
            start = func_node.lineno - 1
            end = func_node.end_lineno or func_node.lineno
            lines_to_remove.update(range(start, end))

        # Build remaining code
        remaining_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]

        return "\n".join(remaining_lines)


class PatternExtractor:
    """
    Extract design patterns from code.
    """

    async def extract_pattern(
        self, source_file: Path, pattern_type: str, target_dir: Path | None = None,
    ) -> ExtractionResult:
        """Extract a design pattern from source file.

        Args:
            source_file: Source file to analyze
            pattern_type: Type of pattern (e.g., 'factory', 'singleton', 'observer')
            target_dir: Target directory for extracted pattern

        Returns:
            ExtractionResult with extraction details
        """
        try:
            content = source_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(source_file))

            # Detect pattern based on type
            if pattern_type.lower() == "factory":
                return await self._extract_factory_pattern(source_file, tree, content, target_dir)
            if pattern_type.lower() == "singleton":
                return await self._extract_singleton_pattern(source_file, tree, content, target_dir)
            if pattern_type.lower() == "strategy":
                return await self._extract_strategy_pattern(source_file, tree, content, target_dir)
            if pattern_type.lower() == "observer":
                return await self._extract_observer_pattern(source_file, tree, content, target_dir)
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code=content,
                success=False,
                error=f"Unknown pattern type: {pattern_type}",
            )

        except Exception as e:
            logger.exception(f"Error extracting pattern {pattern_type} from {source_file}: {e}")
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code="",
                success=False,
                error=str(e),
            )

    async def _extract_factory_pattern(
        self, source_file: Path, tree: ast.AST, content: str, target_dir: Path | None,
    ) -> ExtractionResult:
        """
        Extract factory pattern classes.
        """
        factory_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if "factory" in node.name.lower():
                    factory_classes.append(node)

        if not factory_classes:
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code=content,
                success=False,
                error="No factory pattern found",
            )

        # Extract factory code
        lines = content.splitlines()
        extracted_lines = []

        for factory in factory_classes:
            start = factory.lineno - 1
            end = factory.end_lineno or factory.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        extracted_code = "\n".join(extracted_lines)

        if not target_dir:
            target_dir = source_file.parent
        target_file = target_dir / "factory.py"

        return ExtractionResult(
            source_file=str(source_file),
            target_file=str(target_file),
            extracted_code=extracted_code,
            remaining_code=content,
        )

    async def _extract_singleton_pattern(
        self, source_file: Path, tree: ast.AST, content: str, target_dir: Path | None,
    ) -> ExtractionResult:
        """
        Extract singleton pattern classes.
        """
        # Look for classes with singleton pattern
        singleton_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for __new__ method (common in singleton)
                has_new = any(
                    isinstance(n, ast.FunctionDef) and n.name == "__new__" for n in node.body
                )
                # Check for 'singleton' in name
                has_singleton_name = "singleton" in node.name.lower()

                if has_new or has_singleton_name:
                    singleton_classes.append(node)

        if not singleton_classes:
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code=content,
                success=False,
                error="No singleton pattern found",
            )

        # Extract singleton code
        lines = content.splitlines()
        extracted_lines = []

        for singleton in singleton_classes:
            start = singleton.lineno - 1
            end = singleton.end_lineno or singleton.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        extracted_code = "\n".join(extracted_lines)

        if not target_dir:
            target_dir = source_file.parent
        target_file = target_dir / "singleton.py"

        return ExtractionResult(
            source_file=str(source_file),
            target_file=str(target_file),
            extracted_code=extracted_code,
            remaining_code=content,
        )

    async def _extract_strategy_pattern(
        self, source_file: Path, tree: ast.AST, content: str, target_dir: Path | None,
    ) -> ExtractionResult:
        """
        Extract strategy pattern classes.
        """
        strategy_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if "strategy" in node.name.lower():
                    strategy_classes.append(node)

        if not strategy_classes:
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code=content,
                success=False,
                error="No strategy pattern found",
            )

        lines = content.splitlines()
        extracted_lines = []

        for strategy in strategy_classes:
            start = strategy.lineno - 1
            end = strategy.end_lineno or strategy.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        extracted_code = "\n".join(extracted_lines)

        if not target_dir:
            target_dir = source_file.parent
        target_file = target_dir / "strategy.py"

        return ExtractionResult(
            source_file=str(source_file),
            target_file=str(target_file),
            extracted_code=extracted_code,
            remaining_code=content,
        )

    async def _extract_observer_pattern(
        self, source_file: Path, tree: ast.AST, content: str, target_dir: Path | None,
    ) -> ExtractionResult:
        """
        Extract observer pattern classes.
        """
        observer_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(
                keyword in node.name.lower()
                for keyword in ["observer", "listener", "subscriber"]
            ):
                observer_classes.append(node)

        if not observer_classes:
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code=content,
                success=False,
                error="No observer pattern found",
            )

        lines = content.splitlines()
        extracted_lines = []

        for observer in observer_classes:
            start = observer.lineno - 1
            end = observer.end_lineno or observer.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        extracted_code = "\n".join(extracted_lines)

        if not target_dir:
            target_dir = source_file.parent
        target_file = target_dir / "observer.py"

        return ExtractionResult(
            source_file=str(source_file),
            target_file=str(target_file),
            extracted_code=extracted_code,
            remaining_code=content,
        )


class LayerExtractor:
    """
    Extract code by architectural layer.
    """

    LAYER_PATTERNS = {
        "domain": ["entity", "model", "value_object", "aggregate"],
        "application": ["service", "use_case", "usecase", "command", "query"],
        "adapters": ["adapter", "controller", "repository", "presenter"],
        "infrastructure": ["config", "database", "cache", "queue"],
        "ports": ["port", "interface", "protocol"],
    }

    async def extract_layer(
        self, source_file: Path, layer: str, target_dir: Path | None = None,
    ) -> ExtractionResult:
        """Extract code belonging to a specific architectural layer.

        Args:
            source_file: Source file to analyze
            layer: Layer name (domain, application, adapters, infrastructure, ports)
            target_dir: Target directory for extracted layer

        Returns:
            ExtractionResult with extraction details
        """
        try:
            content = source_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(source_file))

            patterns = self.LAYER_PATTERNS.get(layer.lower(), [])
            if not patterns:
                return ExtractionResult(
                    source_file=str(source_file),
                    target_file="",
                    extracted_code="",
                    remaining_code=content,
                    success=False,
                    error=f"Unknown layer: {layer}",
                )

            # Find layer-related code
            layer_classes = self._find_layer_classes(tree, patterns)
            layer_functions = self._find_layer_functions(tree, patterns)

            if not layer_classes and not layer_functions:
                return ExtractionResult(
                    source_file=str(source_file),
                    target_file="",
                    extracted_code="",
                    remaining_code=content,
                    success=False,
                    error=f"No code found for layer '{layer}'",
                )

            # Build extracted code
            extracted_code = self._build_layer_code(content, tree, layer_classes, layer_functions)

            # Generate target file
            if not target_dir:
                target_dir = source_file.parent / layer.lower()
                target_dir.mkdir(exist_ok=True)

            target_file = target_dir / f"{source_file.stem}_{layer.lower()}.py"

            return ExtractionResult(
                source_file=str(source_file),
                target_file=str(target_file),
                extracted_code=extracted_code,
                remaining_code=content,
            )

        except Exception as e:
            logger.exception(f"Error extracting layer {layer} from {source_file}: {e}")
            return ExtractionResult(
                source_file=str(source_file),
                target_file="",
                extracted_code="",
                remaining_code="",
                success=False,
                error=str(e),
            )

    def _find_layer_classes(self, tree: ast.AST, patterns: list[str]) -> list[ast.ClassDef]:
        """
        Find classes belonging to layer.
        """
        layer_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any(pattern in node.name.lower() for pattern in patterns):
                    layer_classes.append(node)

        return layer_classes

    def _find_layer_functions(self, tree: ast.AST, patterns: list[str]) -> list[ast.FunctionDef]:
        """
        Find functions belonging to layer.
        """
        layer_functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(pattern in node.name.lower() for pattern in patterns):
                    layer_functions.append(node)

        return layer_functions

    def _build_layer_code(
        self,
        content: str,
        tree: ast.AST,
        classes: list[ast.ClassDef],
        functions: list[ast.FunctionDef],
    ) -> str:
        """
        Build code for extracted layer.
        """
        lines = content.splitlines()
        extracted_lines = []

        # Add imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line = lines[node.lineno - 1]
                if line not in extracted_lines:
                    extracted_lines.append(line)

        extracted_lines.append("")

        # Add classes
        for class_node in classes:
            start = class_node.lineno - 1
            end = class_node.end_lineno or class_node.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        # Add functions
        for func_node in functions:
            start = func_node.lineno - 1
            end = func_node.end_lineno or func_node.lineno
            extracted_lines.extend(lines[start:end])
            extracted_lines.append("")

        return "\n".join(extracted_lines)
