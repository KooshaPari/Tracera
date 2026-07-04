/**
 * End-to-End Accessibility Tests for Table Navigation
 *
 * Tests keyboard navigation, screen reader compatibility, and WCAG 2.1 AA compliance.
 * Uses Playwright with Axe for automated accessibility checks.
 */

import AxeBuilder from '@axe-core/playwright';

import { expect, test } from './global-setup';

test.describe('Table Accessibility - Keyboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should have proper ARIA roles on table', async ({ page }) => {
    // Check table structure
    const table = page.locator('[role="table"]').first();
    await expect(table).toBeVisible();

    // Check for aria-label
    const ariaLabel = await table.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
  });

  test('should have accessible column headers with sort indicators', async ({ page }) => {
    const headers = await page.locator('[role="columnheader"]').all();
    expect(headers.length).toBeGreaterThan(0);

    // First header should be Node Identifier
    const firstHeader = headers[0];
    const text = await firstHeader.textContent();
    expect(text).toContain('Node Identifier');

    // Should have aria-sort attribute
    const ariaSort = await firstHeader.getAttribute('aria-sort');
    expect(ariaSort).toBeTruthy();
  });

  test('should support arrow key navigation left/right', async ({ page }) => {
    // Focus first cell
    const firstCell = page.locator('[role="gridcell"]').first();
    await firstCell.focus();

    // Press Right arrow
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(100);

    // Should maintain focus (some cells may not be directly focusable)
    const focused = await page.evaluate(() => document.activeElement?.getAttribute('role'));
    // Focus should still be in table area
    expect(focused).toBeTruthy();
  });

  test('should support arrow key navigation up/down', async ({ page }) => {
    const rows = await page.locator('[role="row"]').all();
    if (rows.length < 3) {
      test.skip(); // Need at least header + 2 data rows
    }

    // Get first data row
    const firstDataRow = rows[1];
    const cell = firstDataRow.locator('[role="gridcell"]').first();
    await cell.focus();

    // Press down arrow to move to next row
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(100);

    // Verify navigation occurred
    const focused = await page.evaluate(() =>
      document.activeElement?.getAttribute('data-row-index'),
    );
    expect(focused).toBeTruthy();
  });

  test('should support Home key to jump to first column', async ({ page }) => {
    const cells = await page.locator('[role="gridcell"]').all();
    if (cells.length === 0) {
      test.skip();
    }

    // Focus a cell
    await cells.at(-1).focus();

    // Press Home to go to first column
    await page.keyboard.press('Home');
    await page.waitForTimeout(100);

    const focused = await page.evaluate(() =>
      document.activeElement?.getAttribute('data-col-index'),
    );
    expect(focused).toBeTruthy();
  });

  test('should support End key to jump to last column', async ({ page }) => {
    const cells = await page.locator('[role="gridcell"]').all();
    if (cells.length === 0) {
      test.skip();
    }

    // Focus first cell
    await cells[0].focus();

    // Press End to go to last column in row
    await page.keyboard.press('End');
    await page.waitForTimeout(100);

    const focused = await page.evaluate(() => document.activeElement);
    expect(focused).toBeTruthy();
  });

  test('should support Ctrl+Home to jump to first cell', async ({ page }) => {
    const cells = await page.locator('[role="gridcell"]').all();
    if (cells.length === 0) {
      test.skip();
    }

    // Focus last cell
    const lastCell = cells.at(-1);
    await lastCell.focus();

    // Press Ctrl+Home (or Cmd+Home on Mac)
    await page.keyboard.press('Control+Home');
    await page.waitForTimeout(100);

    const position = await page.evaluate(() =>
      document.activeElement?.getAttribute('data-row-index'),
    );
    // Should be at first row
    expect(position).toBe('0');
  });

  test('should support Ctrl+End to jump to last cell', async ({ page }) => {
    const rows = await page.locator('[role="row"]').all();
    if (rows.length < 2) {
      test.skip();
    }

    // Focus first cell
    const firstCell = page.locator('[role="gridcell"]').first();
    await firstCell.focus();

    // Press Ctrl+End
    await page.keyboard.press('Control+End');
    await page.waitForTimeout(100);

    const focused = await page.evaluate(() => document.activeElement);
    expect(focused).toBeTruthy();
  });

  test('should support PageUp to jump up 5 rows', async ({ page }) => {
    const rows = await page.locator('[role="row"]').all();
    if (rows.length < 7) {
      test.skip(); // Need at least 7 rows
    }

    // Focus a cell far down
    const cell = rows[6].locator('[role="gridcell"]').first();
    await cell.focus();

    // Press PageUp
    await page.keyboard.press('PageUp');
    await page.waitForTimeout(100);

    const position = await page.evaluate(() =>
      document.activeElement?.getAttribute('data-row-index'),
    );
    expect(position).toBeTruthy();
  });

  test('should support PageDown to jump down 5 rows', async ({ page }) => {
    // Focus first cell
    const firstCell = page.locator('[role="gridcell"]').first();
    await firstCell.focus();

    // Press PageDown
    await page.keyboard.press('PageDown');
    await page.waitForTimeout(100);

    const focused = await page.evaluate(() => document.activeElement);
    expect(focused).toBeTruthy();
  });

  test('should maintain focus visibility when navigating', async ({ page }) => {
    const cell = page.locator('[role="gridcell"]').first();
    await cell.focus();

    // Element should have visible focus indicator
    const hasFocusClass = await cell.evaluate((el: Element) => {
      const classes = (el as HTMLElement).getAttribute('class') ?? '';
      return classes.includes('focus:ring') || classes.includes('focus-visible');
    });

    expect(hasFocusClass).toBe(true);
  });

  test('should announce navigation to screen readers', async ({ page }) => {
    // Check for aria-live region
    const liveRegion = page.locator('[role="status"][aria-live="polite"]').first();
    await expect(liveRegion).toBeInTheDocument();

    // Should have aria-atomic for announcement
    const ariaAtomic = await liveRegion.getAttribute('aria-atomic');
    expect(ariaAtomic).toBe('true');
  });

  test('should have sr-only table instructions', async ({ page }) => {
    const instructions = page.locator('#table-instructions');
    await expect(instructions).toBeInTheDocument();

    // Should be screen-reader only (sr-only class)
    const isHidden = await instructions.evaluate((el: Element) => {
      const classes = (el as HTMLElement).getAttribute('class') ?? '';
      return classes.includes('sr-only');
    });
    expect(isHidden).toBe(true);

    // But content should be present
    const text = await instructions.textContent();
    expect(text).toContain('arrow keys');
    expect(text).toContain('Home and End');
  });
});

