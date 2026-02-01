# Route Protection Quick Start

## TL;DR

Add this to any route that should require authentication:

```typescript
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/your-route")({
  beforeLoad: () => requireAuth(),
  component: YourComponent,
});
```

## Quick Examples

### Basic Protected Route
```typescript
import { createFileRoute } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/")({
  beforeLoad: () => requireAuth(),
  component: ProjectsListView,
});
```

### Protected Route with Loader
```typescript
export const Route = createFileRoute("/projects/$projectId")({
  beforeLoad: () => requireAuth(),
  loader: async ({ params }) => {
    // Only runs for authenticated users
    return await fetchProject(params.projectId);
  },
  component: ProjectDetailView,
});
```

### Custom Redirect Destination
```typescript
export const Route = createFileRoute("/admin/")({
  beforeLoad: () => requireAuth({ redirectTo: "/auth/login" }),
  component: AdminPanel,
});
```

### Require Account Context
```typescript
export const Route = createFileRoute("/settings/")({
  beforeLoad: () => requireAuthWithAccount(),
  component: SettingsView,
});
```

### Public Route (No Auth)
```typescript
export const Route = createFileRoute("/auth/login")({
  component: LoginPage,
  // No beforeLoad - public route
});
```

## Available Guards

### `requireAuth(options?)`
Basic authentication check. Redirects to `/` by default.

**Options:**
- `redirectTo?: string` - Custom redirect path (default: `"/"`)
- `includeReturnUrl?: boolean` - Include returnTo parameter (default: `true`)

### `requireAuthWithAccount(options?)`
Checks authentication AND account context. Redirects to account selection if no account.

**Options:** Same as `requireAuth()`

### `checkAuth()`
Non-blocking check. Returns auth state without redirecting.

**Returns:** `{ isAuthenticated, user, account }`

## Common Patterns

### Multiple Checks
```typescript
beforeLoad: () => {
  requireAuth();
  // Additional validation
  if (!hasPermission("projects.edit")) {
    throw redirect({ to: "/forbidden" });
  }
}
```

### Conditional Redirect
```typescript
beforeLoad: ({ search }) => {
  const { isAuthenticated } = checkAuth();
  if (!isAuthenticated && search.needsAuth) {
    throw redirect({ to: "/auth/login" });
  }
}
```

### Redirect Routes
```typescript
beforeLoad: ({ params }) => {
  requireAuth(); // Check auth first
  throw redirect({ to: "/new-route", params });
}
```

## Testing

### Unit Test Example
```typescript
import { requireAuth } from "@/lib/route-guards";
import { useAuthStore } from "@/stores/authStore";

it("should redirect when not authenticated", () => {
  useAuthStore.setState({ isAuthenticated: false, user: null });
  expect(() => requireAuth()).toThrow();
});
```

### E2E Test Example
```typescript
test("redirects to login when accessing protected route", async ({ page }) => {
  await page.goto("/projects");
  await expect(page).toHaveURL("/?returnTo=/projects");
});
```

## Checklist for New Routes

- [ ] Add `import { requireAuth } from "@/lib/route-guards";`
- [ ] Add `beforeLoad: () => requireAuth(),` to route config
- [ ] Test route without authentication
- [ ] Test route with authentication
- [ ] Verify return URL works after login
- [ ] Update route documentation if needed

## Common Issues

### "requireAuth is not defined"
**Fix:** Add import: `import { requireAuth } from "@/lib/route-guards";`

### Redirect loop
**Fix:** Make sure `/` route doesn't have `requireAuth()`

### Return URL not working
**Fix:** Ensure landing page handles `returnTo` query parameter

### Auth state not persisting
**Fix:** Check localStorage is enabled and working

## Full Documentation

See `/docs/ROUTE_PROTECTION.md` for complete documentation.

## Quick Commands

```bash
# Run auth tests
bun test route-guards

# Find all protected routes
grep -l "requireAuth" src/routes/*.tsx

# Check auth store state
# In browser console:
useAuthStore.getState()
```
