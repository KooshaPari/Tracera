#\!/bin/bash

# Function to create an index.mdx file
create_page() {
  local dir=$1
  local title=$2
  
  if [ \! -f "$dir/index.mdx" ]; then
    mkdir -p "$dir"
    cat > "$dir/index.mdx" << CONTENT
---
title: $title
description: Documentation for $title
---

# $title

This page contains documentation for **$title**.

## Overview

This section covers the key aspects of $title in TraceRTM.

## Getting Started

To get started with $title:

1. Review the concepts and fundamentals
2. Follow the step-by-step guides
3. Explore practical examples
4. Refer to the API reference for detailed information

## Key Topics

- Fundamentals and concepts
- Configuration and setup
- Best practices
- Common use cases
- Troubleshooting

## Need Help?

- Check the [FAQ](/docs/getting-started/faq/)
- Browse related documentation
- Contact support

---

**Last Updated**: $(date +%Y-%m-%d)
CONTENT
    echo "✅ Created: $dir/index.mdx"
  fi
}

# Getting Started pages
create_page "00-getting-started/01-installation" "Installation"
create_page "00-getting-started/02-quick-start" "Quick Start"
create_page "00-getting-started/03-core-concepts" "Core Concepts"
create_page "00-getting-started/04-first-project" "First Project"
create_page "00-getting-started/05-faq" "FAQ"

# Wiki - Concepts
create_page "01-wiki/01-concepts" "Concepts"
create_page "01-wiki/01-concepts/01-traceability" "Traceability"
create_page "01-wiki/01-concepts/02-workflows" "Workflows"
create_page "01-wiki/01-concepts/03-artifacts" "Artifacts"
create_page "01-wiki/01-concepts/04-relationships" "Relationships"
create_page "01-wiki/01-concepts/05-metadata" "Metadata"
create_page "01-wiki/01-concepts/06-versioning" "Versioning"
create_page "01-wiki/01-concepts/07-compliance" "Compliance"

# Wiki - Guides
create_page "01-wiki/02-guides" "Guides"
create_page "01-wiki/02-guides/01-cli-guide" "CLI Guide"
create_page "01-wiki/02-guides/02-web-ui-guide" "Web UI Guide"
create_page "01-wiki/02-guides/03-troubleshooting" "Troubleshooting"
create_page "01-wiki/02-guides/04-performance-tuning" "Performance Tuning"
create_page "01-wiki/02-guides/05-security" "Security"
create_page "01-wiki/02-guides/06-migration-guide" "Migration Guide"
create_page "01-wiki/02-guides/07-integration-patterns" "Integration Patterns"

# Wiki - Examples
create_page "01-wiki/03-examples" "Examples"
create_page "01-wiki/03-examples/01-basic-workflow" "Basic Workflow"
create_page "01-wiki/03-examples/02-advanced-queries" "Advanced Queries"
create_page "01-wiki/03-examples/03-integrations" "Integrations"
create_page "01-wiki/03-examples/04-cicd-pipeline" "CI/CD Pipeline"
create_page "01-wiki/03-examples/05-multi-team-setup" "Multi-Team Setup"
create_page "01-wiki/03-examples/06-compliance-tracking" "Compliance Tracking"
create_page "01-wiki/03-examples/07-real-world-scenarios" "Real-World Scenarios"

# Wiki - Use Cases
create_page "01-wiki/04-use-cases" "Use Cases"
create_page "01-wiki/04-use-cases/01-software-development" "Software Development"
create_page "01-wiki/04-use-cases/02-manufacturing" "Manufacturing"
create_page "01-wiki/04-use-cases/03-healthcare" "Healthcare"
create_page "01-wiki/04-use-cases/04-finance" "Finance"

# Wiki index
create_page "01-wiki" "Wiki"

echo ""
echo "✅ Getting Started and Wiki pages created\!"
