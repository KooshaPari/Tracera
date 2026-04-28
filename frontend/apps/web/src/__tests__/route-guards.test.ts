/**
 * Tests for route guard utilities
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { checkAuth, requireAuth, requireAuthWithAccount } from '@/lib/route-guards';
import { useAuthStore } from '@/stores/authStore';

// Mock the redirect function
vi.mock('@tanstack/react-router', () => ({
  redirect: (options: any) => {
    throw new Error(JSON.stringify(options));
  },
}));

describe('Route Guards', () => {
  beforeEach(() => {
    // Reset auth store before each test
    useAuthStore.setState({
      account: null,
      isAuthenticated: false,
      token: null,
      user: null,
    });
  });

  describe(requireAuth, () => {
    it('should throw redirect when user is not authenticated', async () => {
      try {
        await requireAuth();
        throw new Error('Expected requireAuth to redirect');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should throw redirect when user is null', async () => {
      useAuthStore.setState({
        isAuthenticated: true,
        token: 'token',
        user: null,
      });

      try {
        await requireAuth();
        throw new Error('Expected requireAuth to redirect');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should not throw when user is authenticated', async () => {
      useAuthStore.setState({
        isAuthenticated: true,
        token: 'token',
        user: { email: 'test@example.com', id: '1' },
      });

      await expect(requireAuth()).resolves.toBeUndefined();
    });

    it('should redirect to custom path when specified', async () => {
      try {
        await requireAuth({ redirectTo: '/auth/login' });
      } catch (error) {
        const redirectOptions = JSON.parse((error as Error).message);
        expect(redirectOptions.to).toBe('/auth/login');
      }
    });

    it('should include returnTo parameter by default', async () => {
      const originalLocation = globalThis.location;
      const mockLocation = {
        pathname: '/projects/123',
        search: '?tab=features',
      };
      Object.defineProperty(globalThis, 'location', {
        configurable: true,
        value: mockLocation,
        writable: true,
      });

      try {
        await requireAuth();
      } catch (error) {
        const redirectOptions = JSON.parse((error as Error).message);
        expect(redirectOptions.search).toEqual({
          returnTo: '/projects/123?tab=features',
        });
      }

      Object.defineProperty(globalThis, 'location', {
        configurable: true,
        value: originalLocation,
        writable: true,
      });
    });

    it('should not include returnTo when disabled', async () => {
      try {
        await requireAuth({ includeReturnUrl: false });
      } catch (error) {
        const redirectOptions = JSON.parse((error as Error).message);
        expect(redirectOptions.search).toBeUndefined();
      }
    });
  });

  describe(requireAuthWithAccount, () => {
    it('should throw redirect when user is not authenticated', async () => {
      try {
        await requireAuthWithAccount();
        throw new Error('Expected requireAuthWithAccount to redirect');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should redirect to account selection when authenticated but no account', async () => {
      useAuthStore.setState({
        account: null,
        isAuthenticated: true,
        token: 'token',
        user: { email: 'test@example.com', id: '1' },
      });

      try {
        await requireAuthWithAccount();
      } catch (error) {
        const redirectOptions = JSON.parse((error as Error).message);
        expect(redirectOptions.to).toBe('/account/select');
      }
    });

    it('should not throw when user is authenticated with account', async () => {
      useAuthStore.setState({
        account: {
          account_type: 'team',
          id: 'acc1',
          name: 'Test Account',
          slug: 'test',
        },
        isAuthenticated: true,
        token: 'token',
        user: { email: 'test@example.com', id: '1' },
      });

      await expect(requireAuthWithAccount()).resolves.toBeUndefined();
    });
  });

  describe(checkAuth, () => {
    it('should return current auth state', () => {
      useAuthStore.setState({
        account: null,
        isAuthenticated: false,
        user: null,
      });

      const result = checkAuth();
      expect(result).toEqual({
        account: null,
        isAuthenticated: false,
        user: null,
      });
    });

    it('should return authenticated state', () => {
      const mockUser = { email: 'test@example.com', id: '1' };
      const mockAccount = {
        account_type: 'team',
        id: 'acc1',
        name: 'Test Account',
        slug: 'test',
      };

      useAuthStore.setState({
        account: mockAccount,
        isAuthenticated: true,
        user: mockUser,
      });

      const result = checkAuth();
      expect(result).toEqual({
        account: mockAccount,
        isAuthenticated: true,
        user: mockUser,
      });
    });
  });
});
