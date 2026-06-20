# OpenAPI/Swagger Integration Guide

This document describes the OpenAPI/Swagger integration for TraceRTM's auto-generated API documentation.

## Overview

TraceRTM now has a complete API documentation system that automatically generates MDX files from an OpenAPI 3.1.0 specification. The documentation is integrated with Fumadocs and includes:

- Complete REST API reference
- Authentication guides
- Schema documentation
- Webhook integration guides
- Code examples in multiple languages (cURL, JavaScript, Python, Go)

## File Structure

```
docs-site/
├── content/docs/api/
│   ├── index.mdx                   # API documentation landing page
│   ├── authentication.mdx           # Authentication methods guide
│   ├── webhooks.mdx                # Webhook integration guide
│   ├── meta.json                   # Navigation metadata
│   ├── rest-api/
│   │   ├── index.mdx               # REST API overview
│   │   ├── health.mdx              # Health check endpoints
│   │   ├── items.mdx               # Items CRUD endpoints
│   │   ├── links.mdx               # Links management endpoints
│   │   ├── analysis.mdx            # Analysis endpoints
│   │   └── meta.json               # REST API navigation
│   └── schemas/
│       ├── healthresponse.mdx
│       ├── itemsummary.mdx
│       ├── itemlistresponse.mdx
│       ├── itemdetailresponse.mdx
│       ├── linksummary.mdx
│       ├── linklistresponse.mdx
│       ├── impactanalysisresponse.mdx
│       ├── cycledetectionresponse.mdx
│       ├── shortestpathresponse.mdx
│       ├── error.mdx
│       └── meta.json
│
├── scripts/
│   └── generate-api-docs.ts        # OpenAPI → MDX generator

frontend/apps/web/public/specs/
└── openapi.json                     # OpenAPI 3.1.0 specification
```

## OpenAPI Specification

The source OpenAPI specification is located at:
```
/frontend/apps/web/public/specs/openapi.json
```

### Current Coverage

The OpenAPI spec currently includes:

**Endpoints:**
- Health check (`/health`)
- Items API (`/api/v1/items`, `/api/v1/items/{item_id}`)
- Links API (`/api/v1/links`)
- Analysis API (impact, cycles, shortest path)

**Authentication:**
- JWT Bearer tokens
- API Key authentication

**Schemas:**
- HealthResponse
- ItemSummary, ItemListResponse, ItemDetailResponse
- LinkSummary, LinkListResponse
- ImpactAnalysisResponse
- CycleDetectionResponse
- ShortestPathResponse
- Error

## Generating Documentation

### Quick Start

```bash
# Navigate to docs-site directory
cd docs-site

# Generate API documentation from OpenAPI spec
bun run api:generate
```

This will:
1. Parse `/frontend/apps/web/public/specs/openapi.json`
2. Generate MDX files in `/content/docs/api/`
3. Create endpoint documentation organized by tag
4. Generate schema documentation with examples
5. Include code examples in 4 languages

### Manual Regeneration

If you update the OpenAPI spec, regenerate docs:

```bash
cd docs-site
bun run api:generate
```

## Generator Script

The generator script (`scripts/generate-api-docs.ts`) provides:

### Features

1. **Endpoint Documentation**
   - Organized by OpenAPI tags (Health, Items, Links, Analysis)
   - HTTP method badges
   - Parameter tables (query, path, header)
   - Request body schemas
   - Response examples
   - Multi-language code examples

2. **Schema Documentation**
   - Property tables with types and descriptions
   - Required field indicators
   - Example JSON payloads
   - Cross-references to other schemas

3. **Code Examples**
   - cURL commands
   - JavaScript (fetch API)
   - Python (requests library)
   - Go (net/http)

### Customization

To modify the generator:

```typescript
// scripts/generate-api-docs.ts

// Change output directory
const DOCS_OUTPUT_DIR = join(process.cwd(), 'content/docs/api');

// Modify code example generation
function generateCodeExamples(method: string, path: string, operation: Operation) {
  // Add new language or modify existing ones
}

// Customize formatting
function formatSchemaType(schema: Schema, spec: OpenAPISpec): string {
  // Modify type display
}
```

