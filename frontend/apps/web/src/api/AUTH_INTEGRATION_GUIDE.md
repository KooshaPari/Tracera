# Authentication API Client Integration Guide

## Overview

The authentication API client (`auth.ts`) provides a type-safe, comprehensive interface for all authentication-related operations. It handles login, token refresh, password management, and user profile updates with automatic CSRF protection and cookie-based authentication.

## Quick Start

### Basic Login

```typescript
import { authApi, AuthError, isAuthError } from '@/api/auth';

async function handleLogin(email: string, password: string) {
  try {
    const { user, token } = await authApi.login({ email, password });

    // Store token
    localStorage.setItem('auth_token', token);

    // Update auth state
    authStore.setUser(user);
    authStore.setToken(token);

    // Redirect to dashboard
    navigate('/dashboard');
  } catch (error) {
    if (isAuthError(error)) {
      // Handle auth-specific errors
      showError(getAuthErrorMessage(error));
    } else {
      showError('An unexpected error occurred');
    }
  }
}
```

### Session Recovery

```typescript
import { authApi } from '@/api/auth';

async function restoreSession() {
  try {
    const user = await authApi.getCurrentUser();

    if (user) {
      // User is still authenticated
      authStore.setUser(user);
    } else {
      // No active session
      authStore.logout();
    }
  } catch (error) {
    // Server error, but don't logout
    console.error('Failed to restore session:', error);
  }
}
```

### Token Refresh

```typescript
import { authApi } from '@/api/auth';

async function refreshToken() {
  try {
    const { token } = await authApi.refresh();

    // Update stored token
    localStorage.setItem('auth_token', token);
    authStore.setToken(token);
  } catch (error) {
    // Token refresh failed, logout user
    authStore.logout();
    navigate('/login');
  }
}
```

### Logout

```typescript
import { authApi } from '@/api/auth';

async function handleLogout() {
  try {
    // Notify server
    await authApi.logout();
  } catch (error) {
    console.error('Logout failed:', error);
  } finally {
    // Always clear local state
    localStorage.removeItem('auth_token');
    authStore.logout();
    navigate('/login');
  }
}
```

## API Methods

### `login(credentials: LoginRequest): Promise<AuthResponse>`

Authenticates a user with email and password.

**Parameters:**
- `email`: User's email address
- `password`: User's password

**Returns:** `{ user, token, expiresIn?, refreshToken? }`

**Errors:**
- `401 INVALID_CREDENTIALS` - Wrong email or password
- `404 USER_NOT_FOUND` - User doesn't exist
- `403 USER_DISABLED` - Account is disabled
- `429` - Too many login attempts

**Example:**
```typescript
const { user, token } = await authApi.login({
  email: 'user@example.com',
  password: 'secure-password'
});
```

---

### `getCurrentUser(): Promise<User | null>`

Retrieves the currently authenticated user's profile. Returns `null` if not authenticated (non-throwing).

**Returns:** `User | null`

**Example:**
```typescript
const user = await authApi.getCurrentUser();
if (user) {
  console.log('Logged in as:', user.name);
} else {
  console.log('Not authenticated');
}
```

---

### `refresh(): Promise<AuthResponse>`

Refreshes the authentication token using the current session.

**Returns:** `{ user, token, expiresIn?, refreshToken? }`

**Errors:**
- `401` - Session expired or invalid

**Example:**
```typescript
const { token } = await authApi.refresh();
localStorage.setItem('auth_token', token);
```

---

### `logout(): Promise<void>`

Logs out the current user and invalidates the session.

**Errors:** May throw on server errors, but local logout should proceed regardless.

**Example:**
```typescript
try {
  await authApi.logout();
} finally {
  localStorage.removeItem('auth_token');
  authStore.logout();
}
```

---

### `updateProfile(updates: UpdateUserProfileRequest): Promise<User>`

Updates the current user's profile information.

**Parameters:**
- `name?`: User's display name
- `avatar?`: Avatar URL
- `metadata?`: Custom metadata object

**Returns:** Updated `User` object

**Example:**
```typescript
const updated = await authApi.updateProfile({
  name: 'John Doe',
  avatar: 'https://example.com/avatar.jpg'
});
authStore.setUser(updated);
```

---

### `changePassword(request: ChangePasswordRequest): Promise<void>`

Changes the password for the current user.

**Parameters:**
- `currentPassword`: Current password for verification
- `newPassword`: New password
- `confirmPassword`: Password confirmation

**Errors:**
- `401 INVALID_PASSWORD` - Current password is wrong
- `400 PASSWORD_MISMATCH` - New passwords don't match

**Example:**
```typescript
await authApi.changePassword({
  currentPassword: 'old-password',
  newPassword: 'new-password',
  confirmPassword: 'new-password'
});
```

---

### `requestPasswordReset(request: ResetPasswordRequest): Promise<void>`

Requests a password reset email. Returns success regardless of whether email exists (for security).

**Parameters:**
- `email`: User's email address

