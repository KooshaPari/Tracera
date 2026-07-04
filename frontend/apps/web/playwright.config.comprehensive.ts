import { defineConfig, devices } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Comprehensive Playwright Configuration for TraceRTM
 *
 * Features:
 * - Multi-browser testing (Chromium, Firefox, WebKit)
 * - Mobile device testing (iOS, Android)
 * - Visual regression testing (Percy)
 * - Accessibility testing (axe-core)
 * - Performance testing (Lighthouse)
 * - Parallel execution with sharding
 * - Traces, screenshots, videos
 * - HTML, JSON, JUnit reporters
 */
export default defineConfig({
  // ============================================================================
  // Test Directory & File Patterns
  // ============================================================================
  testDir: './e2e',
  testMatch: '**/*.spec.ts',
  testIgnore: ['**/node_modules/**', '**/dist/**'],

  // ============================================================================
  // Timeouts
  // ============================================================================
  timeout: 60_000, // 60s per test (increased for Lighthouse)
  expect: {
    timeout: 10_000, // 10s for expect assertions
  },

  // ============================================================================
  // Execution Configuration
  // ============================================================================
  fullyParallel: true, // Run tests in parallel across workers
  forbidOnly: Boolean(process.env.CI), // Prevent test.only in CI
  retries: process.env.CI ? 2 : 0, // Retry failed tests on CI
  workers: process.env.CI ? '50%' : undefined, // Use 50% of CPUs on CI

  // ============================================================================
  // Reporters
  // ============================================================================
  reporter: [
    // HTML report with screenshots and traces
    [
      'html',
      {
        open: 'never',
        outputFolder: 'playwright-report', // Don't auto-open, use `npx playwright show-report`
      },
    ],

    // JSON report for programmatic access
    [
      'json',
      {
        outputFile: 'playwright-report/results.json',
      },
    ],

    // JUnit XML for CI integration (Jenkins, GitLab, etc.)
    [
      'junit',
      {
        outputFile: 'playwright-report/junit.xml',
      },
    ],

    // List reporter for terminal output
    [
      'list',
      {
        printSteps: true, // Show test steps in terminal
      },
    ],

    // GitHub Actions reporter (only on CI)
    ...(process.env.CI ? [['github' as const]] : []),

    // Blob reporter for Playwright Cloud/Trace Viewer
    ...(process.env.CI
      ? [
          [
            'blob' as const,
            {
              outputDir: 'playwright-report/blob',
            },
          ],
        ]
      : []),
  ],

  // ============================================================================
  // Global Test Configuration
  // ============================================================================
  use: {
    // Base URL for tests
    baseURL: process.env.BASE_URL ?? 'http://localhost:5173',

    // Browser context options
    viewport: { height: 720, width: 1280 },
    ignoreHTTPSErrors: true,
    acceptDownloads: true,
    locale: 'en-US',
    timezoneId: 'America/New_York',
    permissions: [], // No permissions by default
    geolocation: undefined,
    colorScheme: 'light',

    // Timeouts
    actionTimeout: 10_000, // 10s for actions (click, fill, etc.)
    navigationTimeout: 30_000, // 30s for navigation

    // Traces - capture on failure and retry
    trace: process.env.CI ? 'on-first-retry' : 'retain-on-failure',

    // Screenshots
    screenshot: {
      fullPage: true,
      mode: 'only-on-failure',
    },

    // Videos
    video: {
      mode: 'retain-on-failure',
      size: { height: 720, width: 1280 },
    },

    // Network
    offline: false,
    httpCredentials: undefined,
    proxy: undefined,

    // Context options
    bypassCSP: false,
    javaScriptEnabled: true,
  },

  // ============================================================================
  // Projects - Different Browser/Device Configurations
  // ============================================================================
  projects: [
    // --------------------------------------------------------------------------
    // Desktop Browsers
    // --------------------------------------------------------------------------
    {
      name: 'chromium',
      // Avoid double-running specialized suites (they have dedicated projects below).
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome', // Use installed Chrome (for Lighthouse)
        launchOptions: {
          args: [
            '--disable-blink-features=AutomationControlled', // Hide automation
            '--disable-dev-shm-usage', // Prevent /dev/shm issues in Docker
          ],
        },
      },
    },

    {
      name: 'firefox',
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['Desktop Firefox'],
      },
    },

    {
      name: 'webkit',
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['Desktop Safari'],
      },
    },

    // --------------------------------------------------------------------------
    // Mobile Devices
    // --------------------------------------------------------------------------
    {
      name: 'mobile-chrome',
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['Pixel 5'],
      },
    },

    {
      name: 'mobile-safari',
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['iPhone 13'],
      },
    },

    {
      name: 'tablet-ipad',
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['iPad Pro'],
      },
    },

    // --------------------------------------------------------------------------
    // Branded/Authenticated Tests
    // --------------------------------------------------------------------------
    {
      dependencies: ['setup'],
      name: 'chromium-authenticated',
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        storageState: 'playwright/.auth/user.json', // Reuse auth state
      }, // Run setup project first
    },

    // --------------------------------------------------------------------------
    // Dark Mode Testing
    // --------------------------------------------------------------------------
    {
      name: 'chromium-dark',
      testIgnore: [
        '**/*.a11y.spec.ts',
        '**/*.perf.spec.ts',
        '**/*.visual.spec.ts',
        '**/*.setup.ts',
      ],
      use: {
        ...devices['Desktop Chrome'],
        colorScheme: 'dark',
      },
    },

    // --------------------------------------------------------------------------
    // Accessibility Testing Project (axe-core)
    // --------------------------------------------------------------------------
    {
      name: 'accessibility',
      testMatch: '**/*.a11y.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },

    // --------------------------------------------------------------------------
    // Performance Testing Project (Lighthouse)
    // --------------------------------------------------------------------------
    {
      name: 'performance',
      testMatch: '**/*.perf.spec.ts',
      timeout: 120_000,
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        launchOptions: {
          args: ['--remote-debugging-port=9222'],
        },
      }, // Lighthouse needs more time
    },

    // --------------------------------------------------------------------------
    // Visual Regression Testing (Percy/Chromatic)
    // --------------------------------------------------------------------------
    {
      name: 'visual',
      testMatch: '**/*.visual.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },

    // --------------------------------------------------------------------------
    // Setup Project (runs once before tests)
    // --------------------------------------------------------------------------
    {
      name: 'setup',
      testMatch: '**/*.setup.ts',
    },
  ],

  // ============================================================================
  // Web Server - Start dev server before tests
  // ============================================================================
  webServer: {
    command: 'bun run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000, // 2 minutes to start
    stdout: 'pipe',
    stderr: 'pipe',
    env: {
      NODE_ENV: 'test',
      VITE_API_URL: 'http://localhost:8080',
    },
  },

  // ============================================================================
  // Output Directories
  // ============================================================================
  outputDir: 'test-results', // Test artifacts (videos, traces, screenshots)

  // ============================================================================
  // Global Setup/Teardown
  // ============================================================================
  globalSetup: path.resolve(__dirname, './e2e/global-setup.ts'),
  globalTeardown: path.resolve(__dirname, './e2e/global-teardown.ts'),

  // ============================================================================
  // Metadata
  // ============================================================================
  metadata: {
    'app-version': process.env.npm_package_version ?? 'unknown',
    'build-id': process.env.BUILD_ID ?? 'local',
    'git-commit': process.env.GIT_COMMIT ?? 'unknown',
  },

  // ============================================================================
  // Grep Configuration - Filter tests by tag
  // ============================================================================
  // Run only tests with @smoke tag: npx playwright test --grep @smoke
  // Exclude @slow tests: npx playwright test --grep-invert @slow
  grep: process.env.TEST_GREP ? new RegExp(process.env.TEST_GREP) : undefined,
  grepInvert: process.env.TEST_GREP_INVERT ? new RegExp(process.env.TEST_GREP_INVERT) : undefined,

  // ============================================================================
  // Sharding - Split tests across multiple machines
  // ============================================================================
  // Set via env: SHARD=1/4 (run 1st shard of 4 total)
  shard: process.env.SHARD
    ? {
        current: Number.parseInt(process.env.SHARD.split('/')[0]),
        total: Number.parseInt(process.env.SHARD.split('/')[1]),
      }
    : undefined,
});
