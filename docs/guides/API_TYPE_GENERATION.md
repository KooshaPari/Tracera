# API Type Generation & Synchronization

This document explains how backend API types are generated and synchronized to the frontend for end-to-end type safety.

## Overview

TraceRTM uses a **code-first** approach with automatic type generation:

1. **Backend (Go)**: Swag annotations on handlers → OpenAPI 2.0 spec → OpenAPI 3.0 conversion
2. **Frontend (TypeScript)**: OpenAPI 3.0 spec → TypeScript types via `openapi-typescript`

## Architecture

```
┌─────────────────┐
│  Go Backend     │
│  (Swag Annot.)  │
└────────┬────────┘
         │
         ▼
    [swag init]
         │
         ▼
┌─────────────────┐
│ Swagger 2.0 JSON│
└────────┬────────┘
         │
         ▼
 [swagger2openapi]
         │
         ▼
┌─────────────────┐
│ OpenAPI 3.0 JSON│
└────────┬────────┘
         │
         ▼
     [copy to]
         │
         ▼
┌─────────────────────────────┐
│ frontend/apps/web/public/   │
│   specs/openapi.json        │
└──────────────┬──────────────┘
               │
               ▼
     [openapi-typescript]
               │
               ▼
┌─────────────────────────────┐
│ frontend/apps/web/src/api/  │
│   schema.ts (5000+ lines)   │
└─────────────────────────────┘
```

## Quick Start

### Automated Sync (Recommended)

Use the automated sync script:

```bash
# From project root
./scripts/sync-openapi.sh
```

This script:
1. Generates OpenAPI spec from Go code
2. Converts Swagger 2.0 → OpenAPI 3.0
3. Syncs to frontend
4. Generates TypeScript types
5. Creates backups automatically

### Manual Steps

If you need to run steps individually:

```bash
# 1. Generate backend OpenAPI spec
cd backend
swag init --generalInfo main.go --dir ./ --output ./docs \
  --parseDependency --parseInternal --parseDepth 2 \
  --instanceName "tracertm"

# 2. Convert to OpenAPI 3.0 (required for TypeScript generator)
swagger2openapi docs/tracertm_swagger.json -o docs/openapi.json

# 3. Copy to frontend
cp docs/openapi.json ../frontend/apps/web/public/specs/openapi.json

# 4. Generate TypeScript types
cd ../frontend/apps/web
bun run generate:types
```

## Development Workflow

### When to Regenerate

Regenerate types whenever:
- ✅ Adding new API endpoints
- ✅ Modifying request/response structures
- ✅ Changing endpoint parameters or paths
- ✅ Updating error response formats

### Before Committing

```bash
# 1. Sync types
./scripts/sync-openapi.sh

# 2. Review changes
git diff frontend/apps/web/src/api/schema.ts

# 3. Test compilation
cd frontend/apps/web && bun run build

# 4. Commit both backend and frontend changes together
git add backend/docs/openapi.json frontend/apps/web/public/specs/openapi.json frontend/apps/web/src/api/schema.ts
git commit -m "sync: Update API types from backend changes"
```

## Files & Locations

### Backend Files

- **Source**: Go handlers with Swag annotations (`backend/**/*.go`)
- **Generated Swagger 2.0**: `backend/docs/tracertm_swagger.json` (236 KB)
- **Converted OpenAPI 3.0**: `backend/docs/openapi.json` (generated from Swagger 2.0)

### Frontend Files

- **OpenAPI Spec**: `frontend/apps/web/public/specs/openapi.json` (synced from backend)
- **Generated Types**: `frontend/apps/web/src/api/schema.ts` (~5000 lines, 13 KB minified)
- **Type Utilities**: `frontend/apps/web/src/api/types.ts` (helper types)

### Scripts

- **Main Sync**: `scripts/sync-openapi.sh` (automated end-to-end sync)
- **Backend Gen**: `backend/scripts/generate-openapi.sh` (backend-only generation)

## Type Safety in Action

### Backend Handler Example

```go
// CreateProject godoc
// @Summary Create a new project
// @Tags projects
// @Accept json
// @Produce json
// @Param project body CreateProjectRequest true "Project data"
// @Success 201 {object} ProjectResponse
// @Failure 400 {object} ErrorResponse
// @Router /projects [post]
func (h *Handler) CreateProject(c echo.Context) error {
    var req CreateProjectRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(400, ErrorResponse{Message: "Invalid request"})
    }
    // ...
}
```

