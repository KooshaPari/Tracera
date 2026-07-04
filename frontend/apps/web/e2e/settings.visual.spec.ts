import { expect, test } from './global-setup';

/**
 * Settings Page Visual Regression Tests
 *
 * Captures screenshots of the settings page tabs, forms, and interactive
 * states at multiple viewport sizes to detect unintended visual changes.
 *
 * Tags: @visual @regression @settings
 *
 * Run with: bun x playwright test --project=visual settings.visual
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

test.describe('Settings Visual Regression @visual', () => {
  for (const viewport of viewports) {
    test.describe(`${viewport.name} (${viewport.width}x${viewport.height})`, () => {
      test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
      });

      test(`should match settings general tab at ${viewport.name}`, async ({ page }) => {
        await page.goto('/settings');
        await page.waitForLoadState('networkidle');

        // Wait for settings heading to confirm the page rendered
        const heading = page.getByRole('heading', { name: /settings/i });
        await heading.waitFor({ state: 'visible', timeout: 10_000 });

        // General tab is selected by default
        await page.waitForTimeout(500);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`settings-general-tab-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });

      test(`should match settings appearance tab at ${viewport.name}`, async ({ page }) => {
        await page.goto('/settings');
        await page.waitForLoadState('networkidle');

        // Switch to Appearance tab
        const appearanceTab = page.getByRole('tab', { name: /appearance/i });
        await appearanceTab.waitFor({ state: 'visible', timeout: 10_000 });
        await appearanceTab.click();
        await page.waitForTimeout(500);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`settings-appearance-tab-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });

      test(`should match settings notifications tab at ${viewport.name}`, async ({ page }) => {
        await page.goto('/settings');
        await page.waitForLoadState('networkidle');

        // Switch to Notifications tab
        const notificationsTab = page.getByRole('tab', { name: /notifications/i });
        await notificationsTab.waitFor({ state: 'visible', timeout: 10_000 });
        await notificationsTab.click();
        await page.waitForTimeout(500);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`settings-notifications-tab-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });

      test(`should match settings API tab at ${viewport.name}`, async ({ page }) => {
        await page.goto('/settings');
        await page.waitForLoadState('networkidle');

        // Switch to API tab
        const apiTab = page.getByRole('tab', { name: /api/i });
        await apiTab.waitFor({ state: 'visible', timeout: 10_000 });
        await apiTab.click();
        await page.waitForTimeout(500);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`settings-api-tab-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });
    });
  }

  test.describe('settings form states', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.goto('/settings');
      await page.waitForLoadState('networkidle');
    });

    test('should match settings with filled form fields', async ({ page }) => {
      // Ensure General tab is active
      const generalTab = page.getByRole('tab', { name: /general/i });
      await generalTab.click();
      await page.waitForTimeout(300);

      // Fill in fields to capture a "dirty" form state
      const displayName = page.getByLabel(/display name/i);
      await expect(displayName).toBeVisible({ timeout: 5000 });
      await displayName.fill('Visual Test User');

      const email = page.getByLabel(/email/i);
      await expect(email).toBeVisible({ timeout: 5000 });
      await email.fill('visual-test@example.com');

      await disableAnimations(page);

      await expect(page).toHaveScreenshot('settings-filled-form.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.01,
      });
    });

    test('should match settings with validation error', async ({ page }) => {
      const generalTab = page.getByRole('tab', { name: /general/i });
      await generalTab.click();
      await page.waitForTimeout(300);

      // Enter invalid email to trigger browser validation styling
      const email = page.getByLabel(/email/i);
      await expect(email).toBeVisible({ timeout: 5000 });
      await email.fill('invalid-email');

      // Attempt to save to trigger validation
      const saveButton = page.getByRole('button', { name: /save changes/i });
      await expect(saveButton).toBeVisible({ timeout: 5000 });
      await saveButton.click();
      await page.waitForTimeout(500);

      await disableAnimations(page);

      await expect(page).toHaveScreenshot('settings-validation-error.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.01,
      });
    });
  });

  test.describe('settings dark mode', () => {
    for (const viewport of viewports) {
      test(`should match settings in dark mode at ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.emulateMedia({ colorScheme: 'dark' });
        await page.goto('/settings');
        await page.waitForLoadState('networkidle');

        const heading = page.getByRole('heading', { name: /settings/i });
        await expect(heading).toBeVisible({ timeout: 10_000 });

        await page.waitForTimeout(500);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`settings-dark-mode-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });
    }
  });
});
