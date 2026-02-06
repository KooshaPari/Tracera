import { expect, test } from '@playwright/test';

import { collectBrowserLogs, collectNetworkLogs } from './fixtures/test-helpers';

/**
 * Route Validation E2E Tests
 *
 * Comprehensive validation of all main application routes to ensure they load
 * without console errors or failed API requests. Tests cover dashboard, projects,
 * settings, agents, and common navigation flows.
 *
 * Note: Tests assume MSW mocks are in place for API endpoints.
 * Authentication is mocked by the API layer.
 */

interface RouteTest {
  path: string;
  name: string;
}

const ROUTES_TO_TEST: RouteTest[] = [
  { path: '/', name: 'Dashboard' },
  { path: '/projects', name: 'Projects List' },
  { path: '/settings', name: 'Settings' },
  { path: '/agents', name: 'Agents' },
];

test.describe('Route Validation', () => {
  test.beforeEach(async ({ page }) => {
    /**
     * Collect logs and network activity from the start of each test
     */
    const logs = await collectBrowserLogs(page);
    const networkLogs = await collectNetworkLogs(page);

    // Store in context for use in tests
    (page as any).testLogs = logs;
    (page as any).testNetworkLogs = networkLogs;

    /**
     * Navigate to root - MSW mocks will handle authentication
     * The app will load with mocked API responses
     */
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
    await page.waitForLoadState('networkidle');
  });

  ROUTES_TO_TEST.forEach((route) => {
    test(`should load ${route.name} route without errors`, async ({ page }) => {
      /**
       * Navigate to the route
       */
      await page.goto(`http://localhost:5173${route.path}`, { waitUntil: 'networkidle' });
      await page.waitForLoadState('networkidle');

      // Get collected logs and network data
      const logs = (page as any).testLogs;
      const networkLogs = (page as any).testNetworkLogs;

      /**
       * Verify no console errors (excluding deprecation warnings)
       */
      const consoleErrors = logs.errors.filter(
        (e: { message: string }) =>
          !e.message.includes('Deprecation') &&
          !e.message.includes('ResizeObserver loop') &&
          !e.message.includes('WARNING'),
      );

      expect(
        consoleErrors,
        `No critical errors should appear on ${route.path}. Errors: ${JSON.stringify(consoleErrors)}`,
      ).toHaveLength(0);

      /**
       * Verify no failed API requests (4xx/5xx status codes)
       * Exclude mock URLs and successful requests
       */
      const failedRequests = networkLogs.filter(
        (req: { status: number; url: string }) =>
          req.status >= 400 &&
          !req.url.includes('mock') &&
          !req.url.includes('favicon') &&
          !req.url.includes('.jpg') &&
          !req.url.includes('.png') &&
          !req.url.includes('.gif') &&
          !req.url.includes('.svg') &&
          !req.url.includes('.webp'),
      );

      expect(
        failedRequests,
        `No failed API requests on ${route.path}. Failed: ${JSON.stringify(failedRequests.map((r: { url: string; status: number }) => ({ url: r.url, status: r.status })))}`,
      ).toHaveLength(0);

      /**
       * Verify page title exists and is meaningful
       */
      const pageTitle = await page.title();
      expect(pageTitle).toBeTruthy();
      expect(pageTitle.length).toBeGreaterThan(0);

      /**
       * Verify page URL matches expected route
       */
      const currentUrl = page.url();
      expect(currentUrl).toContain(route.path);

      /**
       * Log success metrics
       */
      console.log(
        `✅ ${route.name} (${route.path}): Loaded successfully - Title: "${pageTitle}", Errors: ${consoleErrors.length}, Failed requests: ${failedRequests.length}`,
      );
    });
  });

  test('should handle navigation between routes without errors', async ({ page }) => {
    /**
     * Test sequential navigation between all routes
     * This validates that route transitions don't break state or create stray errors
     */

    for (const route of ROUTES_TO_TEST) {
      const logs = await collectBrowserLogs(page);

      await page.goto(`http://localhost:5173${route.path}`, { waitUntil: 'networkidle' });
      await page.waitForLoadState('networkidle');

      /**
       * Check for errors after navigation
       */
      const consoleErrors = logs.errors.filter(
        (e: { message: string }) =>
          !e.message.includes('Deprecation') &&
          !e.message.includes('ResizeObserver loop') &&
          !e.message.includes('WARNING'),
      );

      expect(consoleErrors, `No errors during navigation to ${route.path}`).toHaveLength(0);

      /**
       * Verify page loaded completely
       */
      const pageTitle = await page.title();
      expect(pageTitle).toBeTruthy();

      console.log(`✅ Navigation to ${route.name} (${route.path}) successful`);
    }
  });

  test('should handle invalid routes gracefully', async ({ page }) => {
    /**
     * Test navigation to non-existent route
     * Should either show 404 or redirect to valid page, but no console errors
     */

    const logs = await collectBrowserLogs(page);

    // Navigate to invalid route
    await page.goto('http://localhost:5173/nonexistent-route-12345', {
      waitUntil: 'networkidle',
    });

    /**
     * Should not have critical console errors
     */
    const consoleErrors = logs.errors.filter(
      (e) =>
        !e.message.includes('Deprecation') &&
        !e.message.includes('ResizeObserver loop') &&
        !e.message.includes('WARNING'),
    );

    expect(consoleErrors, 'Invalid route should not cause critical console errors').toHaveLength(0);

    console.log('✅ Invalid route handled gracefully');
  });

  test('should maintain authentication across route transitions', async ({ page }) => {
    /**
     * Verify that authentication state persists when navigating between routes
     * This ensures auth tokens and session data are maintained
     */

    // Check localStorage for auth token after initial login
    const authToken = await page.evaluate(
      () => localStorage.getItem('auth_token') ?? sessionStorage.getItem('auth_token'),
    );

    expect(authToken).toBeTruthy();
    const initialToken = authToken;

    /**
     * Navigate through all routes and verify auth token remains consistent
     */
    for (const route of ROUTES_TO_TEST) {
      await page.goto(`http://localhost:5173${route.path}`, { waitUntil: 'networkidle' });

      const currentToken = await page.evaluate(
        () => localStorage.getItem('auth_token') ?? sessionStorage.getItem('auth_token'),
      );

      expect(currentToken).toBe(initialToken);
    }

    console.log('✅ Authentication state maintained across route transitions');
  });

  test('should load all routes within acceptable time', async ({ page }) => {
    /**
     * Performance validation: Routes should load within 5 seconds
     * This catches slow routes that might degrade user experience
     */

    const loadTimes: Record<string, number> = {};

    for (const route of ROUTES_TO_TEST) {
      const startTime = Date.now();

      await page.goto(`http://localhost:5173${route.path}`, { waitUntil: 'networkidle' });
      await page.waitForLoadState('networkidle');

      const loadTime = Date.now() - startTime;
      loadTimes[route.path] = loadTime;

      // Routes should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);

      console.log(`⏱️  ${route.name} (${route.path}): ${loadTime}ms`);
    }

    console.log(`✅ All routes loaded within acceptable time:`, loadTimes);
  });
});
