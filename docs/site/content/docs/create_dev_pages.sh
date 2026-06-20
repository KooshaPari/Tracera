#\!/bin/bash

create_page() {
  local dir=$1
  local title=$2
  
  if [ \! -f "$dir/index.mdx" ]; then
    mkdir -p "$dir"
    cat > "$dir/index.mdx" << CONTENT
---
title: $title
description: Development documentation for $title
---

# $title

This page contains development documentation for **$title**.

## Overview

This section covers the development aspects of $title in TraceRTM.

## Getting Started

To get started with $title development:

1. Review the architecture and design
2. Set up your development environment
3. Follow the contribution guidelines
4. Explore the codebase

## Key Topics

- Architecture and design patterns
- Setup and configuration
- Contributing guidelines
- Internal implementation details
- Deployment and scaling

## Development Resources

- Source code repository
- Issue tracker
- Pull request guidelines
- Code review process

## Need Help?

- Check the [Development Guide](/docs/development/)
- Review [Contributing Guidelines](/docs/development/contributing/)
- Contact the development team

---

**Last Updated**: $(date +%Y-%m-%d)
CONTENT
    echo "✅ Created: $dir/index.mdx"
  fi
}

# Development - Architecture
create_page "03-development/01-architecture" "Architecture"
create_page "03-development/01-architecture/01-system-design" "System Design"
create_page "03-development/01-architecture/02-data-flow" "Data Flow"
create_page "03-development/01-architecture/03-components" "Components"
create_page "03-development/01-architecture/04-database-schema" "Database Schema"
create_page "03-development/01-architecture/05-api-design" "API Design"
create_page "03-development/01-architecture/06-performance" "Performance"

# Development - Setup
create_page "03-development/02-setup" "Setup"
create_page "03-development/02-setup/01-prerequisites" "Prerequisites"
create_page "03-development/02-setup/02-local-development" "Local Development"
create_page "03-development/02-setup/03-docker-setup" "Docker Setup"
create_page "03-development/02-setup/04-database-setup" "Database Setup"
create_page "03-development/02-setup/05-environment-variables" "Environment Variables"
create_page "03-development/02-setup/06-first-run" "First Run"

# Development - Contributing
create_page "03-development/03-contributing" "Contributing"
create_page "03-development/03-contributing/01-code-style" "Code Style"
create_page "03-development/03-contributing/02-commit-messages" "Commit Messages"
create_page "03-development/03-contributing/03-pull-requests" "Pull Requests"
create_page "03-development/03-contributing/04-testing" "Testing"
create_page "03-development/03-contributing/05-documentation" "Documentation"
create_page "03-development/03-contributing/06-releases" "Releases"

# Development - Internals
create_page "03-development/04-internals" "Internals"
create_page "03-development/04-internals/01-backend-handlers" "Backend Handlers"
create_page "03-development/04-internals/02-middleware" "Middleware"
create_page "03-development/04-internals/03-database-queries" "Database Queries"
create_page "03-development/04-internals/04-search-engine" "Search Engine"
create_page "03-development/04-internals/05-event-system" "Event System"
create_page "03-development/04-internals/06-caching" "Caching"

# Development - Deployment
create_page "03-development/05-deployment" "Deployment"
create_page "03-development/05-deployment/01-docker-deployment" "Docker Deployment"
create_page "03-development/05-deployment/02-kubernetes" "Kubernetes"
create_page "03-development/05-deployment/03-cloud-platforms" "Cloud Platforms"
create_page "03-development/05-deployment/04-monitoring" "Monitoring"
create_page "03-development/05-deployment/05-scaling" "Scaling"

# Development index
create_page "03-development" "Development"

echo ""
echo "✅ Development pages created\!"
