/**
 * Test Data Fixtures for E2E Tests
 * Provides reusable test data for various test scenarios
 */

import type { Agent, Item, Link, Project } from "@tracertm/types";

// Helper to generate timestamps
const now = new Date().toISOString();
const yesterday = new Date(Date.now() - 86400000).toISOString();
const lastWeek = new Date(Date.now() - 604800000).toISOString();

/**
 * Test Projects
 */
export const testProjects: Project[] = [
	{
		id: "test-proj-1",
		name: "E2E Test Project",
		description: "Test project for E2E testing",
		metadata: {
			team: "QA",
			status: "active",
		},
		createdAt: lastWeek,
		updatedAt: now,
	},
	{
		id: "test-proj-2",
		name: "Sample Project",
		description: "Sample project for testing filters and search",
		metadata: {
			team: "Dev",
			status: "active",
		},
		createdAt: yesterday,
		updatedAt: now,
	},
];

/**
 * Test Items
 */
export const testItems: Item[] = [
	{
		id: "test-item-1",
		projectId: "test-proj-1",
		view: "feature",
		type: "requirement",
		title: "Test Requirement",
		description: "A requirement for testing",
		status: "todo",
		priority: "high",
		metadata: { tags: ["test", "requirement"] },
		version: 1,
		createdAt: lastWeek,
		updatedAt: now,
	},
	{
		id: "test-item-2",
		projectId: "test-proj-1",
		view: "feature",
		type: "feature",
		title: "Test Feature",
		description: "A feature for testing",
		status: "in_progress",
		priority: "medium",
		metadata: { tags: ["test", "feature"] },
		version: 1,
		createdAt: lastWeek,
		updatedAt: now,
		parentId: "test-item-1",
	},
	{
		id: "test-item-3",
		projectId: "test-proj-1",
		view: "code",
		type: "code",
		title: "Test Implementation",
		description: "Code implementation for testing",
		status: "done",
		priority: "high",
		metadata: { file_path: "src/test.ts" },
		version: 1,
		createdAt: lastWeek,
		updatedAt: yesterday,
	},
];

/**
 * Test Links
 */
export const testLinks: Link[] = [
	{
		id: "test-link-1",
		projectId: "test-proj-1",
		sourceId: "test-item-2",
		targetId: "test-item-1",
		type: "implements",
		metadata: {},
		version: 1,
		createdAt: lastWeek,
		updatedAt: lastWeek,
	},
	{
		id: "test-link-2",
		projectId: "test-proj-1",
		sourceId: "test-item-3",
		targetId: "test-item-2",
		type: "implements",
		metadata: {},
		version: 1,
		createdAt: lastWeek,
		updatedAt: lastWeek,
	},
];

/**
 * Test Agents
 */
export const testAgents: Agent[] = [
	{
		id: "test-agent-1",
		name: "Test Agent 1",
		type: "test",
		status: "idle",
		lastSeen: lastWeek,
	},
	{
		id: "test-agent-2",
		name: "Test Agent 2",
		type: "analyzer",
		status: "active",
		lastSeen: now,
	},
];

/**
 * Form Input Data
 */
export const formInputs = {
	project: {
		name: "Test Project from E2E",
		description: "This project was created by an E2E test",
	},
	item: {
		title: "Test Item from E2E",
		description: "This item was created by an E2E test",
	},
	link: {
		type: "implements",
	},
	agent: {
		name: "Test Agent from E2E",
		type: "test",
	},
};

/**
 * Search Queries
 */
export const searchQueries = {
	valid: ["test", "authentication", "dashboard", "code"],
	invalid: ["xyznoresults123", "notfound999"],
	partial: ["auth", "proj", "item"],
};

/**
 * Filter Values
 */
export const filters = {
	itemType: ["Requirement", "Feature", "Code", "Test", "API", "Database"],
	itemStatus: ["Pending", "In Progress", "Completed", "Blocked"],
	itemPriority: ["Critical", "High", "Medium", "Low"],
	agentStatus: ["Idle", "Busy", "Error", "Offline"],
	linkType: ["Implements", "Tests", "Documents", "Relates To", "Depends On"],
};

