// Mock data for TraceRTM development
import type {
	Agent,
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
	{
		id: "item-3",
		projectId: "proj-1",
		view: "CODE" as ViewType,
		type: "test",
		title: "Auth Tests",
		description: "Unit tests for authentication",
		status: "todo" as ItemStatus,
		priority: "medium" as Priority,
		version: 1,
		createdAt: yesterday,
		updatedAt: now,
	},
	{
		id: "item-4",
		projectId: "proj-1",
		view: "API" as ViewType,
		type: "api",
		title: "Authentication API",
		description: "REST API endpoints for user management",
		status: "in_progress" as ItemStatus,
		priority: "high" as Priority,
		version: 1,
		createdAt: yesterday,
		updatedAt: now,
	},
	{
		id: "item-5",
		projectId: "proj-1",
		view: "DATABASE" as ViewType,
		type: "database",
		title: "User Database Schema",
		description: "Database schema for users table",
		status: "done" as ItemStatus,
		priority: "critical" as Priority,
		version: 1,
		createdAt: lastWeek,
		updatedAt: lastWeek,
	},
	{
		id: "item-6",
		projectId: "proj-2",
		view: "WIREFRAME" as ViewType,
		type: "wireframe",
		title: "Dashboard Mockup",
		description: "Figma mockup for main dashboard",
		status: "done" as ItemStatus,
		priority: "high" as Priority,
		version: 1,
		createdAt: yesterday,
		updatedAt: now,
	},
	{
		id: "item-7",
		projectId: "proj-2",
		view: "DOCUMENTATION" as ViewType,
		type: "documentation",
		title: "API Documentation",
		description: "Complete API documentation",
		status: "in_progress" as ItemStatus,
		priority: "medium" as Priority,
		version: 1,
		createdAt: yesterday,
		updatedAt: now,
	},
	{
		id: "item-8",
		projectId: "proj-2",
		view: "DEPLOYMENT" as ViewType,
		type: "deployment",
		title: "Production Deployment",
		description: "Deploy to production environment",
		status: "todo" as ItemStatus,
		priority: "critical" as Priority,
		version: 1,
		createdAt: now,
		updatedAt: now,
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
	{
		id: "link-2",
		projectId: "proj-1",
		sourceId: "item-2",
		targetId: "item-3",
		type: "tests",
		createdAt: yesterday,
	},
	{
		id: "link-3",
		projectId: "proj-1",
		sourceId: "item-1",
		targetId: "item-4",
		type: "depends_on",
		createdAt: yesterday,
	},
	{
		id: "link-4",
		projectId: "proj-1",
		sourceId: "item-4",
		targetId: "item-5",
		type: "depends_on",
		createdAt: lastWeek,
	},
];

// Mock Agents
export const mockAgents: Agent[] = [
	{
		id: "agent-1",
		name: "Analyzer Agent",
		type: "analyzer",
		status: "active",
		lastSeen: now,
	},
	{
		id: "agent-2",
		name: "Generator Agent",
		type: "generator",
		status: "idle",
		lastSeen: yesterday,
	},
];

// Helper functions for filtering and finding mock data
export const filterItemsByProject = (projectId: string): Item[] => {
	return mockItems.filter((item) => item.projectId === projectId);
};

export const filterLinksBySource = (sourceId: string): Link[] => {
	return mockLinks.filter((link) => link.sourceId === sourceId);
};

export const filterLinksByTarget = (targetId: string): Link[] => {
	return mockLinks.filter((link) => link.targetId === targetId);
};

export const findProjectById = (id: string): Project | undefined => {
	return mockProjects.find((project) => project.id === id);
};

export const findItemById = (id: string): Item | undefined => {
	return mockItems.find((item) => item.id === id);
};

export const findLinkById = (id: string): Link | undefined => {
	return mockLinks.find((link) => link.id === id);
};

export const findAgentById = (id: string): Agent | undefined => {
	return mockAgents.find((agent) => agent.id === id);
};

export const generateProjectId = (): string => {
	return `proj-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const generateItemId = (): string => {
	return `item-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const generateLinkId = (): string => {
	return `link-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const generateAgentId = (): string => {
	return `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// Export all mock data
export const mockData = {
	projects: mockProjects,
	items: mockItems,
	links: mockLinks,
	agents: mockAgents,
};
