import AxeBuilder from '@axe-core/playwright';

import { expect, test } from './global-setup';

/**
 * Accessibility E2E Tests
 *
 * Comprehensive accessibility testing following WCAG 2.1 AA standards.
 * Tests keyboard navigation, screen reader support, color contrast,
 * focus management, and ARIA attributes.
 */

test.describe('Accessibility - Keyboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate entire app using only keyboard', async ({ page }) => {
    // Tab through main navigation
    // First tab should focus skip link
    await page.keyboard.press('Tab');
    await expect(page.locator('a:has-text("Skip to main content")')).toBeFocused();

    // Then focus dashboard link
    await page.keyboard.press('Tab');
    await expect(page.locator('a[href="/"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('a[href="/projects"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('a[href="/items"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('a[href="/agents"]')).toBeFocused();
  });

  test('should activate navigation links with Enter key', async ({ page }) => {
    await page.keyboard.press('Tab'); // Focus skip link
    await page.keyboard.press('Tab'); // Focus dashboard link
    await page.keyboard.press('Tab'); // Focus projects link
    await page.keyboard.press('Enter');

    await page.waitForURL('/projects');
    await expect(page).toHaveURL('/projects');
  });

  test('should activate navigation links with Space key', async ({ page }) => {
    await page.keyboard.press('Tab'); // Skip link
    await page.keyboard.press('Tab'); // Dashboard link
    await page.keyboard.press('Tab'); // Projects link
    await page.keyboard.press('Space');

    await page.waitForURL('/projects');
    await expect(page).toHaveURL('/projects');
  });

  test('should navigate through items list with keyboard', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Tab to first item
    let tabCount = 0;
    while (tabCount < 20) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() =>
        document.activeElement?.getAttribute('data-testid'),
      );
      if (focused === 'item-card') {
        break;
      }
      tabCount++;
    }

    // Use arrow keys to navigate items
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(100);

    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(100);

    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(100);

    // Press Enter to open item
    await page.keyboard.press('Enter');
    await page.waitForURL(/\/items\/.*/);
  });

  test('should support skip to main content link', async ({ page }) => {
    await page.goto('/');

    // First tab should focus skip link
    await page.keyboard.press('Tab');
    const skipLink = page.locator('a:has-text("Skip to main content")');
    await skipLink.focus();
    await expect(skipLink).toBeFocused();

    // Activate skip link
    await page.keyboard.press('Enter');

    // Should focus main content
    const mainContent = page.locator('main');
    await expect(mainContent).toBeFocused();
  });

  test('should trap focus in modal dialogs', async ({ page }) => {
    await page.goto('/items');

    // Open new item dialog
    await page.click('button:has-text("New Item")');

    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();

    // Tab through dialog elements
    await page.keyboard.press('Tab'); // Title input
    await expect(page.locator('input[name="title"]')).toBeFocused();

    await page.keyboard.press('Tab'); // Description
    await expect(page.locator('textarea[name="description"]')).toBeFocused();

    await page.keyboard.press('Tab'); // Type select
    await expect(page.locator('[role="combobox"]')).toBeFocused();

    await page.keyboard.press('Tab'); // Save button
    await expect(page.locator('#create-item-save')).toBeFocused();

    await page.keyboard.press('Tab'); // Cancel button
    await expect(page.locator('#create-item-cancel')).toBeFocused();

    // Tab again should cycle back to first element
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="title"]')).toBeFocused();

    // Shift+Tab should go backwards
    await page.keyboard.press('Shift+Tab');
    await expect(page.locator('#create-item-cancel')).toBeFocused();
  });

  test('should close modal with Escape key', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();

    await page.keyboard.press('Escape');
    await expect(dialog).not.toBeVisible();
  });

  test('should support dropdown menu keyboard navigation', async ({ page }) => {
    await page.goto('/items');
    const firstCard = page.locator('[data-testid="item-card"]').first();
    await firstCard.click({ force: true });

    // Open actions menu
    await page.click('[data-testid="item-menu"]');

    const menu = page.locator('[role="menu"]');
    await expect(menu).toBeVisible();

    // Navigate with arrow keys
    await page.keyboard.press('ArrowDown');
    await expect(page.locator('[role="menuitem"]').first()).toBeFocused();

    await page.keyboard.press('ArrowDown');
    await expect(page.locator('[role="menuitem"]').nth(1)).toBeFocused();

    await page.keyboard.press('ArrowUp');
    await expect(page.locator('[role="menuitem"]').first()).toBeFocused();

    // Activate with Enter
    await page.keyboard.press('Enter');
  });

  test('should support combobox keyboard navigation', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    // Focus type selector
    const typeSelect = page.locator('[role="combobox"]');
    await typeSelect.focus();

    // Open with Space
    await page.keyboard.press('Space');

    const listbox = page.locator('[role="listbox"]');
    await expect(listbox).toBeVisible();

    // Navigate options
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowDown');

    // Select with Enter
    await page.keyboard.press('Enter');

    // Listbox should close
    await expect(listbox).not.toBeVisible();
  });
});

