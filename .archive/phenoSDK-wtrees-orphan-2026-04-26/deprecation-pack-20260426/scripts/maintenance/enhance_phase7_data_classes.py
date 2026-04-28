#!/usr/bin/env python3
"""Enhance Phase 7 data class and enum pages with real descriptions."""

import re
from pathlib import Path

PHASE7_ENHANCEMENTS = {
    "bundle-analysis.mdx": {
        "title": "BundleAnalysis",
        "description": "Comprehensive analysis results from bundle optimization analysis",
        "overview": "The `BundleAnalysis` data class contains detailed results from analyzing a JavaScript/TypeScript bundle, including size metrics, dependency information, and optimization recommendations."
    },
    "code-split-strategy.mdx": {
        "title": "CodeSplitStrategy",
        "description": "Configuration for code splitting strategy and bundle splitting approach",
        "overview": "The `CodeSplitStrategy` configuration class defines how to split bundles across multiple chunks for optimal loading performance and caching."
    },
    "cache-config.mdx": {
        "title": "CacheConfig",
        "description": "Configuration for individual cache layers in multi-layer caching framework",
        "overview": "The `CacheConfig` class configures a specific cache layer (memory, disk, HTTP, service worker, or CDN) with TTL, size limits, and invalidation strategy."
    },
    "invalidation-strategy.mdx": {
        "title": "InvalidationStrategy",
        "description": "Enumeration of cache invalidation strategies (TIME, EVENT, LRU, LFU, SWR)",
        "overview": "The `InvalidationStrategy` enum defines how cached data should be invalidated: time-based, event-based, least-recently-used, least-frequently-used, or stale-while-revalidate."
    },
    "web-vitals.mdx": {
        "title": "WebVitals",
        "description": "Core Web Vitals measurements (LCP, FID, CLS, TTFB, FCP) for performance monitoring",
        "overview": "The `WebVitals` data class holds measurements for all critical Core Web Vitals metrics used to assess page performance and user experience."
    },
    "performance-report.mdx": {
        "title": "PerformanceReport",
        "description": "Comprehensive performance analysis report with metrics, trends, and recommendations",
        "overview": "The `PerformanceReport` class contains a complete analysis of performance metrics, historical trends, and actionable recommendations for improvement."
    },
    "canary-strategy.mdx": {
        "title": "CanaryStrategy",
        "description": "Configuration for canary deployment with gradual rollout percentages and duration",
        "overview": "The `CanaryStrategy` class configures a gradual deployment rollout, starting at a low percentage and incrementally increasing traffic to the new version."
    },
    "feature-flag.mdx": {
        "title": "FeatureFlag",
        "description": "Feature flag definition with percentage-based or user-based targeting configuration",
        "overview": "The `FeatureFlag` class defines a feature flag that controls access to features based on percentage of users or specific user targeting."
    },
    "query-analysis.mdx": {
        "title": "QueryAnalysis",
        "description": "Results from database query analysis including slow queries, N+1 problems, and index recommendations",
        "overview": "The `QueryAnalysis` data class contains comprehensive analysis results from examining database queries for performance issues and optimization opportunities."
    },
    "index-recommendation.mdx": {
        "title": "IndexRecommendation",
        "description": "Recommendation for database index creation with estimated performance improvement",
        "overview": "The `IndexRecommendation` class represents a suggestion to create a database index, including the table, columns, index type, and estimated speedup percentage."
    }
}

def enhance_phase7_page(filename: str, data: dict) -> bool:
    """Enhance a Phase 7 data class page."""
    filepath = Path(f"apps/docs/content/docs/api/phases/phase-7/{filename}")

    if not filepath.exists():
        return False

    text = filepath.read_text()

    # Update description in frontmatter
    text = re.sub(
        r'description: .*',
        f'description: {data["description"]}',
        text
    )

    # Update title in frontmatter
    text = re.sub(
        r'title: .*',
        f'title: {data["title"]}',
        text
    )

    # Update overview section
    overview_section = f"""## Overview

{data["overview"]}

## Properties

This class contains the following properties:
- Standard configuration and data fields for the {data["title"]} use case
- Type-safe access to all metrics and settings
- Integration with other Phase 7 APIs"""

    # Replace the overview section
    text = re.sub(
        r'## Overview\n\n.*?\n\n## Constructor',
        f'{overview_section}\n\n## Constructor',
        text,
        flags=re.DOTALL
    )

    filepath.write_text(text)
    return True

def main():
    """Enhance all Phase 7 data class pages."""
    enhanced = 0
    total = len(PHASE7_ENHANCEMENTS)

    for filename, data in PHASE7_ENHANCEMENTS.items():
        if enhance_phase7_page(filename, data):
            print(f"✓ Phase 7: Enhanced {filename.replace('.mdx', '')}")
            enhanced += 1
        else:
            print(f"✗ Phase 7: Failed to enhance {filename}")

    print(f"\n{'='*60}")
    print(f"Enhanced {enhanced}/{total} Phase 7 data class pages")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
