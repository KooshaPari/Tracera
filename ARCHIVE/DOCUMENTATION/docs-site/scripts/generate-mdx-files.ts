#!/usr/bin/env bun
/**
 * MDX Documentation Generator for TraceRTM
 *
 * This script generates comprehensive MDX documentation files based on the DOCS_STRUCTURE.
 * It recursively walks the structure and creates properly formatted MDX files with:
 * - YAML frontmatter
 * - Structured content sections
 * - Topic-specific examples and code blocks
 * - Best practices and references
 *
 * Usage: bun run scripts/generate-mdx-files.ts
 */

import { mkdir, writeFile } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

// Import the docs structure
const DOCS_STRUCTURE = {
  'getting-started': {
    title: 'Getting Started',
    description: 'Get up and running with TraceRTM in minutes',
    path: '00-getting-started',
    icon: 'Rocket',
    children: {
      'installation': { title: 'Installation', path: '01-installation' },
      'quick-start': { title: 'Quick Start', path: '02-quick-start' },
      'system-requirements': { title: 'System Requirements', path: '03-system-requirements' },
      'core-concepts': { title: 'Core Concepts', path: '04-core-concepts' },
      'first-project': { title: 'First Project', path: '05-first-project' },
      'basic-workflow': { title: 'Basic Workflow', path: '06-basic-workflow' },
      'faq': { title: 'FAQ', path: '07-faq' },
    },
  },
  'wiki': {
    title: 'Wiki',
    description: 'Knowledge base and guides',
    path: '01-wiki',
    icon: 'BookOpen',
    children: {
      'concepts': {
        title: 'Concepts',
        path: '01-concepts',
        children: {
          'traceability': { title: 'Traceability', path: '01-traceability' },
          'workflows': { title: 'Workflows', path: '02-workflows' },
          'artifacts': { title: 'Artifacts', path: '03-artifacts' },
          'relationships': { title: 'Relationships', path: '04-relationships' },
          'metadata': { title: 'Metadata', path: '05-metadata' },
          'versioning': { title: 'Versioning', path: '06-versioning' },
          'compliance': { title: 'Compliance', path: '07-compliance' },
        },
      },
      'guides': {
        title: 'Guides',
        path: '02-guides',
        children: {
          'cli-guide': { title: 'CLI Guide', path: '01-cli-guide' },
          'web-ui-guide': { title: 'Web UI Guide', path: '02-web-ui-guide' },
          'troubleshooting': { title: 'Troubleshooting', path: '03-troubleshooting' },
          'performance-tuning': { title: 'Performance Tuning', path: '04-performance-tuning' },
          'security': { title: 'Security', path: '05-security' },
          'migration-guide': { title: 'Migration Guide', path: '06-migration-guide' },
        },
      },
    },
  },
  'api-reference': {
    title: 'API Reference',
    description: 'Complete API documentation',
    path: '02-api-reference',
    icon: 'Zap',
    children: {
      'authentication': { title: 'Authentication', path: '01-authentication' },
      'rest-api': { title: 'REST API', path: '02-rest-api' },
      'cli': { title: 'CLI', path: '03-cli' },
    },
  },
  'development': {
    title: 'Development',
    description: 'Internal development guides',
    path: '03-development',
    icon: 'Wrench',
    children: {
      'architecture': { title: 'Architecture', path: '01-architecture' },
      'setup': { title: 'Setup', path: '02-setup' },
      'contributing': { title: 'Contributing', path: '03-contributing' },
      'internals': { title: 'Internals', path: '04-internals' },
    },
  },
  'changelog': {
    title: 'Changelog',
    description: 'Version history and updates',
    path: '04-changelog',
    icon: 'RotateCcw',
    children: {
      'v1-0-0': { title: 'v1.0.0', path: '01-v1-0-0' },
      'v0-9-0': { title: 'v0.9.0', path: '02-v0-9-0' },
      'v0-8-0': { title: 'v0.8.0', path: '03-v0-8-0' },
    },
  },
}

// Base directory for docs
const DOCS_BASE_DIR = join(process.cwd(), 'content', 'docs')

