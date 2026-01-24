/**
 * Test Data Fixtures for E2E Tests
 * Provides reusable test data for various test scenarios
 */

import type { Agent, Item, Link, Project } from "../../src/api/types";
import {
	AgentStatus,
	ItemPriority,
	ItemStatus,
	ItemType,
	LinkType,
} from "../../src/api/types";

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
		created_at: lastWeek,
		updated_at: now,
	},
	{
		id: "test-proj-2",
		name: "Sample Project",
		description: "Sample project for testing filters and search",
		metadata: {
			team: "Dev",
			status: "active",
		},
		created_at: yesterday,
		updated_at: now,
	},
];

/**
 * Test Items
 */
export const testItems: Item[] = [
	{
		id: "test-item-1",
		project_id: "test-proj-1",
		type: ItemType.REQUIREMENT,
		title: "Test Requirement",
		description: "A requirement for testing",
		status: ItemStatus.PENDING,
		priority: ItemPriority.HIGH,
		metadata: { tags: ["test", "requirement"] },
		created_at: lastWeek,
		updated_at: now,
	},
	{
		id: "test-item-2",
		project_id: "test-proj-1",
		type: ItemType.FEATURE,
		title: "Test Feature",
		description: "A feature for testing",
		status: ItemStatus.IN_PROGRESS,
		priority: ItemPriority.MEDIUM,
		metadata: { tags: ["test", "feature"] },
		created_at: lastWeek,
		updated_at: now,
		parent_id: "test-item-1",
	},
	{
		id: "test-item-3",
		project_id: "test-proj-1",
		type: ItemType.CODE,
		title: "Test Implementation",
		description: "Code implementation for testing",
		status: ItemStatus.COMPLETED,
		priority: ItemPriority.HIGH,
		metadata: { file_path: "src/test.ts" },
		created_at: lastWeek,
		updated_at: yesterday,
	},
];

/**
 * Test Links
 */
export const testLinks: Link[] = [
	{
		id: "test-link-1",
		source_id: "test-item-2",
		target_id: "test-item-1",
		type: LinkType.IMPLEMENTS,
		metadata: {},
		created_at: lastWeek,
		updated_at: lastWeek,
	},
	{
		id: "test-link-2",
		source_id: "test-item-3",
		target_id: "test-item-2",
		type: LinkType.IMPLEMENTS,
		metadata: {},
		created_at: lastWeek,
		updated_at: lastWeek,
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
		capabilities: ["testing", "validation"],
		status: AgentStatus.IDLE,
		metadata: { version: "1.0.0" },
		created_at: lastWeek,
		updated_at: now,
		last_heartbeat: now,
	},
	{
		id: "test-agent-2",
		name: "Test Agent 2",
		type: "analyzer",
		capabilities: ["analysis", "reporting"],
		status: AgentStatus.BUSY,
		metadata: { version: "1.0.0" },
		created_at: lastWeek,
		updated_at: now,
		last_heartbeat: now,
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
		created_at: now,
		updated_at: now,
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
		project_id: projectId,
		type: ItemType.FEATURE,
		title: `Test Item ${Date.now()}`,
		description: "Auto-generated test item",
		status: ItemStatus.PENDING,
		priority: ItemPriority.MEDIUM,
		metadata: {},
		created_at: now,
		updated_at: now,
		...overrides,
	};
}

/**
 * Generate test link data
 */
export function generateTestLink(
	sourceId: string,
	targetId: string,
	overrides: Partial<Link> = {},
): Link {
	return {
		id: generateTestId("link"),
		source_id: sourceId,
		target_id: targetId,
		type: LinkType.IMPLEMENTS,
		metadata: {},
		created_at: now,
		updated_at: now,
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
		capabilities: ["testing"],
		status: AgentStatus.IDLE,
		metadata: { version: "1.0.0" },
		created_at: now,
		updated_at: now,
		last_heartbeat: now,
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
			lastError = error as Error;
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

	link: (sourceId: string, targetId: string, link: Partial<Link> = {}) => ({
		data: generateTestLink(sourceId, targetId, link),
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
