# TraceRTM Web App - Quick Start Guide

## Prerequisites

- Node.js 20+ or Bun 1.1.38+
- Backend API running on `http://localhost:8000`

## Installation

```bash
# From frontend root
cd frontend

# Install dependencies
bun install

# Or from web app directory
cd apps/web
bun install
```

## Development

```bash
# Start dev server
bun run dev

# Runs on http://localhost:5173
```

## Environment Variables

Create `.env.local` in `apps/web/`:

```env
VITE_API_URL=http://localhost:8000
```

## Available Scripts

```bash
bun run dev      # Start development server
bun run build    # Production build
bun run preview  # Preview production build
bun run test     # Run tests
bun run lint     # Lint code
```

## Project Structure

```
src/
├── api/           # API client and endpoints
├── stores/        # Zustand state stores
├── hooks/         # Custom React hooks
├── components/    # Reusable components
├── pages/         # Route components
├── lib/           # Utilities
└── __tests__/     # Test files
```

## Key Features

### API Integration
```typescript
import { api } from '@/api/endpoints'

// Get all projects
const projects = await api.projects.list()

// Create item
const item = await api.items.create({
  project_id: 'xxx',
  type: 'feature',
  title: 'New Feature'
})
```

### State Management
```typescript
import { useItemsStore, useAuthStore } from '@/stores'

// Get items from store
const items = useItemsStore(state => state.items)

// Check authentication
const isAuthenticated = useAuthStore(state => state.isAuthenticated)
```

### React Query Hooks
```typescript
import { useItemsQuery, useCreateItem } from '@/hooks/useItemsQuery'

function MyComponent() {
  const { data: items } = useItemsQuery(projectId)
  const createItem = useCreateItem()

  const handleCreate = () => {
    createItem.mutate({
      title: 'New Item',
      type: 'feature',
      project_id: projectId
    })
  }
}
```

### Real-time Updates
```typescript
import { useRealtimeSubscription } from '@/hooks/useWebSocketHook'

function MyComponent() {
  useRealtimeSubscription('items:*', (event) => {
    console.log('Item event:', event)
  })
}
```

## Common Tasks

### Add a New View

1. Create component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation in `Sidebar.tsx`

### Add a New API Endpoint

1. Add type in `src/api/types.ts`
2. Add function in `src/api/endpoints.ts`
3. Create hook in `src/hooks/`

### Add a New Store

1. Create file in `src/stores/`
2. Export from `src/stores/index.ts`
3. Use in components with `useStore()`

## Testing

```bash
# Run all tests
bun test

# Run with coverage
bun test --coverage

# Run specific test
bun test src/hooks/useAuth.test.ts
```

## Troubleshooting

### API Connection Issues
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify `VITE_API_URL` in `.env.local`

### Build Errors
```bash
# Clear cache
rm -rf node_modules/.vite
rm -rf dist

# Reinstall
bun install
bun run build
```

### TypeScript Errors
```bash
# Rebuild TypeScript
bun run build --mode development
```

## Production Deployment

```bash
# Build for production
bun run build

# Output directory: dist/
# Serve with any static file server
```

### Docker

```bash
# Build image
docker build -t tracertm-web .

# Run container
docker run -p 80:80 -e VITE_API_URL=https://api.tracertm.com tracertm-web
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name tracertm.com;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Resources

- [React 19 Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://github.com/pmndrs/zustand)
- [Radix UI](https://www.radix-ui.com)