**Example:**
```typescript
await authApi.requestPasswordReset({
  email: 'user@example.com'
});
// Show: "Check your email for reset link"
```

---

### `confirmPasswordReset(request: ResetPasswordConfirm): Promise<void>`

Completes password reset using a token from the reset email.

**Parameters:**
- `token`: Token from reset email
- `newPassword`: New password
- `confirmPassword`: Password confirmation

**Errors:**
- `400 INVALID_TOKEN` - Token is invalid or expired

**Example:**
```typescript
// User clicks link in email: /reset-password?token=...
const token = new URLSearchParams(location.search).get('token');

await authApi.confirmPasswordReset({
  token,
  newPassword: 'new-password',
  confirmPassword: 'new-password'
});

// Redirect to login
navigate('/login');
```

---

### `verifyEmail(token: string): Promise<void>`

Verifies email address using a token from verification email.

**Parameters:**
- `token`: Email verification token

**Errors:**
- `400 INVALID_TOKEN` - Token is invalid or expired

**Example:**
```typescript
const token = new URLSearchParams(location.search).get('token');
await authApi.verifyEmail(token);
```

---

### `requestEmailVerification(): Promise<void>`

Requests a new email verification link.

**Example:**
```typescript
await authApi.requestEmailVerification();
// Show: "Verification email sent"
```

---

### `deleteAccount(): Promise<void>`

Permanently deletes the user account and all data. This action is irreversible.

**Example:**
```typescript
const confirmed = confirm('Are you sure? This cannot be undone.');
if (confirmed) {
  await authApi.deleteAccount();
  authStore.logout();
  navigate('/');
}
```

---

## Error Handling

### AuthError Class

All auth API methods throw `AuthError` on failure (except `getCurrentUser` which returns `null` on 401).

```typescript
export class AuthError extends Error {
  statusCode: number;      // HTTP status code
  code?: string;           // Error code (e.g., 'INVALID_CREDENTIALS')
  details?: Record<string, any>;  // Additional error details
}
```

### Type Guard

Use `isAuthError()` to safely check for auth errors:

```typescript
import { isAuthError } from '@/api/auth';

try {
  await authApi.login(credentials);
} catch (error) {
  if (isAuthError(error)) {
    // Handle auth error
    console.log(error.code, error.statusCode);
  } else {
    // Handle other errors
  }
}
```

### Error Messages

Use `getAuthErrorMessage()` to get user-friendly error messages:

```typescript
import { getAuthErrorMessage } from '@/api/auth';

try {
  await authApi.login(credentials);
} catch (error) {
  if (isAuthError(error)) {
    const message = getAuthErrorMessage(error);
    // "Invalid email or password"
    // "Too many login attempts, please try again later"
    // "Security token missing, please refresh the page"
    showToast(message);
  }
}
```

### Logout On Error

Use `shouldLogoutOnError()` to determine if user should be logged out:

```typescript
import { shouldLogoutOnError } from '@/api/auth';

try {
  await apiCall();
} catch (error) {
  if (isAuthError(error) && shouldLogoutOnError(error)) {
    // Session expired or token invalid
    authStore.logout();
    navigate('/login');
  }
}
```

---

## Integration with Auth Store

### Login Flow

```typescript
import { useAuthStore } from '@/stores/authStore';
import { authApi } from '@/api/auth';

export function useLogin() {
  const authStore = useAuthStore();

  return async (email: string, password: string) => {
    try {
      const { user, token } = await authApi.login({ email, password });

      authStore.setUser(user);
      authStore.setToken(token);

      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };
}
```

### Session Initialization

```typescript
import { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { authApi } from '@/api/auth';

export function SessionProvider({ children }) {
  const authStore = useAuthStore();

  useEffect(() => {
    const initSession = async () => {
      const user = await authApi.getCurrentUser();
      if (user) {
        authStore.setUser(user);
      }
    };

    initSession();
  }, [authStore]);

  return children;
}
```

---

## CSRF Integration

The auth API automatically handles CSRF protection:

1. **Automatic Token Fetching**: CSRF token is fetched on first state-changing request
2. **Token Caching**: Token is cached in memory for subsequent requests
3. **Automatic Injection**: Token is added to all POST/PUT/DELETE requests
4. **Error Recovery**: 403 CSRF errors trigger automatic token refresh and retry

**Manual CSRF Initialization** (optional):

```typescript
import { initializeCSRF } from '@/lib/csrf';

// In app startup
await initializeCSRF();
```

---

## Cookie-Based Authentication

The auth API uses `credentials: 'include'` for all requests:

- Authentication cookies are automatically sent with every request
- Response cookies are automatically stored by the browser
- No manual cookie handling required

---

## Type Safety

All API methods are fully typed with TypeScript:

```typescript
import type {
  User,
  AuthResponse,
  LoginRequest,
  ChangePasswordRequest,
} from '@/api/auth';

const response: AuthResponse = await authApi.login(credentials);
const user: User = response.user;
```

---

## Testing

### Unit Tests

