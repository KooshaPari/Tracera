# Quick Start: OpenAPI Documentation

## Overview

TraceRTM now has complete auto-generated API documentation from OpenAPI 3.1.0 spec.

## Quick Commands

```bash
# Navigate to docs-site
cd docs-site

# Regenerate API docs from OpenAPI spec
bun run api:generate

# Start dev server to view docs
bun run dev

# Build for production
bun run build
```

## View Documentation

After starting dev server (`bun run dev`):

- **API Landing**: http://localhost:3000/docs/api
- **REST API**: http://localhost:3000/docs/api/rest-api
- **Authentication**: http://localhost:3000/docs/api/authentication
- **Webhooks**: http://localhost:3000/docs/api/webhooks
- **Schemas**: http://localhost:3000/docs/api/schemas

## File Locations

```
OpenAPI Spec:
  /frontend/apps/web/public/specs/openapi.json

Generator Script:
  /scripts/generate-api-docs.ts

Generated Docs:
  /content/docs/api/
  ├── index.mdx (landing page)
  ├── authentication.mdx
  ├── webhooks.mdx
  ├── rest-api/
  │   ├── index.mdx
  │   ├── health.mdx
  │   ├── items.mdx
  │   ├── links.mdx
  │   └── analysis.mdx
  └── schemas/
      └── (10 schema files)
```

## What Was Generated

✅ 18 MDX documentation files
✅ REST API reference (5 endpoint groups)
✅ 10 schema definitions
✅ Authentication guide (JWT, API Keys, OAuth)
✅ Webhooks integration guide
✅ Code examples in 4 languages (cURL, JS, Python, Go)
✅ Navigation metadata
✅ Package.json script

## Workflow

### After Updating OpenAPI Spec

1. Edit: `/frontend/apps/web/public/specs/openapi.json`
2. Run: `bun run api:generate`
3. Review: Generated files in `/content/docs/api/`
4. Commit: Changes to git

### Adding New Endpoints

1. Add endpoint to OpenAPI spec
2. Add schema definitions if needed
3. Run: `bun run api:generate`
4. Update navigation in `meta.json` if needed

## Features

- ✅ Auto-generates from OpenAPI 3.1.0
- ✅ Multi-language code examples
- ✅ Complete schema reference
- ✅ Authentication & webhooks guides
- ✅ Fumadocs integration
- ✅ One-command regeneration

## Documentation Structure

**Auto-Generated:**
- REST API endpoints (from OpenAPI paths)
- Schemas (from OpenAPI components.schemas)
- Overview page (from OpenAPI info + servers)

**Manually Created:**
- API landing page
- Authentication guide
- Webhooks guide

## Support Files

- `API_DOCUMENTATION_GUIDE.md` - Complete usage guide
- `OPENAPI_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `QUICK_START_API_DOCS.md` - This file

## Current Coverage

**Endpoints:**
- Health check
- Items (list, get)
- Links (list)
- Analysis (impact, cycles, shortest path)

**Schemas:**
- 10 response/request schemas
- All with examples and property tables

**Authentication:**
- JWT Bearer tokens
- API Keys
- OAuth 2.0

## Next Steps

To expand documentation:

1. **Add more endpoints** to OpenAPI spec
2. **Define additional schemas**
3. **Run generator**: `bun run api:generate`
4. **View results**: `bun run dev`

That's it! The documentation auto-updates from the OpenAPI spec.
