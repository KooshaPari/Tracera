// API Types - Re-exported from @tracertm/types with additional types
import type {
	Item,
	ItemStatus,
	LinkType,
	Priority,
	ViewType,
} from "@tracertm/types";

export type {
	Agent,
	Item,
	ItemStatus,
	Link,
	LinkType,
	Priority,
	Project,
	ViewType,
} from "@tracertm/types";

// Additional input types for API mutations
export interface CreateProjectInput {
	name: string;
	description?: string;
}

export interface UpdateProjectInput {
	name?: string;
	description?: string;
}

export interface CreateItemInput {
	projectId: string;
	type: string;
	title: string;
	description?: string;
	status?: ItemStatus;
	priority?: Priority;
	parentId?: string;
}

export interface UpdateItemInput {
	type?: string;
	title?: string;
	description?: string;
	status?: ItemStatus;
	priority?: Priority;
	parentId?: string;
}

export interface CreateLinkInput {
	sourceId: string;
	targetId: string;
	type: LinkType;
	description?: string;
}

export interface UpdateLinkInput {
	type?: LinkType;
	description?: string;
}

export interface CreateAgentInput {
	name: string;
	type: string;
}

export interface UpdateAgentInput {
	name?: string;
	type?: string;
	status?: "active" | "idle" | "offline";
}

export interface AgentTask {
	id: string;
	agentId: string;
	type: string;
	payload: Record<string, any>;
	status: string;
	createdAt: string;
	updatedAt: string;
}

export interface TaskResult {
	task_id: string;
	result: Record<string, any>;
	status?: string;
}

export interface TaskError {
	task_id: string;
	error: string;
}

export interface SearchQuery {
	q: string;
	types?: string[];
	statuses?: ItemStatus[];
	priorities?: Priority[];
	projectId?: string;
	page?: number;
	per_page?: number;
}

export interface SearchResult {
	items: Item[];
	total: number;
	page: number;
	pageSize: number;
	hasMore: boolean;
}

export interface PaginationParams {
	limit?: number;
	offset?: number;
}

export interface ImpactAnalysis {
	itemId: string;
	affectedItems: Item[];
	affectedCount: number;
	depth: number;
}

export interface DependencyAnalysis {
	itemId: string;
	dependencies: Item[];
	dependencyCount: number;
	depth: number;
}

export interface TraceabilityMatrix {
	requirements: Item[];
	coverage: Record<
		string,
		{
			implementedBy: Item[];
			testedBy: Item[];
			documentedBy: Item[];
			coveragePercentage: number;
		}
	>;
}

export interface GraphNode {
	id: string;
	type: string;
	title: string;
	status: ItemStatus;
	view?: ViewType;
}

export interface GraphEdge {
	id: string;
	source: string;
	target: string;
	type: LinkType;
}

export interface GraphData {
	nodes: GraphNode[];
	edges: GraphEdge[];
}

export interface PaginatedResponse<T> {
	items: T[];
	total: number;
	page: number;
	pageSize: number;
	hasMore: boolean;
}

export interface ApiError {
	code: string;
	message: string;
	details?: Record<string, any>;
}
