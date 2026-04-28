# OAuth Callback Route Documentation

## Overview

The `/auth/callback` route handles the OAuth redirect from WorkOS after user authentication. This is a critical component of the WorkOS AuthKit integration that processes authorization codes, manages token exchange, and redirects users to their intended destination.

## File Location

```
/frontend/apps/web/src/routes/auth.callback.tsx
```

## Route Configuration

- **Path**: `/auth/callback`
- **Access**: Public (no authentication required)
- **Framework**: TanStack Router (file-based routing)

## Architecture

### Integration Points

1. **WorkOS AuthKit React SDK**
   - Automatically handles OAuth callback processing
   - Exchanges authorization code for access tokens
   - Provides user information via `useAuth()` hook

2. **Auth Store** (`useAuthStore`)
   - Syncs WorkOS user/token to local auth state
   - Managed by `AuthKitSync` component in `AppProviders`

3. **Navigation**
   - Uses TanStack Router `useNavigate()` for client-side routing
   - Supports `returnTo` parameter for post-login redirects

4. **Auth Utils**
   - `getReturnTo()` helper validates and sanitizes redirect URLs
   - Prevents redirect loops by filtering auth routes

## Flow Diagram

```
User clicks login
    ↓
Redirected to WorkOS hosted auth page
    ↓
User authenticates with WorkOS
    ↓
WorkOS redirects to /auth/callback?code=xxx&state=yyy
    ↓
/auth/callback route loads
    ↓
AuthKitSync monitors WorkOS SDK state
    ↓
SDK exchanges code for tokens (automatic)
    ↓
Callback component shows loading → success states
    ↓
Navigate to returnTo URL or dashboard
    ↓
AuthKitSync syncs user/token to auth store
```

## Component States

### 1. Loading State

- **Trigger**: Initial load or SDK is processing
- **Display**: Spinning loader with "Authenticating" message
- **Duration**: Until SDK completes or error occurs

### 2. Success State

- **Trigger**: User authenticated successfully
- **Display**: Green checkmark with "Welcome Back" message
- **Duration**: 500ms before redirect
- **Action**: Navigate to `returnTo` URL or `/`

### 3. Error State

- **Trigger**:
  - OAuth error in URL params (`?error=xxx`)
  - No user after SDK completes
  - Network/API failures
- **Display**: Red alert icon with error message
- **Actions**:
  - "Try Again" → Redirect to `/auth/login`
  - "Cancel" → Redirect to `/`

## URL Parameters

### OAuth Parameters (from WorkOS)

- `code`: Authorization code (handled by SDK)
- `state`: CSRF protection token (handled by SDK)
- `error`: OAuth error code (e.g., `access_denied`)
- `error_description`: Human-readable error message

### Application Parameters

- `returnTo`: Post-login redirect URL
  - Validated by `getReturnTo()` helper
  - Auth routes are filtered to prevent loops
  - Default: `/` (dashboard)

## Error Handling

### OAuth Errors

```typescript
// Example error URL
/auth/callback?error=access_denied&error_description=User+cancelled
```

Common error codes:

- `access_denied`: User cancelled authentication
- `invalid_request`: Malformed OAuth request
- `server_error`: WorkOS server error
- `temporarily_unavailable`: Service temporarily down

### Authentication Failures

- **No user after loading**: SDK completed but no user data
- **Token exchange failed**: Network error or invalid code
- **Session expired**: Stale OAuth state

## Security Considerations

### CSRF Protection

- WorkOS SDK handles `state` parameter validation
- No manual CSRF token management needed

### Redirect Validation

- `getReturnTo()` sanitizes redirect URLs
- Prevents open redirect vulnerabilities
- Filters auth routes to prevent loops

### Token Storage

- Tokens are NOT stored in localStorage by this component
- `AuthKitSync` component handles secure token management
- Auth store uses Zustand with persistence

## Dependencies

### Required Packages

```json
{
  "@workos-inc/authkit-react": "^1.x",
  "@tanstack/react-router": "^1.x",
  "zustand": "^4.x",
  "lucide-react": "^0.x"
}
```

### Environment Variables