// Content templates for different page types
const contentTemplates = {
  installation: (title: string) => `
## Overview

Learn how to install TraceRTM on your system. TraceRTM supports multiple installation methods to fit your workflow.

## Prerequisites

Before installing TraceRTM, ensure you have:

- Node.js 18.x or later
- Bun 1.0+ or npm 9+
- Git 2.x or later
- PostgreSQL 15+ (for local development)

## Installation Methods

### Using Bun (Recommended)

\`\`\`bash
# Install TraceRTM CLI globally
bun install -g @tracertm/cli

# Verify installation
tracertm --version
\`\`\`

### Using npm

\`\`\`bash
# Install TraceRTM CLI globally
npm install -g @tracertm/cli

# Verify installation
tracertm --version
\`\`\`

### From Source

\`\`\`bash
# Clone the repository
git clone https://github.com/tracertm/tracertm.git
cd tracertm

# Install dependencies
bun install

# Build the project
bun run build

# Link globally
bun link
\`\`\`

## Post-Installation

After installing TraceRTM, initialize your first project:

\`\`\`bash
# Create a new TraceRTM project
tracertm init my-project
cd my-project

# Start the development server
tracertm dev
\`\`\`

## Troubleshooting

### Permission Issues

If you encounter permission errors during installation:

\`\`\`bash
# On macOS/Linux, use sudo
sudo bun install -g @tracertm/cli
\`\`\`

### Version Conflicts

To update to the latest version:

\`\`\`bash
# Using Bun
bun update -g @tracertm/cli

# Using npm
npm update -g @tracertm/cli
\`\`\`

## Next Steps

- [Quick Start Guide](/docs/getting-started/quick-start)
- [System Requirements](/docs/getting-started/system-requirements)
- [First Project](/docs/getting-started/first-project)
`,

  quickStart: (title: string) => `
## Welcome to TraceRTM

This quick start guide will walk you through creating your first TraceRTM project in under 5 minutes.

## Step 1: Create a New Project

\`\`\`bash
# Initialize a new TraceRTM project
tracertm init my-first-project

# Navigate to the project directory
cd my-first-project
\`\`\`

## Step 2: Explore the Project Structure

Your new project includes:

\`\`\`
my-first-project/
├── .tracertm/          # TraceRTM configuration
├── artifacts/          # Project artifacts
├── requirements/       # Requirements documents
├── tests/             # Test specifications
└── tracertm.config.ts # Configuration file
\`\`\`

## Step 3: Create Your First Requirement

\`\`\`bash
# Create a new requirement
tracertm create requirement "User Authentication"

# View the requirement
tracertm show requirements
\`\`\`

## Step 4: Add Traceability Links

\`\`\`bash
# Create a test case linked to the requirement
tracertm create test "Login Test" --links req-001

# View the traceability matrix
tracertm matrix
\`\`\`

## Step 5: Start the Web UI

\`\`\`bash
# Launch the web interface
tracertm dev

# Open http://localhost:3000 in your browser
\`\`\`

## What's Next?

Now that you've created your first project, explore:

- [Core Concepts](/docs/getting-started/core-concepts) - Understand key TraceRTM concepts
- [Basic Workflow](/docs/getting-started/basic-workflow) - Learn the development workflow
- [CLI Guide](/docs/wiki/guides/cli-guide) - Master the CLI commands

## Example Project

Here's a complete example of a simple project workflow:

\`\`\`bash
# Create requirements
tracertm create requirement "REQ-001: User can log in"
tracertm create requirement "REQ-002: User can log out"

# Create test cases
tracertm create test "TC-001: Verify login" --links REQ-001
tracertm create test "TC-002: Verify logout" --links REQ-002

# Generate traceability report
tracertm report traceability --format html

# View the relationship graph
tracertm graph
\`\`\`
`,

  concepts: (title: string) => `
## Overview

Understanding the core concepts of ${title} is essential for effective use of TraceRTM.

## What is ${title}?

${title} is a fundamental concept in TraceRTM that enables comprehensive requirement and artifact management.

## Key Principles

### Principle 1: Clear Definition

Every ${title.toLowerCase()} must be clearly defined with:
- Unique identifier
- Descriptive name
- Detailed description
- Metadata attributes

### Principle 2: Traceability

All elements maintain bidirectional traceability:
- Parent-child relationships
- Cross-references
- Impact analysis

### Principle 3: Version Control

Changes are tracked with:
- Version history
- Change logs
- Audit trails

## Use Cases

### Use Case 1: Basic Implementation

\`\`\`typescript
import { TraceRTM } from '@tracertm/core'

const tracertm = new TraceRTM({
  project: 'my-project',
  workspace: './workspace'
})

// Create an artifact
await tracertm.create({
  type: '${title.toLowerCase()}',
  name: 'Example ${title}',
  metadata: {
    priority: 'high',
    status: 'active'
  }
})
\`\`\`

### Use Case 2: Advanced Usage

\`\`\`typescript
// Query with filters
const results = await tracertm.query({
  type: '${title.toLowerCase()}',
  filters: {
    status: 'active',
    priority: ['high', 'critical']
  }
})

// Establish relationships
await tracertm.link({
  source: 'REQ-001',
  target: 'TC-001',
  type: 'tests'
})
\`\`\`

## Best Practices

1. **Naming Conventions**: Use clear, descriptive names
2. **Metadata**: Add comprehensive metadata for filtering
3. **Relationships**: Establish links early and maintain them
4. **Documentation**: Keep descriptions up-to-date

## Common Patterns

### Pattern 1: Hierarchical Structure

\`\`\`
Parent ${title}
├── Child ${title} 1
│   ├── Grandchild 1.1
│   └── Grandchild 1.2
└── Child ${title} 2
    └── Grandchild 2.1
\`\`\`

### Pattern 2: Cross-Functional Links

\`\`\`
Requirement ←→ Design ←→ Implementation ←→ Test
\`\`\`

## References

- [${title} API Reference](/docs/api-reference)
- [Best Practices Guide](/docs/wiki/guides)
- [Examples](/docs/examples)
`,

  api: (title: string) => `
## Overview

Complete API reference for ${title}.

## Authentication

All API requests require authentication using JWT tokens:

\`\`\`typescript
const response = await fetch('https://api.tracertm.com/v1/${title.toLowerCase()}', {
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
  }
})
\`\`\`

## Endpoints

### GET /${title.toLowerCase()}

Retrieve all ${title.toLowerCase()} resources.

**Request:**

\`\`\`bash
curl -X GET https://api.tracertm.com/v1/${title.toLowerCase()} \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
\`\`\`

**Response:**

\`\`\`json
{
  "data": [
    {
      "id": "123",
      "type": "${title.toLowerCase()}",
      "attributes": {
        "name": "Example ${title}",
        "created_at": "2025-01-01T00:00:00Z"
      }
    }
  ],
  "meta": {
    "total": 1,
    "page": 1
  }
}
\`\`\`

### POST /${title.toLowerCase()}

Create a new ${title.toLowerCase()} resource.

**Request:**

\`\`\`bash
curl -X POST https://api.tracertm.com/v1/${title.toLowerCase()} \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "New ${title}",
    "description": "Description here"
  }'
\`\`\`

**Response:**

\`\`\`json
{
  "data": {
    "id": "124",
    "type": "${title.toLowerCase()}",
    "attributes": {
      "name": "New ${title}",
      "description": "Description here",
      "created_at": "2025-01-01T00:00:00Z"
    }
  }
}
\`\`\`

### GET /${title.toLowerCase()}/:id

Retrieve a specific ${title.toLowerCase()} by ID.

**Request:**

\`\`\`bash
curl -X GET https://api.tracertm.com/v1/${title.toLowerCase()}/123 \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
\`\`\`

### PUT /${title.toLowerCase()}/:id

Update a ${title.toLowerCase()} resource.

**Request:**

\`\`\`bash
curl -X PUT https://api.tracertm.com/v1/${title.toLowerCase()}/123 \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Updated ${title}",
    "description": "Updated description"
  }'
\`\`\`

### DELETE /${title.toLowerCase()}/:id

Delete a ${title.toLowerCase()} resource.

**Request:**

\`\`\`bash
curl -X DELETE https://api.tracertm.com/v1/${title.toLowerCase()}/123 \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
\`\`\`

## Query Parameters

### Filtering

\`\`\`bash
GET /${title.toLowerCase()}?filter[status]=active&filter[priority]=high
\`\`\`

### Sorting

\`\`\`bash
GET /${title.toLowerCase()}?sort=-created_at,name
\`\`\`

### Pagination

\`\`\`bash
GET /${title.toLowerCase()}?page[number]=2&page[size]=50
\`\`\`

## Error Responses

### 400 Bad Request

\`\`\`json
{
  "errors": [
    {
      "status": "400",
      "title": "Bad Request",
      "detail": "Invalid request parameters"
    }
  ]
}
\`\`\`

### 401 Unauthorized

\`\`\`json
{
  "errors": [
    {
      "status": "401",
      "title": "Unauthorized",
      "detail": "Invalid or expired token"
    }
  ]
}
\`\`\`

### 404 Not Found

\`\`\`json
{
  "errors": [
    {
      "status": "404",
      "title": "Not Found",
      "detail": "Resource not found"
    }
  ]
}
\`\`\`

## Rate Limiting

API requests are limited to:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated requests

Rate limit headers:
\`\`\`
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
\`\`\`

## SDKs

### TypeScript/JavaScript

\`\`\`typescript
import { TraceRTMClient } from '@tracertm/sdk'

const client = new TraceRTMClient({
  apiKey: 'YOUR_API_KEY'
})

const resources = await client.${title.toLowerCase()}.list()
\`\`\`

### Python

\`\`\`python
from tracertm import TraceRTMClient

client = TraceRTMClient(api_key='YOUR_API_KEY')
resources = client.${title.toLowerCase()}.list()
\`\`\`
`,

  guide: (title: string) => `
## Overview

This comprehensive guide covers everything you need to know about ${title}.

## Introduction

${title} is an essential aspect of working with TraceRTM effectively.

## Getting Started

### Prerequisites

Before following this guide, ensure you have:
- TraceRTM installed and configured
- Basic understanding of TraceRTM concepts
- Access to a TraceRTM workspace

### Initial Setup

\`\`\`bash
# Initialize your workspace
tracertm init

# Configure settings
tracertm config set ${title.toLowerCase().replace(/\s+/g, '.')} true
\`\`\`

## Core Workflows

### Workflow 1: Basic Usage

\`\`\`bash
# Step 1: Prepare your environment
tracertm workspace create

# Step 2: Execute the workflow
tracertm ${title.toLowerCase().replace(/\s+/g, '-')} start

# Step 3: Verify results
tracertm ${title.toLowerCase().replace(/\s+/g, '-')} status
\`\`\`

### Workflow 2: Advanced Usage

\`\`\`typescript
import { TraceRTM } from '@tracertm/core'

const tracertm = new TraceRTM()

// Configure advanced options
await tracertm.configure({
  ${title.toLowerCase().replace(/\s+/g, '_')}: {
    enabled: true,
    options: {
      mode: 'advanced',
      optimization: 'performance'
    }
  }
})

// Execute workflow
const result = await tracertm.execute('${title.toLowerCase().replace(/\s+/g, '-')}')
console.log(result)
\`\`\`

## Common Tasks

### Task 1: Configuration

Configure ${title.toLowerCase()} settings:

\`\`\`yaml
# tracertm.config.yml
${title.toLowerCase().replace(/\s+/g, '_')}:
  enabled: true
  mode: production
  options:
    - optimization: high
    - caching: enabled
    - logging: verbose
\`\`\`

### Task 2: Monitoring

Monitor ${title.toLowerCase()} performance:

\`\`\`bash
# View real-time metrics
tracertm monitor ${title.toLowerCase().replace(/\s+/g, '-')}

# Generate performance report
tracertm report performance --component ${title.toLowerCase().replace(/\s+/g, '-')}
\`\`\`

## Best Practices

1. **Plan Ahead**: Design your ${title.toLowerCase()} strategy before implementation
2. **Automate**: Use scripts and CI/CD for repetitive tasks
3. **Monitor**: Regularly check performance and status
4. **Document**: Keep detailed records of configurations and changes
5. **Test**: Validate changes in a test environment first

## Troubleshooting

### Common Issues

#### Issue 1: Configuration Errors

**Symptoms:**
- Error messages during startup
- Unexpected behavior

**Solution:**
\`\`\`bash
# Verify configuration
tracertm config validate

# Reset to defaults
tracertm config reset ${title.toLowerCase().replace(/\s+/g, '-')}
\`\`\`

#### Issue 2: Performance Problems

**Symptoms:**
- Slow response times
- High resource usage

**Solution:**
\`\`\`bash
# Enable performance monitoring
tracertm monitor --verbose

# Optimize settings
tracertm optimize ${title.toLowerCase().replace(/\s+/g, '-')}
\`\`\`

## Advanced Topics

### Custom Integrations

\`\`\`typescript
import { Plugin } from '@tracertm/core'

class Custom${title.replace(/\s+/g, '')}Plugin extends Plugin {
  async initialize() {
    // Custom initialization logic
  }

  async execute() {
    // Custom execution logic
  }
}

// Register plugin
tracertm.registerPlugin(new Custom${title.replace(/\s+/g, '')}Plugin())
\`\`\`

### Performance Optimization

\`\`\`typescript
// Configure caching
tracertm.cache.configure({
  ${title.toLowerCase().replace(/\s+/g, '_')}: {
    ttl: 3600,
    maxSize: 100
  }
})

// Enable batch processing
tracertm.batch.configure({
  size: 100,
  interval: 1000
})
\`\`\`

## Examples

### Example 1: Complete Implementation

\`\`\`typescript
import { TraceRTM } from '@tracertm/core'

async function implement${title.replace(/\s+/g, '')}() {
  const tracertm = new TraceRTM({
    workspace: './workspace',
    config: {
      ${title.toLowerCase().replace(/\s+/g, '_')}: {
        enabled: true
      }
    }
  })

  // Initialize
  await tracertm.initialize()

  // Execute workflow
  const result = await tracertm.execute('${title.toLowerCase().replace(/\s+/g, '-')}', {
    verbose: true,
    dryRun: false
  })

  // Process results
  console.log('Completed:', result.summary)

  return result
}

implement${title.replace(/\s+/g, '')}().catch(console.error)
\`\`\`

### Example 2: Integration with CI/CD

\`\`\`yaml
# .github/workflows/${title.toLowerCase().replace(/\s+/g, '-')}.yml
name: ${title}

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ${title.toLowerCase().replace(/\s+/g, '-')}:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Install TraceRTM
        run: bun install -g @tracertm/cli

      - name: Run ${title}
        run: tracertm ${title.toLowerCase().replace(/\s+/g, '-')} --ci
\`\`\`

## Resources

- [API Reference](/docs/api-reference)
- [CLI Commands](/docs/api-reference/cli)
- [Best Practices](/docs/wiki/guides)
- [Examples Repository](https://github.com/tracertm/examples)
`,

  changelog: (title: string) => `
## ${title}

Release date: January 2025

## Highlights

This release includes significant improvements, new features, and bug fixes.

## New Features

### Feature 1: Enhanced Traceability

- Improved relationship visualization
- Faster graph traversal algorithms
- Support for custom relationship types

\`\`\`typescript
// New relationship API
tracertm.relationships.create({
  source: 'REQ-001',
  target: 'TC-001',
  type: 'custom-validates',
  metadata: {
    confidence: 0.95
  }
})
\`\`\`

### Feature 2: Advanced Querying

- GraphQL API support
- Complex filter expressions
- Aggregation functions

\`\`\`typescript
// GraphQL query example
const query = \`
  query GetRequirements {
    requirements(
      where: { status: { eq: "active" } }
      orderBy: { priority: DESC }
    ) {
      id
      title
      linkedTests {
        id
        status
      }
    }
  }
\`
\`\`\`

### Feature 3: Real-time Collaboration

- Live updates across sessions
- Conflict resolution
- Activity notifications

## Improvements

### Performance

- 40% faster query execution
- Reduced memory footprint by 25%
- Optimized graph algorithms

### User Experience

- Redesigned UI with improved navigation
- Dark mode support
- Customizable dashboards

### Developer Experience

- Enhanced TypeScript types
- Better error messages
- Improved CLI output

## Breaking Changes

### API Changes

The following API endpoints have been updated:

\`\`\`typescript
// Before
tracertm.create({ type: 'requirement', data: {...} })

// After
tracertm.requirements.create({...})
\`\`\`

### Configuration Format

Updated configuration format for better clarity:

\`\`\`yaml
# Before
tracertm:
  db: postgres://...

# After
tracertm:
  database:
    type: postgres
    url: postgres://...
\`\`\`

## Migration Guide

### Step 1: Update Dependencies

\`\`\`bash
bun update @tracertm/cli @tracertm/core
\`\`\`

### Step 2: Update Configuration

\`\`\`bash
# Run migration tool
tracertm migrate config --from v0.9.0 --to v1.0.0
\`\`\`

### Step 3: Update Code

\`\`\`bash
# Run code migration tool
tracertm migrate code --version v1.0.0
\`\`\`

## Bug Fixes

- Fixed memory leak in graph traversal (#123)
- Resolved race condition in concurrent updates (#145)
- Fixed incorrect relationship deletion (#167)
- Corrected timezone handling in timestamps (#189)
- Fixed validation errors for special characters (#201)

## Deprecations

The following features are deprecated and will be removed in v2.0.0:

- \`tracertm.legacy.create()\` - Use \`tracertm.requirements.create()\`
- \`--old-format\` CLI flag - Use \`--format json\`
- \`TRACERTM_LEGACY_MODE\` env variable - No replacement needed

## Known Issues

- Graph visualization may be slow for projects with >10,000 nodes
- Real-time updates have a ~500ms delay on slow connections
- Export to PDF may not preserve custom fonts

## Contributors

Thank you to all contributors who made this release possible:

- @contributor1
- @contributor2
- @contributor3

## Full Changelog

View the complete changelog on [GitHub](https://github.com/tracertm/tracertm/releases/tag/${title.toLowerCase()})
`,

  default: (title: string) => `
## Overview

Welcome to the ${title} documentation.

## Introduction

This page provides comprehensive information about ${title} in TraceRTM.

## Key Features

- Feature 1: Comprehensive functionality
- Feature 2: Easy to use interface
- Feature 3: Powerful capabilities
- Feature 4: Extensible architecture

## Getting Started

To get started with ${title}:

\`\`\`bash
# Initialize
tracertm init

# Configure ${title.toLowerCase()}
tracertm config set ${title.toLowerCase().replace(/\s+/g, '.')} enabled
\`\`\`

## Usage

### Basic Usage

\`\`\`typescript
import { TraceRTM } from '@tracertm/core'

const tracertm = new TraceRTM()

// Use ${title} functionality
const result = await tracertm.${title.toLowerCase().replace(/\s+/g, '')}()
\`\`\`

### Advanced Usage

\`\`\`typescript
// Configure advanced options
const config = {
  ${title.toLowerCase().replace(/\s+/g, '_')}: {
    enabled: true,
    options: {
      mode: 'advanced'
    }
  }
}

const tracertm = new TraceRTM(config)
\`\`\`

## Configuration

Configure ${title} in your \`tracertm.config.ts\`:

\`\`\`typescript
export default {
  ${title.toLowerCase().replace(/\s+/g, '_')}: {
    enabled: true,
    settings: {
      // Your settings here
    }
  }
}
\`\`\`

## Examples

### Example 1: Basic Implementation

\`\`\`typescript
// Example code
const example = await tracertm.${title.toLowerCase().replace(/\s+/g, '')}({
  option1: 'value1',
  option2: 'value2'
})
\`\`\`

### Example 2: Advanced Implementation

\`\`\`typescript
// Advanced example
const advanced = await tracertm.${title.toLowerCase().replace(/\s+/g, '')}({
  option1: 'value1',
  option2: 'value2',
  advanced: {
    feature1: true,
    feature2: false
  }
})
\`\`\`

## Best Practices

1. **Plan First**: Always plan your implementation before coding
2. **Test Thoroughly**: Write comprehensive tests
3. **Document**: Keep documentation up-to-date
4. **Monitor**: Use monitoring and logging
5. **Optimize**: Profile and optimize performance

## Troubleshooting

### Common Issues

#### Issue 1

**Problem:** Description of the problem

**Solution:**
\`\`\`bash
# Solution command
tracertm fix issue-1
\`\`\`

#### Issue 2

**Problem:** Description of another problem

**Solution:**
\`\`\`bash
# Solution command
tracertm fix issue-2
\`\`\`

## API Reference

For detailed API documentation, see:
- [API Overview](/docs/api-reference)
- [REST API](/docs/api-reference/rest-api)
- [CLI Reference](/docs/api-reference/cli)

## Related Topics

- [Getting Started](/docs/getting-started)
- [Core Concepts](/docs/getting-started/core-concepts)
- [Guides](/docs/wiki/guides)
`,
}

