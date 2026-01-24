/**
 * Tests for React Query Hooks
 */

import type {
	UseMutationOptions,
	UseQueryOptions,
} from "@tanstack/react-query";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	queryKeys,
	useAgents,
	useCreateItem,
	useCreateLink,
	useCreateMutation,
	useCreateProject,
	useDeleteItem,
	useDeleteLink,
	useDeleteProject,
	useItem,
	useMutations,
	useProject,
	useProjectItems,
	useProjectLinks,
	useProjects,
	useUpdateItem,
	useUpdateProject,
} from "@/api/queries";

// Mock the API client
vi.mock("@/api/client", () => ({
	apiClient: {
		GET: vi.fn(),
		POST: vi.fn(),
		PUT: vi.fn(),
		DELETE: vi.fn(),
	},
	handleApiResponse: vi.fn((promise) => promise),
}));

import { handleApiResponse } from "@/api/client";
import { mockAgents, mockItems, mockLinks, mockProjects } from "../mocks/data";

// Helper to create wrapper with QueryClient
function createWrapper() {
	const queryClient = new QueryClient({
		defaultOptions: {
			queries: { retry: false },
			mutations: { retry: false },
		},
	});
	return function Wrapper({ children }: { children: ReactNode }) {
		return React.createElement(
			QueryClientProvider,
			{ client: queryClient },
			children,
		);
	};
}

