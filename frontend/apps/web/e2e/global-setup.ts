/**
 * Global Setup - Runs once before all tests
 *
 * Use for:
 * - Starting mock API servers
 * - Seeding test database
 * - Generating authentication tokens
 * - Setting test user environment variables
 */
import { expect, test } from '@playwright/test';

// Global setup runs once before all tests

async function globalSetup(): Promise<void> {
  console.log('🚀 Global setup starting...');

  // Set test user environment variables
  // These will be available to all tests via process.env
  const testUser = {
    email: process.env.TEST_USER_EMAIL ?? 'kooshapari@kooshapari.com',
    password: process.env.TEST_USER_PASSWORD ?? 'testAdmin123',
    firstName: 'Test',
    lastName: 'Admin',
  };

  // Store test user info in environment
  process.env.TEST_USER_EMAIL = testUser.email;
  process.env.TEST_USER_PASSWORD = testUser.password;
  process.env.TEST_USER_FIRST_NAME = testUser.firstName;
  process.env.TEST_USER_LAST_NAME = testUser.lastName;

  console.log(`✅ Test user context initialized: ${testUser.email}`);

  // Example: Start mock API server
  // Const mockServer = await startMockServer();
  // Process.env.MOCK_SERVER_URL = mockServer.url;

  // Example: Seed test database
  // Await seedTestDatabase();

  // Example: Generate authentication token
  // Const token = await generateTestToken(testUser.email);
  // Process.env.TEST_USER_TOKEN = token;

  console.log('✅ Global setup complete');
}

export default globalSetup;
export { expect, test };
