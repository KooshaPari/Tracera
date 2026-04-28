/**
 * Comprehensive tests for Authentication API Client
 *
 * Tests all auth endpoints and error handling:
 * - Login with credentials
 * - Token refresh
 * - Logout
 * - User profile management
 * - Password management
 * - Email verification
 * - Account deletion
 * - CSRF integration
 * - Error handling and conversion
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { AuthResponse, LoginRequest, User } from '@/api/auth';

import {
  AuthError,
  authApi,
  getAuthErrorMessage,
  isAuthError,
  shouldLogoutOnError,
} from '@/api/auth';
import { client } from '@/api/client';

// Mock API client
vi.mock('@/api/client', () => ({
  client: {
    ApiError: class ApiError extends Error {
      public data?: unknown;
      public status: number;
      public statusText: string;

      constructor(status: number, statusText: string, data?: unknown) {
        super(`API Error ${status}: ${statusText}`);
        this.name = 'ApiError';
        this.status = status;
        this.statusText = statusText;
        if (arguments.length > 2) {
          this.data = data;
        }
      }
    },
    apiClient: {
      DELETE: vi.fn(),
      GET: vi.fn(),
      POST: vi.fn(),
      PUT: vi.fn(),
      use: vi.fn(),
    },
    handleApiResponse: vi.fn(),
    safeApiCall: vi.fn(),
  },
}));

// Mock CSRF utilities
vi.mock('@/lib/csrf', () => ({
  fetchCSRFToken: vi.fn(),
  getCSRFToken: vi.fn(),
}));

import * as csrfLib from '@/lib/csrf';

const { ApiError } = client;
const authClient = client;

// Test data
const mockUser: User = {
  email: 'user@example.com',
  id: 'user-123',
  name: 'John Doe',
  role: 'user',
};

const mockAuthResponse: AuthResponse = {
  expiresIn: 3600,
  token: 'token-abc123',
  user: mockUser,
};

const mockLoginRequest: LoginRequest = {
  email: 'user@example.com',
  password: 'password123',
};

describe('Authentication API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock CSRF token availability
    vi.mocked(csrfLib.getCSRFToken).mockReturnValue('csrf-token-123');
    vi.mocked(csrfLib.fetchCSRFToken).mockResolvedValue('csrf-token-123');
  });

  // ========================================================================
  // LOGIN TESTS
  // ========================================================================

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      // Mock the API call
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce(mockAuthResponse);

      const result = await authApi.login(mockLoginRequest);

      // Verify CSRF token was fetched
      expect(csrfLib.getCSRFToken).toHaveBeenCalled();

      // Verify API was called correctly
      expect(authClient.safeApiCall).toHaveBeenCalled();

      // Verify response
      expect(result).toEqual(mockAuthResponse);
      expect(result.user.email).toBe('user@example.com');
      expect(result.token).toBeDefined();
    });

    it('should throw AuthError on invalid credentials', async () => {
      const apiError = new ApiError(401, 'Unauthorized', {
        code: 'INVALID_CREDENTIALS',
        message: 'Invalid email or password',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.login(mockLoginRequest)).rejects.toThrow(AuthError);
    });

    it('should throw AuthError on user not found', async () => {
      const apiError = new ApiError(404, 'Not Found', {
        code: 'USER_NOT_FOUND',
        message: 'User not found',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.login(mockLoginRequest)).rejects.toThrow(AuthError);
    });

    it('should throw AuthError on CSRF token missing', async () => {
      vi.mocked(csrfLib.getCSRFToken).mockReturnValue(null);
      vi.mocked(csrfLib.fetchCSRFToken).mockRejectedValueOnce(new Error('CSRF fetch failed'));

      await expect(authApi.login(mockLoginRequest)).rejects.toThrow(AuthError);
    });

    it('should handle rate limiting (429)', async () => {
      const apiError = new ApiError(429, 'Too Many Requests', {
        message: 'Too many login attempts',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.login(mockLoginRequest)).rejects.toThrow(AuthError);
    });

    it('should handle server errors (500)', async () => {
      const apiError = new ApiError(500, 'Internal Server Error', {
        message: 'Server error',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.login(mockLoginRequest)).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // REFRESH TOKEN TESTS
  // ========================================================================

  describe('refresh', () => {
    it('should successfully refresh token', async () => {
      const newAuthResponse: AuthResponse = {
        ...mockAuthResponse,
        token: 'new-token-def456',
      };

      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce(newAuthResponse);

      const result = await authApi.refresh();

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(result).toEqual(newAuthResponse);
      expect(result.token).toBe('new-token-def456');
    });

    it('should throw AuthError on session expired', async () => {
      const apiError = new ApiError(401, 'Unauthorized', {
        code: 'SESSION_EXPIRED',
        message: 'Session has expired',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.refresh()).rejects.toThrow(AuthError);
    });

    it('should throw AuthError on invalid token', async () => {
      const apiError = new ApiError(401, 'Unauthorized', {
        code: 'INVALID_TOKEN',
        message: 'Invalid token',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.refresh()).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // LOGOUT TESTS
  // ========================================================================

  describe('logout', () => {
    it('should successfully logout', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.logout();

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(authClient.safeApiCall).toHaveBeenCalled();
    });

    it('should handle logout errors gracefully', async () => {
      const apiError = new ApiError(500, 'Internal Server Error', {
        message: 'Logout failed',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.logout()).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // GET CURRENT USER TESTS
  // ========================================================================

  describe('getCurrentUser', () => {
    it('should return current user', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce(mockUser);

      const result = await authApi.getCurrentUser();

      expect(result).toEqual(mockUser);
    });

    it('should return undefined on 401 (not authenticated)', async () => {
      const apiError = new ApiError(401, 'Unauthorized', {
        message: 'Not authenticated',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      const result = await authApi.getCurrentUser();

      expect(result).toBeUndefined();
    });

    it('should throw on server errors (not 401)', async () => {
      const apiError = new ApiError(500, 'Internal Server Error', {
        message: 'Server error',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.getCurrentUser()).rejects.toThrow(AuthError);
    });

    it('should handle 403 errors', async () => {
      const apiError = new ApiError(403, 'Forbidden', {
        message: 'Access denied',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.getCurrentUser()).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // UPDATE PROFILE TESTS
  // ========================================================================

  describe('updateProfile', () => {
    it('should update user profile', async () => {
      const updatedUser: User = {
        ...mockUser,
        name: 'Jane Doe',
      };

      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce(updatedUser);

      const result = await authApi.updateProfile({
        name: 'Jane Doe',
      });

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(result).toEqual(updatedUser);
      expect(result.name).toBe('Jane Doe');
    });

    it('should handle validation errors', async () => {
      const apiError = new ApiError(400, 'Bad Request', {
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.updateProfile({ name: '' })).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // CHANGE PASSWORD TESTS
  // ========================================================================

  describe('changePassword', () => {
    it('should successfully change password', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.changePassword({
        confirmPassword: 'newPass123',
        currentPassword: 'oldPass123',
        newPassword: 'newPass123',
      });

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(authClient.safeApiCall).toHaveBeenCalled();
    });

    it('should throw on invalid current password', async () => {
      const apiError = new ApiError(401, 'Unauthorized', {
        code: 'INVALID_PASSWORD',
        message: 'Current password is incorrect',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(
        authApi.changePassword({
          confirmPassword: 'newPass123',
          currentPassword: 'wrongPassword',
          newPassword: 'newPass123',
        }),
      ).rejects.toThrow(AuthError);
    });

    it('should throw on password mismatch', async () => {
      const apiError = new ApiError(400, 'Bad Request', {
        code: 'PASSWORD_MISMATCH',
        message: 'Passwords do not match',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(
        authApi.changePassword({
          confirmPassword: 'differentPass',
          currentPassword: 'oldPass123',
          newPassword: 'newPass123',
        }),
      ).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // RESET PASSWORD TESTS
  // ========================================================================

  describe('requestPasswordReset', () => {
    it('should request password reset', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.requestPasswordReset({
        email: 'user@example.com',
      });

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(authClient.safeApiCall).toHaveBeenCalled();
    });

    it('should handle non-existent email gracefully', async () => {
      // Should not throw for security reasons
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.requestPasswordReset({
        email: 'nonexistent@example.com',
      });

      expect(authClient.safeApiCall).toHaveBeenCalled();
    });
  });

  describe('confirmPasswordReset', () => {
    it('should confirm password reset with valid token', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.confirmPasswordReset({
        confirmPassword: 'newPass123',
        newPassword: 'newPass123',
        token: 'reset-token-xyz',
      });

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(authClient.safeApiCall).toHaveBeenCalled();
    });

    it('should throw on invalid reset token', async () => {
      const apiError = new ApiError(400, 'Bad Request', {
        code: 'INVALID_TOKEN',
        message: 'Invalid or expired token',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(
        authApi.confirmPasswordReset({
          confirmPassword: 'newPass123',
          newPassword: 'newPass123',
          token: 'invalid-token',
        }),
      ).rejects.toThrow(AuthError);
    });

    it('should throw on expired reset token', async () => {
      const apiError = new ApiError(400, 'Bad Request', {
        code: 'INVALID_TOKEN',
        message: 'Token has expired',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(
        authApi.confirmPasswordReset({
          confirmPassword: 'newPass123',
          newPassword: 'newPass123',
          token: 'expired-token',
        }),
      ).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // EMAIL VERIFICATION TESTS
  // ========================================================================

  describe('verifyEmail', () => {
    it('should verify email with valid token', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.verifyEmail('email-verify-token-123');

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(authClient.safeApiCall).toHaveBeenCalled();
    });

    it('should throw on invalid verification token', async () => {
      const apiError = new ApiError(400, 'Bad Request', {
        code: 'INVALID_TOKEN',
        message: 'Invalid verification token',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.verifyEmail('invalid-token')).rejects.toThrow(AuthError);
    });
  });

  describe('requestEmailVerification', () => {
    it('should request new verification email', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.requestEmailVerification();

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(authClient.safeApiCall).toHaveBeenCalled();
    });
  });

  // ========================================================================
  // DELETE ACCOUNT TESTS
  // ========================================================================

  describe('deleteAccount', () => {
    it('should delete user account', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce();

      await authApi.deleteAccount();

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(authClient.safeApiCall).toHaveBeenCalled();
    });

    it('should handle account deletion errors', async () => {
      const apiError = new ApiError(500, 'Internal Server Error', {
        message: 'Failed to delete account',
      });

      vi.mocked(authClient.handleApiResponse).mockRejectedValueOnce(apiError);

      await expect(authApi.deleteAccount()).rejects.toThrow(AuthError);
    });
  });

  // ========================================================================
  // AUTH ERROR TESTS
  // ========================================================================

  describe(AuthError, () => {
    it('should construct with all parameters', () => {
      const error = new AuthError('Test error', 401, 'TEST_ERROR', {
        field: 'value',
      });

      expect(error.message).toBe('Test error');
      expect(error.statusCode).toBe(401);
      expect(error.code).toBe('TEST_ERROR');
      expect(error.details).toEqual({ field: 'value' });
      expect(error.name).toBe('AuthError');
    });

    it('should construct with minimum parameters', () => {
      const error = new AuthError('Test error', 400);

      expect(error.message).toBe('Test error');
      expect(error.statusCode).toBe(400);
      expect(error.code).toBeUndefined();
      expect(error.details).toBeUndefined();
    });

    it('should be instanceof Error', () => {
      const error = new AuthError('Test', 400);
      expect(error).toBeInstanceOf(Error);
    });
  });

  // ========================================================================
  // UTILITY FUNCTION TESTS
  // ========================================================================

  describe(isAuthError, () => {
    it('should return true for AuthError instances', () => {
      const error = new AuthError('Test', 400);
      expect(isAuthError(error)).toBeTruthy();
    });

    it('should return false for regular Error', () => {
      const error = new Error('Test');
      expect(isAuthError(error)).toBeFalsy();
    });

    it('should return false for ApiError', () => {
      const error = new ApiError(400, 'Bad Request');
      expect(isAuthError(error)).toBeFalsy();
    });

    it('should return false for non-error objects', () => {
      expect(isAuthError(null)).toBeFalsy();
      expect(isAuthError()).toBeFalsy();
      expect(isAuthError('string')).toBeFalsy();
      expect(isAuthError({})).toBeFalsy();
    });
  });

  describe(getAuthErrorMessage, () => {
    it('should return specific message for INVALID_CREDENTIALS', () => {
      const error = new AuthError('Error', 401, 'INVALID_CREDENTIALS');
      expect(getAuthErrorMessage(error)).toBe('Invalid email or password');
    });

    it('should return specific message for USER_NOT_FOUND', () => {
      const error = new AuthError('Error', 404, 'USER_NOT_FOUND');
      expect(getAuthErrorMessage(error)).toBe('User not found');
    });

    it('should return specific message for USER_DISABLED', () => {
      const error = new AuthError('Error', 403, 'USER_DISABLED');
      expect(getAuthErrorMessage(error)).toBe('This account has been disabled');
    });

    it('should return specific message for INVALID_PASSWORD', () => {
      const error = new AuthError('Error', 401, 'INVALID_PASSWORD');
      expect(getAuthErrorMessage(error)).toBe('Current password is incorrect');
    });

    it('should return specific message for PASSWORD_MISMATCH', () => {
      const error = new AuthError('Error', 400, 'PASSWORD_MISMATCH');
      expect(getAuthErrorMessage(error)).toBe('Passwords do not match');
    });

    it('should return specific message for INVALID_TOKEN', () => {
      const error = new AuthError('Error', 400, 'INVALID_TOKEN');
      expect(getAuthErrorMessage(error)).toBe('Invalid or expired token');
    });

    it('should return specific message for CSRF_TOKEN_MISSING', () => {
      const error = new AuthError('Error', 403, 'CSRF_TOKEN_MISSING');
      expect(getAuthErrorMessage(error)).toBe('Security token missing, please refresh the page');
    });

    it('should return rate limit message for 429', () => {
      const error = new AuthError('Error', 429);
      expect(getAuthErrorMessage(error)).toContain('Too many login');
    });

    it('should return server error message for 500+', () => {
      const error = new AuthError('Error', 500);
      expect(getAuthErrorMessage(error)).toContain('Server error');
    });

    it('should return error message as fallback', () => {
      const error = new AuthError('Custom error message', 400);
      expect(getAuthErrorMessage(error)).toBe('Custom error message');
    });

    it('should use default message when error message is empty', () => {
      const error = new AuthError('', 400);
      expect(getAuthErrorMessage(error)).toBe('Authentication failed');
    });
  });

  describe(shouldLogoutOnError, () => {
    it('should return true for 401 status', () => {
      const error = new AuthError('Error', 401);
      expect(shouldLogoutOnError(error)).toBeTruthy();
    });

    it('should return true for SESSION_EXPIRED code', () => {
      const error = new AuthError('Error', 200, 'SESSION_EXPIRED');
      expect(shouldLogoutOnError(error)).toBeTruthy();
    });

    it('should return true for INVALID_TOKEN code', () => {
      const error = new AuthError('Error', 200, 'INVALID_TOKEN');
      expect(shouldLogoutOnError(error)).toBeTruthy();
    });

    it('should return false for other errors', () => {
      const error = new AuthError('Error', 400, 'VALIDATION_ERROR');
      expect(shouldLogoutOnError(error)).toBeFalsy();
    });

    it('should return false for client errors', () => {
      const error = new AuthError('Error', 400);
      expect(shouldLogoutOnError(error)).toBeFalsy();
    });

    it('should return false for server errors', () => {
      const error = new AuthError('Error', 500);
      expect(shouldLogoutOnError(error)).toBeFalsy();
    });
  });

  // ========================================================================
  // CSRF INTEGRATION TESTS
  // ========================================================================

  describe('CSRF Integration', () => {
    it('should fetch CSRF token if not available', async () => {
      vi.mocked(csrfLib.getCSRFToken).mockReturnValueOnce(null);
      vi.mocked(csrfLib.fetchCSRFToken).mockResolvedValueOnce('fetched-csrf-token');
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce(mockAuthResponse);

      await authApi.login(mockLoginRequest);

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(csrfLib.fetchCSRFToken).toHaveBeenCalled();
    });

    it('should use cached CSRF token', async () => {
      vi.mocked(csrfLib.getCSRFToken).mockReturnValueOnce('cached-token');
      vi.mocked(authClient.handleApiResponse).mockResolvedValueOnce(mockAuthResponse);

      await authApi.login(mockLoginRequest);

      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
      expect(csrfLib.fetchCSRFToken).not.toHaveBeenCalled();
    });

    it('should throw AuthError if CSRF fetch fails', async () => {
      vi.mocked(csrfLib.getCSRFToken).mockReturnValueOnce(null);
      vi.mocked(csrfLib.fetchCSRFToken).mockRejectedValueOnce(new Error('CSRF unavailable'));

      await expect(authApi.login(mockLoginRequest)).rejects.toThrow(AuthError);
    });

    it('should ensure CSRF for all state-changing operations', async () => {
      vi.mocked(authClient.handleApiResponse).mockResolvedValue();

      // These should all try to get/fetch CSRF token
      await authApi.logout();
      expect(csrfLib.getCSRFToken).toHaveBeenCalled();

      vi.clearAllMocks();
      vi.mocked(csrfLib.getCSRFToken).mockReturnValue('token');
      vi.mocked(authClient.handleApiResponse).mockResolvedValue();

      await authApi.changePassword({
        confirmPassword: 'new',
        currentPassword: 'old',
        newPassword: 'new',
      });
      expect(csrfLib.getCSRFToken).toHaveBeenCalled();
    });
  });
});
