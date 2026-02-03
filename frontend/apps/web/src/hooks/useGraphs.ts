import { useQuery } from "@tanstack/react-query";
import { QUERY_CONFIGS, queryKeys } from "@/lib/queryConfig";
import { client } from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

/**
 * Graph node data structure
 */
export type GraphNode = Record<
	string,
	string | number | boolean | object | null | undefined
>;

/**
 * Graph link data structure
 */
export type GraphLink = Record<
	string,
	string | number | boolean | object | null | undefined
>;

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
	if (!res.ok) {
		throw new Error("Failed to fetch graphs");
	}
	const data = await res.json();
	const graphs = data["graphs"] || [];
	return graphs.map((graph: any) => ({
		description: graph.description,
		graphRules: graph.graph_rules || graph.graphRules,
		graphType: graph.graph_type || graph.graphType,
		graphVersion: graph.graph_version || graph.graphVersion,
		id: graph.id,
		metadata: graph.metadata || graph.graph_metadata || graph.graphMetadata,
		name: graph.name,
		rootItemId: graph.root_item_id || graph.rootItemId,
	}));
}

async function fetchGraphProjection(
	projectId: string,
	graphId?: string,
	graphType?: string,
): Promise<GraphProjection> {
	const params = new URLSearchParams();
	if (graphId) {
		params.set("graph_id", graphId);
	}
	if (graphType) {
		params.set("graph_type", graphType);
	}
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/graph?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		throw new Error("Failed to fetch graph projection");
	}
	const data = await res.json();
	return {
		graph: data["graph"]
			? {
					description: data["graph"].description,
					graphRules: data["graph"].graph_rules || data["graph"].graphRules,
					graphType: data["graph"].graph_type || data["graph"].graphType,
					graphVersion:
						data["graph"].graph_version || data["graph"].graphVersion,
					id: data["graph"].id,
					metadata:
						data["graph"].metadata ||
						data["graph"].graph_metadata ||
						data["graph"].graphMetadata,
					name: data["graph"].name,
					rootItemId: data["graph"].root_item_id || data["graph"].rootItemId,
				}
			: undefined,
		links: data["links"] || [],
		nodes: data["nodes"] || [],
	};
}

export function useGraphs(projectId?: string) {
	return useQuery({
		queryKey: projectId ? queryKeys.graph.full(projectId) : ["graphs"],
		queryFn: () => fetchGraphs(projectId || ""),
		enabled: Boolean(projectId),
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
		enabled: Boolean(projectId) && (Boolean(graphId) || Boolean(graphType)),
		...QUERY_CONFIGS.graph, // Graph projections are expensive, cache longer
	});
}
