import { useQuery } from "@tanstack/react-query";
import { api } from "../api/endpoints";

export const graphKeys = {
	all: ["graph"] as const,
	full: (projectId?: string) => [...graphKeys.all, "full", projectId] as const,
	ancestors: (id: string, depth?: number) =>
		[...graphKeys.all, "ancestors", id, depth] as const,
	descendants: (id: string, depth?: number) =>
		[...graphKeys.all, "descendants", id, depth] as const,
	impact: (id: string, depth?: number) =>
		[...graphKeys.all, "impact", id, depth] as const,
	dependencies: (id: string, depth?: number) =>
		[...graphKeys.all, "dependencies", id, depth] as const,
	path: (sourceId: string, targetId: string) =>
		[...graphKeys.all, "path", sourceId, targetId] as const,
	cycles: (projectId?: string) =>
		[...graphKeys.all, "cycles", projectId] as const,
	orphans: (projectId?: string) =>
		[...graphKeys.all, "orphans", projectId] as const,
};

export function useFullGraph(projectId?: string) {
	return useQuery({
		queryKey: graphKeys.full(projectId),
		queryFn: () => api.graph.getFullGraph(projectId),
		staleTime: 60000, // 1 minute
	});
}

export function useAncestors(id: string, depth?: number) {
	return useQuery({
		queryKey: graphKeys.ancestors(id, depth),
		queryFn: () => api.graph.getAncestors(id, depth),
		enabled: !!id,
	});
}

export function useDescendants(id: string, depth?: number) {
	return useQuery({
		queryKey: graphKeys.descendants(id, depth),
		queryFn: () => api.graph.getDescendants(id, depth),
		enabled: !!id,
	});
}

export function useImpactAnalysis(id: string, depth?: number) {
	return useQuery({
		queryKey: graphKeys.impact(id, depth),
		queryFn: () => api.graph.getImpactAnalysis(id, depth),
		enabled: !!id,
	});
}

export function useDependencyAnalysis(id: string, depth?: number) {
	return useQuery({
		queryKey: graphKeys.dependencies(id, depth),
		queryFn: () => api.graph.getDependencyAnalysis(id, depth),
		enabled: !!id,
	});
}

export function useFindPath(sourceId: string, targetId: string) {
	return useQuery({
		queryKey: graphKeys.path(sourceId, targetId),
		queryFn: () => api.graph.findPath(sourceId, targetId),
		enabled: !!sourceId && !!targetId,
	});
}

export function useDetectCycles(projectId?: string) {
	return useQuery({
		queryKey: graphKeys.cycles(projectId),
		queryFn: () => api.graph.detectCycles(projectId),
	});
}

export function useOrphanItems(projectId?: string) {
	return useQuery({
		queryKey: graphKeys.orphans(projectId),
		queryFn: () => api.graph.getOrphanItems(projectId),
	});
}
