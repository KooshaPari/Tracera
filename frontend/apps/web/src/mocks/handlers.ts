// MSW handlers for TraceRTM API mocking
import { HttpResponse, http } from "msw";
import type {
	Agent,
	CreateAgentInput,
	CreateItemInput,
	CreateLinkInput,
	CreateProjectInput,
	DependencyAnalysis,
	GraphData,
	ImpactAnalysis,
	Item,
	Link,
	Project,
	UpdateItemInput,
	UpdateLinkInput,
	UpdateProjectInput,
} from "../api/types";
import {
	filterItemsByProject,
	filterLinksBySource,
	filterLinksByTarget,
	findAgentById,
	findItemById,
	findLinkById,
	findProjectById,
	generateAgentId,
	generateItemId,
	generateLinkId,
	generateProjectId,
	mockAgents,
	mockItems,
	mockLinks,
	mockProjects,
} from "./data";

const API_BASE = "http://localhost:8000";

// Helper to simulate delays
const delay = (ms = 100) => new Promise((resolve) => setTimeout(resolve, ms));

export const handlers = [
	// ============================================================================
	// HEALTH CHECK
	// ============================================================================
	http.get(`${API_BASE}/health`, async () => {
		await delay();
		return HttpResponse.json({
			status: "ok",
			service: "tracertm-api",
		});
	}),

	http.get(`${API_BASE}/api/v1/health`, async () => {
		await delay();
		return HttpResponse.json({
			status: "ok",
			service: "tracertm-api",
		});
	}),

	// ============================================================================
	// PROJECT ENDPOINTS
	// ============================================================================
	http.get(`${API_BASE}/api/v1/projects`, async ({ request }) => {
		await delay();
		const url = new URL(request.url);
		const limit = Number(url.searchParams.get("limit")) || mockProjects.length;
		const offset = Number(url.searchParams.get("offset")) || 0;

		const paginatedProjects = mockProjects.slice(offset, offset + limit);
		// API returns { total: number, projects: Project[] }
		return HttpResponse.json({
			total: mockProjects.length,
			projects: paginatedProjects,
		});
	}),

	http.get(`${API_BASE}/api/v1/projects/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const project = findProjectById(id as string);

		if (!project) {
			return HttpResponse.json({ error: "Project not found" }, { status: 404 });
		}

		return HttpResponse.json(project);
	}),

	http.post(`${API_BASE}/api/v1/projects`, async ({ request }) => {
		await delay();
		const body = (await request.json()) as CreateProjectInput;

		const newProject: Project = {
			id: generateProjectId(),
			name: body.name,
			...(body.description !== undefined && { description: body.description }),
			metadata: body.metadata || {},
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
		};

		mockProjects.push(newProject);
		return HttpResponse.json(newProject, { status: 201 });
	}),

	http.put(`${API_BASE}/api/v1/projects/:id`, async ({ params, request }) => {
		await delay();
		const { id } = params;
		const body = (await request.json()) as UpdateProjectInput;
		const projectIndex = mockProjects.findIndex((p) => p.id === id);

		if (projectIndex === -1) {
			return HttpResponse.json({ error: "Project not found" }, { status: 404 });
		}

		const baseProject = mockProjects[projectIndex]!;
		const updatedProject: Project = {
			id: baseProject.id,
			name: body.name ?? baseProject.name,
			...(body.description !== undefined
				? { description: body.description }
				: baseProject.description !== undefined
					? { description: baseProject.description }
					: {}),
			...(body.metadata !== undefined
				? { metadata: body.metadata }
				: baseProject.metadata !== undefined
					? { metadata: baseProject.metadata }
					: {}),
			createdAt: baseProject.createdAt,
			updatedAt: new Date().toISOString(),
		};

		mockProjects[projectIndex] = updatedProject;
		return HttpResponse.json(updatedProject);
	}),

	http.delete(`${API_BASE}/api/v1/projects/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const projectIndex = mockProjects.findIndex((p) => p.id === id);

		if (projectIndex === -1) {
			return HttpResponse.json({ error: "Project not found" }, { status: 404 });
		}

		mockProjects.splice(projectIndex, 1);
		return HttpResponse.json(null, { status: 204 });
	}),

	// ============================================================================
	// ITEM ENDPOINTS
	// ============================================================================
	http.get(`${API_BASE}/api/v1/items`, async ({ request }) => {
		await delay();
		const url = new URL(request.url);
		const projectId = url.searchParams.get("project_id");
		const limit = Number(url.searchParams.get("limit")) || mockItems.length;
		const offset = Number(url.searchParams.get("offset")) || 0;

		let items = projectId ? filterItemsByProject(projectId) : mockItems;
		const total = items.length;
		items = items.slice(offset, offset + limit);

		// API returns { total: number, items: Item[] }
		return HttpResponse.json({ total, items });
	}),

	http.get(`${API_BASE}/api/v1/items/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const item = findItemById(id as string);

		if (!item) {
			return HttpResponse.json({ error: "Item not found" }, { status: 404 });
		}

		return HttpResponse.json(item);
	}),

	http.post(`${API_BASE}/api/v1/items`, async ({ request }) => {
		await delay();
		const body = (await request.json()) as CreateItemInput;

		const newItem: Item = {
			id: generateItemId(),
			projectId: body.project_id,
			type: body.type,
			title: body.title,
			...(body.description !== undefined && { description: body.description }),
			status: body.status || ("pending" as any),
			...(body.priority !== undefined && { priority: body.priority }),
			metadata: body.metadata || {},
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
			...(body.parent_id !== undefined && { parentId: body.parent_id }),
		};

		mockItems.push(newItem);
		return HttpResponse.json(newItem, { status: 201 });
	}),

	http.put(`${API_BASE}/api/v1/items/:id`, async ({ params, request }) => {
		await delay();
		const { id } = params;
		const body = (await request.json()) as UpdateItemInput;
		const itemIndex = mockItems.findIndex((i) => i.id === id);

		if (itemIndex === -1) {
			return HttpResponse.json({ error: "Item not found" }, { status: 404 });
		}

		const baseItem = mockItems[itemIndex]!;
		const updatedItem: Item = {
			id: baseItem.id,
			projectId: baseItem.projectId,
			type: body.type ?? baseItem.type,
			title: body.title ?? baseItem.title,
			...((body.description ?? baseItem.description) !== undefined && {
				description: body.description ?? baseItem.description,
			}),
			status: body.status ?? baseItem.status,
			...((body.priority ?? baseItem.priority) !== undefined && {
				priority: body.priority ?? baseItem.priority,
			}),
			...((body.metadata ?? baseItem.metadata) !== undefined && {
				metadata: body.metadata ?? baseItem.metadata,
			}),
			createdAt: baseItem.createdAt,
			updatedAt: new Date().toISOString(),
			...((body.parent_id ?? baseItem.parent_id) !== undefined && {
				parentId: body.parent_id ?? baseItem.parent_id,
			}),
		};

		mockItems[itemIndex] = updatedItem;
		return HttpResponse.json(updatedItem);
	}),

	http.delete(`${API_BASE}/api/v1/items/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const itemIndex = mockItems.findIndex((i) => i.id === id);

		if (itemIndex === -1) {
			return HttpResponse.json({ error: "Item not found" }, { status: 404 });
		}

		mockItems.splice(itemIndex, 1);
		return HttpResponse.json(null, { status: 204 });
	}),

	// ============================================================================
	// LINK ENDPOINTS
	// ============================================================================
	http.get(`${API_BASE}/api/v1/links`, async ({ request }) => {
		await delay();
		const url = new URL(request.url);
		const projectId = url.searchParams.get("project_id");
		const limit = Number(url.searchParams.get("limit")) || mockLinks.length;
		const offset = Number(url.searchParams.get("offset")) || 0;

		let links = mockLinks;
		if (projectId) {
			// Filter links by project (check source or target items)
			links = mockLinks.filter((link) => {
				const sourceItem = findItemById(link.source_id);
				const targetItem = findItemById(link.target_id);
				return (
					sourceItem?.projectId === projectId ||
					targetItem?.projectId === projectId
				);
			});
		}
		const total = links.length;
		const paginatedLinks = links.slice(offset, offset + limit);
		// API returns { total: number, links: Link[] }
		return HttpResponse.json({ total, links: paginatedLinks });
	}),

	http.get(`${API_BASE}/api/v1/links/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const link = findLinkById(id as string);

		if (!link) {
			return HttpResponse.json({ error: "Link not found" }, { status: 404 });
		}

		return HttpResponse.json(link);
	}),

	http.post(`${API_BASE}/api/v1/links`, async ({ request }) => {
		await delay();
		const body = (await request.json()) as CreateLinkInput;

		const newLink: Link = {
			id: generateLinkId(),
			sourceId: body.source_id,
			targetId: body.target_id,
			type: body.type,
			metadata: body.metadata || {},
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
		};

		mockLinks.push(newLink);
		return HttpResponse.json(newLink, { status: 201 });
	}),

	http.put(`${API_BASE}/api/v1/links/:id`, async ({ params, request }) => {
		await delay();
		const { id } = params;
		const body = (await request.json()) as UpdateLinkInput;
		const linkIndex = mockLinks.findIndex((l) => l.id === id);

		if (linkIndex === -1) {
			return HttpResponse.json({ error: "Link not found" }, { status: 404 });
		}

		const baseLink = mockLinks[linkIndex]!;
		const updatedLink: Link = {
			id: baseLink.id,
			sourceId: baseLink.source_id,
			targetId: baseLink.target_id,
			type: body.type ?? baseLink.type,
			...((body.metadata ?? baseLink.metadata) !== undefined && {
				metadata: body.metadata ?? baseLink.metadata,
			}),
			createdAt: baseLink.createdAt,
			updatedAt: new Date().toISOString(),
		};

		mockLinks[linkIndex] = updatedLink;
		return HttpResponse.json(updatedLink);
	}),

	http.delete(`${API_BASE}/api/v1/links/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const linkIndex = mockLinks.findIndex((l) => l.id === id);

		if (linkIndex === -1) {
			return HttpResponse.json({ error: "Link not found" }, { status: 404 });
		}

		mockLinks.splice(linkIndex, 1);
		return HttpResponse.json(null, { status: 204 });
	}),

	// ============================================================================
	// AGENT ENDPOINTS
	// ============================================================================
	http.get(`${API_BASE}/api/v1/agents`, async ({ request }) => {
		await delay();
		const url = new URL(request.url);
		const limit = Number(url.searchParams.get("limit")) || mockAgents.length;
		const offset = Number(url.searchParams.get("offset")) || 0;

		const paginatedAgents = mockAgents.slice(offset, offset + limit);
		return HttpResponse.json(paginatedAgents);
	}),

	http.get(`${API_BASE}/api/v1/agents/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const agent = findAgentById(id as string);

		if (!agent) {
			return HttpResponse.json({ error: "Agent not found" }, { status: 404 });
		}

		return HttpResponse.json(agent);
	}),

	http.post(`${API_BASE}/api/v1/agents`, async ({ request }) => {
		await delay();
		const body = (await request.json()) as CreateAgentInput;

		const newAgent: Agent = {
			id: generateAgentId(),
			name: body.name,
			type: body.type,
			capabilities: body.capabilities,
			status: "idle" as any,
			metadata: body.metadata || {},
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
			last_heartbeat: new Date().toISOString(),
		};

		mockAgents.push(newAgent);
		return HttpResponse.json(newAgent, { status: 201 });
	}),

	// ============================================================================
	// GRAPH ENDPOINTS
	// ============================================================================
	http.get(`${API_BASE}/api/v1/graph/full`, async ({ request }) => {
		await delay();
		const url = new URL(request.url);
		const projectId = url.searchParams.get("project_id");

		const items = projectId ? filterItemsByProject(projectId) : mockItems;
		const nodes = items.map((item) => ({
			id: item.id,
			type: item.type,
			title: item.title,
			status: item.status,
			...(item.metadata !== undefined && { metadata: item.metadata }),
		}));

		const edges = mockLinks.map((link) => ({
			id: link.id,
			source: link.source_id,
			target: link.target_id,
			type: link.type,
			...(link.metadata !== undefined && { metadata: link.metadata }),
		}));

		const graphData: GraphData = { nodes, edges };
		return HttpResponse.json(graphData);
	}),

	http.get(`${API_BASE}/api/v1/graph/impact/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const item = findItemById(id as string);

		if (!item) {
			return HttpResponse.json({ error: "Item not found" }, { status: 404 });
		}

		const affectedLinks = filterLinksByTarget(id as string);
		const affectedItems = affectedLinks
			.map((link) => findItemById(link.source_id))
			.filter(Boolean) as Item[];

		const impactAnalysis: ImpactAnalysis = {
			item_id: id as string,
			affected_items: affectedItems,
			affected_count: affectedItems.length,
			depth: 1,
		};

		return HttpResponse.json(impactAnalysis);
	}),

	http.get(`${API_BASE}/api/v1/graph/dependencies/:id`, async ({ params }) => {
		await delay();
		const { id } = params;
		const item = findItemById(id as string);

		if (!item) {
			return HttpResponse.json({ error: "Item not found" }, { status: 404 });
		}

		const dependencyLinks = filterLinksBySource(id as string);
		const dependencies = dependencyLinks
			.map((link) => findItemById(link.target_id))
			.filter(Boolean) as Item[];

		const dependencyAnalysis: DependencyAnalysis = {
			item_id: id as string,
			dependencies,
			dependency_count: dependencies.length,
			depth: 1,
		};

		return HttpResponse.json(dependencyAnalysis);
	}),

	// ============================================================================
	// SYNC STATUS ENDPOINT
	// ============================================================================
	http.get(`${API_BASE}/api/v1/sync/status`, async () => {
		await delay();
		return HttpResponse.json({
			status: "synced",
			last_sync: new Date().toISOString(),
			pending_changes: 0,
		});
	}),
];
