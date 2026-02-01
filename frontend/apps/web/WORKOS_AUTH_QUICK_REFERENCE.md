# WorkOS AuthKit Integration - Quick Reference

## Overview
TraceRTM uses WorkOS AuthKit for authentication, delegating all auth UI to WorkOS hosted pages.

## Auth Flow Architecture

```
User Action         →  Application Route      →  WorkOS           →  Application Callback
─────────────────────────────────────────────────────────────────────────────────────────
Visit /auth/login   →  LoginRedirect          →  Hosted Login     →  /auth/callback
Visit /auth/register→  RegisterRedirect       →  Hosted Register  →  /auth/callback
                                                                    →  Dashboard
```

## Route Implementations

### `/auth/login` - Login Redirect Handler
**Purpose:** Immediately redirect to WorkOS hosted login UI

**Implementation:**
```typescript
function LoginRedirect() {
  const { user, isLoading, signIn } = useAuth();

  useEffect(() => {
    if (user && !isLoading) {
      navigate({ to: "/" }); // Already logged in
      return;
    }
    if (!isLoading && !user) {
      signIn(); // Redirect to WorkOS
    }
  }, [user, isLoading, signIn, navigate]);

  return <div>Redirecting to sign in...</div>;
}
```

**User Experience:**
1. User visits `/auth/login`
2. Sees "Redirecting to sign in..." for <1 second
3. Browser redirects to WorkOS hosted UI
4. User completes authentication on WorkOS
5. WorkOS redirects back to `/auth/callback`
6. User lands on dashboard

### `/auth/register` - Register Redirect Handler
**Purpose:** Immediately redirect to WorkOS hosted registration UI

**Implementation:**
```typescript
function RegisterRedirect() {
  const { user, isLoading, signUp } = useAuth();

  useEffect(() => {
    if (user && !isLoading) {
      navigate({ to: "/" }); // Already logged in
      return;
    }
    if (!isLoading && !user) {
      signUp(); // Redirect to WorkOS
    }
  }, [user, isLoading, signUp, navigate]);

  return <div>Redirecting to sign up...</div>;
}
```

**User Experience:**
1. User visits `/auth/register`
2. Sees "Redirecting to sign up..." for <1 second
3. Browser redirects to WorkOS hosted UI (registration mode)
4. User creates account on WorkOS
5. WorkOS redirects back to `/auth/callback`
6. User lands on dashboard

### `/auth/callback` - OAuth Callback Handler
**Purpose:** Process OAuth response from WorkOS

**Flow:**
1. WorkOS redirects to `/auth/callback?code=...&state=...`
2. WorkOS SDK automatically exchanges code for tokens
3. `AuthKitSync` component syncs user data to auth store
4. User redirected to dashboard (or `returnTo` URL)

**Error Handling:**
- OAuth errors from WorkOS → Show error message with retry
- Network errors → Show error with manual retry button
- Missing user data → Redirect to login

### `/auth/logout` - Logout Handler
**Purpose:** Clear session and redirect to login

**Flow:**
1. User visits `/auth/logout`
2. Clear local auth state
3. Call WorkOS `signOut()`
4. Redirect to `/auth/login`

## Configuration

### AuthKitProvider Setup
**File:** `src/providers/AppProviders.tsx`

```typescript
<AuthKitProvider
  clientId={VITE_WORKOS_CLIENT_ID}
  redirectUri={`${window.location.origin}/auth/callback`}
>
  {/* App content */}
  <AuthKitSync />
</AuthKitProvider>
```

**Critical Settings:**
- `clientId`: From WorkOS Dashboard (env: `VITE_WORKOS_CLIENT_ID`)
- `redirectUri`: Must point to `/auth/callback` route
- `redirectUri` must be registered in WorkOS Dashboard

### Environment Variables
```bash
# .env.local
VITE_WORKOS_CLIENT_ID=client_123...
```

