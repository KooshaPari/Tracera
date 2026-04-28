#\!/bin/bash

# Create Getting Started structure
mkdir -p 00-getting-started

# Create Wiki structure
mkdir -p 01-wiki/01-concepts
mkdir -p 01-wiki/02-guides
mkdir -p 01-wiki/03-examples
mkdir -p 01-wiki/04-use-cases

# Create API Reference structure
mkdir -p 02-api-reference/01-authentication
mkdir -p 02-api-reference/02-rest-api
mkdir -p 02-api-reference/03-cli
mkdir -p 02-api-reference/04-sdks/01-python
mkdir -p 02-api-reference/04-sdks/02-javascript
mkdir -p 02-api-reference/04-sdks/03-go

# Create Development structure
mkdir -p 03-development/01-architecture
mkdir -p 03-development/02-setup
mkdir -p 03-development/03-contributing
mkdir -p 03-development/04-internals
mkdir -p 03-development/05-deployment

# Create Changelog structure
mkdir -p 04-changelog

echo "✅ Directory structure created successfully\!"
ls -la
