# MSW (Mock Service Worker) Setup

This document explains how the Mock Service Worker is configured for TraceRTM frontend development.

## Overview

MSW enables the frontend to work independently without requiring the backend to be running. This is perfect for:
- Frontend development without backend dependencies
- Testing and demonstrations
- Offline development
- API contract validation

## Configuration

### Environment Variables

The MSW setup is controlled by environment variables in `.env.local`:

```bash
# Enable MSW (set to false to use real backend)
VITE_ENABLE_MSW=true

# Backend API URL (used when MSW is disabled)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Files Structure

```
apps/web/src/mocks/
├── browser.ts          # MSW browser worker setup
├── data.ts            # Mock data (projects, items, links, agents)
├── handlers.ts        # API endpoint handlers
└── index.ts           # Exports
```

### Mock Data

The mock data includes:
- **2 Projects**: "TraceRTM Core" and "Mobile App"
- **10 Items**: Requirements, features, code, tests, API endpoints, etc.
- **7 Links**: Traceability links between items
- **3 Agents**: Code analyzer, test runner, documentation generator

## Usage

### Development Mode

By default, MSW is enabled in development:

```bash
cd frontend/apps/web
bun run dev
```

You'll see a console message: `[MSW] Mock Service Worker started successfully`

### Disable MSW (Use Real Backend)

Set in `.env.local`:
```bash
VITE_ENABLE_MSW=false
```

Or start the real backend:
```bash
cd backend
go run cmd/server/main.go
```

### Production Build

MSW is automatically disabled in production builds. It only runs in development mode.

## API Endpoints Mocked

All TraceRTM API v1 endpoints are mocked:

### Projects
- `GET /api/v1/projects` - List all projects
- `GET /api/v1/projects/:id` - Get project by ID
- `POST /api/v1/projects` - Create project
- `PUT /api/v1/projects/:id` - Update project
- `DELETE /api/v1/projects/:id` - Delete project

### Items
- `GET /api/v1/items` - List all items (with optional project_id filter)
- `GET /api/v1/items/:id` - Get item by ID
- `POST /api/v1/items` - Create item
- `PUT /api/v1/items/:id` - Update item
- `DELETE /api/v1/items/:id` - Delete item

### Links
- `GET /api/v1/links` - List all links
- `GET /api/v1/links/:id` - Get link by ID
- `POST /api/v1/links` - Create link
- `PUT /api/v1/links/:id` - Update link
- `DELETE /api/v1/links/:id` - Delete link

### Agents
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/:id` - Get agent by ID
- `POST /api/v1/agents` - Create agent

### Graph
- `GET /api/v1/graph/full` - Get full graph data
- `GET /api/v1/graph/impact/:id` - Get impact analysis
- `GET /api/v1/graph/dependencies/:id` - Get dependency analysis

### System
- `GET /health` - Health check
- `GET /api/v1/sync/status` - Sync status

## Customizing Mock Data

Edit `apps/web/src/mocks/data.ts` to add or modify mock data:

```typescript
import { mockProjects, mockItems, mockLinks } from './data'

// Add a new project
mockProjects.push({
  id: 'proj-3',
  name: 'New Project',
  description: 'My new project',
  metadata: {},
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
})
```

## Adding New Endpoints

To mock new endpoints, add handlers to `apps/web/src/mocks/handlers.ts`:

```typescript
export const handlers = [
  // ... existing handlers

  http.get(`${API_BASE}/api/v1/new-endpoint`, async () => {
    await delay()
    return HttpResponse.json({ data: 'response' })
  }),
]
```

## Troubleshooting

### MSW not starting
- Check browser console for errors
- Verify `public/mockServiceWorker.js` exists
- Try clearing browser cache and reloading

### Network requests bypassing MSW
- Check if `VITE_ENABLE_MSW=true` in `.env.local`
- Verify the API base URL matches in `handlers.ts`
- Check browser DevTools Network tab for MSW indicator

### TypeScript errors
- Ensure types in `handlers.ts` match `api/types.ts`
- Run `bun run type-check` to validate

## Benefits

1. **Independent Development**: Frontend developers can work without backend
2. **Fast Iteration**: No backend startup or API delays
3. **Predictable Data**: Consistent mock data for testing
4. **Offline Development**: Work without network connectivity
5. **Contract Testing**: Validates API contract between frontend and backend

## Migration to Real Backend

When the backend is ready:
1. Set `VITE_ENABLE_MSW=false`
2. Start the backend server
3. Verify all endpoints work correctly
4. Remove or keep MSW for testing purposes

## Resources

- [MSW Documentation](https://mswjs.io/)
- [TraceRTM API Documentation](../../backend/docs/api.md)
- [Frontend Architecture](./ARCHITECTURE.md)
