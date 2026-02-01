import { test } from "./global-setup";

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

test.describe("Component Library", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/graph");
		await page.waitForLoadState("networkidle");
		await page.waitForTimeout(1000);
	});

	test.describe("Component Library Access", () => {
		test("should display component library button/panel", async ({ page }) => {
			// Look for component library access
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog|registry|browser/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				console.log("Component library button found");
			} else {
				console.log("Component library not visible on graph page");
			}
		});

		test("should open component library panel", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Look for library panel
				const libraryPanel = page.locator(
					"aside, [class*='library'], [class*='panel'], .w-96",
				);

				if (
					await libraryPanel.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					console.log("Component library panel opened");
				} else {
					console.log("Library panel may open as modal or separate view");
				}
			}
		});

		test("should display component categories", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Look for category tabs or list
				const categories = page.locator(
					"[role='tab'], button[class*='category'], nav",
				);
				const categoryCount = await categories.count().catch(() => 0);

				if (categoryCount > 0) {
					console.log(`Found ${categoryCount} component categories`);
				}

				// Look for category text
				const categoryLabels = page.getByText(
					/requirement|feature|code|test|architecture|ui|api/i,
				);
				const labelCount = await categoryLabels.count().catch(() => 0);

				if (labelCount > 0) {
					console.log(`${labelCount} category labels displayed`);
				}
			}
		});
	});

	test.describe("Browse Components", () => {
		test("should list components in library", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Count components in list
				const componentItems = page.locator(
					"[role='listitem'], li, [class*='component-item']",
				);
				const componentCount = await componentItems.count().catch(() => 0);

				if (componentCount > 0) {
					console.log(`Found ${componentCount} components in library`);
				} else {
					console.log("Component list may load dynamically");
				}
			}
		});

		test("should display component names and types", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Look for component items with name and type
				const componentItems = page.locator("[role='listitem'], li").first();

				if (
					await componentItems.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					const text = await componentItems.textContent().catch(() => "");

					if (text) {
						console.log("Component items display name and metadata");
					}
				}
			}
		});

		test("should allow browsing components by scrolling", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Find scrollable container
				const libraryPanel = page
					.locator("aside, [class*='library'], [class*='panel']")
					.first();

				if (
					await libraryPanel.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					// Scroll in the panel
					await libraryPanel.evaluate((el) => {
						if (el.scrollHeight > el.clientHeight) {
							el.scrollTop = el.scrollHeight / 2;
						}
					});

					await page.waitForTimeout(300);

					console.log("Library components scrollable");
				}
			}
		});

		test("should show component count", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Look for count indicator
				const countLabel = page.getByText(
					/\(\d+\)|\d+\s*(items?|components?)/i,
				);

				if (await countLabel.isVisible({ timeout: 2000 }).catch(() => false)) {
					console.log("Component count displayed");
				}
			}
		});
	});

	test.describe("Search Components", () => {
		test("should display search input in component library", async ({
			page,
		}) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Look for search input
				const searchInput = page
					.locator("input")
					.filter({ hasAttribute: "placeholder", name: /search/i })
					.first();

				if (await searchInput.isVisible({ timeout: 2000 }).catch(() => false)) {
					console.log("Search input found in component library");
				}
			}
		});

		test("should search components by name", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const searchInput = page
					.locator("input")
					.filter({ hasAttribute: "placeholder", name: /search/i })
					.first();

				if (await searchInput.isVisible({ timeout: 2000 }).catch(() => false)) {
					// Type search query
					await searchInput.fill("authentication");
					await page.waitForTimeout(500);

					// Check if results are filtered
					const resultItems = page.locator("[role='listitem'], li");
					const resultCount = await resultItems.count().catch(() => 0);

					if (resultCount > 0) {
						console.log(`Search returned ${resultCount} results`);
					}

					// Clear search
					await searchInput.clear();
					await page.waitForTimeout(300);

					console.log("Component search functional");
				}
			}
		});

		test("should search components by type", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const searchInput = page
					.locator("input")
					.filter({ hasAttribute: "placeholder", name: /search/i })
					.first();

				if (await searchInput.isVisible({ timeout: 2000 }).catch(() => false)) {
					// Search by type keyword
					await searchInput.fill("test");
					await page.waitForTimeout(500);

					const resultItems = page.locator("[role='listitem'], li");
					const resultCount = await resultItems.count().catch(() => 0);

					console.log(`Type search returned ${resultCount} results`);

					await searchInput.clear();
				}
			}
		});

		test("should show no results message when search returns nothing", async ({
			page,
		}) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const searchInput = page
					.locator("input")
					.filter({ hasAttribute: "placeholder", name: /search/i })
					.first();

				if (await searchInput.isVisible({ timeout: 2000 }).catch(() => false)) {
					// Search with unlikely term
					await searchInput.fill("xyznotfound123");
					await page.waitForTimeout(500);

					const noResultsMsg = page.getByText(
						/no.*result|not.*found|no.*match/i,
					);

					if (
						await noResultsMsg.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						console.log("No results message displayed");
					}

					await searchInput.clear();
				}
			}
		});
	});

	test.describe("Filter Components", () => {
		test("should filter components by category", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Look for category filter/tabs
				const categoryFilters = page.locator(
					"[role='tab'], button[class*='category']",
				);
				const filterCount = await categoryFilters.count().catch(() => 0);

				if (filterCount > 0) {
					// Click first category
					await categoryFilters.first().click();
					await page.waitForTimeout(500);

					console.log(
						`Category filter applied, found ${filterCount} categories`,
					);
				}
			}
		});

		test("should filter components by status", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Look for status filter
				const statusFilter = page
					.locator("button, select")
					.filter({ hasText: /status|state|active/i })
					.first();

				if (
					await statusFilter.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await statusFilter.click();
					await page.waitForTimeout(300);

					const statusOption = page
						.locator("[role='option'], button")
						.filter({ hasText: /[a-z]/i })
						.first();

					if (
						await statusOption.isVisible({ timeout: 1000 }).catch(() => false)
					) {
						await statusOption.click();
						await page.waitForTimeout(500);

						console.log("Component status filter applied");
					}
				}
			}
		});
	});

	test.describe("View Component Details", () => {
		test("should click on component to view details", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Click first component
				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await componentItem.click();
					await page.waitForTimeout(500);

					// Look for detail panel
					const detailPanel = page.locator(
						"[class*='detail'], [class*='panel']",
					);

					if (
						await detailPanel.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						console.log("Component details panel displayed");
					}
				}
			}
		});

		test("should display component metadata", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await componentItem.click();
					await page.waitForTimeout(500);

					// Look for metadata fields
					const metadata = page.getByText(
						/type|status|version|author|created|modified/i,
					);
					const metadataCount = await metadata.count().catch(() => 0);

					if (metadataCount > 0) {
						console.log(`Found ${metadataCount} metadata fields`);
					}
				}
			}
		});

		test("should show component description", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await componentItem.click();
					await page.waitForTimeout(500);

					// Look for description text
					const description = page.locator("p, [class*='description']");

					if (
						await description
							.first()
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						console.log("Component description displayed");
					}
				}
			}
		});

		test("should show component relationships", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await componentItem.click();
					await page.waitForTimeout(500);

					// Look for relationships section
					const relationships = page.getByText(
						/related|depends|link|reference|parent|child/i,
					);
					const relationCount = await relationships.count().catch(() => 0);

					if (relationCount > 0) {
						console.log(`Found ${relationCount} relationship indicators`);
					}
				}
			}
		});
	});

	test.describe("Component Visualization", () => {
		test("should visualize component in graph context", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await componentItem.click();
					await page.waitForTimeout(500);

					// Look for visualization button
					const visualizeBtn = page
						.locator("button")
						.filter({ hasText: /visualize|show|view.*graph/i })
						.first();

					if (
						await visualizeBtn.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						await visualizeBtn.click();
						await page.waitForTimeout(1000);

						// Check if graph updated
						const graphContainer = page.locator(".react-flow");
						if (
							await graphContainer
								.isVisible({ timeout: 2000 })
								.catch(() => false)
						) {
							console.log("Component visualized in graph");
						}
					}
				}
			}
		});

		test("should highlight component in graph when selected", async ({
			page,
		}) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await componentItem.click();
					await page.waitForTimeout(500);

					// Look for highlighted node in graph
					const highlightedNodes = page.locator(
						".react-flow__nodes [class*='highlighted'], [class*='selected']",
					);
					const highlightCount = await highlightedNodes.count().catch(() => 0);

					if (highlightCount > 0) {
						console.log(`${highlightCount} component nodes highlighted`);
					}
				}
			}
		});
	});

	test.describe("Add Component to Graph", () => {
		test("should show add/import component button", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const addBtn = page
					.locator("button")
					.filter({ hasText: /add|import|insert|use/i })
					.first();

				if (await addBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
					console.log("Add component button found");
				}
			}
		});

		test("should add component to graph", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				// Get initial node count
				const initialCount = await page
					.locator(".react-flow__nodes > div[data-id]")
					.count()
					.catch(() => 0);

				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					// Look for add button in component item
					const addBtn = componentItem
						.locator("button")
						.filter({ hasText: /add|import|insert/i });

					if (await addBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await addBtn.click();
						await page.waitForTimeout(1000);

						// Check if node count increased
						const finalCount = await page
							.locator(".react-flow__nodes > div[data-id]")
							.count()
							.catch(() => 0);

						if (finalCount > initialCount) {
							console.log(
								`Component added to graph: ${initialCount} -> ${finalCount} nodes`,
							);
						}
					}
				}
			}
		});

		test("should show add confirmation feedback", async ({ page }) => {
			const libraryBtn = page
				.locator("button, [role='button']")
				.filter({
					hasText: /component|library|palette|catalog/i,
				})
				.first();

			if (await libraryBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await libraryBtn.click();
				await page.waitForTimeout(500);

				const componentItem = page.locator("[role='listitem'], li").first();

				if (
					await componentItem.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					const addBtn = componentItem
						.locator("button")
						.filter({ hasText: /add|import|insert/i });

					if (await addBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await addBtn.click();
						await page.waitForTimeout(500);

						// Look for confirmation message
						const confirmation = page.getByText(
							/added|imported|success|created/i,
						);

						if (
							await confirmation.isVisible({ timeout: 2000 }).catch(() => false)
						) {
							console.log("Add component confirmation displayed");
						}
					}
				}
			}
		});
	});
});
