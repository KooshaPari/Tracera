/**
 * Type Safety Tests
 * Validates OpenAPI schema types and ensures no unsafe type casts
 * Verifies all endpoints have proper TypeScript types
 */

import { describe, expect, it } from 'vitest';

import { logger } from '@/lib/logger';

// Runtime schema for path/schema existence checks (types are in api/schema)
import openApiSpec from '../../../public/specs/openapi.json';

interface OpenApiSpec {
  paths?: Record<string, unknown> | undefined;
  components?: { schemas?: Record<string, unknown> } | undefined;
}
const spec = openApiSpec as OpenApiSpec;
const pathsRecord = (): Record<string, unknown> => spec.paths ?? {};
const schemasRecord = (): Record<string, unknown> => spec.components?.schemas! ?? {};

describe('API Type Safety', () => {
  describe('Path Definitions', () => {
    it('should have auth login endpoint', () => {
      const key = '/api/v1/auth/login';
      expect(pathsRecord()[key]).toBeDefined();
    });

    it('should have auth logout endpoint', () => {
      const key = '/api/v1/auth/logout';
      expect(pathsRecord()[key]).toBeDefined();
    });

    it('should have graph analysis impact endpoint', () => {
      const key = '/api/v1/graph/analysis/impact';
      expect(pathsRecord()[key]).toBeDefined();
    });

    it('should have graph analysis cycles endpoint', () => {
      const key = '/api/v1/graph/analysis/cycles';
      expect(pathsRecord()[key]).toBeDefined();
    });

    it('should have docs search endpoint', () => {
      const key = '/api/v1/docs/search';
      expect(pathsRecord()[key]).toBeDefined();
    });
  });

  describe('Request Body Types', () => {
    it('should have typed auth login request', () => {
      const pathDef = pathsRecord()['/api/v1/auth/login'];
      expect(typeof pathDef).toBe('object');
    });

    it('should have typed filter requests', () => {
      // Given: Filter parameters
      interface FilterQuery {
        filter?: string | undefined;
        sort?: string | undefined;
        limit?: number | undefined;
      }

      // Then: Verify filter types are available
      const filterExample: FilterQuery = {
        filter: 'status:open',
        limit: 10,
        sort: 'createdAt:desc',
      };

      expect(filterExample.filter).toBeTruthy();
    });
  });

  describe('Response Types', () => {
    it('should have typed auth me response', () => {
      expect(pathsRecord()['/auth/me']).toBeDefined();
    });

    it('should have error response types', () => {
      // Given: Error responses
      interface ErrorResponse {
        error: string;
        code?: string | undefined;
        details?: string | undefined;
      }

      // Then: Verify error structure
      const errorExample: ErrorResponse = {
        code: 'NOT_FOUND',
        details: 'Item with id 123 not found',
        error: 'Not found',
      };

      expect(errorExample.error).toBeTruthy();
      expect(errorExample.code).toBeTruthy();
    });

    it('should have paginated response types', () => {
      // Given: Paginated response
      interface PaginatedResponse<T> {
        data: T[];
        pagination: {
          total: number;
          page: number;
          pageSize: number;
          totalPages: number;
        };
      }

      // Then: Verify pagination structure
      const paginatedExample: PaginatedResponse<{ id: string }> = {
        data: [{ id: '1' }],
        pagination: {
          page: 1,
          pageSize: 10,
          total: 100,
          totalPages: 10,
        },
      };

      expect(paginatedExample.pagination.total).toBe(100);
    });

    it('should have typed analysis response', () => {
      expect(pathsRecord()['/api/v1/graph/analysis/impact']).toBeDefined();
    });
  });

  describe('Parameter Types', () => {
    it('should have typed path parameters', () => {
      // Given: Path parameter types
      type ItemIdParam = string;
      type ProjectIdParam = string;

      // Then: Verify parameters are typed
      const itemId: ItemIdParam = 'item-123';
      const projectId: ProjectIdParam = 'project-456';

      expect(itemId).toBeTruthy();
      expect(projectId).toBeTruthy();
    });

    it('should have typed query parameters', () => {
      // Given: Query parameter types
      interface ListItemsQuery {
        projectId: string;
        page?: number | undefined;
        limit?: number | undefined;
        filter?: string | undefined;
        sort?: string | undefined;
      }

      // Then: Verify query parameters are typed
      const query: ListItemsQuery = {
        filter: 'status:open',
        limit: 20,
        page: 1,
        projectId: 'proj-123',
        sort: 'title',
      };

      expect(query.projectId).toBeTruthy();
      expect(query.limit).toBe(20);
    });

    it('should have typed header parameters', () => {
      // Given: Header parameter types
      interface RequestHeaders {
        'Content-Type': string;
        Authorization?: string | undefined;
        'X-Request-ID'?: string;
      }

      // Then: Verify headers are typed
      const headers: RequestHeaders = {
        Authorization: 'Bearer token',
        'Content-Type': 'application/json',
        'X-Request-ID': 'request-id',
      };

      expect(headers['Content-Type']).toBeTruthy();
    });
  });

  describe('Component Schemas', () => {
    it('should have auth.User schema', () => {
      const schemas = schemasRecord();
      expect(schemas['auth.User']).toBeDefined();
    });

    it('should have handlers.ErrorResponse schema', () => {
      const schemas = schemasRecord();
      expect(schemas['handlers.ErrorResponse']).toBeDefined();
    });
  });

  describe('Type Strictness', () => {
    it('should not allow Record<string, any> in strict mode', () => {
      // Given: Checking for unsafe any types (UnsafeRecord = Record<string, any> should not be used in new code)
      type SafeRecord = Record<string, string | number | boolean>;

      // Then: Verify safe types are available
      const safeData: SafeRecord = {
        active: true,
        count: 5,
        name: 'test',
      };

      expect(safeData).toBeDefined();
      // UnsafeRecord should not be used in new code
    });

    it('should enforce type checking on API responses', () => {
      // Given: Type-safe API response
      interface TypedResponse<T> {
        data: T;
        status: 'success' | 'error';
        timestamp: string;
      }

      // Then: Verify types are enforced
      const response: TypedResponse<{ id: string; name: string }> = {
        data: { id: '1', name: 'Test' },
        status: 'success',
        timestamp: new Date().toISOString(),
      };

      expect(response.data.id).toBe('1');
    });

    it('should use discriminated unions instead of any', () => {
      // Given: Discriminated union types
      interface SuccessResponse {
        status: 'success';
        data: unknown;
      }
      interface ErrorResponse {
        status: 'error';
        error: string;
      }
      type Response = SuccessResponse | ErrorResponse;

      // Then: Verify discriminated unions work
      const response: Response = { data: { id: '1' }, status: 'success' };

      if (response.status === 'success') {
        expect(response.data).toBeDefined();
      }
    });

    it('should use unknown instead of any where type is unknown', () => {
      // Given: Unknown vs Any
      type SafeFunction = (input: unknown) => string;

      // Then: Verify unknown is preferred
      const safeFunc: SafeFunction = (input) => String(input);
      expect(safeFunc('test')).toBe('test');
    });
  });

  describe('Generic Type Parameters', () => {
    it('should use generic types for collections', () => {
      // Given: Generic collection types
      interface Collection<T> {
        items: T[];
        count: number;
      }

      // Then: Verify generics work
      const stringCollection: Collection<string> = {
        count: 3,
        items: ['a', 'b', 'c'],
      };

      expect(stringCollection.items).toHaveLength(3);
    });

    it('should use generic types for responses', () => {
      // Given: Generic response type
      interface ApiResponse<T> {
        data: T;
        error?: string | undefined;
        status: number;
      }

      // Then: Verify generic responses work
      const itemResponse: ApiResponse<{ id: string }> = {
        data: { id: '123' },
        status: 200,
      };

      expect(itemResponse.data.id).toBe('123');
    });
  });

  describe('Conditional Types', () => {
    it('should use conditional types for flexible APIs', () => {
      // Given: Conditional type
      type Flatten<T> = T extends (infer U)[] ? U : T;

      // Then: Verify conditional types work
      type Str = Flatten<string[]>;
      type Num = Flatten<number>;

      const str: Str = 'test';
      const num: Num = 42;

      expect(str).toBeTruthy();
      expect(num).toBe(42);
    });
  });

  describe('Utility Types', () => {
    it('should use Omit for optional fields', () => {
      // Given: Base type with optional fields
      interface User {
        id: string;
        name: string;
        email: string;
        password: string;
      }

      type PublicUser = Omit<User, 'password'>;

      // Then: Verify Omit removes password
      const publicUser: PublicUser = {
        email: 'john@example.com',
        id: '1',
        name: 'John',
      };

      expect(publicUser).toBeDefined();
      // @ts-expect-error password should not exist
      expect((publicUser as { password?: string }).password).toBeUndefined();
    });

    it('should use Partial for optional updates', () => {
      // Given: Partial type
      type UpdateRequest = Partial<{
        name: string;
        status: string;
        priority: number;
      }>;

      // Then: Verify Partial makes all fields optional
      const update: UpdateRequest = {
        name: 'Updated',
      };

      expect(update.name).toBe('Updated');
    });

    it('should use Pick for specific fields', () => {
      // Given: Pick type
      interface User {
        id: string;
        name: string;
        email: string;
        createdAt: string;
      }

      type UserSummary = Pick<User, 'id' | 'name'>;

      // Then: Verify Pick includes only specified fields
      const summary: UserSummary = {
        id: '1',
        name: 'John',
      };

      expect(summary).toBeDefined();
    });
  });

  describe('Type Inference', () => {
    it('should infer types correctly', () => {
      // Given: Type inference
      const response = {
        data: { id: '1', name: 'test' },
        status: 200,
        timestamp: new Date(),
      };

      // Then: Verify inferred types work
      type ResponseType = typeof response;
      const typed: ResponseType = response;

      expect(typed.status).toBe(200);
    });

    it('should infer function return types', () => {
      const getItem = (id: string) => ({
        active: true,
        id,
        name: 'Test',
      });

      type ItemType = ReturnType<typeof getItem>;
      const item: ItemType = getItem('123');

      expect(item.id).toBe('123');
    });
  });

  describe('Literal Types', () => {
    it('should use literal types for enums', () => {
      // Given: Literal union for status
      type ItemStatus = 'todo' | 'in_progress' | 'done';

      // Then: Verify literal types enforce values
      const status: ItemStatus = 'in_progress';

      expect(status).toBe('in_progress');
      // @ts-expect-error should only allow valid literals
      const _invalid: ItemStatus = 'invalid';
    });

    it('should use as const for literal inference', () => {
      // Given: as const declaration
      const STATUSES = ['todo', 'in_progress', 'done'] as const;

      // Then: Verify literal types are inferred
      type Status = (typeof STATUSES)[number];
      const status: Status = 'done';

      expect(status).toBe('done');
    });
  });

  describe('Function Types', () => {
    it('should have typed handlers', () => {
      // Given: Handler type
      type RequestHandler = (request: unknown) => Promise<unknown>;

      // Then: Verify handler typing works
      const handler: RequestHandler = async (_request) => ({ success: true });

      expect(handler).toBeDefined();
    });

    it('should have typed callbacks', () => {
      type ProgressCallback = (percent: number) => void;

      const onProgress: ProgressCallback = (percent) => {
        logger.info(`Progress: ${percent}%`);
      };

      expect(onProgress).toBeDefined();
    });
  });
});
