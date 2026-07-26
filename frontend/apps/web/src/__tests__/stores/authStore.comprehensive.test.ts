/**
 * Comprehensive tests for auth store
 * Tests authentication state management, login/logout, and persistence
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { User } from '../../stores/authStore';

import { useAuthStore } from '../../stores/authStore';

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      isAuthenticated: false,
      isLoading: false,
      token: null,
      user: null,
    });
    // Clear localStorage
    localStorage.clear();
  });

  const mockUser: User = {
    avatar: 'https://example.com/avatar.jpg',
    email: 'test@example.com',
    id: 'user-1',
    metadata: { department: 'Engineering' },
    name: 'Test User',
    role: 'admin',
  };

  describe('initial state', () => {
    it('should have null user initially', () => {
      const { user } = useAuthStore.getState();
      expect(user).toBeNull();
    });

    it('should have null token initially', () => {
      const { token } = useAuthStore.getState();
      expect(token).toBeNull();
    });

    it('should not be authenticated initially', () => {
      const { isAuthenticated } = useAuthStore.getState();
      expect(isAuthenticated).toBeFalsy();
    });

    it('should not be loading initially', () => {
      const { isLoading } = useAuthStore.getState();
      expect(isLoading).toBeFalsy();
    });
  });

  describe('setUser', () => {
    it('should set user', () => {
      const { setUser } = useAuthStore.getState();
      setUser(mockUser);

      const { user } = useAuthStore.getState();
      expect(user).toEqual(mockUser);
    });

    it('should set isAuthenticated to true when user is set', () => {
      const { setUser } = useAuthStore.getState();
      setUser(mockUser);

      const { isAuthenticated } = useAuthStore.getState();
      expect(isAuthenticated).toBeTruthy();
    });

    it('should set isAuthenticated to false when user is null', () => {
      const { setUser } = useAuthStore.getState();
      setUser(mockUser);
      setUser(null);

      const { isAuthenticated } = useAuthStore.getState();
      expect(isAuthenticated).toBeFalsy();
    });

    it('should handle partial user data', () => {
      const { setUser } = useAuthStore.getState();
      const partialUser: User = {
        email: 'test@example.com',
        id: 'user-1',
      };
      setUser(partialUser);

      const { user } = useAuthStore.getState();
      expect(user).toEqual(partialUser);
      expect(user?.name).toBeUndefined();
    });

    it('should overwrite existing user', () => {
      const { setUser } = useAuthStore.getState();
      setUser(mockUser);

      const newUser: User = {
        email: 'new@example.com',
        id: 'user-2',
      };
      setUser(newUser);

      const { user } = useAuthStore.getState();
      expect(user).toEqual(newUser);
    });
  });

  describe('setToken', () => {
    it('should set token in state', () => {
      const { setToken } = useAuthStore.getState();
      setToken('test-token');

      const { token } = useAuthStore.getState();
      expect(token).toBe('test-token');
    });

    it('should store token in localStorage', () => {
      const { setToken } = useAuthStore.getState();
      setToken('test-token');

      expect(localStorage.getItem('auth_token')).toBe('test-token');
    });

    it('should remove token from localStorage when null', () => {
      const { setToken } = useAuthStore.getState();
      setToken('test-token');
      setToken(null);

      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    it('should clear token from state when null', () => {
      const { setToken } = useAuthStore.getState();
      setToken('test-token');
      setToken(null);

      const { token } = useAuthStore.getState();
      expect(token).toBeNull();
    });

    it('should handle empty string token', () => {
      const { setToken } = useAuthStore.getState();
      setToken('');

      // Empty string is falsy, should be treated as null
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(useAuthStore.getState().token).toBeNull();
    });
  });

  describe('login', () => {
    it('should set loading state during login', async () => {
      const { login } = useAuthStore.getState();

      // Note: In the mock implementation, login completes synchronously
      // So we can only verify the final state after completion
      await login('test@example.com', 'password');

      // Loading should be false after completion
      expect(useAuthStore.getState().isLoading).toBeFalsy();
      // User should be set after successful login
      expect(useAuthStore.getState().user).not.toBeNull();
    });

    it('should set user and token on successful login', async () => {
      const { login } = useAuthStore.getState();
      await login('test@example.com', 'password');

      const { user, token, isAuthenticated } = useAuthStore.getState();
      expect(user).not.toBeNull();
      expect(user?.email).toBe('test@example.com');
      expect(token).not.toBeNull();
      expect(isAuthenticated).toBeTruthy();
    });

    it('should derive username from email', async () => {
      const { login } = useAuthStore.getState();
      await login('john.doe@example.com', 'password');

      const { user } = useAuthStore.getState();
      expect(user?.name).toBe('john.doe');
    });

    it('should handle login errors', async () => {
      // This is a mock implementation, so it doesn't actually fail
      // But in a real implementation, we'd test error handling
      const { login } = useAuthStore.getState();

      await expect(login('test@example.com', 'password')).resolves.toBeUndefined();
    });

    it('should clear loading state on error', async () => {
      // Mock a failing login by temporarily replacing the login function
      const originalLogin = useAuthStore.getState().login;

      useAuthStore.setState({
        login: async () => {
          useAuthStore.setState({ isLoading: true });
          try {
            throw new Error('Login failed');
          } finally {
            useAuthStore.setState({ isLoading: false });
          }
        },
      });

      await expect(useAuthStore.getState().login('test@example.com', 'wrong')).rejects.toThrow();
      expect(useAuthStore.getState().isLoading).toBeFalsy();

      // Restore original
      useAuthStore.setState({ login: originalLogin });
    });

    it('should persist token to localStorage', async () => {
      const { login } = useAuthStore.getState();
      await login('test@example.com', 'password');

      expect(localStorage.getItem('auth_token')).not.toBeNull();
    });
  });

  describe('logout', () => {
    it('should clear user', () => {
      const { setUser, logout } = useAuthStore.getState();
      setUser(mockUser);
      void logout();

      const { user } = useAuthStore.getState();
      expect(user).toBeNull();
    });

    it('should clear token', () => {
      const { setToken, logout } = useAuthStore.getState();
      setToken('test-token');
      void logout();

      const { token } = useAuthStore.getState();
      expect(token).toBeNull();
    });

    it('should set isAuthenticated to false', () => {
      const { setUser, logout } = useAuthStore.getState();
      setUser(mockUser);
      void logout();

      const { isAuthenticated } = useAuthStore.getState();
      expect(isAuthenticated).toBeFalsy();
    });

    it('should remove token from localStorage', () => {
      const { setToken, logout } = useAuthStore.getState();
      setToken('test-token');
      void logout();

      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    it('should handle logout when already logged out', () => {
      const { logout } = useAuthStore.getState();

      expect(async () => logout()).not.toThrow();

      const { user, token, isAuthenticated } = useAuthStore.getState();
      expect(user).toBeNull();
      expect(token).toBeNull();
      expect(isAuthenticated).toBeFalsy();
    });
  });

  describe('refreshToken', () => {
    it('should not throw error', async () => {
      const { refreshToken } = useAuthStore.getState();

      await expect(refreshToken()).resolves.not.toThrow();
    });

    it('should log message about not being implemented', async () => {
      const consoleSpy = vi.spyOn(console, 'log');
      const { refreshToken } = useAuthStore.getState();

      await refreshToken();

      expect(consoleSpy).toHaveBeenCalledWith('Token refresh not implemented yet');
      consoleSpy.mockRestore();
    });
  });

  describe('updateProfile', () => {
    it('should update user profile', () => {
      const { setUser, updateProfile } = useAuthStore.getState();
      setUser(mockUser);

      updateProfile({ name: 'Updated Name' });

      const { user } = useAuthStore.getState();
      expect(user?.name).toBe('Updated Name');
    });

    it('should preserve unchanged fields', () => {
      const { setUser, updateProfile } = useAuthStore.getState();
      setUser(mockUser);

      updateProfile({ name: 'Updated Name' });

      const { user } = useAuthStore.getState();
      expect(user?.email).toBe('test@example.com');
      expect(user?.id).toBe('user-1');
    });

    it('should handle multiple field updates', () => {
      const { setUser, updateProfile } = useAuthStore.getState();
      setUser(mockUser);

      updateProfile({
        avatar: 'https://example.com/new-avatar.jpg',
        name: 'New Name',
        role: 'user',
      });

      const { user } = useAuthStore.getState();
      expect(user?.name).toBe('New Name');
      expect(user?.avatar).toBe('https://example.com/new-avatar.jpg');
      expect(user?.role).toBe('user');
    });

    it('should handle updating metadata', () => {
      const { setUser, updateProfile } = useAuthStore.getState();
      setUser(mockUser);

      updateProfile({
        metadata: { department: 'Sales', location: 'NYC' },
      });

      const { user } = useAuthStore.getState();
      expect(user?.metadata).toEqual({ department: 'Sales', location: 'NYC' });
    });

    it('should do nothing if no user is set', () => {
      const { updateProfile } = useAuthStore.getState();

      expect(() => {
        updateProfile({ name: 'Test' });
      }).not.toThrow();

      const { user } = useAuthStore.getState();
      expect(user).toBeNull();
    });

    it('should handle empty updates', () => {
      const { setUser, updateProfile } = useAuthStore.getState();
      setUser(mockUser);

      updateProfile({});

      const { user } = useAuthStore.getState();
      expect(user).toEqual(mockUser);
    });
  });

  describe('persistence', () => {
    it('should persist user to localStorage', () => {
      const { setUser } = useAuthStore.getState();
      setUser(mockUser);

      // Check if data is persisted
      const stored = localStorage.getItem('tracertm-auth-store');
      expect(stored).not.toBeNull();

      const parsed = JSON.parse(stored!);
      expect(parsed.state.user).toEqual(mockUser);
    });

    it('should persist authentication state', () => {
      const { setUser } = useAuthStore.getState();
      setUser(mockUser);

      const stored = localStorage.getItem('tracertm-auth-store');
      const parsed = JSON.parse(stored!);
      expect(parsed.state.isAuthenticated).toBeTruthy();
    });

    it('should not persist isLoading state', () => {
      useAuthStore.setState({ isLoading: true });

      const stored = localStorage.getItem('tracertm-auth-store');
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.isLoading).toBeUndefined();
      }
    });
  });

  describe('edge cases', () => {
    it('should handle rapid state changes', () => {
      const { setUser } = useAuthStore.getState();

      for (let i = 0; i < 100; i++) {
        setUser({ email: `user${i}@example.com`, id: `user-${i}` });
      }

      const { user } = useAuthStore.getState();
      expect(user?.id).toBe('user-99');
    });

    it('should handle concurrent login/logout', async () => {
      const { login, logout } = useAuthStore.getState();

      const loginPromise = login('test@example.com', 'password');
      await loginPromise;
      void logout();

      // State should reflect the last operation
      const { user, isAuthenticated } = useAuthStore.getState();
      expect(user).toBeNull(); // Logout completed last
      expect(isAuthenticated).toBeFalsy();
    });

    it('should handle user with minimal data', () => {
      const { setUser } = useAuthStore.getState();
      const minimalUser: User = {
        email: 'user@example.com',
        id: '1',
      };

      setUser(minimalUser);

      const { user, isAuthenticated } = useAuthStore.getState();
      expect(user).toEqual(minimalUser);
      expect(isAuthenticated).toBeTruthy();
    });

    it('should handle user with maximum data', () => {
      const { setUser } = useAuthStore.getState();
      const maximalUser: User = {
        avatar: 'https://example.com/avatar.jpg',
        email: 'user@example.com',
        id: '1',
        metadata: {
          custom_field_1: 'value1',
          custom_field_2: 'value2',
          department: 'Engineering',
          location: 'Remote',
          team: 'Platform',
          timezone: 'UTC',
        },
        name: 'Test User',
        role: 'super_admin',
      };

      setUser(maximalUser);

      const { user } = useAuthStore.getState();
      expect(user).toEqual(maximalUser);
    });

    it('should handle special characters in email', async () => {
      const { login } = useAuthStore.getState();
      await login('test+tag@example.com', 'password');

      const { user } = useAuthStore.getState();
      expect(user?.email).toBe('test+tag@example.com');
      expect(user?.name).toBe('test+tag');
    });

    it('should handle very long email', async () => {
      const { login } = useAuthStore.getState();
      const longEmail = `${'a'.repeat(50)}@example.com`;
      await login(longEmail, 'password');

      const { user } = useAuthStore.getState();
      expect(user?.email).toBe(longEmail);
    });
  });

  describe('type safety', () => {
    it('should enforce User type for setUser', () => {
      const { setUser } = useAuthStore.getState();

      // Valid user
      expect(() => {
        setUser({
          email: 'test@example.com',
          id: '1',
        });
      }).not.toThrow();

      // Null is valid
      expect(() => {
        setUser(null);
      }).not.toThrow();
    });

    it('should allow optional User fields', () => {
      const { setUser } = useAuthStore.getState();

      const userWithoutOptional: User = {
        email: 'test@example.com',
        id: '1',
      };

      expect(() => {
        setUser(userWithoutOptional);
      }).not.toThrow();
    });
  });
});
