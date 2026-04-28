# Route Protection Implementation

This document describes the frontend route protection system implemented using TanStack Router's `beforeLoad` hook.

## Overview

All protected routes now use the `requireAuth()` guard to ensure users are authenticated before accessing the route. Unauthenticated users are automatically redirected to the landing page (`/`) with a `returnTo` parameter to enable seamless return to the intended destination after login.

## Implementation

### Route Guard Utility

The route guards are defined in `/src/lib/route-guards.ts` and provide:

1. **`requireAuth(options?)`** - Basic authentication check
   - Redirects to `/` (or custom path) if not authenticated
   - Includes `returnTo` query parameter by default
   - Throws TanStack Router `redirect` exception

2. **`requireAuthWithAccount(options?)`** - Authentication + account check
   - Checks both user authentication and account context
   - Redirects to account selection if no account is set
   - Useful for multi-tenant features

3. **`checkAuth()`** - Non-blocking auth state check
   - Returns current auth state without redirecting
   - Useful for conditional rendering in components

### Usage Pattern

```typescript
import { createFileRoute } from '@tanstack/react-router';
import { requireAuth } from '@/lib/route-guards';

export const Route = createFileRoute('/protected-route')({
  beforeLoad: () => requireAuth(),
  component: ProtectedComponent,
});
```

### Advanced Usage

```typescript
// Custom redirect destination
beforeLoad: () => requireAuth({ redirectTo: '/auth/login' });

// Disable returnTo parameter
beforeLoad: () => requireAuth({ includeReturnUrl: false });

// Require account context
beforeLoad: () => requireAuthWithAccount();

// Multiple checks in beforeLoad
beforeLoad: () => {
  requireAuth();
  // Additional validation logic
};
```

## Protected Routes

All routes under the following paths are now protected:

### Project Routes

- `/projects/` - Project list
- `/projects/:projectId` - All project detail pages
- `/projects/:projectId/views/:viewType` - All view types
- `/projects/:projectId/specifications` - Specifications dashboard
- `/projects/:projectId/settings` - Project settings
- `/projects/:projectId/features` - Features (redirects to specifications)
- `/projects/:projectId/features/:featureId` - Feature details
- `/projects/:projectId/features/:featureId/scenarios/:scenarioId` - Scenario details
- `/projects/:projectId/adrs` - ADRs (redirects to specifications)
- `/projects/:projectId/adrs/:adrId` - ADR details
- `/projects/:projectId/contracts` - Contracts (redirects to specifications)
- `/projects/:projectId/contracts/:contractId` - Contract details
- `/projects/:projectId/compliance` - Compliance (redirects to specifications)
- `/projects/:projectId/agents` - Agent workflows
- `/projects/:projectId/equivalence` - Equivalence management
- `/projects/:projectId/scenario-activity` - Scenario activity
- `/projects/:projectId/temporal` - Temporal navigation
- `/projects/:projectId/views/:viewType/:itemId` - Item details

### Other Protected Routes

- `/home` - Dashboard
- `/settings/` - User settings
- `/items/:itemId` - Legacy item redirect

### Public Routes

These routes remain accessible without authentication:

- `/` - Landing page (redirects to `/home` if authenticated)
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/auth/logout` - Logout handler
- `/auth/callback` - OAuth callback

## Authentication Flow

1. **Initial Request**: User navigates to protected route
2. **Auth Check**: `beforeLoad` executes `requireAuth()`
3. **Not Authenticated**:
   - Redirect to `/` (landing page)
   - Include `returnTo` query parameter with original URL
   - Landing page shows login UI
4. **After Login**:
   - Check for `returnTo` parameter
   - Redirect to original destination
   - User continues their workflow

## Testing

Route guards can be tested using the test suite at:

- `/src/__tests__/route-guards.test.ts`

Run tests:

```bash
bun test route-guards
```

## Migration from ProtectedRoute Component

The old `ProtectedRoute` wrapper component is deprecated but still available for backward compatibility:

**Old Pattern (Deprecated):**

```typescript
function Component() {
  return (
    <ProtectedRoute>
      <YourContent />
    </ProtectedRoute>
  );
}
```

**New Pattern (Recommended):**

```typescript
export const Route = createFileRoute('/route')({
  beforeLoad: () => requireAuth(),
  component: YourContent,
});
```

### Benefits of New Approach

1. **Earlier Redirect**: Auth check happens before component render
2. **Cleaner Code**: No wrapper components needed
3. **Better DX**: TypeScript-first with proper types
4. **Centralized Logic**: All route config in one place
5. **Proper Loading States**: TanStack Router handles pending states
6. **Return URL Support**: Automatic returnTo parameter handling

## Architecture Notes

### Why beforeLoad instead of loader?

- `beforeLoad` runs before `loader`, ensuring auth check happens first
- Can throw redirect before any data fetching occurs
- Prevents unnecessary API calls for unauthenticated users
- Clearer separation of concerns

### Why not use middleware/layout?

- TanStack Router doesn't have traditional middleware
- Route-level guards provide fine-grained control
- Each route explicitly declares its auth requirements
- Easier to understand and maintain

### Session Validation

The auth store automatically:

- Validates session on mount
- Refreshes tokens every 20 minutes
- Handles token expiration
- Clears state on logout

See `/src/stores/authStore.ts` for implementation details.

## Troubleshooting

### Redirect Loop

If you experience redirect loops:

1. Check that `/` route doesn't have `requireAuth()`
2. Ensure auth state is properly initialized
3. Clear localStorage and cookies
4. Check browser console for errors

### returnTo Not Working

1. Verify `includeReturnUrl` is not set to `false`
2. Check browser allows query parameters
3. Ensure landing page handles `returnTo` parameter

### Auth State Not Persisting

1. Check browser localStorage is enabled
2. Verify Zustand persist middleware is working
3. Check for errors in auth store initialization
4. Ensure cookies are enabled for HttpOnly tokens

## Future Enhancements

Potential improvements to consider:

1. **Role-Based Access Control**

   ```typescript
   requireAuth({ roles: ['admin', 'editor'] });
   ```

2. **Permission Checks**

   ```typescript
   requirePermission('projects.edit');
   ```

3. **Rate Limiting**
   - Track auth check frequency
   - Prevent brute force attempts

4. **Analytics**
   - Track unauthorized access attempts
   - Monitor auth flow completion rates

## Related Files

- `/src/lib/route-guards.ts` - Route guard utilities
- `/src/stores/authStore.ts` - Authentication state management
- `/src/hooks/useAuth.ts` - Auth hooks
- `/src/components/auth/ProtectedRoute.tsx` - Legacy wrapper (deprecated)
- `/src/routes/__root.tsx` - Root route configuration

## Support

For issues or questions about route protection:

1. Check this documentation
2. Review test suite for examples
3. Check auth store implementation
4. Review TanStack Router documentation
