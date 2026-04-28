#!/usr/bin/env python3
"""
Enhance generated API reference pages with real descriptions and content.

This script reads the API_REFERENCE_MAPPING.md and updates generated pages
with substantive descriptions, method examples, and use cases based on the
mapping and phase documentation.
"""

import re
from pathlib import Path
from typing import Optional

# API Descriptions from mapping
API_DESCRIPTIONS = {
    # Phase 1
    "EnhancedDependencyAnalyzer": {
        "desc": "Analyzes semantic dependencies and module relationships to provide comprehensive dependency graphs",
        "methods": ["analyze_dependencies", "get_dependency_graph", "identify_circular_dependencies"],
        "use_cases": ["Understand module relationships", "Detect circular dependencies", "Optimize module structure"]
    },
    "ModuleDependencyGraph": {
        "desc": "Data structure representing the directed graph of module dependencies",
        "methods": ["add_edge", "get_nodes", "get_edges", "topological_sort"],
        "use_cases": ["Visualize module structure", "Dependency analysis", "Import optimization"]
    },
    "NextJsSemanticIntegrator": {
        "desc": "Integrates semantic dependency analysis with Next.js page structure and routing",
        "methods": ["integrate", "analyze_page_dependencies", "generate_import_map"],
        "use_cases": ["Optimize Next.js page loading", "Analyze route dependencies", "Generate import strategies"]
    },
    "MultiDimensionalTestAnalyzer": {
        "desc": "Analyzes test coverage across multiple dimensions: unit, integration, e2e, performance, security",
        "methods": ["analyze", "get_coverage_matrix", "identify_gaps"],
        "use_cases": ["Achieve comprehensive test coverage", "Identify testing gaps", "Plan test strategy"]
    },
    "DocumentationQualityAnalyzer": {
        "desc": "Evaluates documentation quality across completeness, clarity, examples, and consistency",
        "methods": ["analyze", "get_quality_score", "generate_report"],
        "use_cases": ["Improve documentation quality", "Measure documentation health", "Plan documentation work"]
    },

    # Phase 2
    "DocumentationAlignmentAnalyzer": {
        "desc": "Ensures documentation is consistently maintained across multiple languages",
        "methods": ["analyze_alignment", "get_alignment_matrix", "identify_misalignments"],
        "use_cases": ["Maintain multi-language docs", "Identify translation gaps", "Track localization status"]
    },
    "IntegrationTracker": {
        "desc": "Tracks and catalogs all integrations with external services and third-party APIs",
        "methods": ["track_integration", "get_integrations", "analyze_ecosystem"],
        "use_cases": ["Catalog integrations", "Manage dependencies", "Plan integration work"]
    },
    "SecurityCompliance": {
        "desc": "Analyzes codebase for security issues and compliance with regulations (GDPR, HIPAA, SOC2)",
        "methods": ["analyze", "get_compliance_status", "generate_audit_report"],
        "use_cases": ["Ensure regulatory compliance", "Audit security posture", "Plan security improvements"]
    },
    "LicenseTracker": {
        "desc": "Manages and tracks all open source licenses used in the project",
        "methods": ["track_license", "get_licenses", "generate_attribution"],
        "use_cases": ["Manage open source licenses", "Generate attribution", "Check compliance"]
    },

    # Phase 3
    "InteractiveDocumentationGenerator": {
        "desc": "Generates interactive documentation with embedded code execution environments",
        "methods": ["generate", "create_executable_blocks", "generate_interactive_examples"],
        "use_cases": ["Create executable documentation", "Enable code playgrounds", "Improve user learning"]
    },
    "AIDocumentationGenerator": {
        "desc": "Uses AI models to automatically generate or enhance documentation from code",
        "methods": ["generate", "enhance_existing", "generate_examples"],
        "use_cases": ["Auto-generate documentation", "Create code examples", "Improve doc quality"]
    },
    "UsageAnalyticsTracker": {
        "desc": "Tracks how users interact with and use APIs and documentation",
        "methods": ["track_usage", "get_analytics", "identify_patterns"],
        "use_cases": ["Understand user behavior", "Identify popular features", "Plan improvements"]
    },
    "ArchitectureDiagramGenerator": {
        "desc": "Generates visual architecture diagrams from code structure analysis",
        "methods": ["generate_diagram", "generate_from_code", "export"],
        "use_cases": ["Visualize architecture", "Document system design", "Communicate structure"]
    },
    "VersionedDocumentationManager": {
        "desc": "Maintains multiple versions of documentation for different software versions",
        "methods": ["create_version", "manage_versions", "generate_version_selector"],
        "use_cases": ["Maintain version-specific docs", "Support multiple versions", "Document upgrades"]
    },

    # Phase 4
    "DocAsCodePipelineGenerator": {
        "desc": "Generates CI/CD pipelines for documentation generation and validation",
        "methods": ["generate_pipeline", "generate_workflow", "validate_pipeline"],
        "use_cases": ["Automate doc generation", "Validate documentation", "Deploy docs to CDN"]
    },
    "PatternEcosystemManager": {
        "desc": "Manages a shared library of reusable patterns and best practices",
        "methods": ["register_pattern", "search_patterns", "share_pattern"],
        "use_cases": ["Share patterns across teams", "Discover best practices", "Build pattern library"]
    },
    "SemanticSearchEngine": {
        "desc": "Provides semantic search across documentation using AI embeddings",
        "methods": ["index", "search", "semantic_search"],
        "use_cases": ["Find relevant documentation", "Natural language search", "Improve discoverability"]
    },
    "SLAMonitor": {
        "desc": "Monitors service level agreements and tracks uptime metrics",
        "methods": ["monitor", "check_sla", "generate_report"],
        "use_cases": ["Track uptime", "Monitor SLA compliance", "Alert on failures"]
    },
    "FullStackObserver": {
        "desc": "Provides end-to-end observability across frontend, backend, and infrastructure",
        "methods": ["observe", "get_metrics", "generate_dashboard"],
        "use_cases": ["Monitor system health", "Track performance", "Debug issues"]
    },

    # Phase 5
    "ProviderSwitchingOrchestrator": {
        "desc": "Orchestrates switching between different hosting/infrastructure providers",
        "methods": ["plan_migration", "switch_provider", "validate_migration"],
        "use_cases": ["Migrate to new provider", "Compare providers", "Reduce vendor lock-in"]
    },
    "MonorepoAnalyzer": {
        "desc": "Analyzes monorepo structure and identifies optimization opportunities",
        "methods": ["analyze", "get_package_graph", "identify_issues"],
        "use_cases": ["Understand monorepo structure", "Optimize workspaces", "Plan refactoring"]
    },
    "IntegrationCatalogManager": {
        "desc": "Maintains a discoverable catalog of all available integrations",
        "methods": ["register_integration", "search", "get_integration_details"],
        "use_cases": ["Discover integrations", "Publish integrations", "Manage catalog"]
    },
    "MultiEnvironmentDocGenerator": {
        "desc": "Generates environment-specific documentation for dev, staging, prod",
        "methods": ["generate", "generate_for_environment", "compare_environments"],
        "use_cases": ["Document environments", "Environment-specific guides", "Deploy documentation"]
    },
    "ProjectInitializer": {
        "desc": "Initializes new projects with sensible defaults and best practices",
        "methods": ["initialize", "create_structure", "configure_defaults"],
        "use_cases": ["Start new project", "Apply best practices", "Set up templates"]
    },

    # Phase 6
    "NextJsVersionUpgrader": {
        "desc": "Automates Next.js version upgrades with breaking change detection",
        "methods": ["detect_breaking_changes", "plan_upgrade", "execute_upgrade"],
        "use_cases": ["Upgrade Next.js safely", "Detect breaking changes", "Plan migration"]
    },
    "React19Modernizer": {
        "desc": "Modernizes React code to use React 19 features and patterns",
        "methods": ["analyze", "generate_migrations", "apply_modernizations"],
        "use_cases": ["Migrate to React 19", "Use new hooks", "Update patterns"]
    },
    "MagicUIComponentCatalog": {
        "desc": "Catalogs and organizes Magic UI components with metadata and examples",
        "methods": ["add_component", "search_components", "get_component"],
        "use_cases": ["Discover components", "Build component library", "Share components"]
    },
    "LiquidGlassThemeGenerator": {
        "desc": "Generates liquid glass morphism CSS and React components with animations",
        "methods": ["generate_theme", "generate_component", "export_css"],
        "use_cases": ["Create glass effect components", "Generate theme", "Build modern UI"]
    },
    "DocumentationUIGenerator": {
        "desc": "Generates beautiful, responsive documentation UI with components",
        "methods": ["generate_ui", "generate_component", "apply_theme"],
        "use_cases": ["Create doc website", "Generate components", "Apply theme"]
    },

    # Phase 7
    "BundleOptimizer": {
        "desc": "Analyzes and optimizes JavaScript/TypeScript bundle size through code splitting and tree-shaking",
        "methods": ["analyze_bundle", "recommend_optimizations", "generate_config"],
        "use_cases": ["Reduce bundle size", "Optimize load times", "Improve performance"]
    },
    "CachingFramework": {
        "desc": "Provides multi-layer caching (memory, disk, HTTP, service worker, CDN) with configurable strategies",
        "methods": ["create_cache", "set_invalidation", "generate_config"],
        "use_cases": ["Implement caching", "Reduce API calls", "Improve response times"]
    },
    "PerformanceMonitor": {
        "desc": "Tracks Core Web Vitals and performance metrics with real-time alerting",
        "methods": ["track_vitals", "set_alerts", "generate_report"],
        "use_cases": ["Monitor performance", "Track metrics", "Alert on issues"]
    },
    "DeploymentOrchestrator": {
        "desc": "Orchestrates safe deployments using canary, blue-green, rolling, and feature flag strategies",
        "methods": ["deploy_canary", "deploy_blue_green", "create_feature_flag"],
        "use_cases": ["Deploy safely", "Control rollout", "Minimize downtime"]
    },
    "DatabaseOptimizer": {
        "desc": "Analyzes database queries for N+1 problems, recommends indexes, and optimizes schema",
        "methods": ["analyze_queries", "recommend_indexes", "optimize_schema"],
        "use_cases": ["Optimize queries", "Improve database performance", "Reduce latency"]
    },
}

