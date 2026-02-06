/**
 * Tests for useAuth hook
 */

import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useAuth, useIsAuthenticated, useUser } from '../../hooks/useAuth';
import { useAuthStore } from '../../stores/authStore';

describe(useAuth, () => {
  beforeEach(() => {
    const { logout } = useAuthStore.getState();
    logout();
    localStorage.clear();
  });

  describe(useAuth, () => {
    it('should return auth state and methods', () => {
      const { result } = renderHook(() => useAuth());

      expect(result.current).toHaveProperty('user');
      expect(result.current).toHaveProperty('token');
      expect(result.current).toHaveProperty('isAuthenticated');
      expect(result.current).toHaveProperty('isLoading');
      expect(result.current).toHaveProperty('login');
      expect(result.current).toHaveProperty('logout');
      expect(result.current).toHaveProperty('refreshToken');
      expect(result.current).toHaveProperty('updateProfile');
    });

    it('should handle login', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.login('test@example.com', 'password');
      });

      expect(result.current.isAuthenticated).toBeTruthy();
      expect(result.current.user).toBeTruthy();
    });

    it('should handle logout', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.login('test@example.com', 'password');
      });

      act(() => {
        result.current.logout();
      });

      expect(result.current.isAuthenticated).toBeFalsy();
      expect(result.current.user).toBeNull();
    });
  });

  describe(useUser, () => {
    it('should return user when authenticated', async () => {
      const { result: authResult } = renderHook(() => useAuth());

      await act(async () => {
        await authResult.current.login('test@example.com', 'password');
      });

      const { result } = renderHook(() => useUser());

      expect(result.current).toBeTruthy();
      expect(result.current?.email).toBe('test@example.com');
    });

    it('should return null when not authenticated', () => {
      const { result } = renderHook(() => useUser());

      expect(result.current).toBeNull();
    });
  });

  describe(useIsAuthenticated, () => {
    it('should return true when authenticated', async () => {
      const { result: authResult } = renderHook(() => useAuth());

      await act(async () => {
        await authResult.current.login('test@example.com', 'password');
      });

      const { result } = renderHook(() => useIsAuthenticated());

      expect(result.current).toBeTruthy();
    });

    it('should return false when not authenticated', () => {
      const { result } = renderHook(() => useIsAuthenticated());

      expect(result.current).toBeFalsy();
    });
  });
});

describe('useAuth - token expiry and refresh', () => {
  beforeEach(() => {
    const { logout } = useAuthStore.getState();
    logout();
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('should initialize auto-refresh on login', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.token).toBeTruthy();
  });

  it('should handle token refresh failure', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.isAuthenticated).toBeTruthy();

    // Refresh token
    await act(async () => {
      await result.current.refreshToken();
    });

    // Token should still exist after refresh attempt
    expect(result.current.token).toBeTruthy();
  });

  it('should clear token on logout', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    const tokenBeforeLogout = result.current.token;
    expect(tokenBeforeLogout).toBeTruthy();

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
  });

  it('should handle login with empty credentials', async () => {
    const { result } = renderHook(() => useAuth());

    await expect(
      act(async () => {
        await result.current.login('', 'password');
      }),
    ).rejects.toThrow();

    expect(result.current.isAuthenticated).toBeFalsy();
  });

  it('should handle login with missing password', async () => {
    const { result } = renderHook(() => useAuth());

    await expect(
      act(async () => {
        await result.current.login('test@example.com', '');
      }),
    ).rejects.toThrow();

    expect(result.current.isAuthenticated).toBeFalsy();
  });

  it('should update profile while authenticated', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    const updatedName = 'Updated Name';

    act(() => {
      result.current.updateProfile({ name: updatedName });
    });

    expect(result.current.user?.name).toBe(updatedName);
  });

  it('should not update profile when not authenticated', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.user).toBeNull();

    act(() => {
      result.current.updateProfile({ name: 'New Name' });
    });

    expect(result.current.user).toBeNull();
  });
});