### Generated Frontend Types

```typescript
// In schema.ts (auto-generated)
export interface operations {
  createProject: {
    requestBody: {
      content: {
        "application/json": components["schemas"]["CreateProjectRequest"];
      };
    };
    responses: {
      201: {
        content: {
          "application/json": components["schemas"]["ProjectResponse"];
        };
      };
      400: {
        content: {
          "application/json": components["schemas"]["ErrorResponse"];
        };
      };
    };
  };
}
```

### Frontend API Client Usage

```typescript
import type { paths } from '@/api/schema';
import createClient from 'openapi-fetch';

const client = createClient<paths>({ baseUrl: '/api/v1' });

// Fully typed request/response
const { data, error } = await client.POST('/projects', {
  body: {
    name: 'My Project',
    description: 'Project description',
  }
});

// data and error are fully typed based on backend!
if (error) {
  console.error(error.message); // TypeScript knows this exists
} else {
  console.log(data.id); // TypeScript knows ProjectResponse shape
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Type Sync Check

on: [pull_request]

jobs:
  check-types:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'

      - name: Install Swag
        run: go install github.com/swaggo/swag/cmd/swag@latest

      - name: Install Bun
        uses: oven-sh/setup-bun@v1

      - name: Install swagger2openapi
        run: npm install -g swagger2openapi

      - name: Sync API Types
        run: ./scripts/sync-openapi.sh

      - name: Check for uncommitted changes
        run: |
          git diff --exit-code frontend/apps/web/src/api/schema.ts || \
          (echo "❌ API types are out of sync! Run ./scripts/sync-openapi.sh" && exit 1)
```

## Tools & Dependencies

### Backend

- **Swag** v1.16.4+
  ```bash
  go install github.com/swaggo/swag/cmd/swag@latest
  ```

### Conversion

- **swagger2openapi** (npm package)
  ```bash
  npm install -g swagger2openapi
  ```

### Frontend

- **openapi-typescript** v6.7.3 (already in package.json)
  ```bash
  bun add -d openapi-typescript@6.7.3
  ```

- **openapi-fetch** (runtime client)
  ```bash
  bun add openapi-fetch
  ```

## Troubleshooting

### "Swagger 2.0 no longer supported"

**Problem**: `openapi-typescript` v7+ dropped Swagger 2.0 support
**Solution**: We convert Swagger 2.0 → OpenAPI 3.0 using `swagger2openapi`

### Types are out of sync

```bash
# Check file sizes
ls -lh backend/docs/openapi.json frontend/apps/web/public/specs/openapi.json

# Compare content
diff backend/docs/openapi.json frontend/apps/web/public/specs/openapi.json

# Re-sync
./scripts/sync-openapi.sh
```

### Generation fails

```bash
# Verify Swag is installed
swag --version  # Should show v1.16.4+

# Verify swagger2openapi is installed
which swagger2openapi

# Check Go code for Swag annotation errors
cd backend && swag init --generalInfo main.go --dir ./ --output ./docs
```

### Frontend compilation errors after sync

This usually means the backend made breaking changes. Options:

1. **Update frontend code** to match new types
2. **Revert backend changes** if they're unintentional
3. **Check migration guide** in the API changelog

## Best Practices

### ✅ DO

- Run sync script before every commit
- Commit backend + frontend type changes together
- Use semantic versioning for breaking API changes
- Document breaking changes in PR descriptions
- Test API changes with both old and new clients

### ❌ DON'T

- Manually edit `schema.ts` (it's auto-generated!)
- Commit backend changes without syncing frontend types
- Skip type generation to "save time"
- Make breaking changes without a migration plan
- Use `any` types to bypass TypeScript errors

## Status & Metrics

**Last Sync**: Jan 31, 2026
**Backend Spec Size**: 236 KB (OpenAPI 3.0)
**Frontend Types**: 5,201 lines (+3,987 from previous)
**Endpoints Covered**: 100+
**Type Safety**: End-to-end ✅

## Related Documentation

- [Backend OpenAPI Setup Guide](../../backend/OPENAPI_SETUP_GUIDE.md)
- [Frontend API Client Documentation](../../frontend/apps/web/src/api/README.md)
- [API Versioning Strategy](./API_VERSIONING.md)
