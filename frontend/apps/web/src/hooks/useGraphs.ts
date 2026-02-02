import { useQuery } from "@tanstack/react-query";
import { QUERY_CONFIGS, queryKeys } from "@/lib/queryConfig";
import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

/**
 * Graph node data structure
 */
export interface GraphNode {
	[key: string]: string | number | boolean | object | null | undefined;
}

/**
 * Graph link data structure
 */
export interface GraphLink {
	[key: string]: string | number | boolean | object | null | undefined;
}

export interface GraphSummary {
	id: string;
	name: string;
	graphType: string;
	description?: string | null;
	rootItemId?: string | null;
	graphVersion?: number;
	graphRules?: Record<string, unknown>;
	metadata?: Record<string, unknown>;
}

export interface GraphProjection {
	graph?: GraphSummary | undefined;
	nodes: GraphNode[];
	links: GraphLink[];
}

async function fetchGraphs(projectId: string): Promise<GraphSummary[]> {
	const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/graphs`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch graphs");
	const data = await res.json();
	const graphs = data['graphs'] || [];
	return graphs.map((graph: any) => ({
		id: graph.id,
		name: graph.name,
		graphType: graph.graph_type || graph.graphType,
		description: graph.description,
		rootItemId: graph.root_item_id || graph.rootItemId,
		graphVersion: graph.graph_version || graph.graphVersion,
		graphRules: graph.graph_rules || graph.graphRules,
		metadata: graph.metadata || graph.graph_metadata || graph.graphMetadata,
	}));
}

async function fetchGraphProjection(
	projectId: string,
	graphId?: string,
	graphType?: string,
): Promise<GraphProjection> {
	const params = new URLSearchParams();
	if (graphId) params.set("graph_id", graphId);
	if (graphType) params.set("graph_type", graphType);
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/graph?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch graph projection");
	const data = await res.json();
	return {
		graph: data['graph']
			? {
					id: data['graph'].id,
					name: data['graph'].name,
					graphType: data['graph'].graph_type || data['graph'].graphType,
					description: data['graph'].description,
					rootItemId: data['graph'].root_item_id || data['graph'].rootItemId,
					graphVersion: data['graph'].graph_version || data['graph'].graphVersion,
					graphRules: data['graph'].graph_rules || data['graph'].graphRules,
					metadata:
						data['graph'].metadata ||
						data['graph'].graph_metadata ||
						data['graph'].graphMetadata,
				}
			: undefined,
		nodes: data['nodes'] || [],
		links: data['links'] || [],
	};
}

export function useGraphs(projectId?: string) {
	return useQuery({
		queryKey: projectId ? queryKeys.graph.full(projectId) : ["graphs"],
		queryFn: () => fetchGraphs(projectId || ""),
		enabled: !!projectId,
		...QUERY_CONFIGS.graph, // Graph data is expensive, cache longer
	});
}

export function useGraphProjection(
	projectId?: string,
	graphId?: string,
	graphType?: string,
) {
	return useQuery({
		queryKey: projectId
			? [...queryKeys.graph.full(projectId), graphId, graphType]
			: ["graph", graphId, graphType],
		queryFn: () => fetchGraphProjection(projectId || "", graphId, graphType),
		enabled: !!projectId && (!!graphId || !!graphType),
		...QUERY_CONFIGS.graph, // Graph projections are expensive, cache longer
	});
}
