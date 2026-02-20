import { describe, it, expect } from 'vitest';

import { ApiError } from '@/api/client-errors';
import {
  buildErrorMetadata,
  extractValidationErrors,
  formatValidationErrorMessage,
  getErrorType,
  getUserFriendlyMessage,
  isAuthError,
  isNetworkError,
  isServerError,
  isTimeoutError,
  isValidationError,
} from '@/lib/api-error-handler';

describe('API Error Handler', () => {
  describe('getErrorType', () => {
    it('should identify network errors', () => {
      const error = new TypeError('Failed to fetch: network error');
      expect(getErrorType(error)).toBe('network');
    });

    it('should identify timeout errors', () => {
      const error = new Error('Request timeout');
      expect(getErrorType(error)).toBe('timeout');
    });

    it('should identify auth errors', () => {
      const error401 = new ApiError(401, 'Unauthorized');
      const error403 = new ApiError(403, 'Forbidden');
      expect(getErrorType(error401)).toBe('auth');
      expect(getErrorType(error403)).toBe('auth');
    });

    it('should identify validation errors', () => {
      const error = new ApiError(422, 'Validation Error');
      expect(getErrorType(error)).toBe('validation');
    });

    it('should identify server errors', () => {
      const error = new ApiError(500, 'Internal Server Error');
      expect(getErrorType(error)).toBe('server');
    });

    it('should default to unknown for unexpected errors', () => {
      const error = new Error('Some unknown error');
      expect(getErrorType(error)).toBe('unknown');
    });
  });

  describe('getUserFriendlyMessage', () => {
    it('should return appropriate message for network errors', () => {
      const message = getUserFriendlyMessage('network');
      expect(message).toContain('internet connection');
    });

    it('should return appropriate message for timeout errors', () => {
      const message = getUserFriendlyMessage('timeout');
      expect(message.toLowerCase()).toContain('timed out');
    });

    it('should return appropriate message for validation errors', () => {
      const message = getUserFriendlyMessage('validation');
      expect(message).toContain('check your input');
    });

    it('should return appropriate message for auth errors', () => {
      const message = getUserFriendlyMessage('auth');
      expect(message).toContain('expired');
    });

    it('should return appropriate message for server errors', () => {
      const message = getUserFriendlyMessage('server');
      expect(message).toContain('Server error');
    });
  });

  describe('extractValidationErrors', () => {
    it('should extract errors from standard format', () => {
      const error = new ApiError(422, 'Validation Error', {
        errors: {
          name: ['Name is required'],
          email: ['Invalid email format'],
        },
      });

      const result = extractValidationErrors(error);
      expect(result).toEqual({
        email: ['Invalid email format'],
        name: ['Name is required'],
      });
    });

    it('should handle flat error format', () => {
      const error = new ApiError(422, 'Validation Error', {
        name: ['Name is required'],
        email: ['Invalid email format'],
      });

      const result = extractValidationErrors(error);
      expect(result).toEqual({
        email: ['Invalid email format'],
        name: ['Name is required'],
      });
    });

    it('should return null for non-validation errors', () => {
      const error = new ApiError(500, 'Server Error', { message: 'Something went wrong' });
      expect(extractValidationErrors(error)).toBeNull();
    });

    it('should return null for non-ApiError', () => {
      const error = new Error('Regular error');
      expect(extractValidationErrors(error)).toBeNull();
    });
  });

  describe('formatValidationErrorMessage', () => {
    it('should format validation errors for display', () => {
      const errors = {
        email: ['Invalid email format'],
        name: ['Name is required'],
      };

      const message = formatValidationErrorMessage(errors);
      expect(message).toContain('Validation failed');
      expect(message).toContain('email');
      expect(message).toContain('name');
    });

    it('should handle multiple errors per field', () => {
      const errors = {
        password: ['Must be at least 8 characters', 'Must contain a number'],
      };

      const message = formatValidationErrorMessage(errors);
      expect(message).toContain('password');
      expect(message).toContain('Must be at least 8 characters');
      expect(message).toContain('Must contain a number');
    });
  });

  describe('buildErrorMetadata', () => {
    it('should build complete metadata for retryable errors', () => {
      const error = new ApiError(500, 'Server Error');
      const metadata = buildErrorMetadata(error);

      expect(metadata.type).toBe('server');
      expect(metadata.retryable).toBe(true);
      expect(metadata.statusCode).toBe(500);
      expect(metadata.userMessage).toContain('Server error');
    });

    it('should build metadata for non-retryable errors', () => {
      const error = new ApiError(422, 'Validation Error');
      const metadata = buildErrorMetadata(error);

      expect(metadata.type).toBe('validation');
      expect(metadata.retryable).toBe(false);
      expect(metadata.statusCode).toBe(422);
    });

    it('should handle generic errors', () => {
      const error = new Error('Generic error');
      const metadata = buildErrorMetadata(error);

      expect(metadata.type).toBe('unknown');
      expect(metadata.message).toBe('Generic error');
    });
  });
});
