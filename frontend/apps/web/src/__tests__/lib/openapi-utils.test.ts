/**
 * Tests for openapi-utils
 * Target: 0% → 95% coverage
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { OpenAPISpec } from '../../lib/openapi-utils';

import {
  downloadSpec,
  fetchOpenAPISpec,
  formatPathWithParams,
  generateCodeExamples,
  getEndpointByOperationId,
  getHttpMethods,
  getResponseExamples,
  getSecuritySchemes,
  getServerUrls,
  getSupportedAuthTypes,
  getTags,
  requiresAuth,
  validateOpenAPISpec,
} from '../../lib/openapi-utils';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock as any;

// Mock document.createElement and related DOM APIs
global.document = {
  createElement: vi.fn(() => ({
    href: '',
    download: '',
    click: vi.fn(),
  })),
  body: {
    appendChild: vi.fn(),
    removeChild: vi.fn(),
  },
} as any;

global.URL = {
  createObjectURL: vi.fn(() => 'blob:url'),
  revokeObjectURL: vi.fn(),
} as any;

global.Blob = class Blob {
  constructor(
    public parts: unknown[],
    public options: Record<string, unknown>,
  ) {}
} as any;

describe('openapi-utils', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe('fetchOpenAPISpec', () => {
    it('should fetch OpenAPI spec successfully', async () => {
      const mockSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test API', version: '1.0.0' },
        paths: {},
      };

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSpec,
      } as Response);

      const result = await fetchOpenAPISpec('http://api.example.com/openapi.json');

      expect(result).toEqual(mockSpec);
      expect(global.fetch).toHaveBeenCalledWith('http://api.example.com/openapi.json');
    });

    it('should throw error on failed fetch', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      } as Response);

      await expect(fetchOpenAPISpec('http://api.example.com/openapi.json')).rejects.toThrow(
        'Failed to fetch OpenAPI spec: Not Found',
      );
    });
  });

  describe('validateOpenAPISpec', () => {
    it('should validate valid OpenAPI spec', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      expect(validateOpenAPISpec(spec)).toBe(true);
    });

    it('should reject invalid spec without openapi', () => {
      const spec = { info: {}, paths: {} };
      expect(validateOpenAPISpec(spec)).toBe(false);
    });

    it('should reject invalid spec without info', () => {
      const spec = { openapi: '3.0.0', paths: {} };
      expect(validateOpenAPISpec(spec)).toBe(false);
    });

    it('should reject invalid spec without paths', () => {
      const spec = { openapi: '3.0.0', info: {} };
      expect(validateOpenAPISpec(spec)).toBe(false);
    });

    it('should reject null spec', () => {
      expect(validateOpenAPISpec(null)).toBe(false);
    });

    it('should reject non-object spec', () => {
      expect(validateOpenAPISpec('string')).toBe(false);
    });

    it('should warn about non-3.x version', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const spec = {
        openapi: '2.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      validateOpenAPISpec(spec);

      expect(consoleSpy).toHaveBeenCalledWith('Only OpenAPI 3.x is fully supported');
      consoleSpy.mockRestore();
    });
  });

  describe('getHttpMethods', () => {
    it('should extract all HTTP methods', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {
          '/items': {
            get: {},
            post: {},
            put: {},
            patch: {},
            delete: {},
          },
        },
      };

      const methods = getHttpMethods(spec);
      expect(methods).toContain('GET');
      expect(methods).toContain('POST');
      expect(methods).toContain('PUT');
      expect(methods).toContain('PATCH');
      expect(methods).toContain('DELETE');
    });

    it('should handle empty paths', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      expect(getHttpMethods(spec)).toEqual([]);
    });
  });

  describe('getTags', () => {
    it('should extract all tags', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {
          '/items': {
            get: { tags: ['items', 'read'] },
            post: { tags: ['items', 'write'] },
          },
        },
      };

      const tags = getTags(spec);
      expect(tags).toContain('items');
      expect(tags).toContain('read');
      expect(tags).toContain('write');
    });

    it('should handle paths without tags', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {
          '/items': {
            get: {},
          },
        },
      };

      expect(getTags(spec)).toEqual([]);
    });
  });

  describe('getSecuritySchemes', () => {
    it('should return security schemes', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
            },
          },
        },
      };

      const schemes = getSecuritySchemes(spec);
      expect(schemes).toEqual({
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
        },
      });
    });

    it('should return undefined when no components', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      expect(getSecuritySchemes(spec)).toBeUndefined();
    });
  });

  describe('requiresAuth', () => {
    it('should return true when security schemes exist', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
        components: {
          securitySchemes: {
            bearerAuth: { type: 'http', scheme: 'bearer' },
          },
        },
      };

      expect(requiresAuth(spec)).toBe(true);
    });

    it('should return false when no security schemes', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      expect(requiresAuth(spec)).toBe(false);
    });
  });

  describe('getSupportedAuthTypes', () => {
    it('should return bearer auth type', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
        components: {
          securitySchemes: {
            bearerAuth: { type: 'http', scheme: 'bearer' },
          },
        },
      };

      expect(getSupportedAuthTypes(spec)).toContain('bearer');
    });

    it('should return apiKey auth type', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
        components: {
          securitySchemes: {
            apiKey: { type: 'apiKey', in: 'header', name: 'X-API-Key' },
          },
        },
      };

      expect(getSupportedAuthTypes(spec)).toContain('apiKey');
    });

    it('should return oauth2 auth type', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
        components: {
          securitySchemes: {
            oauth2: { type: 'oauth2', flows: {} },
          },
        },
      };

      expect(getSupportedAuthTypes(spec)).toContain('oauth2');
    });

    it('should return basic auth type', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
        components: {
          securitySchemes: {
            basicAuth: { type: 'http', scheme: 'basic' },
          },
        },
      };

      expect(getSupportedAuthTypes(spec)).toContain('basic');
    });

    it('should return empty array when no schemes', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      expect(getSupportedAuthTypes(spec)).toEqual([]);
    });
  });

  describe('getServerUrls', () => {
    it('should return server URLs', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
        servers: [{ url: 'https://api.example.com' }, { url: 'https://staging.example.com' }],
      };

      expect(getServerUrls(spec)).toEqual([
        'https://api.example.com',
        'https://staging.example.com',
      ]);
    });

    it('should return default URL when no servers', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      expect(getServerUrls(spec)).toEqual(['http://localhost:4000']);
    });
  });

  describe('generateCodeExamples', () => {
    it('should generate curl example', () => {
      const examples = generateCodeExamples('GET', '/items', 'https://api.com');
      expect(examples.curl).toContain('curl -X GET');
      expect(examples.curl).toContain('/items');
    });

    it('should generate curl example with auth', () => {
      const examples = generateCodeExamples('GET', '/items', 'https://api.com', 'token123');
      expect(examples.curl).toContain('Authorization: Bearer token123');
    });

    it('should generate JavaScript example', () => {
      const examples = generateCodeExamples('GET', '/items', 'https://api.com');
      expect(examples.javascript).toContain('fetch');
      expect(examples.javascript).toContain('/items');
    });

    it('should generate Python example', () => {
      const examples = generateCodeExamples('GET', '/items', 'https://api.com');
      expect(examples.python).toContain('import requests');
      expect(examples.python).toContain('/items');
    });

    it('should generate TypeScript example', () => {
      const examples = generateCodeExamples('GET', '/items', 'https://api.com');
      expect(examples.typescript).toContain('fetch');
      expect(examples.typescript).toContain('/items');
    });

    it('should include body for POST requests', () => {
      const examples = generateCodeExamples('POST', '/items', 'https://api.com');
      expect(examples.curl).toContain('-d');
      expect(examples.javascript).toContain('body');
    });
  });

  describe('downloadSpec', () => {
    it('should download spec as JSON', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {},
      };

      downloadSpec(spec, 'test.json');

      expect(global.document.createElement).toHaveBeenCalledWith('a');
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  describe('getEndpointByOperationId', () => {
    it('should find endpoint by operationId', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {
          '/items': {
            get: {
              operationId: 'getItems',
              summary: 'Get items',
            },
          },
        },
      };

      const result = getEndpointByOperationId(spec, 'getItems');
      expect(result).toEqual({
        path: '/items',
        method: 'get',
        operation: {
          operationId: 'getItems',
          summary: 'Get items',
        },
      });
    });

    it('should return null when operationId not found', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        paths: {
          '/items': {
            get: {
              operationId: 'getItems',
            },
          },
        },
      };

      expect(getEndpointByOperationId(spec, 'notFound')).toBeNull();
    });
  });

  describe('formatPathWithParams', () => {
    it('should format path with parameters', () => {
      const path = '/items/{itemId}/comments/{commentId}';
      const params = { itemId: '123', commentId: '456' };

      const result = formatPathWithParams(path, params);
      expect(result).toBe('/items/123/comments/456');
    });

    it('should handle path without params', () => {
      const path = '/items';
      const params = {};

      const result = formatPathWithParams(path, params);
      expect(result).toBe('/items');
    });
  });

  describe('getResponseExamples', () => {
    it('should extract response examples', () => {
      const operation = {
        responses: {
          '200': {
            content: {
              'application/json': {
                example: { id: '1', name: 'Item' },
              },
            },
          },
        },
      };

      const examples = getResponseExamples(operation);
      expect(examples['200']).toEqual({ id: '1', name: 'Item' });
    });

    it('should handle responses without examples', () => {
      const operation = {
        responses: {
          '200': {
            description: 'Success',
          },
        },
      };

      expect(getResponseExamples(operation)).toEqual({});
    });
  });
});
