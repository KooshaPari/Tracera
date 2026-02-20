import percySnapshot from '@percy/playwright';
/**
 * Visual Regression Testing Example with Percy
 *
 * Demonstrates:
 * - Visual snapshots with Percy
 * - Component visual testing
 * - Responsive visual testing
 * - Dark mode visual testing
 *
 * Tags: @visual @percy @regression
 *
 * Setup Required:
 * 1. Set PERCY_TOKEN environment variable
 * 2. Run: npx percy exec -- playwright test --project=visual
 */
import { expect, test } from '@playwright/test';

test.describe('Visual Regression - Homepage', () => {
  test('should match homepage snapshot @visual', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Take Percy snapshot
    await percySnapshot(page, 'Homepage');
  });

  test('should match homepage in dark mode', async ({ page }) => {
    // Set dark mode
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await percySnapshot(page, 'Homepage - Dark Mode');
  });

  test('should match homepage on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ height: 667, width: 375 }); // IPhone SE

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await percySnapshot(page, 'Homepage - Mobile', {
      widths: [375, 414], // IPhone SE, iPhone 11
    });
  });

  test('should match homepage on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ height: 1024, width: 768 }); // IPad

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await percySnapshot(page, 'Homepage - Tablet', {
      widths: [768, 1024], // IPad portrait and landscape
    });
  });
});

test.describe('Visual Regression - Components', () => {
  test('should match button states', async ({ page }) => {
    await page.goto('/components/buttons'); // Adjust URL to your component showcase

    // Default state
    await percySnapshot(page, 'Buttons - Default');

    // Hover state
    await page.hover('button:first-of-type');
    await percySnapshot(page, 'Buttons - Hover');

    // Focus state
    await page.focus('button:first-of-type');
    await percySnapshot(page, 'Buttons - Focus');

    // Disabled state
    await percySnapshot(page, 'Buttons - All States');
  });

  test('should match form components', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Empty form
    await percySnapshot(page, 'Login Form - Empty');

    // Filled form
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await percySnapshot(page, 'Login Form - Filled');

    // Form with validation errors
    await page.fill('input[type="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500); // Wait for validation
    await percySnapshot(page, 'Login Form - Validation Errors');
  });

  test('should match navigation states', async ({ page }) => {
    await page.goto('/');

    // Default navigation
    await percySnapshot(page, 'Navigation - Default');

    // Open mobile menu (if applicable)
    const menuButton = page.locator('button[aria-label*="menu"]').first();
    if ((await menuButton.count()) > 0) {
      await menuButton.click();
      await page.waitForTimeout(300); // Animation
      await percySnapshot(page, 'Navigation - Mobile Menu Open');
    }
  });
});

test.describe('Visual Regression - Responsive Breakpoints', () => {
  const breakpoints = [
    { height: 568, name: 'Mobile Small', width: 320 }, // IPhone 5/SE
    { height: 667, name: 'Mobile', width: 375 }, // IPhone 6/7/8
    { height: 896, name: 'Mobile Large', width: 414 }, // IPhone 11
    { height: 1024, name: 'Tablet', width: 768 }, // IPad
    { height: 768, name: 'Desktop Small', width: 1024 }, // Small laptop
    { height: 800, name: 'Desktop', width: 1280 }, // Standard desktop
    { height: 1080, name: 'Desktop Large', width: 1920 }, // Full HD
  ];

  for (const breakpoint of breakpoints) {
    test(`should match at ${breakpoint.name} breakpoint`, async ({ page }) => {
      await page.setViewportSize({
        height: breakpoint.height,
        width: breakpoint.width,
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      await percySnapshot(page, `Breakpoint - ${breakpoint.name}`, {
        widths: [breakpoint.width],
      });
    });
  }
});

test.describe('Visual Regression - Interactive States', () => {
  test('should match modal dialogs', async ({ page }) => {
    await page.goto('/');

    // Find and click modal trigger (adjust selector)
    const modalTrigger = page.getByRole('button', { name: /open|show/i }).first();

    if ((await modalTrigger.count()) > 0) {
      await modalTrigger.click();
      await page.waitForTimeout(300); // Wait for animation

      // Modal open
      await percySnapshot(page, 'Modal - Open');

      // Close modal
      const closeButton = page.getByRole('button', { name: /close/i }).first();
      await closeButton.click();
      await page.waitForTimeout(300);

      // Modal closed
      await percySnapshot(page, 'Modal - Closed');
    }
  });

  test('should match dropdown menus', async ({ page }) => {
    await page.goto('/');

    // Find dropdown (adjust selector)
    const dropdown = page.locator('[role="combobox"], select').first();

    if ((await dropdown.count()) > 0) {
      // Closed state
      await percySnapshot(page, 'Dropdown - Closed');

      // Open state
      await dropdown.click();
      await page.waitForTimeout(200);
      await percySnapshot(page, 'Dropdown - Open');
    }
  });

  test('should match loading states', async ({ page }) => {
    await page.goto('/dashboard');

    // Capture loading state (may need to throttle network)
    await percySnapshot(page, 'Dashboard - Loading');

    // Wait for load completion
    await page.waitForLoadState('networkidle');
    await percySnapshot(page, 'Dashboard - Loaded');
  });
});

test.describe('Visual Regression - Data Visualizations', () => {
  test('should match charts and graphs', async ({ page }) => {
    await page.goto('/analytics'); // Adjust to your analytics page

    await page.waitForLoadState('networkidle');

    // Wait for charts to render
    await page.waitForTimeout(1000);

    // Full page snapshot
    await percySnapshot(page, 'Analytics - Charts');
  });

  test('should match tables with data', async ({ page }) => {
    await page.goto('/data-table'); // Adjust to your data table page

    await page.waitForLoadState('networkidle');

    // Default table view
    await percySnapshot(page, 'Data Table - Default');

    // Sorted table (if sortable)
    const sortButton = page.locator('th[role="columnheader"]').first();
    if ((await sortButton.count()) > 0) {
      await sortButton.click();
      await page.waitForTimeout(300);
      await percySnapshot(page, 'Data Table - Sorted');
    }
  });
});

test.describe('Visual Regression - Error States', () => {
  test('should match 404 page', async ({ page }) => {
    await page.goto('/non-existent-page');
    await page.waitForLoadState('networkidle');

    await percySnapshot(page, '404 Error Page');
  });

  test('should match error messages', async ({ page }) => {
    await page.goto('/login');

    // Trigger error (invalid credentials)
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Wait for error message
    await page.waitForTimeout(1000);

    await percySnapshot(page, 'Login - Error Message');
  });
});

test.describe('Visual Regression - Advanced Options', () => {
  test('should use Percy snapshot options', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Snapshot with custom options
    await percySnapshot(page, 'Homepage - Advanced', {
      widths: [375, 768, 1280], // Multiple widths
      minHeight: 1024, // Minimum height
      percyCSS: `
				/* Hide dynamic content from snapshot */
				.timestamp, .live-update {
					display: none !important;
				}
			`,
      // Scope to specific element
      scope: '#main-content',
    });
  });

  test('should handle animations', async ({ page }) => {
    await page.goto('/');

    // Disable animations for consistent snapshots
    await page.addStyleTag({
      content: `
				*, *::before, *::after {
					animation-duration: 0s !important;
					animation-delay: 0s !important;
					transition-duration: 0s !important;
					transition-delay: 0s !important;
				}
			`,
    });

    await page.waitForLoadState('networkidle');
    await percySnapshot(page, 'Homepage - No Animations');
  });
});
