# TanStack Router - Quick Start Guide

## Status: ✅ COMPLETE

All 68 routes are configured and ready to use. Everything is working out of the box.

---

## Start Development

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun run dev
```

Navigate to: http://localhost:5173

---

## Using Routes in Components

### Navigate with Link
```tsx
import { Link } from '@tanstack/react-router'

// Simple route
<Link to="/projects">View Projects</Link>

// Dynamic route with parameters
<Link 
  to="/projects/$projectId/features/$featureId"
  params={{ projectId: "proj-123", featureId: "feat-456" }}
>
  View Feature
</Link>
```

### Navigate Programmatically
```tsx
import { useNavigate } from '@tanstack/react-router'

const navigate = useNavigate()

// Navigate with parameters
navigate({
  to: "/projects/$projectId",
  params: { projectId: "proj-123" }
})
```

### Access Route Parameters
```tsx
import { Route } from './routes/projects.$projectId.features.$featureId'

function FeatureDetail() {
  // Type-safe parameter access
  const { projectId, featureId } = Route.useParams()
  
  return <div>Project: {projectId}, Feature: {featureId}</div>
}
```

### Access Search Parameters
```tsx
function SearchPage() {
  const { q, type } = Route.useSearch()
  
  return <div>Search: {q}, Type: {type}</div>
}
```

---

## Adding New Routes

### Step 1: Create Route File
```bash
touch src/routes/my-feature.index.tsx
```

### Step 2: Define Route
```tsx
// src/routes/my-feature.index.tsx
import { createFileRoute } from '@tanstack/react-router'
import { MyFeatureView } from '@/views/MyFeatureView'

export const Route = createFileRoute('/my-feature')({
  component: MyFeatureView,
})
```

### Step 3: Regenerate Route Tree
```bash
bunx @tanstack/router-cli@latest generate
```

### Step 4: Use the Route
```tsx
<Link to="/my-feature">Go to My Feature</Link>
```

---

## Common Patterns

### Dynamic Route
```tsx
// File: src/routes/items.$itemId.tsx
export const Route = createFileRoute('/items/$itemId')({
  component: ItemDetail,
})

function ItemDetail() {
  const { itemId } = Route.useParams()
  return <div>Item: {itemId}</div>
}
```

### Nested Route
```tsx
// File: src/routes/projects.$projectId.features.$featureId.tsx
export const Route = createFileRoute(
  '/projects/$projectId/features/$featureId'
)({
  component: FeatureDetail,
})
```

### Route with Search Parameters
```tsx
// File: src/routes/search.index.tsx
export const Route = createFileRoute('/search')({
  component: SearchPage,
})

function SearchPage() {
  const { q, type } = Route.useSearch()
  const navigate = useNavigate()
  
  return (
    <div>
      <input 
        value={q} 
        onChange={(e) => navigate({ 
          to: '/search', 
          search: { q: e.target.value, type } 
        })}
      />
    </div>
  )
}
```

---

## Route List (Quick Reference)

### Public Routes (No Auth Required)
- `/auth/login`
- `/auth/register`
- `/auth/reset-password`
- `/auth/callback`
- `/integrations/callback`

### Protected Routes (Require Auth)
- `/` (home)
- `/projects`
- `/items`
- `/graph`
- `/search`
- `/settings`
- `/reports`
- `/matrix`
- `/impact`
- `/events`

### Dynamic Routes
- `/items/$itemId`
- `/projects/$projectId`
- `/projects/$projectId/features/$featureId`
- `/projects/$projectId/contracts/$contractId`
- `/projects/$projectId/adrs/$adrId`
- `/projects/$projectId/views/$viewType`
- `/projects/$projectId/views/$viewType/$itemId`

### View Routes
See ROUTES_INDEX.md for complete list of all 25+ view routes

---

## Troubleshooting

### Routes not working?
```bash
# Regenerate route tree
bunx @tanstack/router-cli@latest generate
```

### Type errors?
```bash
# Check types
bun run typecheck
```

### 404 errors?
1. Check file exists in `src/routes/`
2. Check file name matches route path
3. Verify route uses `createFileRoute()`
4. Regenerate route tree

### Parameters undefined?
1. Use `$` prefix in file names: `$itemId`
2. Access with `Route.useParams()`
3. Ensure parameter is in path: `/items/$itemId`

---

## Documentation

- **Complete Routes Reference:** ROUTES_INDEX.md
- **Verification Report:** ROUTING_VERIFICATION.md
- **Full Summary:** ROUTING_COMPLETION_SUMMARY.md
- **Verification Script:** ./verify-routing.sh

---

## Run Verification

```bash
./verify-routing.sh
```

Expected output: All checks pass ✅

---

## Key Files

| File | Purpose |
|------|---------|
| `src/routeTree.gen.ts` | Auto-generated route definitions |
| `src/router.tsx` | Router configuration |
| `src/main.tsx` | App entry point |
| `src/routes/` | Route files directory |

---

## Framework Details

- **Framework:** TanStack Router v1.157.16
- **File-based routing:** Yes (automatic)
- **Type-safe navigation:** Yes
- **Parameter typing:** Yes
- **Search parameter typing:** Yes
- **Preload strategy:** intent (hover/focus)
- **Code splitting:** Vite-enabled

---

## Next Steps

1. ✅ Start dev server: `bun run dev`
2. ✅ Navigate around the app
3. ✅ Try adding a new route
4. ✅ Test dynamic routes
5. ✅ Continue with feature development

---

**Status:** Production Ready ✅  
**Last Updated:** 2026-01-29
