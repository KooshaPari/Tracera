/**
 * Global Teardown - Runs once after all tests
 *
 * Use for:
 * - Stopping mock servers
 * - Cleaning up test data
 * - Generating reports
 */
import type { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Global teardown starting...');

  // Example: Stop mock server
  // Await stopMockServer();

  console.log('✅ Global teardown complete');
}

export default globalTeardown;