### WorkOS Dashboard Configuration
1. Go to [WorkOS Dashboard](https://dashboard.workos.com)
2. Select your application
3. Navigate to "Redirect URIs"
4. Add the following URIs:

**Development:**
```
http://localhost:5173/auth/callback
```

**Production:**
```
https://yourdomain.com/auth/callback
```

## Authentication State Management

### AuthKitSync Component
**Purpose:** Sync WorkOS auth state to Zustand store

**Located:** `src/components/auth/AuthKitSync.tsx`

**Responsibilities:**
- Monitor WorkOS `user` and access token changes
- Update `useAuthStore` with WorkOS data
- Provide centralized auth state for application

### useAuth Hook (WorkOS)
**Provider:** `@workos-inc/authkit-react`

**Available Methods:**
```typescript
const {
  user,              // Current user object (null if not authenticated)
  isLoading,         // Loading state
  getAccessToken,    // Get current access token
  signIn,            // Redirect to login
  signUp,            // Redirect to registration
  signOut,           // Clear session and logout
} = useAuth();
```

### useAuthStore Hook (Application)
**Provider:** Custom Zustand store

**Available State:**
```typescript
const {
  user,              // Synced from WorkOS
  token,             // Access token
  isAuthenticated,   // Boolean flag
  login,             // Set auth state
  logout,            // Clear auth state
  setAuthFromWorkOS, // Sync from WorkOS
} = useAuthStore();
```

## Protected Routes

### Route Protection Pattern
```typescript
// In route beforeLoad
export const Route = createFileRoute("/protected/path")({
  beforeLoad: async ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: "/auth/login",
        search: {
          returnTo: location.href,
        },
      });
    }
  },
});
```

### Return URL Handling
After login, users are redirected to:
1. `returnTo` URL parameter (if present)
2. Dashboard (`/`) by default

**Example:**
```
/auth/login?returnTo=/projects/123
→ Login on WorkOS
→ Redirect to /auth/callback?returnTo=/projects/123
→ Redirect to /projects/123
```

## Testing

### Manual Testing Checklist
- [ ] Visit `/auth/login` → redirects to WorkOS
- [ ] Complete login → returns to dashboard
- [ ] Visit `/auth/register` → redirects to WorkOS
- [ ] Complete registration → returns to dashboard
- [ ] Visit protected route → redirects to login with returnTo
- [ ] Complete login with returnTo → returns to original route
- [ ] Visit `/auth/logout` → clears session, redirects to login
- [ ] Visit `/auth/login` when logged in → redirects to dashboard

### Common Issues

**Issue:** Infinite redirect loop on login
**Cause:** `redirectUri` mismatch or not set correctly
**Fix:** Verify `redirectUri={window.location.origin}/auth/callback` in `AppProviders.tsx`

**Issue:** "Invalid redirect URI" error from WorkOS
**Cause:** Redirect URI not registered in WorkOS Dashboard
**Fix:** Add `http://localhost:5173/auth/callback` to WorkOS Dashboard

**Issue:** User not persisted after login
**Cause:** `AuthKitSync` not mounted or not working
**Fix:** Verify `<AuthKitSync />` is rendered inside `<AuthKitProvider>`

**Issue:** Access token not available
**Cause:** Token not synced to auth store
**Fix:** Check `AuthKitSync` is properly calling `setAuthFromWorkOS`

## Debugging

### Enable Debug Logs
```typescript
// In AppProviders.tsx
if (import.meta.env.DEV) {
  console.log("[AppProviders] AuthKitProvider props:", {
    clientId: providerProps.clientId,
    redirectUri: providerProps.redirectUri,
  });
}
```

### Check Auth State
```typescript
// In any component
const { user, isLoading } = useAuth();
console.log("WorkOS user:", user);
console.log("Loading:", isLoading);

const authStore = useAuthStore();
console.log("Auth store:", authStore);
```

### Monitor Network Requests
1. Open DevTools → Network tab
2. Filter by "workos"
3. Look for OAuth token exchange requests
4. Check response for errors

## Migration from Custom Auth

### Removed Code
- Custom login form UI
- Custom registration form UI
- Manual email/password handling
- Session management logic

### Kept Code
- Auth route structure (`/auth/*`)
- Auth store (now synced from WorkOS)
- Protected route logic
- Return URL handling

### Benefits
- Reduced code maintenance (no custom forms)
- Better security (WorkOS handles auth)
- Professional auth UI (WorkOS hosted pages)
- Easy to add SSO, MFA, etc. (WorkOS features)

## Advanced Features

### Single Sign-On (SSO)
WorkOS AuthKit supports SSO out of the box. Configure in WorkOS Dashboard.

### Multi-Factor Authentication (MFA)
Enable MFA in WorkOS Dashboard. No code changes required.

### Social Login
Add social providers (Google, GitHub, etc.) in WorkOS Dashboard.

### Custom Domains
Configure custom auth domain in WorkOS Dashboard for white-label experience.

## Resources

- [WorkOS AuthKit Docs](https://workos.com/docs/authkit)
- [WorkOS React SDK](https://workos.com/docs/authkit/react)
- [WorkOS Dashboard](https://dashboard.workos.com)
- Internal: `/auth/callback` documentation
- Internal: `AUTH_REFACTOR_SUMMARY.md`
