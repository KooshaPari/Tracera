# OAuth Callback - Quick Start Guide

## What This Does

The `/auth/callback` route handles the redirect from WorkOS after authentication. When users log in, they:

1. Click "Sign in" → redirected to WorkOS
2. Authenticate on WorkOS page
3. **Redirected back to `/auth/callback`** ← This route
4. Tokens exchanged, user logged in
5. Redirected to dashboard or intended page

## Quick Setup

### 1. Configure WorkOS (One-Time)

Add to `.env.local`:

```bash
VITE_WORKOS_CLIENT_ID=client_your_client_id_here
```

Add redirect URI in WorkOS Dashboard:

- Development: `http://localhost:5173/auth/callback`
- Production: `https://your-domain.com/auth/callback`

### 2. Start Development

```bash
cd frontend/apps/web
bun run dev
```

The route is automatically registered by TanStack Router.

### 3. Test the Flow

1. Navigate to: `http://localhost:5173/auth/login`
2. Click "Sign in with WorkOS"
3. Authenticate on WorkOS page
4. Redirected to `/auth/callback`
5. Success! Redirected to dashboard

## How It Works

### Authentication Flow

```
User → /auth/login
        ↓
     WorkOS Auth Page
        ↓
     /auth/callback?code=xxx  ← This route handles this
        ↓
     Token exchange (automatic)
        ↓
     / (dashboard) or returnTo URL
```

### Component States

**Loading**: "Authenticating..." with spinner
**Success**: "Welcome Back!" → redirect
**Error**: Show error message + retry button

### returnTo Parameter

Preserve user's intended destination:

```
User wants: /projects/123
       ↓
Not authenticated → redirect to /auth/login?returnTo=/projects/123
       ↓
After auth → /auth/callback?returnTo=/projects/123
       ↓
Success → redirect to /projects/123  ← User gets where they wanted
```

## File Locations

```
Route:          /frontend/apps/web/src/routes/auth.callback.tsx
Tests:          /frontend/apps/web/src/__tests__/routes/auth.callback.test.tsx
Documentation:  /frontend/apps/web/src/routes/AUTH_CALLBACK_DOCUMENTATION.md
```

## Common Issues

### Issue: "Cannot find route /auth/callback"

**Solution**: Restart dev server to regenerate route tree

### Issue: Infinite redirect loop

**Solution**: Check `returnTo` parameter doesn't point to auth routes

### Issue: CORS error

**Solution**: Add callback URL to WorkOS Dashboard

### Issue: User not logged in after callback

**Solution**: Check `AuthKitProvider` is wrapping app in `AppProviders.tsx`

## Testing

### Run Tests

```bash
bun test src/__tests__/routes/auth.callback.test.tsx
```

### Manual Test

1. Go to `/auth/callback` (no params)
2. Should show error: "No user information received"
3. This is correct! (no OAuth code = can't authenticate)

### Test with returnTo

1. Go to `/projects/123` (requires auth)
2. Redirected to `/auth/login?returnTo=/projects/123`
3. Sign in
4. Should redirect back to `/projects/123`

## Integration Points

### 1. WorkOS SDK

```tsx
const { user, isLoading } = useAuth();
// Automatic OAuth handling - no manual code exchange needed
```

### 2. Auth Store

```tsx
const setAuthFromWorkOS = useAuthStore((state) => state.setAuthFromWorkOS);
// Syncs user/token to app state
```

### 3. Navigation

```tsx
const navigate = useNavigate();
navigate({ to: returnTo });
// Client-side redirect after success
```

## Security

✅ **CSRF Protection**: WorkOS SDK validates `state` parameter
✅ **Redirect Validation**: `getReturnTo()` sanitizes URLs
✅ **Token Storage**: Handled by `AuthKitSync` component
✅ **Public Access**: Route is public (required for OAuth flow)

## Environment Setup

### Development

```bash
# .env.local
VITE_WORKOS_CLIENT_ID=client_dev_xxx
```

### Production

```bash
# .env.production
VITE_WORKOS_CLIENT_ID=client_prod_xxx
```

## Key Code Snippets

### Success Flow

```tsx
if (user && !isLoading) {
  setState({
    status: 'success',
    message: 'Authentication successful! Redirecting...',
  });

  const returnTo = getReturnTo(searchParams);
  navigate({ to: returnTo });
}
```

### Error Handling

```tsx
const error = searchParams.get('error');
if (error) {
  setState({
    status: 'error',
    message: errorDescription || 'Authentication failed',
  });
}
```

### Retry Logic

```tsx
const handleRetry = () => {
  window.location.href = AUTH_ROUTES.LOGIN;
};
```

## Developer Notes

- **No Token Storage**: Don't manually store tokens in this component
- **Use SDK**: Let WorkOS SDK handle OAuth complexity
- **500ms Delay**: Success state shows briefly before redirect (UX)
- **Error Recovery**: Always provide retry option for users
- **URL Validation**: Always validate returnTo to prevent open redirects

## Related Documentation

- Full docs: `/src/routes/AUTH_CALLBACK_DOCUMENTATION.md`
- Auth utils: `/src/lib/auth-utils.ts`
- Auth store: `/src/stores/authStore.ts`
- WorkOS setup: https://workos.com/docs

## Quick Commands

```bash
# Start dev server
bun run dev

# Run tests
bun test src/__tests__/routes/auth.callback.test.tsx

# Type check
bun run typecheck

# View route tree
cat src/routeTree.gen.ts | grep callback
```

## Support

For issues:

1. Check this guide
2. Review full documentation
3. Check WorkOS docs
4. Contact engineering team
