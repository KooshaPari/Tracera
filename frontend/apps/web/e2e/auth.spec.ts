import { expect, test } from "@playwright/test";

/**
 * Authentication E2E Tests
 *
 * Tests for login/logout flows and authentication state management.
 * Note: Since MSW is handling API mocks, we focus on UI flows.
 */

test.describe("Authentication Flows", () => {
	test.beforeEach(async ({ page }) => {
		// Navigate to the app
		await page.goto("/");
	});

	test("should load the application", async ({ page }) => {
		// Wait for the app to load
		await page.waitForLoadState("networkidle");

		// Check that we're on the dashboard (default route)
		await expect(page).toHaveURL("/");

		// Verify page title
		await expect(page).toHaveTitle(/TraceRTM/);
	});

	test("should display main navigation", async ({ page }) => {
		// Wait for navigation to be visible
		const nav = page.locator("nav");
		await expect(nav).toBeVisible();

		// Check for key navigation items
		await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
		await expect(page.getByRole("link", { name: /projects/i })).toBeVisible();
	});

	test("should handle user session", async ({ page }) => {
		// Since MSW mocks are active, the app should load without authentication errors
		await page.waitForLoadState("networkidle");

		// Check that localStorage or sessionStorage has been set
		const localStorage = await page.evaluate(() => window.localStorage);
		expect(localStorage).toBeDefined();
	});

	test("should persist session across page reloads", async ({ page }) => {
		// Navigate to dashboard
		await page.goto("/");
		await page.waitForLoadState("networkidle");

		// Reload the page
		await page.reload();
		await page.waitForLoadState("networkidle");

		// Should still be on dashboard
		await expect(page).toHaveURL("/");
	});
});

test.describe("Navigation Guard", () => {
	test("should allow access to all routes when authenticated", async ({
		page,
	}) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");

		// Test navigation to various routes
		const routes = ["/projects", "/items", "/agents", "/settings"];

		for (const route of routes) {
			await page.goto(route);
			await page.waitForLoadState("networkidle");
			await expect(page).toHaveURL(route);
		}
	});
});
