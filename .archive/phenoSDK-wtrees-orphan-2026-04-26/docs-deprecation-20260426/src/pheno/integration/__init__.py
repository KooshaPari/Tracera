"""
Pheno Integration - Comprehensive Integration and Validation Library

A comprehensive integration library that validates all consolidated libraries
across the pheno-sdk ecosystem and ensures seamless integration.

Features:
- Cross-library integration testing
- Performance validation and benchmarking
- Migration path validation
- Production readiness assessment
- Comprehensive validation suite
- Migration validation tools
- Performance benchmarking tools

Usage:
    from pheno_integration import IntegrationValidator, PerformanceBenchmark, MigrationValidator

    # Create integration validator
    validator = IntegrationValidator()

    # Validate all libraries
    result = validator.validate_all_libraries()

    # Create performance benchmark
    benchmark = PerformanceBenchmark()

    # Run performance tests
    results = benchmark.run_performance_tests()

    # Create migration validator
    migration_validator = MigrationValidator()

    # Validate migration path
    is_valid = migration_validator.validate_migration_path("old", "new")
"""

from .benchmarks.performance import PerformanceBenchmark
from .migration.validator import MigrationValidator
from .reports.generator import ReportGenerator
from .validation.suite import ValidationSuite
from .validation.validator import IntegrationValidator

__version__ = "1.0.0"
__all__ = [
    "IntegrationValidator",
    "MigrationValidator",
    "PerformanceBenchmark",
    "ReportGenerator",
    "ValidationSuite",
]