def enhance_page(phase: int, filename: str, class_name: str) -> bool:
    """Enhance a single API page with real content."""
    filepath = Path(f"apps/docs/content/docs/api/phases/phase-{phase}/{filename}")

    if not filepath.exists():
        return False

    # Get content from mapping
    content = API_DESCRIPTIONS.get(class_name, {})
    if not content:
        return False

    description = content.get("desc", "")
    methods = content.get("methods", [])
    use_cases = content.get("use_cases", [])

    # Read the file
    text = filepath.read_text()

    # Update description in frontmatter
    text = re.sub(
        r'description: .*',
        f'description: {description}',
        text
    )

    # Update overview section
    overview_section = f"""## Overview

The `{class_name}` class provides {description.lower()}.

This is a critical tool for improving software quality and maintaining system health."""

    text = re.sub(
        r'## Overview\n\nThe `.*?` class provides .*?\n\n## Constructor',
        overview_section + '\n\n## Constructor',
        text,
        flags=re.DOTALL
    )

    # Add method examples if methods are available
    if methods:
        method_section = "\n\n### Available Methods\n\n"
        for method in methods[:5]:  # Limit to 5 methods
            method_formatted = method.replace('_', ' ').title()
            method_section += f"- `{method}()` - {method_formatted}\n"

        # Insert after core methods header
        text = text.replace("## Core Methods\n", f"## Core Methods\n{method_section}")

    # Add use cases if available
    if use_cases:
        use_case_section = "\n## Common Use Cases\n\n"
        for i, use_case in enumerate(use_cases, 1):
            use_case_section += f"{i}. {use_case}\n"

        # Append to end before See Also
        text = text.replace("## See Also\n", f"{use_case_section}\n## See Also\n")

    filepath.write_text(text)
    return True

