/**
 * Tests for useProjects hook
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	useCreateProject,
	useProject,
	useProjects,
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

describe("useProjects", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("should fetch projects", async () => {
		const mockProjects = [
			{ id: "1", name: "Project 1", description: "Desc 1" },
			{ id: "2", name: "Project 2", description: "Desc 2" },
		];

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => mockProjects,
		});

		const { result } = renderHook(() => useProjects(), {
			wrapper: createWrapper(),
		});

		await waitFor(() => expect(result.current.isSuccess).toBe(true));

		expect(result.current.data).toEqual(mockProjects);
		expect(mockFetch).toHaveBeenCalledTimes(1);
	});

	it("should handle fetch error", async () => {
		mockFetch.mockResolvedValueOnce({
			ok: false,
			status: 500,
		});

		const { result } = renderHook(() => useProjects(), {
			wrapper: createWrapper(),
		});

		await waitFor(() => expect(result.current.isError).toBe(true));

		expect(result.current.error).toBeTruthy();
	});
});

describe("useProject", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("should fetch a single project", async () => {
		const mockProject = {
			id: "1",
			name: "Project 1",
			description: "Description",
		};

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => mockProject,
		});

		const { result } = renderHook(() => useProject("1"), {
			wrapper: createWrapper(),
		});

		await waitFor(() => expect(result.current.isSuccess).toBe(true));

		expect(result.current.data).toEqual(mockProject);
		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/projects/1"),
			expect.objectContaining({
				headers: {
					"X-Bulk-Operation": "true",
				},
			}),
		);
	});

	it("should not fetch when id is empty", () => {
		const { result } = renderHook(() => useProject(""), {
			wrapper: createWrapper(),
		});

		expect(result.current.fetchStatus).toBe("idle");
		expect(mockFetch).not.toHaveBeenCalled();
	});
});

describe("useCreateProject", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("should create a project", async () => {
		const newProject = {
			name: "New Project",
			description: "New Description",
		};

		const createdProject = {
			id: "1",
			...newProject,
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
		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/projects"),
			expect.objectContaining({
				method: "POST",
			}),
		);
	});

	it("should handle create error", async () => {
		mockFetch.mockResolvedValueOnce({
			ok: false,
			status: 400,
		});

		const { result } = renderHook(() => useCreateProject(), {
			wrapper: createWrapper(),
		});

		result.current.mutate({
			name: "New Project",
			description: "Description",
		});

		await waitFor(() => expect(result.current.isError).toBe(true));
	});
});
