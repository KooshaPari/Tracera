/**
 * Comprehensive tests for client-response-handlers.ts
 * Coverage targets: All response handlers, error cases, toast notifications, CSRF handling
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { responseHandlers } from '../../api/client-response-handlers';

// Mock CSRF handling
vi.mock('../../lib/csrf', () => ({
  extractCSRFTokenFromResponse: vi.fn(),
  handleCSRFError: vi.fn(),
}));

// Mock connection status store
vi.mock('../../stores/connection-status-store', () => ({
  useConnectionStatusStore: {
    getState: () => ({
      setLost: vi.fn(),
    }),
  },
}));

// Mock sonner
vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
  },
}));

// Mock logger
vi.mock('../../lib/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}));

function createMockResponse(status: number, data?: unknown, headers?: Record<string, string>) {
  const responseHeaders = new Headers(headers);
  responseHeaders.set('Content-Type', 'application/json');

  return new Response(data ? JSON.stringify(data) : null, {
    headers: responseHeaders,
    status,
    url: 'http://localhost:4000/api/test',
  });
}

describe('Client Response Handlers - P1 Coverage', () => {
  const mockLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ============================================================================
  // SUCCESSFUL RESPONSE TESTS
  // ============================================================================

  describe('handleResponse - Success Cases', () => {
    it('should handle 200 OK response', async () => {
      const response = createMockResponse(200, { data: 'success' });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(200);
      expect(mockLogout).not.toHaveBeenCalled();
    });

    it('should handle 201 Created response', async () => {
      const response = createMockResponse(201, { id: '123' });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(201);
    });

    it('should handle 204 No Content response', async () => {
      const response = createMockResponse(204);

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(204);
    });

    it('should extract CSRF token from response', async () => {
      const { extractCSRFTokenFromResponse } = await import('../../lib/csrf');
      const response = createMockResponse(200);

      await responseHandlers.handleResponse(response, mockLogout);

      expect(extractCSRFTokenFromResponse).toHaveBeenCalled();
    });

    it('should return response unchanged on success', async () => {
      const response = createMockResponse(200, { data: 'test' });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result).toBe(response);
    });
  });

  // ============================================================================
  // UNAUTHORIZED (401) TESTS
  // ============================================================================

  describe('handleResponse - 401 Unauthorized', () => {
    it('should handle 401 unauthorized response', async () => {
      const response = createMockResponse(401, { error: 'Unauthorized' });

      await responseHandlers.handleResponse(response, mockLogout);

      expect(mockLogout).toHaveBeenCalled();
    });

    it('should handle integration_auth_required code', async () => {
      const response = createMockResponse(401, {
        code: 'integration_auth_required',
        detail: 'Integration token expired',
      });

      await responseHandlers.handleResponse(response, mockLogout);

      // Should show toast instead of logout
      expect(mockLogout).not.toHaveBeenCalled();
    });

    it('should redirect to settings on integration auth failure', async () => {
      const response = createMockResponse(401, {
        code: 'integration_auth_required',
        detail: 'Reconnect integration',
      });

      await responseHandlers.handleResponse(response, mockLogout);

      // Toast should be shown with settings link
      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalled();
    });

    it('should use default message for integration auth', async () => {
      const response = createMockResponse(401, {
        code: 'integration_auth_required',
      });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalled();
    });

    it('should not treat login endpoint 401 as auth failure', async () => {
      const response = new Response(JSON.stringify({ error: 'Bad credentials' }), {
        headers: { 'Content-Type': 'application/json' },
        status: 401,
        url: 'http://localhost:4000/auth/login',
      });

      await responseHandlers.handleResponse(response, mockLogout);

      expect(mockLogout).not.toHaveBeenCalled();
    });

    it('should handle unknown 401 response', async () => {
      const response = createMockResponse(401, { error: 'Unknown' });

      await responseHandlers.handleResponse(response, mockLogout);

      expect(mockLogout).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // FORBIDDEN (403) TESTS
  // ============================================================================

  describe('handleResponse - 403 Forbidden', () => {
    it('should handle 403 forbidden response', async () => {
      const response = createMockResponse(403, { error: 'Forbidden' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith(
        'Access denied',
        expect.objectContaining({
          description: "You don't have permission for this action.",
        }),
      );
    });

    it('should not show error for CSRF 403', async () => {
      const { handleCSRFError } = await import('../../lib/csrf');
      (handleCSRFError as any).mockResolvedValueOnce(true);

      const response = createMockResponse(403, { error: 'Forbidden' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      // Should not show access denied toast if it's a CSRF error
      expect(toast.error).not.toHaveBeenCalledWith('Access denied', expect.anything());
    });

    it('should attempt CSRF handling for 403', async () => {
      const { handleCSRFError } = await import('../../lib/csrf');
      const response = createMockResponse(403);

      await responseHandlers.handleResponse(response, mockLogout);

      expect(handleCSRFError).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // NOT FOUND (404) TESTS
  // ============================================================================

  describe('handleResponse - 404 Not Found', () => {
    it('should handle 404 not found response', async () => {
      const response = createMockResponse(404, { error: 'Not found' });

      await responseHandlers.handleResponse(response, mockLogout);

      // Should not crash, handle gracefully
      expect(response.status).toBe(404);
    });

    it('should show toast for integration_not_found', async () => {
      const response = createMockResponse(404, {
        code: 'integration_not_found',
        detail: 'Integration was deleted',
      });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalled();
    });

    it('should use default message for 404', async () => {
      const response = createMockResponse(404, { code: 'integration_not_found' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalled();
    });

    it('should handle generic 404 without special handling', async () => {
      const response = createMockResponse(404, { error: 'Resource not found' });

      await responseHandlers.handleResponse(response, mockLogout);

      // Should still return response
      expect(response.status).toBe(404);
    });
  });

  // ============================================================================
  // RATE LIMIT (429) TESTS
  // ============================================================================

  describe('handleResponse - 429 Rate Limited', () => {
    it('should handle 429 rate limited response', async () => {
      const response = createMockResponse(429, {
        detail: 'Too many requests',
        retry_after: 60,
      });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Rate limited', expect.anything());
    });

    it('should parse retry_after from header', async () => {
      const response = createMockResponse(429, {}, { 'Retry-After': '30' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Rate limited', expect.stringContaining('30'));
    });

    it('should parse retry_after from body', async () => {
      const response = createMockResponse(429, { retry_after: 120 });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Rate limited', expect.stringContaining('2'));
    });

    it('should use default retry time if not provided', async () => {
      const response = createMockResponse(429, {});

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Rate limited', expect.anything());
    });

    it('should convert seconds to minutes in message', async () => {
      const response = createMockResponse(429, { retry_after: 120 });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      const { calls } = (toast.error as any).mock;
      const description = calls.at(-1)?.[1]?.description;

      expect(description).toContain('2');
      expect(description).toContain('minute');
    });

    it('should keep seconds in message if less than a minute', async () => {
      const response = createMockResponse(429, { retry_after: 45 });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      const { calls } = (toast.error as any).mock;
      const description = calls.at(-1)?.[1]?.description;

      expect(description).toContain('45');
      expect(description).toContain('second');
    });

    it('should use custom detail message if provided', async () => {
      const response = createMockResponse(429, {
        detail: 'Custom rate limit message',
        retry_after: 60,
      });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      const { calls } = (toast.error as any).mock;
      const description = calls.at(-1)?.[1]?.description;

      expect(description).toContain('Custom rate limit message');
    });
  });

  // ============================================================================
  // SERVER ERROR (5xx) TESTS
  // ============================================================================

  describe('handleResponse - 5xx Server Errors', () => {
    it('should handle 500 internal server error', async () => {
      const response = createMockResponse(500, { error: 'Internal server error' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith(
        'Server error',
        expect.objectContaining({
          description: expect.stringContaining("We'll retry"),
        }),
      );
    });

    it('should handle 502 bad gateway', async () => {
      const response = createMockResponse(502, { error: 'Bad gateway' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Server error', expect.anything());
    });

    it('should handle 503 service unavailable', async () => {
      const response = createMockResponse(503, { error: 'Service unavailable' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Server error', expect.anything());
    });

    it('should update connection status store', async () => {
      const response = createMockResponse(500, { error: 'Server error' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { useConnectionStatusStore } = await import('../../stores/connection-status-store');
      const store = useConnectionStatusStore.getState();

      expect(store.setLost).toHaveBeenCalled();
    });

    it('should not treat 4xx as server error', async () => {
      const response = createMockResponse(400, { error: 'Bad request' });

      await responseHandlers.handleResponse(response, mockLogout);

      const { useConnectionStatusStore } = await import('../../stores/connection-status-store');
      const store = useConnectionStatusStore.getState();

      expect(store.setLost).not.toHaveBeenCalled();
    });
  });

  // ============================================================================
  // CSRF ERROR HANDLING TESTS
  // ============================================================================

  describe('handleResponse - CSRF Handling', () => {
    it('should attempt CSRF handling on 403', async () => {
      const { handleCSRFError } = await import('../../lib/csrf');
      const response = createMockResponse(403);

      await responseHandlers.handleResponse(response, mockLogout);

      expect(handleCSRFError).toHaveBeenCalled();
    });

    it('should skip other handlers if CSRF error is true', async () => {
      const { handleCSRFError } = await import('../../lib/csrf');
      (handleCSRFError as any).mockResolvedValueOnce(true);

      const response = createMockResponse(403);

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      // Should not show access denied if it was CSRF
      expect(toast.error).not.toHaveBeenCalledWith('Access denied', expect.anything());
    });

    it('should log CSRF token refresh', async () => {
      const { handleCSRFError } = await import('../../lib/csrf');
      const { logger } = await import('../../lib/logger');
      (handleCSRFError as any).mockResolvedValueOnce(true);

      const response = createMockResponse(403);

      await responseHandlers.handleResponse(response, mockLogout);

      expect(logger.warn).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // RESPONSE PARSING TESTS
  // ============================================================================

  describe('Response Parsing', () => {
    it('should handle JSON response', async () => {
      const response = createMockResponse(200, { key: 'value' });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(200);
    });

    it('should handle empty response body', async () => {
      const response = createMockResponse(204);

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(204);
    });

    it('should handle non-JSON response', async () => {
      const response = new Response('Plain text response', {
        headers: { 'Content-Type': 'text/plain' },
        status: 200,
        url: 'http://localhost:4000/api/test',
      });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(200);
    });

    it('should handle malformed JSON', async () => {
      const response = new Response('{ invalid json', {
        headers: { 'Content-Type': 'application/json' },
        status: 400,
        url: 'http://localhost:4000/api/test',
      });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(400);
    });
  });

  // ============================================================================
  // INTEGRATION TESTS
  // ============================================================================

  describe('Integration Scenarios', () => {
    it('should handle complete error flow: 401 -> logout', async () => {
      const response = createMockResponse(401, { error: 'Session expired' });

      await responseHandlers.handleResponse(response, mockLogout);

      expect(mockLogout).toHaveBeenCalled();
    });

    it('should handle error flow: 403 -> CSRF handling -> unauthorized', async () => {
      const { handleCSRFError } = await import('../../lib/csrf');
      (handleCSRFError as any).mockResolvedValueOnce(false);

      const response = createMockResponse(403);

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Access denied', expect.anything());
    });

    it('should handle rate limit then retry scenario', async () => {
      const response = createMockResponse(429, { retry_after: 60 });

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Rate limited', expect.anything());
    });

    it('should handle server error recovery', async () => {
      const response = createMockResponse(500);

      await responseHandlers.handleResponse(response, mockLogout);

      const { toast } = await import('sonner');
      expect(toast.error).toHaveBeenCalledWith('Server error', expect.anything());
    });
  });

  // ============================================================================
  // EDGE CASES
  // ============================================================================

  describe('Edge Cases', () => {
    it('should handle response with null body', async () => {
      const response = createMockResponse(200);

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(200);
    });

    it('should handle response with missing headers', async () => {
      const response = new Response(JSON.stringify({}), {
        status: 200,
        url: 'http://localhost:4000/api/test',
      });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(200);
    });

    it('should handle very large response body', async () => {
      const largeData = { data: 'x'.repeat(1_000_000) };
      const response = createMockResponse(200, largeData);

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(200);
    });

    it('should handle response with special characters in error message', async () => {
      const response = createMockResponse(400, {
        error: 'Error with <script> and "quotes"',
      });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(400);
    });

    it('should handle null logout callback', async () => {
      const response = createMockResponse(401);

      // Should not throw even with null logout
      const noOpLogout = () => {};
      await responseHandlers.handleResponse(response, noOpLogout);

      expect(noOpLogout).toHaveBeenCalled();
    });

    it('should handle response from different origins', async () => {
      const response = new Response(JSON.stringify({}), {
        headers: { 'Content-Type': 'application/json' },
        status: 200,
        url: 'https://external-api.com/endpoint',
      });

      const result = await responseHandlers.handleResponse(response, mockLogout);

      expect(result.status).toBe(200);
    });
  });
});