```typescript
import { authApi, AuthError } from '@/api/auth';

describe('authApi.login', () => {
  it('should throw AuthError on invalid credentials', async () => {
    await expect(
      authApi.login({ email: 'user@example.com', password: 'wrong' })
    ).rejects.toThrow(AuthError);
  });
});
```

### Integration Tests

```typescript
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'user@example.com');
  await page.fill('input[type="password"]', 'password');
  await page.click('button:has-text("Login")');

  // Should redirect to dashboard
  await expect(page).toHaveURL('/dashboard');
});
```

---

## Best Practices

### 1. Always Handle Logout Errors

```typescript
async function logout() {
  try {
    await authApi.logout();
  } catch (error) {
    console.error('Logout failed:', error);
  } finally {
    // Always clear local state
    authStore.logout();
    navigate('/login');
  }
}
```

### 2. Implement Token Refresh

```typescript
// Setup interceptor or hook to refresh token before expiration
const { expiresIn } = await authApi.login(credentials);
const refreshTime = (expiresIn - 300) * 1000; // 5 min before expiry

setTimeout(async () => {
  await authApi.refresh();
}, refreshTime);
```

### 3. Handle Session Restoration

```typescript
// On app startup
const user = await authApi.getCurrentUser();
if (user) {
  authStore.setUser(user);
} else {
  authStore.logout();
}
```

### 4. User-Friendly Error Messages

```typescript
import { getAuthErrorMessage } from '@/api/auth';

try {
  await authApi.login(credentials);
} catch (error) {
  if (isAuthError(error)) {
    toast.error(getAuthErrorMessage(error));
  }
}
```

### 5. Secure Password Handling

- Never log passwords
- Use HTTPS in production
- Implement rate limiting on login (429 response)
- Clear password from memory after submission

---

## Common Patterns

### Protected Route Hook

```typescript
import { useAuthStore } from '@/stores/authStore';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

export function useProtectedRoute() {
  const authStore = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!authStore.isAuthenticated) {
      navigate('/login');
    }
  }, [authStore.isAuthenticated, navigate]);
}
```

### Auto-Logout on Token Expiry

```typescript
import { useAuthStore } from '@/stores/authStore';
import { useEffect } from 'react';

export function useAutoLogout() {
  const authStore = useAuthStore();

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_token' && e.newValue === null) {
        authStore.logout();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [authStore]);
}
```

### Profile Update with Validation

```typescript
import { authApi, isAuthError } from '@/api/auth';

async function updateUserProfile(name: string) {
  if (!name || name.trim().length === 0) {
    throw new Error('Name cannot be empty');
  }

  try {
    const updated = await authApi.updateProfile({ name });
    authStore.setUser(updated);
    return true;
  } catch (error) {
    if (isAuthError(error) && error.statusCode === 400) {
      throw new Error('Invalid profile data');
    }
    throw error;
  }
}
```

---

## API Endpoint Specification

All endpoints are served from `/api/v1/auth/`:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/login` | Login with credentials |
| POST | `/refresh` | Refresh authentication token |
| POST | `/logout` | Logout current user |
| GET | `/me` | Get current user profile |
| PUT | `/profile` | Update user profile |
| POST | `/change-password` | Change password |
| POST | `/reset-password` | Request password reset |
| POST | `/reset-password/confirm` | Confirm password reset |
| POST | `/verify-email` | Verify email with token |
| POST | `/request-verification` | Request verification email |
| DELETE | `/account` | Delete user account |

---

## Troubleshooting

### "CSRF token missing" Error

- CSRF token is automatically fetched on first request
- If error persists, check that GET `/api/v1/csrf-token` is accessible
- Try refreshing the page to force CSRF initialization

### "Session expired" Error

- Token has expired, implement token refresh logic
- Use `authApi.refresh()` to get a new token
- Falls back to login if refresh fails

### 401 Unauthorized on API Calls

- May indicate token expiration
- Call `authApi.refresh()` and retry the request
- If refresh fails, logout user

### Cookies Not Being Sent

- Ensure `credentials: 'include'` is set (done automatically)
- Check that frontend and backend are same-origin or CORS is properly configured
- Verify SameSite cookie attribute if cross-origin

---

## Migration from Old Auth System

If migrating from a different auth system:

1. **Replace imports:**
   ```typescript
   // Old
   import { login } from '@/services/auth';

   // New
   import { authApi } from '@/api/auth';
   ```

2. **Update error handling:**
   ```typescript
   // Old
   catch (error: any) { ... }

   // New
   catch (error) {
     if (isAuthError(error)) { ... }
   }
   ```

3. **Update token storage:**
   - Continue storing token in localStorage
   - API client will automatically inject it in Authorization header

4. **Update CSRF handling:**
   - Remove any manual CSRF token management
   - API client handles it automatically

---

## Support

For issues or questions:
1. Check the test file: `src/__tests__/api/auth.comprehensive.test.ts`
2. Review error messages from `getAuthErrorMessage()`
3. Enable debug logging: Check browser console for `[CSRF]` and auth-related logs
4. Examine response status codes and error codes from AuthError
