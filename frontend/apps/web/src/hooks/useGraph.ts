import { useQuery } from "@tanstack/react-query";
import { api } from "../api/endpoints";

export const graphKeys = {
	all: ["graph"] as const,
	ancestors: (id: string, depth?: number) =>
		[...graphKeys.all, "ancestors", id, depth] as const,
	cycles: (projectId?: string) =>
		[...graphKeys.all, "cycles", projectId] as const,
	dependencies: (id: string, depth?: number) =>
		[...graphKeys.all, "dependencies", id, depth] as const,
	descendants: (id: string, depth?: number) =>
		[...graphKeys.all, "descendants", id, depth] as const,
	full: (projectId?: string) => [...graphKeys.all, "full", projectId] as const,
	impact: (id: string, depth?: number) =>
		[...graphKeys.all, "impact", id, depth] as const,
	orphans: (projectId?: string) =>
		[...graphKeys.all, "orphans", projectId] as const,
	path: (sourceId: string, targetId: string) =>
		[...graphKeys.all, "path", sourceId, targetId] as const,
};

export function useFullGraph(projectId?: string) {
	return useQuery({
		queryFn: () => api.graph.getFullGraph(projectId),
		queryKey: graphKeys.full(projectId),
		staleTime: 60000, // 1 minute
	});
}

export function useAncestors(id: string, depth?: number) {
	return useQuery({
		enabled: !!id,
		queryFn: () => api.graph.getAncestors(id, depth),
		queryKey: graphKeys.ancestors(id, depth),
	});
}

export function useDescendants(id: string, depth?: number) {
	return useQuery({
		enabled: !!id,
		queryFn: () => api.graph.getDescendants(id, depth),
		queryKey: graphKeys.descendants(id, depth),
	});
}

export function useImpactAnalysis(id: string, depth?: number) {
	return useQuery({
		enabled: !!id,
		queryFn: () => api.graph.getImpactAnalysis(id, depth),
		queryKey: graphKeys.impact(id, depth),
	});
}

export function useDependencyAnalysis(id: string, depth?: number) {
	return useQuery({
		enabled: !!id,
		queryFn: () => api.graph.getDependencyAnalysis(id, depth),
		queryKey: graphKeys.dependencies(id, depth),
	});
}

export function useFindPath(sourceId: string, targetId: string) {
	return useQuery({
		enabled: !!sourceId && !!targetId,
		queryFn: () => api.graph.findPath(sourceId, targetId),
		queryKey: graphKeys.path(sourceId, targetId),
	});
}

export function useDetectCycles(projectId?: string) {
	return useQuery({
		queryFn: () => api.graph.detectCycles(projectId),
		queryKey: graphKeys.cycles(projectId),
	});
}

export function useOrphanItems(projectId?: string) {
	return useQuery({
		queryFn: () => api.graph.getOrphanItems(projectId),
		queryKey: graphKeys.orphans(projectId),
	});
}
