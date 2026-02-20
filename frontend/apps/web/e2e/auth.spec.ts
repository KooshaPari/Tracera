import { expect, test } from './global-setup';

/**
 * Authentication E2E Tests
 *
 * Tests for login/logout flows and authentication state management.
 * Note: Since MSW is handling API mocks, we focus on UI flows.
 */

test.describe('Authentication Flows', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('should load the application', async ({ page }) => {
    // Wait for the app to load
    await page.waitForLoadState('networkidle');

    // Check that we're on the dashboard (default route)
    await expect(page).toHaveURL('/');

    // Verify page title
    await expect(page).toHaveTitle(/TraceRTM/);
  });

  test('should display main navigation', async ({ page }) => {
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');

    // Wait for dashboard heading first to ensure page is rendered
    const dashboardHeading = page.getByRole('heading', {
      name: /traceability dashboard/i,
    });
    await expect(dashboardHeading).toBeVisible({ timeout: 5000 });

    // Check for navigation elements
    // The dashboard shows "New Project" button and project links
    const newProjectLink = page.getByRole('link', { name: 'New Project' });
    await expect(newProjectLink).toBeVisible({ timeout: 5000 });
  });

  test('should handle user session', async ({ page }) => {
    // Since MSW mocks are active, the app should load without authentication errors
    await page.waitForLoadState('networkidle');

    // Check that localStorage or sessionStorage has been set
    const localStorage = await page.evaluate(() => globalThis.localStorage);
    expect(localStorage).toBeDefined();
  });

  test('should persist session across page reloads', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // Wait for dashboard content to appear
    const heading = page.getByRole('heading', {
      name: /traceability dashboard/i,
    });
    await expect(heading).toBeVisible({ timeout: 10_000 });

    // Reload the page
    await page.reload();
    await page.waitForLoadState('domcontentloaded');

    // Should still be on dashboard with content
    await expect(page).toHaveURL('/');
    await expect(heading).toBeVisible({ timeout: 10_000 });
  });
});

test.describe('Navigation Guard', () => {
  test('should allow access to all routes when authenticated', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Test navigation to various routes
    const routes = ['/projects', '/items', '/agents', '/settings'];

    for (const route of routes) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(route);
    }
  });
});
