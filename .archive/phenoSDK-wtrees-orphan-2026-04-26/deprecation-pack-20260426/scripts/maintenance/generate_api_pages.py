#!/usr/bin/env python3
"""
Batch generator for API reference pages.
Creates MDX files for all 105 PhenoSDK APIs based on phase documentation.
"""

import json
from pathlib import Path
from typing import Dict, List

# API mapping for all 105 APIs across 7 phases
APIS = {
    "phase-1": [
        {"name": "EnhancedDependencyAnalyzer", "file": "enhanced-dependency-analyzer.mdx", "desc": "Semantic link analysis and dependency tracking orchestrator"},
        {"name": "ModuleDependencyGraph", "file": "module-dependency-graph.mdx", "desc": "Dependency graph data structure and visualization"},
        {"name": "SemanticLink", "file": "semantic-link.mdx", "desc": "Individual semantic link between code elements"},
        {"name": "DependencyType", "file": "dependency-type.mdx", "desc": "Enumeration of dependency types (IMPORT, RUNTIME, LAZY)"},
        {"name": "DependencyTiming", "file": "dependency-timing.mdx", "desc": "Enumeration of dependency timing (IMPORT_TIME, RUNTIME, LAZY)"},
        {"name": "DependencyStrength", "file": "dependency-strength.mdx", "desc": "Enumeration of dependency strength (REQUIRED, OPTIONAL, SUGGESTED)"},
        {"name": "NextJsSemanticIntegrator", "file": "nextjs-semantic-integrator.mdx", "desc": "Integrates semantic linking with Next.js pages and routes"},
        {"name": "NextJsPageDependencies", "file": "nextjs-page-dependencies.mdx", "desc": "Page-level dependency tracking for Next.js applications"},
        {"name": "DeploymentDependencyChecklist", "file": "deployment-dependency-checklist.mdx", "desc": "Automated deployment validation checklist generation"},
        {"name": "MultiDimensionalTestAnalyzer", "file": "multidimensional-test-analyzer.mdx", "desc": "Multi-dimension test coverage analysis and tracking"},
        {"name": "DimensionalTestMatrix", "file": "dimensional-test-matrix.mdx", "desc": "Test coverage metrics across dimensions (unit, integration, e2e, perf)"},
        {"name": "CoverageMetric", "file": "coverage-metric.mdx", "desc": "Individual coverage metric with value and dimension"},
        {"name": "CoverageDimension", "file": "coverage-dimension.mdx", "desc": "Enumeration of test coverage dimensions"},
        {"name": "DocumentationQualityAnalyzer", "file": "documentation-quality-analyzer.mdx", "desc": "Analyzes documentation quality across multiple dimensions"},
        {"name": "DocumentationQualityMatrix", "file": "documentation-quality-matrix.mdx", "desc": "Quality metrics across completeness, clarity, currency, correctness"},
    ],
    "phase-2": [
        {"name": "DocumentationAlignmentAnalyzer", "file": "documentation-alignment-analyzer.mdx", "desc": "Multi-language documentation alignment and consistency tracking"},
        {"name": "DocumentationAlignmentMatrix", "file": "documentation-alignment-matrix.mdx", "desc": "Language coverage and parity metrics"},
        {"name": "LanguageType", "file": "language-type.mdx", "desc": "Enumeration of supported languages (EN, ES, FR, DE, JA, ZH, etc.)"},
        {"name": "IntegrationTracker", "file": "integration-tracker.mdx", "desc": "Tracks and catalogs all system integrations"},
        {"name": "IntegrationMatrix", "file": "integration-matrix.mdx", "desc": "Integration metrics and health scores"},
        {"name": "IntegrationPattern", "file": "integration-pattern.mdx", "desc": "Integration pattern definition and metadata"},
        {"name": "DeploymentDocumentationGenerator", "file": "deployment-documentation-generator.mdx", "desc": "Generates platform-specific deployment guides"},
        {"name": "DeploymentDocumentation", "file": "deployment-documentation.mdx", "desc": "Structured deployment guide with steps and configuration"},
        {"name": "DeploymentTarget", "file": "deployment-target.mdx", "desc": "Enumeration of deployment targets (AWS, GCP, Azure, K8s, Docker)"},
        {"name": "SecurityCompliance", "file": "security-compliance.mdx", "desc": "Compliance analysis and framework tracking"},
        {"name": "ComplianceMatrix", "file": "compliance-matrix.mdx", "desc": "Framework compliance metrics and audit trails"},
        {"name": "ComplianceFramework", "file": "compliance-framework.mdx", "desc": "Enumeration of compliance frameworks (GDPR, HIPAA, SOC2, PCI-DSS, CCPA)"},
        {"name": "LicenseTracker", "file": "license-tracker.mdx", "desc": "License scanning and attribution management"},
        {"name": "LicenseMatrix", "file": "license-matrix.mdx", "desc": "License type distribution and compatibility analysis"},
        {"name": "LicenseType", "file": "license-type.mdx", "desc": "Enumeration of license types (MIT, Apache2.0, GPL, Commercial, Proprietary)"},
    ],
    "phase-3": [
        {"name": "InteractiveDocumentationGenerator", "file": "interactive-documentation-generator.mdx", "desc": "Generates interactive documentation with live code execution"},
        {"name": "InteractiveDocumentation", "file": "interactive-documentation.mdx", "desc": "Interactive documentation with runnable code examples"},
        {"name": "ExecutionEnvironment", "file": "execution-environment.mdx", "desc": "Code execution environment configuration (Python, JavaScript, TypeScript, SQL)"},
        {"name": "AIDocumentationGenerator", "file": "ai-documentation-generator.mdx", "desc": "AI-powered documentation generation from code"},
        {"name": "GeneratedDocumentation", "file": "generated-documentation.mdx", "desc": "AI-generated documentation content with sections"},
        {"name": "DocumentationSection", "file": "documentation-section.mdx", "desc": "Individual documentation section with content"},
        {"name": "UsageAnalyticsTracker", "file": "usage-analytics-tracker.mdx", "desc": "Tracks API and feature usage patterns"},
        {"name": "UsageAnalyticsMatrix", "file": "usage-analytics-matrix.mdx", "desc": "Usage metrics and adoption statistics"},
        {"name": "UsagePattern", "file": "usage-pattern.mdx", "desc": "Individual usage pattern with frequency and trends"},
        {"name": "ArchitectureDiagramGenerator", "file": "architecture-diagram-generator.mdx", "desc": "Generates visual architecture diagrams (Mermaid, PlantUML, SVG)"},
        {"name": "ArchitectureDiagram", "file": "architecture-diagram.mdx", "desc": "Architecture diagram data and visualization"},
        {"name": "DiagramFormat", "file": "diagram-format.mdx", "desc": "Enumeration of diagram formats (MERMAID, PLANTUML, SVG)"},
        {"name": "VersionedDocumentationManager", "file": "versioned-documentation-manager.mdx", "desc": "Manages documentation across multiple versions"},
        {"name": "DocumentationVersion", "file": "documentation-version.mdx", "desc": "Specific documentation version with metadata"},
        {"name": "VersionMetadata", "file": "version-metadata.mdx", "desc": "Version information and release notes"},
    ],
    "phase-4": [
        {"name": "DocAsCodePipelineGenerator", "file": "doc-as-code-pipeline-generator.mdx", "desc": "Generates CI/CD pipelines for documentation"},
        {"name": "DocumentationPipeline", "file": "documentation-pipeline.mdx", "desc": "Documentation CI/CD pipeline configuration"},
        {"name": "CICDProvider", "file": "cicd-provider.mdx", "desc": "Enumeration of CI/CD providers (GITHUB_ACTIONS, GITLAB_CI, JENKINS, CIRCLECI)"},
        {"name": "PatternEcosystemManager", "file": "pattern-ecosystem-manager.mdx", "desc": "Manages pattern library and ecosystem"},
        {"name": "DocumentationPattern", "file": "documentation-pattern.mdx", "desc": "Reusable documentation pattern definition"},
        {"name": "PatternLibrary", "file": "pattern-library.mdx", "desc": "Pattern library collection and organization"},
        {"name": "SemanticSearchEngine", "file": "semantic-search-engine.mdx", "desc": "Semantic search for intelligent documentation discovery"},
        {"name": "SearchIndex", "file": "search-index.mdx", "desc": "Search index data structure"},
        {"name": "SearchResult", "file": "search-result.mdx", "desc": "Individual search result with relevance"},
        {"name": "SLAMonitor", "file": "sla-monitor.mdx", "desc": "Service level agreement monitoring and tracking"},
        {"name": "SLAMetrics", "file": "sla-metrics.mdx", "desc": "SLA compliance metrics and uptime"},
        {"name": "UptimeTracker", "file": "uptime-tracker.mdx", "desc": "Uptime tracking and incident management"},
        {"name": "FullStackObserver", "file": "fullstack-observer.mdx", "desc": "Full-stack observability across all layers"},
        {"name": "ObservabilityMetrics", "file": "observability-metrics.mdx", "desc": "Comprehensive observability metrics"},
        {"name": "TraceContext", "file": "trace-context.mdx", "desc": "Distributed trace context and correlation"},
    ],
    "phase-5": [
        {"name": "ProviderSwitchingOrchestrator", "file": "provider-switching-orchestrator.mdx", "desc": "Automates provider switching and migration"},
        {"name": "Provider", "file": "provider.mdx", "desc": "Cloud provider configuration and metrics"},
        {"name": "ProviderFamily", "file": "provider-family.mdx", "desc": "Enumeration of provider families (AWS, GCP, AZURE, VERCEL, HEROKU, DIGITALOCEAN)"},
        {"name": "MonorepoAnalyzer", "file": "monorepo-analyzer.mdx", "desc": "Analyzes monorepo structure and dependencies"},
        {"name": "Package", "file": "package.mdx", "desc": "Monorepo package definition and metadata"},
        {"name": "DependencyGraph", "file": "dependency-graph.mdx", "desc": "Package dependency graph visualization"},
        {"name": "IntegrationCatalogManager", "file": "integration-catalog-manager.mdx", "desc": "Manages integration discovery and catalog"},
        {"name": "Integration", "file": "integration.mdx", "desc": "Integration definition with documentation and setup"},
        {"name": "IntegrationCategory", "file": "integration-category.mdx", "desc": "Enumeration of integration categories (PAYMENTS, AUTH, DATABASE, HOSTING, etc.)"},
        {"name": "MultiEnvironmentDocGenerator", "file": "multi-environment-doc-generator.mdx", "desc": "Generates environment-specific documentation"},
        {"name": "EnvironmentConfig", "file": "environment-config.mdx", "desc": "Environment-specific configuration"},
        {"name": "EnvironmentType", "file": "environment-type.mdx", "desc": "Enumeration of environments (DEVELOPMENT, STAGING, PRODUCTION)"},
        {"name": "ProjectInitializer", "file": "project-initializer.mdx", "desc": "Creates new projects with sensible defaults"},
        {"name": "ProjectTemplate", "file": "project-template.mdx", "desc": "Project template definition and scaffolding"},
        {"name": "ProjectType", "file": "project-type.mdx", "desc": "Enumeration of project types (WEB, API, CLI, FULLSTACK, etc.)"},
    ],
    "phase-6": [
        {"name": "NextJsVersionUpgrader", "file": "nextjs-version-upgrader.mdx", "desc": "Automates Next.js version upgrades with breaking change detection"},
        {"name": "BreakingChange", "file": "breaking-change.mdx", "desc": "Breaking change definition and migration path"},
        {"name": "UpgradeStep", "file": "upgrade-step.mdx", "desc": "Individual upgrade step with instructions"},
        {"name": "React19Modernizer", "file": "react19-modernizer.mdx", "desc": "Modernizes code for React 19 and TypeScript 7"},
        {"name": "HookMigration", "file": "hook-migration.mdx", "desc": "Hook migration pattern and automation"},
        {"name": "ComponentPattern", "file": "component-pattern.mdx", "desc": "Modern React component pattern"},
        {"name": "MagicUIComponentCatalog", "file": "magic-ui-component-catalog.mdx", "desc": "Catalog of 50+ Magic UI components"},
        {"name": "ComponentTemplate", "file": "component-template.mdx", "desc": "Component template with variants"},
        {"name": "InteractionPattern", "file": "interaction-pattern.mdx", "desc": "UI interaction pattern definition"},
        {"name": "LiquidGlassThemeGenerator", "file": "liquid-glass-theme-generator.mdx", "desc": "Generates glassmorphic theme configurations"},
        {"name": "GlassComponent", "file": "glass-component.mdx", "desc": "Glassmorphic component definition"},
        {"name": "EffectConfiguration", "file": "effect-configuration.mdx", "desc": "Visual effect configuration (blur, refraction, overlay)"},
        {"name": "DocumentationUIGenerator", "file": "documentation-ui-generator.mdx", "desc": "Generates documentation UI with Fumadocs + Shadcn"},
        {"name": "DocLayout", "file": "doc-layout.mdx", "desc": "Documentation layout configuration"},
        {"name": "ComponentIntegration", "file": "component-integration.mdx", "desc": "Component integration with documentation"},
    ],
    "phase-7": [
        {"name": "BundleOptimizer", "file": "bundle-optimizer.mdx", "desc": "Bundle analysis and code splitting optimization", "created": True},
        {"name": "BundleAnalysis", "file": "bundle-analysis.mdx", "desc": "Bundle analysis results with optimization recommendations"},
        {"name": "CodeSplitStrategy", "file": "code-split-strategy.mdx", "desc": "Code splitting strategy configuration"},
        {"name": "CachingFramework", "file": "caching-framework.mdx", "desc": "Multi-layer caching system (memory, disk, HTTP, SW, CDN)", "created": True},
        {"name": "CacheConfig", "file": "cache-config.mdx", "desc": "Cache layer configuration"},
        {"name": "InvalidationStrategy", "file": "invalidation-strategy.mdx", "desc": "Enumeration of cache invalidation strategies (TIME, EVENT, LRU, LFU, SWR)"},
        {"name": "PerformanceMonitor", "file": "performance-monitor.mdx", "desc": "Web Vitals and performance metrics tracking", "created": True},
        {"name": "WebVitals", "file": "web-vitals.mdx", "desc": "Core Web Vitals data structure"},
        {"name": "PerformanceReport", "file": "performance-report.mdx", "desc": "Comprehensive performance analysis report"},
        {"name": "DeploymentOrchestrator", "file": "deployment-orchestrator.mdx", "desc": "Safe deployment with canary, blue-green, feature flags", "created": True},
        {"name": "CanaryStrategy", "file": "canary-strategy.mdx", "desc": "Canary deployment configuration"},
        {"name": "FeatureFlag", "file": "feature-flag.mdx", "desc": "Feature flag definition with control"},
        {"name": "DatabaseOptimizer", "file": "database-optimizer.mdx", "desc": "Query and schema optimization analysis", "created": True},
        {"name": "QueryAnalysis", "file": "query-analysis.mdx", "desc": "Query analysis results with issues"},
        {"name": "IndexRecommendation", "file": "index-recommendation.mdx", "desc": "Database index recommendation"},
    ],
}

