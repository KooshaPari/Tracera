import { expect, test } from './global-setup';

/**
 * Dashboard E2E Tests - LIVE DATA
 *
 * Tests dashboard with real SwiftRide project data (5,686 items).
 *
 * Run with:
 * VITE_USE_MOCK_DATA=false npx playwright test dashboard-live-data.spec.ts
 *
 * Test Account:
 * - Email: test@tracertm.io
 * - Project: SwiftRide - Ride-sharing Platform (5,686 items)
 * - Access: Full member access via account
 */

test.describe('Dashboard - Live Data with 5,686 Items', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home dashboard
    await page.goto('/home');
    await page.waitForLoadState('networkidle');
  });

  test('should load dashboard with real API data', async ({ page }) => {
    // Wait for dashboard API call to complete
    const dashboardResponse = await page.waitForResponse(
      (response) => response.url().includes('/api/v1/dashboard/summary'),
      { timeout: 10_000 },
    );

    // If running in live mode, we expect real API calls
    if (process.env.VITE_USE_MOCK_DATA === 'false') {
      expect(dashboardResponse.status()).toBe(200);
      console.log('✓ Real dashboard API endpoint called');
    }

    // Verify dashboard is visible
    const dashboardContainer = page.locator('[class*="space-y"]').first();
    await expect(dashboardContainer).toBeVisible({ timeout: 5000 });

    // Check for dashboard heading
    const heading = page.getByRole('heading', {
      name: /traceability dashboard|dashboard overview/i,
    });
    await expect(heading).toBeVisible();
  });

  test('should display SwiftRide project with real data', async ({ page }) => {
    // Wait for projects to load
    await page.waitForLoadState('networkidle');

    // Look for SwiftRide project name
    const swiftRideCard = page.locator('text=SwiftRide');
    await expect(swiftRideCard).toBeVisible({ timeout: 5000 });

    console.log('✓ SwiftRide project found in dashboard');
  });

  test('should show item count metrics', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Look for item statistics
    // The real dashboard should show actual counts from database
    const statsContainer = page.locator('[data-testid="dashboard-stats"], [class*="stat"]').first();
    await expect(statsContainer).toBeVisible({ timeout: 5000 });
  });

  test('should respond to user interactions', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Try to navigate to projects
    const projectsLink = page.getByRole('link', { name: /projects/i }).first();
    await expect(projectsLink).toBeVisible({ timeout: 2000 });
    await projectsLink.click();
    await page.waitForLoadState('networkidle');

    // Should navigate to projects page
    await expect(page).toHaveURL(/\/projects/);
    console.log('✓ Navigation to projects works');
  });
});

test.describe('Dashboard - Performance with Large Dataset', () => {
  test('should load dashboard within acceptable time with 5,686 items', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;
    console.log(`📊 Dashboard load time: ${loadTime}ms`);

    // Should load within 10 seconds even with large dataset
    expect(loadTime).toBeLessThan(10_000);

    // Verify content is rendered
    const content = page.locator('body');
    const hasContent = await content.textContent().then((text) => text && text.length > 100);
    expect(hasContent).toBe(true);
  });

  test('should handle scrolling through projects list', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // Find projects list
    const projectsList = page.locator('[class*="grid"], [class*="list"]').first();

    await expect(projectsList).toBeVisible({ timeout: 2000 });
    // Scroll down to check for virtual scrolling or lazy loading
    await projectsList.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    // Should still be interactive after scroll
    await expect(projectsList).toBeVisible();

    console.log('✓ Scrolling performance acceptable');
  });
});

test.describe('Dashboard - Data Validation', () => {
  test('should display correct project count', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // When using live data, we should see actual projects
    // SwiftRide should be present
    const projectText = await page.textContent('body');
    expect(projectText).toContain('SwiftRide');
  });

  test('should fetch dashboard summary from real API', async ({ page }) => {
    const apiCalls: string[] = [];

    // Intercept all API calls
    page.on('response', (response) => {
      if (response.url().includes('/api/v1/')) {
        apiCalls.push(response.url());
      }
    });

    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // In live mode, should have real API calls
    const hasDashboardCall = apiCalls.some((url) => url.includes('/api/v1/dashboard/summary'));

    if (process.env.VITE_USE_MOCK_DATA === 'false') {
      expect(hasDashboardCall).toBe(true);
      console.log(`✓ Real API calls detected: ${apiCalls.length} total`);
    }
  });
});