## Documentation Pages

### API Landing Page (`/docs/api/index.mdx`)

Features:
- Overview of API capabilities
- Quick start guide
- Links to major sections
- Authentication overview
- Core resources explanation
- API status and support information

### REST API Overview (`/docs/api/rest-api/index.mdx`)

Auto-generated content:
- Base URLs (local, staging, production)
- Authentication methods with examples
- Rate limiting information
- Error codes reference
- Pagination guide

### Resource Pages

Each resource (Health, Items, Links, Analysis) gets its own page with:
- Endpoint descriptions
- Parameter tables
- Code examples in 4 languages
- Request/response examples

### Authentication Guide (`/docs/api/authentication.mdx`)

Comprehensive guide covering:
- JWT Bearer tokens
- API keys (live vs test)
- OAuth 2.0 flows
- Security best practices
- Token rotation
- Error handling
- Rate limits per method

### Webhooks Guide (`/docs/api/webhooks.mdx`)

Complete webhook integration guide:
- Event types (item, link, project, analysis events)
- Event payload structure
- Signature verification (with code examples)
- Best practices (idempotency, async processing)
- Retry logic
- Testing with ngrok
- Monitoring and troubleshooting

### Schema Documentation (`/docs/api/schemas/*.mdx`)

Each schema includes:
- Property table with types
- Required field indicators
- Descriptions
- Example JSON payload

## Extending the Documentation

### Adding New Endpoints

1. **Update OpenAPI Spec**

Edit `/frontend/apps/web/public/specs/openapi.json`:

```json
{
  "paths": {
    "/api/v1/projects": {
      "get": {
        "tags": ["Projects"],
        "summary": "List Projects",
        "description": "Retrieve all projects",
        "operationId": "listProjects",
        "security": [{"bearerAuth": []}],
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {"$ref": "#/components/schemas/ProjectList"}
              }
            }
          }
        }
      }
    }
  }
}
```

2. **Add Schema Definition**

```json
{
  "components": {
    "schemas": {
      "Project": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
          "id": {"type": "string", "format": "uuid"},
          "name": {"type": "string"},
          "description": {"type": "string", "nullable": true}
        }
      }
    }
  }
}
```

3. **Regenerate Documentation**

```bash
cd docs-site
bun run api:generate
```

4. **Update Navigation**

Edit `/content/docs/api/rest-api/meta.json`:

```json
{
  "title": "REST API",
  "pages": [
    "index",
    "health",
    "items",
    "links",
    "projects",  // Add new page
    "analysis"
  ]
}
```

### Adding New Schemas

New schemas are automatically generated and added to `/content/docs/api/schemas/`.

Update `/content/docs/api/schemas/meta.json` to include in navigation:

```json
{
  "title": "Schemas",
  "pages": [
    "healthresponse",
    "project",  // Add new schema
    "itemsummary",
    // ...
  ]
}
```

## Navigation Structure

Navigation is controlled by `meta.json` files:

### API Section Navigation

`/content/docs/api/meta.json`:
```json
{
  "title": "API Documentation",
  "pages": [
    "index",           // Landing page
    "authentication",  // Auth guide
    "webhooks",       // Webhooks guide
    "rest-api",       // REST API section
    "schemas"         // Schemas section
  ]
}
```

### REST API Navigation

`/content/docs/api/rest-api/meta.json`:
```json
{
  "title": "REST API",
  "pages": [
    "index",    // Overview
    "health",   // Health endpoints
    "items",    // Items endpoints
    "links",    // Links endpoints
    "analysis"  // Analysis endpoints
  ]
}
```

## Best Practices

### OpenAPI Spec Maintenance

1. **Keep spec in sync with backend**
   - Update spec when adding endpoints
   - Include all parameters and schemas
   - Add examples for complex types

2. **Use descriptive tags**
   - Group related endpoints
   - Tags become section pages

3. **Include security schemes**
   - Document all auth methods
   - Specify per-endpoint requirements

