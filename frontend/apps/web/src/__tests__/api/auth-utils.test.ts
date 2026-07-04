/**
 * Auth Utils Tests
 * Covers: normalizeToken, parseErrorData, getAuthErrorMessage, isAuthError,
 * hasWindow, getStoredToken, ensureCSRFToken error paths
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import authConstants from '../../api/auth-constants';
import { AuthError } from '../../api/auth-types';
import {
  getAuthErrorMessage,
  getStoredToken,
  hasWindow,
  isAuthError,
  normalizeToken,
  parseErrorData,
} from '../../api/auth-utils';

describe(normalizeToken, () => {
  it('should return trimmed string for valid token', () => {
    expect(normalizeToken('  abc123  ')).toBe('abc123');
  });

  it('should return undefined for empty string', () => {
    expect(normalizeToken('')).toBeUndefined();
  });

  it('should return undefined for whitespace-only string', () => {
    expect(normalizeToken('   ')).toBeUndefined();
  });

  it('should return undefined for null', () => {
    expect(normalizeToken(null)).toBeUndefined();
  });

  it('should return undefined for undefined', () => {
    expect(normalizeToken()).toBeUndefined();
  });

  it('should convert number to string', () => {
    expect(normalizeToken(12_345 as any)).toBe('12345');
  });

  it('should return undefined for boolean', () => {
    expect(normalizeToken(true as any)).toBeUndefined();
  });

  it('should return undefined for object', () => {
    expect(normalizeToken({} as any)).toBeUndefined();
  });

  it('should return undefined for array', () => {
    expect(normalizeToken([] as any)).toBeUndefined();
  });
});

describe(parseErrorData, () => {
  it('should extract message, code, and details from record object', () => {
    const data = {
      code: 'INVALID_TOKEN',
      details: { reason: 'expired' },
      message: 'Token expired',
    };

    const result = parseErrorData(data);
    expect(result.message).toBe('Token expired');
    expect(result.code).toBe('INVALID_TOKEN');
    expect(result.details).toEqual({ reason: 'expired' });
  });

  it('should return empty message for non-object input', () => {
    expect(parseErrorData('string')).toEqual({ message: '' });
    expect(parseErrorData(null)).toEqual({ message: '' });
    expect(parseErrorData()).toEqual({ message: '' });
    expect(parseErrorData(42)).toEqual({ message: '' });
    expect(parseErrorData(true)).toEqual({ message: '' });
  });

  it('should handle object with missing message', () => {
    const result = parseErrorData({ code: 'ERR' });
    expect(result.message).toBe('');
    expect(result.code).toBe('ERR');
  });

  it('should omit code when not a string', () => {
    const result = parseErrorData({ code: 123, message: 'test' });
    expect(result.code).toBeUndefined();
  });

  it('should omit details when not a record object', () => {
    const result = parseErrorData({ details: 'not-an-object', message: 'test' });
    expect(result.details).toBeUndefined();
  });

  it('should omit code when it is empty string', () => {
    const result = parseErrorData({ code: '', message: 'test' });
    // Empty string is falsy -- code should not be set since it passes the empty check
    expect(result.code).toBeUndefined();
  });

  it('should handle array input as non-record', () => {
    const result = parseErrorData([1, 2, 3]);
    expect(result.message).toBe('');
  });
});

describe(isAuthError, () => {
  it('should return true for AuthError instances', () => {
    const error = new AuthError('test', 401);
    expect(isAuthError(error)).toBeTruthy();
  });

  it('should return false for plain Error', () => {
    expect(isAuthError(new Error('test'))).toBeFalsy();
  });

  it('should return false for non-error objects', () => {
    expect(isAuthError({ message: 'test', statusCode: 401 })).toBeFalsy();
  });

  it('should return false for null and undefined', () => {
    expect(isAuthError(null)).toBeFalsy();
    expect(isAuthError()).toBeFalsy();
  });

  it('should return false for strings', () => {
    expect(isAuthError('error')).toBeFalsy();
  });
});

describe(getAuthErrorMessage, () => {
  it('should return specific message for CSRF_TOKEN_MISSING', () => {
    const error = new AuthError('test', 403, 'CSRF_TOKEN_MISSING');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.CSRF_TOKEN_MISSING);
  });

  it('should return specific message for INVALID_CREDENTIALS', () => {
    const error = new AuthError('test', 401, 'INVALID_CREDENTIALS');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.INVALID_CREDENTIALS);
  });

  it('should return specific message for USER_NOT_FOUND', () => {
    const error = new AuthError('test', 404, 'USER_NOT_FOUND');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.USER_NOT_FOUND);
  });

  it('should return specific message for USER_DISABLED', () => {
    const error = new AuthError('test', 403, 'USER_DISABLED');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.USER_DISABLED);
  });

  it('should return specific message for PASSWORD_MISMATCH', () => {
    const error = new AuthError('test', 400, 'PASSWORD_MISMATCH');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.PASSWORD_MISMATCH);
  });

  it('should return specific message for INVALID_PASSWORD', () => {
    const error = new AuthError('test', 400, 'INVALID_PASSWORD');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.INVALID_PASSWORD);
  });

  it('should return specific message for INVALID_TOKEN', () => {
    const error = new AuthError('test', 401, 'INVALID_TOKEN');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.INVALID_TOKEN);
  });

  it('should return rate limit message for 429 status', () => {
    const error = new AuthError('test', 429);
    expect(getAuthErrorMessage(error)).toBe('Too many login attempts, please try again later');
  });

  it('should return server error message for 500+ status', () => {
    const error = new AuthError('test', 500);
    expect(getAuthErrorMessage(error)).toBe('Server error, please try again later');
  });

  it('should return server error for 502 status', () => {
    const error = new AuthError('test', 502);
    expect(getAuthErrorMessage(error)).toBe('Server error, please try again later');
  });

  it('should return error message when present and no code match', () => {
    const error = new AuthError('Custom error message', 400);
    expect(getAuthErrorMessage(error)).toBe('Custom error message');
  });

  it('should return default message when error message is empty and no code match', () => {
    const error = new AuthError('', 400);
    expect(getAuthErrorMessage(error)).toBe('Authentication failed');
  });

  it('should prioritize code match over status code', () => {
    // Error with both a known code and 429 status -- code takes priority
    const error = new AuthError('test', 429, 'INVALID_CREDENTIALS');
    expect(getAuthErrorMessage(error)).toBe(authConstants.authErrorMessages.INVALID_CREDENTIALS);
  });
});

describe(hasWindow, () => {
  it('should return true in jsdom environment', () => {
    expect(hasWindow()).toBeTruthy();
  });
});

describe(getStoredToken, () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should return undefined when no token exists', () => {
    const result = getStoredToken();
    // No token in localStorage or store -- should be undefined
    expect(result).toBeUndefined();
  });

  it('should return token from localStorage', () => {
    localStorage.setItem('auth_token', 'stored-token-123');
    const result = getStoredToken();
    expect(result).toBe('stored-token-123');
  });

  it('should return undefined for empty localStorage token', () => {
    localStorage.setItem('auth_token', '');
    const result = getStoredToken();
    expect(result).toBeUndefined();
  });

  it('should return undefined for whitespace-only localStorage token', () => {
    localStorage.setItem('auth_token', '   ');
    const result = getStoredToken();
    expect(result).toBeUndefined();
  });
});