/**
 * Determines the appropriate content template based on the page slug and title
 */
function getContentTemplate(slug: string[], title: string): string {
  const slugStr = slug.join('/')

  // Check for specific page types
  if (slugStr.includes('installation')) {
    return contentTemplates.installation(title)
  }
  if (slugStr.includes('quick-start')) {
    return contentTemplates.quickStart(title)
  }
  if (slugStr.includes('changelog') || slugStr.includes('v1-0-0') || slugStr.includes('v0-')) {
    return contentTemplates.changelog(title)
  }
  if (slugStr.includes('api-reference')) {
    return contentTemplates.api(title)
  }
  if (slugStr.includes('guide')) {
    return contentTemplates.guide(title)
  }
  if (slugStr.includes('concepts') || slugStr.includes('wiki')) {
    return contentTemplates.concepts(title)
  }

  return contentTemplates.default(title)
}

/**
 * Generates MDX content with frontmatter and body
 */
function generateMDXContent(title: string, description: string | undefined, slug: string[]): string {
  const desc = description || `Documentation for ${title}`
  const content = getContentTemplate(slug, title)

  return `---
title: "${title}"
description: "${desc}"
---

# ${title}
${content}
`
}

/**
 * Recursively processes the structure and generates MDX files
 */
async function processStructure(
  structure: any,
  basePath: string[],
  parentPath: string = ''
): Promise<{ total: number; created: number }> {
  let stats = { total: 0, created: 0 }

  for (const [key, value] of Object.entries(structure)) {
    if (typeof value !== 'object' || !value) continue

    const item = value as any
    const currentPath = item.path ? item.path : key
    const fullPath = parentPath ? join(parentPath, currentPath) : currentPath
    const currentSlug = [...basePath, key]

    // Create directory
    const dirPath = join(DOCS_BASE_DIR, fullPath)
    await mkdir(dirPath, { recursive: true })

    // Generate MDX file
    const mdxPath = join(dirPath, 'index.mdx')
    stats.total++

    if (!existsSync(mdxPath)) {
      const content = generateMDXContent(
        item.title || key,
        item.description,
        currentSlug
      )
      await writeFile(mdxPath, content, 'utf-8')
      stats.created++
      console.log(`✓ Created: ${fullPath}/index.mdx`)
    } else {
      console.log(`○ Exists: ${fullPath}/index.mdx`)
    }

    // Process children recursively
    if (item.children) {
      const childStats = await processStructure(item.children, currentSlug, fullPath)
      stats.total += childStats.total
      stats.created += childStats.created
    }
  }

  return stats
}

/**
 * Main execution function
 */
async function main() {
  console.log('🚀 TraceRTM Documentation Generator\n')
  console.log('Base directory:', DOCS_BASE_DIR)
  console.log('Starting MDX file generation...\n')

  const startTime = Date.now()

  try {
    // Ensure base directory exists
    await mkdir(DOCS_BASE_DIR, { recursive: true })

    // Process the entire structure
    const stats = await processStructure(DOCS_STRUCTURE, [])

    const duration = ((Date.now() - startTime) / 1000).toFixed(2)

    console.log('\n✨ Generation complete!')
    console.log(`\n📊 Statistics:`)
    console.log(`   Total pages: ${stats.total}`)
    console.log(`   Created: ${stats.created}`)
    console.log(`   Already existed: ${stats.total - stats.created}`)
    console.log(`   Duration: ${duration}s`)
    console.log(`\n✅ All MDX files are ready!`)
  } catch (error) {
    console.error('\n❌ Error generating MDX files:', error)
    process.exit(1)
  }
}

// Run the script
main()
