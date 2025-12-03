#\!/bin/bash

create_page() {
  local dir=$1
  local title=$2
  
  if [ \! -f "$dir/index.mdx" ]; then
    mkdir -p "$dir"
    cat > "$dir/index.mdx" << CONTENT
---
title: $title
description: API documentation for $title
---

# $title

This page contains API documentation for **$title**.

## Overview

This section covers the $title API endpoints and usage.

## Getting Started

To use the $title API:

1. Authenticate with your API key
2. Review the endpoint documentation
3. Try the examples
4. Integrate into your application

## Key Endpoints

- Base URL: \`https://api.tracertm.com/v1\`
- Authentication: Bearer token in Authorization header
- Response Format: JSON

## Error Handling

All API responses include appropriate HTTP status codes and error messages.

## Rate Limiting

API requests are rate-limited to 1000 requests per hour per API key.

## Need Help?

- Check the [API Reference](/docs/api-reference/)
- Browse [Examples](/docs/wiki/examples/)
- Contact support

---

**Last Updated**: $(date +%Y-%m-%d)
CONTENT
    echo "✅ Created: $dir/index.mdx"
  fi
}

# API Reference - Authentication
create_page "02-api-reference/01-authentication" "Authentication"
create_page "02-api-reference/01-authentication/01-api-keys" "API Keys"
create_page "02-api-reference/01-authentication/02-oauth" "OAuth"
create_page "02-api-reference/01-authentication/03-jwt" "JWT"

# API Reference - REST API
create_page "02-api-reference/02-rest-api" "REST API"
create_page "02-api-reference/02-rest-api/01-projects" "Projects"
create_page "02-api-reference/02-rest-api/02-items" "Items"
create_page "02-api-reference/02-rest-api/03-links" "Links"
create_page "02-api-reference/02-rest-api/04-workflows" "Workflows"
create_page "02-api-reference/02-rest-api/05-search" "Search"
create_page "02-api-reference/02-rest-api/06-batch-operations" "Batch Operations"
create_page "02-api-reference/02-rest-api/07-webhooks" "Webhooks"
create_page "02-api-reference/02-rest-api/08-rate-limiting" "Rate Limiting"
create_page "02-api-reference/02-rest-api/09-pagination" "Pagination"
create_page "02-api-reference/02-rest-api/10-filtering" "Filtering"
create_page "02-api-reference/02-rest-api/11-sorting" "Sorting"
create_page "02-api-reference/02-rest-api/12-errors" "Errors"
create_page "02-api-reference/02-rest-api/13-versioning" "Versioning"
create_page "02-api-reference/02-rest-api/14-deprecations" "Deprecations"

# API Reference - CLI
create_page "02-api-reference/03-cli" "CLI"
create_page "02-api-reference/03-cli/01-installation" "Installation"
create_page "02-api-reference/03-cli/02-configuration" "Configuration"
create_page "02-api-reference/03-cli/03-commands" "Commands"
create_page "02-api-reference/03-cli/04-scripting" "Scripting"
create_page "02-api-reference/03-cli/05-plugins" "Plugins"
create_page "02-api-reference/03-cli/06-troubleshooting" "Troubleshooting"
create_page "02-api-reference/03-cli/07-examples" "Examples"

# API Reference - SDKs
create_page "02-api-reference/04-sdks" "SDKs"

# Python SDK
create_page "02-api-reference/04-sdks/01-python" "Python SDK"
create_page "02-api-reference/04-sdks/01-python/01-installation" "Installation"
create_page "02-api-reference/04-sdks/01-python/02-quickstart" "Quick Start"
create_page "02-api-reference/04-sdks/01-python/03-api-reference" "API Reference"
create_page "02-api-reference/04-sdks/01-python/04-examples" "Examples"
create_page "02-api-reference/04-sdks/01-python/05-async" "Async"
create_page "02-api-reference/04-sdks/01-python/06-testing" "Testing"

# JavaScript SDK
create_page "02-api-reference/04-sdks/02-javascript" "JavaScript SDK"
create_page "02-api-reference/04-sdks/02-javascript/01-installation" "Installation"
create_page "02-api-reference/04-sdks/02-javascript/02-quickstart" "Quick Start"
create_page "02-api-reference/04-sdks/02-javascript/03-api-reference" "API Reference"
create_page "02-api-reference/04-sdks/02-javascript/04-examples" "Examples"
create_page "02-api-reference/04-sdks/02-javascript/05-async" "Async"
create_page "02-api-reference/04-sdks/02-javascript/06-testing" "Testing"

# Go SDK
create_page "02-api-reference/04-sdks/03-go" "Go SDK"
create_page "02-api-reference/04-sdks/03-go/01-installation" "Installation"
create_page "02-api-reference/04-sdks/03-go/02-quickstart" "Quick Start"
create_page "02-api-reference/04-sdks/03-go/03-api-reference" "API Reference"
create_page "02-api-reference/04-sdks/03-go/04-examples" "Examples"
create_page "02-api-reference/04-sdks/03-go/05-concurrency" "Concurrency"
create_page "02-api-reference/04-sdks/03-go/06-testing" "Testing"

# API Reference index
create_page "02-api-reference" "API Reference"

echo ""
echo "✅ API Reference pages created\!"
