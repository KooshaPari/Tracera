# Frontend Auth Architecture Change: WorkOS AuthKit → Custom Implementation

## Summary

The frontend authentication was switched from **WorkOS AuthKit hosted UI** to a **custom, self-built authentication UI** as of commit `d21c99d06` (Feb 6, 2026).

## Timeline

- **Before**: Delegated auth entirely to WorkOS AuthKit hosted UI (used `@workos-inc/authkit-react`)
- **Change Date**: Feb 6, 2026 (commit `d21c99d060c6e9faf75618c57cf2d8e8e9a29371`)
- **Current**: Custom form-based authentication integrated with internal backend

## Detailed Changes

### Login Route (`/auth/login`)

**Before (WorkOS Hosted UI)**:
```tsx
import { useAuth } from '@workos-inc/authkit-react';

const Login = () => {
  const { user, isLoading, signIn } = useAuth();

  useEffect(() => {
    if (user && !isLoading) {
      globalThis.location.href = '/home';
    } else if (!isLoading && !user) {
      signIn?.(); // Redirects to WorkOS hosted UI
    }
  }, [user, isLoading, signIn]);

  return (
    <div>Redirecting to sign in...</div>
  );
};
```

**After (Custom Implementation)**:
```tsx
import { useAuthStore } from '@/stores/auth-store';

const Login = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate({ to: '/home' });
    } catch {
      toast.error('Invalid credentials');
    }
  };

  return (
    <div className='flex min-h-screen items-center justify-center bg-slate-950 p-4'>
      {/* Custom form with email/password fields */}
    </div>
  );
};
```

### Register Route (`/auth/register`)

**Before (WorkOS Hosted UI)**:
```tsx
import { useAuth } from '@workos-inc/authkit-react';

function Register() {
  const { user, signUp } = useAuth();

  useEffect(() => {
    if (user) {
      globalThis.location.href = '/home';
    } else {
      // Redirects to WorkOS signup UI
      signUp?.();
    }
  }, [user, signUp]);

  return <div>Redirecting to sign up...</div>;
}
```

**After (Custom Implementation)**:
```tsx
import { useAuthStore } from '@/stores/auth-store';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed');
    }

    if (data.user && data.token) {
      setUser(data.user);
      setToken(data.token);
      initializeAutoRefresh();
      toast.success('Account created successfully!');
      navigate({ to: '/home' });
    }
  };

  return (
    <div className='flex min-h-screen items-center justify-center bg-slate-950 p-4'>
      {/* Custom form with name, email, password, confirm password fields */}
    </div>
  );
};
```

## Why This Change?

### Reasons for the Switch

1. **Full Control**: Custom implementation allows complete control over the auth flow, styling, and UX
2. **Branding**: Can fully customize the authentication forms to match the application's design language
3. **Feature Flexibility**: Easier to add custom features like two-factor authentication, passwordless auth, or social logins
4. **Backend Integration**: Direct integration with the backend's auth API (`/api/v1/auth/login`, `/api/v1/auth/register`)
5. **Dependency Reduction**: Removes reliance on third-party hosted UI service
6. **Cost/Maintenance**: Eliminates dependency on WorkOS AuthKit, potentially reducing cost or maintenance overhead

### Integration with Backend

The custom auth now directly uses:
- **Auth Store** (`@/stores/auth-store`): Zustand store managing user state, token, and auto-refresh
- **Backend API**:
  - `POST /api/v1/auth/login` - Login endpoint
  - `POST /api/v1/auth/register` - Registration endpoint
  - Token-based authentication with auto-refresh mechanism

### Authentication Flow

```
User Input (Email/Password)
    ↓
Custom React Form
    ↓
useAuthStore.login() or fetch(/api/v1/auth/register)
    ↓
Backend API (Go backend)
    ↓
User + Token returned
    ↓
Store user & token in Zustand + localStorage
    ↓
Auto-refresh token every 20 minutes
    ↓
Redirect to /home
```

## UI Implementation Details

### Common Components Used
- `Button` from `@tracertm/ui`
- `Input` from `@tracertm/ui`
- `Lucide React` icons (Eye, EyeOff, Loader2)
- `Sonner` for toast notifications
- Tailwind CSS for styling (dark theme: slate-950, slate-900)

### Features
- Email/password form fields
- Show/hide password toggle
- Loading states with spinner
- Toast notifications for errors/success
- Client-side password validation (on register)
- Redirect to register/login links
- Responsive design (full screen, mobile-friendly)

## Related Files

- `frontend/apps/web/src/routes/auth.login.tsx` - Login page
- `frontend/apps/web/src/routes/auth.register.tsx` - Registration page
- `frontend/apps/web/src/routes/auth.callback.tsx` - Callback handler
- `frontend/apps/web/src/routes/auth.logout.tsx` - Logout handler
- `frontend/apps/web/src/stores/auth-store.ts` - Auth state management
- `frontend/apps/web/src/api/auth.ts` - Auth API exports
- `frontend/apps/web/src/api/auth-api.ts` - Auth API calls
- `frontend/apps/web/src/components/auth/protected-route.tsx` - Route protection
- `frontend/apps/web/src/components/auth/auth-kit-sync.tsx` - Auth kit synchronization (legacy)

## Remaining WorkOS References

Some legacy code may still reference WorkOS/AuthKit in:
- Comments or documentation
- Configuration files (if `authkit-react` is still in dependencies)
- Unused imports that can be cleaned up

## Authentication Guard

Routes are protected using `protected-route.tsx` component which checks:
1. User is authenticated (token exists)
2. User object is set in auth store
3. Redirects to `/auth/login` if not authenticated

## Token Management

The auth store handles:
- **Token Storage**: Persisted to localStorage under `auth_token` key
- **Auto-Refresh**: Refreshes token every 20 minutes to keep session alive
- **CSRF Protection**: Uses CSRF headers from `@/lib/csrf`
- **Logout**: Clears token and user from store and localStorage

## Conclusion

The shift from WorkOS AuthKit hosted UI to custom authentication gives the application:
- ✅ Full UI/UX control
- ✅ Tighter backend integration
- ✅ Reduced external dependencies
- ✅ Custom feature support
- ✅ Better branding alignment

The custom implementation is production-ready with proper error handling, token management, and secure password handling.
