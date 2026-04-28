import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  clearCSRFToken,
  extractCSRFTokenFromResponse,
  fetchCSRFToken,
  getCSRFHeaders,
  getCSRFToken,
  handleCSRFError,
  initializeCSRF,
  refreshCSRFToken,
  setCSRFToken,
} from './csrf';

// Mock fetch globally
global.fetch = vi.fn();

describe('CSRF Token Management', () => {
  beforeEach(() => {
    // Clear token before each test
    clearCSRFToken();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchCSRFToken', () => {
    it('should fetch and store CSRF token', async () => {
      const mockToken = 'test-csrf-token-12345';
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: mockToken, valid: true }),
      });

      const token = await fetchCSRFToken();

      expect(token).toBe(mockToken);
      expect(getCSRFToken()).toBe(mockToken);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/csrf-token'),
        expect.objectContaining({
          method: 'GET',
          credentials: 'include',
        }),
      );
    });

    it('should reuse token if already fetched', async () => {
      const mockToken = 'test-csrf-token-12345';
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: mockToken, valid: true }),
      });

      const token1 = await fetchCSRFToken();
      const token2 = await fetchCSRFToken();

      expect(token1).toBe(token2);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should handle fetch errors gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(fetchCSRFToken()).rejects.toThrow('Network error');
    });

    it('should handle non-200 responses', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(fetchCSRFToken()).rejects.toThrow('Failed to fetch CSRF token');
    });

    it('should handle missing token in response', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: null, valid: false }),
      });

      await expect(fetchCSRFToken()).rejects.toThrow('No CSRF token');
    });
  });

  describe('getCSRFToken', () => {
    it('should return null when token not loaded', () => {
      const token = getCSRFToken();
      expect(token).toBeNull();
    });

    it("should return token after it's set", () => {
      const testToken = 'test-token';
      setCSRFToken(testToken);
      expect(getCSRFToken()).toBe(testToken);
    });
  });

  describe('setCSRFToken', () => {
    it('should set token in memory', () => {
      const testToken = 'new-token';
      setCSRFToken(testToken);
      expect(getCSRFToken()).toBe(testToken);
    });
  });

  describe('refreshCSRFToken', () => {
    it('should clear and refetch token', async () => {
      const oldToken = 'old-token';
      const newToken = 'new-token';

      setCSRFToken(oldToken);
      expect(getCSRFToken()).toBe(oldToken);

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: newToken, valid: true }),
      });

      const refreshed = await refreshCSRFToken();

      expect(refreshed).toBe(newToken);
      expect(getCSRFToken()).toBe(newToken);
    });
  });

  describe('initializeCSRF', () => {
    it('should fetch token on init', async () => {
      const mockToken = 'init-token';
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: mockToken, valid: true }),
      });

      await initializeCSRF();

      expect(getCSRFToken()).toBe(mockToken);
    });

    it('should handle init errors gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Init failed'));

      // initializeCSRF should NOT throw - it catches and logs errors
      // This allows app to continue even if CSRF init fails
      await expect(initializeCSRF()).resolves.toBeUndefined();
    });
  });

  describe('getCSRFHeaders', () => {
    beforeEach(() => {
      setCSRFToken('test-token');
    });

    it('should add header for POST requests', () => {
      const headers = getCSRFHeaders('POST');
      expect(headers['X-CSRF-Token']).toBe('test-token');
    });

    it('should add header for PUT requests', () => {
      const headers = getCSRFHeaders('PUT');
      expect(headers['X-CSRF-Token']).toBe('test-token');
    });

    it('should add header for PATCH requests', () => {
      const headers = getCSRFHeaders('PATCH');
      expect(headers['X-CSRF-Token']).toBe('test-token');
    });

    it('should add header for DELETE requests', () => {
      const headers = getCSRFHeaders('DELETE');
      expect(headers['X-CSRF-Token']).toBe('test-token');
    });

    it('should not add header for GET requests', () => {
      const headers = getCSRFHeaders('GET');
      expect(headers['X-CSRF-Token']).toBeUndefined();
      expect(Object.keys(headers).length).toBe(0);
    });

    it('should not add header for HEAD requests', () => {
      const headers = getCSRFHeaders('HEAD');
      expect(Object.keys(headers).length).toBe(0);
    });

    it('should not add header when token not available', () => {
      clearCSRFToken();
      const headers = getCSRFHeaders('POST');
      expect(headers['X-CSRF-Token']).toBeUndefined();
    });

    it('should handle lowercase methods', () => {
      const headers = getCSRFHeaders('post');
      expect(headers['X-CSRF-Token']).toBe('test-token');
    });
  });

  describe('extractCSRFTokenFromResponse', () => {
    it('should extract token from response header', () => {
      const newToken = 'new-response-token';
      const response = new Response(null, {
        headers: {
          'X-CSRF-Token': newToken,
        },
      });

      const extracted = extractCSRFTokenFromResponse(response);

      expect(extracted).toBe(newToken);
      expect(getCSRFToken()).toBe(newToken);
    });

    it('should handle missing token in response', () => {
      const response = new Response(null);
      const extracted = extractCSRFTokenFromResponse(response);

      expect(extracted).toBeNull();
    });

    it('should detect cookie-based tokens', () => {
      const response = new Response(null, {
        headers: {
          'set-cookie': 'csrf_token=value; Path=/; HttpOnly',
        },
      });

      const extracted = extractCSRFTokenFromResponse(response);

      // Cookie pattern should return null (token is set by browser)
      expect(extracted).toBeNull();
    });
  });

  describe('handleCSRFError', () => {
    it('should detect CSRF errors', async () => {
      const response = new Response(JSON.stringify({ error: 'invalid CSRF token' }), {
        status: 403,
        headers: { 'content-type': 'application/json' },
      });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'new-token', valid: true }),
      });

      const handled = await handleCSRFError(response);

      expect(handled).toBe(true);
    });

    it('should detect token-related errors', async () => {
      const response = new Response(JSON.stringify({ error: 'missing token validation' }), {
        status: 403,
        headers: { 'content-type': 'application/json' },
      });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'new-token', valid: true }),
      });

      const handled = await handleCSRFError(response);

      expect(handled).toBe(true);
    });

    it('should not handle non-CSRF 403 errors', async () => {
      const response = new Response(JSON.stringify({ error: 'forbidden' }), {
        status: 403,
        headers: { 'content-type': 'application/json' },
      });

      const handled = await handleCSRFError(response);

      expect(handled).toBe(false);
    });

    it('should not handle non-403 responses', async () => {
      const response = new Response(JSON.stringify({ error: 'error' }), {
        status: 401,
        headers: { 'content-type': 'application/json' },
      });

      const handled = await handleCSRFError(response);

      expect(handled).toBe(false);
    });

    it('should handle malformed JSON gracefully', async () => {
      const response = new Response('invalid json', {
        status: 403,
        headers: { 'content-type': 'application/json' },
      });

      const handled = await handleCSRFError(response);

      expect(handled).toBe(false);
    });

    it('should refresh token on CSRF error', async () => {
      const response = new Response(JSON.stringify({ error: 'invalid CSRF token' }), {
        status: 403,
        headers: { 'content-type': 'application/json' },
      });

      setCSRFToken('old-token');

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'new-token', valid: true }),
      });

      await handleCSRFError(response);

      expect(getCSRFToken()).toBe('new-token');
    });
  });

  describe('clearCSRFToken', () => {
    it('should clear token from memory', () => {
      setCSRFToken('test-token');
      expect(getCSRFToken()).not.toBeNull();

      clearCSRFToken();

      expect(getCSRFToken()).toBeNull();
    });
  });

  describe('Integration scenarios', () => {
    it('should handle complete token lifecycle', async () => {
      // 1. Initialize
      const mockToken1 = 'token-1';
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: mockToken1, valid: true }),
      });

      await initializeCSRF();
      expect(getCSRFToken()).toBe(mockToken1);

      // 2. Get headers for request
      const headers = getCSRFHeaders('POST');
      expect(headers['X-CSRF-Token']).toBe(mockToken1);

      // 3. Receive new token in response
      const mockToken2 = 'token-2';
      const response = new Response(null, {
        headers: { 'X-CSRF-Token': mockToken2 },
      });
      extractCSRFTokenFromResponse(response);
      expect(getCSRFToken()).toBe(mockToken2);

      // 4. Use new token in next request
      const newHeaders = getCSRFHeaders('PUT');
      expect(newHeaders['X-CSRF-Token']).toBe(mockToken2);
    });

    it('should handle CSRF error recovery', async () => {
      const originalToken = 'original-token';
      const refreshedToken = 'refreshed-token';

      setCSRFToken(originalToken);

      // Simulate CSRF error response
      const errorResponse = new Response(JSON.stringify({ error: 'invalid CSRF token' }), {
        status: 403,
        headers: { 'content-type': 'application/json' },
      });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: refreshedToken, valid: true }),
      });

      const wasHandled = await handleCSRFError(errorResponse);

      expect(wasHandled).toBe(true);
      expect(getCSRFToken()).toBe(refreshedToken);

      // Use new token
      const headers = getCSRFHeaders('POST');
      expect(headers['X-CSRF-Token']).toBe(refreshedToken);
    });
  });
});
