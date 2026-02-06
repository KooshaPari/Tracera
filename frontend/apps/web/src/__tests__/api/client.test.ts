/**
 * Comprehensive tests for API client
 * Goal: Increase coverage from 58% to 95%
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { client } from '@/api/client';

const { ApiError, apiClient, handleApiResponse, safeApiCall } = client;

// Mock openapi-fetch
vi.mock('openapi-fetch', () => {
  const mockClient = {
    DELETE: vi.fn(),
    GET: vi.fn(),
    POST: vi.fn(),
    PUT: vi.fn(),
    use: vi.fn(),
  };
  return {
    default: vi.fn(() => mockClient),
  };
});

// Mock localStorage
const localStorageMock = {
  clear: vi.fn(),
  getItem: vi.fn(),
  removeItem: vi.fn(),
  setItem: vi.fn(),
};
globalThis.localStorage = localStorageMock as any;

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('apiClient initialization', () => {
    it('should initialize apiClient', () => {
      expect(apiClient).toBeDefined();
      expect(apiClient.GET).toBeDefined();
      expect(apiClient.POST).toBeDefined();
      expect(apiClient.PUT).toBeDefined();
      expect(apiClient.DELETE).toBeDefined();
    });

    it('should have use method for interceptors', () => {
      expect(apiClient.use).toBeDefined();
    });
  });

  describe('safeApiCall', () => {
    it('should return promise when valid', async () => {
      const mockPromise = Promise.resolve({
        data: 'test',
        error: undefined,
        response: new Response(),
      });
      const result = await safeApiCall(mockPromise);
      expect(result).toEqual({
        data: 'test',
        error: undefined,
        response: expect.any(Response),
      });
    });

    it('should reject when promise is null', async () => {
      try {
        await safeApiCall(null);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as InstanceType<typeof ApiError>).statusText).toContain(
          'API request failed: promise is null',
        );
      }
    });

    it('should reject when promise is undefined', async () => {
      try {
        await safeApiCall();
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
      }
    });
  });

  describe(handleApiResponse, () => {
    it('should return data when successful', async () => {
      const mockPromise = Promise.resolve({
        data: { id: '1', name: 'Test' },
        error: undefined,
        response: new Response(),
      });

      const result = await handleApiResponse(mockPromise);
      expect(result).toEqual({ id: '1', name: 'Test' });
    });

    it('should throw ApiError when promise is null', async () => {
      try {
        await handleApiResponse(null);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as InstanceType<typeof ApiError>).statusText).toContain(
          'API request failed: promise is null',
        );
      }
    });

    it('should throw ApiError when promise is undefined', async () => {
      await expect(handleApiResponse()).rejects.toThrow(ApiError);
    });

    it('should throw ApiError when error is present', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { message: 'Not found' },
        response: new Response(null, { status: 404, statusText: 'Not Found' }),
      });

      await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
      try {
        await handleApiResponse(mockPromise);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(404);
        expect(apiError.statusText).toBe('Not Found');
      }
    });

    it('should throw ApiError when no data returned', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: undefined,
        response: new Response(null, { status: 204, statusText: 'No Content' }),
      });

      await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
      try {
        await handleApiResponse(mockPromise);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(204);
        expect(apiError.statusText).toBe('No data returned');
      }
    });

    it('should handle error without response', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { message: 'Error' },
        response: undefined as any,
      });

      await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
      try {
        await handleApiResponse(mockPromise);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(500);
        expect(apiError.statusText).toBe('Unknown error');
      }
    });

    it('should handle no data without response', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: undefined,
        response: undefined as any,
      });

      await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
      try {
        await handleApiResponse(mockPromise);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(500);
        expect(apiError.statusText).toBe('No data returned');
      }
    });
  });

  describe('ApiError class', () => {
    it('should create ApiError with status and statusText', () => {
      const error = new ApiError(404, 'Not Found', {
        message: 'Resource not found',
      });
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(404);
      expect(error.statusText).toBe('Not Found');
      expect(error.data).toEqual({ message: 'Resource not found' });
      expect(error.message).toBe('API Error 404: Not Found');
      expect(error.name).toBe('ApiError');
    });

    it('should create ApiError without data', () => {
      const error = new ApiError(500, 'Internal Server Error');
      expect(error.status).toBe(500);
      expect(error.statusText).toBe('Internal Server Error');
      expect(error.data).toBeUndefined();
    });
  });

  describe('interceptors', () => {
    it('should have use method for interceptors', () => {
      expect(apiClient.use).toBeDefined();
      expect(typeof apiClient.use).toBe('function');
    });

    it('should call use method', () => {
      const interceptor = {
        onRequest: vi.fn(async ({ request }) => request),
        onResponse: vi.fn(async ({ response }) => response),
      };

      apiClient.use(interceptor);
      expect(apiClient.use).toHaveBeenCalledWith(interceptor);
    });
  });

  describe('HTTP error responses', () => {
    it('should handle 401 Unauthorized with error message', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { code: 'UNAUTHORIZED', message: 'Invalid credentials' },
        response: new Response(null, { status: 401, statusText: 'Unauthorized' }),
      });

      await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);

      try {
        await handleApiResponse(mockPromise);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(401);
        expect(apiError.statusText).toBe('Unauthorized');
        expect(apiError.data).toEqual({ code: 'UNAUTHORIZED', message: 'Invalid credentials' });
      }
    });

    it('should handle 403 Forbidden response', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { code: 'FORBIDDEN' },
        response: new Response(null, { status: 403, statusText: 'Forbidden' }),
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(403);
        expect(apiError.statusText).toBe('Forbidden');
      }
    });

    it('should handle 422 Unprocessable Entity with validation errors', async () => {
      const validationError = {
        errors: [
          { field: 'email', message: 'Invalid format' },
          { field: 'password', message: 'Too short' },
        ],
      };
      const mockPromise = Promise.resolve({
        data: undefined,
        error: validationError,
        response: new Response(null, { status: 422, statusText: 'Unprocessable Entity' }),
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(422);
        expect(apiError.data).toEqual(validationError);
      }
    });

    it('should handle 500 Internal Server Error', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { message: 'Database connection failed' },
        response: new Response(null, { status: 500, statusText: 'Internal Server Error' }),
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(500);
        expect(apiError.statusText).toBe('Internal Server Error');
      }
    });

    it('should handle 503 Service Unavailable', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { message: 'Service temporarily unavailable' },
        response: new Response(null, { status: 503, statusText: 'Service Unavailable' }),
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(503);
      }
    });
  });

  describe('Response body parsing failures', () => {
    it('should handle malformed JSON in error response', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { raw: 'non-json error body' },
        response: new Response(null, { status: 400, statusText: 'Bad Request' }),
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
      }
    });

    it('should handle error with null response', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { message: 'Error occurred' },
        response: null as any,
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(500);
        expect(apiError.statusText).toBe('Unknown error');
      }
    });

    it('should handle undefined response with error', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: true,
        response: undefined as any,
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(500);
      }
    });

    it('should handle response with statusText as empty string', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { code: 'ERROR' },
        response: new Response(null, { status: 400, statusText: '' }),
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.statusText).toBe('Unknown error');
      }
    });

    it('should handle response with undefined statusText', async () => {
      const mockPromise = Promise.resolve({
        data: undefined,
        error: { message: 'Error' },
        response: new Response(null, { status: 400, statusText: undefined as any }),
      });

      try {
        await handleApiResponse(mockPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.statusText).toBe('Unknown error');
      }
    });
  });

  describe('Network and timeout errors', () => {
    it('should handle promise rejection with network error', async () => {
      const networkError = new Error('Failed to fetch');
      const failingPromise = Promise.reject(networkError);

      try {
        await safeApiCall(failingPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect((error as Error).message).toBe('Failed to fetch');
      }
    });

    it('should handle promise rejection with timeout error', async () => {
      const timeoutError = new Error('Request timeout');
      const failingPromise = Promise.reject(timeoutError);

      try {
        await safeApiCall(failingPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect((error as Error).message).toBe('Request timeout');
      }
    });

    it('should handle promise rejection with abort error', async () => {
      const abortError = new DOMException('The operation was aborted', 'AbortError');
      const failingPromise = Promise.reject(abortError);

      try {
        await safeApiCall(failingPromise);
        expect.fail('should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should handle null promise in safeApiCall', async () => {
      await expect(safeApiCall(null)).rejects.toThrow(ApiError);
      try {
        await safeApiCall(null);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(500);
        expect(apiError.statusText).toContain('promise is null');
      }
    });

    it('should handle undefined promise in safeApiCall', async () => {
      await expect(safeApiCall()).rejects.toThrow(ApiError);
      try {
        await safeApiCall();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        const apiError = error as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(500);
      }
    });
  });

  describe('Data consistency checks', () => {
    it('should return falsy data like 0 as-is', async () => {
      const mockPromise = Promise.resolve({
        data: 0,
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await handleApiResponse(mockPromise);
      expect(result).toBe(0);
      expect(result).not.toBeUndefined();
    });

    it('should return falsy data like false as-is', async () => {
      const mockPromise = Promise.resolve({
        data: false,
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await handleApiResponse(mockPromise);
      expect(result).toBeFalsy();
      expect(result).not.toBeUndefined();
    });

    it('should return empty string as-is', async () => {
      const mockPromise = Promise.resolve({
        data: '',
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await handleApiResponse(mockPromise);
      expect(result).toBe('');
      expect(result).not.toBeUndefined();
    });

    it('should return empty array', async () => {
      const mockPromise = Promise.resolve({
        data: [],
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await handleApiResponse(mockPromise);
      expect(Array.isArray(result)).toBeTruthy();
      expect((result as any).length).toBe(0);
    });

    it('should return empty object', async () => {
      const mockPromise = Promise.resolve({
        data: {},
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await handleApiResponse(mockPromise);
      expect(typeof result).toBe('object');
      expect(Object.keys(result as any).length).toBe(0);
    });

    it('should return null data', async () => {
      const mockPromise = Promise.resolve({
        data: null,
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await handleApiResponse(mockPromise);
      expect(result).toBeNull();
    });
  });

  describe('API Error type checks', () => {
    it('should properly extend Error class', () => {
      const error = new ApiError(400, 'Bad Request', { detail: 'Invalid input' });

      expect(error instanceof Error).toBeTruthy();
      expect(error instanceof ApiError).toBeTruthy();
      expect(Object.getPrototypeOf(Object.getPrototypeOf(error)).constructor.name).toBe('Error');
    });

    it('should have all required properties', () => {
      const error = new ApiError(404, 'Not Found', { resource: 'user' });

      expect(error.hasOwnProperty('status')).toBeTruthy();
      expect(error.hasOwnProperty('statusText')).toBeTruthy();
      expect(error.hasOwnProperty('data')).toBeTruthy();
      expect(error.hasOwnProperty('message')).toBeTruthy();
      expect(error.hasOwnProperty('name')).toBeTruthy();
    });

    it('should be throwable', () => {
      const error = new ApiError(500, 'Server Error');
      let caught = false;
      try {
        throw error;
      } catch (error) {
        caught = error instanceof ApiError;
      }
      expect(caught).toBeTruthy();
    });

    it('should be catchable as Error', () => {
      const error = new ApiError(500, 'Server Error');
      let caught = false;
      try {
        throw error;
      } catch (error) {
        caught = error instanceof Error;
      }
      expect(caught).toBeTruthy();
    });
  });
});