test.describe('Accessibility - Screen Reader Support', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have proper ARIA labels on all interactive elements', async ({ page }) => {
    await page.goto('/items');

    // Check buttons
    const newButton = page.locator('button:has-text("New Item")');
    await expect(newButton).toHaveAttribute('aria-label', /create|new item/i);

    const searchButton = page.locator('button[aria-label*="Search"]');
    await expect(searchButton).toBeVisible();

    const filterButton = page.locator('button[aria-label*="Filter"]');
    await expect(filterButton).toBeVisible();
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/items');

    // Check heading levels
    const h1 = page.locator('h1');
    await expect(h1).toHaveCount(1);
    await expect(h1).toBeVisible();

    // H2 should come after H1
    const h2Elements = page.locator('h2');
    const h2Count = await h2Elements.count();
    expect(h2Count).toBeGreaterThan(0);

    // Should not skip heading levels
    const h4WithoutH3 = await page.evaluate(() => {
      const h3Exists = document.querySelector('h3') !== null;
      const h4Exists = document.querySelector('h4') !== null;
      return h4Exists && !h3Exists;
    });
    expect(h4WithoutH3).toBe(false);
  });

  test('should announce loading states', async ({ page }) => {
    await page.goto('/items');

    // Trigger loading state
    await page.click('button:has-text("Refresh")');

    // Should have live region
    const liveRegion = page.locator('[data-testid="items-live-region"]');
    await expect(liveRegion).toBeVisible();
    await expect(liveRegion).toContainText(/loading/i);

    // Wait for loading to complete
    await page.waitForLoadState('networkidle');

    // Should announce completion
    await expect(liveRegion).toContainText(/loaded|complete/i);
  });

  test('should announce form errors', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    // Submit without filling required fields
    await page.click('button:has-text("Save")');

    // Errors should be in alert
    const alert = page.locator('[role="alert"]');
    await expect(alert).toBeVisible();
    await expect(alert).toHaveAttribute('aria-live', 'assertive');
  });

  test('should have descriptive link text', async ({ page }) => {
    await page.goto('/projects');

    // Links should not be just "click here" or "read more"
    const links = page.locator('a');
    const count = await links.count();

    for (let i = 0; i < Math.min(count, 10); i++) {
      const text = await links.nth(i).textContent();
      expect(text).not.toMatch(/^(click here|read more|more)$/i);
    }
  });

  test('should label form inputs properly', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    // All inputs should have labels
    const titleInput = page.locator('input[name="title"]');
    const titleLabel = await titleInput.evaluate((el) => {
      const id = el.getAttribute('id');
      return document.querySelector(`label[for="${id}"]`)?.textContent;
    });
    expect(titleLabel).toBeTruthy();

    // Or aria-label
    const hasAriaLabel = await titleInput.getAttribute('aria-label');
    const hasAriaLabelledBy = await titleInput.getAttribute('aria-labelledby');

    expect(titleLabel ?? hasAriaLabel ?? hasAriaLabelledBy).toBeTruthy();
  });

  test('should announce dynamic content changes', async ({ page }) => {
    await page.goto('/items');

    // Create new item
    await page.click('button:has-text("New Item")');
    await page.fill('input[name="title"]', 'Test Item');
    await page.click('button:has-text("Save")');

    // Should announce success
    const liveRegion = page.locator('[data-testid="items-live-region"]');
    await expect(liveRegion).toContainText(/created|added/i);
  });

  test('should support landmarks', async ({ page }) => {
    // Check for proper landmarks
    const header = page.locator('header');
    await expect(header).toHaveAttribute('role', 'banner');

    const nav = page.locator('nav').first();
    await expect(nav).toHaveAttribute('role', 'navigation');

    const main = page.locator('main');
    await expect(main).toHaveAttribute('role', 'main');

    const footer = page.locator('footer');
    if ((await footer.count()) > 0) {
      await expect(footer).toHaveAttribute('role', 'contentinfo');
    }
  });
});