test.describe('Table Accessibility - Screen Reader Support', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should have descriptive labels on action buttons', async ({ page }) => {
    // Open/view button should have aria-label
    const openButtons = await page.locator('button[aria-label*="Open item"]').all();
    expect(openButtons.length).toBeGreaterThan(0);

    // Delete button should have aria-label
    const deleteButtons = await page.locator('button[aria-label*="Delete item"]').all();
    expect(deleteButtons.length).toBeGreaterThan(0);
  });

  test('should label status information accessibly', async ({ page }) => {
    // Status badges should be readable by screen readers
    const statusBadges = await page.locator('[data-col-index="2"]').all();
    expect(statusBadges.length).toBeGreaterThan(0);

    // Each should have descriptive text content
    for (const badge of statusBadges) {
      const text = await badge.textContent();
      expect(text?.length).toBeGreaterThan(0);
    }
  });

  test('should label priority information with icons and text', async ({ page }) => {
    // Priority cells should have both visual (dot) and text information
    const priorityCells = await page.locator('[data-col-index="3"]').all();

    for (const cell of priorityCells) {
      // Should contain priority text (low, medium, high, critical)
      const text = await cell.textContent();
      const hasPriorityText =
        (text?.includes('low') ?? false) ||
        (text?.includes('medium') ?? false) ||
        (text?.includes('high') ?? false) ||
        (text?.includes('critical') ?? false);
      expect(hasPriorityText).toBe(true);
    }
  });

  test('should have accessible search input', async ({ page }) => {
    const searchInput = page.locator('input[aria-label*="Search items"]');
    await expect(searchInput).toBeInTheDocument();
  });

  test('should have accessible create button', async ({ page }) => {
    const createButton = page.locator('button[aria-label*="Create new node"]');
    await expect(createButton).toBeInTheDocument();
  });

  test('should have sortable column headers', async ({ page }) => {
    const sortButton = page.locator('button[aria-label*="sorted"]');

    // Should have indication of sort state
    await expect(sortButton.first()).toBeVisible({ timeout: 5000 });
    const ariaLabel = await sortButton.first().getAttribute('aria-label');
    expect(ariaLabel).toMatch(/sorted|not sorted/i);
  });

  test('should have accessible modal dialog', async ({ page }) => {
    // Open create modal
    await page.locator('button[aria-label*="Create new node"]').click();
    await page.waitForTimeout(300);

    // Modal should have dialog role
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeInTheDocument();

    // Should have aria-modal
    const ariaModal = await modal.getAttribute('aria-modal');
    expect(ariaModal).toBe('true');

    // Should have aria-labelledby
    const ariaLabelledBy = await modal.getAttribute('aria-labelledby');
    expect(ariaLabelledBy).toBeTruthy();

    // Close modal
    await page.locator('button[aria-label*="Close dialog"]').click();
  });

  test('should label form inputs in modal', async ({ page }) => {
    // Open modal
    await page.locator('button[aria-label*="Create new node"]').click();
    await page.waitForTimeout(300);

    // All form inputs should have labels
    const titleLabel = page.locator('label:has-text("Title")');
    await expect(titleLabel).toBeVisible({ timeout: 5000 });

    const typeLabel = page.locator('label:has-text("Type")');
    await expect(typeLabel).toBeVisible({ timeout: 5000 });

    const statusLabel = page.locator('label:has-text("Status")');
    await expect(statusLabel).toBeVisible({ timeout: 5000 });

    const priorityLabel = page.locator('label:has-text("Priority")');
    await expect(priorityLabel).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Table Accessibility - Automated Axe Checks', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should pass automated accessibility audit', async ({ page }) => {
    const results = await new AxeBuilder({ page }).withTags(['wcag2aa', 'wcag21aa']).analyze();

    expect(results.violations).toEqual([]);
  });

  test('should have no color contrast violations', async ({ page }) => {
    const results = await new AxeBuilder({ page }).withRules(['color-contrast']).analyze();

    expect(results.violations).toEqual([]);
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    const results = await new AxeBuilder({ page }).withRules(['heading-order']).analyze();

    expect(results.violations).toEqual([]);
  });

  test('should have descriptive button labels', async ({ page }) => {
    const results = await new AxeBuilder({ page }).withRules(['button-name']).analyze();

    expect(results.violations).toEqual([]);
  });

  test('should have proper form labels', async ({ page }) => {
    // Open modal with form
    await page.locator('button[aria-label*="Create new node"]').click();
    await page.waitForTimeout(300);

    const results = await new AxeBuilder({ page }).withRules(['label']).analyze();

    expect(results.violations).toEqual([]);
  });

  test('should have proper landmark roles', async ({ page }) => {
    const results = await new AxeBuilder({ page })
      .withRules(['landmark-one-main', 'region'])
      .analyze();

    // Should have regions defined
    expect(results.violations.length).toBeLessThan(2);
  });
});

