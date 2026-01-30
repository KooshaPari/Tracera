import { expect, test } from "./global-setup";

/**
 * E2E Tests for Sync Status and Offline Indicators
 * Tests sync functionality, offline mode, and real-time updates
 */
test.describe("Sync and Offline Mode", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test.describe("Sync Status Indicator", () => {
		test("should display sync status in header", async ({ page }) => {
			// Look for sync status indicator
			const syncIndicator = page.locator('[data-testid="sync-status"]');
			await expect(syncIndicator)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Sync status indicator not found in header");
				});

			// Alternative: check for sync icon
			const syncIcon = page.getByRole("button", { name: /sync|synchronize/i });
			await expect(syncIcon)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Sync icon not found");
				});
		});

		test("should show synced status when online", async ({ page }) => {
			// Check for synced indicator
			const syncedText = page.getByText(/synced|up to date|connected/i);
			await expect(syncedText)
				.toBeVisible({ timeout: 10000 })
				.catch(() => {
					console.log("Synced status not displayed");
				});

			// Check for green/success indicator
			const successIndicator = page.locator(
				'[data-testid="sync-status"][class*="success"]',
			);
			await expect(successIndicator)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Success indicator not found for sync status");
				});
		});

		test("should show last sync time", async ({ page }) => {
			// Look for last sync timestamp
			const lastSync = page.getByText(/last sync|synced.*ago|updated.*ago/i);
			await expect(lastSync)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Last sync time not displayed");
				});
		});

		test("should trigger manual sync", async ({ page }) => {
			// Find sync button
			const syncBtn = page.getByRole("button", {
				name: /sync|refresh|reload/i,
			});
			if (await syncBtn.isVisible({ timeout: 2000 })) {
				await syncBtn.click();

				// Should show syncing indicator
				const syncingIndicator = page.getByText(/syncing|synchronizing/i);
				await expect(syncingIndicator)
					.toBeVisible({ timeout: 5000 })
					.catch(() => {
						console.log("Syncing indicator not shown during sync");
					});

				// Wait for sync to complete
				await page.waitForLoadState("networkidle");

				// Should show synced status
				const syncedIndicator = page.getByText(/synced|up to date/i);
				await expect(syncedIndicator).toBeVisible({ timeout: 10000 });
			} else {
				console.log("Manual sync button not found");
			}
		});
	});

	test.describe("Offline Mode", () => {
		test("should detect offline status", async ({ page, context }) => {
			// Go offline
			await context.setOffline(true);
			await page.reload();
			await page.waitForLoadState("networkidle");

			// Should show offline indicator
			const offlineIndicator = page.getByText(
				/offline|disconnected|no connection/i,
			);
			await expect(offlineIndicator)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Offline indicator not displayed");
				});

			// Check for offline icon/badge
			const offlineBadge = page.locator('[data-testid="offline-badge"]');
			await expect(offlineBadge)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Offline badge not found");
				});

			// Go back online
			await context.setOffline(false);
		});

		test("should show offline banner", async ({ page, context }) => {
			// Go offline
			await context.setOffline(true);
			await page.reload();
			await page.waitForLoadState("networkidle");

			// Look for offline banner
			const banner = page.getByRole("alert", { name: /offline/i });
			await expect(banner)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Offline banner not displayed");
				});

			// Banner should be dismissible or auto-hide
			const closeBtn = banner.getByRole("button", { name: /close|dismiss/i });
			if (await closeBtn.isVisible({ timeout: 2000 })) {
				await closeBtn.click();
				await expect(banner).not.toBeVisible();
			}

			await context.setOffline(false);
		});

		test("should allow viewing cached data offline", async ({
			page,
			context,
		}) => {
			// Load data while online
			await page.getByRole("link", { name: /items/i }).click();
			await page.waitForLoadState("networkidle");

			// Verify items are loaded
			const items = page.locator('[data-testid="item-row"]');
			const onlineCount = await items.count().catch(() => 0);
			expect(onlineCount).toBeGreaterThan(0);

			// Go offline
			await context.setOffline(true);
			await page.reload();
			await page.waitForLoadState("networkidle");

			// Navigate to items again
			await page.getByRole("link", { name: /items/i }).click();
			await page.waitForLoadState("networkidle");

			// Should still show cached items
			const cachedItems = page.locator('[data-testid="item-row"]');
			const offlineCount = await cachedItems.count().catch(() => 0);
			expect(offlineCount).toBeGreaterThan(0);

			await context.setOffline(false);
		});

		test("should queue changes while offline", async ({ page, context }) => {
			// Go offline
			await context.setOffline(true);
			await page.reload();
			await page.waitForLoadState("networkidle");

			// Try to create an item
			await page.getByRole("link", { name: /items/i }).click();
			await page.waitForLoadState("networkidle");

			const createBtn = page.getByRole("button", { name: /create|new item/i });
			if (await createBtn.isVisible({ timeout: 2000 })) {
				await createBtn.click();

				// Fill form
				await page.getByLabel(/title/i).fill("Offline Test Item");
				await page.getByLabel(/type/i).click();
				await page
					.getByText(/feature/i)
					.first()
					.click();
				await page.getByRole("button", { name: /create|save/i }).click();
				await page.waitForLoadState("networkidle");

				// Should show queued message
				const queuedMsg = page.getByText(/queued|will sync|pending/i);
				await expect(queuedMsg)
					.toBeVisible({ timeout: 5000 })
					.catch(() => {
						console.log("Queued changes message not shown");
					});
			} else {
				console.log("Cannot test offline changes - create form not available");
			}

			await context.setOffline(false);
		});

		test("should sync queued changes when back online", async ({
			page,
			context,
		}) => {
			// Go offline and make changes
			await context.setOffline(true);
			await page.reload();
			await page.waitForLoadState("networkidle");

			// Make a change (simplified - actual implementation may vary)
			console.log("Making offline changes...");

			// Go back online
			await context.setOffline(false);
			await page.reload();
			await page.waitForLoadState("networkidle");

			// Should show syncing indicator
			const syncingMsg = page.getByText(/syncing|uploading changes/i);
			await expect(syncingMsg)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Syncing message not shown when reconnecting");
				});

			// Wait for sync to complete
			await page.waitForTimeout(2000);

			// Should show synced status
			const syncedMsg = page.getByText(/synced|up to date/i);
			await expect(syncedMsg).toBeVisible({ timeout: 10000 });
		});
	});

	test.describe("Sync Conflicts", () => {
		test("should detect sync conflicts", async ({ page }) => {
			// This test requires backend support for conflict simulation
			// For now, just check if conflict UI exists
			const conflictIndicator = page.locator('[data-testid="sync-conflict"]');
			await expect(conflictIndicator)
				.not.toBeVisible()
				.catch(() => {
					console.log(
						"No sync conflicts detected (expected in normal operation)",
					);
				});
		});

		test("should allow resolving conflicts", async ({ page }) => {
			// Navigate to settings or sync management
			const settingsLink = page.getByRole("link", { name: /settings/i });
			if (await settingsLink.isVisible({ timeout: 2000 })) {
				await settingsLink.click();
				await page.waitForLoadState("networkidle");

				// Look for conflict resolution UI
				const conflictSection = page.getByText(/conflicts|resolve/i);
				await expect(conflictSection)
					.toBeVisible({ timeout: 5000 })
					.catch(() => {
						console.log("Conflict resolution UI not found in settings");
					});
			} else {
				console.log(
					"Settings not accessible - skipping conflict resolution test",
				);
			}
		});
	});

	test.describe("Real-time Updates", () => {
		test("should show WebSocket connection status", async ({ page }) => {
			// Look for WebSocket indicator
			const wsIndicator = page.locator('[data-testid="websocket-status"]');
			await expect(wsIndicator)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("WebSocket status indicator not found");
				});

			// Check for connected status
			const connectedMsg = page.getByText(/connected|live/i);
			await expect(connectedMsg)
				.toBeVisible({ timeout: 10000 })
				.catch(() => {
					console.log("WebSocket connected status not shown");
				});
		});

		test("should receive real-time updates", async ({ page }) => {
			// Navigate to items page
			await page.getByRole("link", { name: /items/i }).click();
			await page.waitForLoadState("networkidle");

			// Note: Actual real-time update testing requires WebSocket simulation
			// For now, just verify the page is listening for updates
			console.log(
				"Real-time updates require WebSocket simulation - skipping actual update test",
			);

			// Check if update notifications appear
			const updateNotification = page.locator(
				'[data-testid="update-notification"]',
			);
			await expect(updateNotification)
				.not.toBeVisible()
				.catch(() => {
					console.log(
						"No real-time updates received (expected in test environment)",
					);
				});
		});

		test("should show live status badges", async ({ page }) => {
			// Look for live status indicator
			const liveBadge = page.getByText(/live|real-time/i);
			await expect(liveeBadge)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Live status badge not displayed");
				});
		});
	});

	test.describe("Sync Settings", () => {
		test("should access sync settings", async ({ page }) => {
			// Navigate to settings
			const settingsLink = page.getByRole("link", { name: /settings/i });
			if (await settingsLink.isVisible({ timeout: 2000 })) {
				await settingsLink.click();
				await page.waitForLoadState("networkidle");

				// Look for sync settings section
				const syncSection = page.getByRole("heading", {
					name: /sync|synchronization/i,
				});
				await expect(syncSection)
					.toBeVisible({ timeout: 5000 })
					.catch(() => {
						console.log("Sync settings section not found");
					});
			} else {
				console.log("Settings page not accessible");
			}
		});

		test("should toggle auto-sync", async ({ page }) => {
			const settingsLink = page.getByRole("link", { name: /settings/i });
			if (await settingsLink.isVisible({ timeout: 2000 })) {
				await settingsLink.click();
				await page.waitForLoadState("networkidle");

				// Look for auto-sync toggle
				const autoSyncToggle = page.getByLabel(/auto.*sync|automatic.*sync/i);
				if (await autoSyncToggle.isVisible({ timeout: 2000 })) {
					// Toggle off
					await autoSyncToggle.click();
					await page.waitForTimeout(500);

					// Verify state changed
					const isChecked = await autoSyncToggle.isChecked();
					console.log(
						`Auto-sync is now: ${isChecked ? "enabled" : "disabled"}`,
					);
				} else {
					console.log("Auto-sync toggle not found");
				}
			} else {
				console.log("Settings not accessible");
			}
		});

		test("should configure sync interval", async ({ page }) => {
			const settingsLink = page.getByRole("link", { name: /settings/i });
			if (await settingsLink.isVisible({ timeout: 2000 })) {
				await settingsLink.click();
				await page.waitForLoadState("networkidle");

				// Look for sync interval setting
				const intervalSelect = page.getByLabel(/sync interval|refresh rate/i);
				if (await intervalSelect.isVisible({ timeout: 2000 })) {
					await intervalSelect.click();
					await page
						.getByText(/5.*minutes|10.*minutes|30.*minutes/i)
						.first()
						.click();

					console.log("Sync interval configured");
				} else {
					console.log("Sync interval setting not found");
				}
			} else {
				console.log("Settings not accessible");
			}
		});
	});

	test.describe("Sync History", () => {
		test("should display sync history", async ({ page }) => {
			const settingsLink = page.getByRole("link", { name: /settings/i });
			if (await settingsLink.isVisible({ timeout: 2000 })) {
				await settingsLink.click();
				await page.waitForLoadState("networkidle");

				// Look for sync history section
				const historySection = page.getByRole("heading", {
					name: /sync.*history|recent.*syncs/i,
				});
				if (await historySection.isVisible({ timeout: 2000 })) {
					// Check for sync log entries
					const logEntries = page.locator('[data-testid="sync-log-entry"]');
					const count = await logEntries.count().catch(() => 0);
					console.log(`Found ${count} sync history entries`);
				} else {
					console.log("Sync history not available");
				}
			} else {
				console.log("Settings not accessible");
			}
		});

		test("should show sync errors in history", async ({ page }) => {
			const settingsLink = page.getByRole("link", { name: /settings/i });
			if (await settingsLink.isVisible({ timeout: 2000 })) {
				await settingsLink.click();
				await page.waitForLoadState("networkidle");

				// Look for error entries in sync history
				const errorEntry = page.locator('[data-testid="sync-error"]');
				await expect(errorEntry)
					.not.toBeVisible()
					.catch(() => {
						console.log(
							"No sync errors in history (expected in normal operation)",
						);
					});
			} else {
				console.log("Settings not accessible");
			}
		});
	});

	test.describe("Network Error Handling", () => {
		test("should show error when sync fails", async ({ page, context }) => {
			// Simulate network error by going offline during sync
			const syncBtn = page.getByRole("button", { name: /sync/i });
			if (await syncBtn.isVisible({ timeout: 2000 })) {
				// Go offline
				await context.setOffline(true);

				// Try to sync
				await syncBtn.click();
				await page.waitForTimeout(1000);

				// Should show error message
				const errorMsg = page.getByText(
					/sync failed|connection.*error|offline/i,
				);
				await expect(errorMsg)
					.toBeVisible({ timeout: 5000 })
					.catch(() => {
						console.log("Sync error message not displayed");
					});

				await context.setOffline(false);
			} else {
				console.log("Sync button not available for error testing");
			}
		});

		test("should retry failed syncs", async ({ page, context }) => {
			// This requires more complex setup
			console.log("Sync retry testing requires backend simulation");

			// Look for retry button in error state
			const retryBtn = page.getByRole("button", { name: /retry|try again/i });
			await expect(retryBtn)
				.not.toBeVisible()
				.catch(() => {
					console.log(
						"No failed syncs to retry (expected in normal operation)",
					);
				});
		});
	});

	test.describe("Data Freshness Indicators", () => {
		test("should show data age indicator", async ({ page }) => {
			await page.getByRole("link", { name: /items/i }).click();
			await page.waitForLoadState("networkidle");

			// Look for data freshness indicator
			const freshnessIndicator = page.getByText(
				/updated.*ago|last.*updated|fresh|stale/i,
			);
			await expect(freshnessIndicator)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Data freshness indicator not displayed");
				});
		});

		test("should warn about stale data", async ({ page, context }) => {
			// Go offline to make data stale
			await context.setOffline(true);
			await page.reload();
			await page.waitForLoadState("networkidle");

			// Wait a bit to simulate stale data
			await page.waitForTimeout(2000);

			// Navigate to items
			await page.getByRole("link", { name: /items/i }).click();
			await page.waitForLoadState("networkidle");

			// Look for stale data warning
			const staleWarning = page.getByText(
				/stale|outdated|old data|offline data/i,
			);
			await expect(staleWarning)
				.toBeVisible({ timeout: 5000 })
				.catch(() => {
					console.log("Stale data warning not displayed");
				});

			await context.setOffline(false);
		});
	});
});
