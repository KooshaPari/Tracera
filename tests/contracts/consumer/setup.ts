/**
 * Pact Consumer Test Setup
 *
 * Configures Pact mock server for consumer contract tests.
 */

import { Pact, MatchersV3 } from '@pact-foundation/pact';
import path from 'path';

const { like, eachLike, regex, integer, decimal, iso8601DateTime, uuid } = MatchersV3;

// Export matchers for use in tests
export { like, eachLike, regex, integer, decimal, iso8601DateTime, uuid };

/**
 * Create Pact provider for a specific domain
 */
export function createPactProvider(consumerName: string, providerName = 'TraceRTM-API') {
  const provider = new Pact({
    consumer: consumerName,
    provider: providerName,
    port: 8080,
    log: path.resolve(process.cwd(), '../../../tests/contracts/logs', `${consumerName}-pact.log`),
    dir: path.resolve(process.cwd(), '../../../tests/contracts/pacts'),
    logLevel: 'INFO',
    spec: 3, // Pact Specification v3
  });

  return provider;
}

/**
 * Standard response matchers
 */
export const standardMatchers = {
  // Timestamp matcher
  timestamp: iso8601DateTime(),

  // UUID matcher
  uuid: uuid(),

  // ID matcher (numeric or UUID)
  id: like(1),

  // Pagination matcher
  pagination: {
    page: integer(1),
    pageSize: integer(20),
    total: integer(100),
    totalPages: integer(5),
  },

  // Error response
  error: {
    error: like('Error message'),
    code: like('ERROR_CODE'),
    details: like({}),
  },

  // Success response
  success: {
    success: like(true),
    message: like('Operation completed successfully'),
  },
};

/**
 * Standard headers
 */
export const standardHeaders = {
  'Content-Type': 'application/json',
  'Authorization': regex({
    generate: 'Bearer abc123token',
    matcher: '^Bearer .+$',
  }),
};

/**
 * Standard request headers (without auth)
 */
export const standardRequestHeaders = {
  'Content-Type': 'application/json',
};

/**
 * Helper to create authenticated request headers
 */
export function withAuth(additionalHeaders: Record<string, any> = {}) {
  return {
    ...standardRequestHeaders,
    'Authorization': regex({
      generate: 'Bearer test-token',
      matcher: '^Bearer .+$',
    }),
    ...additionalHeaders,
  };
}

/**
 * Helper to create response with standard fields
 */
export function standardResponse<T>(data: T, status = 200) {
  return {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
    body: data,
  };
}

/**
 * Helper to create error response
 */
export function errorResponse(message: string, code: string, status = 400) {
  return {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
    body: {
      error: message,
      code: code,
      timestamp: iso8601DateTime(),
    },
  };
}

/**
 * Helper to create paginated response
 */
export function paginatedResponse<T>(items: T[], page = 1, pageSize = 20, total = 100) {
  return standardResponse({
    items: eachLike(items[0]),
    pagination: {
      page: integer(page),
      pageSize: integer(pageSize),
      total: integer(total),
      totalPages: integer(Math.ceil(total / pageSize)),
    },
  });
}

/**
 * Common provider states
 */
export const providerStates = {
  // Auth states
  userExists: 'user exists',
  userNotFound: 'user does not exist',
  userAuthenticated: 'user is authenticated',
  userUnauthorized: 'user is not authenticated',

  // Resource states
  resourceExists: (type: string, id: string) => `${type} with id ${id} exists`,
  resourceNotFound: (type: string, id: string) => `${type} with id ${id} does not exist`,

  // Project states
  projectExists: 'project exists',
  projectNotFound: 'project does not exist',
  projectHasItems: 'project has items',
  projectEmpty: 'project is empty',

  // Database states
  databaseEmpty: 'database is empty',
  databaseSeeded: 'database is seeded with test data',
};

/**
 * Test data generators
 */
export const testData = {
  user: {
    id: uuid('user-123'),
    email: like('user@example.com'),
    name: like('Test User'),
    createdAt: iso8601DateTime(),
    updatedAt: iso8601DateTime(),
  },

  project: {
    id: uuid('project-123'),
    name: like('Test Project'),
    description: like('Test project description'),
    status: like('active'),
    createdAt: iso8601DateTime(),
    updatedAt: iso8601DateTime(),
  },

  item: {
    id: uuid('item-123'),
    projectId: uuid('project-123'),
    type: like('requirement'),
    title: like('Test Item'),
    description: like('Test item description'),
    status: like('draft'),
    createdAt: iso8601DateTime(),
    updatedAt: iso8601DateTime(),
  },

  link: {
    id: uuid('link-123'),
    sourceId: uuid('item-123'),
    targetId: uuid('item-456'),
    linkType: like('implements'),
    createdAt: iso8601DateTime(),
    updatedAt: iso8601DateTime(),
  },
};

/**
 * Setup and teardown helpers
 */
export async function setupPact(provider: Pact) {
  await provider.setup();
}

export async function teardownPact(provider: Pact, writePact = true) {
  if (writePact) {
    await provider.writePact();
  }
  await provider.finalize();
}

/**
 * Helper to run a pact test
 */
export async function runPactTest(
  provider: Pact,
  testFn: () => Promise<void>,
  writePact = true
) {
  try {
    await setupPact(provider);
    await testFn();
    await teardownPact(provider, writePact);
  } catch (error) {
    await provider.finalize();
    throw error;
  }
}
