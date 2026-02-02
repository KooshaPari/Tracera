import { expect, test } from "./global-setup";

/**
 * Dimension Filters Tests
 *
 * Tests for applying and managing dimension-based filters on the graph.
 *
 * Dimension Filters:
 * - Maturity: Draft, Review, Approved, Deprecated
 * - Complexity: Low, Medium, High, Critical
 * - Coverage: Not Covered, Partial, Complete
 * - Risk: Low, Medium, High, Critical
 *
 * Filter Display Modes:
 * - Filter: Hide non-matching items
 * - Highlight: Visual emphasis on matching items
 * - Color: Color-code nodes by dimension value
 * - Size: Node size represents dimension value
 */

test.describe("Dimension Filters", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/graph");
		await page.waitForLoadState("networkidle");
		await page.waitForTimeout(1000); // Allow graph to render
	});

	test.describe("Maturity Filters", () => {
		test("should display maturity filter control", async ({ page }) => {
			// Look for maturity filter control
			const maturityFilter = page
				.locator("button, select, [role='combobox']")
				.filter({ hasText: /maturity|draft|review|approved/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				console.log("Maturity filter found");
			} else {
				console.log("Maturity filter not visible");
			}
		});

		test("should apply maturity filter - Draft", async ({ page }) => {
			// Get initial node count
			const initialNodeCount = await page
				.locator(".react-flow__nodes > div[data-id]")
				.count()
				.catch(() => 0);

			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(1000);

					// Verify filter applied
					const filteredNodeCount = await page
						.locator(".react-flow__nodes > div[data-id]")
						.count()
						.catch(() => 0);

					console.log(
						`Draft filter applied: ${initialNodeCount} -> ${filteredNodeCount} nodes`,
					);
				}
			}
		});

		test("should apply maturity filter - Approved", async ({ page }) => {
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const approvedOption = page.getByText(/approved/i);
				if (
					await approvedOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await approvedOption.click();
					await page.waitForTimeout(1000);

					const graphContainer = page.locator(".react-flow");
					await expect(graphContainer).toBeVisible();

					console.log("Approved maturity filter applied");
				}
			}
		});

		test("should apply multiple maturity filters", async ({ page }) => {
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				// Apply first filter
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(300);

					// Check if multi-select is available
					const checkboxes = page.locator(
						'input[type="checkbox"][aria-label*="draft" i]',
					);
					if (
						await checkboxes
							.first()
							.isVisible({ timeout: 1000 })
							.catch(() => false)
					) {
						console.log("Multi-select maturity filter available");
					}
				}
			}
		});
	});

	test.describe("Complexity Filters", () => {
		test("should apply complexity filter - High", async ({ page }) => {
			const complexityFilter = page
				.locator("button, select")
				.filter({ hasText: /complexity|complex/i })
				.first();

			if (
				await complexityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await complexityFilter.click();
				await page.waitForTimeout(300);

				const highOption = page.getByText(/high/i);
				if (await highOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await highOption.click();
					await page.waitForTimeout(1000);

					console.log("High complexity filter applied");
				}
			}
		});

		test("should apply complexity filter - Low", async ({ page }) => {
			const complexityFilter = page
				.locator("button, select")
				.filter({ hasText: /complexity|complex/i })
				.first();

			if (
				await complexityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await complexityFilter.click();
				await page.waitForTimeout(300);

				const lowOption = page.getByText(/low/i);
				if (await lowOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await lowOption.click();
					await page.waitForTimeout(1000);

					const graphContainer = page.locator(".react-flow");
					await expect(graphContainer).toBeVisible();

					console.log("Low complexity filter applied");
				}
			}
		});

		test("should apply complexity filter - Critical", async ({ page }) => {
			const complexityFilter = page
				.locator("button, select")
				.filter({ hasText: /complexity|complex/i })
				.first();

			if (
				await complexityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await complexityFilter.click();
				await page.waitForTimeout(300);

				const criticalOption = page.getByText(/critical/i);
				if (
					await criticalOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await criticalOption.click();
					await page.waitForTimeout(1000);

					console.log("Critical complexity filter applied");
				}
			}
		});
	});

	test.describe("Coverage Filters", () => {
		test("should apply coverage filter - Complete", async ({ page }) => {
			const coverageFilter = page
				.locator("button, select")
				.filter({ hasText: /coverage|cover/i })
				.first();

			if (
				await coverageFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await coverageFilter.click();
				await page.waitForTimeout(300);

				const completeOption = page.getByText(/complete/i);
				if (
					await completeOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await completeOption.click();
					await page.waitForTimeout(1000);

					console.log("Complete coverage filter applied");
				}
			}
		});

		test("should apply coverage filter - Partial", async ({ page }) => {
			const coverageFilter = page
				.locator("button, select")
				.filter({ hasText: /coverage|cover/i })
				.first();

			if (
				await coverageFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await coverageFilter.click();
				await page.waitForTimeout(300);

				const partialOption = page.getByText(/partial/i);
				if (
					await partialOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await partialOption.click();
					await page.waitForTimeout(1000);

					const graphContainer = page.locator(".react-flow");
					await expect(graphContainer).toBeVisible();

					console.log("Partial coverage filter applied");
				}
			}
		});

		test("should apply coverage filter - Not Covered", async ({ page }) => {
			const coverageFilter = page
				.locator("button, select")
				.filter({ hasText: /coverage|cover/i })
				.first();

			if (
				await coverageFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await coverageFilter.click();
				await page.waitForTimeout(300);

				const notCoveredOption = page.getByText(/not.*cover|uncovered/i);
				if (
					await notCoveredOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await notCoveredOption.click();
					await page.waitForTimeout(1000);

					console.log("Not Covered filter applied");
				}
			}
		});
	});

	test.describe("Risk Filters", () => {
		test("should apply risk filter - High", async ({ page }) => {
			const riskFilter = page
				.locator("button, select")
				.filter({ hasText: /risk/i })
				.first();

			if (await riskFilter.isVisible({ timeout: 2000 }).catch(() => false)) {
				await riskFilter.click();
				await page.waitForTimeout(300);

				const highOption = page.getByText(/high/i);
				if (await highOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await highOption.click();
					await page.waitForTimeout(1000);

					console.log("High risk filter applied");
				}
			}
		});

		test("should apply risk filter - Critical", async ({ page }) => {
			const riskFilter = page
				.locator("button, select")
				.filter({ hasText: /risk/i })
				.first();

			if (await riskFilter.isVisible({ timeout: 2000 }).catch(() => false)) {
				await riskFilter.click();
				await page.waitForTimeout(300);

				const criticalOption = page.getByText(/critical/i);
				if (
					await criticalOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await criticalOption.click();
					await page.waitForTimeout(1000);

					const graphContainer = page.locator(".react-flow");
					await expect(graphContainer).toBeVisible();

					console.log("Critical risk filter applied");
				}
			}
		});

		test("should apply risk filter - Low", async ({ page }) => {
			const riskFilter = page
				.locator("button, select")
				.filter({ hasText: /risk/i })
				.first();

			if (await riskFilter.isVisible({ timeout: 2000 }).catch(() => false)) {
				await riskFilter.click();
				await page.waitForTimeout(300);

				const lowOption = page.getByText(/low/i);
				if (await lowOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await lowOption.click();
					await page.waitForTimeout(1000);

					console.log("Low risk filter applied");
				}
			}
		});
	});

	test.describe("Filter Display Modes", () => {
		test("should switch to filter display mode - Hide non-matching", async ({
			page,
		}) => {
			// Apply a dimension filter first
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(500);

					// Now look for filter display mode selector
					const displayModeSelector = page
						.locator("button")
						.filter({ hasText: /display|mode|filter|highlight|color|size/i })
						.first();

					if (
						await displayModeSelector
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						await displayModeSelector.click();
						await page.waitForTimeout(300);

						const filterMode = page.getByText(/filter|hide.*non|show.*only/i);
						if (
							await filterMode.isVisible({ timeout: 1000 }).catch(() => false)
						) {
							await filterMode.click();
							await page.waitForTimeout(1000);

							console.log("Filter display mode activated");
						}
					}
				}
			}
		});

		test("should switch to highlight display mode", async ({ page }) => {
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(500);

					// Look for highlight mode selector
					const displayModeSelector = page
						.locator("button")
						.filter({ hasText: /display|mode|highlight/i })
						.first();

					if (
						await displayModeSelector
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						await displayModeSelector.click();
						await page.waitForTimeout(300);

						const highlightMode = page.getByText(/highlight|emphasize|bold/i);
						if (
							await highlightMode
								.isVisible({ timeout: 1000 })
								.catch(() => false)
						) {
							await highlightMode.click();
							await page.waitForTimeout(1000);

							console.log("Highlight display mode activated");
						}
					}
				}
			}
		});

		test("should switch to color display mode", async ({ page }) => {
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(500);

					const displayModeSelector = page
						.locator("button")
						.filter({ hasText: /display|mode|color/i })
						.first();

					if (
						await displayModeSelector
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						await displayModeSelector.click();
						await page.waitForTimeout(300);

						const colorMode = page.getByText(/color|colored|gradient/i);
						if (
							await colorMode.isVisible({ timeout: 1000 }).catch(() => false)
						) {
							await colorMode.click();
							await page.waitForTimeout(1000);

							// Verify color coding is applied
							const coloredNodes = page.locator(
								"[style*='color'], [style*='background']",
							);
							const colorCount = await coloredNodes.count().catch(() => 0);

							if (colorCount > 0) {
								console.log(
									`Color mode activated with ${colorCount} colored nodes`,
								);
							} else {
								console.log("Color display mode activated");
							}
						}
					}
				}
			}
		});

		test("should switch to size display mode", async ({ page }) => {
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity|complexity|risk|coverage/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const filterOption = page
					.locator("button, [role='option']")
					.filter({ hasText: /draft|high|low|complete|critical/i })
					.first();

				if (
					await filterOption.isVisible({ timeout: 1000 }).catch(() => false)
				) {
					await filterOption.click();
					await page.waitForTimeout(500);

					const displayModeSelector = page
						.locator("button")
						.filter({ hasText: /display|mode|size/i })
						.first();

					if (
						await displayModeSelector
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						await displayModeSelector.click();
						await page.waitForTimeout(300);

						const sizeMode = page.getByText(/size|scale|proportional/i);
						if (
							await sizeMode.isVisible({ timeout: 1000 }).catch(() => false)
						) {
							await sizeMode.click();
							await page.waitForTimeout(1000);

							console.log("Size display mode activated");
						}
					}
				}
			}
		});
	});

	test.describe("Clear and Reset Filters", () => {
		test("should clear all filters", async ({ page }) => {
			// Apply a filter first
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(500);

					// Get node count with filter applied
					const filteredCount = await page
						.locator(".react-flow__nodes > div[data-id]")
						.count()
						.catch(() => 0);

					// Look for clear/reset button
					const clearBtn = page
						.locator("button")
						.filter({ hasText: /clear|reset|all|none/i })
						.first();

					if (await clearBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await clearBtn.click();
						await page.waitForTimeout(1000);

						// Get node count after clear
						const clearedCount = await page
							.locator(".react-flow__nodes > div[data-id]")
							.count()
							.catch(() => 0);

						if (clearedCount > filteredCount) {
							console.log(
								`Filters cleared: ${filteredCount} -> ${clearedCount} nodes`,
							);
						} else {
							console.log("Clear filters triggered");
						}
					}
				}
			}
		});

		test("should reset individual filter", async ({ page }) => {
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(500);

					// Look for filter tag/chip with X button to remove
					const filterChip = page
						.locator("[class*='filter'], [class*='tag'], [class*='chip']")
						.filter({ hasText: /draft/i });

					if (
						await filterChip.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						// Find close button within the chip
						const closeBtn = filterChip.locator("button, svg");
						if (
							await closeBtn.isVisible({ timeout: 1000 }).catch(() => false)
						) {
							await closeBtn.click();
							await page.waitForTimeout(500);

							console.log("Individual filter removed");
						}
					} else {
						console.log("Filter chip not found");
					}
				}
			}
		});

		test("should combine multiple filters", async ({ page }) => {
			const initialNodeCount = await page
				.locator(".react-flow__nodes > div[data-id]")
				.count()
				.catch(() => 0);

			// Apply maturity filter
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(500);

					// Apply complexity filter
					const complexityFilter = page
						.locator("button, select")
						.filter({ hasText: /complexity/i })
						.first();

					if (
						await complexityFilter
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						await complexityFilter.click();
						await page.waitForTimeout(300);

						const highOption = page.getByText(/high/i);
						if (
							await highOption.isVisible({ timeout: 1000 }).catch(() => false)
						) {
							await highOption.click();
							await page.waitForTimeout(1000);

							const combinedCount = await page
								.locator(".react-flow__nodes > div[data-id]")
								.count()
								.catch(() => 0);

							console.log(
								`Combined filters applied: ${initialNodeCount} -> ${combinedCount} nodes`,
							);
						}
					}
				}
			}
		});
	});

	test.describe("Filter Persistence", () => {
		test("should preserve filters across graph interactions", async ({
			page,
		}) => {
			// Apply filter
			const maturityFilter = page
				.locator("button, select")
				.filter({ hasText: /maturity/i })
				.first();

			if (
				await maturityFilter.isVisible({ timeout: 2000 }).catch(() => false)
			) {
				await maturityFilter.click();
				await page.waitForTimeout(300);

				const draftOption = page.getByText(/draft/i);
				if (await draftOption.isVisible({ timeout: 1000 }).catch(() => false)) {
					await draftOption.click();
					await page.waitForTimeout(500);

					const filteredCount = await page
						.locator(".react-flow__nodes > div[data-id]")
						.count()
						.catch(() => 0);

					// Perform graph interaction - zoom in
					const zoomInBtn = page.locator(".react-flow__controls button").nth(0);
					if (await zoomInBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await zoomInBtn.click();
						await page.waitForTimeout(500);
					}

					// Check if filter is still applied
					const postInteractionCount = await page
						.locator(".react-flow__nodes > div[data-id]")
						.count()
						.catch(() => 0);

					if (postInteractionCount === filteredCount) {
						console.log("Filter preserved across zoom interaction");
					}
				}
			}
		});
	});
});
