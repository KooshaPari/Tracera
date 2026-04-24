/**
 * Client Errors Edge Case Tests
 * Covers: ApiError construction, serialization, handleApiResponse edge paths,
 * safeApiCall with various falsy values, empty statusText fallback
 */

import { describe, expect, it } from 'vitest';

import { ApiError, handleApiResponse, safeApiCall } from '../../api/client-errors';

describe('ApiError class', () => {
  it('should set name to ApiError', () => {
    const error = new ApiError(500, 'Internal Server Error');
    expect(error.name).toBe('ApiError');
  });

  it('should format message with status and statusText', () => {
    const error = new ApiError(404, 'Not Found');
    expect(error.message).toBe('API Error 404: Not Found');
  });

  it('should store data payload', () => {
    const payload = { errors: [{ field: 'email', message: 'required' }] };
    const error = new ApiError(422, 'Unprocessable Entity', payload);
    expect(error.data).toEqual(payload);
    expect(error.status).toBe(422);
    expect(error.statusText).toBe('Unprocessable Entity');
  });

  it('should be an instance of Error', () => {
    const error = new ApiError(400, 'Bad Request');
    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(ApiError);
  });

  it('should handle undefined data', () => {
    const error = new ApiError(500, 'Server Error');
    expect(error.data).toBeUndefined();
  });

  it('should handle null data', () => {
    const error = new ApiError(500, 'Server Error', null);
    expect(error.data).toBeNull();
  });

  it('should handle zero status code', () => {
    const error = new ApiError(0, 'Network Error');
    expect(error.status).toBe(0);
    expect(error.message).toBe('API Error 0: Network Error');
  });
});

describe(safeApiCall, () => {
  it('should return the resolved promise for valid input', async () => {
    const response = new Response(null, { status: 200 });
    const promise = Promise.resolve({ data: 'value', error: undefined, response });
    const result = await safeApiCall(promise);
    expect(result.data).toBe('value');
  });

  it('should throw ApiError with 500 status when promise is null', async () => {
    try {
      await safeApiCall(null);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(500);
      expect((error as ApiError).statusText).toBe('API request failed: promise is null');
    }
  });

  it('should throw ApiError with 500 status when promise is undefined', async () => {
    try {
      await safeApiCall();
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(500);
    }
  });

  it('should propagate rejection from the underlying promise', async () => {
    const failingPromise = Promise.reject(new Error('Network failure'));
    try {
      await safeApiCall(failingPromise);
      expect.fail('should have thrown');
    } catch (error) {
      expect((error as Error).message).toBe('Network failure');
    }
  });
});