# Template for main classes
MAIN_CLASS_TEMPLATE = '''---
title: {name}
description: {desc}
---

# {name}

**Module**: `pheno.documentation.{module}`
**Type**: {type}
**Stability**: Beta
**Since**: Phase {phase}

## Overview

{overview}

## Constructor

```python
class {name}:
    def __init__(self, repo_root: Path):
        """
        Initialize {name_lower}.

        Args:
            repo_root: Root path of the project
        """
```

## Core Methods

### method_name()

Brief description of method.

```python
def method_name(self, param: Type) -> ReturnType:
    """
    Method description.

    Args:
        param: Parameter description

    Returns:
        Return value description
    """
```

**Example**:
```python
instance = {name}(Path("."))
result = instance.method_name(param)
```

## Related APIs

- Related API 1
- Related API 2
- Related Guide

## Use Cases

### Use Case 1
```python
# Example code
```

### Use Case 2
```python
# Example code
```

## See Also

- [Phase {phase}: Documentation](/docs/phases/phase-{phase})
- [Related Guide](/docs/guides/guide-name)
'''

# Template for data classes/models
DATA_CLASS_TEMPLATE = '''---
title: {name}
description: {desc}
---

# {name}

**Module**: `pheno.documentation.{module}`
**Type**: {type}
**Stability**: Beta
**Since**: Phase {phase}

## Overview

Data structure representing {name_lower}.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| prop1 | str | Description |
| prop2 | int | Description |

## Example

```python
instance = {name}(
    prop1="value",
    prop2=123
)
```

## Related APIs

- Parent Class
- Related Data Class
- Usage Examples

## See Also

- [Phase {phase}: Documentation](/docs/phases/phase-{phase})
'''

