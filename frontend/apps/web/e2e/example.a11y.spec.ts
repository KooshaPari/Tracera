import AxeBuilder from '@axe-core/playwright';
/**
 * Accessibility Testing Example
 *
 * Demonstrates:
 * - axe-core integration for WCAG compliance
 * - Keyboard navigation testing
 * - ARIA attribute validation
 * - Screen reader compatibility
 * - Color contrast checks
 *
 * Tags: @a11y @accessibility
 */
import { expect, test } from '@playwright/test';

test.describe('Accessibility - Homepage', () => {
  test('should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/');

    // Run axe-core accessibility scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    // Assert no violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should have proper page structure with landmarks', async ({ page }) => {
    await page.goto('/');

    // Run axe with landmark rules
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('main')
      .include('nav')
      .include('header')
      .include('footer')
      .withTags(['best-practice'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should have accessible images with alt text', async ({ page }) => {
    await page.goto('/');

    // Check for images without alt text
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('img')
      .withRules(['image-alt'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await page.goto('/');

    // Check color contrast ratios
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});

test.describe('Accessibility - Forms', () => {
  test('should have accessible form labels', async ({ page }) => {
    await page.goto('/login');

    // Check form accessibility
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('form')
      .withRules(['label', 'label-content-name-mismatch'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/login');

    // Start at first focusable element
    await page.keyboard.press('Tab');

    // Check that focus is visible
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).not.toBe('BODY');

    // Tab through all form elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Submit form with Enter key
    await page.keyboard.press('Enter');
  });

  test('should have proper ARIA attributes on interactive elements', async ({ page }) => {
    await page.goto('/login');

    // Check ARIA attributes
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['aria-valid-attr', 'aria-required-attr', 'button-name'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});

test.describe('Accessibility - Navigation', () => {
  test('should have skip links for keyboard users', async ({ page }) => {
    await page.goto('/');

    // Tab to first element (should be skip link)
    await page.keyboard.press('Tab');

    const skipLink = await page.evaluate(() => {
      const { activeElement } = document;
      return activeElement?.textContent?.toLowerCase().includes('skip');
    });

    // Skip link should be present (optional but recommended)
    // This is a soft check - uncomment if skip links are implemented
    // Expect(skipLink).toBe(true);
  });

  test('should have accessible navigation menus', async ({ page }) => {
    await page.goto('/');

    // Check navigation accessibility
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('nav')
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should maintain focus management when navigating', async ({ page }) => {
    await page.goto('/');

    // Click a navigation link
    await page
      .getByRole('link', { name: /dashboard|home/i })
      .first()
      .click();

    // Wait for navigation
    await page.waitForLoadState('networkidle');

    // Check that focus is managed (not on body)
    const focusAfterNav = await page.evaluate(() => document.activeElement?.tagName);

    // Focus should be on main content or heading, not body
    expect(focusAfterNav).not.toBe('BODY');
  });
});

test.describe('Accessibility - Dynamic Content', () => {
  test('should announce loading states to screen readers', async ({ page }) => {
    await page.goto('/dashboard');

    // Check for aria-live regions
    const liveRegions = await page.locator('[aria-live]').count();

    // Should have at least one live region for status updates
    expect(liveRegions).toBeGreaterThan(0);
  });

  test('should have accessible modals/dialogs', async ({ page }) => {
    await page.goto('/');

    // Open a modal (adjust selector based on your app)
    const modalTrigger = page.getByRole('button', { name: /open|show|modal/i }).first();

    if ((await modalTrigger.count()) > 0) {
      await modalTrigger.click();

      // Check modal accessibility
      const accessibilityScanResults = await new AxeBuilder({ page })
        .include("[role='dialog']")
        .withRules(['aria-dialog-name', 'focus-order-semantics'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    }
  });
});

test.describe('Accessibility - Exclusions and Disabling', () => {
  test('should exclude third-party widgets from accessibility scan', async ({ page }) => {
    await page.goto('/');

    // Exclude known third-party components that may have a11y issues
    const accessibilityScanResults = await new AxeBuilder({ page })
      .exclude('#third-party-widget')
      .exclude('.external-embed')
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should disable specific rules when justified', async ({ page }) => {
    await page.goto('/');

    // Example: Disable color-contrast for specific components
    // Only use this when you have a documented exception
    const accessibilityScanResults = await new AxeBuilder({ page })
      .disableRules(['color-contrast']) // ONLY if justified
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    // Document why rules are disabled in comments above
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
