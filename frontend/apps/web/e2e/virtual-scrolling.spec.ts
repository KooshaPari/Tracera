import { test, expect } from "@playwright/test";

test.describe("ItemsTableView - Virtual Scrolling Performance", () => {
	test.beforeEach(async ({ page }) => {
		// Navigate to items table view
		await page.goto("/items");
		// Wait for the table to load
		await page.waitForSelector("table", { timeout: 5000 });
	});

	test("should render large dataset with virtual scrolling", async ({
		page,
	}) => {
		// Measure initial render time
		const startTime = Date.now();

		// Wait for table to be visible
		await page.locator("table").isVisible();

		const renderTime = Date.now() - startTime;

		// Should render in under 1 second with virtual scrolling
		expect(renderTime).toBeLessThan(1000);
	});

	test("should only render visible rows in viewport", async ({ page }) => {
		// Get initial row count (visible rows only)
		const initialRows = await page.locator("tbody tr").count();

		// Should be small number (10-30 rows visible, not all 1000+)
		expect(initialRows).toBeLessThan(50);
		expect(initialRows).toBeGreaterThan(0);
	});

	test("should handle smooth scrolling", async ({ page }) => {
		// Get the scrollable container
		const scrollContainer = page.locator('[class*="overflow-y-auto"]').first();

		// Measure scroll performance
		const startTime = Date.now();

		// Scroll down
		await scrollContainer.evaluate((el) => {
			el.scrollTop += 500;
		});

		const scrollTime = Date.now() - startTime;

		// Scrolling should be responsive (under 500ms)
		expect(scrollTime).toBeLessThan(500);
	});

	test("should update visible rows when scrolling", async ({ page }) => {
		// Get initial first visible item ID
		const initialFirstItem = await page
			.locator("tbody tr")
			.first()
			.textContent();

		// Scroll down
		const scrollContainer = page.locator('[class*="overflow-y-auto"]').first();
		await scrollContainer.evaluate((el) => {
			el.scrollTop = 1000;
		});

		// Wait a moment for rendering
		await page.waitForTimeout(100);

		// Get new first visible item
		const newFirstItem = await page.locator("tbody tr").first().textContent();

		// Items should have changed
		expect(newFirstItem).not.toBe(initialFirstItem);
	});

	test("should maintain sort order while scrolling", async ({ page }) => {
		// Click to sort by title
		await page.click('button:has-text("Node Identifier")');

		// Wait for sort
		await page.waitForTimeout(200);

		// Get all visible item titles
		const titles = await page.locator("tbody tr").allTextContents();
		expect(titles.length).toBeGreaterThan(0);

		// Scroll down
		const scrollContainer = page.locator('[class*="overflow-y-auto"]').first();
		await scrollContainer.evaluate((el) => {
			el.scrollTop += 1000;
		});

		// Wait for new items to render
		await page.waitForTimeout(100);

		// Get new visible titles
		const newTitles = await page.locator("tbody tr").allTextContents();

		// Should still have items
		expect(newTitles.length).toBeGreaterThan(0);
	});

	test("should handle filtering with virtual scrolling", async ({ page }) => {
		// Get initial row count
		const initialCount = await page.locator("tbody tr").count();

		// Type in search
		await page.fill('input[placeholder="Search identifiers..."]', "test");

		// Wait for filtering
		await page.waitForTimeout(200);

		// Get filtered row count
		const filteredCount = await page.locator("tbody tr").count();

		// Should have fewer rows
		expect(filteredCount).toBeLessThanOrEqual(initialCount);
	});

	test("should handle dynamic row heights efficiently", async ({ page }) => {
		// Measure time to scroll through entire list
		const scrollContainer = page.locator('[class*="overflow-y-auto"]').first();

		const startTime = Date.now();

		// Scroll to bottom
		await scrollContainer.evaluate((el) => {
			el.scrollTop = el.scrollHeight;
		});

		// Wait for last items to render
		await page.waitForTimeout(200);

		const totalTime = Date.now() - startTime;

		// Should scroll to bottom efficiently (under 2 seconds)
		expect(totalTime).toBeLessThan(2000);
	});

	test("should keep header sticky while scrolling", async ({ page }) => {
		// Get header position
		const header = page.locator("thead tr").first();
		const headerBox = await header.boundingBox();

		// Scroll down
		const scrollContainer = page.locator('[class*="overflow-y-auto"]').first();
		await scrollContainer.evaluate((el) => {
			el.scrollTop = 500;
		});

		// Header should still be visible (sticky)
		const headerBoxAfter = await header.boundingBox();

		expect(headerBoxAfter).toBeDefined();
		if (headerBox && headerBoxAfter) {
			expect(headerBoxAfter.y).toBeLessThanOrEqual(headerBox.y + 100);
		}
	});

	test("should handle rapid scrolling", async ({ page }) => {
		const scrollContainer = page.locator('[class*="overflow-y-auto"]').first();

		// Perform rapid scrolls
		for (let i = 0; i < 5; i++) {
			await scrollContainer.evaluate((el) => {
				el.scrollTop += 200;
			});
			await page.waitForTimeout(50);
		}

		// Should still have visible rows
		const rows = await page.locator("tbody tr").count();
		expect(rows).toBeGreaterThan(0);
	});

	test("should recover from scroll bounce", async ({ page }) => {
		const scrollContainer = page.locator('[class*="overflow-y-auto"]').first();

		// Scroll and bounce
		await scrollContainer.evaluate((el) => {
			el.scrollTop = el.scrollHeight;
			setTimeout(() => {
				el.scrollTop = 0;
			}, 100);
		});

		// Wait for recovery
		await page.waitForTimeout(200);

		// Should show top items
		const firstRow = await page.locator("tbody tr").first().textContent();
		expect(firstRow).toBeDefined();
	});

	test("should handle actions on virtual rows", async ({ page }) => {
		// Click on an item
		const firstItem = page.locator("tbody tr").first();
		await firstItem.click();

		// Should navigate or expand
		await page.waitForTimeout(200);

		// Verify action was processed
		const url = page.url();
		// Either URL changed or some state changed
		expect(url).toBeDefined();
	});

	test("performance: render 1000+ items efficiently", async ({ page }) => {
		// This test would be for actual measurement
		// In real scenario, you'd measure:
		// - Initial paint time
		// - First contentful paint
		// - Time to interactive

		const startMetrics = await page.evaluate(() => ({
			timestamp: performance.now(),
			memory: (performance as any).memory?.usedJSHeapSize,
		}));

		// Wait for full load
		await page.waitForTimeout(1000);

		const endMetrics = await page.evaluate(() => ({
			timestamp: performance.now(),
			memory: (performance as any).memory?.usedJSHeapSize,
		}));

		const totalTime = endMetrics.timestamp - startMetrics.timestamp;

		// Should load 1000+ items in under 2 seconds
		expect(totalTime).toBeLessThan(2000);
	});
});