4. **Provide examples**
   - Request examples
   - Response examples
   - Error examples

### Documentation Quality

1. **Clear descriptions**
   - Explain what each endpoint does
   - Document side effects
   - Include use cases

2. **Complete parameter documentation**
   - Type information
   - Required vs optional
   - Default values
   - Validation rules

3. **Error handling**
   - Document error responses
   - Include error codes
   - Provide troubleshooting tips

### Regeneration Workflow

1. **After backend changes**
   ```bash
   cd docs-site
   bun run api:generate
   ```

2. **Review generated files**
   - Check for completeness
   - Verify code examples
   - Test navigation

3. **Commit changes**
   ```bash
   git add content/docs/api/
   git commit -m "docs: update API documentation"
   ```

## Integration with Fumadocs

The generated documentation integrates seamlessly with Fumadocs:

1. **Source Configuration** (`lib/source.ts`)
   ```typescript
   export const apiDocs = loader({
     baseUrl: '/docs/api',
     rootDir: 'api',
     source: createMDXSource(docs, meta),
   });
   ```

2. **Navigation**
   - Automatic sidebar generation
   - Breadcrumbs
   - Search indexing

3. **Components**
   - Tabs (for code examples)
   - Cards
   - Callouts
   - Badges
   - Accordions

## Testing the Documentation

### Local Development

```bash
cd docs-site
bun run dev
```

Visit:
- http://localhost:3000/docs/api - API landing page
- http://localhost:3000/docs/api/rest-api - REST API overview
- http://localhost:3000/docs/api/authentication - Auth guide
- http://localhost:3000/docs/api/webhooks - Webhooks guide
- http://localhost:3000/docs/api/schemas - Schema reference

### Build Verification

```bash
cd docs-site
bun run build
```

## Future Enhancements

### Planned Improvements

1. **GraphQL Documentation**
   - Generate from GraphQL schema
   - Query/mutation examples
   - Subscription documentation

2. **SDK Documentation**
   - Auto-generate from OpenAPI
   - Language-specific guides
   - Installation instructions

3. **Interactive API Explorer**
   - Try API calls directly
   - Request/response viewer
   - Authentication testing

4. **Changelog Integration**
   - Version-specific docs
   - Migration guides
   - Deprecation notices

5. **Additional Content**
   - Rate limiting details
   - Pagination strategies
   - Filtering/sorting guides
   - Batch operations
   - Caching strategies

## Troubleshooting

### Generator Issues

**Problem:** Generator fails to parse OpenAPI spec

```bash
# Validate OpenAPI spec
npx @redocly/cli lint /frontend/apps/web/public/specs/openapi.json
```

**Problem:** Missing schemas or endpoints

- Check that all `$ref` references are valid
- Ensure schemas are defined in `components.schemas`
- Verify tags exist in `tags` array

### Navigation Issues

**Problem:** Pages not appearing in sidebar

- Check `meta.json` files
- Ensure page filenames match exactly
- Verify MDX frontmatter is valid

**Problem:** Broken links

- Use relative paths
- Reference correct schema names
- Check for typos in cross-references

### Build Errors

**Problem:** TypeScript errors in generated MDX

- Ensure MDX syntax is valid
- Check for unescaped characters
- Verify code blocks are properly closed

## Support

For questions or issues:

- **Documentation**: This guide
- **OpenAPI Spec**: `/frontend/apps/web/public/specs/openapi.json`
- **Generator Script**: `/scripts/generate-api-docs.ts`
- **Examples**: Check existing generated files in `/content/docs/api/`

## Summary

The OpenAPI/Swagger integration provides:

✅ Auto-generated API documentation from OpenAPI 3.1.0 spec
✅ Complete REST API reference with code examples
✅ Authentication and webhooks guides
✅ Schema documentation with examples
✅ Multi-language code samples (cURL, JS, Python, Go)
✅ Fumadocs integration with navigation
✅ Easy regeneration workflow
✅ Extensible generator script

To update documentation:
1. Edit OpenAPI spec
2. Run `bun run api:generate`
3. Review and commit changes
