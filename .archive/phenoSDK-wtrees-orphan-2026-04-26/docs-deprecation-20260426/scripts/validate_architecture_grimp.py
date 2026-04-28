#!/usr/bin/env python3
"""
Grimp-based Architecture Validation Script
Validates hexagonal architecture boundaries for PhenoSDK

Usage:
    python scripts/validate_architecture_grimp.py
    python scripts/validate_architecture_grimp.py --verbose
    python scripts/validate_architecture_grimp.py --report

See: openspec/ARCHITECTURE_TOOLS_SPEC.md
"""

import sys
from pathlib import Path
from typing import List, Set, Tuple

try:
    from grimp import build_graph
except ImportError:
    print("Error: grimp not installed. Run: uv pip install grimp")
    sys.exit(1)


# ============================================================================
# HEXAGONAL ARCHITECTURE LAYER DEFINITIONS
# ============================================================================

LAYERS = {
    "domain": [
        "pheno.domain",
        "pheno.exceptions.domain",
    ],
    "ports": [
        "pheno.ports",
        "pheno.core.ports",
        "pheno.application.ports",
    ],
    "application": [
        "pheno.application",
        "pheno.credentials",
        "pheno.auth",
    ],
    "adapters": [
        "pheno.adapters",
        "pheno.core.adapters",
        "pheno.infra.adapters",
    ],
    "infrastructure": [
        "pheno.infra",
        "pheno.database",
    ],
    "interface": [
        "pheno.cli",
        "pheno_sdk",
    ],
    "cross_cutting": [
        "pheno.core",
        "pheno.logging",
        "pheno.observability",
        "pheno.exceptions",
        "pheno.events",
        "pheno.config",
    ],
    # Special: Development/Testing (allowed to import anything)
    "dev": [
        "pheno.dev",
        "pheno.testing",
    ],
}

# Layer dependency rules (what each layer CAN import from)
LAYER_DEPENDENCIES = {
    "domain": [],  # Pure domain, no dependencies
    "ports": ["domain"],
    "application": ["domain", "ports"],
    "adapters": ["domain", "ports"],
    "infrastructure": ["domain", "ports", "adapters", "application"],
    "interface": ["domain", "application", "cross_cutting"],
    "cross_cutting": ["domain"],
    "dev": [],  # Can import anything (not enforced)
}

# Explicit forbidden patterns
FORBIDDEN_PATTERNS = [
    # Domain violations
    ("pheno.domain", "pheno.infra"),
    ("pheno.domain", "pheno.adapters"),
    ("pheno.domain", "pheno.application"),
    ("pheno.domain", "pheno.cli"),
    ("pheno.domain", "pheno.dev"),

    # Ports violations
    ("pheno.ports", "pheno.adapters"),
    ("pheno.core.ports", "pheno.core.adapters"),

    # Application violations
    ("pheno.application", "pheno.infra"),
    ("pheno.application", "pheno.database"),

    # CLI violations
    ("pheno.cli", "pheno.infra"),
    ("pheno.cli", "pheno.adapters"),

    # Security violations
    ("pheno.credentials", "pheno.dev"),
]


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def get_module_layer(module: str) -> str | None:
    """Determine which layer a module belongs to."""
    for layer_name, modules in LAYERS.items():
        for layer_module in modules:
            if module.startswith(layer_module):
                return layer_name
    return None


def validate_layer_dependencies(graph) -> List[Tuple[str, str, str]]:
    """Validate that modules only import from allowed layers."""
    violations = []

    for module in graph.modules:
        source_layer = get_module_layer(module)
        if not source_layer or source_layer == "dev":
            continue  # Skip unknown or dev modules

        allowed_layers = LAYER_DEPENDENCIES.get(source_layer, [])
        allowed_layers.append(source_layer)  # Allow same-layer imports

        for imported in graph.find_modules_directly_imported_by(module):
            target_layer = get_module_layer(imported)
            if not target_layer:
                continue

            if target_layer not in allowed_layers and target_layer != "cross_cutting":
                violations.append((module, imported, f"{source_layer} -> {target_layer}"))

    return violations


def validate_forbidden_patterns(graph) -> List[Tuple[str, str]]:
    """Validate explicit forbidden import patterns."""
    violations = []

    for source, target in FORBIDDEN_PATTERNS:
        # Check if any module in source imports any module in target
        source_modules = [m for m in graph.modules if m.startswith(source)]
        target_modules = [m for m in graph.modules if m.startswith(target)]

        for source_mod in source_modules:
            imports = graph.find_modules_directly_imported_by(source_mod)
            for target_mod in target_modules:
                if target_mod in imports:
                    violations.append((source_mod, target_mod))

    return violations


def check_circular_dependencies(graph) -> List[List[str]]:
    """Find circular import chains."""
    chains = graph.find_circular_imports()
    return [list(chain) for chain in chains]


