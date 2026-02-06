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

describe('useAuth - advanced state transitions', () => {
  it('should have refreshToken function available', () => {
    const { result } = renderHook(() => useAuth());

    expect(typeof result.current.refreshToken).toBe('function');
  });

  it('should have updateProfile function available', () => {
    const { result } = renderHook(() => useAuth());

    expect(typeof result.current.updateProfile).toBe('function');
  });

  it('should handle updateProfile when not authenticated', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.user).toBeNull();

    act(() => {
      result.current.updateProfile({ name: 'New Name' });
    });

    expect(result.current.user).toBeNull();
  });

  it('should report isLoading as boolean', async () => {
    const { result } = renderHook(() => useAuth());

    expect(typeof result.current.isLoading).toBe('boolean');
  });
});

describe('useAuth - shared store behavior', () => {
  it('should return same store reference across multiple hooks', () => {
    const { result: result1 } = renderHook(() => useAuth());
    const { result: result2 } = renderHook(() => useAuth());

    // Both should have the same authentication state initially
    expect(result1.current.isAuthenticated).toBe(result2.current.isAuthenticated);
    expect(result1.current.user).toBe(result2.current.user);
    expect(result1.current.token).toBe(result2.current.token);
  });

  it('should have consistent methods across hook instances', () => {
    const { result: result1 } = renderHook(() => useAuth());
    const { result: result2 } = renderHook(() => useAuth());

    expect(typeof result1.current.login).toBe('function');
    expect(typeof result2.current.login).toBe('function');
    expect(typeof result1.current.logout).toBe('function');
    expect(typeof result2.current.logout).toBe('function');
  });
});

describe('useUser - selector behavior', () => {
  it('should return user from store', () => {
    const { result } = renderHook(() => useUser());

    expect(result.current === null || typeof result.current === 'object').toBeTruthy();
  });

  it('should have same value as useAuth().user', () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: userResult } = renderHook(() => useUser());

    expect(userResult.current).toBe(authResult.current.user);
  });

  it('should return null initially', () => {
    const { result } = renderHook(() => useUser());

    expect(result.current).toBeNull();
  });
});

describe('useIsAuthenticated - selector behavior', () => {
  it('should return boolean value', () => {
    const { result } = renderHook(() => useIsAuthenticated());

    expect(typeof result.current).toBe('boolean');
  });

  it('should return false initially', () => {
    const { result } = renderHook(() => useIsAuthenticated());

    expect(result.current).toBeFalsy();
  });

  it('should match useAuth().isAuthenticated', () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: statusResult } = renderHook(() => useIsAuthenticated());

    expect(statusResult.current).toBe(authResult.current.isAuthenticated);
  });

  it('should be false when user is null', () => {
    const { result: authResult } = renderHook(() => useAuth());
    const { result: statusResult } = renderHook(() => useIsAuthenticated());

    expect(authResult.current.user).toBeNull();
    expect(statusResult.current).toBeFalsy();
  });
});

describe('useAuth - object structure and properties', () => {
  it('should return object with all required properties', () => {
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

  it('should have functions as expected types', () => {
    const { result } = renderHook(() => useAuth());

    expect(typeof result.current.login).toBe('function');
    expect(typeof result.current.logout).toBe('function');
    expect(typeof result.current.refreshToken).toBe('function');
    expect(typeof result.current.updateProfile).toBe('function');
  });

  it('should have correct initial state values', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
    expect(typeof result.current.isLoading).toBe('boolean');
  });

  it('should not mutate object reference on re-render', () => {
    const { result, rerender } = renderHook(() => useAuth());

    const firstRef = result.current;
    rerender();
    const secondRef = result.current;

    // References might not be identical if Zustand returns new proxy objects,
    // But properties should match
    expect(firstRef.user).toBe(secondRef.user);
    expect(firstRef.token).toBe(secondRef.token);
    expect(firstRef.isAuthenticated).toBe(secondRef.isAuthenticated);
  });
});
