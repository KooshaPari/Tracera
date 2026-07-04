import { expect, test } from './global-setup';

/**
 * E2E Tests for Search and Filter Functionality
 * Tests global search, filters, and command palette
 */
test.describe('Search and Filter', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Global Search', () => {
    test('should show search input in header', async ({ page }) => {
      // Look for search input in header with placeholder
      const searchInput = page.getByPlaceholder(/Search items/i);
      await expect(searchInput).toBeVisible({ timeout: 5000 });
    });

    test('should accept search input', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await expect(searchInput).toBeVisible({ timeout: 5000 });
      // Type search query
      await searchInput.fill('project');
      await page.waitForTimeout(500);

      // Verify input was filled
      const inputValue = await searchInput.inputValue();
      expect(inputValue).toBe('project');
    });

    test('should accept and clear search input', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await expect(searchInput).toBeVisible({ timeout: 5000 });
      // Perform search
      await searchInput.fill('test');
      await page.waitForTimeout(500);

      // Verify input has value
      const inputValue = await searchInput.inputValue();
      expect(inputValue).toBe('test');

      // Clear search
      await searchInput.clear();
      await page.waitForTimeout(500);

      // Verify search input is cleared
      const clearedValue = await searchInput.inputValue();
      expect(clearedValue).toBe('');
    });
  });

  test.describe('Command Palette', () => {
    test('should open command palette with keyboard shortcut', async ({ page }) => {
      // Open with Cmd+K (Mac) or Ctrl+K (Windows/Linux)
      const isMac = process.platform === 'darwin';
      if (isMac) {
        await page.keyboard.press('Meta+K');
      } else {
        await page.keyboard.press('Control+K');
      }

      // Command palette should be visible
      const commandPalette = page.locator('[data-testid="command-palette"]');
      await expect(commandPalette).toBeVisible({ timeout: 5000 });

      // Alternative: check for dialog with search input
      const dialog = page.getByRole('dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });
      const paletteInput = dialog.getByPlaceholder(/search|type.*command/i);
      await expect(paletteInput).toBeVisible();
    });

    test('should search commands in palette', async ({ page }) => {
      // Open command palette
      await page.keyboard.press('Meta+K');

      const dialog = page.getByRole('dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });
      const paletteInput = dialog.getByRole('combobox');
      await paletteInput.fill('project');
      await page.waitForTimeout(500);

      // Should show project-related commands
      const projectCommand = dialog.getByText(/create.*project|new.*project/i);
      await expect(projectCommand).toBeVisible({ timeout: 5000 });
    });

    test('should navigate using command palette', async ({ page }) => {
      // Open command palette
      await page.keyboard.press('Meta+K');

      const dialog = page.getByRole('dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });
      // Type navigation command
      const paletteInput = dialog.getByRole('combobox');
      await paletteInput.fill('items');
      await page.waitForTimeout(500);

      // Select items option
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');

      // Should navigate to items page
      await expect(page).toHaveURL(/\/items/);
    });

    test('should close command palette with escape', async ({ page }) => {
      // Open command palette
      await page.keyboard.press('Meta+K');

      const dialog = page.getByRole('dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });
      // Press escape to close
      await page.keyboard.press('Escape');

      // Dialog should be hidden
      await expect(dialog).not.toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Project Filters', () => {
    test('should filter projects by status', async ({ page }) => {
      await page.getByRole('link', { name: /projects/i }).click();
      await page.waitForLoadState('networkidle');

      // Look for status filter
      const statusFilter = page.getByLabel(/status|filter.*status/i);
      await expect(statusFilter).toBeVisible({ timeout: 5000 });
      await statusFilter.click();
      await page.getByText(/active/i).click();
      await page.waitForLoadState('networkidle');

      // All visible projects should be active
      const projectCards = page.locator('[data-testid="project-card"]');
      await expect(projectCards.first()).toBeVisible({ timeout: 5000 });
    });

    test('should search projects by name', async ({ page }) => {
      await page.getByRole('link', { name: /projects/i }).click();
      await page.waitForLoadState('networkidle');

      const searchInput = page
        .getByRole('searchbox')
        .or(page.getByPlaceholder(/search/i))
        .first();

      await expect(searchInput).toBeVisible({ timeout: 5000 });
      // Search for Pokemon
      await searchInput.fill('Pokemon');
      await page.waitForTimeout(500);

      // Should show Pokemon Go Demo
      const pokemonProject = page.getByText(/Pokemon Go Demo/);
      await expect(pokemonProject).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Items Filters', () => {
    test('should filter items by type', async ({ page }) => {
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Look for type filter
      const typeFilter = page.getByLabel(/type|filter.*type/i);
      await expect(typeFilter).toBeVisible({ timeout: 5000 });
      await typeFilter.click();
      await page
        .getByText(/requirement|feature/i)
        .first()
        .click();
      await page.waitForLoadState('networkidle');
    });

    test('should filter items by status', async ({ page }) => {
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Look for status filter
      const statusFilter = page.getByLabel(/status|filter.*status/i);
      await expect(statusFilter).toBeVisible({ timeout: 5000 });
      await statusFilter.click();
      await page
        .getByText(/todo|done|in_progress/i)
        .first()
        .click();
      await page.waitForLoadState('networkidle');
    });
  });
});