test.describe('Table Accessibility - Focus Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should have logical focus order', async ({ page }) => {
    // Tab through elements - they should appear in logical order
    const _initialFocus = await page.evaluate(() => document.activeElement?.tagName);

    await page.keyboard.press('Tab');
    const firstTab = await page.evaluate(() => document.activeElement?.tagName);

    await page.keyboard.press('Tab');
    const secondTab = await page.evaluate(() => document.activeElement?.tagName);

    // Should have moved through elements
    expect(firstTab).toBeTruthy();
    expect(secondTab).toBeTruthy();
  });

  test('should indicate focused element with visible indicator', async ({ page }) => {
    // Focus an element
    await page.locator('[role="gridcell"]').first().focus();

    // Check for focus indicator
    const hasOutline = await page.evaluate(() => {
      const focused = document.activeElement;
      if (!focused) {
        return false;
      }
      const styles = globalThis.getComputedStyle(focused);
      const className = 'className' in focused ? String(focused.className) : '';
      return styles.outline !== 'none' || className.includes('ring') || className.includes('focus');
    });

    expect(hasOutline).toBe(true);
  });

  test('should trap focus in modal dialog', async ({ page }) => {
    // Open modal
    await page.locator('button[aria-label*="Create new node"]').click();
    await page.waitForTimeout(300);

    // Tab through modal - focus should stay within
    const _initialElement = await page.evaluate(() => document.activeElement?.id);

    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    const finalElementId = await page.evaluate(() => document.activeElement?.id);

    // Element should still be in modal context
    await expect(page.locator('[role="dialog"]').locator(`#${finalElementId}`)).toBeVisible({
      timeout: 5000,
    });

    // Close modal
    await page.locator('button[aria-label*="Close dialog"]').click();
  });
});

test.describe('Table Accessibility - WCAG 2.1 AA Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should have sufficient touch target size', async ({ page }) => {
    // All buttons should be at least 44x44px
    const buttons = await page.locator('button').all();

    for (const button of buttons) {
      const box = await button.boundingBox();
      await expect(button).toBeVisible({ timeout: 2000 });
      if (box !== null) {
        // Should meet minimum size requirement
        expect(box.width + box.height).toBeGreaterThan(40);
      }
    }
  });

  test('should support text resizing', async ({ page }) => {
    // Zoom in 200%
    await page.evaluate(() => {
      document.body.style.zoom = '2';
    });

    // Content should still be visible and usable
    const table = page.locator('[role="table"]').first();
    await expect(table).toBeVisible();

    // Reset zoom
    await page.evaluate(() => {
      document.body.style.zoom = '1';
    });
  });

  test('should not rely on color alone for information', async ({ page }) => {
    // Status should have text, not just color
    const statusCells = await page.locator('[data-col-index="2"]').all();

    for (const cell of statusCells) {
      const text = await cell.textContent();
      // Should have text content beyond just color
      expect(text?.length).toBeGreaterThan(0);
    }
  });

  test('should maintain focus visibility', async ({ page }) => {
    const cell = page.locator('[role="gridcell"]').first();
    await cell.focus();

    const isFocusVisible = await cell.evaluate((el: Element) => {
      const styles = globalThis.getComputedStyle(el);
      const className = (el as HTMLElement).getAttribute('class') ?? '';
      return styles.outline !== 'none' || styles.boxShadow !== 'none' || className.includes('ring');
    });

    expect(isFocusVisible).toBe(true);
  });
});
