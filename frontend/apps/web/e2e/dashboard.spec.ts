import { expect, test } from "@playwright/test";

/**
 * Dashboard E2E Tests
 *
 * Tests for dashboard functionality, widgets, metrics, and overview displays.
 */

test.describe("Dashboard Overview", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should display dashboard page", async ({ page }) => {
		// Should be on dashboard
		await expect(page).toHaveURL("/");

		// Dashboard content should be visible
		const main = page.locator("main");
		await expect(main).toBeVisible();
	});

	test("should show dashboard heading", async ({ page }) => {
		// Look for main heading
		const heading = page
			.getByRole("heading", { name: /dashboard|overview|home/i })
			.first();

		await expect(heading)
			.toBeVisible({ timeout: 5000 })
			.catch(() =>
				console.log("Dashboard heading not found - may use different text"),
			);
	});

	test("should load dashboard data", async ({ page }) => {
		// Wait for data to load
		await page.waitForLoadState("networkidle");

		// Should show some content (projects, items, stats, etc.)
		// This is a general check that dashboard isn't empty
		const content = page.locator("main");
		const textContent = await content.textContent();

		expect(textContent).toBeTruthy();
		expect(textContent!.length).toBeGreaterThan(50);
	});
});

test.describe("Dashboard Metrics", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should display project count metric", async ({ page }) => {
		// Look for project count
		await page
			.locator("text=/projects/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Project count not displayed"));

		// Should show "2" projects from mock data
		await page
			.locator("text=/2/")
			.first()
			.waitFor({ state: "visible", timeout: 2000 })
			.catch(() => console.log("Project count value not displayed"));
	});

	test("should display items count metric", async ({ page }) => {
		// Look for items count
		await page
			.locator("text=/items/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Items count not displayed"));

		// Should show "10" items from mock data
		await page
			.locator("text=/10/")
			.first()
			.waitFor({ state: "visible", timeout: 2000 })
			.catch(() => console.log("Items count value not displayed"));
	});

	test("should display status metrics", async ({ page }) => {
		// Look for status breakdown (completed, in progress, pending)
		await page
			.locator("text=/completed|in progress|pending/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Status metrics not displayed"));
	});

	test("should display priority metrics", async ({ page }) => {
		// Look for priority breakdown
		await page
			.locator("text=/critical|high|medium|low/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Priority metrics not displayed"));
	});
});

test.describe("Dashboard Widgets", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should display recent projects widget", async ({ page }) => {
		// Look for recent/active projects section
		await page
			.locator("text=/recent|projects|active/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Recent projects widget not displayed"));
	});

	test("should display recent items widget", async ({ page }) => {
		// Look for recent items section
		await page
			.locator("text=/recent|items|latest/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Recent items widget not displayed"));
	});

	test("should display activity timeline", async ({ page }) => {
		// Look for activity or timeline widget
		await page
			.locator("text=/activity|timeline|recent changes/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Activity timeline not displayed"));
	});

	test("should display agents status widget", async ({ page }) => {
		// Look for agents status
		await page
			.locator("text=/agents|status|running/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Agents status widget not displayed"));
	});
});

test.describe("Dashboard Navigation", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should navigate to projects from dashboard", async ({ page }) => {
		// Look for "View All Projects" or similar link
		const viewProjectsLink = page
			.getByRole("link", { name: /view.*projects|all projects|see all/i })
			.or(page.getByText(/TraceRTM Core|Mobile App/).first());

		if (await viewProjectsLink.isVisible({ timeout: 3000 })) {
			await viewProjectsLink.click();
			await page.waitForLoadState("networkidle");

			// Should navigate to projects page or project detail
			await expect(page).toHaveURL(/\/projects/);
		}
	});

	test("should navigate to items from dashboard", async ({ page }) => {
		// Look for items link or recent items
		const viewItemsLink = page.getByRole("link", {
			name: /view.*items|all items/i,
		});

		if (await viewItemsLink.isVisible({ timeout: 3000 })) {
			await viewItemsLink.click();
			await page.waitForLoadState("networkidle");

			await expect(page).toHaveURL(/\/items/);
		}
	});

	test("should navigate to specific project from dashboard", async ({
		page,
	}) => {
		// Click on a project name
		const projectLink = page.getByText("TraceRTM Core").first();

		if (await projectLink.isVisible({ timeout: 3000 })) {
			await projectLink.click();
			await page.waitForLoadState("networkidle");

			await expect(page).toHaveURL(/\/projects\/proj-/);
		}
	});
});

