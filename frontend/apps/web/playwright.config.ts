import { defineConfig, devices } from '@playwright/test';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Playwright configuration for TraceRTM E2E tests
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Directory where test files are located
  testDir: './e2e',

  // Maximum time one test can run for
  timeout: 30 * 1000,

  // Run tests in files in parallel - disabled due to API mock isolation issues
  fullyParallel: false,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: Boolean(process.env.CI),

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Limit workers to prevent API mock interference between tests
  // Use 1 worker on CI for stability, 2 locally for speed
  workers: process.env.CI ? 1 : 2,

  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['junit', { outputFile: 'playwright-report/junit.xml' }],
    ['list'],
    // Custom reporter for failed routes
    [join(__dirname, './e2e/reporters/failed-routes-reporter.ts')],
  ],

  // Shared settings for all the projects below
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: 'http://localhost:5173',

    // Run tests in headless mode (default for CI and local)
    headless: true,

    // Collect trace when retrying the failed test
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on retry (saves space, only captures when tests are retried)
    video: 'retain-on-failure',

    // Action timeout
    actionTimeout: 10_000,

    // Navigation timeout
    navigationTimeout: 30_000,
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Uncomment to test on other browsers
    // {
    //   Name: 'firefox',
    //   Use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   Name: 'webkit',
    //   Use: { ...devices['Desktop Safari'] },
    // },

    // Test against mobile viewports
    // {
    //   Name: 'Mobile Chrome',
    //   Use: { ...devices['Pixel 5'] },
    // },
    // {
    //   Name: 'Mobile Safari',
    //   Use: { ...devices['iPhone 12'] },
    // },
  ],

  // Run your local dev server before starting the tests
  webServer: {
    command: 'bun run dev',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    url: 'http://localhost:5173',
  },
});
