/**
 * Tests for useItems hook
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
	useCreateItem,
	useDeleteItem,
	useItem,
	useItems,
	useUpdateItem,
} from "../../hooks/useItems";

// Setup global fetch mock
const originalFetch = global.fetch;
const mockFetch = vi.fn();

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

describe("useItems", () => {
	beforeEach(() => {
		mockFetch.mockClear();
		global.fetch = mockFetch as unknown as typeof fetch;
	});

	afterEach(() => {
		global.fetch = originalFetch;
	});

	it("should fetch items", async () => {
		const mockItems = [
			{
				id: "1",
				title: "Item 1",
				type: "feature",
				status: "todo",
				priority: "high",
			},
			{
				id: "2",
				title: "Item 2",
				type: "bug",
				status: "done",
				priority: "medium",
			},
		];

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => ({ items: mockItems, total: 2 }),
		});

		const { result } = renderHook(() => useItems({ projectId: "p1" }), {
			wrapper: createWrapper(),
		});

		await waitFor(() => expect(result.current.isSuccess).toBe(true));

		expect(result.current.data).toEqual({ items: mockItems, total: 2 });
		expect(mockFetch).toHaveBeenCalledTimes(1);
	});

	it("should fetch items with project filter", async () => {
		const mockItems = [{ id: "1", title: "Item 1", projectId: "project-1" }];

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => ({ items: mockItems, total: 1 }),
		});

		const { result } = renderHook(() => useItems({ projectId: "project-1" }), {
			wrapper: createWrapper(),
		});

		await waitFor(() => expect(result.current.isSuccess).toBe(true));

		expect(result.current.data).toEqual({ items: mockItems, total: 1 });
		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("project_id=project-1"),
			expect.any(Object),
		);
	});

	it("should handle fetch error", async () => {
		mockFetch.mockResolvedValueOnce({
			ok: false,
			status: 500,
		});

		const { result } = renderHook(() => useItems({ projectId: "p1" }), {
			wrapper: createWrapper(),
		});

		await waitFor(() => expect(result.current.isError).toBe(true));

		expect(result.current.error).toBeTruthy();
	});
});

describe("useItem", () => {
	beforeEach(() => {
		mockFetch.mockClear();
		global.fetch = mockFetch as unknown as typeof fetch;
	});

	afterEach(() => {
		global.fetch = originalFetch;
	});

	it("should fetch a single item", async () => {
		const mockItem = {
			id: "1",
			title: "Item 1",
			type: "feature",
			status: "todo",
			priority: "high",
		};

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => mockItem,
		});

		const { result } = renderHook(() => useItem("1"), {
			wrapper: createWrapper(),
		});

		await waitFor(() => expect(result.current.isSuccess).toBe(true));

		expect(result.current.data).toEqual(mockItem);
		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/items/1"),
		);
	});

	it("should not fetch when id is empty", () => {
		const { result } = renderHook(() => useItem(""), {
			wrapper: createWrapper(),
		});

		expect(result.current.fetchStatus).toBe("idle");
		expect(mockFetch).not.toHaveBeenCalled();
	});
});

describe("useCreateItem", () => {
	beforeEach(() => {
		mockFetch.mockClear();
		global.fetch = mockFetch as unknown as typeof fetch;
	});

	afterEach(() => {
		global.fetch = originalFetch;
	});

	it("should create an item", async () => {
		const newItem = {
			projectId: "project-1",
			view: "CODE" as const,
			type: "feature",
			title: "New Item",
			status: "todo" as const,
			priority: "high" as const,
		};

		const createdItem = {
			id: "1",
			...newItem,
		};

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => createdItem,
		});

		const { result } = renderHook(() => useCreateItem(), {
			wrapper: createWrapper(),
		});

		await act(async () => {
			result.current.mutate(newItem);
		});

		await waitFor(
			() => {
				expect(result.current.isSuccess).toBe(true);
			},
			{ timeout: 5000 },
		);

		expect(result.current.data).toEqual(createdItem);
		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/items"),
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

		const { result } = renderHook(() => useCreateItem(), {
			wrapper: createWrapper(),
		});

		const newItem = {
			projectId: "project-1",
			view: "CODE" as const,
			type: "feature",
			title: "New Item",
			status: "todo" as const,
			priority: "high" as const,
		};

		await act(async () => {
			result.current.mutate(newItem);
		});

		await waitFor(
			() => {
				expect(result.current.isError).toBe(true);
			},
			{ timeout: 5000 },
		);
	});
});

describe("useUpdateItem", () => {
	beforeEach(() => {
		mockFetch.mockClear();
		global.fetch = mockFetch as unknown as typeof fetch;
	});

	afterEach(() => {
		global.fetch = originalFetch;
	});

	it("should update an item", async () => {
		const updatedItem = {
			id: "1",
			title: "Updated Item",
			status: "in_progress" as const,
		};

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => updatedItem,
		});

		const { result } = renderHook(() => useUpdateItem(), {
			wrapper: createWrapper(),
		});

		await act(async () => {
			result.current.mutate({
				id: "1",
				data: { title: "Updated Item", status: "in_progress" as const },
			});
		});

		await waitFor(
			() => {
				expect(result.current.isSuccess).toBe(true);
			},
			{ timeout: 5000 },
		);

		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/items/1"),
			expect.objectContaining({
				method: "PATCH",
			}),
		);
	});
});

describe("useDeleteItem", () => {
	beforeEach(() => {
		mockFetch.mockClear();
		global.fetch = mockFetch as unknown as typeof fetch;
	});

	afterEach(() => {
		global.fetch = originalFetch;
	});

	it("should delete an item", async () => {
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => ({}),
		});

		const { result } = renderHook(() => useDeleteItem(), {
			wrapper: createWrapper(),
		});

		await act(async () => {
			result.current.mutate("1");
		});

		await waitFor(
			() => {
				expect(result.current.isSuccess).toBe(true);
			},
			{ timeout: 5000 },
		);

		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/items/1"),
			expect.objectContaining({
				method: "DELETE",
			}),
		);
	});
});
