// API Types - Re-exported from @tracertm/types with additional types

import type {
	Item,
	ItemStatus,
	LinkType,
	Priority,
	ViewType,
} from "@tracertm/types";
import type { paths } from "./schema";

export type {
	Item,
	ItemStatus,
	Link,
	LinkType,
	Priority,
	Project,
	ViewType,
} from "@tracertm/types";

// OpenAPI Schema Type Exports
export type { paths } from "./schema";

/**
 * Extract path keys from OpenAPI schema
 * @example type ItemsPaths = ApiPaths<"/api/v1/items">;
 */
export type ApiPaths = keyof paths;

/**
 * Extract operation keys for a specific path
 * @example type GetItemsOp = PathOperations<"/api/v1/items">;
 */
export type PathOperations<P extends ApiPaths> = keyof paths[P];

/**
 * Extract request body type for a specific operation
 * @example type CreateItemBody = ApiRequestBody<"/api/v1/items", "post">;
 */
export type ApiRequestBody<
	P extends ApiPaths,
	M extends PathOperations<P>,
> = paths[P][M] extends {
	requestBody: { content: { "application/json": infer Body } };
}
	? Body
	: never;

/**
 * Extract response type for a specific operation
 * @example type ListItemsResponse = ApiResponse<"/api/v1/items", "get", 200>;
 */
export type ApiResponse<
	P extends ApiPaths,
	M extends PathOperations<P>,
	Status extends number = 200,
> = paths[P][M] extends { responses: infer R }
	? Status extends keyof R
		? R[Status] extends { content: { "application/json": infer Body } }
			? Body
			: never
		: never
	: never;

/**
 * Extract query parameters for a specific operation
 * @example type ListItemsParams = ApiQueryParams<"/api/v1/items", "get">;
 */
export type ApiQueryParams<
	P extends ApiPaths,
	M extends PathOperations<P>,
> = paths[P][M] extends { parameters: { query?: infer Q } } ? Q : never;

/**
 * Extract path parameters for a specific operation
 * @example type GetItemParams = ApiPathParams<"/api/v1/items/{item_id}", "get">;
 */
export type ApiPathParams<
	P extends ApiPaths,
	M extends PathOperations<P>,
> = paths[P][M] extends { parameters: { path?: infer P } } ? P : never;

/**
 * Complete parameter set for an operation
 * @example type ListItemsParams = ApiAllParams<"/api/v1/items", "get">;
 */
export type ApiAllParams<P extends ApiPaths, M extends PathOperations<P>> = {
	query?: ApiQueryParams<P, M>;
	path?: ApiPathParams<P, M>;
};

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

export interface ErrorDetails {
	[key: string]: string | number | boolean | object | null | undefined;
}

export interface ApiError {
	code: string;
	message: string;
	details?: ErrorDetails;
}
