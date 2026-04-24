import { expect, test } from './global-setup';

/**
 * Dashboard Visual Regression Tests
 *
 * Captures screenshots of the dashboard page at multiple viewport sizes
 * to detect unintended visual changes across releases.
 *
 * Tags: @visual @regression @dashboard
 *
 * Run with: bun x playwright test --project=visual dashboard.visual
 */

const viewports = [
  { name: 'desktop', width: 1280, height: 720 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 667 },
] as const;

/**
 * Inject CSS to disable animations and transitions for deterministic screenshots.
 */
async function disableAnimations(page: import('@playwright/test').Page): Promise<void> {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
        caret-color: transparent !important;
      }
    `,
  });
}

test.describe('Dashboard Visual Regression @visual', () => {
  for (const viewport of viewports) {
    test.describe(`${viewport.name} (${viewport.width}x${viewport.height})`, () => {
      test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
      });

      test(`should match dashboard full-page screenshot at ${viewport.name}`, async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Wait for dashboard heading to confirm content has rendered
        const heading = page.getByRole('heading', { name: /traceability dashboard/i });
        await heading.waitFor({ state: 'visible', timeout: 10_000 });

        // Allow charts and widgets to finish rendering
        await page.waitForTimeout(1000);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`dashboard-full-page-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });

      test(`should match dashboard metrics section at ${viewport.name}`, async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Wait for stats/metrics to render
        const activeProjects = page.getByRole('heading', { name: /active projects/i });
        await expect(activeProjects).toBeVisible({ timeout: 10_000 });

        await page.waitForTimeout(500);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`dashboard-metrics-${viewport.name}.png`, {
          fullPage: false,
          maxDiffPixelRatio: 0.01,
        });
      });

      test(`should match dashboard in dark mode at ${viewport.name}`, async ({ page }) => {
        await page.emulateMedia({ colorScheme: 'dark' });
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        const heading = page.getByRole('heading', { name: /traceability dashboard/i });
        await expect(heading).toBeVisible({ timeout: 10_000 });

        await page.waitForTimeout(1000);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`dashboard-dark-mode-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });
    });
  }

  test.describe('dashboard interactive states', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
    });

    test('should match dashboard after data loads', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Wait for project cards or content sections to appear
      const content = page.locator('[class*="space-y"]').first();
      await expect(content).toBeVisible({ timeout: 10_000 });

      await page.waitForTimeout(1000);
      await disableAnimations(page);

      await expect(page).toHaveScreenshot('dashboard-loaded-state.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.01,
      });
    });

    test('should match dashboard recent projects section', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      const recentProjects = page.getByText(/recent projects/i);
      await expect(recentProjects).toBeVisible({ timeout: 10_000 });

      await page.waitForTimeout(500);
      await disableAnimations(page);

      await expect(page).toHaveScreenshot('dashboard-recent-projects.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.01,
      });
    });
  });
});
