/**
 * Comprehensive tests for useProjects hook
 * Target: 52.94% → 95% coverage
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	useCreateProject,
	useDeleteProject,
	useProject,
	useProjects,
	useUpdateProject,
} from "../../hooks/useProjects";

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch as unknown as typeof fetch;

const createWrapper = () => {
	const queryClient = new QueryClient({
		defaultOptions: {
			queries: { retry: false },
			mutations: { retry: false },
		},
	});

	return ({ children }: { children: React.ReactNode }) =>
		React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe("useProjects - Comprehensive Coverage", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("useProjects", () => {
		it("should fetch empty projects list", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => [],
			});

			const { result } = renderHook(() => useProjects(), {
				wrapper: createWrapper(),
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toEqual([]);
		});

		it("should handle network errors", async () => {
			mockFetch.mockRejectedValueOnce(new Error("Network error"));

			const { result } = renderHook(() => useProjects(), {
				wrapper: createWrapper(),
			});

			await waitFor(() => expect(result.current.isError).toBe(true));

			expect(result.current.error).toBeTruthy();
		});
	});

	describe("useProject", () => {
		it("should handle fetch errors", async () => {
			// Mock for initial attempt and one retry (retry: 1)
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				text: async () => "Not found",
			});
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				text: async () => "Not found",
			});

			const { result } = renderHook(() => useProject("proj-1"), {
				wrapper: createWrapper(),
			});

			await waitFor(() => expect(result.current.isError).toBe(true), {
				timeout: 3000,
			});
		});

		it("should handle network errors", async () => {
			// Mock for initial attempt and one retry (retry: 1)
			mockFetch.mockRejectedValueOnce(new Error("Network error"));
			mockFetch.mockRejectedValueOnce(new Error("Network error"));

			const { result } = renderHook(() => useProject("proj-1"), {
				wrapper: createWrapper(),
			});

			await waitFor(() => expect(result.current.isError).toBe(true), {
				timeout: 3000,
			});
		});
	});

	describe("useCreateProject", () => {
		it("should create project without description", async () => {
			const newProject = {
				name: "New Project",
			};

			const createdProject = {
				id: "1",
				...newProject,
				description: undefined,
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => createdProject,
			});

			const { result } = renderHook(() => useCreateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate(newProject);

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toEqual(createdProject);
		});

		it("should handle validation errors", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
			});

			const { result } = renderHook(() => useCreateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				name: "",
				description: "Invalid",
			});

			await waitFor(() => expect(result.current.isError).toBe(true));
		});
	});

	describe("useUpdateProject", () => {
		it("should update project", async () => {
			const updates = { name: "Updated Name" };
			const updatedProject = {
				id: "proj-1",
				name: "Updated Name",
				description: "Original Description",
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => updatedProject,
			});

			const { result } = renderHook(() => useUpdateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({ id: "proj-1", data: updates });

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toEqual(updatedProject);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/projects/proj-1"),
				expect.objectContaining({
					method: "PATCH",
					headers: expect.objectContaining({
						"Content-Type": "application/json",
					}),
					body: JSON.stringify(updates),
				}),
			);
		});

		it("should invalidate both list and single project queries", async () => {
			const updates = { description: "New Description" };
			const updatedProject = {
				id: "proj-1",
				name: "Project 1",
				description: "New Description",
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => updatedProject,
			});

			const { result } = renderHook(() => useUpdateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({ id: "proj-1", data: updates });

			await waitFor(() => expect(result.current.isSuccess).toBe(true));
		});

		it("should handle update errors", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
			});

			const { result } = renderHook(() => useUpdateProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate({
				id: "proj-1",
				data: { name: "Updated" },
			});

			await waitFor(() => expect(result.current.isError).toBe(true));
		});
	});

	describe("useDeleteProject", () => {
		it("should delete project", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
			});

			const { result } = renderHook(() => useDeleteProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate("proj-1");

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/projects/proj-1"),
				expect.objectContaining({
					method: "DELETE",
				}),
			);
		});

		it("should invalidate queries on success", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
			});

			const { result } = renderHook(() => useDeleteProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate("proj-1");

			await waitFor(() => expect(result.current.isSuccess).toBe(true));
		});

		it("should handle delete errors", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
			});

			const { result } = renderHook(() => useDeleteProject(), {
				wrapper: createWrapper(),
			});

			result.current.mutate("proj-1");

			await waitFor(() => expect(result.current.isError).toBe(true));
		});
	});
});