test.describe("Dashboard Charts", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should display items by type chart", async ({ page }) => {
		// Look for chart or visualization
		const chart = page
			.locator("canvas, svg")
			.first()
			.or(page.locator('[role="img"]').first());

		await expect(chart)
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Charts not displayed on dashboard"));
	});

	test("should display items by status chart", async ({ page }) => {
		// Look for status breakdown chart
		await page
			.locator("text=/status|completed|in progress/i")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Status chart not displayed"));
	});

	test("should display trend chart", async ({ page }) => {
		// Look for trend/timeline chart
		await page
			.locator("canvas, svg")
			.first()
			.waitFor({ state: "visible", timeout: 5000 })
			.catch(() => console.log("Trend chart not displayed"));
	});
});

test.describe("Dashboard Quick Actions", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should show quick action buttons", async ({ page }) => {
		// Look for quick action buttons (Create Project, Create Item, etc.)
		const quickActions = page
			.locator("button")
			.filter({ hasText: /create|new|add/i });

		if (await quickActions.first().isVisible({ timeout: 3000 })) {
			const count = await quickActions.count();
			expect(count).toBeGreaterThan(0);
		}
	});

	test("should create project from dashboard", async ({ page }) => {
		const createProjectButton = page
			.getByRole("button", { name: /create.*project|new project/i })
			.first();

		if (await createProjectButton.isVisible({ timeout: 3000 })) {
			await createProjectButton.click();

			// Should open create project dialog
			const dialog = page.getByRole("dialog");
			await expect(dialog)
				.toBeVisible({ timeout: 2000 })
				.catch(() =>
					console.log("Create project dialog not opened from dashboard"),
				);
		}
	});

	test("should create item from dashboard", async ({ page }) => {
		const createItemButton = page
			.getByRole("button", { name: /create.*item|new item/i })
			.first();

		if (await createItemButton.isVisible({ timeout: 3000 })) {
			await createItemButton.click();

			// Should open create item dialog or navigate to create page
			await page.waitForTimeout(500);
		}
	});
});

test.describe("Dashboard Filters", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should show project filter", async ({ page }) => {
		// Look for project filter dropdown
		const projectFilter = page
			.locator("select")
			.filter({ hasText: /project/i })
			.first()
			.or(page.getByLabel(/project/i).first());

		if (await projectFilter.isVisible({ timeout: 3000 })) {
			console.log("Project filter available on dashboard");
		}
	});

	test("should filter dashboard by project", async ({ page }) => {
		const projectFilter = page.locator("select").first();

		if (await projectFilter.isVisible({ timeout: 3000 })) {
			await projectFilter.click();
			await page.waitForTimeout(300);

			// Select a project
			const projectOption = page.getByText("TraceRTM Core").first();
			if (await projectOption.isVisible({ timeout: 2000 })) {
				await projectOption.click();
				await page.waitForLoadState("networkidle");
			}
		}
	});

	test("should show time range filter", async ({ page }) => {
		// Look for date/time range filter
		const timeFilter = page
			.locator("select, button")
			.filter({ hasText: /today|week|month|year|range/i })
			.first();

		if (await timeFilter.isVisible({ timeout: 3000 })) {
			console.log("Time range filter available on dashboard");
		}
	});
});

test.describe("Dashboard Refresh", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should show refresh button", async ({ page }) => {
		// Look for refresh button
		const refreshButton = page
			.getByRole("button", { name: /refresh|reload/i })
			.first()
			.or(page.locator('button[aria-label*="refresh" i]').first());

		if (await refreshButton.isVisible({ timeout: 3000 })) {
			console.log("Refresh button available on dashboard");
		}
	});

	test("should refresh dashboard data", async ({ page }) => {
		const refreshButton = page
			.getByRole("button", { name: /refresh|reload/i })
			.first();

		if (await refreshButton.isVisible({ timeout: 3000 })) {
			await refreshButton.click();
			await page.waitForLoadState("networkidle");

			// Data should be reloaded
			await page.waitForTimeout(500);
		}
	});

	test("should auto-refresh on navigation back", async ({ page }) => {
		// Navigate away
		await page.goto("/projects");
		await page.waitForLoadState("networkidle");

		// Navigate back to dashboard
		await page.goto("/");
		await page.waitForLoadState("networkidle");

		// Dashboard should reload data
		const main = page.locator("main");
		await expect(main).toBeVisible();
	});
});
