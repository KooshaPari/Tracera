import type { Page, Route } from "@playwright/test";

/**
 * Mock API data for E2E tests
 */
export const mockProjects = [
	{
		id: "1",
		name: "TraceRTM Frontend",
		description: "Desktop App + Website for traceability management",
		status: "active",
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
	{
		id: "2",
		name: "Pokemon Go Demo",
		description: "Demo project for testing",
		status: "active",
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
	{
		id: "3",
		name: "E-Commerce Platform",
		description: "Online shopping application",
		status: "active",
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
];

export const mockItems = [
	{
		id: "item-1",
		title: "User Authentication",
		description: "Implement user login and registration",
		type: "requirement",
		status: "in_progress",
		priority: "high",
		projectId: "1",
		view: "Feature",
		version: 1,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
	{
		id: "item-2",
		title: "Dashboard View",
		description: "Create main dashboard with metrics",
		type: "feature",
		status: "todo",
		priority: "medium",
		projectId: "1",
		view: "Feature",
		version: 1,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
	{
		id: "item-3",
		title: "API Integration",
		description: "Connect to backend services",
		type: "requirement",
		status: "done",
		priority: "high",
		projectId: "1",
		view: "Code",
		version: 1,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
	{
		id: "item-4",
		title: "Unit Tests",
		description: "Write comprehensive unit tests",
		type: "test",
		status: "in_progress",
		priority: "medium",
		projectId: "1",
		view: "Test",
		version: 1,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
];

export const mockAgents = [
	{
		id: "agent-1",
		name: "Code Analyzer",
		type: "analyzer",
		status: "idle",
		capabilities: ["code-analysis", "dependency-check"],
		lastHeartbeat: new Date().toISOString(),
	},
	{
		id: "agent-2",
		name: "Test Runner",
		type: "executor",
		status: "busy",
		capabilities: ["test-execution", "coverage-report"],
		lastHeartbeat: new Date().toISOString(),
	},
	{
		id: "agent-3",
		name: "Documentation Generator",
		type: "generator",
		status: "idle",
		capabilities: ["doc-generation", "api-docs"],
		lastHeartbeat: new Date().toISOString(),
	},
];

export const mockLinks = [
	{
		id: "link-1",
		sourceId: "item-1",
		targetId: "item-2",
		type: "depends_on",
		createdAt: new Date().toISOString(),
	},
	{
		id: "link-2",
		sourceId: "item-3",
		targetId: "item-4",
		type: "tests",
		createdAt: new Date().toISOString(),
	},
];

export const mockSystemStatus = {
	status: "healthy",
	uptime: 99.9,
	activeAgents: 2,
	queuedJobs: 5,
};

/**
 * Setup API route mocking for E2E tests
 * Uses a single route handler with URL parsing for reliable interception
 */
export async function setupApiMocks(page: Page): Promise<void> {
	const apiUrl = "http://localhost:8000";

	// Single comprehensive route handler for all API calls
	await page.route(`${apiUrl}/**`, async (route: Route) => {
		const url = route.request().url();
		const method = route.request().method();
		const pathname = new URL(url).pathname;

		// Health endpoint
		if (pathname === "/api/v1/health") {
			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify({ status: "healthy" }),
			});
			return;
		}

		// Projects endpoints
		if (pathname.startsWith("/api/v1/projects")) {
			if (method === "GET") {
				if (
					pathname !== "/api/v1/projects" &&
					pathname.includes("/projects/")
				) {
					// Single project
					const projectId = pathname.split("/projects/")[1]?.split("/")[0];
					const project = mockProjects.find((p) => p.id === projectId);
					await route.fulfill({
						status: project ? 200 : 404,
						contentType: "application/json",
						body: JSON.stringify(project || { error: "Not found" }),
					});
				} else {
					// List projects
					await route.fulfill({
						status: 200,
						contentType: "application/json",
						body: JSON.stringify(mockProjects),
					});
				}
			} else if (method === "POST") {
				const body = route.request().postDataJSON();
				const newProject = {
					id: `proj-${Date.now()}`,
					...body,
					createdAt: new Date().toISOString(),
					updatedAt: new Date().toISOString(),
				};
				await route.fulfill({
					status: 201,
					contentType: "application/json",
					body: JSON.stringify(newProject),
				});
			} else {
				await route.fulfill({
					status: 200,
					contentType: "application/json",
					body: JSON.stringify({}),
				});
			}
			return;
		}

		// Items endpoints
		if (pathname.startsWith("/api/v1/items")) {
			if (method === "GET") {
				if (pathname !== "/api/v1/items" && pathname.includes("/items/")) {
					// Single item
					const itemId = pathname.split("/items/")[1]?.split("/")[0];
					const item = mockItems.find((i) => i.id === itemId);
					await route.fulfill({
						status: item ? 200 : 404,
						contentType: "application/json",
						body: JSON.stringify(item || { error: "Not found" }),
					});
				} else {
					// List items with optional filtering
					const urlParams = new URL(url).searchParams;
					const projectId = urlParams.get("project_id");
					let items = mockItems;
					if (projectId) {
						items = mockItems.filter((i) => i.projectId === projectId);
					}
					await route.fulfill({
						status: 200,
						contentType: "application/json",
						body: JSON.stringify({ items, total: items.length }),
					});
				}
			} else if (method === "POST") {
				const body = route.request().postDataJSON();
				const newItem = {
					id: `item-${Date.now()}`,
					...body,
					createdAt: new Date().toISOString(),
					updatedAt: new Date().toISOString(),
				};
				await route.fulfill({
					status: 201,
					contentType: "application/json",
					body: JSON.stringify(newItem),
				});
			} else {
				await route.fulfill({
					status: 200,
					contentType: "application/json",
					body: JSON.stringify({}),
				});
			}
			return;
		}

		// Agents endpoints
		if (pathname.startsWith("/api/v1/agents")) {
			if (method === "GET") {
				await route.fulfill({
					status: 200,
					contentType: "application/json",
					body: JSON.stringify(mockAgents),
				});
			} else {
				await route.fulfill({
					status: 200,
					contentType: "application/json",
					body: JSON.stringify({}),
				});
			}
			return;
		}

		// Links endpoints
		if (pathname.startsWith("/api/v1/links")) {
			if (method === "GET") {
				await route.fulfill({
					status: 200,
					contentType: "application/json",
					body: JSON.stringify(mockLinks),
				});
			} else {
				await route.fulfill({
					status: 200,
					contentType: "application/json",
					body: JSON.stringify({}),
				});
			}
			return;
		}

		// Graph endpoints
		if (pathname.startsWith("/api/v1/graph")) {
			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify({
					nodes: mockItems.map((item) => ({
						id: item.id,
						label: item.title,
						type: item.type,
						data: item,
					})),
					edges: mockLinks.map((link) => ({
						id: link.id,
						source: link.sourceId,
						target: link.targetId,
						type: link.type,
					})),
				}),
			});
			return;
		}

		// System status
		if (pathname.startsWith("/api/v1/system")) {
			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify(mockSystemStatus),
			});
			return;
		}

		// Search endpoint
		if (pathname.startsWith("/api/v1/search")) {
			const urlParams = new URL(url).searchParams;
			const query = urlParams.get("q") || "";

			const results = mockItems.filter(
				(item) =>
					item.title.toLowerCase().includes(query.toLowerCase()) ||
					item.description.toLowerCase().includes(query.toLowerCase()),
			);

			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify({ results, total: results.length }),
			});
			return;
		}

		// Events endpoint
		if (pathname.startsWith("/api/v1/events")) {
			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify([
					{
						id: "event-1",
						type: "item_created",
						data: { itemId: "item-1", title: "User Authentication" },
						timestamp: new Date().toISOString(),
					},
				]),
			});
			return;
		}

		// Default fallback for unhandled API routes
		console.log(`Unhandled API route: ${method} ${url}`);
		await route.fulfill({
			status: 200,
			contentType: "application/json",
			body: JSON.stringify({}),
		});
	});
}
