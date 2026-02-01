// useTemporal - React Query hooks for temporal navigation
// Handles branch and version management

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Branch, Version } from "@/components/temporal/TemporalNavigator";
import { getAuthHeaders } from "@/api/client";
import { QUERY_CONFIGS, queryKeys } from "@/lib/queryConfig";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// FETCH BRANCHES
async function fetchBranches(projectId: string): Promise<Branch[]> {
	const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/branches`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch branches");
	const data = await res.json();
	return Array.isArray(data) ? data : data.branches || [];
}

export function useBranches(projectId: string) {
	return useQuery({
		queryKey: [queryKeys.branches, projectId],
		queryFn: () => fetchBranches(projectId),
		...QUERY_CONFIGS.default,
	});
}

// FETCH VERSIONS
async function fetchVersions(branchId: string): Promise<Version[]> {
	const res = await fetch(`${API_URL}/api/v1/branches/${branchId}/versions`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch versions");
	const data = await res.json();
	return Array.isArray(data) ? data : data.versions || [];
}

export function useVersions(branchId: string) {
	return useQuery({
		queryKey: [queryKeys.versions, branchId],
		queryFn: () => fetchVersions(branchId),
		...QUERY_CONFIGS.default,
	});
}

// CREATE BRANCH
interface CreateBranchInput {
	projectId: string;
	name: string;
	description?: string;
	parentId?: string;
}

async function createBranch(input: CreateBranchInput): Promise<Branch> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${input.projectId}/branches`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(input),
		},
	);
	if (!res.ok) throw new Error("Failed to create branch");
	return res.json();
}

export function useCreateBranch() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createBranch,
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: [queryKeys.branches, variables.projectId],
			});
		},
	});
}

// CREATE VERSION
interface CreateVersionInput {
	branchId: string;
	title: string;
	description?: string;
	tag?: string;
	status?: "draft" | "published" | "archived";
}

async function createVersion(input: CreateVersionInput): Promise<Version> {
	const res = await fetch(
		`${API_URL}/api/v1/branches/${input.branchId}/versions`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(input),
		},
	);
	if (!res.ok) throw new Error("Failed to create version");
	return res.json();
}

export function useCreateVersion() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createVersion,
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: [queryKeys.versions, variables.branchId],
			});
		},
	});
}

// MERGE BRANCH
interface MergeBranchInput {
	sourceBranchId: string;
	targetBranchId: string;
	conflictResolution?: "manual" | "source" | "target";
}

async function mergeBranch(
	input: MergeBranchInput,
): Promise<{ success: boolean; conflicts?: any[] }> {
	const res = await fetch(
		`${API_URL}/api/v1/branches/${input.targetBranchId}/merge`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify({
				sourceBranchId: input.sourceBranchId,
				conflictResolution: input.conflictResolution || "manual",
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to merge branches");
	return res.json();
}

export function useMergeBranch() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: mergeBranch,
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: [queryKeys.branches],
			});
			queryClient.invalidateQueries({
				queryKey: [queryKeys.versions, variables.targetBranchId],
			});
		},
	});
}

/**
 * Version snapshot data structure
 */
export interface VersionSnapshot {
	[key: string]: string | number | boolean | object | null | undefined;
}

// GET VERSION SNAPSHOT
async function getVersionSnapshot(versionId: string): Promise<VersionSnapshot> {
	const res = await fetch(`${API_URL}/api/v1/versions/${versionId}/snapshot`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch version snapshot");
	return res.json();
}

export function useVersionSnapshot(versionId: string) {
	return useQuery({
		queryKey: [queryKeys.versionSnapshot, versionId],
		queryFn: () => getVersionSnapshot(versionId),
		...QUERY_CONFIGS.default,
	});
}

// UPDATE BRANCH
interface UpdateBranchInput {
	branchId: string;
	name?: string;
	description?: string;
	status?: "active" | "review" | "merged" | "abandoned";
}

async function updateBranch(input: UpdateBranchInput): Promise<Branch> {
	const res = await fetch(`${API_URL}/api/v1/branches/${input.branchId}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			name: input.name,
			description: input.description,
			status: input.status,
		}),
	});
	if (!res.ok) throw new Error("Failed to update branch");
	return res.json();
}

export function useUpdateBranch() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: updateBranch,
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: [queryKeys.branches],
			});
		},
	});
}

// UPDATE VERSION
interface UpdateVersionInput {
	versionId: string;
	title?: string;
	description?: string;
	tag?: string;
	status?: "draft" | "published" | "archived";
}

async function updateVersion(input: UpdateVersionInput): Promise<Version> {
	const res = await fetch(`${API_URL}/api/v1/versions/${input.versionId}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			title: input.title,
			description: input.description,
			tag: input.tag,
			status: input.status,
		}),
	});
	if (!res.ok) throw new Error("Failed to update version");
	return res.json();
}

export function useUpdateVersion() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: updateVersion,
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: [queryKeys.versions],
			});
		},
	});
}

// DELETE BRANCH
async function deleteBranch(branchId: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/branches/${branchId}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete branch");
}

export function useDeleteBranch() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteBranch,
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: [queryKeys.branches],
			});
		},
	});
}

// COMPARE BRANCHES
interface ComparisonResult {
	divergencePoint: Version | null;
	sourceVersions: Version[];
	targetVersions: Version[];
	commonVersions: Version[];
	conflicts: any[];
}

async function compareBranches(
	sourceBranchId: string,
	targetBranchId: string,
): Promise<ComparisonResult> {
	const res = await fetch(
		`${API_URL}/api/v1/branches/${sourceBranchId}/compare/${targetBranchId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to compare branches");
	return res.json();
}

export function useCompareBranches(
	sourceBranchId: string,
	targetBranchId: string,
) {
	return useQuery({
		queryKey: [queryKeys.branchComparison, sourceBranchId, targetBranchId],
		queryFn: () => compareBranches(sourceBranchId, targetBranchId),
		...QUERY_CONFIGS.default,
	});
}
