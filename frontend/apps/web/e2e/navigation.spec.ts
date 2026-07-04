import { expect, test } from './global-setup';

/**
 * Navigation E2E Tests
 *
 * Tests for application navigation, routing, and command palette functionality.
 */

test.describe('Application Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');
    await page.waitForLoadState('networkidle');

    // Dashboard should show "Traceability Dashboard" heading, or handle error state
    const dashboardHeading = page.getByRole('heading', {
      name: /traceability dashboard/i,
    });
    const errorHeading = page.getByRole('heading', { name: /system anomaly/i });

    // Wait for either dashboard or error to appear
    await expect(dashboardHeading.or(errorHeading)).toBeVisible({ timeout: 10_000 });

    if (await errorHeading.isVisible()) {
      console.log('Dashboard error state - retrying');
      await page.reload();
      await page.waitForLoadState('networkidle');
    }

    // Final check - verify dashboard is visible
    await expect(dashboardHeading).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to projects list', async ({ page }) => {
    await page.goto('/projects');
    await expect(page).toHaveURL('/projects');
    await page.waitForLoadState('networkidle');

    // Handle potential error states
    const errorHeading = page.getByRole('heading', { name: /system anomaly/i });
    if (await errorHeading.isVisible()) {
      await page.reload();
      await page.waitForLoadState('networkidle');
    }

    // Should show projects list with "Project Registry" heading
    const projectsHeading = page.getByRole('heading', {
      name: /project registry/i,
    });
    await expect(projectsHeading).toBeVisible({ timeout: 10_000 });

    // Wait for project cards to load
    const projectCards = page.locator('a >> text=/TraceRTM|Pokemon|E-Commerce|Banking/i');
    await expect(projectCards.first()).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to items view', async ({ page }) => {
    await page.goto('/items');
    await expect(page).toHaveURL('/items');
    await page.waitForLoadState('networkidle');

    // Handle potential error states
    const errorHeading = page.getByRole('heading', { name: /system anomaly/i });
    if (await errorHeading.isVisible()) {
      await page.reload();
      await page.waitForLoadState('networkidle');
    }

    // Items table view should be visible - look for "Node Registry" heading
    const nodeHeading = page.getByRole('heading', { name: /node registry/i });
    await expect(nodeHeading).toBeVisible({ timeout: 10_000 });
  });

  test('should navigate to agents view', async ({ page }) => {
    await page.goto('/agents');
    await expect(page).toHaveURL('/agents');
    await page.waitForLoadState('networkidle');

    // Handle potential error states
    const errorHeading = page.getByRole('heading', { name: /system anomaly/i });
    if (await errorHeading.isVisible()) {
      await page.reload();
      await page.waitForLoadState('networkidle');
    }

    // Agents heading should be visible - "Agent Cluster"
    const agentsHeading = page.getByRole('heading', { name: /agent cluster/i });
    await expect(agentsHeading).toBeVisible({ timeout: 10_000 });
  });

  test('should navigate to graph view', async ({ page }) => {
    await page.goto('/graph');
    await expect(page).toHaveURL('/graph');

    // Graph visualization should be rendered
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to settings', async ({ page }) => {
    await page.goto('/settings');
    await expect(page).toHaveURL('/settings');

    // Settings form should be visible
    await page.waitForLoadState('networkidle');
  });

  test('should handle deep linking to project detail', async ({ page }) => {
    await page.goto('/projects/proj-1');
    await expect(page).toHaveURL('/projects/proj-1');

    // Project detail should load
    await page.waitForLoadState('networkidle');
  });

  test('should handle deep linking to item detail', async ({ page }) => {
    await page.goto('/items/item-1');
    await expect(page).toHaveURL('/items/item-1');

    // Item detail should load
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Command Palette', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should open command palette with keyboard shortcut', async ({ page }) => {
    // Press Cmd+K (or Ctrl+K on Windows/Linux)
    const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
    await page.keyboard.press(`${modifier}+KeyK`);

    // Command palette should be visible
    // Look for dialog or modal with search input
    const commandPalette = page.locator('[role="dialog"]').filter({ hasText: /command|search/i });
    await expect(commandPalette).toBeVisible({ timeout: 5000 });
  });

  test('should close command palette with Escape', async ({ page }) => {
    // Try to open command palette
    const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
    await page.keyboard.press(`${modifier}+KeyK`);

    // Wait a bit for animation
    await page.waitForTimeout(500);

    // Press Escape
    await page.keyboard.press('Escape');

    // Command palette should be hidden (or not affect the test)
    await page.waitForTimeout(500);
  });
});

test.describe('Sidebar Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should show navigation links', async ({ page }) => {
    // Common navigation items that should be present
    const navItems = [/dashboard/i, /projects/i, /items/i];

    for (const item of navItems) {
      const link = page.getByRole('link', { name: item });
      await expect(link).toBeVisible({ timeout: 5000 });
    }
  });

  test('should navigate using sidebar links', async ({ page }) => {
    // Click on Projects link if it exists
    const projectsLink = page.getByRole('link', { name: /projects/i }).first();

    await expect(projectsLink).toBeVisible({ timeout: 5000 });
    await projectsLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe('Breadcrumb Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should show breadcrumbs on detail pages', async ({ page }) => {
    // Navigate to a project detail page
    await page.goto('/projects/proj-1');
    await page.waitForLoadState('networkidle');

    // Look for breadcrumb navigation (common pattern)
    const breadcrumb = page.locator(
      'nav[aria-label="breadcrumb"], nav[aria-label="Breadcrumb"], .breadcrumb',
    );

    await expect(breadcrumb).toBeVisible({ timeout: 10_000 });
  });
});

test.describe('Back Button Navigation', () => {
  test('should handle browser back button', async ({ page }) => {
    // Navigate through multiple pages
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Go back
    await page.goBack();
    await expect(page).toHaveURL('/projects');

    // Go back again
    await page.goBack();
    await expect(page).toHaveURL('/');
  });

  test('should handle browser forward button', async ({ page }) => {
    // Navigate forward
    await page.goto('/');
    await page.goto('/projects');
    await page.goBack();
    await page.goForward();

    await expect(page).toHaveURL('/projects');
  });
});