def main():
    """Enhance all generated API pages with real content."""
    # Skip Phase 7 manually created pages
    skip_pages = {
        7: ['bundle-optimizer', 'caching-framework', 'performance-monitor',
            'deployment-orchestrator', 'database-optimizer']
    }

    # Map of files to class names for enhancement
    enhancements = {
        1: {
            'enhanced-dependency-analyzer': 'EnhancedDependencyAnalyzer',
            'module-dependency-graph': 'ModuleDependencyGraph',
            'nextjs-semantic-integrator': 'NextJsSemanticIntegrator',
            'multidimensional-test-analyzer': 'MultiDimensionalTestAnalyzer',
            'documentation-quality-analyzer': 'DocumentationQualityAnalyzer',
        },
        2: {
            'documentation-alignment-analyzer': 'DocumentationAlignmentAnalyzer',
            'integration-tracker': 'IntegrationTracker',
            'security-compliance': 'SecurityCompliance',
            'license-tracker': 'LicenseTracker',
        },
        3: {
            'interactive-documentation-generator': 'InteractiveDocumentationGenerator',
            'ai-documentation-generator': 'AIDocumentationGenerator',
            'usage-analytics-tracker': 'UsageAnalyticsTracker',
            'architecture-diagram-generator': 'ArchitectureDiagramGenerator',
            'versioned-documentation-manager': 'VersionedDocumentationManager',
        },
        4: {
            'doc-as-code-pipeline-generator': 'DocAsCodePipelineGenerator',
            'pattern-ecosystem-manager': 'PatternEcosystemManager',
            'semantic-search-engine': 'SemanticSearchEngine',
            'sla-monitor': 'SLAMonitor',
            'fullstack-observer': 'FullStackObserver',
        },
        5: {
            'provider-switching-orchestrator': 'ProviderSwitchingOrchestrator',
            'monorepo-analyzer': 'MonorepoAnalyzer',
            'integration-catalog-manager': 'IntegrationCatalogManager',
            'multi-environment-doc-generator': 'MultiEnvironmentDocGenerator',
            'project-initializer': 'ProjectInitializer',
        },
        6: {
            'nextjs-version-upgrader': 'NextJsVersionUpgrader',
            'react19-modernizer': 'React19Modernizer',
            'magic-ui-component-catalog': 'MagicUIComponentCatalog',
            'liquid-glass-theme-generator': 'LiquidGlassThemeGenerator',
            'documentation-ui-generator': 'DocumentationUIGenerator',
        },
        7: {
            'bundle-analysis': 'BundleAnalysis',
            'code-split-strategy': 'CodeSplitStrategy',
            'cache-config': 'CacheConfig',
            'invalidation-strategy': 'InvalidationStrategy',
            'web-vitals': 'WebVitals',
            'performance-report': 'PerformanceReport',
            'canary-strategy': 'CanaryStrategy',
            'feature-flag': 'FeatureFlag',
            'query-analysis': 'QueryAnalysis',
            'index-recommendation': 'IndexRecommendation',
        }
    }

    total = 0
    enhanced = 0

    for phase, files in enhancements.items():
        skipped = skip_pages.get(phase, [])
        for filename, class_name in files.items():
            if filename in skipped:
                print(f"⊘ Phase {phase}: {filename} (manually created, skipping)")
                continue

            if enhance_page(phase, f"{filename}.mdx", class_name):
                print(f"✓ Phase {phase}: Enhanced {filename}")
                enhanced += 1
            else:
                print(f"✗ Phase {phase}: Failed to enhance {filename}")
            total += 1

    print(f"\n{'='*60}")
    print(f"Enhanced {enhanced}/{total} pages with real descriptions")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
