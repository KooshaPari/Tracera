// tests/e2e/support/config/test.config.ts
// Configuration: Test Settings
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
export const testConfig = {
  baseUrl: 'http://localhost:3000',
  browser: {
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
  timeouts: {
    pageLoad: 30000,
    element: 5000,
    navigation: 10000,
    api: 15000,
  },
  retries: {
    enabled: true,
    count: 2,
  },
  screenshot: {
    mode: 'only-on-failure',
    fullPage: true,
  },
  video: {
    mode: 'retain-on-failure',
  },
  trace: {
    mode: 'retain-on-failure',
  },
  users: {
    projectManager: {
      email: 'sarah@example.com',
      password: 'password123',
    },
    developer: {
      email: 'john@example.com',
      password: 'password123',
    },
    designer: {
      email: 'emma@example.com',
      password: 'password123',
    },
    qaEngineer: {
      email: 'mike@example.com',
      password: 'password123',
    },
  },
  testData: {
    defaultItemTitle: 'Test Item',
    defaultProjectName: 'Test Project',
    defaultTag: 'test-tag',
  },
};

export type TestConfig = typeof testConfig;
