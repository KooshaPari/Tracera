/**
 * Test Data Fixtures for E2E Tests
 * Provides reusable test data for various test scenarios
 */

import type { Agent, Item, Link, Project } from '@tracertm/types';

// Helper to generate timestamps
const now = new Date().toISOString();
const yesterday = new Date(Date.now() - 86_400_000).toISOString();
const lastWeek = new Date(Date.now() - 604_800_000).toISOString();

/**
 * Test Projects
 */
export const testProjects: Project[] = [
  {
    createdAt: lastWeek,
    description: 'Test project for E2E testing',
    id: 'test-proj-1',
    metadata: {
      status: 'active',
      team: 'QA',
    },
    name: 'E2E Test Project',
    updatedAt: now,
  },
  {
    createdAt: yesterday,
    description: 'Sample project for testing filters and search',
    id: 'test-proj-2',
    metadata: {
      status: 'active',
      team: 'Dev',
    },
    name: 'Sample Project',
    updatedAt: now,
  },
];

/**
 * Test Items
 */
export const testItems: Item[] = [
  {
    createdAt: lastWeek,
    description: 'A requirement for testing',
    id: 'test-item-1',
    metadata: { tags: ['test', 'requirement'] },
    priority: 'high',
    projectId: 'test-proj-1',
    status: 'todo',
    title: 'Test Requirement',
    type: 'requirement',
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    createdAt: lastWeek,
    description: 'A feature for testing',
    id: 'test-item-2',
    metadata: { tags: ['test', 'feature'] },
    parentId: 'test-item-1',
    priority: 'medium',
    projectId: 'test-proj-1',
    status: 'in_progress',
    title: 'Test Feature',
    type: 'feature',
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    createdAt: lastWeek,
    description: 'Code implementation for testing',
    id: 'test-item-3',
    metadata: { file_path: 'src/test.ts' },
    priority: 'high',
    projectId: 'test-proj-1',
    status: 'done',
    title: 'Test Implementation',
    type: 'code',
    updatedAt: yesterday,
    version: 1,
    view: 'code',
  },
];

/**
 * Test Links
 */
export const testLinks: Link[] = [
  {
    createdAt: lastWeek,
    id: 'test-link-1',
    metadata: {},
    projectId: 'test-proj-1',
    sourceId: 'test-item-2',
    targetId: 'test-item-1',
    type: 'implements',
    updatedAt: lastWeek,
    version: 1,
  },
  {
    createdAt: lastWeek,
    id: 'test-link-2',
    metadata: {},
    projectId: 'test-proj-1',
    sourceId: 'test-item-3',
    targetId: 'test-item-2',
    type: 'implements',
    updatedAt: lastWeek,
    version: 1,
  },
];

/**
 * Test Agents
 */
export const testAgents: Agent[] = [
  {
    id: 'test-agent-1',
    lastSeen: lastWeek,
    name: 'Test Agent 1',
    status: 'idle',
    type: 'test',
  },
  {
    id: 'test-agent-2',
    lastSeen: now,
    name: 'Test Agent 2',
    status: 'active',
    type: 'analyzer',
  },
];

/**
 * Form Input Data
 */
export const formInputs = {
  agent: {
    name: 'Test Agent from E2E',
    type: 'test',
  },
  item: {
    description: 'This item was created by an E2E test',
    title: 'Test Item from E2E',
  },
  link: {
    type: 'implements',
  },
  project: {
    description: 'This project was created by an E2E test',
    name: 'Test Project from E2E',
  },
};

/**
 * Search Queries
 */
export const searchQueries = {
  invalid: ['xyznoresults123', 'notfound999'],
  partial: ['auth', 'proj', 'item'],
  valid: ['test', 'authentication', 'dashboard', 'code'],
};

/**
 * Filter Values
 */
export const filters = {
  agentStatus: ['Idle', 'Busy', 'Error', 'Offline'],
  itemPriority: ['Critical', 'High', 'Medium', 'Low'],
  itemStatus: ['Pending', 'In Progress', 'Completed', 'Blocked'],
  itemType: ['Requirement', 'Feature', 'Code', 'Test', 'API', 'Database'],
  linkType: ['Implements', 'Tests', 'Documents', 'Relates To', 'Depends On'],
};

/**
 * Validation Error Messages
 */
export const validationMessages = {
  invalidEmail: /invalid.*email/i,
  invalidFormat: /invalid format/i,
  required: /required/i,
  tooLong: /too long|maximum length/i,
  tooShort: /too short|minimum length/i,
};

/**
 * Success Messages
 */
export const successMessages = {
  created: /created successfully|successfully created/i,
  deleted: /deleted successfully|successfully deleted/i,
  saved: /saved successfully|successfully saved/i,
  updated: /updated successfully|successfully updated/i,
};