describe(handleApiResponse, () => {
  it('should return data on successful response', async () => {
    const promise = Promise.resolve({
      data: { id: 1, name: 'Test' },
      error: undefined,
      response: new Response(null, { status: 200, statusText: 'OK' }),
    });

    const result = await handleApiResponse(promise);
    expect(result).toEqual({ id: 1, name: 'Test' });
  });

  it('should throw when promise is null', async () => {
    await expect(handleApiResponse(null)).rejects.toThrow(ApiError);
  });

  it('should throw when promise is undefined', async () => {
    await expect(handleApiResponse()).rejects.toThrow(ApiError);
  });

  it('should throw ApiError with statusText when error is present', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { message: 'Resource not found' },
      response: new Response(null, { status: 404, statusText: 'Not Found' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(404);
      expect((error as ApiError).statusText).toBe('Not Found');
      expect((error as ApiError).data).toEqual({ message: 'Resource not found' });
    }
  });

  it('should use "Unknown error" when error present but statusText is empty', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { code: 'ERR_001' },
      response: new Response(null, { status: 400, statusText: '' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).statusText).toBe('Unknown error');
    }
  });

  it('should throw "No data returned" when data is undefined and no error', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: undefined,
      response: new Response(null, { status: 200, statusText: 'OK' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).statusText).toBe('No data returned');
    }
  });

  it('should use 500 status when response object is falsy', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { message: 'bad' },
      response: undefined as any,
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(500);
      expect((error as ApiError).statusText).toBe('Unknown error');
    }
  });

  it('should handle error being a boolean true (truthy non-null value)', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: true,
      response: new Response(null, { status: 500, statusText: 'Server Error' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(500);
    }
  });

  it('should return falsy data (0, empty string) without throwing', async () => {
    // Test that data = 0 is returned (not treated as undefined)
    const promiseZero = Promise.resolve({
      data: 0 as any,
      error: undefined,
      response: new Response(null, { status: 200 }),
    });
    const result = await handleApiResponse(promiseZero);
    expect(result).toBe(0);
  });

  it('should return null data without throwing', async () => {
    const promiseNull = Promise.resolve({
      data: null as any,
      error: undefined,
      response: new Response(null, { status: 200 }),
    });
    // Null is not undefined, so it should be returned
    const result = await handleApiResponse(promiseNull);
    expect(result).toBeNull();
  });

  it('should handle 401 Unauthorized response', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { code: 'UNAUTHORIZED' },
      response: new Response(null, { status: 401, statusText: 'Unauthorized' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(401);
      expect((error as ApiError).statusText).toBe('Unauthorized');
      expect((error as ApiError).data).toEqual({ code: 'UNAUTHORIZED' });
    }
  });

  it('should handle 403 Forbidden response', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { code: 'FORBIDDEN' },
      response: new Response(null, { status: 403, statusText: 'Forbidden' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(403);
      expect((error as ApiError).statusText).toBe('Forbidden');
    }
  });

  it('should handle 500 Server Error response', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { message: 'Internal server error' },
      response: new Response(null, { status: 500, statusText: 'Internal Server Error' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(500);
      expect((error as ApiError).statusText).toBe('Internal Server Error');
    }
  });

  it('should handle 422 Unprocessable Entity with validation errors', async () => {
    const validationErrors = {
      errors: [
        { field: 'email', message: 'Invalid email format' },
        { field: 'password', message: 'Too short' },
      ],
    };
    const promise = Promise.resolve({
      data: undefined,
      error: validationErrors,
      response: new Response(null, { status: 422, statusText: 'Unprocessable Entity' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(422);
      expect((error as ApiError).data).toEqual(validationErrors);
    }
  });

  it('should handle response with empty statusText triggering unknown error', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { code: 'ERROR' },
      response: new Response(null, { status: 400, statusText: '' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(400);
      expect((error as ApiError).statusText).toBe('Unknown error');
    }
  });

  it('should handle complex nested error object', async () => {
    const complexError = {
      code: 'VALIDATION_ERROR',
      details: {
        fields: {
          email: { code: 'INVALID_FORMAT', message: 'Not a valid email' },
          phone: { code: 'INVALID_FORMAT', message: 'Invalid phone number' },
        },
      },
      timestamp: '2024-01-01T00:00:00Z',
    };
    const promise = Promise.resolve({
      data: undefined,
      error: complexError,
      response: new Response(null, { status: 400, statusText: 'Bad Request' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).data).toEqual(complexError);
    }
  });

  it('should handle array data returned (falsy but not undefined/null)', async () => {
    const arrayData = [] as any;
    const promise = Promise.resolve({
      data: arrayData,
      error: undefined,
      response: new Response(null, { status: 200 }),
    });

    const result = await handleApiResponse(promise);
    expect(result).toEqual([]);
    expect(Array.isArray(result)).toBeTruthy();
  });

  it('should handle response with low HTTP status code', async () => {
    const promise = Promise.resolve({
      data: undefined,
      error: { message: 'Network error' },
      response: new Response(null, { status: 200, statusText: '' }),
    });

    try {
      await handleApiResponse(promise);
      expect.fail('should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(200);
      expect((error as ApiError).statusText).toBe('Unknown error');
    }
  });
});

describe('ApiError serialization and properties', () => {
  it('should have correct error name', () => {
    const error = new ApiError(500, 'Server Error', { detail: 'Database connection failed' });
    expect(error.name).toBe('ApiError');
    expect(error.toString().includes('ApiError')).toBeTruthy();
  });

  it('should preserve stack trace', () => {
    const error = new ApiError(400, 'Bad Request', null);
    expect(error.stack).toBeDefined();
    expect(error.stack?.includes('ApiError')).toBeTruthy();
  });

  it('should be throwable and catchable', () => {
    const error = new ApiError(403, 'Forbidden');
    let caught = false;
    try {
      throw error;
    } catch (error) {
      caught = error instanceof ApiError;
    }
    expect(caught).toBeTruthy();
  });

  it('should support instanceof check for Error', () => {
    const error = new ApiError(500, 'Error');
    expect(error instanceof Error).toBeTruthy();
    expect(error instanceof ApiError).toBeTruthy();
  });

  it('should have message property accessible', () => {
    const error = new ApiError(404, 'Not Found', { id: 'missing-resource' });
    expect(error.message).toBeDefined();
    expect(typeof error.message).toBe('string');
    expect(error.message.includes('404')).toBeTruthy();
    expect(error.message.includes('Not Found')).toBeTruthy();
  });

  it('should handle special characters in statusText', () => {
    const specialStatusText = 'Error: Connection <interrupted> & "reset"';
    const error = new ApiError(500, specialStatusText);
    expect(error.statusText).toBe(specialStatusText);
    expect(error.message).toContain(specialStatusText);
  });

  it('should store data of various types', () => {
    const stringData = 'error string';
    const error1 = new ApiError(400, 'Error', stringData);
    expect(error1.data).toBe(stringData);

    const numberData = 12_345;
    const error2 = new ApiError(400, 'Error', numberData);
    expect(error2.data).toBe(numberData);

    const booleanData = true;
    const error3 = new ApiError(400, 'Error', booleanData);
    expect(error3.data).toBe(booleanData);

    const arrayData = [1, 2, 3];
    const error4 = new ApiError(400, 'Error', arrayData);
    expect(error4.data).toEqual(arrayData);
  });
});

describe('safeApiCall edge cases', () => {
  it('should handle promise that resolves to minimal response', async () => {
    const minimalResponse = new Response(null, { status: 200 });
    const promise = Promise.resolve({
      data: { value: 'test' },
      error: undefined,
      response: minimalResponse,
    });

    const result = await safeApiCall(promise);
    expect(result.response.status).toBe(200);
    expect(result.data).toEqual({ value: 'test' });
  });

  it('should propagate rejection with Error object', async () => {
    const error = new Error('Network timeout');
    const failingPromise = Promise.reject(error);

    try {
      await safeApiCall(failingPromise);
      expect.fail('should have thrown');
    } catch (error) {
      expect((error as Error).message).toBe('Network timeout');
    }
  });

  it('should propagate rejection with string', async () => {
    const failingPromise = Promise.reject('Simple error string');

    await expect(safeApiCall(failingPromise)).rejects.toBe('Simple error string');
  });

  it('should propagate rejection with object', async () => {
    const errorObj = { code: 'NETWORK_ERROR', message: 'Failed to fetch' };
    const failingPromise = Promise.reject(errorObj);

    await expect(safeApiCall(failingPromise)).rejects.toEqual(errorObj);
  });

  it('should handle very large response data', async () => {
    const largeData = {
      items: Array.from({ length: 10_000 }, (_, i) => ({
        id: i,
        name: `item-${i}`,
        data: `value-${i}`,
      })),
    };
    const promise = Promise.resolve({
      data: largeData,
      error: undefined,
      response: new Response(null, { status: 200 }),
    });

    const result = await safeApiCall(promise);
    expect(result.data).toEqual(largeData);
    expect((result.data as any).items.length).toBe(10_000);
  });
});
