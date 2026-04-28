#!/usr/bin/env python3
"""Architecture Detection Example.

This example demonstrates how to use the pheno.analytics.architecture module to detect
architectural patterns in a codebase.
"""

import asyncio
from pathlib import Path

from pheno.analytics.architecture import (
    ArchitectureDetector,
    ArchitectureDetectorConfig,
    ArchitectureValidator,
    ArchitectureValidatorConfig,
    DesignPatternDetector,
    PatternRegistry,
)


async def main():
    """
    Main example function.
    """
    print("🏗️ Architecture Detection Example")
    print("=" * 50)

    # Setup detector
    config = ArchitectureDetectorConfig(
        min_confidence=0.3,
        max_depth=10,
        include_hidden=False,
        skip_directories=[".git", "node_modules", "__pycache__"],
    )

    detector = ArchitectureDetector(config)

    # Detect architecture
    project_path = Path()  # Current directory
    print(f"Analyzing project: {project_path.absolute()}")

    report = detector.detect(project_path)

    # Display results
    print(f"\n📊 Detected Patterns: {report.detected_patterns}")
    print(f"🎯 Confidence Scores: {report.confidence_scores}")
    print(f"🏛️ Layer Separation: {report.layer_structure.separation_score:.2f}")
    print(f"🔧 Design Patterns: {report.design_patterns}")

    # Display metrics
    print("\n📈 Architecture Metrics:")
    print(f"  • Layer Separation Score: {report.metrics.layer_separation_score:.2f}")
    print(f"  • Dependency Complexity: {report.metrics.dependency_complexity:.2f}")
    print(f"  • Pattern Coverage: {report.metrics.pattern_coverage:.2f}")
    print(f"  • Overall Score: {report.metrics.overall_score:.2f}")

    # Display recommendations
    print("\n💡 Recommendations:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"  {i}. {rec}")

    # Validate architecture
    print("\n🔍 Architecture Validation:")
    validator_config = ArchitectureValidatorConfig(
        enforce_layer_boundaries=True, enforce_solid_principles=True,
    )
    validator = ArchitectureValidator(validator_config)

    violations = validator.validate_directory(project_path)
    print(f"  • Violations found: {len(violations)}")

    for violation in violations[:5]:  # Show first 5 violations
        print(f"    - {violation.description} ({violation.severity.value})")

    # Pattern registry example
    print("\n🔧 Pattern Registry:")
    registry = PatternRegistry()

    # Register design pattern detector
    design_detector = DesignPatternDetector()
    registry.register_detector(design_detector)

    print(f"  • Registered detectors: {len(registry.list_detectors())}")

    # Export report
    report_dict = report.to_dict()
    print(f"\n📄 Report exported with {len(report_dict)} fields")

    return report


if __name__ == "__main__":
    asyncio.run(main())
