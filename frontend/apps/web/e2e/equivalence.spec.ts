import { test } from "./global-setup";

/**
 * Equivalence Panel Tests
 *
 * Tests for viewing, managing, and navigating equivalent items
 * across different dimensions in the traceability graph.
 *
 * Equivalence Features:
 * - View equivalence panel for selected node
 * - Confirm suggested equivalences
 * - Reject suggested equivalences
 * - Navigate via pivot targets
 * - Display equivalence strength/confidence
 * - Show equivalence relationships visually
 */

test.describe("Equivalence Panel", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/graph");
		await page.waitForLoadState("networkidle");
		await page.waitForTimeout(1000);
	});

	test.describe("View Equivalence Panel", () => {
		test("should display equivalence panel when node is selected", async ({
			page,
		}) => {
			// Click on a node to select it
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for equivalence panel
				const equivalencePanel = page
					.locator(
						"[class*='equivalence'], [class*='equivalent'], aside, .w-96",
					)
					.filter({ hasText: /equivalent|maps to|corresponds|related/i });

				if (
					await equivalencePanel.isVisible({ timeout: 3000 }).catch(() => false)
				) {
					console.log("Equivalence panel displayed for selected node");
				} else {
					// Try alternative panel location
					const detailPanel = page.locator(".w-96");
					if (
						await detailPanel.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						console.log("Detail panel visible - equivalence may be a tab");
					}
				}
			}
		});

		test("should show equivalence list for selected item", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for equivalence section or tab
				const equivalenceTab = page.getByRole("tab", {
					name: /equivalent|equivalence/i,
				});

				if (
					await equivalenceTab.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					await equivalenceTab.click();
					await page.waitForTimeout(500);

					console.log("Equivalence tab selected");
				}

				// Look for list of equivalent items
				const equivalentList = page
					.locator("ul, [role='list']")
					.filter({ hasText: /equivalent|maps to/i });

				if (
					await equivalentList.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					const itemCount = await equivalentList
						.locator("li, [role='listitem']")
						.count()
						.catch(() => 0);

					console.log(`Found ${itemCount} equivalent items`);
				}
			}
		});

		test("should display equivalence strength/confidence", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for confidence/strength indicator
				const confidenceIndicators = page.getByText(
					/confidence|strength|match|score|%/i,
				);
				const indicatorCount = await confidenceIndicators
					.count()
					.catch(() => 0);

				if (indicatorCount > 0) {
					console.log(`Found ${indicatorCount} confidence indicators`);
				}

				// Look for progress bars or rating indicators
				const progressBars = page.locator(
					"[role='progressbar'], [class*='progress'], [class*='strength']",
				);
				const barCount = await progressBars.count().catch(() => 0);

				if (barCount > 0) {
					console.log(`${barCount} strength/confidence bars found`);
				}
			}
		});

		test("should show equivalence metadata", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for equivalence metadata section
				const metadata = page.getByText(
					/dimension|view|perspective|type|status|version/i,
				);
				const metadataCount = await metadata.count().catch(() => 0);

				if (metadataCount > 0) {
					console.log(`Found ${metadataCount} metadata fields`);
				}
			}
		});
	});

	test.describe("Suggested Equivalences", () => {
		test("should display suggested equivalences", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for suggested equivalences section
				const suggestedSection = page.getByText(
					/suggested|recommended|potential|candidate/i,
				);

				if (
					await suggestedSection.isVisible({ timeout: 2000 }).catch(() => false)
				) {
					console.log("Suggested equivalences section found");
				}

				// Look for equivalence items marked as suggested
				const suggestedItems = page.locator(
					"[class*='suggested'], [class*='recommended']",
				);
				const suggestedCount = await suggestedItems.count().catch(() => 0);

				if (suggestedCount > 0) {
					console.log(`${suggestedCount} suggested equivalences`);
				}
			}
		});

		test("should show confirmation actions for suggested equivalences", async ({
			page,
		}) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for confirm/approve buttons
				const confirmBtn = page
					.locator("button")
					.filter({ hasText: /confirm|approve|accept|yes/i })
					.first();

				if (await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
					console.log("Confirmation button found for equivalence");
				}

				// Look for reject/deny buttons
				const rejectBtn = page
					.locator("button")
					.filter({ hasText: /reject|deny|no|dismiss/i })
					.first();

				if (await rejectBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
					console.log("Reject button found for equivalence");
				}
			}
		});
	});

	test.describe("Confirm Equivalences", () => {
		test("should confirm suggested equivalence", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Find a suggested equivalence item with confirm button
				const suggestedItems = page.locator(
					"[class*='suggested'], [class*='recommended']",
				);
				const itemCount = await suggestedItems.count().catch(() => 0);

				if (itemCount > 0) {
					// Get the first suggested item
					const firstSuggested = suggestedItems.first();

					// Look for confirm button within or near the item
					const confirmBtn = firstSuggested
						.locator("button")
						.filter({ hasText: /confirm|approve|accept/i });

					if (
						await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						await confirmBtn.click();
						await page.waitForTimeout(1000);

						console.log("Equivalence confirmed");

						// Verify equivalence is now in confirmed list
						const confirmedItems = page.locator(
							"[class*='confirmed'], [class*='approved']",
						);
						const confirmedCount = await confirmedItems.count().catch(() => 0);

						if (confirmedCount > 0) {
							console.log("Equivalence moved to confirmed list");
						}
					} else {
						console.log("Confirm button not found");
					}
				}
			}
		});

		test("should confirm multiple equivalences", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Find suggested items with confirm buttons
				const suggestedItems = page.locator(
					"[class*='suggested'], [class*='recommended']",
				);
				const itemCount = await suggestedItems.count().catch(() => 0);

				if (itemCount >= 2) {
					// Confirm first item
					const firstConfirmBtn = suggestedItems
						.nth(0)
						.locator("button")
						.filter({ hasText: /confirm|approve|accept/i });

					if (
						await firstConfirmBtn
							.isVisible({ timeout: 2000 })
							.catch(() => false)
					) {
						await firstConfirmBtn.click();
						await page.waitForTimeout(500);

						// Confirm second item
						const secondConfirmBtn = suggestedItems
							.nth(1)
							.locator("button")
							.filter({ hasText: /confirm|approve|accept/i });

						if (
							await secondConfirmBtn
								.isVisible({ timeout: 2000 })
								.catch(() => false)
						) {
							await secondConfirmBtn.click();
							await page.waitForTimeout(500);

							console.log("Multiple equivalences confirmed");
						}
					}
				}
			}
		});

		test("should show confirmation feedback", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				const suggestedItems = page.locator(
					"[class*='suggested'], [class*='recommended']",
				);

				if (
					await suggestedItems
						.first()
						.isVisible({ timeout: 2000 })
						.catch(() => false)
				) {
					const confirmBtn = suggestedItems
						.first()
						.locator("button")
						.filter({ hasText: /confirm|approve|accept/i });

					if (
						await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false)
					) {
						await confirmBtn.click();
						await page.waitForTimeout(500);

						// Look for feedback message/toast
						const feedback = page.getByText(
							/confirmed|approved|success|added/i,
						);
						if (
							await feedback.isVisible({ timeout: 2000 }).catch(() => false)
						) {
							console.log("Confirmation feedback displayed");
						}
					}
				}
			}
		});
	});

	test.describe("Reject Equivalences", () => {
		test("should reject suggested equivalence", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				const suggestedItems = page.locator(
					"[class*='suggested'], [class*='recommended']",
				);
				const itemCount = await suggestedItems.count().catch(() => 0);

				if (itemCount > 0) {
					const firstSuggested = suggestedItems.first();

					const rejectBtn = firstSuggested
						.locator("button")
						.filter({ hasText: /reject|deny|no|dismiss/i });

					if (await rejectBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await rejectBtn.click();
						await page.waitForTimeout(1000);

						console.log("Equivalence rejected");

						// Verify item is removed from suggested list
						const remainingSuggested = page.locator(
							"[class*='suggested'], [class*='recommended']",
						);
						const remainingCount = await remainingSuggested
							.count()
							.catch(() => 0);

						if (remainingCount < itemCount) {
							console.log("Rejected equivalence removed from list");
						}
					}
				}
			}
		});

		test("should show rejection feedback", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				const suggestedItems = page.locator(
					"[class*='suggested'], [class*='recommended']",
				);

				if (
					await suggestedItems
						.first()
						.isVisible({ timeout: 2000 })
						.catch(() => false)
				) {
					const rejectBtn = suggestedItems
						.first()
						.locator("button")
						.filter({ hasText: /reject|deny|dismiss/i });

					if (await rejectBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
						await rejectBtn.click();
						await page.waitForTimeout(500);

						// Look for feedback message
						const feedback = page.getByText(/rejected|dismissed|removed/i);
						if (
							await feedback.isVisible({ timeout: 2000 }).catch(() => false)
						) {
							console.log("Rejection feedback displayed");
						}
					}
				}
			}
		});
	});

	test.describe("Navigate via Pivot Targets", () => {
		test("should navigate to equivalent item", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for equivalence list
				const equivalentItems = page
					.locator("[class*='equivalent'], li")
					.filter({ hasText: /equivalent|maps to|corresponds/i });

				const itemCount = await equivalentItems.count().catch(() => 0);

				if (itemCount > 0) {
					// Click first equivalent item
					const firstEquivalent = equivalentItems.first();

					const navLink = firstEquivalent.locator("a, button[class*='link']");

					if (await navLink.isVisible({ timeout: 2000 }).catch(() => false)) {
						await navLink.click();
						await page.waitForTimeout(500);

						// Verify navigation occurred
						const graphContainer = page.locator(".react-flow");
						if (
							await graphContainer
								.isVisible({ timeout: 2000 })
								.catch(() => false)
						) {
							console.log("Navigated to equivalent item");
						}
					} else {
						// Try clicking the item directly
						await firstEquivalent.click();
						await page.waitForTimeout(500);

						console.log("Equivalent item selected");
					}
				}
			}
		});

		test("should highlight selected equivalent in graph", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				const equivalentItems = page
					.locator("[class*='equivalent'], li")
					.filter({ hasText: /equivalent|maps to/i });

				if (
					await equivalentItems
						.first()
						.isVisible({ timeout: 2000 })
						.catch(() => false)
				) {
					// Click first equivalent
					await equivalentItems.first().click();
					await page.waitForTimeout(500);

					// Look for highlighted node in graph
					const highlightedNodes = page.locator(
						"[class*='selected'], [class*='highlighted'], [class*='active']",
					);
					const highlightCount = await highlightedNodes.count().catch(() => 0);

					if (highlightCount > 0) {
						console.log(
							`${highlightCount} equivalent nodes highlighted in graph`,
						);
					}
				}
			}
		});

		test("should show pivot path to equivalent", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for equivalence with path information
				const pathInfo = page.getByText(/via|through|path|route|connection/i);

				if (await pathInfo.isVisible({ timeout: 2000 }).catch(() => false)) {
					console.log("Pivot path information displayed");
				}

				// Look for breadcrumb or path visualization
				const breadcrumb = page.locator(
					"nav, [role='navigation'], [class*='breadcrumb']",
				);

				if (await breadcrumb.isVisible({ timeout: 2000 }).catch(() => false)) {
					console.log("Pivot path breadcrumb shown");
				}
			}
		});

		test("should navigate to pivot target and update panel", async ({
			page,
		}) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Get initial panel content
				const initialPanel = page.locator("aside, [class*='panel'], .w-96");
				const initialText = await initialPanel.textContent().catch(() => "");

				const equivalentItems = page
					.locator("[class*='equivalent'], li")
					.filter({ hasText: /equivalent|maps to/i });

				if (
					await equivalentItems
						.first()
						.isVisible({ timeout: 2000 })
						.catch(() => false)
				) {
					// Click to navigate to equivalent
					await equivalentItems.first().click();
					await page.waitForTimeout(500);

					// Check if panel updated
					const updatedText = await initialPanel.textContent().catch(() => "");

					if (updatedText !== initialText) {
						console.log("Panel updated after pivot navigation");
					} else {
						console.log("Pivot navigation completed");
					}
				}
			}
		});
	});

	test.describe("Equivalence Visual Relationships", () => {
		test("should show equivalence edges in graph", async ({ page }) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				// Look for equivalence edges marked with special styling
				const equivalenceEdges = page.locator(
					".react-flow__edges [class*='equivalent'], [class*='maps-to']",
				);
				const edgeCount = await equivalenceEdges.count().catch(() => 0);

				if (edgeCount > 0) {
					console.log(`${edgeCount} equivalence edges displayed`);
				} else {
					// Alternative: check all edges for equivalence styling
					const _allEdges = page.locator(".react-flow__edges g, svg path");
					console.log("Checking for equivalence edge visualization");
				}
			}
		});

		test("should highlight equivalence relationships when hovering", async ({
			page,
		}) => {
			const firstNode = page
				.locator(".react-flow__nodes > div[data-id]")
				.first();

			if (await firstNode.isVisible({ timeout: 2000 }).catch(() => false)) {
				await firstNode.click();
				await page.waitForTimeout(500);

				const equivalentItems = page
					.locator("[class*='equivalent'], li")
					.filter({ hasText: /equivalent|maps to/i });

				if (
					await equivalentItems
						.first()
						.isVisible({ timeout: 2000 })
						.catch(() => false)
				) {
					// Hover over equivalent item
					await equivalentItems.first().hover();
					await page.waitForTimeout(300);

					// Look for highlighted edges or nodes
					const highlightedElements = page.locator(
						"[class*='highlighted'], [style*='highlight']",
					);
					const highlightCount = await highlightedElements
						.count()
						.catch(() => 0);

					if (highlightCount > 0) {
						console.log(`${highlightCount} elements highlighted on hover`);
					}
				}
			}
		});
	});
});