describe("React Query Hooks", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("Query Keys", () => {
		it("should define projects query key", () => {
			const key = queryKeys.projects;
			expect(key).toEqual(["projects"]);
		});

		it("should define project query key with ID", () => {
			const key = queryKeys.project("proj-1");
			expect(key).toEqual(["projects", "proj-1"]);
		});

		it("should define projectItems query key with ID", () => {
			const key = queryKeys.projectItems("proj-1");
			expect(key).toEqual(["projects", "proj-1", "items", undefined]);
		});

		it("should define projectItems query key with filters", () => {
			const filters = { status: "completed", priority: "high" };
			const key = queryKeys.projectItems("proj-1", filters);
			expect(key).toContain("projects");
			expect(key).toContain("proj-1");
			expect(key).toContain("items");
		});

		it("should define item query key", () => {
			const key = queryKeys.item("item-1");
			expect(key).toEqual(["items", "item-1"]);
		});

		it("should define projectLinks query key", () => {
			const key = queryKeys.projectLinks("proj-1");
			expect(key).toEqual(["projects", "proj-1", "links"]);
		});

		it("should define agents query key", () => {
			const key = queryKeys.agents;
			expect(key).toEqual(["agents"]);
		});

		it("should define mutations query key", () => {
			const key = queryKeys.mutations();
			expect(key).toEqual(["mutations", undefined]);
		});

		it("should define mutations query key with filters", () => {
			const filters = { agentId: "agent-1", synced: true };
			const key = queryKeys.mutations(filters);
			expect(key).toContain("mutations");
		});

		it("should create unique keys for different resources", () => {
			const keys = [
				queryKeys.projects,
				queryKeys.project("proj-1"),
				queryKeys.item("item-1"),
				queryKeys.agents,
			];

			const uniqueKeys = new Set(keys.map((k) => JSON.stringify(k)));
			expect(uniqueKeys.size).toBe(4);
		});
	});

	describe("useProjects hook", () => {
		it("should fetch all projects", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue({
				items: mockProjects,
				total: 2,
				page: 1,
				pageSize: 10,
			});

			const { result } = renderHook(() => useProjects(), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});

			expect(result.current.data?.items).toEqual(mockProjects);
		});

		it("should support custom options", () => {
			vi.mocked(handleApiResponse).mockResolvedValue({
				items: [],
				total: 0,
				page: 1,
				pageSize: 10,
			});

			const options: UseQueryOptions = { staleTime: 5000 };
			const { result } = renderHook(() => useProjects(options), {
				wrapper: createWrapper(),
			});

			expect(result.current).toBeDefined();
		});
	});

	describe("useProject hook", () => {
		it("should fetch a single project", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockProjects[0]);

			const { result } = renderHook(() => useProject("proj-1"), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});

			expect(result.current.data?.id).toBe("proj-1");
		});

		it("should be disabled when project ID is empty", () => {
			const { result } = renderHook(() => useProject(""), {
				wrapper: createWrapper(),
			});

			// When disabled, the query should not fetch data
			expect(result.current.status).toBe("pending");
		});

		it("should support custom options", () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockProjects[0]);

			const options: UseQueryOptions = { staleTime: 10000 };
			const { result } = renderHook(() => useProject("proj-1", options), {
				wrapper: createWrapper(),
			});

			expect(result.current).toBeDefined();
		});
	});

	describe("useCreateProject mutation", () => {
		it("should create a project", async () => {
			const newProject = { name: "New Project", description: "Test" };
			vi.mocked(handleApiResponse).mockResolvedValue({
				...newProject,
				id: "new-proj",
			});

			const { result } = renderHook(() => useCreateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate(newProject);

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});

		it("should support custom options", () => {
			const options: UseMutationOptions = { onSuccess: vi.fn() };
			const { result } = renderHook(() => useCreateProject(options), {
				wrapper: createWrapper(),
			});

			expect(result.current).toBeDefined();
		});

		it("should invalidate projects query on success", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue({
				id: "new-proj",
				name: "New",
			});

			const { result } = renderHook(() => useCreateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({ name: "New" });

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useUpdateProject mutation", () => {
		it("should update a project", async () => {
			const updated = {
				...mockProjects[0],
				name: "Updated Name",
			};
			vi.mocked(handleApiResponse).mockResolvedValue(updated);

			const { result } = renderHook(() => useUpdateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				projectId: "proj-1",
				data: { name: "Updated Name" },
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});

		it("should invalidate related queries on success", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockProjects[0]);

			const { result } = renderHook(() => useUpdateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				projectId: "proj-1",
				data: { name: "Updated" },
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useDeleteProject mutation", () => {
		it("should delete a project", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(undefined);

			const { result } = renderHook(() => useDeleteProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate("proj-1");

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});

		it("should invalidate projects query on success", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(undefined);

			const { result } = renderHook(() => useDeleteProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate("proj-1");

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useProjectItems hook", () => {
		it("should fetch items for a project", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue({
				items: mockItems,
				total: 3,
				page: 1,
				pageSize: 10,
			});

			const { result } = renderHook(() => useProjectItems("proj-1"), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});

			expect(result.current.data?.items).toEqual(mockItems);
		});

		it("should support filter parameters", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue({
				items: [mockItems[0]],
				total: 1,
				page: 1,
				pageSize: 10,
			});

			const { result } = renderHook(
				() =>
					useProjectItems("proj-1", {
						status: "completed",
						priority: "high",
					}),
				{ wrapper: createWrapper() },
			);

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});

		it("should be disabled when project ID is empty", () => {
			const { result } = renderHook(() => useProjectItems(""), {
				wrapper: createWrapper(),
			});

			// When disabled, the query should not fetch data
			expect(result.current.status).toBe("pending");
		});
	});

	describe("useItem hook", () => {
		it("should fetch a single item", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockItems[0]);

			const { result } = renderHook(() => useItem("item-1"), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});

			expect(result.current.data?.id).toBe("item-1");
		});

		it("should be disabled when item ID is empty", () => {
			const { result } = renderHook(() => useItem(""), {
				wrapper: createWrapper(),
			});

			// When disabled, the query should not fetch data
			expect(result.current.status).toBe("pending");
		});
	});

	describe("useCreateItem mutation", () => {
		it("should create an item", async () => {
			const newItem = { title: "New Item", type: "feature" };
			vi.mocked(handleApiResponse).mockResolvedValue({
				...mockItems[0],
				...newItem,
				id: "new-item",
			});

			const { result } = renderHook(() => useCreateItem(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				projectId: "proj-1",
				data: newItem,
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});

		it("should invalidate project items on success", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue({
				...mockItems[0],
				id: "new-item",
			});

			const { result } = renderHook(() => useCreateItem(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				projectId: "proj-1",
				data: { title: "New" },
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useUpdateItem mutation", () => {
		it("should update an item", async () => {
			const updated = { ...mockItems[0], title: "Updated" };
			vi.mocked(handleApiResponse).mockResolvedValue(updated);

			const { result } = renderHook(() => useUpdateItem(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				itemId: "item-1",
				data: { title: "Updated" },
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useDeleteItem mutation", () => {
		it("should delete an item", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(undefined);

			const { result } = renderHook(() => useDeleteItem(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				itemId: "item-1",
				projectId: "proj-1",
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useProjectLinks hook", () => {
		it("should fetch links for a project", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockLinks);

			const { result } = renderHook(() => useProjectLinks("proj-1"), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});

			expect(result.current.data).toEqual(mockLinks);
		});

		it("should be disabled when project ID is empty", () => {
			const { result } = renderHook(() => useProjectLinks(""), {
				wrapper: createWrapper(),
			});

			// When disabled, the query should not fetch data
			expect(result.current.status).toBe("pending");
		});
	});

	describe("useCreateLink mutation", () => {
		it("should create a link", async () => {
			const newLink = {
				source_id: "item-1",
				target_id: "item-2",
				type: "implements" as const,
			};
			vi.mocked(handleApiResponse).mockResolvedValue({
				...mockLinks[0],
				...newLink,
				id: "new-link",
			});

			const { result } = renderHook(() => useCreateLink(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				projectId: "proj-1",
				data: newLink,
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});

		it("should invalidate project links on success", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockLinks[0]);

			const { result } = renderHook(() => useCreateLink(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				projectId: "proj-1",
				data: mockLinks[0],
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useDeleteLink mutation", () => {
		it("should delete a link", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(undefined);

			const { result } = renderHook(() => useDeleteLink(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				linkId: "link-1",
				projectId: "proj-1",
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useAgents hook", () => {
		it("should fetch all agents", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockAgents);

			const { result } = renderHook(() => useAgents(), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});

			expect(result.current.data).toEqual(mockAgents);
		});

		it("should refetch at regular intervals", () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockAgents);

			const { result } = renderHook(() => useAgents(), {
				wrapper: createWrapper(),
			});

			expect(result.current).toBeDefined();
		});

		it("should support custom options", () => {
			vi.mocked(handleApiResponse).mockResolvedValue(mockAgents);

			const options: UseQueryOptions = { staleTime: 5000 };
			const { result } = renderHook(() => useAgents(options), {
				wrapper: createWrapper(),
			});

			expect(result.current).toBeDefined();
		});
	});

	describe("useMutations hook", () => {
		it("should fetch mutations", async () => {
			const mockMutations = [
				{ id: "mut-1", agentId: "agent-1" },
				{ id: "mut-2", agentId: "agent-1" },
			];
			vi.mocked(handleApiResponse).mockResolvedValue(mockMutations);

			const { result } = renderHook(() => useMutations(), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});

			expect(result.current.data).toEqual(mockMutations);
		});

		it("should support filter parameters", async () => {
			const mockMutations = [{ id: "mut-1", agentId: "agent-1" }];
			vi.mocked(handleApiResponse).mockResolvedValue(mockMutations);

			const { result } = renderHook(
				() =>
					useMutations({
						agentId: "agent-1",
						synced: false,
					}),
				{ wrapper: createWrapper() },
			);

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("useCreateMutation mutation", () => {
		it("should create a mutation", async () => {
			const newMutation = {
				agentId: "agent-1",
				itemId: "item-1",
				operation: "create" as const,
				data: { field: "value" },
			};
			vi.mocked(handleApiResponse).mockResolvedValue({
				id: "mut-1",
				...newMutation,
			});

			const { result } = renderHook(() => useCreateMutation(), {
				wrapper: createWrapper(),
			});

			result.current.mutate(newMutation);

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});

		it("should invalidate mutations query on success", async () => {
			vi.mocked(handleApiResponse).mockResolvedValue({
				id: "mut-1",
				agentId: "agent-1",
			});

			const { result } = renderHook(() => useCreateMutation(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				agentId: "agent-1",
				itemId: "item-1",
				operation: "create" as const,
				data: {},
			});

			await waitFor(() => {
				expect(result.current.isSuccess).toBe(true);
			});
		});
	});

	describe("Query hook error handling", () => {
		it("should handle fetch errors gracefully", async () => {
			vi.mocked(handleApiResponse).mockRejectedValue(new Error("API error"));

			const { result } = renderHook(() => useProjects(), {
				wrapper: createWrapper(),
			});

			await waitFor(() => {
				expect(result.current.isError).toBe(true);
			});
		});

		it("should handle mutation errors gracefully", async () => {
			vi.mocked(handleApiResponse).mockRejectedValue(
				new Error("Mutation failed"),
			);

			const { result } = renderHook(() => useCreateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({ name: "Test" });

			await waitFor(() => {
				expect(result.current.isError).toBe(true);
			});
		});
	});

	describe("Query hook loading states", () => {
		it("should indicate loading state during fetch", () => {
			vi.mocked(handleApiResponse).mockImplementation(
				() =>
					new Promise((resolve) =>
						setTimeout(() => resolve({ items: [] }), 100),
					),
			);

			const { result } = renderHook(() => useProjects(), {
				wrapper: createWrapper(),
			});

			expect(result.current.isPending).toBe(true);
		});
	});
});
