// API Types - Re-exported from @tracertm/types with additional types

import type {
  Item,
  ItemStatus,
  Link,
  LinkType,
  Priority,
  Project,
  ViewType,
} from '@tracertm/types';

import type { paths } from './schema';

// OpenAPI Schema Type Exports

type ApiPaths = keyof paths;

type PathOperations<P extends ApiPaths> = keyof paths[P];

type ApiRequestBody<P extends ApiPaths, M extends PathOperations<P>> = paths[P][M] extends {
  requestBody: { content: { 'application/json': infer Body } };
}
  ? Body
  : never;

type ApiResponse<
  P extends ApiPaths,
  M extends PathOperations<P>,
  Status extends number = 200,
> = paths[P][M] extends { responses: infer R }
  ? Status extends keyof R
    ? R[Status] extends { content: { 'application/json': infer Body } }
      ? Body
      : never
    : never
  : never;

type ApiQueryParams<P extends ApiPaths, M extends PathOperations<P>> = paths[P][M] extends {
  parameters: { query?: infer Q };
}
  ? Q
  : never;

type ApiPathParams<P extends ApiPaths, M extends PathOperations<P>> = paths[P][M] extends {
  parameters: { path?: infer P };
}
  ? P
  : never;

interface ApiAllParams<P extends ApiPaths, M extends PathOperations<P>> {
  path?: ApiPathParams<P, M> | undefined;
  query?: ApiQueryParams<P, M> | undefined;
}

interface CreateProjectInput {
  description?: string | undefined;
  name: string;
}

interface UpdateProjectInput {
  description?: string | undefined;
  name?: string | undefined;
}

interface CreateItemInput {
  description?: string | undefined;
  parentId?: string | undefined;
  priority?: Priority | undefined;
  projectId: string;
  status?: ItemStatus | undefined;
  title: string;
  type: string;
}

interface UpdateItemInput {
  description?: string | undefined;
  parentId?: string | undefined;
  priority?: Priority | undefined;
  status?: ItemStatus | undefined;
  title?: string | undefined;
  type?: string | undefined;
}

interface CreateLinkInput {
  description?: string | undefined;
  sourceId: string;
  targetId: string;
  type: LinkType;
}

interface UpdateLinkInput {
  description?: string | undefined;
  type?: LinkType | undefined;
}

interface SearchQuery {
  page?: number | undefined;
  per_page?: number | undefined;
  priorities?: Priority[] | undefined;
  projectId?: string | undefined;
  q: string;
  statuses?: ItemStatus[] | undefined;
  types?: string[] | undefined;
}

interface SearchResult {
  hasMore: boolean;
  items: Item[];
  page: number;
  pageSize: number;
  total: number;
}

interface PaginationParams {
  cursor?: string | undefined;
  limit?: number | undefined;
  offset?: number | undefined;
}

interface CursorPaginationResponse<T> {
  count: number;
  has_more: boolean;
  items: T[];
  next_cursor?: string | undefined;
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
  view?: ViewType | undefined;
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

type ErrorDetails = Record<string, string | number | boolean | object | null | undefined>;

interface ApiError {
  code: string;
  details?: ErrorDetails | undefined;
  message: string;
}

// Grouped type exports
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
