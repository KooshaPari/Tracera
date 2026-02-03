/* eslint-disable id-length, no-magic-numbers -- OpenAPI generics and status literals */
// API Types - Re-exported from @tracertm/types with additional types

import type {
	Item,
	ItemStatus,
	Link,
	LinkType,
	Priority,
	Project,
	ViewType,
} from "@tracertm/types";
import type { paths } from "./schema";

// OpenAPI Schema Type Exports

type ApiPaths = keyof paths;

type PathOperations<P extends ApiPaths> = keyof paths[P];

type ApiRequestBody<
	P extends ApiPaths,
	M extends PathOperations<P>,
> = paths[P][M] extends {
	requestBody: { content: { "application/json": infer Body } };
}
	? Body
	: never;

type ApiResponse<
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

type ApiQueryParams<
	P extends ApiPaths,
	M extends PathOperations<P>,
> = paths[P][M] extends { parameters: { query?: infer Q } } ? Q : never;

type ApiPathParams<
	P extends ApiPaths,
	M extends PathOperations<P>,
> = paths[P][M] extends { parameters: { path?: infer P } } ? P : never;

interface ApiAllParams<P extends ApiPaths, M extends PathOperations<P>> {
	path?: ApiPathParams<P, M>;
	query?: ApiQueryParams<P, M>;
}

interface CreateProjectInput {
	description?: string;
	name: string;
}

interface UpdateProjectInput {
	description?: string;
	name?: string;
}

interface CreateItemInput {
	description?: string;
	parentId?: string;
	priority?: Priority;
	projectId: string;
	status?: ItemStatus;
	title: string;
	type: string;
}

interface UpdateItemInput {
	description?: string;
	parentId?: string;
	priority?: Priority;
	status?: ItemStatus;
	title?: string;
	type?: string;
}

interface CreateLinkInput {
	description?: string;
	sourceId: string;
	targetId: string;
	type: LinkType;
}

interface UpdateLinkInput {
	description?: string;
	type?: LinkType;
}

interface SearchQuery {
	page?: number;
	per_page?: number;
	priorities?: Priority[];
	projectId?: string;
	q: string;
	statuses?: ItemStatus[];
	types?: string[];
}

interface SearchResult {
	hasMore: boolean;
	items: Item[];
	page: number;
	pageSize: number;
	total: number;
}

interface PaginationParams {
	cursor?: string;
	limit?: number;
	offset?: number;
}

interface CursorPaginationResponse<T> {
	count: number;
	has_more: boolean;
	items: T[];
	next_cursor?: string;
}

interface ImpactAnalysis {
	affectedCount: number;
	affectedItems: Item[];
	depth: number;
	itemId: string;
}

interface DependencyAnalysis {
	dependencies: Item[];
	dependencyCount: number;
	depth: number;
	itemId: string;
}

interface TraceabilityMatrix {
	coverage: Record<
		string,
		{
			coveragePercentage: number;
			documentedBy: Item[];
			implementedBy: Item[];
			testedBy: Item[];
		}
	>;
	requirements: Item[];
}

interface GraphNode {
	id: string;
	status: ItemStatus;
	title: string;
	type: string;
	view?: ViewType;
}

interface GraphEdge {
	id: string;
	source: string;
	target: string;
	type: LinkType;
}

interface GraphData {
	edges: GraphEdge[];
	nodes: GraphNode[];
}

interface PaginatedResponse<T> {
	hasMore: boolean;
	items: T[];
	page: number;
	pageSize: number;
	total: number;
}

type ErrorDetails = Record<
	string,
	string | number | boolean | object | null | undefined
>;

interface ApiError {
	code: string;
	details?: ErrorDetails;
	message: string;
}

export type {
	ApiAllParams,
	ApiError,
	ApiPathParams,
	ApiPaths,
	ApiQueryParams,
	ApiRequestBody,
	ApiResponse,
	CreateItemInput,
	CreateLinkInput,
	CreateProjectInput,
	CursorPaginationResponse,
	DependencyAnalysis,
	ErrorDetails,
	GraphData,
	GraphEdge,
	GraphNode,
	ImpactAnalysis,
	Item,
	ItemStatus,
	Link,
	LinkType,
	PaginatedResponse,
	PaginationParams,
	PathOperations,
	Priority,
	Project,
	SearchQuery,
	SearchResult,
	TraceabilityMatrix,
	UpdateItemInput,
	UpdateLinkInput,
	UpdateProjectInput,
	ViewType,
	paths,
};
