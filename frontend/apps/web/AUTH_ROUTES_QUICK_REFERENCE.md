# Auth Routes Quick Reference

## Using AUTH_ROUTES Constants

When working with authentication routes, always use the centralized constants instead of hardcoded strings.

### Import
```typescript
import { AUTH_ROUTES } from "@/config/constants";
```

### Available Routes
```typescript
AUTH_ROUTES.LOGIN          // "/auth/login"
AUTH_ROUTES.REGISTER       // "/auth/register"
AUTH_ROUTES.LOGOUT         // "/auth/logout"
AUTH_ROUTES.CALLBACK       // "/auth/callback"
AUTH_ROUTES.RESET_PASSWORD // "/auth/reset-password"
```

### Examples

#### Navigation
```typescript
// ❌ Bad
navigate({ to: "/auth/login" });

// ✅ Good
navigate({ to: AUTH_ROUTES.LOGIN });
```

#### Redirects
```typescript
// ❌ Bad
window.location.href = "/auth/callback";

// ✅ Good
window.location.href = AUTH_ROUTES.CALLBACK;
```

#### Route Checks
```typescript
// ❌ Bad
if (pathname === "/auth/login") { /* ... */ }

// ✅ Good
if (pathname === AUTH_ROUTES.LOGIN) { /* ... */ }
```

#### Using Helper Functions
```typescript
import { isPublicRoute } from "@/lib/auth-utils";

// Check if route is a public auth route
if (isPublicRoute(pathname)) {
  // This is a login/register/callback page
}
```

## WorkOS Integration

### How It Works
1. User clicks login button
2. `signIn()` from WorkOS redirects to WorkOS hosted UI
3. User authenticates with WorkOS
4. WorkOS redirects back to `AUTH_ROUTES.CALLBACK`
5. Callback route exchanges code for token
6. `AuthKitSync` syncs token to local store
7. User redirected to intended destination

### Key Components

#### AuthKitProvider
Location: `/src/providers/AppProviders.tsx`
- Wraps app with WorkOS authentication
- Configures redirect URI
- Provides `useAuth()` hook

#### AuthKitSync
Location: `/src/components/auth/AuthKitSync.tsx`
- Syncs WorkOS auth state to local store
- Handles redirect logic after auth
- Refreshes tokens periodically

#### Auth Routes
Location: `/src/routes/auth.*.tsx`
- `auth.login.tsx` - Shows WorkOS login button
- `auth.register.tsx` - Shows WorkOS register button
- `auth.callback.tsx` - Handles OAuth callback
- `auth.logout.tsx` - Handles logout flow

## Common Patterns

### Redirect After Login
```typescript
// auth.callback.tsx example
const returnTo = getReturnTo(searchParams);
navigate({ to: returnTo }); // Already filtered, safe to use
```

### Check Authentication
```typescript
import { useIsAuthenticated } from "@/lib/auth-utils";

const isAuth = useIsAuthenticated();
if (!isAuth) {
  navigate({ to: AUTH_ROUTES.LOGIN });
}
```

### Store Return URL
```typescript
// Before redirecting to login, save current location
const currentPath = window.location.pathname;
navigate({ 
  to: AUTH_ROUTES.LOGIN,
  search: { returnTo: currentPath }
});
```

## Best Practices

1. **Always use constants** - Never hardcode route strings
2. **Use helper functions** - `isPublicRoute()`, `getReturnTo()`, etc.
3. **Let WorkOS handle UI** - Don't build custom auth forms
4. **Trust AuthKitSync** - Don't manually sync tokens
5. **Use navigate() over window.location** - Better for SPA navigation

## Debugging

### Check WorkOS Config
```typescript
// In browser console
console.log(import.meta.env.VITE_WORKOS_CLIENT_ID);
```

### Check Auth State
```typescript
import { useAuth } from "@workos-inc/authkit-react";

const { user, isLoading } = useAuth();
console.log({ user, isLoading });
```

### Check Token
```typescript
import { useAuthStore } from "@/stores/authStore";

const token = useAuthStore((state) => state.token);
console.log({ token });
```

## Troubleshooting

### User Not Redirecting After Login
- Check `AuthKitProvider` redirectUri matches WorkOS dashboard
- Verify callback route is handling errors correctly
- Check browser console for errors in AuthKitSync

### Infinite Redirect Loop
- Ensure `getReturnTo()` filters out auth routes
- Check that callback route doesn't redirect to itself
- Verify `hasRedirectedRef` prevents multiple redirects

### Token Not Persisting
- Check AuthKitSync is mounted in AppProviders
- Verify `setAuthFromWorkOS()` is being called
- Check localStorage for token (if using persistence)

## File Structure
```
src/
├── config/
│   └── constants.ts          # AUTH_ROUTES defined here
├── lib/
│   └── auth-utils.ts         # isPublicRoute, getReturnTo, etc.
├── stores/
│   └── authStore.ts          # Auth state management
├── components/
│   └── auth/
│       └── AuthKitSync.tsx   # Token sync component
├── providers/
│   └── AppProviders.tsx      # AuthKitProvider setup
└── routes/
    ├── auth.login.tsx        # Login page
    ├── auth.register.tsx     # Register page
    ├── auth.callback.tsx     # OAuth callback
    └── auth.logout.tsx       # Logout page
```