def check_module_complexity(graph, max_fanout: int = 25) -> List[Tuple[str, int]]:
    """Check for modules with too many dependencies (high fanout)."""
    violations = []

    for module in graph.modules:
        descendants = graph.find_descendants(module)
        fanout = len(descendants)
        if fanout > max_fanout:
            violations.append((module, fanout))

    return violations


# ============================================================================
# REPORTING FUNCTIONS
# ============================================================================

def print_layer_violations(violations: List[Tuple[str, str, str]]):
    """Print layer dependency violations."""
    if not violations:
        print("✓ No layer dependency violations found")
        return

    print(f"\n❌ Found {len(violations)} layer dependency violation(s):")
    for source, target, layer_info in violations:
        print(f"  - {source} → {target}")
        print(f"    (Illegal: {layer_info})")


def print_forbidden_violations(violations: List[Tuple[str, str]]):
    """Print forbidden pattern violations."""
    if not violations:
        print("✓ No forbidden pattern violations found")
        return

    print(f"\n❌ Found {len(violations)} forbidden pattern violation(s):")
    for source, target in violations:
        print(f"  - {source} → {target}")


def print_circular_dependencies(chains: List[List[str]]):
    """Print circular dependency chains."""
    if not chains:
        print("✓ No circular dependencies found")
        return

    print(f"\n⚠️  Found {len(chains)} circular dependency chain(s):")
    for i, chain in enumerate(chains, 1):
        print(f"\n  Chain {i}:")
        for module in chain:
            print(f"    → {module}")


def print_complexity_violations(violations: List[Tuple[str, int]], max_fanout: int):
    """Print module complexity violations."""
    if not violations:
        print(f"✓ No modules exceed {max_fanout} dependencies")
        return

    print(f"\n⚠️  Found {len(violations)} module(s) with high complexity:")
    for module, fanout in sorted(violations, key=lambda x: x[1], reverse=True):
        print(f"  - {module}: {fanout} dependencies (max: {max_fanout})")


def generate_report(graph):
    """Generate detailed architecture health report."""
    print("\n" + "=" * 80)
    print("PHENO SDK - ARCHITECTURE VALIDATION REPORT")
    print("=" * 80)

    # Basic stats
    print(f"\nTotal modules: {len(graph.modules)}")

    # Layer distribution
    print("\nModule distribution by layer:")
    for layer_name, modules in LAYERS.items():
        count = sum(1 for m in graph.modules if any(m.startswith(mod) for mod in modules))
        print(f"  - {layer_name:15s}: {count:3d} modules")

    # Run all validations
    print("\n" + "-" * 80)
    print("VALIDATION RESULTS")
    print("-" * 80)

    layer_violations = validate_layer_dependencies(graph)
    print_layer_violations(layer_violations)

    forbidden_violations = validate_forbidden_patterns(graph)
    print_forbidden_violations(forbidden_violations)

    circular_deps = check_circular_dependencies(graph)
    print_circular_dependencies(circular_deps)

    complexity_violations = check_module_complexity(graph)
    print_complexity_violations(complexity_violations, max_fanout=25)

    # Summary
    print("\n" + "-" * 80)
    print("SUMMARY")
    print("-" * 80)

    total_violations = len(layer_violations) + len(forbidden_violations)
    total_warnings = len(circular_deps) + len(complexity_violations)

    if total_violations == 0 and total_warnings == 0:
        print("✅ All architecture boundaries are correctly enforced!")
        return 0
    elif total_violations == 0:
        print(f"⚠️  No violations, but {total_warnings} warning(s) detected")
        return 0  # Warnings don't fail the check
    else:
        print(f"❌ {total_violations} violation(s) found")
        print(f"⚠️  {total_warnings} warning(s) detected")
        return 1


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate PhenoSDK architecture boundaries")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", "-r", action="store_true", help="Generate full report")
    args = parser.parse_args()

    # Build dependency graph
    print("Building dependency graph...")
    try:
        import sys
        import os
        # Add src to path
        sys.path.insert(0, os.path.join(os.getcwd(), "src"))
        graph = build_graph("pheno")
    except Exception as e:
        print(f"Error building graph: {e}")
        return 1

    if args.report:
        return generate_report(graph)

    # Quick validation
    layer_violations = validate_layer_dependencies(graph)
    forbidden_violations = validate_forbidden_patterns(graph)

    if layer_violations or forbidden_violations:
        print_layer_violations(layer_violations)
        print_forbidden_violations(forbidden_violations)
        print(f"\n❌ Total violations: {len(layer_violations) + len(forbidden_violations)}")
        return 1

    print("✅ All architecture boundaries validated successfully!")

    if args.verbose:
        circular_deps = check_circular_dependencies(graph)
        complexity_violations = check_module_complexity(graph)
        print_circular_dependencies(circular_deps)
        print_complexity_violations(complexity_violations, max_fanout=25)

    return 0


if __name__ == "__main__":
    sys.exit(main())
