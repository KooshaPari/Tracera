"""Hexagonal Architecture Refactoring Patterns.

This package provides tools for analyzing, extracting, and validating hexagonal
architecture patterns in Python codebases.

Main Components:
    - analyzer: Code analysis for metrics, complexity, and violations
    - extractor: Automated code extraction by class, concern, pattern, or layer
    - validator: Hexagonal architecture validation
    - cli: Command-line interface

Quick Start:
    ```python
    from pheno.patterns.refactoring import CodeAnalyzer, ClassExtractor, validate_layers
    from pathlib import Path

    # Analyze a file
    analyzer = CodeAnalyzer()
    result = await analyzer.analyze_file(Path('myfile.py'))
    print(f"Complexity: {result.metrics.cyclomatic_complexity}")

    # Extract a class
    extractor = ClassExtractor()
    result = await extractor.extract_class(
        Path('source.py'),
        'MyClass',
        Path('target.py')
    )

    # Validate architecture
    validation = await validate_layers(Path('myfile.py'))
    print(f"Valid: {validation.is_valid}")
    ```

CLI Usage:
    ```bash
    # Analyze a file
    python -m pheno.patterns.refactoring.cli analyze file myfile.py

    # Extract a class
    python -m pheno.patterns.refactoring.cli extract class myfile.py MyClass

    # Validate architecture
    python -m pheno.patterns.refactoring.cli validate layers myfile.py

    # Generate report
    python -m pheno.patterns.refactoring.cli report ./src
    ```
"""

from .analyzer import (
    AnalysisResult,
    ArchitecturalViolation,
    CodeAnalyzer,
    CodeMetrics,
    ComplexityAnalyzer,
    analyze_complexity,
    detect_large_files,
    detect_violations,
)
from .extractor import (
    ClassExtractor,
    ClassInfo,
    ConcernExtractor,
    ConcernInfo,
    ExtractionResult,
    LayerExtractor,
    PatternExtractor,
)
from .validator import (
    DependencyValidator,
    LayerValidator,
    PortAdapterValidator,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    validate_dependencies,
    validate_layers,
    validate_port_adapter,
)

__all__ = [
    "AnalysisResult",
    "ArchitecturalViolation",
    # Extractor
    "ClassExtractor",
    "ClassInfo",
    # Analyzer
    "CodeAnalyzer",
    "CodeMetrics",
    "ComplexityAnalyzer",
    "ConcernExtractor",
    "ConcernInfo",
    "DependencyValidator",
    "ExtractionResult",
    "LayerExtractor",
    "LayerValidator",
    "PatternExtractor",
    # Validator
    "PortAdapterValidator",
    "ValidationIssue",
    "ValidationResult",
    "ValidationRule",
    "analyze_complexity",
    "detect_large_files",
    "detect_violations",
    "validate_dependencies",
    "validate_layers",
    "validate_port_adapter",
]

__version__ = "1.0.0"
__author__ = "Pheno SDK Team"
__description__ = "Hexagonal Architecture Refactoring Patterns for Python"
