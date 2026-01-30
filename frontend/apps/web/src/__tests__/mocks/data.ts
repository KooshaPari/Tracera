import type {
	Item,
	ItemStatus,
	Link,
	Priority,
	Project,
	ViewType,
} from "@tracertm/types";

// Helper to generate timestamps
const now = new Date().toISOString();
const yesterday = new Date(Date.now() - 86400000).toISOString();
const lastWeek = new Date(Date.now() - 604800000).toISOString();

// Mock Projects
export const mockProjects: Project[] = [
	{
		id: "proj-1",
		name: "TraceRTM Core",
		description: "Core traceability management system",
		createdAt: lastWeek,
		updatedAt: yesterday,
	},
	{
		id: "proj-2",
		name: "Web Dashboard",
		description: "Web interface for traceability management",
		createdAt: yesterday,
		updatedAt: now,
	},
];

// Mock Items
export const mockItems: Item[] = [
	{
		id: "item-1",
		projectId: "proj-1",
		view: "FEATURE" as ViewType,
		type: "requirement",
		title: "User Authentication",
		description: "Implement secure user authentication system",
		status: "done" as ItemStatus,
		priority: "high" as Priority,
		version: 1,
		createdAt: lastWeek,
		updatedAt: yesterday,
	},
	{
		id: "item-2",
		projectId: "proj-1",
		view: "FEATURE" as ViewType,
		type: "feature",
		title: "Project Dashboard",
		description: "Create comprehensive project dashboard with metrics",
		status: "in_progress" as ItemStatus,
		priority: "high" as Priority,
		version: 1,
		createdAt: lastWeek,
		updatedAt: now,
		parentId: "item-1",
	},
];

// Mock Links
export const mockLinks: Link[] = [
	{
		id: "link-1",
		projectId: "proj-1",
		sourceId: "item-1",
		targetId: "item-2",
		type: "implements",
		createdAt: lastWeek,
	},
];

export const mockData = {
	projects: mockProjects,
	items: mockItems,
	links: mockLinks,
};
