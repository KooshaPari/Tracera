# TraceRTM Frontend - Quick Start

## Start Development (No Backend Required)

```bash
cd frontend/apps/web
bun run dev
```

Open http://localhost:3001 in your browser.

You should see in console: `[MSW] Mock Service Worker started successfully`

## Environment Setup

### First Time Setup

1. Copy environment template:

```bash
cp .env.example .env.local
```

2. Verify MSW is enabled (default):

```bash
cat .env.local
# Should show: VITE_ENABLE_MSW=true
```

3. Start development:

```bash
bun run dev
```

## Working Modes

### Mode 1: Mock Backend (Default)

**Best for:** Frontend development, testing, demos

```bash
# .env.local
VITE_ENABLE_MSW=true
VITE_API_URL=http://localhost:8000
```

Start frontend only:

```bash
bun run dev
```

### Mode 2: Real Backend

**Best for:** Integration testing, production-like environment

```bash
# .env.local
VITE_ENABLE_MSW=false
VITE_API_URL=http://localhost:8000
```

Start backend first:

```bash
cd ../../../backend
go run cmd/server/main.go
```

Then start frontend:

```bash
cd ../frontend/apps/web
bun run dev
```

## Available Commands

```bash
bun run dev          # Start dev server
bun run build        # Production build
bun run preview      # Preview production build
bun run lint         # Run linter
bun run test         # Run tests
```

## Mock Data Available

When using MSW, you have access to:

### Projects (2)

- TraceRTM Core (proj-1)
- Mobile App (proj-2)

### Items (10)

- Requirements, Features, Code, Tests
- API endpoints, Database schemas
- Wireframes, Documentation

### Links (7)

- Traceability between items
- Implements, Tests, Documents relationships

### Agents (3)

- Code Analyzer (idle)
- Test Runner (busy)
- Documentation Generator (idle)

## Customizing Mock Data

Edit `src/mocks/data.ts`:

```typescript
import { mockProjects } from './mocks/data';

// Add a new project
mockProjects.push({
  id: 'proj-3',
  name: 'My New Project',
  description: 'Test project',
  metadata: {},
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
});
```

## Troubleshooting

### MSW not starting?

- Check browser console
- Verify `public/mockServiceWorker.js` exists
- Clear browser cache

### API calls failing?

- Check `.env.local` has `VITE_ENABLE_MSW=true`
- Verify API base URL is `http://localhost:8000`
- Check browser Network tab

### Build errors?

```bash
bun run build
# Check for TypeScript errors
```

## Features

✅ Full CRUD operations for projects, items, links
✅ Graph API (impact analysis, dependencies)
✅ Realistic network delays (100ms)
✅ Proper error handling
✅ TypeScript type safety
✅ Hot module replacement
✅ Fast refresh

## Performance

- Dev server start: ~250ms
- Build time: ~7.6s
- Mock response time: 100ms

## Next Steps

1. **Start building**: Components automatically use mocked API
2. **Add features**: Create new components and hooks
3. **Test integration**: Switch to real backend when ready
4. **Deploy**: MSW automatically disabled in production

For detailed documentation, see:

- [MSW_SETUP.md](./MSW_SETUP.md) - Complete MSW guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Frontend architecture

## Support

Having issues? Check:

1. MSW Setup Guide: `MSW_SETUP.md`
2. Browser console for errors
3. Network tab in DevTools
