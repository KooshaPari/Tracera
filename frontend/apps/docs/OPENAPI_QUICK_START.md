# OpenAPI Integration - Quick Start Guide

## Overview

Phase 4 implements automatic API documentation generation from the FastAPI backend's OpenAPI specification.

## What's Implemented

### ✅ Working Now

1. **OpenAPI Spec Generation**
   - Fetches spec from backend
   - Converts JSON → YAML
   - Saves to docs content directory

2. **Build Integration**
   - Automatic generation before builds
   - Manual generation command available

3. **API Documentation Structure**
   - API reference homepage
   - Authentication documentation
   - Code samples in 4 languages

## Quick Start

### 1. Start the Backend

```bash
# From project root
cd /path/to/trace
uvicorn tracertm.api.main:app --reload
```

Verify it's running:

```bash
curl http://localhost:4000/openapi.json | head
```

### 2. Generate OpenAPI Spec

```bash
# From docs directory
cd frontend/apps/docs

# Generate the spec
bun run openapi
```

Expected output:

```
🚀 OpenAPI Spec Generator
📡 Fetching OpenAPI spec from http://localhost:4000/openapi.json...
✅ Fetched OpenAPI 3.1.0 spec: TraceRTM API v1.0.0
   Endpoints: 184
🔄 Converting JSON to YAML...
✅ Converted to YAML (313096 bytes)
💾 Saving to .../content/docs/03-api-reference/openapi.yaml...
✅ OpenAPI spec saved successfully
```

### 3. View the Generated Spec

```bash
# View YAML file
cat content/docs/03-api-reference/openapi.yaml | head -50

# Check file size
ls -lh content/docs/03-api-reference/openapi.yaml
```

### 4. Build the Docs

```bash
# Automatic generation + build
bun run build
```

The `prebuild` script will automatically regenerate the OpenAPI spec before building.

## File Structure

```
frontend/apps/docs/
├── scripts/
│   └── generate-openapi.ts          # Generation script
├── content/docs/03-api-reference/
│   ├── index.mdx                    # API reference homepage
│   ├── 01-auth.mdx                  # Authentication docs
│   ├── meta.json                    # Navigation config
│   └── openapi.yaml                 # Generated OpenAPI spec ⚡
├── package.json                     # With prebuild script
└── PHASE_4_OPENAPI_INTEGRATION_SUMMARY.md
```

## Manual API Documentation

### Current Docs

- **API Reference**: `/docs/03-api-reference`
  - Overview and getting started
  - Authentication guide
  - Error handling
  - Rate limiting

- **Authentication**: `/docs/03-api-reference/01-auth`
  - Device OAuth 2.0 flow
  - Endpoint documentation
  - Code samples (TypeScript, Python, curl, Go)

### Adding New Endpoints

Create new MDX files in `content/docs/03-api-reference/`:

```mdx
---
title: Projects API
description: Manage projects and requirements
---

# Projects API

## Create Project

`POST /api/v1/projects`

Creates a new project.

**Request Body:**
\`\`\`json
{
"name": "My Project",
"description": "Project description"
}
\`\`\`

**Code Samples:**

<Tabs items={['TypeScript', 'Python', 'curl', 'Go']}>
  <Tab value="TypeScript">
    \`\`\`typescript
    const response = await fetch('http://localhost:4000/api/v1/projects', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: 'My Project',
        description: 'Project description'
      })
    });
    \`\`\`
  </Tab>
  <!-- Add other tabs -->
</Tabs>
```

## Available Commands

```bash
# Generate OpenAPI spec manually
bun run openapi

# Development server (needs module resolution fix)
bun run dev

# Build docs (includes prebuild)
bun run build

# Type checking
bun run typecheck

# Linting
bun run lint
```

## Accessing API Documentation

### Interactive Explorers

While the docs site is being fixed, use these alternatives:

1. **Swagger UI** (Interactive)

   ```
   http://localhost:4000/docs
   ```

   - Try API endpoints
   - See request/response schemas
   - Execute requests directly

2. **ReDoc** (Read-only)

   ```
   http://localhost:4000/redoc
   ```

   - Clean, organized view
   - Searchable
   - Download OpenAPI spec

3. **Raw OpenAPI**

   ```bash
   # JSON
   curl http://localhost:4000/openapi.json

   # Or use the generated YAML
   cat content/docs/03-api-reference/openapi.yaml
   ```

## Troubleshooting

### Backend Not Running

**Error**: `Failed to connect to backend at http://localhost:4000`

**Solution**:

```bash
# Start the backend
uvicorn tracertm.api.main:app --reload

# Verify it's running
curl http://localhost:4000/openapi.json
```

### Spec Not Updating

**Problem**: Generated YAML is stale

**Solution**:

```bash
# Regenerate manually
bun run openapi

# Or rebuild (includes regeneration)
bun run build
```

### Module Resolution Issues

**Error**: `Cannot find package 'fumadocs-mdx'`

**Current Status**: Known issue with monorepo setup

**Workaround**: Use manual API documentation until resolved

**Permanent Fix**: (In progress)

```bash
cd frontend/apps/docs
rm -rf node_modules
bun install
```

## Code Sample Examples

### TypeScript (fetch)

```typescript
const response = await fetch('http://localhost:4000/api/v1/auth/me', {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});
const user = await response.json();
```

### Python (requests)

```python
import requests

response = requests.get(
    'http://localhost:4000/api/v1/auth/me',
    headers={'Authorization': f'Bearer {access_token}'}
)
user = response.json()
```

### curl

```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:4000/api/v1/auth/me
```

### Go

```go
req, _ := http.NewRequest("GET", "http://localhost:4000/api/v1/auth/me", nil)
req.Header.Set("Authorization", "Bearer "+accessToken)

client := &http.Client{}
resp, _ := client.Do(req)
```

## Environment Variables

```bash
# Backend URL (default: http://localhost:4000)
BACKEND_URL=http://localhost:4000

# For production builds
BACKEND_URL=https://api.tracertm.com bun run build
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Generate API Docs

on:
  push:
    paths:
      - 'src/tracertm/api/**'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Start backend
        run: |
          uvicorn tracertm.api.main:app &
          sleep 5

      - name: Generate OpenAPI
        working-directory: frontend/apps/docs
        run: bun run openapi

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add frontend/apps/docs/content/docs/03-api-reference/openapi.yaml
          git commit -m "docs: Update OpenAPI spec" || exit 0
          git push
```

## Next Steps

1. **Fix Module Resolution** → Enable dev server
2. **Add More Endpoints** → Complete API documentation
3. **Enable Auto-generation** → fumadocs-openapi integration
4. **Deploy Docs** → Make publicly accessible

## Resources

- **OpenAPI Spec**: `content/docs/03-api-reference/openapi.yaml`
- **Generation Script**: `scripts/generate-openapi.ts`
- **Full Summary**: `PHASE_4_OPENAPI_INTEGRATION_SUMMARY.md`
- **Backend Docs**: http://localhost:4000/docs

## Support

For issues or questions:

1. Check `PHASE_4_OPENAPI_INTEGRATION_SUMMARY.md`
2. Review troubleshooting section above
3. Inspect generation script logs
4. Verify backend is accessible

---

**Last Updated**: 2026-01-30
**Phase**: 4 - OpenAPI Integration
**Status**: Core features working, dev server needs module resolution fix
