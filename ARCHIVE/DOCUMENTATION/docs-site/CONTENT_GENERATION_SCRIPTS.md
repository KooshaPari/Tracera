# Content Generation Scripts

This document describes scripts and tools to help automate content generation from the codebase.

## API Endpoint Extractor

### Purpose
Extract all API endpoints from `src/tracertm/api/main.py` and generate documentation templates.

### Usage
```bash
python scripts/extract-api-endpoints.py > api-endpoints.json
```

### Output Format
```json
{
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/v1/projects",
      "function": "list_projects",
      "summary": "List all projects",
      "parameters": [],
      "responses": {
        "200": "List of projects"
      }
    }
  ]
}
```

## Content Template Generator

### Purpose
Generate MDX file templates from the documentation structure.

### Usage
```bash
python scripts/generate-content-templates.py --section api-reference
```

## Code Example Extractor

### Purpose
Extract code examples from test files.

### Usage
```bash
python scripts/extract-code-examples.py --test-file tests/unit/api/test_api_comprehensive.py
```

## Link Validator

### Purpose
Validate all internal links in documentation.

### Usage
```bash
python scripts/validate-links.py
```

## Placeholder Finder

### Purpose
Find all pages with placeholder content.

### Usage
```bash
python scripts/find-placeholders.py
```