# Template for enumerations
ENUM_TEMPLATE = '''---
title: {name}
description: {desc}
---

# {name}

**Module**: `pheno.documentation.{module}`
**Type**: Enumeration
**Stability**: Beta
**Since**: Phase {phase}

## Overview

Enumeration of {name_lower} options.

## Values

```python
class {name}(str, Enum):
    OPTION_1 = "option_1"
    OPTION_2 = "option_2"
    OPTION_3 = "option_3"
```

## Example

```python
value = {name}.OPTION_1
print(value.value)  # "option_1"
```

## Related APIs

- Classes that use this enum
- Alternative enumerations

## See Also

- [Phase {phase}: Documentation](/docs/phases/phase-{phase})
'''

def generate_page(api: Dict, phase: int, output_dir: Path) -> None:
    """Generate a single API reference page."""

    # Skip already created pages
    if api.get("created"):
        return

    name = api["name"]
    filename = api["file"]
    desc = api["desc"]

    # Determine if it's a main class, data class, or enum
    if "Enum" in name or name.endswith("Type"):
        template = ENUM_TEMPLATE
        api_type = "Enumeration"
    elif name.endswith(("Data", "Config", "Matrix", "Analysis", "Result", "Report", "Context")):
        template = DATA_CLASS_TEMPLATE
        api_type = "DataClass"
    else:
        template = MAIN_CLASS_TEMPLATE
        api_type = "Class"

    # Get module name from phase
    phase_modules = {
        1: "semantic_links",
        2: "language_alignment",
        3: "usage_analytics",
        4: "semantic_search",
        5: "provider_switching",
        6: "liquid_glass_theme",
        7: "bundle_optimization",
    }
    module = phase_modules.get(phase, f"phase_{phase}_module")

    # Generate content
    content = template.format(
        name=name,
        name_lower=name[0].lower() + name[1:],
        desc=desc,
        module=module,
        type=api_type,
        phase=phase,
        overview=f"The `{name}` class provides {desc.lower()}."
    )

    # Write file
    filepath = output_dir / filename
    filepath.write_text(content)
    print(f"✓ Created {filename}")

def main():
    """Generate all API reference pages."""

    base_dir = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/apps/docs/content/docs/api/phases")

    total_created = 0
    total_skipped = 0

    for phase, phase_key in enumerate([f"phase-{i}" for i in range(1, 8)], 1):
        phase_dir = base_dir / phase_key
        phase_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📝 Phase {phase}:")

        for api in APIS.get(phase_key, []):
            try:
                if api.get("created"):
                    print(f"⊘ {api['file']} (already created)")
                    total_skipped += 1
                else:
                    generate_page(api, phase, phase_dir)
                    total_created += 1
            except Exception as e:
                print(f"✗ Error creating {api['file']}: {e}")

    print(f"\n{'='*60}")
    print(f"Summary: Created {total_created} new pages, {total_skipped} already existing")
    print(f"Total: {total_created + total_skipped}/105 API reference pages")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