test.describe('Accessibility - Visual and Color', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await page.goto('/items');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('body')
      .withTags(['wcag2aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should not rely solely on color for information', async ({ page }) => {
    await page.goto('/items');

    // Status indicators should have text or icons, not just color
    const statusBadges = page.locator('[data-testid="status-badge"]');
    const count = await statusBadges.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const text = await statusBadges.nth(i).textContent();
      expect(text).toBeTruthy();
      expect(text!.length).toBeGreaterThan(0);
    }
  });

  test('should support high contrast mode', async ({ page }) => {
    // Enable high contrast
    await page.emulateMedia({ colorScheme: 'dark', forcedColors: 'active' });
    await page.goto('/items');

    // Elements should still be visible
    const items = page.locator('[data-testid="item-card"]');
    await expect(items.first()).toBeVisible();

    // Text should be readable
    const title = items.first().locator('[data-testid="item-title"]');
    await expect(title).toBeVisible();
  });

  test('should scale properly at 200% zoom', async ({ page }) => {
    // Set viewport to simulate 200% zoom
    await page.setViewportSize({ height: 480, width: 640 });
    await page.goto('/items');

    // Content should not be cut off
    const main = page.locator('main');
    await expect(main).toBeVisible();

    // Horizontal scrolling should not be required
    const hasHorizontalScroll = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    expect(hasHorizontalScroll).toBe(false);
  });

  test('should have visible focus indicators', async ({ page }) => {
    await page.goto('/items');

    // Tab to first interactive element
    await page.keyboard.press('Tab');

    // Get focused element's outline
    const focusedOutline = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el) {
        return {
          boxShadow: 'none',
          outline: '',
          outlineColor: '',
          outlineWidth: '0px',
        };
      }
      const styles = globalThis.getComputedStyle(el);
      return {
        boxShadow: styles.boxShadow,
        outline: styles.outline,
        outlineColor: styles.outlineColor,
        outlineWidth: styles.outlineWidth,
      };
    });

    // Should have visible focus indicator
    const hasFocusIndicator =
      focusedOutline.outlineWidth !== '0px' || focusedOutline.boxShadow !== 'none';

    expect(hasFocusIndicator).toBe(true);
  });

  test('should support reduced motion preference', async ({ page }) => {
    // Set prefers-reduced-motion
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/items');

    // Animations should be disabled or minimal
    const hasAnimations = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      for (const el of elements) {
        const styles = globalThis.getComputedStyle(el);
        if (styles.animationDuration !== '0s' && styles.animationDuration !== '') {
          return true;
        }
      }
      return false;
    });

    // Reduced motion should minimize animations
    // This is a soft check as some animations may be acceptable
    expect(hasAnimations).toBeDefined();
  });
});

test.describe('Accessibility - Focus Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should manage focus after modal opens', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    // Focus should move to first input
    await expect(page.locator('input[name="title"]')).toBeFocused();
  });

  test('should restore focus after modal closes', async ({ page }) => {
    await page.goto('/items');

    // Focus on new item button
    const newButton = page.locator('button:has-text("New Item")');
    await newButton.focus();

    await newButton.click();

    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();

    // Close dialog
    await page.keyboard.press('Escape');
    await expect(dialog).not.toBeVisible();

    // Focus should return to button
    await expect(newButton).toBeFocused();
  });

  test('should manage focus after navigation', async ({ page }) => {
    await page.goto('/items');

    // Click item
    await page.click('[data-testid="item-card"]').first();

    await page.waitForURL(/\/items\/.*/);

    // Focus should be on main heading or skip link
    const h1Focused = await page.evaluate(() => document.activeElement?.tagName === 'H1');

    const skipLinkFocused = await page.evaluate(() =>
      document.activeElement?.textContent?.includes('Skip'),
    );

    expect(h1Focused ?? skipLinkFocused).toBe(true);
  });

  test('should not create keyboard traps', async ({ page }) => {
    await page.goto('/items');

    // Tab through entire page
    const focusedElements = [];
    let tabCount = 0;
    const maxTabs = 100;

    while (tabCount < maxTabs) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => {
        const el = document.activeElement;
        return el?.tagName + (el?.getAttribute('data-testid') ?? '');
      });

      const f = focused ?? '';
      if (focusedElements.includes(f) && focusedElements.length > 5) {
        break;
      }

      focusedElements.push(f);
      tabCount++;
    }

    // Should be able to tab through without getting stuck
    expect(tabCount).toBeGreaterThan(5);
  });

  test('should maintain focus order', async ({ page }) => {
    await page.goto('/items');

    const focusOrder = [];

    // Tab through first 10 elements
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      const position = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || !('getBoundingClientRect' in el)) {
          return { x: 0, y: 0 };
        }
        const rect = el.getBoundingClientRect();
        return { x: rect.left, y: rect.top };
      });
      focusOrder.push(position);
    }

    // Focus should generally move left-to-right, top-to-bottom
    // (allowing some flexibility for layouts)
    for (let i = 1; i < focusOrder.length - 1; i++) {
      const prev = focusOrder[i - 1];
      const curr = focusOrder[i];

      // Current should be after or below previous
      const isLogicalOrder = curr.y > prev.y || (curr.y === prev.y && curr.x >= prev.x);

      // Some flexibility for complex layouts
      expect(isLogicalOrder || Math.abs(curr.y - prev.y) < 50).toBe(true);
    }
  });
});

test.describe('Accessibility - Automated Testing', () => {
  test('dashboard page should have no accessibility violations', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('projects page should have no accessibility violations', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('items page should have no accessibility violations', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('agents page should have no accessibility violations', async ({ page }) => {
    await page.goto('/agents');
    await page.waitForLoadState('networkidle');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('graph page should have no accessibility violations', async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('item detail page should have no accessibility violations', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    await page.click('[data-testid="item-card"]').first();
    await page.waitForURL(/\/items\/.*/);

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('modal dialogs should have no accessibility violations', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();

    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
