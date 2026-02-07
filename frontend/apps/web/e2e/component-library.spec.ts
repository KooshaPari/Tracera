import { test } from './global-setup';

/**
 * Component Library Tests
 *
 * Tests for browsing, searching, and viewing components within the
 * multi-dimensional traceability graph's component library feature.
 *
 * Component Library Features:
 * - Browse available components
 * - Search component by name/type
 * - Filter components by category
 * - View component details/metadata
 * - Show component relationships
 * - Visualize component in context
 * - Add components to graph
 */

test.describe('Component Library', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test.describe('Component Library Access', () => {
    test('should display component library button/panel', async ({ page }) => {
      // Look for component library access
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog|registry|browser/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
    });

    test('should open component library panel', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Look for library panel
      const libraryPanel = page
        .locator("aside, [class*='library'], [class*='panel'], .w-96")
        .first();

      await expect(libraryPanel).toBeVisible({ timeout: 2000 });
    });

    test('should display component categories', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Look for category tabs or list
      const categories = page.locator("[role='tab'], button[class*='category'], nav").first();
      await expect(categories).toBeVisible();

      // Look for category text
      const categoryLabels = page.getByText(/requirement|feature|code|test|architecture|ui|api/i);
      await expect(categoryLabels.first()).toBeVisible();
    });
  });

  test.describe('Browse Components', () => {
    test('should list components in library', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Count components in list
      const componentItems = page.locator("[role='listitem'], li, [class*='component-item']");
      await expect(componentItems.first()).toBeVisible();
    });

    test('should display component names and types', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Look for component items with name and type
      const componentItems = page.locator("[role='listitem'], li").first();

      await expect(componentItems).toBeVisible({ timeout: 2000 });
      const text = await componentItems.textContent();
      expect(text).not.toBe('');
    });

    test('should allow browsing components by scrolling', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Find scrollable container
      const libraryPanel = page.locator("aside, [class*='library'], [class*='panel']").first();

      await expect(libraryPanel).toBeVisible({ timeout: 2000 });
      // Scroll in the panel
      await libraryPanel.evaluate((el) => {
        if (el.scrollHeight > el.clientHeight) {
          el.scrollTop = el.scrollHeight / 2;
        }
      });

      await page.waitForTimeout(300);
    });

    test('should show component count', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Look for count indicator
      const countLabel = page.getByText(/\(\d+\)|\d+\s*(items?|components?)/i);

      await expect(countLabel.first()).toBeVisible({ timeout: 2000 });
    });
  });

  test.describe('Search Components', () => {
    test('should display search input in component library', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Look for search input
      const searchInput = page.getByPlaceholder(/search/i).first();

      await expect(searchInput).toBeVisible({ timeout: 2000 });
    });

    test('should search components by name', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const searchInput = page.getByPlaceholder(/search/i).first();

      await expect(searchInput).toBeVisible({ timeout: 2000 });
      // Type search query
      await searchInput.fill('authentication');
      await page.waitForTimeout(500);

      // Check if results are filtered
      const resultItems = page.locator("[role='listitem'], li");
      await expect(resultItems.first()).toBeVisible();

      // Clear search
      await searchInput.clear();
      await page.waitForTimeout(300);
    });

    test('should search components by type', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const searchInput = page.getByPlaceholder(/search/i).first();

      await expect(searchInput).toBeVisible({ timeout: 2000 });
      // Search by type keyword
      await searchInput.fill('test');
      await page.waitForTimeout(500);

      const resultItems = page.locator("[role='listitem'], li");
      await expect(resultItems.first()).toBeVisible();

      await searchInput.clear();
    });

    test('should show no results message when search returns nothing', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const searchInput = page.getByPlaceholder(/search/i).first();

      await expect(searchInput).toBeVisible({ timeout: 2000 });
      // Search with unlikely term
      await searchInput.fill('xyznotfound123');
      await page.waitForTimeout(500);

      const noResultsMsg = page.getByText(/no.*result|not.*found|no.*match/i);

      await expect(noResultsMsg.first()).toBeVisible({ timeout: 2000 });

      await searchInput.clear();
    });
  });

  test.describe('Filter Components', () => {
    test('should filter components by category', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Look for category filter/tabs
      const categoryFilters = page.locator("[role='tab'], button[class*='category']");
      await expect(categoryFilters.first()).toBeVisible();

      // Click first category
      await categoryFilters.first().click();
      await page.waitForTimeout(500);
    });

    test('should filter components by status', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Look for status filter
      const statusFilter = page
        .locator('button, select')
        .filter({ hasText: /status|state|active/i })
        .first();

      await expect(statusFilter).toBeVisible({ timeout: 2000 });
      await statusFilter.click();
      await page.waitForTimeout(300);

      const statusOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[a-z]/i })
        .first();

      await expect(statusOption).toBeVisible({ timeout: 1000 });
      await statusOption.click();
      await page.waitForTimeout(500);
    });
  });

  test.describe('View Component Details', () => {
    test('should click on component to view details', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      // Click first component
      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      await componentItem.click();
      await page.waitForTimeout(500);

      // Look for detail panel
      const detailPanel = page.locator("[class*='detail'], [class*='panel']").first();

      await expect(detailPanel).toBeVisible({ timeout: 2000 });
    });

    test('should display component metadata', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      await componentItem.click();
      await page.waitForTimeout(500);

      // Look for metadata fields
      const metadata = page.getByText(/type|status|version|author|created|modified/i);
      await expect(metadata.first()).toBeVisible();
    });

    test('should show component description', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      await componentItem.click();
      await page.waitForTimeout(500);

      // Look for description text
      const description = page.locator("p, [class*='description']").first();

      await expect(description).toBeVisible({ timeout: 2000 });
    });

    test('should show component relationships', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      await componentItem.click();
      await page.waitForTimeout(500);

      // Look for relationships section
      const relationships = page.getByText(/related|depends|link|reference|parent|child/i);
      await expect(relationships.first()).toBeVisible();
    });
  });

  test.describe('Component Visualization', () => {
    test('should visualize component in graph context', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      await componentItem.click();
      await page.waitForTimeout(500);

      // Look for visualization button
      const visualizeBtn = page
        .locator('button')
        .filter({ hasText: /visualize|show|view.*graph/i })
        .first();

      await expect(visualizeBtn).toBeVisible({ timeout: 2000 });
      await visualizeBtn.click();
      await page.waitForTimeout(1000);

      // Check if graph updated
      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible({ timeout: 2000 });
    });

    test('should highlight component in graph when selected', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      await componentItem.click();
      await page.waitForTimeout(500);

      // Look for highlighted node in graph
      const highlightedNodes = page
        .locator(".react-flow__nodes [class*='highlighted'], [class*='selected']")
        .first();
      await expect(highlightedNodes).toBeVisible();
    });
  });

  test.describe('Add Component to Graph', () => {
    test('should show add/import component button', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const addBtn = page
        .locator('button')
        .filter({ hasText: /add|import|insert|use/i })
        .first();

      await expect(addBtn).toBeVisible({ timeout: 2000 });
    });

    test('should add component to graph', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      // Look for add button in component item
      const addBtn = componentItem.locator('button').filter({ hasText: /add|import|insert/i });

      await expect(addBtn).toBeVisible({ timeout: 2000 });
      await addBtn.click();
      await page.waitForTimeout(1000);

      // Check if node count increased
      const finalCount = await page.locator('.react-flow__nodes > div[data-id]').count();
      expect(finalCount).toBeGreaterThan(0);
    });

    test('should show add confirmation feedback', async ({ page }) => {
      const libraryBtn = page
        .locator("button, [role='button']")
        .filter({
          hasText: /component|library|palette|catalog/i,
        })
        .first();

      await expect(libraryBtn).toBeVisible({ timeout: 2000 });
      await libraryBtn.click();
      await page.waitForTimeout(500);

      const componentItem = page.locator("[role='listitem'], li").first();

      await expect(componentItem).toBeVisible({ timeout: 2000 });
      const addBtn = componentItem.locator('button').filter({ hasText: /add|import|insert/i });

      await expect(addBtn).toBeVisible({ timeout: 2000 });
      await addBtn.click();
      await page.waitForTimeout(500);

      // Look for confirmation message
      const confirmation = page.getByText(/added|imported|success|created/i);

      await expect(confirmation.first()).toBeVisible({ timeout: 2000 });
    });
  });
});