/**
 * Helper Functions
 */

/**
 * Generate a unique test ID
 */
export function generateTestId(prefix = 'test'): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(7)}`;
}

/**
 * Generate test project data
 */
export function generateTestProject(overrides: Partial<Project> = {}): Project {
  return {
    id: generateTestId('proj'),
    name: `Test Project ${Date.now()}`,
    description: 'Auto-generated test project',
    metadata: { status: 'active', team: 'QA' },
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

/**
 * Generate test item data
 */
export function generateTestItem(projectId: string, overrides: Partial<Item> = {}): Item {
  return {
    id: generateTestId('item'),
    projectId,
    view: 'feature',
    type: 'feature',
    title: `Test Item ${Date.now()}`,
    description: 'Auto-generated test item',
    status: 'todo',
    priority: 'medium',
    metadata: {},
    version: 1,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

/**
 * Generate test link data
 */
export function generateTestLink(
  projectId: string,
  sourceId: string,
  targetId: string,
  overrides: Partial<Link> = {},
): Link {
  return {
    id: generateTestId('link'),
    projectId,
    sourceId,
    targetId,
    type: 'implements',
    metadata: {},
    version: 1,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

/**
 * Generate test agent data
 */
export function generateTestAgent(overrides: Partial<Agent> = {}): Agent {
  return {
    id: generateTestId('agent'),
    name: `Test Agent ${Date.now()}`,
    type: 'test',
    status: 'idle',
    lastSeen: now,
    ...overrides,
  };
}

/**
 * Wait for a specific duration (for timing-sensitive tests)
 */
export async function waitFor(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry a function until it succeeds or max attempts reached
 */
export async function retryUntil<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  delayMs = 1000,
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt < maxAttempts) {
        await waitFor(delayMs);
      }
    }
  }

  throw lastError ?? new Error('Retry failed');
}

/**
 * Mock API Response Helpers
 */
export const mockResponses = {
  agent: (agent: Partial<Agent> = {}) => ({
    data: generateTestAgent(agent),
    status: 200,
  }),

  error: (message: string, status = 400) => ({
    error: { message },
    status,
  }),

  item: (projectId: string, item: Partial<Item> = {}) => ({
    data: generateTestItem(projectId, item),
    status: 200,
  }),

  link: (projectId: string, sourceId: string, targetId: string, link: Partial<Link> = {}) => ({
    data: generateTestLink(projectId, sourceId, targetId, link),
    status: 200,
  }),

  project: (project: Partial<Project> = {}) => ({
    data: generateTestProject(project),
    status: 200,
  }),
};

/**
 * Table Test Items - For accessibility testing
 * Includes varied types, statuses, and priorities for comprehensive table testing
 */
export const tableTestItems: Item[] = [
  {
    createdAt: lastWeek,
    description: 'Authentication system implementation requirement',
    id: 'table-item-1',
    priority: 'high',
    projectId: 'test-proj-1',
    status: 'done',
    title: 'User Authentication',
    type: 'requirement',
    updatedAt: yesterday,
    version: 1,
  },
  {
    createdAt: lastWeek,
    description: 'Database schema design for user management',
    id: 'table-item-2',
    priority: 'high',
    projectId: 'test-proj-1',
    status: 'in_progress',
    title: 'Database Design',
    type: 'feature',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: yesterday,
    description: 'API endpoint specifications',
    id: 'table-item-3',
    priority: 'medium',
    projectId: 'test-proj-1',
    status: 'todo',
    title: 'API Endpoints',
    type: 'specification',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: yesterday,
    description: 'Frontend component library setup',
    id: 'table-item-4',
    priority: 'medium',
    projectId: 'test-proj-1',
    status: 'in_progress',
    title: 'Component Library',
    type: 'feature',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: now,
    description: 'Performance optimization for graph rendering',
    id: 'table-item-5',
    priority: 'low',
    projectId: 'test-proj-1',
    status: 'todo',
    title: 'Performance Optimization',
    type: 'task',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: now,
    description: 'Accessibility compliance testing and fixes',
    id: 'table-item-6',
    priority: 'high',
    projectId: 'test-proj-1',
    status: 'in_progress',
    title: 'Accessibility Testing',
    type: 'task',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: now,
    description: 'Security audit and penetration testing',
    id: 'table-item-7',
    priority: 'high',
    projectId: 'test-proj-1',
    status: 'todo',
    title: 'Security Audit',
    type: 'requirement',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: now,
    description: 'Documentation generation and hosting',
    id: 'table-item-8',
    priority: 'low',
    projectId: 'test-proj-1',
    status: 'todo',
    title: 'Documentation',
    type: 'feature',
    updatedAt: now,
    version: 1,
  },
];
