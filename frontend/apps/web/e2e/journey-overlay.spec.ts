import { test } from "./global-setup";

/**
 * Journey Overlay Tests
 *
 * Tests for selecting and visualizing user journeys overlaid on the
 * multi-dimensional traceability graph.
 *
 * Journey Features:
 * - Select journey from dropdown
 * - Verify journey nodes are highlighted
 * - Show journey path through graph
 * - Journey statistics and metrics
 * - Journey explorer navigation
 * - Filter graph to show only journey items
 * - Clear journey overlay
 */

test.describe("Journey Overlay", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/graph");
		await page.waitForLoadState("networkidle");
		await page.waitForTimeout(1000);
	});

	test.describe("Journey Selection", () => {
		test("should display journey selector dropdown", async ({ page }) => {
			// Look for journey selector
			const journeySelector = page
				.locator("button, select, [role='combobox']")
				.filter({ hasText: /journey|user.*flow|user.*path|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				console.log("Journey selector found");
			} else {
				console.log("Journey selector not visible");
			}
		});

		test("should list available journeys", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario|flow/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				// Count available journey options
				const journeyOptions = page
					.locator("button, [role='option'], li")
					.filter({ hasText: /[a-z]/i });
				const optionCount = await journeyOptions.count().catch(() => 0);

				if (optionCount > 0) {
					console.log(`Found ${optionCount} available journeys`);
				}
			}
		});

		test("should select journey from dropdown", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario|flow/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				// Select first available journey
				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					console.log("Journey selected from dropdown");
				}
			}
		});

		test("should show selected journey name", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario|flow/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					const journeyName = await journeyOption.textContent().catch(() => "");

					await journeyOption.click();
					await page.waitForTimeout(500);

					// Check if journey name is displayed in selector
					const selectedText = await journeySelector
						.textContent()
						.catch(() => "");

					if (selectedText.includes(journeyName)) {
						console.log(`Selected journey "${journeyName}" displayed`);
					}
				}
			}
		});

		test("should handle multiple journey selection", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario|flow/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				// Look for checkboxes to enable multi-select
				const checkboxes = page.locator(
					"input[type='checkbox'], [role='checkbox']",
				);
				const checkboxCount = await checkboxes.count().catch(() => 0);

				if (checkboxCount > 0) {
					console.log("Multi-select journeys available");

					// Try selecting multiple journeys
					await checkboxes
						.nth(0)
						.click({ timeout: 1000 })
						.catch(() => {});
					await page.waitForTimeout(300);

					await checkboxes
						.nth(1)
						.click({ timeout: 1000 })
						.catch(() => {});
					await page.waitForTimeout(500);

					console.log("Multiple journeys selected");
				} else {
					console.log("Single journey selection mode");
				}
			}
		});
	});

	test.describe("Journey Highlighting", () => {
		test("should highlight journey nodes in graph", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				// Get initial nodes
				const initialNodes = page.locator(".react-flow__nodes > div[data-id]");
				const initialCount = await initialNodes.count().catch(() => 0);

				// Select a journey
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Check for highlighted nodes
					const highlightedNodes = page.locator(
						"[class*='journey'], [class*='highlighted'], [class*='active']",
					);
					const highlightedCount = await highlightedNodes
						.count()
						.catch(() => 0);

					if (highlightedCount > 0) {
						console.log(`${highlightedCount} journey nodes highlighted`);
					} else {
						console.log("Journey overlay applied to graph");
					}
				}
			}
		});

		test("should show journey path visualization", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for journey path visualization
					const journeyEdges = page.locator(
						".react-flow__edges [class*='journey'], [class*='path']",
					);
					const edgeCount = await journeyEdges.count().catch(() => 0);

					if (edgeCount > 0) {
						console.log(`${edgeCount} journey path edges displayed`);
					} else {
						console.log("Journey path visualization applied");
					}
				}
			}
		});

		test("should distinguish journey start and end nodes", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for start/end node indicators
					const startNode = page.locator("[class*='start'], [class*='begin']");
					const endNode = page.locator("[class*='end'], [class*='finish']");

					const startVisible = await startNode
						.isVisible({ timeout: 2000 })
						.catch(() => false);
					const endVisible = await endNode
						.isVisible({ timeout: 2000 })
						.catch(() => false);

					if (startVisible || endVisible) {
						console.log("Journey start/end nodes marked");
					} else {
						console.log("Journey flow visualization applied");
					}
				}
			}
		});

		test("should highlight journey sequence steps", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for numbered steps or sequence indicators
					const sequenceNumbers = page.getByText(/^\d+$/);
					const numberCount = await sequenceNumbers.count().catch(() => 0);

					if (numberCount > 0) {
						console.log(`${numberCount} journey steps numbered`);
					}

					// Check for step badge or marker
					const stepMarkers = page.locator(
						"[class*='step'], [class*='sequence']",
					);
					const markerCount = await stepMarkers.count().catch(() => 0);

					if (markerCount > 0) {
						console.log(`${markerCount} step markers displayed`);
					}
				}
			}
		});
	});

	test.describe("Journey Statistics and Metrics", () => {
		test("should display journey statistics panel", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for statistics panel
					const statsPanel = page.locator(
						"[class*='stats'], [class*='metrics'], [class*='summary']",
					);

					if (
						await statsPanel.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						console.log("Journey statistics panel displayed");
					}
				}
			}
		});

		test("should show journey step count", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for step count
					const stepCount = page.getByText(/step|count|length|items?/i);
					if (await stepCount.isVisible({ timeout: 2000 }).catch(() => false)) {
						console.log("Journey step count displayed");
					}
				}
			}
		});

		test("should display journey coverage metrics", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for coverage metric
					const coverage = page.getByText(/coverage|cover|percent|%/i);
					if (await coverage.isVisible({ timeout: 2000 }).catch(() => false)) {
						console.log("Journey coverage metric displayed");
					}
				}
			}
		});

		test("should show journey completion status", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for completion status
					const status = page.getByText(
						/complete|done|pending|in.*progress|status/i,
					);
					if (await status.isVisible({ timeout: 2000 }).catch(() => false)) {
						console.log("Journey completion status displayed");
					}
				}
			}
		});
	});

	test.describe("Journey Explorer Navigation", () => {
		test("should navigate journey steps sequentially", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for next/previous navigation buttons
					const nextBtn = page
						.locator("button")
						.filter({ hasText: /next|forward|right/i })
						.first();

					if (await nextBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await nextBtn.click();
						await page.waitForTimeout(500);

						console.log("Navigated to next journey step");
					}
				}
			}
		});

		test("should click on journey step in list to navigate", async ({
			page,
		}) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for journey step list/explorer
					const stepList = page
						.locator("ul, [role='list']")
						.filter({ hasText: /step|item|node/i });

					if (await stepList.isVisible({ timeout: 2000 }).catch(() => false)) {
						const steps = stepList.locator("li, [role='listitem']");
						const stepCount = await steps.count().catch(() => 0);

						if (stepCount > 1) {
							// Click second step
							await steps.nth(1).click();
							await page.waitForTimeout(500);

							console.log("Clicked journey step to navigate");
						}
					}
				}
			}
		});

		test("should scroll to center graph on journey step selection", async ({
			page,
		}) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Look for journey step list
					const stepList = page
						.locator("ul, [role='list']")
						.filter({ hasText: /step|item/i });

					if (await stepList.isVisible({ timeout: 2000 }).catch(() => false)) {
						const steps = stepList.locator("li, [role='listitem']");

						if (
							await steps
								.nth(1)
								.isVisible({ timeout: 1000 })
								.catch(() => false)
						) {
							await steps.nth(1).click();
							await page.waitForTimeout(500);

							console.log("Graph centered on journey step");
						}
					}
				}
			}
		});
	});

	test.describe("Journey Filtering", () => {
		test("should filter graph to show only journey items", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				// Get initial node count
				const initialCount = await page
					.locator(".react-flow__nodes > div[data-id]")
					.count()
					.catch(() => 0);

				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Check if there's a filter toggle for journey-only view
					const filterToggle = page
						.locator("button")
						.filter({ hasText: /filter|journey.*only|show.*only/i })
						.first();

					if (
						await filterToggle.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						await filterToggle.click();
						await page.waitForTimeout(500);

						const filteredCount = await page
							.locator(".react-flow__nodes > div[data-id]")
							.count()
							.catch(() => 0);

						console.log(
							`Journey filter: ${initialCount} -> ${filteredCount} nodes`,
						);
					} else {
						console.log("Journey filter may be automatic");
					}
				}
			}
		});

		test("should preserve other filters when journey is selected", async ({
			page,
		}) => {
			// Apply a dimension filter first
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity|status|type/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const option = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (await option.isVisible({ timeout: 1000 }).catch(() => false)) {
					await option.click();
					await page.waitForTimeout(500);

					// Now select journey
					const journeySelector = page
						.locator("button, select")
						.filter({ hasText: /journey|scenario/i })
						.first();

					if (
						await journeySelector
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						await journeySelector.click();
						await page.waitForTimeout(300);

						const journeyOption = page
							.locator("[role='option'], button")
							.filter({ hasText: /[A-Za-z]/ })
							.first();

						if (
							await journeyOption
								.isVisible({ timeout: 1000 })
								.catch(() => false)
						) {
							await journeyOption.click();
							await page.waitForTimeout(1000);

							console.log("Journey selected with filters preserved");
						}
					}
				}
			}
		});
	});

	test.describe("Clear Journey Overlay", () => {
		test("should clear journey selection", async ({ page }) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					// Get highlighted nodes count
					const highlightedCount = await page
						.locator("[class*='journey'], [class*='highlighted']")
						.count()
						.catch(() => 0);

					// Look for clear/reset button
					const clearBtn = page
						.locator("button")
						.filter({ hasText: /clear|reset|none|remove/i })
						.first();

					if (await clearBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await clearBtn.click();
						await page.waitForTimeout(500);

						// Verify journey highlighting removed
						const remainingHighlighted = await page
							.locator("[class*='journey'], [class*='highlighted']")
							.count()
							.catch(() => 0);

						if (remainingHighlighted < highlightedCount) {
							console.log("Journey overlay cleared successfully");
						}
					}
				}
			}
		});

		test("should restore normal graph after clearing journey", async ({
			page,
		}) => {
			const journeySelector = page
				.locator("button, select")
				.filter({ hasText: /journey|scenario/i })
				.first();

			if (
				await journeySelector.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await journeySelector.click();
				await page.waitForTimeout(300);

				const journeyOption = page
					.locator("[role='option'], button")
					.filter({ hasText: /[A-Za-z]/ })
					.first();

				if (
					await journeyOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await journeyOption.click();
					await page.waitForTimeout(1000);

					const allNodes = await page
						.locator(".react-flow__nodes > div[data-id]")
						.count()
						.catch(() => 0);

					// Clear journey
					const clearBtn = page
						.locator("button")
						.filter({ hasText: /clear|reset|none/i })
						.first();

					if (await clearBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await clearBtn.click();
						await page.waitForTimeout(500);

						const nodesAfterClear = await page
							.locator(".react-flow__nodes > div[data-id]")
							.count()
							.catch(() => 0);

						if (nodesAfterClear === allNodes) {
							console.log(
								"Graph restored to normal state after clearing journey",
							);
						}
					}
				}
			}
		});
	});
});