/**
 * Validation Error Messages
 */
export const validationMessages = {
	required: /required/i,
	invalidEmail: /invalid.*email/i,
	tooShort: /too short|minimum length/i,
	tooLong: /too long|maximum length/i,
	invalidFormat: /invalid format/i,
};

/**
 * Success Messages
 */
export const successMessages = {
	created: /created successfully|successfully created/i,
	updated: /updated successfully|successfully updated/i,
	deleted: /deleted successfully|successfully deleted/i,
	saved: /saved successfully|successfully saved/i,
};

/**
 * Helper Functions
 */

/**
 * Generate a unique test ID
 */
export function generateTestId(prefix = "test"): string {
	return `${prefix}-${Date.now()}-${Math.random().toString(36).substring(7)}`;
}

/**
 * Generate test project data
 */
export function generateTestProject(overrides: Partial<Project> = {}): Project {
	return {
		id: generateTestId("proj"),
		name: `Test Project ${Date.now()}`,
		description: "Auto-generated test project",
		metadata: { team: "QA", status: "active" },
		createdAt: now,
		updatedAt: now,
		...overrides,
	};
}

/**
 * Generate test item data
 */
export function generateTestItem(
	projectId: string,
	overrides: Partial<Item> = {},
): Item {
	return {
		id: generateTestId("item"),
		projectId,
		view: "feature",
		type: "feature",
		title: `Test Item ${Date.now()}`,
		description: "Auto-generated test item",
		status: "todo",
		priority: "medium",
		metadata: {},
		version: 1,
		createdAt: now,
		updatedAt: now,
		...overrides,
	};
}

/**
 * Generate test link data
 */
export function generateTestLink(
	projectId: string,
	sourceId: string,
	targetId: string,
	overrides: Partial<Link> = {},
): Link {
	return {
		id: generateTestId("link"),
		projectId,
		sourceId,
		targetId,
		type: "implements",
		metadata: {},
		version: 1,
		createdAt: now,
		updatedAt: now,
		...overrides,
	};
}

/**
 * Generate test agent data
 */
export function generateTestAgent(overrides: Partial<Agent> = {}): Agent {
	return {
		id: generateTestId("agent"),
		name: `Test Agent ${Date.now()}`,
		type: "test",
		status: "idle",
		lastSeen: now,
		...overrides,
	};
}

/**
 * Wait for a specific duration (for timing-sensitive tests)
 */
export async function waitFor(ms: number): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry a function until it succeeds or max attempts reached
 */
export async function retryUntil<T>(
	fn: () => Promise<T>,
	maxAttempts = 3,
	delayMs = 1000,
): Promise<T> {
	let lastError: Error | undefined;

	for (let attempt = 1; attempt <= maxAttempts; attempt++) {
		try {
			return await fn();
		} catch (error) {
			lastError = error instanceof Error ? error : new Error(String(error));
			if (attempt < maxAttempts) {
				await waitFor(delayMs);
			}
		}
	}

	throw lastError || new Error("Retry failed");
}

/**
 * Mock API Response Helpers
 */
export const mockResponses = {
	project: (project: Partial<Project> = {}) => ({
		data: generateTestProject(project),
		status: 200,
	}),

	item: (projectId: string, item: Partial<Item> = {}) => ({
		data: generateTestItem(projectId, item),
		status: 200,
	}),

	link: (projectId: string, sourceId: string, targetId: string, link: Partial<Link> = {}) => ({
		data: generateTestLink(projectId, sourceId, targetId, link),
		status: 200,
	}),

	agent: (agent: Partial<Agent> = {}) => ({
		data: generateTestAgent(agent),
		status: 200,
	}),

	error: (message: string, status = 400) => ({
		error: { message },
		status,
	}),
};
