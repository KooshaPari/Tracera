# Auth Routes Quick Start

## Routes Available

### Login
**URL**: `/auth/login`
**Purpose**: User login page
**Triggers**: WorkOS AuthKit sign-in flow
**Redirects to**: Dashboard (`/`) if already authenticated

### Register
**URL**: `/auth/register`
**Purpose**: New user registration
**Triggers**: WorkOS AuthKit sign-up flow
**Redirects to**: Dashboard (`/`) if already authenticated
**Link to login**: Included for existing users

### Logout
**URL**: `/auth/logout`
**Purpose**: Sign out current user
**Actions**:
1. Clears local auth state
2. Signs out from WorkOS
3. Redirects to login page

### Callback
**URL**: `/auth/callback`
**Purpose**: OAuth callback handler
**Handles**: WorkOS authentication redirect
**Flow**:
1. Processes OAuth response
2. Syncs user/token to store
3. Redirects to returnTo or dashboard

## Usage Examples

### Navigate to Login
```tsx
import { useNavigate } from '@tanstack/react-router';

const navigate = useNavigate();
navigate({ to: '/auth/login' });
```

### Logout User
```tsx
import { useNavigate } from '@tanstack/react-router';

const navigate = useNavigate();
navigate({ to: '/auth/logout' });
```

### Protected Route Pattern
```tsx
import { useAuth } from '@workos-inc/authkit-react';
import { useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';

function ProtectedPage() {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !user) {
      navigate({ to: '/auth/login' });
    }
  }, [user, isLoading, navigate]);

  if (isLoading) return <div>Loading...</div>;
  if (!user) return null;

  return <div>Protected content</div>;
}
```

### Check Auth Status
```tsx
import { useAuth } from '@workos-inc/authkit-react';

function Header() {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {user ? (
        <a href="/auth/logout">Logout</a>
      ) : (
        <a href="/auth/login">Login</a>
      )}
    </div>
  );
}
```

## Environment Setup

### Required Variables
```env
# .env or .env.local
VITE_WORKOS_CLIENT_ID=client_your_workos_client_id_here
VITE_API_URL=http://localhost:4000
```

### WorkOS Dashboard Configuration
1. Add redirect URI: `http://localhost:5173/` (dev)
2. Add redirect URI: `https://your-domain.com/` (prod)
3. Enable desired auth providers (Google, GitHub, etc.)

## Testing Flow

### Manual Test
1. Start dev server: `cd frontend/apps/web && bun run dev`
2. Navigate to `http://localhost:5173/auth/login`
3. Click "Sign In with WorkOS"
4. Complete authentication on WorkOS
5. Verify redirect to dashboard
6. Navigate to `/auth/logout`
7. Verify redirect to login page

### Test with ReturnTo
1. Navigate to: `http://localhost:5173/auth/login?returnTo=/projects`
2. Complete login
3. Verify redirect to `/projects` (not dashboard)

## Common Issues

### Issue: "Client ID not found"
**Solution**: Ensure `VITE_WORKOS_CLIENT_ID` is set in `.env`

### Issue: "Redirect URI mismatch"
**Solution**: Add exact redirect URI to WorkOS dashboard (including trailing slash)

### Issue: Routes not found (404)
**Solution**: Restart dev server to regenerate route tree

### Issue: Already authenticated but showing login
**Solution**: Check browser console for AuthKit errors, verify CSRF token

### Issue: Infinite redirect loop
**Solution**: Check `returnTo` parameter is not an auth route

## File Locations

```
frontend/apps/web/
├── src/
│   ├── routes/
│   │   ├── auth.login.tsx       # Login page
│   │   ├── auth.register.tsx    # Registration page
│   │   ├── auth.logout.tsx      # Logout handler
│   │   └── auth.callback.tsx    # OAuth callback
│   ├── stores/
│   │   └── authStore.ts         # Auth state management
│   ├── lib/
│   │   └── auth-utils.ts        # Auth utilities
│   └── components/
│       └── auth/
│           └── AuthKitSync.tsx  # WorkOS sync
└── .env                          # Environment variables
```

## Next Steps

1. Configure WorkOS dashboard with your domain
2. Test authentication flow in development
3. Add protected routes using `ProtectedRoute` component
4. Implement role-based access control if needed
5. Add email verification flow (optional)
6. Configure password reset flow (optional)

## Documentation Links

- [WorkOS AuthKit Docs](https://workos.com/docs/user-management/authkit)
- [TanStack Router Docs](https://tanstack.com/router/latest)
- [Auth Store Implementation](/frontend/apps/web/src/stores/authStore.ts)
- [Auth API Client](/frontend/apps/web/src/api/auth.ts)

## Status
✅ All routes implemented and verified
✅ WorkOS integration complete
✅ TanStack Router integration complete
✅ Dev server tested and working