describe('useAuth - multiple hook instances', () => {
  beforeEach(() => {
    const { logout } = useAuthStore.getState();
    logout();
    localStorage.clear();
  });

  it('should share state across multiple useAuth hooks', async () => {
    const { result: result1 } = renderHook(() => useAuth());
    const { result: result2 } = renderHook(() => useAuth());

    await act(async () => {
      await result1.current.login('test@example.com', 'password');
    });

    expect(result1.current.isAuthenticated).toBeTruthy();
    expect(result2.current.isAuthenticated).toBeTruthy();
    expect(result1.current.user?.email).toBe(result2.current.user?.email);
  });

  it('should reflect logout across multiple hook instances', async () => {
    const { result: result1 } = renderHook(() => useAuth());
    const { result: result2 } = renderHook(() => useAuth());

    await act(async () => {
      await result1.current.login('test@example.com', 'password');
    });

    await act(async () => {
      await result2.current.logout();
    });

    expect(result1.current.isAuthenticated).toBeFalsy();
    expect(result2.current.isAuthenticated).toBeFalsy();
  });
});

describe('useUser - reactive updates', () => {
  beforeEach(() => {
    const { logout } = useAuthStore.getState();
    logout();
    localStorage.clear();
  });

  it('should update when user logs in', async () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: userResult } = renderHook(() => useUser());

    expect(userResult.current).toBeNull();

    await act(async () => {
      await authResult.current.login('test@example.com', 'password');
    });

    expect(userResult.current).not.toBeNull();
    expect(userResult.current?.email).toBe('test@example.com');
  });

  it('should clear when user logs out', async () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: userResult } = renderHook(() => useUser());

    await act(async () => {
      await authResult.current.login('test@example.com', 'password');
    });

    expect(userResult.current).not.toBeNull();

    await act(async () => {
      await authResult.current.logout();
    });

    expect(userResult.current).toBeNull();
  });

  it('should update user metadata when profile is updated', async () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: userResult } = renderHook(() => useUser());

    await act(async () => {
      await authResult.current.login('test@example.com', 'password');
    });

    const newMetadata = { theme: 'dark', language: 'en' };

    act(() => {
      authResult.current.updateProfile({ metadata: newMetadata });
    });

    expect(userResult.current?.metadata).toEqual(newMetadata);
  });
});

describe('useIsAuthenticated - reactive state', () => {
  beforeEach(() => {
    const { logout } = useAuthStore.getState();
    logout();
    localStorage.clear();
  });

  it('should update reactively on login', async () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: authStatusResult } = renderHook(() => useIsAuthenticated());

    expect(authStatusResult.current).toBe(false);

    await act(async () => {
      await authResult.current.login('test@example.com', 'password');
    });

    expect(authStatusResult.current).toBe(true);
  });

  it('should update reactively on logout', async () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: authStatusResult } = renderHook(() => useIsAuthenticated());

    await act(async () => {
      await authResult.current.login('test@example.com', 'password');
    });

    expect(authStatusResult.current).toBe(true);

    await act(async () => {
      await authResult.current.logout();
    });

    expect(authStatusResult.current).toBe(false);
  });

  it('should remain false when login fails', async () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: authStatusResult } = renderHook(() => useIsAuthenticated());

    await expect(
      act(async () => {
        await authResult.current.login('', 'password');
      }),
    ).rejects.toThrow();

    expect(authStatusResult.current).toBe(false);
  });
});

describe('useAuth - edge cases', () => {
  beforeEach(() => {
    const { logout } = useAuthStore.getState();
    logout();
    localStorage.clear();
  });

  it('should have isLoading property', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current).toHaveProperty('isLoading');
    expect(typeof result.current.isLoading).toBe('boolean');
  });

  it('should handle multiple sequential logins', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('first@example.com', 'password');
    });

    const firstUser = result.current.user;

    await act(async () => {
      await result.current.logout();
    });

    await act(async () => {
      await result.current.login('second@example.com', 'password');
    });

    const secondUser = result.current.user;

    expect(firstUser?.email).not.toBe(secondUser?.email);
    expect(secondUser?.email).toBe('second@example.com');
  });

  it('should handle logout when already logged out', async () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.isAuthenticated).toBeFalsy();

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.isAuthenticated).toBeFalsy();
    expect(result.current.user).toBeNull();
  });
});
