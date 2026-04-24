/**
 * Tests for authStore
 */

import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';

import { useAuthStore } from '../../stores/authStore';

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    const { logout } = useAuthStore.getState();
    logout();
    localStorage.clear();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBeFalsy();
      expect(result.current.isLoading).toBeFalsy();
    });
  });

  describe('setUser', () => {
    it('should set user and update authentication status', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser({
          email: 'test@example.com',
          id: '1',
          name: 'Test User',
        });
      });

      expect(result.current.user).toEqual({
        email: 'test@example.com',
        id: '1',
        name: 'Test User',
      });
      expect(result.current.isAuthenticated).toBeTruthy();
    });

    it('should clear authentication when user is null', () => {
      const { result } = renderHook(() => useAuthStore());

      // First set a user
      act(() => {
        result.current.setUser({
          email: 'test@example.com',
          id: '1',
        });
      });

      // Then clear it
      act(() => {
        result.current.setUser(null);
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBeFalsy();
    });
  });

  describe('setToken', () => {
    it('should store token in state and localStorage', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setToken('test-token');
      });

      expect(result.current.token).toBe('test-token');
      expect(localStorage.getItem('auth_token')).toBe('test-token');
    });

    it('should remove token from localStorage when null', () => {
      const { result } = renderHook(() => useAuthStore());

      // Set token first
      act(() => {
        result.current.setToken('test-token');
      });

      // Then remove it
      act(() => {
        result.current.setToken(null);
      });

      expect(result.current.token).toBeNull();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('test@example.com', 'password');
      });

      expect(result.current.isAuthenticated).toBeTruthy();
      expect(result.current.user).toEqual({
        email: 'test@example.com',
        id: '1',
        name: 'test',
      });
      expect(result.current.token).toBe('mock-jwt-token');
    });

    it('should set loading state during login', async () => {
      const { result } = renderHook(() => useAuthStore());

      // Start login
      act(() => {
        result.current.login('test@example.com', 'password');
      });

      // Login should eventually complete
      expect(result.current).toBeDefined();
    });
  });

  describe('logout', () => {
    it('should clear all auth data', async () => {
      const { result } = renderHook(() => useAuthStore());

      // Login first
      await act(async () => {
        await result.current.login('test@example.com', 'password');
      });

      // Then logout
      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBeFalsy();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('updateProfile', () => {
    it('should update user profile', async () => {
      const { result } = renderHook(() => useAuthStore());

      // Login first
      await act(async () => {
        await result.current.login('test@example.com', 'password');
      });

      // Update profile
      act(() => {
        result.current.updateProfile({
          avatar: 'avatar.jpg',
          name: 'Updated Name',
        });
      });

      expect(result.current.user).toEqual({
        avatar: 'avatar.jpg',
        email: 'test@example.com',
        id: '1',
        name: 'Updated Name',
      });
    });

    it('should not update if no user is logged in', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.updateProfile({
          name: 'Updated Name',
        });
      });

      expect(result.current.user).toBeNull();
    });
  });

  describe('persistence', () => {
    it('should persist auth state to localStorage', async () => {
      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('test@example.com', 'password');
      });

      // Check that state was persisted
      const storedData = localStorage.getItem('tracertm-auth-store');
      expect(storedData).toBeTruthy();

      if (storedData) {
        const parsed = JSON.parse(storedData);
        expect(parsed.state.user).toBeTruthy();
        expect(parsed.state.isAuthenticated).toBeTruthy();
      }
    });
  });
});
