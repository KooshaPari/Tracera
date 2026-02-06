import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Visual Regression Testing Configuration for TraceRTM
 *
 * This configuration is optimized for visual regression testing with:
 * - Multiple viewport sizes (mobile, tablet, desktop)
 * - Cross-browser testing (Chromium, Firefox, WebKit)
 * - Consistent screenshot comparison settings
 * - Organized snapshot storage
 */
export default defineConfig({
  testDir: './visual',

  // Snapshots configuration
  snapshotDir: './visual-snapshots',
  snapshotPathTemplate: '{snapshotDir}/{testFileDir}/{testFileName}/{arg}{ext}',

  // Timeout for visual tests (some may need rendering time)
  timeout: 30 * 1000,

  // Run tests in parallel for speed
  fullyParallel: true,

  // Fail on CI if test.only is accidentally left
  forbidOnly: Boolean(process.env.CI),

  // Retry failed tests on CI
  retries: process.env.CI ? 2 : 0,

  // Workers on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report-visual' }],
    ['json', { outputFile: 'playwright-report-visual/results.json' }],
    ['list'],
  ],

  use: {
    // Base URL
    baseURL: 'http://localhost:5173',

    // Always capture trace for visual tests (helps debug visual regressions)
    trace: 'on',

    // Screenshot settings for visual regression
    screenshot: 'only-on-failure',

    // Video for failed tests
    video: 'retain-on-failure',

    // Ensure consistent rendering
    launchOptions: {
      args: ['--disable-web-security', '--disable-features=IsolateOrigins,site-per-process'],
    },
  },

  // Expect configuration for visual comparisons
  expect: {
    toHaveScreenshot: {
      // Max difference in pixels before test fails
      maxDiffPixels: 100,

      // Threshold for pixel difference (0 = exact match, 1 = any difference allowed)
      threshold: 0.2,

      // Animation handling
      animations: 'disabled',

      // CSS animations
      caret: 'hide',
    },
  },

  // Projects for different browsers and viewports
  projects: [
    // Desktop - Chromium
    {
      name: 'chromium-desktop',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { height: 1080, width: 1920 },
      },
    },

    // Desktop - Firefox
    {
      name: 'firefox-desktop',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { height: 1080, width: 1920 },
      },
    },

    // Desktop - WebKit
    {
      name: 'webkit-desktop',
      use: {
        ...devices['Desktop Safari'],
        viewport: { height: 1080, width: 1920 },
      },
    },

    // Tablet - iPad
    {
      name: 'tablet-ipad',
      use: { ...devices['iPad Pro'] },
    },

    // Tablet - Landscape
    {
      name: 'tablet-landscape',
      use: {
        ...devices['iPad Pro landscape'],
      },
    },

    // Mobile - iPhone
    {
      name: 'mobile-iphone',
      use: { ...devices['iPhone 12'] },
    },

    // Mobile - Android
    {
      name: 'mobile-android',
      use: { ...devices['Pixel 5'] },
    },

    // Mobile - Small
    {
      name: 'mobile-small',
      use: {
        ...devices['iPhone SE'],
      },
    },
  ],

  // Run dev server before tests
  webServer: {
    command: 'bun run dev',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    url: 'http://localhost:5173',
  },
});
