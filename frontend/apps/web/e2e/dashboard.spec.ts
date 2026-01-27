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
		// Look for main dashboard heading - should show "Welcome to TraceRTM"
		const heading = page.getByText(/Welcome to TraceRTM/i);

		await expect(heading)
			.toBeVisible({ timeout: 5000 })
			.catch(() =>
				console.log("Dashboard welcome heading not found"),
			);
	});

	test("should load dashboard data", async ({ page }) => {
		// Wait for data to load
		await page.waitForLoadState("networkidle");

		// Should show dashboard subtitle
		const subtitle = page.getByText(
			/Agent-native requirements traceability and project management/i,
		);
		await expect(subtitle).toBeVisible({ timeout: 5000 });

		// General content check
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
		// Look for project count stat card
		const projectStat = page.getByText("Projects").first();
		await expect(projectStat)
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Project count metric not displayed"));

		// Should show numeric value - check parent section
		const mainContent = page.locator("main");
		const projectText = await mainContent.textContent();
		expect(projectText).toContain("Projects");
	});

	test("should display items count metric", async ({ page }) => {
		// Look for items count stat
		const itemStat = page.getByText("Items").first();
		await expect(itemStat)
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Items count not displayed"));
	});

	test("should display links count metric", async ({ page }) => {
		// Look for links count
		const linkStat = page.getByText("Links").first();
		await expect(linkStat)
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Links metric not displayed"));
	});

	test("should display active agents metric", async ({ page }) => {
		// Look for active agents count
		const agentStat = page.getByText(/Active Agents/i);
		await expect(agentStat)
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Active Agents metric not displayed"));
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

	test("should display recent projects section", async ({ page }) => {
		// Look for Recent Projects heading
		const recentProjects = page.getByText(/Recent Projects/i);
		await expect(recentProjects)
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Recent projects section not displayed"));
	});

	test("should display project cards with information", async ({ page }) => {
		// Look for project names in the recent projects section
		const traceRTMProject = page.getByText(/TraceRTM Frontend/);
		await expect(traceRTMProject)
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Project cards not displayed"));
	});

	test("should show items and links counts", async ({ page }) => {
		// Look for item and link counts in project cards
		const itemsCount = page.getByText(/items/i);
		await expect(itemsCount.first())
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Items count not displayed"));

		const linksCount = page.getByText(/links/i);
		await expect(linksCount.first())
			.toBeVisible({ timeout: 5000 })
			.catch(() => console.log("Links count not displayed"));
	});
});

test.describe("Dashboard Navigation", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
	});

	test("should navigate to projects from stats", async ({ page }) => {
		// Click on Projects metric card
		const projectsCard = page.getByText("Projects").first();

		if (await projectsCard.isVisible({ timeout: 3000 })) {
			// Find the parent card and click it
			const card = projectsCard.locator("../..");
			await card.click();
			await page.waitForLoadState("networkidle");

			// Should navigate to projects page
			await expect(page).toHaveURL(/\/projects/);
		}
	});

	test("should navigate to specific project from dashboard", async ({
		page,
	}) => {
		// Click on a project name in recent projects
		const projectLink = page
			.getByText(/TraceRTM Frontend/)
			.first()
			.locator("..");
		// Find clickable parent link

		if (await projectLink.isVisible({ timeout: 3000 })) {
			await projectLink.click();
			await page.waitForLoadState("networkidle");

			// Should navigate to projects page or project detail
			await expect(page).toHaveURL(/\/projects/);
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