```bash
VITE_WORKOS_CLIENT_ID=client_xxx       # Required
VITE_WORKOS_API_HOSTNAME=api.workos.com # Optional (defaults to api.workos.com)
```

## Configuration

### WorkOS Dashboard Setup

1. Add redirect URI: `http://localhost:5173/auth/callback` (development)
2. Add redirect URI: `https://your-domain.com/auth/callback` (production)
3. Configure allowed domains
4. Set session timeout

### AppProviders Integration

```tsx
<AuthKitProvider
  clientId={VITE_WORKOS_CLIENT_ID}
  redirectUri={`${window.location.origin}/auth/callback`}
>
  {children}
  <AuthKitSync />
</AuthKitProvider>
```

## Testing

### Unit Tests

Location: `/src/__tests__/routes/auth.callback.test.tsx`

Test coverage:

- ✅ Loading state rendering
- ✅ Success state and redirect
- ✅ Error state with retry
- ✅ OAuth error handling
- ✅ returnTo parameter extraction
- ✅ Auth store integration

### Manual Testing

1. **Successful Login**

   ```
   1. Navigate to /auth/login
   2. Click "Sign in with WorkOS"
   3. Authenticate on WorkOS page
   4. Redirected to /auth/callback
   5. Should show success and redirect to /
   ```

2. **Login with returnTo**

   ```
   1. Navigate to /projects/123 (requires auth)
   2. Redirected to /auth/login?returnTo=/projects/123
   3. Authenticate
   4. Should redirect back to /projects/123
   ```

3. **Error Handling**
   ```
   1. Manually navigate to /auth/callback?error=access_denied
   2. Should show error message
   3. Click "Try Again" → redirects to /auth/login
   ```

## Troubleshooting

### Issue: Infinite redirect loop

**Cause**: returnTo points to another auth route
**Solution**: `getReturnTo()` filters auth routes, check implementation

### Issue: User not authenticated after callback

**Cause**: `AuthKitSync` not running
**Solution**: Ensure `AuthKitProvider` wraps app in `AppProviders`

### Issue: Token not persisted

**Cause**: Auth store not properly configured
**Solution**: Check Zustand persistence middleware

### Issue: CORS errors

**Cause**: Redirect URI not whitelisted in WorkOS
**Solution**: Add callback URL to WorkOS Dashboard

### Issue: Invalid state parameter

**Cause**: Stale OAuth flow or CSRF mismatch
**Solution**: Clear cookies and restart auth flow

## Performance Considerations

### Code Splitting

- Route is lazy-loaded by TanStack Router
- Only loaded when navigating to `/auth/callback`

### Redirect Timing

- 500ms delay before redirect (shows success state)
- Prevents jarring instant redirects
- Can be adjusted in component code

### Bundle Size

- Minimal overhead: ~2KB (component only)
- WorkOS SDK: ~15KB (shared across app)
- Lucide icons: Tree-shaken

## Related Files

- `/src/components/auth/AuthKitSync.tsx` - Token sync logic
- `/src/stores/authStore.ts` - Auth state management
- `/src/lib/auth-utils.ts` - Helper functions
- `/src/providers/app-providers.tsx` - WorkOS provider setup
- `/src/config/constants.ts` - Auth route constants

## API Endpoints (Backend)

While this route handles client-side OAuth callback, the backend may need:

- `GET /api/v1/auth/me` - Verify session
- `POST /api/v1/auth/refresh` - Refresh tokens
- `POST /api/v1/auth/logout` - Invalidate session

## Future Enhancements

- [ ] Add analytics tracking for auth success/failure
- [ ] Implement progressive enhancement for no-JS users
- [ ] Add session expiry warning
- [ ] Support multi-factor authentication flow
- [ ] Add biometric authentication option
- [ ] Implement remember-me functionality

## Changelog

### 2026-01-30 - Initial Implementation

- Created OAuth callback route
- Integrated with WorkOS AuthKit
- Added comprehensive error handling
- Implemented loading/success/error states
- Added unit tests

## Support

For issues or questions:

1. Check WorkOS documentation: https://workos.com/docs
2. Review this documentation
3. Check test suite for examples
4. Contact engineering team
